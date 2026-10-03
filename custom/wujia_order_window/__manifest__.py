{
    'name': 'Wujia Order Window',
    'version': '19.0.1.0.0',
    'category': 'Wujia',
    'summary': 'Khung giờ đặt hàng theo khu vực (BA Section B.5 + Model Field Mục I)',
    'description': """
Khung giờ được phép tạo đơn portal, cấu hình theo khu vực. Tách từ wujia_portal_order_window (F7, ADR-027).

- Model wujia.order.window: khung giờ riêng cho từng res.area; một khu vực có thể có nhiều khung (sáng + tối).
- res.config.settings: 3 tham số fallback wujia_portal.* khi khu vực chưa cấu hình riêng.
- _is_within_order_window(area_id): ưu tiên khu vực, fallback chung, xử lý qua nửa đêm theo tz người dùng.
- _next_order_window(area_id): khung sắp mở (giờ + ngày) cho màn "ngoài khung giờ".
- sale.order.create chặn đơn portal ngoài khung giờ, raise OrderWindowClosed.
""",
    'author': 'WujiaTea',
    'license': 'LGPL-3',
    'depends': ['wujia_sale'],
    'data': [
        'security/ir.model.access.csv',
        'views/wujia_order_window_views.xml',
        'views/res_config_settings_views.xml',
    ],
    'pre_init_hook': 'pre_init_hook',
    'installable': True,
    'application': False,
    'auto_install': False,
}
