{
    'name': 'Wujia Portal — Support Tickets',
    'version': '19.0.1.0.0',
    'category': 'Wujia',
    'summary': 'Yêu cầu hỗ trợ từ cửa hàng nhượng quyền (skeleton — có mail.thread cho conversation)',
    'author': 'WujiaTea',
    'license': 'LGPL-3',
    'depends': ['wujia_portal_base', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'security/wujia_support_rules.xml',
        'data/ir_sequence_data.xml',
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
