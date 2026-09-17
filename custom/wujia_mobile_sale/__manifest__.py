# -*- coding: utf-8 -*-
{
    'name': 'Wujia Mobile Sale',
    'version': '19.0.1.0.0',
    'category': 'Wujia/Mobile',
    'summary': 'Responsive Mobile Kanban and Form Views for Wujia Sales Orders',
    'author': 'WujiaTea',
    'license': 'LGPL-3',
    'depends': [
        'wujia_mobile_core',
        'wujia_sale',
    ],
    'data': [
        'views/sale_order_mobile_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
