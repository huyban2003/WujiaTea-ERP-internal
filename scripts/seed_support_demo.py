"""Seed demo data for wujia_portal_support (full BA spec).

Idempotent. Creates support tickets in mixed states/categories,
some linked to existing sale orders / picking batches seeded by
seed_portal_demo.py. Categories are loaded from XML data file at
module install; this script only adds tickets on top.

Run AFTER seed_portal_demo.py:
    cd /home/huyban/odoo-dev/WujiaTea/odoo19
    /home/huyban/miniconda3/envs/odoo/bin/python odoo-bin shell \\
        -c /home/huyban/odoo-dev/WujiaTea/config/odoo.conf \\
        -d wujia_tea_19 --no-http \\
        < /home/huyban/odoo-dev/WujiaTea/scripts/seed_support_demo.py
"""
from datetime import datetime, timedelta

print("=== SEEDING WUJIA_PORTAL_SUPPORT DEMO DATA ===")


def upsert(model_name, search_domain, vals, label):
    Model = env[model_name]
    rec = Model.search(search_domain, limit=1)
    if rec:
        rec.write(vals)
        print(f"  [UPDATE] {label}: {rec.display_name or rec.id}")
    else:
        rec = Model.create(vals)
        print(f"  [CREATE] {label}: {rec.display_name or rec.id}")
    return rec


# -----------------------------------------------------------------
# Pre-checks
# -----------------------------------------------------------------
franchises = env['wujia.franchise.management'].search([], limit=3)
if not franchises:
    print("WARNING: no franchise found. Run seed_admin_franchise.py first.")
    raise SystemExit

categories = env['wujia.support.category'].search([], order='sequence')
if not categories:
    print("WARNING: no support category found. Module install should seed them.")
    raise SystemExit

cat_by_code = {c.code: c for c in categories}
admin = env.ref('base.user_admin')

# Pull a sale.order from each franchise (if seed_portal_demo has run).
SO = env['sale.order']
Batch = env['stock.picking.batch']
some_so = SO.search([('franchise_id', '!=', False)], limit=3)
some_batch = Batch.search([], limit=2)

print(f"\n[INFO] franchises={len(franchises)}, categories={len(categories)}, "
      f"sale_orders_with_franchise={len(some_so)}, batches={len(some_batch)}")

# -----------------------------------------------------------------
# Tickets — mix state, priority, links
# -----------------------------------------------------------------
now = datetime.now()

tickets = [
    {
        'title': 'Không đặt được đơn hàng — POS treo',
        'description': '<p>POS treo ở bước xác nhận thanh toán đã 2 lần trong sáng.</p>',
        'franchise_id': franchises[0].id,
        'created_by_id': admin.id,
        'category_id': cat_by_code['pos'].id,
        'priority': 'urgent',
        'state': 'new',
    },
    {
        'title': 'Sai số lượng giao trà ô long',
        'description': '<p>Đơn giao thiếu 2 hộp trà ô long.</p>',
        'franchise_id': franchises[0].id,
        'created_by_id': admin.id,
        'category_id': cat_by_code['delivery'].id,
        'priority': 'normal',
        'state': 'in_progress',
        'assigned_user_id': admin.id,
        'in_progress_date': now - timedelta(hours=4),
        'sale_order_id': some_so[:1].id if some_so else False,
        'picking_batch_id': some_batch[:1].id if some_batch else False,
    },
    {
        'title': 'Reset mật khẩu user POS',
        'description': '<p>Nhân viên mới cần quyền POS.</p>',
        'franchise_id': franchises[min(1, len(franchises) - 1)].id,
        'created_by_id': admin.id,
        'category_id': cat_by_code['account'].id,
        'priority': 'normal',
        'state': 'waiting_customer',
        'assigned_user_id': admin.id,
        'in_progress_date': now - timedelta(days=1),
        'last_message_date': now - timedelta(hours=12),
        'last_response_by': 'hq',
        'need_customer_reply': True,
    },
    {
        'title': 'Đã giải quyết — sai mã sản phẩm trên portal',
        'description': '<p>Mã SP TR-001 hiển thị nhầm tên.</p>',
        'franchise_id': franchises[min(2, len(franchises) - 1)].id,
        'created_by_id': admin.id,
        'category_id': cat_by_code['product'].id,
        'priority': 'normal',
        'state': 'resolved',
        'assigned_user_id': admin.id,
        'in_progress_date': now - timedelta(days=3),
        'resolved_date': now - timedelta(days=2),
    },
    {
        'title': 'Đóng — yêu cầu hỗ trợ marketing Tết',
        'description': '<p>Cần bộ banner Tết.</p>',
        'franchise_id': franchises[0].id,
        'created_by_id': admin.id,
        'category_id': cat_by_code['operation'].id,
        'priority': 'normal',
        'state': 'closed',
        'closed_date': now - timedelta(days=10),
    },
    {
        'title': 'Đặt nhầm — yêu cầu huỷ',
        'description': '<p>Đặt nhầm đơn 2 lần.</p>',
        'franchise_id': franchises[0].id,
        'created_by_id': admin.id,
        'category_id': cat_by_code['order'].id,
        'priority': 'normal',
        'state': 'cancelled',
        'cancel_reason': 'Cửa hàng chủ động huỷ — đã đặt trùng.',
    },
]

for vals in tickets:
    upsert(
        'wujia.support.ticket',
        [('title', '=', vals['title'])],
        vals,
        f'ticket: {vals["title"][:40]}',
    )

env.cr.commit()
print("\n=== DONE ===")
