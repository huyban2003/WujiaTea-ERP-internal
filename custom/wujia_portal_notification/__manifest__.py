{
    'name': 'Wujia Portal — Notification',
    'version': '19.0.1.7.0',
    'category': 'Wujia',
    'summary': 'Thông báo HQ → cửa hàng nhượng quyền (skeleton)',
    'author': 'WujiaTea',
    'license': 'LGPL-3',
    'depends': ['wujia_portal_base', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'security/wujia_notification_rules.xml',
        'data/notification_type_data.xml',
        'views/sidenav_inherit.xml',
        'views/header_bell_inherit.xml',
        'views/portal_notification.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'wujia_portal_notification/static/src/css/portal_notification.css',
            'wujia_portal_notification/static/src/js/header_bell_badge.js',
            'wujia_portal_notification/static/src/js/portal_notification_pc.js',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
}
