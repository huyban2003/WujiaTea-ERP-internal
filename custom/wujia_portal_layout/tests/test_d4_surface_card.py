"""D4 — CMP-SC-001 SurfaceCard: hợp đồng render của component wj_surface_card.

Bám cột `Kết quả mong muốn` của issue UI-SURFACECARD-001 (STT 127) cho phần lượt
D4b phủ: 4 biến thể, 2 mức mật độ, bodyMode padded/flush, interactive wholeCard,
BỎ shadow mặc định, CÓ viền 1px, và KHÔNG khoá cứng chiều cao.
"""
import os
import re

from lxml import html

from odoo.tests import TransactionCase, tagged

TMPL = 'wujia_portal_layout.wj_surface_card'
CSS_DIR = os.path.join(os.path.dirname(__file__), '..', 'static', 'assets', 'css')


def _css(name):
    with open(os.path.join(CSS_DIR, name), encoding='utf-8') as fh:
        return fh.read()


def _strip_comments(css):
    return re.sub(r'/\*.*?\*/', '', css, flags=re.S)


def _rule(css, selector):
    """Thân của rule ở TẦNG GỐC (ngoài mọi @media). Gộp @media vào là bẫy đã trả
    giá ở D4a — wj-auth-card từng bị đọc ra số của bản mobile."""
    css = _strip_comments(css)
    depth, i, out = 0, 0, None
    while i < len(css):
        c = css[i]
        if c == '{':
            depth += 1
        elif c == '}':
            depth -= 1
        elif depth == 0 and css.startswith(selector, i):
            after = css[i + len(selector)]
            if after in ' ,{\n':
                j = css.index('{', i)
                if css[i:j].strip() == selector:
                    out = css[j + 1:css.index('}', j)]
                    break
        i += 1
    return out


@tagged('post_install', '-at_install', 'wujia_surface_card_d4')
class TestSurfaceCardComponent(TransactionCase):

    def _root(self, **values):
        out = self.env['ir.qweb']._render(TMPL, values)
        return html.fragment_fromstring(str(out).strip())

    # --- biến thể ---------------------------------------------------------

    def test_default_variant_is_section(self):
        self.assertIn('wj-surface-card--section', self._root().get('class'))

    def test_each_variant_gets_its_modifier(self):
        for v in ('record', 'summary', 'transactional'):
            with self.subTest(variant=v):
                self.assertIn('wj-surface-card--%s' % v,
                              self._root(sc_variant=v).get('class'))

    def test_unknown_variant_falls_back_to_section(self):
        cls = self._root(sc_variant='bogus').get('class')
        self.assertIn('wj-surface-card--section', cls)
        self.assertNotIn('bogus', cls)

    # --- mật độ: BA chốt compact-first ------------------------------------

    def test_density_defaults_to_compact(self):
        self.assertIn('wj-surface-card--compact', self._root().get('class'))

    def test_density_regular_replaces_compact(self):
        cls = self._root(sc_density='regular').get('class')
        self.assertIn('wj-surface-card--regular', cls)
        self.assertNotIn('wj-surface-card--compact', cls)

    # --- bodyMode ---------------------------------------------------------

    def test_body_defaults_to_padded(self):
        self.assertIn('wj-surface-card--padded', self._root().get('class'))

    def test_body_flush(self):
        self.assertIn('wj-surface-card--flush',
                      self._root(sc_body='flush').get('class'))

    # --- interactive: wholeCard ------------------------------------------

    def test_href_wraps_the_card_in_an_anchor(self):
        root = self._root(sc_href='/portal/notification')
        self.assertEqual(root.tag, 'a')
        self.assertEqual(root.get('href'), '/portal/notification')
        self.assertIn('wj-surface-card-link', root.get('class'))
        self.assertIn('wj-surface-card', root[0].get('class'))

    def test_no_href_means_no_anchor_wrapper(self):
        self.assertEqual(self._root().tag, 'div')

    def test_link_keeps_caller_class(self):
        # Lớp cũ phải sống sót, nếu không ba danh sách :is() hover ở
        # _interaction.css mất đối tượng và thẻ KPI hết phản hồi.
        root = self._root(sc_href='/x', sc_link_class='wujia-kpi-card-link')
        self.assertIn('wujia-kpi-card-link', root.get('class'))

    def test_card_keeps_caller_class(self):
        self.assertIn('wujia-content-card',
                      self._root(sc_class='wujia-content-card').get('class'))

    # --- slot thân --------------------------------------------------------

    def _via_call(self, sets='', body='<p id="inner">nội dung</p>'):
        # _render() xoá values['0'] (ir_qweb.py:712) — slot CHỈ đến được qua
        # t-call thật, nên test phải dựng một view gọi component.
        view = self.env['ir.ui.view'].create({
            'name': 'wj surface card probe',
            'type': 'qweb',
            'arch_db': '<t t-name="wj_sc_probe">'
                       '<t t-call="%s">%s%s</t></t>' % (TMPL, sets, body),
        })
        out = self.env['ir.qweb']._render(view.id)
        return html.fragment_fromstring(str(out).strip())

    def test_body_passes_through_untouched(self):
        root = self._via_call()
        self.assertEqual(len(root), 1)          # KHÔNG bọc thêm tầng nào
        self.assertEqual(root[0].get('id'), 'inner')
        self.assertIn('wj-surface-card', root.get('class'))

    def test_body_passes_through_under_anchor_too(self):
        root = self._via_call(
            sets='<t t-set="sc_href" t-value="\'/portal\'"/>')
        self.assertEqual(root.tag, 'a')
        self.assertEqual(root[0][0].get('id'), 'inner')

    # --- BA: KHÔNG khoá cứng chiều cao ------------------------------------

    def test_component_never_emits_inline_height(self):
        for kw in ({}, {'sc_href': '/x'}, {'sc_density': 'regular'}):
            with self.subTest(**kw):
                self.assertNotIn('height', str(self._root(**kw).get('style') or ''))

    def test_kpi_card_no_longer_locks_height(self):
        body = _rule(_css('_components.css'), '.wujia-kpi-card')
        self.assertIsNotNone(body)
        self.assertNotIn('min-height', body)

    def test_no_kpi_min_height_token_left(self):
        self.assertNotIn('--wujia-kpi-card-min-height', _css('_variables.css'))

    # --- BA: bỏ shadow, thêm viền ----------------------------------------

    def test_surface_card_has_no_default_shadow(self):
        self.assertNotIn('box-shadow', _rule(_css('_components.css'), '.wj-surface-card'))

    def test_surface_card_has_one_pixel_border(self):
        body = _rule(_css('_components.css'), '.wj-surface-card')
        self.assertTrue(re.search(r'border:\s*1px solid var\(--wujia-border-soft\)', body),
                        'viền PC phải là 1px --wujia-border-soft (#EEF2F5)')

    # --- gap: KHÔNG ở base, nếu không cộng chồng nhịp D3 -------------------

    def test_base_card_declares_no_gap(self):
        # Card xếp dọc đã có nhịp header→body 12px do margin của wj_card_header.
        # Thêm gap ở base là 12+12=24px — đo được, mà RULE 1/2 không thấy vì nó
        # đều tay trên mọi card.
        self.assertNotIn('gap', _rule(_css('_components.css'), '.wj-surface-card'))

    def test_summary_variant_owns_the_gap(self):
        body = _rule(_css('_components.css'), '.wj-surface-card--summary')
        self.assertIsNotNone(body)
        self.assertIn('gap: var(--wujia-surface-gap)', body)

    def test_hover_of_whole_card_drops_the_shadow_too(self):
        # wholeCard: bỏ shadow mặc định mà giữ shadow hover là vẫn còn shadow.
        css = _css('_components.css')
        i = css.index('.wujia-kpi-card-link:hover .wujia-kpi-card')
        self.assertNotIn('box-shadow', css[i:css.index('}', i)])

    def test_legacy_families_no_longer_declare_surface_shape(self):
        # Hai rule cùng đặc hiệu cùng khai padding thì thắng thua do thứ tự
        # nguồn — chủ sở hữu phải là DUY NHẤT.
        css = _css('_components.css')
        for sel in ('.wujia-kpi-card', '.wujia-content-card'):
            with self.subTest(sel=sel):
                body = _rule(css, sel)
                for prop in ('padding', 'border-radius', 'box-shadow'):
                    self.assertNotIn(prop, body,
                                     '%s không được khai %s nữa' % (sel, prop))


MOD_DIR = os.path.join(os.path.dirname(__file__), '..', '..')


def _mod_css(module, name):
    with open(os.path.join(MOD_DIR, module, 'static', 'src', 'css', name),
              encoding='utf-8') as fh:
        return fh.read()


PROP = r'(?:^|;)\s*%s\s*:'


def _declares(body, prop):
    """Có khai THUỘC TÍNH prop không. Dò chuỗi con là bẫy: `top: var(--wj-pc-
    content-padding)` chứa chữ "padding" mà không hề khai padding."""
    return re.search(PROP % re.escape(prop), body) is not None


def _rules_anywhere(css, selector):
    """Mọi thân rule của selector, KỂ CẢ trong @media. `_rule` cố ý bỏ @media;
    các modifier của exam nằm trọn trong @media nên phải có bản quét này."""
    css = _strip_comments(css)
    out = []
    for m in re.finditer(re.escape(selector) + r'\s*(?=[,{])', css):
        j = css.find('{', m.end())
        head = css[m.end():j]
        if head.strip() not in ('', ','):
            continue
        out.append(css[j + 1:css.index('}', j)])
    return out


@tagged('post_install', '-at_install', 'wujia_surface_card_d4')
class TestSurfaceCardD4c(TransactionCase):
    """D4c — họ shell PC: wj-pc-card + 8 modifier + wj-pc-acct-headcard."""

    def _root(self, **values):
        out = self.env['ir.qweb']._render(TMPL, values)
        return html.fragment_fromstring(str(out).strip())

    # --- chủ sở hữu DUY NHẤT của dáng khung -------------------------------

    def test_pc_card_no_longer_declares_surface_shape(self):
        body = _rule(_css('_pc_components.css'), '.wj-pc-card')
        self.assertIsNone(body, '.wj-pc-card không được khai dáng khung nữa')

    def test_acct_headcard_keeps_layout_but_drops_shape(self):
        body = _rule(_css('_pc_account.css'), '.wj-pc-acct-headcard')
        self.assertIsNotNone(body)
        for prop in ('background', 'border', 'border-radius', 'padding'):
            with self.subTest(prop=prop):
                self.assertFalse(_declares(body, prop))
        self.assertIn('display: flex', body, 'phần bố cục phải giữ nguyên')

    def test_modifiers_no_longer_declare_padding(self):
        # Chúng nằm ở CSS module khác, nạp SAU _pc_components.css ⇒ cùng đặc hiệu
        # (0,1,0) mà thắng theo thứ tự nguồn. Đây là chỗ "sửa xong vẫn y như cũ".
        for module, css_name, sel in (
                ('wujia_portal_debt', 'portal_debt.css', '.wj-debt-pc-card'),
                ('wujia_portal_exam', 'portal_exam.css', '.wj-exam-pc-card'),
                ('wujia_portal_exam', 'portal_exam.css', '.wj-exam-pc-fcard'),
                ('wujia_portal_exam', 'portal_exam.css', '.wj-exam-pc-sumcard'),
                ('wujia_portal_exam', 'portal_exam.css', '.wj-exam-pc-dcard'),
                ('wujia_portal_sale', 'portal_order.css', '.wj-pc-order-card'),
                ('wujia_portal_report', 'portal_report.css', '.wj-rep-pccard')):
            with self.subTest(sel=sel):
                for body in _rules_anywhere(_mod_css(module, css_name), sel):
                    self.assertFalse(_declares(body, 'padding'),
                                     '%s vẫn đè padding lên SurfaceCard' % sel)

    def test_paycard_keeps_its_non_shape_rule(self):
        # max-width KHÔNG phải dáng khung ⇒ modifier được giữ.
        bodies = _rules_anywhere(_mod_css('wujia_portal_debt', 'portal_debt.css'),
                                 '.wj-debt-pc-paycard')
        self.assertTrue(any('max-width' in b for b in bodies))

    # --- token ------------------------------------------------------------

    def test_pc_card_radius_token_converged_to_sixteen(self):
        # DRIFT: --wj-pc-card-radius 18 vs --wujia-card-radius 16, cùng vai trò.
        css = _strip_comments(_css('_variables.css'))
        self.assertTrue(re.search(r'--wj-pc-card-radius:\s*16px', css))

    def test_tonal_tokens_exist(self):
        css = _strip_comments(_css('_variables.css'))
        self.assertTrue(re.search(r'--wujia-surface-tonal:\s*#F8FAFC', css, re.I))
        self.assertTrue(re.search(r'--wujia-surface-tonal-radius:\s*12px', css))

    # --- biến thể tonal ---------------------------------------------------

    def test_tone_tonal_adds_the_modifier(self):
        self.assertIn('wj-surface-card--tonal',
                      self._root(sc_tone='tonal').get('class'))

    def test_tone_defaults_to_none(self):
        self.assertNotIn('wj-surface-card--tonal', self._root().get('class'))

    def test_tonal_variant_has_no_border_and_no_shadow(self):
        body = _rule(_css('_components.css'), '.wj-surface-card--tonal')
        self.assertIsNotNone(body)
        self.assertIn('var(--wujia-surface-tonal)', body)
        self.assertIn('var(--wujia-surface-tonal-radius)', body)
        self.assertTrue(re.search(r'border:\s*0', body))
        self.assertTrue(re.search(r'box-shadow:\s*none', body))

    def test_nested_exam_panels_no_longer_paint_white(self):
        # BA cấm thẻ trắng lồng thẻ trắng — 2 vi phạm ở /portal/exam/register.
        css = _mod_css('wujia_portal_exam', 'portal_exam.css')
        for sel in ('.wj-exam-pc-cal', '.wj-exam-pc-slots'):
            with self.subTest(sel=sel):
                for body in _rules_anywhere(css, sel):
                    self.assertFalse(_declares(body, 'background'))
                    self.assertFalse(_declares(body, 'border'))

    # --- call site không phải <div> ---------------------------------------

    def test_non_div_call_sites_carry_the_owner_class(self):
        # <form> POST, <aside>, <section> không đi qua t-call được (component
        # luôn sinh <div>) ⇒ mang thẳng class chủ sở hữu, không mất landmark.
        views = self.env['ir.ui.view'].search([
            ('key', 'in', ['wujia_portal_support.portal_support_form',
                           'wujia_portal_exam.portal_exam_register',
                           'wujia_portal_report.portal_report_orders'])])
        self.assertEqual(len(views), 3)
        for v in views:
            with self.subTest(key=v.key):
                self.assertIn('wj-surface-card', v.arch_db)
