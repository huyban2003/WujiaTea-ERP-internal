{
    'name': 'Wujia Portal — Công nợ & thanh toán',
    'version': '19.0.2.2.0',
    'category': 'Wujia',
    'summary': 'Công nợ theo tuần, lịch sử thanh toán và màn chuyển khoản (portal mobile)',
    'description': """
Wujia Portal — Công nợ & thanh toán
===================================
Dựng 7 màn Figma ``WJ_Debt_..._MVP_v31`` (page Dashboard, node 5013).

**Sprint 43** — UI-only (seam ``wujia.portal.debt`` trả dict thuần, 0 query).
**Sprint 48** — wire backend thật (BA task Tasks!STT9, Controller CT-050..CT-055):
seam đọc ``account.move``/``account.payment`` scope theo ``franchise_id`` (3 field custom
ở module ``wujia_account``), badge công nợ dùng field store perf, controller chặn Staff.
Template/CSS/JS KHÔNG đổi — chỉ ruột seam + controller guard.
""",
    'author': 'WujiaTea',
    'license': 'LGPL-3',
    'depends': ['wujia_portal_base', 'wujia_account'],
    'data': [
        'views/portal_debt.xml',
        'views/bottomnav_inherit.xml',
        'views/home_kpi_inherit.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'wujia_portal_debt/static/src/css/portal_debt.css',
            'wujia_portal_debt/static/src/js/portal_debt.js',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
}
