{
    'name': 'Wujia Portal — Sale (Catalog + Cart)',
    'version': '19.0.2.5.0',
    'category': 'Wujia',
    'summary': 'Trang đặt hàng portal — catalog sản phẩm + giỏ hàng (skeleton UI)',
    'author': 'WujiaTea',
    'license': 'LGPL-3',
    'depends': ['wujia_sale', 'wujia_portal_base', 'wujia_portal_order_window'],
    'data': [
        'views/sidenav_inherit.xml',
        'views/header_cart_inherit.xml',
        'views/portal_order_catalog.xml',
        'views/portal_order_product_detail.xml',
        'views/portal_order_cart.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'wujia_portal_sale/static/src/css/portal_order.css',
            'wujia_portal_sale/static/src/js/portal_order.js',
            'wujia_portal_sale/static/src/js/header_cart_badge.js',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
}
