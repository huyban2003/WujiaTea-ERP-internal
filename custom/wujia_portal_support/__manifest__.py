{
    'name': 'Wujia Portal — Support Tickets',
    'version': '19.0.2.0.0',
    'category': 'Wujia',
    'summary': 'Yêu cầu hỗ trợ từ cửa hàng nhượng quyền — backend + portal',
    'author': 'WujiaTea',
    'license': 'LGPL-3',
    'depends': ['wujia_portal_base', 'mail', 'wujia_franchise'],
    'data': [
        'security/ir.model.access.csv',
        'security/wujia_support_rules.xml',
        'data/ir_sequence_data.xml',
        'views/wujia_support_backend_views.xml',
        'views/sidenav_inherit.xml',
        'views/portal_support.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'wujia_portal_support/static/src/css/portal_support.css',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
}
