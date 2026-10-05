{
    'name': 'Wujia Translations',
    'version': '19.0.1.1.0',
    'category': 'Wujia',
    'summary': 'Translation catalog: scan, edit, apply instantly, keep edits across module upgrades',
    'description': """
Backend translation tool (cluster J, sessions J-T1+T2):
- Scan module strings (same source as Odoo's .pot export) into a term x language catalog
- Edit translations in place; filter untranslated / edited / waiting to apply; coverage per module
- Apply instantly to labels, menus, views and QWeb templates (no restart); edits are re-applied after every -u
- Python/JS strings: edited here, take effect after .po export + restart (J-T4)
""",
    'author': 'WujiaTea',
    'license': 'LGPL-3',
    'depends': ['base', 'web'],
    'data': [
        'security/i18n_security.xml',
        'data/res_lang_data.xml',
        'security/ir.model.access.csv',
        'wizard/scan_wizard_views.xml',
        'views/i18n_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
