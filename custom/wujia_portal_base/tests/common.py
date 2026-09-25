"""Test quét nhiều module chạy được khi `portal_base` cài một mình: thiếu module chủ ⇒ skip."""

# Module sở hữu mục điều hướng — sổ vàng menu chỉ so được khi đủ bộ.
PORTAL_SUITE = (
    'wujia_portal_sale', 'wujia_portal_delivery', 'wujia_portal_purchase_history',
    'wujia_portal_return', 'wujia_portal_debt', 'wujia_portal_report',
    'wujia_portal_support', 'wujia_portal_knowledge', 'wujia_portal_exam',
    'wujia_portal_notification', 'wujia_portal_info_request', 'wujia_portal_inspection',
)


def need(case, *refs):
    """`refs` là tên module hoặc xmlid/key `module.x`; module nào chưa cài thì skip test (hoặc subTest)."""
    Module = case.env['ir.module.module']
    missing = sorted({r.split('.', 1)[0] for r in refs if Module._get(r.split('.', 1)[0]).state != 'installed'})
    if missing:
        case.skipTest('chưa cài ' + ', '.join(missing))


def need_suite(case):
    need(case, *PORTAL_SUITE)


def find_view(case, key):
    need(case, key)
    return case.env['ir.ui.view'].search([('key', '=', key)], limit=1)
