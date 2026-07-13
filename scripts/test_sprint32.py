"""Smoke test Sprint 32 — Controller Thông báo (BA FINAL) — ORM level.

Chạy qua odoo shell:
    cd /home/huyban/odoo-dev/WujiaTea/odoo19
    /home/huyban/miniconda3/envs/odoo/bin/python odoo-bin shell \\
        -c /home/huyban/odoo-dev/WujiaTea/config/odoo.conf \\
        -d wujia_tea_19 --no-http \\
        < /home/huyban/odoo-dev/WujiaTea/scripts/test_sprint32.py

Tạo fixture (noti còn hiệu lực / hết hạn / có file) + commit → HTTP test đọc lại.
"""
import json
from datetime import timedelta

from psycopg2 import IntegrityError

from odoo import fields
from odoo.addons.wujia_portal_notification.controllers import portal as N

print("=== SPRINT 32 SMOKE (ORM) ===")
PASS, FAIL = 0, 0


def check(cond, msg):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  PASS: {msg}")
    else:
        FAIL += 1
        print(f"  FAIL: {msg}")


Noti = env['wujia.notification'].sudo()
Read = env['wujia.notification.read'].sudo()
Type = env['wujia.notification.type'].sudo()
Att = env['ir.attachment'].sudo()
Franchise = env['wujia.franchise.management'].sudo()
now = fields.Datetime.now()

# ---------- 0. cleanup prior fixtures ----------
Noti.search([('dispatch_number', 'like', 'S32-%')]).unlink()

owner = env['res.users'].search([('login', '=', 'anh.owner')], limit=1)
check(bool(owner), "user anh.owner tồn tại")
owner_fids = owner._get_accessible_franchise_ids() if owner else []
store = Franchise.browse(owner_fids[0]) if owner_fids else Franchise.search([], limit=1)
store_b = Franchise.search([('id', '!=', store.id)], limit=1)
check(bool(store), f"owner store = {store.display_name}")
gen = Type.search([('code', '=', 'GEN')], limit=1)


def mk(disp, priority, days_ago=1, expired=None, published=True):
    return Noti.create({
        'name': f'Thông báo {disp}', 'type_id': gen.id, 'dispatch_number': disp,
        'date': now - timedelta(days=days_ago), 'content': f'<p>Nội dung {disp}</p>',
        'priority': priority, 'published': published, 'expired_date': expired,
        'franchise_ids': [(5, 0, 0)],  # broadcast
    })


eff = mk('S32-EFF', 'urgent')
imp = mk('S32-IMP', 'important', days_ago=2)
nrm = mk('S32-NRM', 'normal', days_ago=3)
exp = mk('S32-EXP', 'important', days_ago=5, expired=now - timedelta(days=1))
att_noti = mk('S32-ATT', 'normal', days_ago=1)
other_noti = mk('S32-OTH', 'normal', days_ago=1)
attA = Att.create({'name': 'fileA.pdf', 'datas': b'QQ==', 'mimetype': 'application/pdf',
                   'res_model': 'wujia.notification', 'res_id': att_noti.id})
attB = Att.create({'name': 'fileB.pdf', 'datas': b'Qg==', 'mimetype': 'application/pdf',
                   'res_model': 'wujia.notification', 'res_id': other_noti.id})
att_noti.attachment_ids = [(4, attA.id)]
other_noti.attachment_ids = [(4, attB.id)]

# ---------- 1. priority migration (không còn low/high) + selection keys BA ----------
print("\n[1] priority realign")
check(not Noti.search_count([('priority', 'in', ['low', 'high'])]),
      "không còn record priority low/high (đã remap)")
check(set(dict(N.PC_PRIORITY_TAGS)) == {'normal', 'important', 'urgent'},
      "PC_PRIORITY_TAGS dùng keys BA normal/important/urgent")

# ---------- 2. priority_label backend trả về ----------
print("\n[2] priority_label")
check(eff.priority_label == 'Cần làm', "urgent → 'Cần làm'")
check(imp.priority_label == 'Quan trọng', "important → 'Quan trọng'")
check(nrm.priority_label == 'Lưu ý', "normal → 'Lưu ý'")

# ---------- 3. is_expired compute ----------
print("\n[3] is_expired")
check(exp.is_expired is True, "noti có expired_date quá khứ → is_expired True")
check(eff.is_expired is False, "noti không expired_date → is_expired False")

# ---------- 4. effective vs history domain ----------
print("\n[4] effective vs history domain")
fids = list(owner_fids)
eff_rows = Noti.search(N._effective_domain(fids))
his_rows = Noti.search(N._history_domain(fids))
check(eff in eff_rows and exp not in eff_rows, "effective: chứa còn-hiệu-lực, LOẠI hết hạn")
check(exp in his_rows and eff in his_rows, "history: chứa CẢ hết hạn + còn hiệu lực")

# ---------- 5. read tracking theo (noti, user, cửa hàng) ----------
print("\n[5] read per-store constraint")
Read.search([('notification_id', '=', eff.id), ('user_id', '=', owner.id)]).unlink()
r1 = Read.create({'notification_id': eff.id, 'user_id': owner.id,
                  'franchise_id': store.id, 'read_date': now, 'last_open_date': now})
check(bool(r1), "tạo read line (eff, owner, storeA) OK")
dup_ok = False
try:
    with env.cr.savepoint():
        Read.create({'notification_id': eff.id, 'user_id': owner.id, 'franchise_id': store.id})
except IntegrityError:
    dup_ok = True
check(dup_ok, "tạo trùng (eff, owner, storeA) → chặn bởi unique constraint")
if store_b:
    r2 = Read.create({'notification_id': eff.id, 'user_id': owner.id, 'franchise_id': store_b.id})
    check(bool(r2), "cùng (eff, owner) khác cửa hàng → đọc độc lập, KHÔNG bị chặn")
    # store A đã đọc eff; store B cũng vừa tạo — nhưng nrm chưa đọc ở đâu.
    read_a = set(Read.search([('user_id', '=', owner.id), ('franchise_id', '=', store.id)])
                 .mapped('notification_id').ids)
    check(eff.id in read_a and nrm.id not in read_a,
          "read scope store A: eff đã đọc, nrm chưa đọc")

# cleanup read fixtures (HTTP test sẽ tự tạo lại) — giữ trạng thái sạch cho badge test
Read.search([('notification_id', 'in', [eff.id, imp.id, nrm.id]),
             ('user_id', '=', owner.id)]).unlink()

# ---------- 6. fixture cho HTTP ----------
fixture = {
    'store_id': store.id,
    'eff_id': eff.id, 'eff_name': eff.name,
    'imp_id': imp.id, 'nrm_id': nrm.id,
    'exp_id': exp.id, 'exp_name': exp.name,
    'att_noti_id': att_noti.id, 'attA_id': attA.id,
    'other_noti_id': other_noti.id, 'attB_id': attB.id,
}
path = ('/tmp/claude-1000/-home-huyban-odoo-dev/'
        '8e2a3da0-d53a-494c-8971-b50bb299556b/scratchpad/s32_fixture.json')
with open(path, 'w') as f:
    json.dump(fixture, f)
print(f"  fixture → {path}: {fixture}")

env.cr.commit()
print(f"\n=== RESULT: {PASS} PASS / {FAIL} FAIL ===")
