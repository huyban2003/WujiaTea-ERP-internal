{
    'name': 'Wujia Portal — Knowledge Library',
    'version': '19.0.3.0.1',
    'category': 'Wujia',
    'summary': 'Thư viện kiến thức / blog / SOP cho cửa hàng nhượng quyền',
    'author': 'WujiaTea',
    'license': 'LGPL-3',
    'depends': ['wujia_portal_base', 'wujia_franchise', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'data/ir_cron_data.xml',
        'views/wujia_knowledge_backend_views.xml',
        'views/sidenav_inherit.xml',
        'views/portal_knowledge.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'wujia_portal_knowledge/static/src/css/portal_knowledge.css',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
}
