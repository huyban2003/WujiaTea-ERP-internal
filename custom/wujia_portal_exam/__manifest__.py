{
    'name': 'Wujia Portal — Exam (Đào tạo / Thi)',
    'version': '19.0.1.0.0',
    'category': 'Wujia',
    'summary': 'Lịch thi + đăng ký + kết quả (skeleton model + UI)',
    'author': 'WujiaTea',
    'license': 'LGPL-3',
    'depends': ['wujia_portal_base'],
    'data': [
        'security/ir.model.access.csv',
        'security/wujia_exam_rules.xml',
        'data/ir_sequence_data.xml',
        'views/sidenav_inherit.xml',
        'views/portal_exam.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'wujia_portal_exam/static/src/css/portal_exam.css',
            'wujia_portal_exam/static/src/js/portal_exam.js',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
}
