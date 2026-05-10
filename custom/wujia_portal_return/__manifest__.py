{
    'name': 'Wujia Portal — Return Request',
    'version': '19.0.1.0.0',
    'category': 'Wujia',
    'summary': 'Đổi trả hàng portal — list, create, detail (skeleton model + UI)',
    'author': 'WujiaTea',
    'license': 'LGPL-3',
    'depends': ['wujia_sale', 'wujia_portal_base'],
    'data': [
        'security/ir.model.access.csv',
        'security/wujia_return_rules.xml',
        'data/ir_sequence_data.xml',
        'data/return_error_type_data.xml',
        'views/sidenav_inherit.xml',
        'views/portal_return_list.xml',
        'views/portal_return_form.xml',
        'views/portal_return_detail.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'wujia_portal_return/static/src/css/portal_return.css',
            'wujia_portal_return/static/src/js/portal_return.js',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
}
