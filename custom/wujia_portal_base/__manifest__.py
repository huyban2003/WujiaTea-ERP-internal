{
    'name': 'Wujia Portal Base',
    'version': '19.0.2.0.0',
    'category': 'Wujia',
    'summary': 'Portal layer cho cửa hàng nhượng quyền + real-time member updates',
    'author': 'WujiaTea',
    'license': 'LGPL-3',
    'depends': ['wujia_franchise', 'wujia_portal_layout', 'portal', 'bus'],
    'data': [
        'views/portal_templates.xml',
        'views/portal_franchises_in_layout.xml',
        'data/sample_data.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'wujia_portal_base/static/src/js/franchise_realtime.js',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
}
