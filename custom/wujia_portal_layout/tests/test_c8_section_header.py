"""C8 — CMP-SH-001 SectionHeader: hợp đồng render của component wj_section_header.

Bám từng gạch đầu dòng cột `Kết quả mong muốn` của issue UI-SECTIONHEADER-001 (STT 83):
title là heading THẬT theo level từng màn, TỐI ĐA một right slot, count hiện cả khi = 0
và dùng từ đầy đủ, meta ra markup thô để `wj_ajax_list` swap được.
"""
from lxml import html
from markupsafe import Markup

from odoo.tests import TransactionCase, tagged

TMPL = 'wujia_portal_layout.wj_section_header'


@tagged('post_install', '-at_install', 'wujia_section_header_c8')
class TestSectionHeaderComponent(TransactionCase):

    def _root(self, **values):
        values.setdefault('sh_title', 'Tiêu đề')
        out = self.env['ir.qweb']._render(TMPL, values)
        return html.fragment_fromstring(str(out).strip())

    # --- title là heading thật, đúng level từng màn -----------------------

    def test_default_level_is_h3(self):
        self.assertEqual(self._root()[0].tag, 'h3')

    def test_level_follows_caller(self):
        for lvl, tag in ((2, 'h2'), (3, 'h3'), (4, 'h4')):
            with self.subTest(level=lvl):
                self.assertEqual(self._root(sh_level=lvl)[0].tag, tag)

    def test_title_never_span(self):
        # Spec cấm bọc title bằng <span>; và chỉ có ĐÚNG MỘT heading trong header.
        root = self._root(sh_level=2, sh_meta=Markup('<span>3 mục</span>'))
        heads = root.xpath('.//h1|.//h2|.//h3|.//h4|.//h5|.//h6')
        self.assertEqual(len(heads), 1)
        self.assertEqual(heads[0].get('class'), 'wj-section-header__title')
        self.assertEqual(heads[0].text, 'Tiêu đề')

    def test_unknown_level_falls_back_to_h3(self):
        self.assertEqual(self._root(sh_level=6)[0].tag, 'h3')

    # --- TỐI ĐA một right slot -------------------------------------------

    def test_action_wins_over_control_and_meta(self):
        root = self._root(sh_action_url='/portal/delivery',
                          sh_control=Markup('<select id="c"/>'),
                          sh_meta=Markup('<span id="m">3 mục</span>'))
        self.assertTrue(root.xpath('.//a[@class="wj-section-header__action"]'))
        self.assertFalse(root.xpath('.//*[@id="c"]'))
        self.assertFalse(root.xpath('.//*[@id="m"]'))
        self.assertIn('wj-section-header--action', root.get('class'))

    def test_control_wins_over_meta(self):
        root = self._root(sh_control=Markup('<select id="c"/>'),
                          sh_meta=Markup('<span id="m">3 mục</span>'))
        self.assertTrue(root.xpath('.//*[@id="c"]'))
        self.assertFalse(root.xpath('.//*[@id="m"]'))
        self.assertIn('wj-section-header--control', root.get('class'))

    def test_default_variant_has_no_right_slot(self):
        root = self._root()
        self.assertEqual(len(root), 1)
        self.assertIn('wj-section-header--none', root.get('class'))

    def test_action_label_default_and_override(self):
        self.assertEqual(
            self._root(sh_action_url='/x').xpath('.//a/span')[0].text, 'Xem tất cả')
        self.assertEqual(
            self._root(sh_action_url='/x', sh_action_label='Xem thêm')
            .xpath('.//a/span')[0].text, 'Xem thêm')

    # --- meta là markup THÔ, không bị bọc thêm element ---------------------

    def test_meta_is_direct_child_not_wrapped(self):
        # `wj_ajax_list` swap theo id: meta bị bọc thêm 1 lớp là hỏng slot (bài học B3a).
        root = self._root(sh_meta=Markup('<span id="m" class="wj-section-header__meta">'
                                         '0 sản phẩm</span>'))
        self.assertEqual([c.get('id') for c in root][1:], ['m'])

    def test_meta_keeps_multiple_top_level_nodes(self):
        root = self._root(sh_meta=Markup('<span id="a"/><span id="b"/>'))
        self.assertEqual([c.get('id') for c in root][1:], ['a', 'b'])

    # --- visibility / id / class truyền qua --------------------------------

    def test_platform_bakes_visibility(self):
        self.assertIn('d-flex d-lg-none', self._root(sh_platform='m').get('class'))
        self.assertIn('d-none d-lg-flex', self._root(sh_platform='pc').get('class'))
        self.assertIn('d-flex', self._root().get('class'))

    def test_id_and_extra_class(self):
        root = self._root(sh_id='wj-hist-head', sh_class='wj-section-header--inline')
        self.assertEqual(root.get('id'), 'wj-hist-head')
        self.assertIn('wj-section-header--inline', root.get('class'))


@tagged('post_install', '-at_install', 'wujia_section_header_c8')
class TestSectionHeaderCallSites(TransactionCase):
    """Các call site C8a phải dùng component + đúng rule đếm của spec."""

    def _arch(self, xmlid):
        return self.env.ref(xmlid).arch_db

    # Header nằm trong sub-template render thật (fragment của wj_ajax_list),
    # không phải view gốc `portal_*` — bám đúng id có t-call.
    CALL_SITES = {
        'wujia_portal_base.portal_home_page': 8,
        'wujia_portal_sale.portal_order_catalog_results_part': 2,
        'wujia_portal_sale.mcart_panel': 1,
        'wujia_portal_purchase_history.portal_history_results_part': 1,
        'wujia_portal_delivery.portal_delivery_results_part': 1,
    }

    def test_call_sites_use_component(self):
        for xmlid, count in self.CALL_SITES.items():
            with self.subTest(view=xmlid):
                self.assertEqual(
                    self._arch(xmlid).count('wujia_portal_layout.wj_section_header'),
                    count)

    def _sh_metas(self, xmlid):
        """Nội dung mọi slot meta của SectionHeader trong view (bỏ qua meta của
        PageHeader `wj-page-header__meta` — đó là CMP-PG-001, ngoài scope C8)."""
        root = html.fromstring(f'<div>{self._arch(xmlid)}</div>')
        return [m.text_content()
                for m in root.xpath('.//*[@class="wj-section-header__meta"]')]

    def test_count_uses_full_word_not_abbreviation(self):
        # Spec: "5 sản phẩm", KHÔNG "5 SP".
        metas = self._sh_metas('wujia_portal_sale.portal_order_catalog_results_part')
        self.assertEqual(len(metas), 2)
        for m in metas:
            self.assertIn('sản phẩm', m)
            self.assertNotRegex(m, r'\bSP\b')

    def test_count_not_hidden_when_zero(self):
        # Meta đếm không được bọc trong t-if="products" — 0 vẫn phải hiện.
        arch = self._arch('wujia_portal_sale.portal_order_catalog_results_part')
        root = html.fromstring(f'<div>{arch}</div>')
        for m in root.xpath('.//*[@class="wj-section-header__meta"]'):
            for node in [m] + m.xpath('.//*'):
                self.assertNotIn('products', node.get('t-if') or '')
