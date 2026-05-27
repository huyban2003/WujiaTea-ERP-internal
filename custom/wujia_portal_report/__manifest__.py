{
    'name': 'Wujia Portal — Báo cáo',
    'version': '19.0.1.2.0',
    'category': 'Wujia',
    'summary': 'Báo cáo đặt hàng cho Owner/Manager (BA Phase 1)',
    'description': 'Trang /portal/reports/orders với KPI cards + bar chart 12 tháng + top SP + state distribution. Staff bị block redirect.',
    'author': 'WujiaTea',
    'license': 'LGPL-3',
    'depends': ['wujia_sale', 'wujia_portal_base'],
    'data': [
        'views/sidenav_inherit.xml',
        'views/portal_report_orders.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'wujia_portal_report/static/src/css/portal_report.css',
            'wujia_portal_report/static/src/js/portal_report_charts.js',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
}
