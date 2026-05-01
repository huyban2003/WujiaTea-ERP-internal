{
    'name': 'Wujia Sale',
    'version': '19.0.2.0.0',
    'category': 'Wujia',
    'summary': 'Sale order extension cho cửa hàng nhượng quyền + tính khối lượng',
    'author': 'WujiaTea',
    'description': """
Mở rộng sale.order cho luồng đặt hàng từ portal (BA spec):
- is_portal_order: phân biệt đơn portal vs admin tạo manual.
- franchise_partner_id (M2o res.partner is_franchise=True).
- franchise_id (M2o wujia.franchise.management) — required nếu is_portal_order.
- portal_requester_user_id, portal_member_id (audit trail).
- area_id (related franchise_id.area_id, store).
- portal_delivery_street/phone/note: override địa chỉ giao theo đơn.

Tính khối lượng (BA spec mục 3):
- sale.order.line.weight_per_unit (snapshot từ product.weight, readonly).
- sale.order.line.planned_weight (compute = qty * weight_per_unit, store).
- sale.order.total_planned_weight (compute store).
- stock.move.weight_per_unit/planned_weight/done_weight.
- stock.picking.planned_weight/done_weight (aggregate).
- stock.picking.batch.planned_weight/done_weight (aggregate).

product.template thêm: is_public_website, min_qty, max_qty (cho portal catalog).
""",
    'license': 'LGPL-3',
    'depends': [
        'sale',
        'stock',
        'stock_picking_batch',
        'wujia_franchise',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/wujia_sale_rules.xml',
        'views/sale_order_views.xml',
        'views/product_template_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
