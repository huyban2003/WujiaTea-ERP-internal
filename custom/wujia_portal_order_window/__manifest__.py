{
    'name': 'Wujia Portal Order Window',
    'version': '19.0.2.1.0',
    'category': 'Wujia',
    'summary': 'Khung giờ portal đặt hàng theo khu vực (BA Section B.5 + Model Field Mục I)',
    'description': """
Khung giờ portal được phép tạo sale.order, cấu hình theo khu vực.

Model:
- wujia.order.window (per-area, multi-record): khung giờ riêng cho từng res.area.
  Một khu vực có thể có nhiều khung giờ (vd sáng + tối).

Settings (fallback):
- res.config.settings: portal_order_time_from / to (Float),
  portal_order_time_limit_enabled (Boolean) — lưu ir.config_parameter
  wujia_portal.* — chỉ áp dụng khi khu vực chưa cấu hình riêng.

Helper:
- res.config.settings._is_within_order_window(area_id=None):
  ưu tiên wujia.order.window theo khu vực, fallback global,
  handle khung qua nửa đêm, check timezone user.

Defense in depth:
- sale.order.create override chặn portal order ngoài khung giờ
  (resolve area_id từ franchise_id).
""",
    'author': 'WujiaTea',
    'license': 'LGPL-3',
    'depends': ['wujia_sale'],
    'data': [
        'security/ir.model.access.csv',
        'views/wujia_order_window_views.xml',
        'views/res_config_settings_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
