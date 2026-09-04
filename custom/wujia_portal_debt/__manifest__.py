{
    'name': 'Wujia Portal — Công nợ & thanh toán',
    'version': '19.0.4.3.0',
    'category': 'Wujia',
    'summary': 'Công nợ theo tuần, lịch sử thanh toán và màn chuyển khoản (portal mobile + PC)',
    'description': """
Wujia Portal — Công nợ & thanh toán
===================================
Dựng 7 màn Figma ``WJ_Debt_..._MVP_v31`` (page Dashboard, node 5013).

**Sprint 43** — UI-only (seam ``wujia.portal.debt`` trả dict thuần, 0 query).
**Sprint 48** — wire backend thật (BA task Tasks!STT9, Controller CT-050..CT-055):
seam đọc ``account.move``/``account.payment`` scope theo ``franchise_id`` (3 field custom
ở module ``wujia_account``), badge công nợ dùng field store perf, controller chặn Staff.
Template/CSS/JS KHÔNG đổi — chỉ ruột seam + controller guard.
**Sprint 49** — giao diện PC 1920×1080 (BA task Tasks!STT10, Figma ``WJ_Debt_PC_MVP_v1_1``
node 5077): khối desktop ``.wj-debt-pc`` (d-none d-lg-block) bám hệ ``wj-pc-*``/shell
``pc_source_ui_v1_5`` — tab Công nợ/Lịch sử, filter, summary 3 cột (5 biến thể state),
bảng hoá đơn phân trang, empty box, modal QR. Mobile giữ nguyên (bọc ``d-lg-none``).
Seam mở rộng **additive** (mỗi hoá đơn thêm ``total/paid/remaining``; ``get_payments``
thêm ``keyword``) + controller thêm context PC — KHÔNG đổi field/rule/migration.
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
