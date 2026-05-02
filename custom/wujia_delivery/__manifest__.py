{
    'name': 'Wujia Delivery',
    'version': '19.0.1.0.0',
    'category': 'Wujia',
    'summary': 'Điều phối giao hàng: gắn xe vào batch, tính cost, report đội xe / cửa hàng',
    'author': 'WujiaTea',
    'description': """
Điều phối giao hàng (BA spec mục B):

- Mở rộng sale.order: tự copy franchise_id xuống stock.picking khi confirm.
- Mở rộng stock.picking: franchise_id, area_id (related), vehicle_id (related từ batch),
  delivery_status, shipping_cost, drop_fee phân bổ theo planned_weight.
- Mở rộng stock.picking.batch: vehicle_id, capacity meter (is_over_capacity),
  pricelist_id (auto-suggest), shipping_cost / drop_fee_total / total_shipping_cost,
  planned/actual_departure, delivery_batch_status (parallel với native state).

Reports (SQL view):
- wujia.fleet.shipping.report: 1 row / batch — cost theo đội xe + chi tiết tải trọng.
- wujia.franchise.shipping.report: 1 row / picking — cost phân bổ theo cửa hàng.
""",
    'license': 'LGPL-3',
    'depends': [
        'wujia_fleet',
        'wujia_sale',
        'stock_picking_batch',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/stock_picking_views.xml',
        'views/stock_picking_batch_views.xml',
        'views/wujia_fleet_management_views.xml',
        'report/wujia_fleet_shipping_report_views.xml',
        'report/wujia_franchise_shipping_report_views.xml',
        'views/wujia_delivery_menu.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
