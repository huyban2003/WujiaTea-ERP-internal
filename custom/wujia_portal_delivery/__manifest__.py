{
    'name': 'Wujia Portal — Delivery Tracking',
    'version': '19.0.1.1.0',
    'category': 'Wujia',
    'summary': 'Theo dõi chuyến giao hàng portal — list batch + detail (skeleton UI)',
    'author': 'WujiaTea',
    'license': 'LGPL-3',
    'depends': ['wujia_delivery', 'wujia_portal_base'],
    'data': [
        'views/sidenav_inherit.xml',
        'views/portal_delivery.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'wujia_portal_delivery/static/src/css/portal_delivery.css',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
}
