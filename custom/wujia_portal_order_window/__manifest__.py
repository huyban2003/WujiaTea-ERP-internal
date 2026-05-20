{
    'name': 'Wujia Portal Order Window',
    'version': '19.0.1.0.0',
    'category': 'Wujia',
    'summary': 'Khung giờ cho phép portal đặt hàng (BA Section B.5)',
    'description': """
Cấu hình khung giờ portal được phép tạo sale.order.
- res.config.settings: order_from (Float), order_to (Float),
  portal_order_time_limit_enabled (Boolean) — lưu vào ir.config_parameter
  với key wujia_portal.*.
- helper is_within_order_window() — handle 2 trường hợp from<to và from>to,
  check theo timezone user.
- override sale.order.create chặn order portal ngoài khung giờ (defense in depth).
""",
    'author': 'WujiaTea',
    'license': 'LGPL-3',
    'depends': ['wujia_sale'],
    'data': [
        'views/res_config_settings_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
