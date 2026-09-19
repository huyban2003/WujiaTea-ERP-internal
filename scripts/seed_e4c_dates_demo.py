"""Seed cho lượt E4c (FilterBar — wiring ngày).

Vì sao cần: phép đo "lọc ngày áp dụng thật" và "sang trang giữ lọc" đòi mỗi màn
có >1 trang VÀ bản ghi trải trên nhiều ngày. Sau seed E3/E3c thì Thi, Giao hàng,
Đổi trả, Thông báo đã đủ; riêng Lịch sử đặt hàng + Báo cáo chỉ có 6 đơn cùng MỘT
ngày ⇒ lọc ngày nào cũng ra y hệt, đo xong vẫn không biết lọc có chạy không.

Idempotent qua `client_order_ref` mang dấu SEED-E4C.

LOCAL-ONLY — chạy trên DB copy, KHÔNG chạy trên wujia_tea_19 hay production.

    python3 odoo19/odoo-bin shell -c <conf> -d <db-copy> --no-http \
        < scripts/seed_e4c_dates_demo.py
"""
from datetime import datetime, timedelta

MARK = 'SEED-E4C'
TARGET = 45

print('=== SEED E4C — ĐƠN HÀNG TRẢI NGÀY ===')

franchise = env['wujia.franchise.management'].search([('code', '=', 'HCM-01')], limit=1)
if not franchise:
    franchise = env['wujia.franchise.management'].search([], order='code', limit=1)
print('Franchise: [%s] %s (id=%s)' % (franchise.code, franchise.name, franchise.id))

SO = env['sale.order']
src = SO.search([('franchise_id', '=', franchise.id), ('state', '!=', 'cancel')],
                order='id desc', limit=1)
if not src:
    raise SystemExit('Không có đơn mẫu của cửa hàng — seed portal demo trước.')

have = SO.search_count([('franchise_id', '=', franchise.id),
                        ('client_order_ref', 'like', MARK)])
now = datetime.now()
made = []
for i in range(have, TARGET):
    ref = '%s-%03d' % (MARK, i + 1)
    if SO.search_count([('client_order_ref', '=', ref)]):
        continue
    order = src.copy({'client_order_ref': ref, 'franchise_id': franchise.id})
    made.append((order.id, now - timedelta(days=i)))

# `create_date` là trường hệ thống, ORM không cho ghi ⇒ lùi ngày bằng SQL, chỉ
# trên DB copy. `date_order` ghi được qua ORM nên để ORM lo, giữ hai mốc khớp nhau.
for oid, when in made:
    SO.browse(oid).sudo().write({'date_order': when})
    env.cr.execute('UPDATE sale_order SET create_date = %s WHERE id = %s', (when, oid))

print('Đơn hàng: %d → %d (+%d), trải %d ngày'
      % (have, have + len(made), len(made), TARGET))
env.cr.commit()
print('=== XONG ===')
