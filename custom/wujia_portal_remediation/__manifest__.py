# -*- coding: utf-8 -*-
{
    'name': 'Wujia Portal — Remediation (Khắc phục)',
    'version': '19.0.1.0.0',
    'category': 'Wujia',
    'summary': 'Giao diện Portal Khắc phục cửa hàng nhượng quyền',
    'author': 'WujiaTea',
    'license': 'LGPL-3',
    'depends': ['wujia_portal_base', 'wujia_portal_layout', 'wujia_franchise'],
    'data': [
        'security/ir.model.access.csv',
        'views/sidenav_inherit.xml',
        'views/portal_remediation_templates.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
