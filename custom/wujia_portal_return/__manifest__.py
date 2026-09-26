{
    'name': 'Wujia Portal — Return Request',
    'version': '19.0.4.0.0',
    'category': 'Wujia',
    'summary': 'Portal đổi trả / bù hàng — danh sách, tạo yêu cầu, chi tiết (nghiệp vụ ở wujia_return).',
    'author': 'WujiaTea',
    'license': 'LGPL-3',
    'depends': ['wujia_portal_base', 'wujia_return'],
    'data': [
        'views/bottomnav_inherit.xml',
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
