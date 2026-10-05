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


def load_vi(env):
    """J-V2 — bật vi_VN + nạp .po của khung và `portal_base`; trả env `lang=vi_VN`.

    Câu gốc portal_base là tiếng Anh, tiếng Việt nằm ở `i18n/vi_VN.po` (Phần V §6 #5: test assert
    nhãn tiếng Việt chạy ở vi_VN, không xoá assert). `_activate_lang` không nạp .po ⇒ `_update_translations`.
    """
    env['res.lang']._activate_lang('vi_VN')
    env['ir.module.module'].search([
        ('name', 'in', ('wujia_portal_layout', 'wujia_portal_base')),
    ])._update_translations(['vi_VN'])
    return env(context=dict(env.context, lang='vi_VN'))
