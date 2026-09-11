"""Seed dữ liệu cho cụm D6 (Bù hàng — UAT-BH-007/008/009).

Vì sao cần: DB dev KHÔNG tái hiện được BH-007 và chỉ tái hiện 1/4 BH-008.
Đo trên `wujia_tea_d5h2` ngày 10/09/2026:

  * 35/35 phiếu bù hàng có `product_id` RỖNG. Seed D5 tưởng đã gán — nhưng
    `product_id` là related+store **readonly** từ `sale_order_line_id`
    (wujia_return_request.py:71-75), nên ORM bỏ qua giá trị ghi thẳng và
    tính lại ra False. Card rơi vào nhánh fallback `issue_type_id.name`
    ⇒ đo tên sản phẩm là đo nhầm ô.
  * Tên sản phẩm dài nhất toàn DB = 25 ký tự, không có tên song ngữ/CJK nào
    ⇒ dòng `white-space:nowrap` của card CHƯA HỀ tràn ⇒ BH-007 "Pass rỗng".
  * Chỉ 1 phiếu có `resolution_type='compensation'` (status `partial`)
    ⇒ 3/4 biến thể badge "Tiến độ bù" không có bản ghi nào để đo.

Đây đúng bẫy D5h.1 (bảng *Kết quả thi* ẩn sau `state=='confirmed'` nên bộ đo
báo sạch): không seed đủ trạng thái thì bảng đo xanh mà lỗi vẫn còn.

`compensation_status` cũng là computed store (từ `allocation_ids`), nên muốn
có đủ none/allocated/partial/done thì phải tạo allocation thật, không ghi thẳng.

Idempotent: mọi bản ghi mang dấu SEED-D6 và được search-or-create.
LOCAL-ONLY — chạy trên DB copy, KHÔNG chạy trên wujia_tea_19 hay production.

    cd /home/huyban/odoo-dev/WujiaTea
    python3 odoo19/odoo-bin shell -c config/odoo.conf -d <db-copy> --no-http \
        --logfile=<thư-mục>/x.log < scripts/seed_d6_return_demo.py
"""
from datetime import datetime, timedelta

MARK = 'SEED-D6'

print("=== SEED D6 — BÙ HÀNG ===")

franchise = env['wujia.franchise.management'].search([('code', '=', 'HN-01')], limit=1)
if not franchise:
    franchise = env['wujia.franchise.management'].search([], order='code', limit=1)
if not franchise:
    raise SystemExit("Không có franchise nào.")
print(f"Franchise: [{franchise.code}] {franchise.name} (id={franchise.id})")

now = datetime.now()
uom = env.ref('uom.product_uom_unit')
partner = franchise.partner_id or env.ref('base.user_admin').partner_id

# --------------------------------------------------------------- sản phẩm
# Ba mốc độ dài, có CJK, để đo đúng ngưỡng "tối đa 2 dòng" của BH-007.
# Không đổi tên sản phẩm có sẵn (BA: "Không thay đổi tên sản phẩm trong Odoo")
# — đây là sản phẩm MỚI mang dấu SEED-D6.
PRODUCTS = [
    ('D6-SHORT', 'Trà Sữa Trân Châu'),
    ('D6-MED', '波霸奶茶 Trà Sữa Trân Châu Đường Đen size L'),
    ('D6-LONG', '黑糖波霸厚乳鮮奶茶 Trà Sữa Trân Châu Đường Đen Hoàng Kim '
                'size L (thùng 24 bịch × 1kg) — NCC Đài Loan'),
]
products = env['product.product']
for code, name in PRODUCTS:
    p = env['product.product'].search([('default_code', '=', code)], limit=1)
    if not p:
        p = env['product.product'].create({
            'name': name, 'default_code': code, 'type': 'consu',
            'list_price': 120000.0, 'uom_id': uom.id,
        })
        print(f"  + sản phẩm {code}: {len(name)} ký tự")
    else:
        p.write({'name': name})
        print(f"  = sản phẩm {code}: {len(name)} ký tự (đã có)")
    products |= p

# ----------------------------------------------------------- đơn hàng gốc
# Giữ ở `draft`: card chỉ đọc `sale_order_id.name`, không cần confirm.
# (QA §10 — không tạo/confirm đơn thật.)
so = env['sale.order'].search([('client_order_ref', '=', MARK)], limit=1)
if not so:
    so = env['sale.order'].create({
        'partner_id': partner.id,
        'franchise_id': franchise.id,
        'client_order_ref': MARK,
        'order_line': [(0, 0, {
            'product_id': p.id, 'product_uom_qty': 50.0,
        }) for p in products],
    })
    print(f"  + đơn gốc {so.name} — {len(so.order_line)} dòng")
else:
    print(f"  = đơn gốc {so.name} (đã có)")
lines = {l.product_id.default_code: l for l in so.order_line}

issue_type = env['wujia.return.issue.type'].search([], limit=1)

# ------------------------------------------------------------ ma trận đo
# BH-008 cần đủ 4 biến thể `compensation_status`; BH-007 cần 3 mốc độ dài tên.
# `compensation_status` là computed store từ allocation ⇒ lái bằng
# (allocated_qty, delivered_qty) chứ không ghi thẳng field.
#   none      : không allocation
#   allocated : có allocation, delivered = 0
#   partial   : 0 < delivered < approved
#   done      : delivered >= approved
MATRIX = [
    # (hậu tố, state, resolution, product_code, approved, allocated, delivered)
    ('01', 'processing', 'compensation', 'D6-LONG',  10.0, 10.0,  0.0),   # allocated
    ('02', 'processing', 'compensation', 'D6-LONG',  10.0, 10.0,  4.0),   # partial
    ('03', 'done',       'compensation', 'D6-LONG',  10.0, 10.0, 10.0),   # done
    ('04', 'approved',   'compensation', 'D6-MED',    8.0,  0.0,  0.0),   # none
    ('05', 'processing', 'compensation', 'D6-MED',    8.0,  8.0,  3.0),   # partial
    ('06', 'done',       'compensation', 'D6-MED',    8.0,  8.0,  8.0),   # done
    ('07', 'processing', 'compensation', 'D6-SHORT',  5.0,  5.0,  0.0),   # allocated
    ('08', 'submitted',  'exchange',     'D6-LONG',   3.0,  0.0,  0.0),   # không có badge bù
    ('09', 'reviewing',  False,          'D6-MED',    2.0,  0.0,  0.0),
    ('10', 'rejected',   False,          'D6-SHORT',  1.0,  0.0,  0.0),
]

RR = env['wujia.return.request']
ALLOC = env['wujia.compensation.allocation']
created = 0
for suffix, state, resolution, pcode, approved, alloc_qty, deliv_qty in MATRIX:
    code = f'{MARK}/{suffix}'
    rr = RR.search([('name', '=', code)], limit=1)
    vals = {
        'name': code,
        'franchise_id': franchise.id,
        'request_date': now - timedelta(days=int(suffix)),
        'state': state,
        'sale_order_id': so.id,
        'sale_order_line_id': lines[pcode].id,
        'request_qty': approved,
        'approved_qty': approved,
        'request_uom_id': uom.id,
        'opening_datetime': now - timedelta(days=int(suffix), hours=2),
        'issue_type_id': issue_type.id if issue_type else False,
        'resolution_type': resolution,
        'note': f'Phiếu đo D6 {suffix}',
    }
    if rr:
        rr.write(vals)
    else:
        rr = RR.create(vals)
        created += 1
    # allocation lái compensation_status
    rr.allocation_ids.filtered(lambda a: a.name == code).unlink()
    if alloc_qty > 0:
        ALLOC.create({
            'name': code,
            'request_id': rr.id,
            'allocated_qty': alloc_qty,
            'allocation_uom_id': uom.id,
            'delivered_qty': deliv_qty,
            'state': 'done' if deliv_qty >= alloc_qty else (
                'partial' if deliv_qty > 0 else 'allocated'),
        })

RR.invalidate_model()
print(f"\n  + {created} phiếu mới / {len(MATRIX)} phiếu đo")
for suffix, state, resolution, pcode, *_ in MATRIX:
    rr = RR.search([('name', '=', f'{MARK}/{suffix}')], limit=1)
    print(f"    {rr.name:14s} state={rr.state:11s} res={str(rr.resolution_type):13s} "
          f"comp={str(rr.compensation_status):10s} sp={len(rr.product_id.display_name or '')} ký tự")

env.cr.commit()
print("\n=== XONG ===")
