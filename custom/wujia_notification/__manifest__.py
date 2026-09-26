{
    'name': 'Wujia Notifications',
    'version': '19.0.1.0.0',
    'category': 'Wujia',
    'summary': 'Thông báo HQ → cửa hàng nhượng quyền — soạn, chọn đối tượng, gửi, thu hồi, theo dõi đã đọc.',
    'description': """
Nghiệp vụ thông báo. Tách từ wujia_portal_notification (F11, ADR-027).

- Model wujia.notification (mã ANN/, chatter, chọn đối tượng nhận, gửi/thu hồi),
  wujia.notification.type (loại), wujia.notification.read (đã đọc theo user + cửa hàng).
- _portal_history_domain / _portal_effective_domain / _portal_unread_count / _mark_read /
  _portal_get_attachment: luật dùng chung cho mọi kênh.
""",
    'author': 'WujiaTea',
    'license': 'LGPL-3',
    'depends': ['mail', 'wujia_franchise'],
    'data': [
        'security/wujia_notification_groups.xml',
        'security/ir.model.access.csv',
        'security/wujia_notification_rules.xml',
        'data/ir_sequence_data.xml',
        'data/notification_type_data.xml',
        'views/backend_notification_views.xml',
        'views/backend_menu.xml',
    ],
    'pre_init_hook': 'pre_init_hook',
    'installable': True,
    'application': False,
    'auto_install': False,
}
