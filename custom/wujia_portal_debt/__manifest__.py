{
    'name': 'Wujia Portal — Công nợ & thanh toán',
    'version': '19.0.1.0.0',
    'category': 'Wujia',
    'summary': 'Công nợ theo tuần, lịch sử thanh toán và màn chuyển khoản (portal mobile)',
    'description': """
Wujia Portal — Công nợ & thanh toán
===================================
Dựng 7 màn Figma ``WJ_Debt_..._MVP_v31`` (page Dashboard, node 5013).

**UI-ONLY** (chốt với chủ dự án 2026-07-31): BA chưa đặc tả model/field cho mục
"D. Quản lý công nợ nhượng quyền" (tab `1. Model/ Field` mới chỉ có tiêu đề), DB chưa
có field nối `account.move` ↔ franchise, và chính Figma ghi QR/ngân hàng là "minh họa".
Mọi số liệu đi qua **một** hàm duy nhất `wujia.portal.debt.get_summary()` — khi BA chốt
spec backend thì đổi nguồn trong hàm đó, template/controller không phải sửa.
""",
    'author': 'WujiaTea',
    'license': 'LGPL-3',
    'depends': ['wujia_portal_base'],
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
