# -*- coding: utf-8 -*-
{
    'name': "View fields value",

    'summary': """
        This module allows you to see all fields value of current form""",

    'description': """
        Sometime we want to see value of field that is not visible on the form view
        If this is your case this apps is made for you
    """,

    'author': "Apanda",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        'views/assets_backend.xml',
        'views/views.xml',
    ],
    'license': 'AGPL-3',

    'images': ['static/description/cover.gif'],
}