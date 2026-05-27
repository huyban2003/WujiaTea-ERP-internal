"""Seed demo data nhỏ cho Sprint 9.13 UI-12 Content Card pages.

Mục đích: tạo ~20 record demo nhỏ để showcase 5 page sau khi deploy:
    /portal                       (home: noti + order + return latest lists)
    /portal/notification          (full notification list)
    /portal/knowledge             (sidebar + article grid)
    /portal/purchase-history      (sale order list)
    /portal/return                (return request list)

Idempotent: mọi record dùng marker `[UI12]` trong name / `ui12-` slug
prefix, search-or-create. Chạy nhiều lần KHÔNG nhân đôi.

Run trên Windows server (D:\\wujia-tea):
    cd D:\\wujia-tea
    $env:PYTHONUTF8 = "1"
    $env:PYTHONIOENCODING = "utf-8"
    chcp 65001
    [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
    nssm stop Odoo
    python odoo19\\odoo-bin shell `
        -c config\\odoo-server.conf `
        -d wujia_tea_19 --no-http `
        < scripts\\seed_ui12_demo.py
    nssm start Odoo

Run local dev (Linux):
    cd /home/huyban/odoo-dev/WujiaTea/odoo19
    /home/huyban/miniconda3/envs/odoo/bin/python odoo-bin shell \\
        -c /home/huyban/odoo-dev/WujiaTea/config/odoo.conf \\
        -d wujia_tea_19 --no-http \\
        < /home/huyban/odoo-dev/WujiaTea/scripts/seed_ui12_demo.py
"""
from datetime import datetime, timedelta

MARKER = '[UI12]'
SLUG_PREFIX = 'ui12-'

print(f"=== SEEDING SPRINT 9.13 UI-12 DEMO DATA (marker={MARKER}) ===")


def upsert(model, domain, vals, label):
    Model = env[model]
    rec = Model.search(domain, limit=1)
    if rec:
        rec.write(vals)
        print(f"  [UPDATE] {label}: {rec.display_name or rec.id}")
    else:
        rec = Model.create(vals)
        print(f"  [CREATE] {label}: {rec.display_name or rec.id}")
    return rec


now = datetime.now()
today = now.date()

# ---------- Franchises (lookup) ----------
print("\n[1] Franchise lookup")
franchises = env['wujia.franchise.management'].search([], limit=3)
if not franchises:
    print("  ERROR: Không có franchise. Cần `wujia_portal_base/data/sample_data.xml` trước.")
    raise SystemExit(1)
print(f"  Found {len(franchises)} franchise: {franchises.mapped('name')}")

# ---------- 1. Notifications (5 record) ----------
print(f"\n[2] Notifications (5 records {MARKER})")
ntypes = {t.code: t for t in env['wujia.notification.type'].search([])}
noti_samples = [
    ('URG',   'Cập nhật giá sản phẩm tháng 6 — áp dụng từ 01/06',  'urgent'),
    ('GEN',   'Lịch giao hàng tuần này có thay đổi do kho HQ kiểm kê', 'normal'),
    ('PROMO', 'Combo sinh nhật khách hàng — khởi động chương trình', 'normal'),
    ('SYS',   'Bảo trì hệ thống POS đêm 30/05 từ 22h–24h', 'normal'),
    ('GEN',   'Mời họp đối tác nhượng quyền tháng 6 — link Google Meet', 'normal'),
]
for i, (code, title, prio) in enumerate(noti_samples):
    name = f'{MARKER} {title}'
    upsert(
        'wujia.notification',
        [('name', '=', name)],
        {
            'name': name,
            'type_id': ntypes.get(code).id if ntypes.get(code) else False,
            'dispatch_number': f'CV-UI12-{i+1:03d}',
            'date': now - timedelta(hours=i*6),
            'content': (
                f'<p><strong>{title}</strong></p>'
                f'<p>Nội dung demo UI-12 cho thông báo #{i+1}. Vui lòng xem kỹ và phản hồi nếu có thắc mắc.</p>'
                f'<ul><li>Áp dụng cho toàn bộ cửa hàng nhượng quyền</li><li>Hiệu lực từ {today.isoformat()}</li></ul>'
            ),
            'franchise_ids': [(6, 0, franchises.ids)],
            'published': True,
            'priority': prio,
        },
        f'noti #{i+1}',
    )

# ---------- 2. Knowledge: 2 category + 5 article ----------
print(f"\n[3] Knowledge categories + articles {MARKER}")
cat_ops = upsert(
    'wujia.knowledge.category',
    [('code', '=', f'{SLUG_PREFIX}ops')],
    {'code': f'{SLUG_PREFIX}ops', 'name': f'{MARKER} Vận hành', 'sequence': 10,
     'description': 'Demo category vận hành cửa hàng.'},
    'cat ops',
)
cat_prod = upsert(
    'wujia.knowledge.category',
    [('code', '=', f'{SLUG_PREFIX}prod')],
    {'code': f'{SLUG_PREFIX}prod', 'name': f'{MARKER} Sản phẩm', 'sequence': 20,
     'description': 'Demo category sản phẩm + pha chế.'},
    'cat prod',
)

article_samples = [
    (cat_ops,  'Checklist mở cửa hàng buổi sáng',  'mandatory', 'published'),
    (cat_ops,  'Quy trình giao ca giữa nhân viên',  'important', 'published'),
    (cat_prod, 'Công thức Hồng Trà Sữa size M',     'mandatory', 'published'),
    (cat_prod, 'Pha trà Đào Olong size L',          'new',       'published'),
    (cat_prod, 'Cách bảo quản nguyên liệu trong tủ mát', 'important', 'published'),
]
for i, (cat, title, badge, state) in enumerate(article_samples):
    slug = f'{SLUG_PREFIX}{i+1:02d}'
    name = f'{MARKER} {title}'
    upsert(
        'wujia.knowledge.article',
        [('slug', '=', slug)],
        {
            'name': name,
            'slug': slug,
            'category_id': cat.id,
            'summary': f'Tóm tắt demo cho bài {title}. Mục đích test giao diện UI-12.',
            'content': f'<h3>{title}</h3><p>Nội dung demo chi tiết cho bài viết. Mục tiêu kiểm tra rendering grid knowledge card.</p>',
            'state': state,
            'portal_badge': badge,
            'publish_date': now - timedelta(days=i),
            'sequence': 10 + i,
        },
        f'article #{i+1}',
    )

# ---------- 3. Return requests (5 record, 5 state) ----------
print(f"\n[4] Return requests (5 records {MARKER})")
error_types = env['wujia.return.error.type'].search([], limit=5)
states = ['draft', 'sent', 'approved', 'rejected', 'done']
state_labels = {'draft': 'Nháp', 'sent': 'Đã gửi', 'approved': 'Đã duyệt',
                'rejected': 'Từ chối', 'done': 'Hoàn thành'}
for i, st in enumerate(states):
    code = f'WJ-RR/UI12/{i+1:03d}'
    upsert(
        'wujia.return.request',
        [('name', '=', code)],
        {
            'name': code,
            'franchise_id': franchises[i % len(franchises)].id,
            'request_date': now - timedelta(days=i),
            'state': st,
            'error_id': error_types[i % len(error_types)].id if error_types else False,
            'note': f'{MARKER} Yêu cầu đổi trả demo #{i+1} — trạng thái {state_labels[st]}',
            'expected_delivery_date': today + timedelta(days=3),
            'refuse_reason': 'Không đủ chứng cứ ảnh' if st == 'rejected' else False,
        },
        f'return #{i+1} {st}',
    )

# ---------- 4. Sale orders (5 record, mix state) ----------
print(f"\n[5] Sale orders (5 records {MARKER})")
SO = env['sale.order']
Member = env['wujia.franchise.member']
products = env['product.product'].search([], limit=5)
if not products:
    print("  WARNING: không có product nào — bỏ qua tạo SO.")
else:
    # 5 orders: 2 draft, 2 confirmed (sale), 1 cancel
    order_plan = [
        ('draft',  3),  # qty 3
        ('sale',   5),
        ('draft',  2),
        ('sale',   8),
        ('cancel', 4),
    ]
    for i, (target_state, qty) in enumerate(order_plan):
        franch = franchises[i % len(franchises)]
        client_ref = f'WJ-UI12-SO-{i+1:03d}'
        membership = Member.search(
            [('franchise_id', '=', franch.id), ('is_currently_valid', '=', True)],
            limit=1,
        )
        if not membership:
            print(f"  WARNING: franchise {franch.name} chưa có member valid — bỏ qua SO #{i+1}")
            continue
        existing = SO.search([('client_order_ref', '=', client_ref)], limit=1)
        if existing:
            print(f"  [SKIP] SO {client_ref} đã tồn tại: {existing.name} ({existing.state})")
            continue
        partner = franch.partner_id or env['res.partner'].search([('is_company', '=', True)], limit=1)
        so = SO.create({
            'partner_id': partner.id,
            'is_portal_order': True,
            'franchise_id': franch.id,
            'franchise_partner_id': partner.id,
            'portal_requester_user_id': membership.user_id.id,
            'portal_member_id': membership.id,
            'client_order_ref': client_ref,
            'origin': f'Wujia Portal {MARKER}',
            'date_order': now - timedelta(days=i),
            'order_line': [(0, 0, {
                'product_id': products[i % len(products)].id,
                'product_uom_qty': qty,
            })],
        })
        if target_state in ('sale', 'cancel'):
            so.action_confirm()
        if target_state == 'cancel':
            so._action_cancel() if hasattr(so, '_action_cancel') else so.action_cancel()
        print(f"  [CREATE] SO {client_ref}: {so.name} → state={so.state}")

# ---------- Commit ----------
env.cr.commit()
print(f"\n=== DONE — đã commit transaction ===")
print("Verify:")
print("  /portal                    → 4 KPI card + 3 latest list (5 noti / 5 order / 5 return)")
print("  /portal/notification       → 5 noti record")
print("  /portal/knowledge          → 2 category + 5 article")
print("  /portal/purchase-history   → 5 sale order (2 draft, 2 confirmed, 1 cancel)")
print("  /portal/return             → 5 return request (full 5 state)")
