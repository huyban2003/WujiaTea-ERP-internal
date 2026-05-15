{
    'name': 'Wujia Portal — Knowledge Library',
    'version': '19.0.2.0.0',
    'category': 'Wujia',
    'summary': 'Thư viện kiến thức / blog / SOP cho cửa hàng nhượng quyền',
    'author': 'WujiaTea',
    'license': 'LGPL-3',
    'depends': ['wujia_portal_base', 'wujia_franchise'],
    'data': [
        'security/ir.model.access.csv',
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
