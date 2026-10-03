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
    'category': 'Technical',
    'version': '19.0.1.0.0',

    'depends': ['base', 'web'],

    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'fields_value/static/src/js/fields_value.js',
            'fields_value/static/src/xml/fields_value.xml',
        ],
    },
    'license': 'AGPL-3',
    'images': ['static/description/cover.gif'],
}