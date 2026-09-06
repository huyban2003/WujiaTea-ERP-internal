# -*- coding: utf-8 -*-
"""Seed sản phẩm portal — chạy TRƯỚC seed_portal_demo.py.

Không module nào ship sẵn product data, và reseed dùng --without-demo=True, nên
DB dựng mới không có sản phẩm nào. Hệ quả dây chuyền: khối [4] và [8] của
seed_portal_demo tự bỏ qua ⇒ không có đơn hàng ⇒ /portal/order, /portal/
purchase-history và /portal/reports/orders đều rỗng, tức là không đo được đúng
những màn cụm D4 cần.

Sản phẩm ở đây bám field portal của wujia_sale: is_public_portal, public_categ_id,
min_qty/max_qty, wujia_packaging (tên field sau khi B2 đổi khỏi description_ecommerce).
"""
from odoo import fields  # noqa: F401  (đồng bộ với các seed khác)

Category = env['wujia.product.category']
Product = env['product.product']

CATEGORIES = [
    ('Trà & nguyên liệu', 10),
    ('Topping', 20),
    ('Bao bì', 30),
]

# (tên, danh mục, giá, đơn vị đóng gói, min, max)
PRODUCTS = [
    ('Hồng trà Wujia 500g',        'Trà & nguyên liệu', 185000, 'Túi 500g',   1, 100),
    ('Trà xanh Wujia 500g',        'Trà & nguyên liệu', 195000, 'Túi 500g',   1, 100),
    ('Trà Ô long Wujia 500g',      'Trà & nguyên liệu', 245000, 'Túi 500g',   1,  80),
    ('Bột sữa Wujia 1kg',          'Trà & nguyên liệu', 165000, 'Bao 1kg',    1, 120),
    ('Trân châu đen 3kg',          'Topping',            98000, 'Bao 3kg',    1, 150),
    ('Thạch trái cây 2kg',         'Topping',            76000, 'Hộp 2kg',    1, 150),
    ('Ly nhựa 500ml (thùng 1000)', 'Bao bì',            420000, 'Thùng 1000', 1,  40),
    ('Ống hút giấy (thùng 2000)',  'Bao bì',            180000, 'Thùng 2000', 1,  40),
]

print("\n[P] Danh mục sản phẩm portal")
cats = {}
for name, seq in CATEGORIES:
    cat = Category.search([('name', '=', name)], limit=1)
    if not cat:
        cat = Category.create({'name': name, 'sequence': seq})
        print(f"  [CREATE] danh mục {name}")
    else:
        print(f"  [SKIP]   danh mục {name}")
    cats[name] = cat

print("\n[P] Sản phẩm portal")
created = 0
for name, cat_name, price, packaging, min_qty, max_qty in PRODUCTS:
    if Product.search_count([('name', '=', name)]):
        print(f"  [SKIP]   {name}")
        continue
    Product.create({
        'name': name,
        'type': 'consu',
        'is_storable': True,
        'sale_ok': True,
        'purchase_ok': True,
        'list_price': price,
        'is_public_portal': True,
        'public_categ_id': cats[cat_name].id,
        'wujia_packaging': packaging,
        'min_qty': min_qty,
        'max_qty': max_qty,
    })
    created += 1
    print(f"  [CREATE] {name}")

env.cr.commit()
print(f"\n=== DONE — {created} sản phẩm mới, {Product.search_count([('is_public_portal', '=', True)])} sản phẩm portal tổng cộng ===")
