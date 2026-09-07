"""Seed dữ liệu cho cụm D5 (DataList CMP-DL-001) — đủ mốc BA acceptance #7.

BA đòi thử danh sách ở 0/1/2/10/11/50+ record, mà DB dev chỉ có 4 ticket / 4 phiếu
bù hàng / 1 chuyến giao / 0 hoá đơn / 0 phiếu khảo sát cho HN-01 (xem
docs/d5-datalist-inventory.md §5). Không có dữ liệu thì không có bảng đo trước–sau.

Idempotent: mọi bản ghi mang dấu SEED-D5 và được search-or-create.
LOCAL-ONLY — chạy trên DB copy, KHÔNG chạy trên wujia_tea_19 hay production.

    cd /home/huyban/odoo-dev/WujiaTea
    python3 odoo19/odoo-bin shell -c config/odoo.conf -d <db-copy> --no-http \
        --logfile=<thư-mục>/x.log < scripts/seed_d5_datalist_demo.py
"""
from datetime import date, datetime, timedelta

MARK = 'SEED-D5'
N_TICKET = 55      # > 50 để chạm mốc "50+" của acceptance #7
N_RETURN = 24        # > PAGE_SIZE 20 ⇒ pager thật sự hiện, guard page_count>1 được thử
N_INVOICE = 14
N_INSPECTION = 14
N_BATCH = 14

print("=== SEED D5 DATALIST ===")

franchise = env['wujia.franchise.management'].search([('code', '=', 'HN-01')], limit=1)
if not franchise:
    franchise = env['wujia.franchise.management'].search([], order='code', limit=1)
if not franchise:
    raise SystemExit("Không có franchise nào.")
print(f"Franchise: [{franchise.code}] {franchise.name} (id={franchise.id})")

now = datetime.now()
today = date.today()
admin = env.ref('base.user_admin')

# Portal Hỗ trợ lọc theo created_by_id = user đang đăng nhập, nên ticket phải thuộc
# chính chủ cửa hàng, không phải admin.
member = env['wujia.franchise.member'].search(
    [('franchise_id', '=', franchise.id), ('user_id', '!=', False)], limit=1)
owner_user = member.user_id or admin
print(f"Chủ cửa hàng: {owner_user.login} (id={owner_user.id})")


def upsert(model, domain, vals, label):
    rec = env[model].search(domain, limit=1)
    if rec:
        return rec
    rec = env[model].create(vals)
    print(f"  [CREATE] {label}: {rec.display_name or rec.id}")
    return rec


# ---------------------------------------------------------------- tickets
cats = env['wujia.support.category'].search([], order='sequence')
states = ['new', 'in_progress', 'waiting', 'resolved', 'closed']
prios = ['low', 'normal', 'high', 'urgent']
have = env['wujia.support.ticket'].search_count([('franchise_id', '=', franchise.id)])
print(f"\n[1] Support tickets — hiện {have}, cần {N_TICKET}")
Ticket = env['wujia.support.ticket']
valid_states = [s for s in states if s in dict(Ticket._fields['state'].selection)]
valid_prios = [p for p in prios if p in dict(Ticket._fields['priority'].selection)]
for i in range(max(0, N_TICKET - have)):
    title = f'[{MARK}] Yêu cầu hỗ trợ mẫu số {i + 1:03d}'
    upsert('wujia.support.ticket', [('title', '=', title)], {
        'title': title,
        'franchise_id': franchise.id,
        'category_id': cats[i % len(cats)].id,
        'created_by_id': owner_user.id,
        'priority': valid_prios[i % len(valid_prios)],
        'state': valid_states[i % len(valid_states)],
        'description': f'<p>Nội dung mẫu cho phiếu hỗ trợ số {i + 1}.</p>',
    }, f'ticket {i + 1}')
stale = env['wujia.support.ticket'].search(
    [('title', 'like', f'[{MARK}]'), ('created_by_id', '!=', owner_user.id)])
if stale:
    stale.write({'created_by_id': owner_user.id})
    print(f"  [FIX] gán lại {len(stale)} ticket về {owner_user.login}")
print(f"  → {env['wujia.support.ticket'].search_count([('created_by_id', '=', owner_user.id)])} ticket của chủ cửa hàng")

# ---------------------------------------------------------------- returns
issue_types = env['wujia.return.issue.type'].search([], limit=5)
products = env['product.product'].search([('sale_ok', '=', True)], limit=5)
uom = env.ref('uom.product_uom_unit', raise_if_not_found=False)
have = env['wujia.return.request'].search_count([('franchise_id', '=', franchise.id)])
print(f"\n[2] Return requests — hiện {have}, cần {N_RETURN}")
if not (issue_types and products and uom):
    print("  ! bỏ qua: thiếu loại lỗi / sản phẩm / đơn vị tính")
else:
    rr_states = ['draft', 'submitted', 'reviewing', 'approved', 'processing', 'done', 'rejected']
    # Đánh số theo mã cố định 001..N (không theo phần còn thiếu) — chạy lại lần hai
    # với N lớn hơn thì phần thêm mới không đụng mã đã có.
    for i in range(N_RETURN):
        code = f'WJ-RR/{MARK}/{i + 1:03d}'
        upsert('wujia.return.request', [('name', '=', code)], {
            'name': code,
            'franchise_id': franchise.id,
            'request_date': now - timedelta(days=i),
            'state': rr_states[i % len(rr_states)],
            'product_id': products[i % len(products)].id,
            'request_qty': 1.0 + i,
            'request_uom_id': uom.id,
            'opening_datetime': now - timedelta(days=i, hours=2),
            'issue_type_id': issue_types[i % len(issue_types)].id,
            'note': f'Phiếu bù hàng mẫu {i + 1}',
        }, f'return {i + 1}')
print(f"  → {env['wujia.return.request'].search_count([('franchise_id', '=', franchise.id)])} phiếu")

# ---------------------------------------------------------------- invoices
print(f"\n[3] Hoá đơn có franchise_id (cho /portal/debt)")
partner = franchise.partner_id or admin.partner_id
income = env['account.account'].search([('account_type', '=', 'income')], limit=1)
journal = env['account.journal'].search(
    [('type', '=', 'sale'), ('company_id', '=', env.company.id)], limit=1)
have = env['account.move'].search_count(
    [('franchise_id', '=', franchise.id), ('move_type', '=', 'out_invoice')])
print(f"  hiện {have}, cần {N_INVOICE}")
if not (income and journal and partner):
    print("  ! bỏ qua: thiếu partner / income account / sale journal")
else:
    for i in range(max(0, N_INVOICE - have)):
        ref = f'{MARK}-INV-{i + 1:03d}'
        if env['account.move'].search_count([('ref', '=', ref)]):
            continue
        inv_date = today - timedelta(days=7 * i)
        move = env['account.move'].create({
            'move_type': 'out_invoice',
            'partner_id': partner.id,
            'invoice_date': inv_date,
            'journal_id': journal.id,
            'franchise_id': franchise.id,
            'ref': ref,
            'invoice_payment_term_id': False,
            'invoice_line_ids': [(0, 0, {
                'name': f'Nguyên liệu đợt {i + 1}',
                'quantity': 1,
                'price_unit': 1500000.0 + i * 250000,
                'account_id': income.id,
                'tax_ids': [(6, 0, [])],
            })],
        })
        move.action_post()
        # Xen kẽ quá hạn / chưa tới hạn để thử đủ trạng thái công nợ.
        move.invoice_date_due = inv_date + timedelta(days=3 if i % 2 else 30)
        print(f"  [CREATE] invoice {ref}")
print(f"  → {env['account.move'].search_count([('franchise_id', '=', franchise.id)])} hoá đơn")

# ---------------------------------------------------------------- inspections
print(f"\n[4] Phiếu khảo sát (cho /portal/inspection)")
have = env['wujia.franchise.inspection'].search_count([('franchise_id', '=', franchise.id)])
print(f"  hiện {have}, cần {N_INSPECTION}")
template = env['wujia.franchise.inspection.template'].search([], limit=1)
for i in range(max(0, N_INSPECTION - have)):
    name = f'KS/{MARK}/{i + 1:03d}'
    # schedule_id là NOT NULL ở tầng DB — mỗi phiếu phải có lịch giám sát riêng.
    schedule = upsert('wujia.supervision.schedule', [('name', '=', f'LGS/{MARK}/{i + 1:03d}')], {
        'name': f'LGS/{MARK}/{i + 1:03d}',
        'store_id': franchise.id,
        'user_id': admin.id,
        'date': today - timedelta(days=10 * i),
    }, f'schedule {i + 1}')
    vals = {
        'name': name,
        'schedule_id': schedule.id,
        'franchise_id': franchise.id,
        'planned_date': today - timedelta(days=10 * i),
        'submit_date': today - timedelta(days=10 * i),
        'state': 'need_remediation' if i % 3 else 'done',
        'inspector_user_id': admin.id,
        'test_employee_name': f'Nhân viên mẫu {i + 1}',
    }
    if template:
        vals['template_id'] = template.id
    upsert('wujia.franchise.inspection', [('name', '=', name)], vals, f'inspection {i + 1}')
print(f"  → {env['wujia.franchise.inspection'].search_count([('franchise_id', '=', franchise.id)])} phiếu")

# ---------------------------------------------------------------- delivery
print(f"\n[5] Chuyến giao (cho /portal/delivery)")
Picking = env['stock.picking']
Batch = env['stock.picking.batch']
src = Picking.search([('franchise_id', '=', franchise.id), ('batch_id', '!=', False)], limit=1) \
    or Picking.search([('franchise_id', '=', franchise.id)], limit=1)
have = Batch.search_count([('picking_ids.franchise_id', '=', franchise.id)])
print(f"  hiện {have}, cần {N_BATCH}")
if not src:
    print("  ! bỏ qua: không có picking mẫu của cửa hàng này")
else:
    b_states = ['draft', 'assigned', 'delivering', 'done']
    for i in range(max(0, N_BATCH - have)):
        origin = f'{MARK}-DLV-{i + 1:03d}'
        if Picking.search_count([('origin', '=', origin)]):
            continue
        pick = src.copy({'origin': origin, 'franchise_id': franchise.id})
        batch = Batch.create({
            'picking_ids': [(6, 0, pick.ids)],
            'planned_departure': now - timedelta(days=i, hours=3),
        })
        status = b_states[i % len(b_states)]
        if 'delivery_batch_status' in batch._fields:
            batch.delivery_batch_status = status
        print(f"  [CREATE] batch {batch.name} ({status}) ← {origin}")
print(f"  → {Batch.search_count([('picking_ids.franchise_id', '=', franchise.id)])} chuyến")

env.cr.commit()
print("\n=== SEED D5 XONG ===")
