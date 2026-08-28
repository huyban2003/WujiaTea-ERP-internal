"""D3 — CMP-CH-001 CardHeader: hợp đồng render của component wj_card_header.

Bám từng gạch đầu dòng cột `Kết quả mong muốn` của issue UI-CARDHEADER-001 (STT 125):
title là heading THẬT theo level từng màn, TỐI ĐA một trailing, count 0 vẫn hiện,
trailing ra markup thô để `wj_ajax_list` swap được, icon trang trí có aria-hidden,
compact là mặc định và migrate KHÔNG được cộng chồng margin header với body.
"""
from lxml import html
from markupsafe import Markup

from odoo.tests import TransactionCase, tagged

TMPL = 'wujia_portal_layout.wj_card_header'


@tagged('post_install', '-at_install', 'wujia_card_header_d3')
class TestCardHeaderComponent(TransactionCase):

    def _root(self, **values):
        values.setdefault('ch_title', 'Tiêu đề')
        out = self.env['ir.qweb']._render(TMPL, values)
        return html.fragment_fromstring(str(out).strip())

    def _title(self, root):
        heads = root.xpath('.//h1|.//h2|.//h3|.//h4|.//h5|.//h6')
        self.assertEqual(len(heads), 1, 'phải có ĐÚNG một heading trong CardHeader')
        return heads[0]

    # --- title là heading thật, đúng level từng màn -----------------------

    def test_default_level_is_h3(self):
        self.assertEqual(self._title(self._root()).tag, 'h3')

    def test_level_follows_caller(self):
        for lvl, tag in ((2, 'h2'), (3, 'h3'), (4, 'h4')):
            with self.subTest(level=lvl):
                self.assertEqual(self._title(self._root(ch_level=lvl)).tag, tag)

    def test_unknown_level_falls_back_to_h3(self):
        self.assertEqual(self._title(self._root(ch_level=6)).tag, 'h3')

    def test_title_is_never_p_or_span(self):
        # Đúng ca BA than: `<p class="wujia-mdash-title">` giả heading.
        root = self._root(ch_subtitle='phụ', ch_meta=Markup('<span>3 mục</span>'))
        title = self._title(root)
        self.assertEqual(title.get('class'), 'wj-card-header__title')
        self.assertEqual(title.text, 'Tiêu đề')

    # --- TỐI ĐA một trailing ---------------------------------------------

    def test_action_wins_over_control_and_meta(self):
        root = self._root(ch_action_url='/portal/support',
                          ch_control=Markup('<select id="c"/>'),
                          ch_meta=Markup('<span id="m">3 mục</span>'))
        self.assertTrue(root.xpath('.//a[@class="wj-card-header__action"]'))
        self.assertFalse(root.xpath('.//*[@id="c"]'))
        self.assertFalse(root.xpath('.//*[@id="m"]'))
        self.assertIn('wj-card-header--action', root.get('class'))

    def test_control_wins_over_meta(self):
        root = self._root(ch_control=Markup('<select id="c"/>'),
                          ch_meta=Markup('<span id="m">3 mục</span>'))
        self.assertTrue(root.xpath('.//*[@id="c"]'))
        self.assertFalse(root.xpath('.//*[@id="m"]'))
        self.assertIn('wj-card-header--control', root.get('class'))

    def test_no_trailing_by_default(self):
        root = self._root()
        self.assertEqual(len(root), 1)          # chỉ có __lead
        self.assertIn('wj-card-header--none', root.get('class'))

    def test_action_label_default_and_override(self):
        self.assertEqual(
            self._root(ch_action_url='/x').xpath('.//a/span')[0].text, 'Xem tất cả')
        self.assertEqual(
            self._root(ch_action_url='/x', ch_action_label='Xem thêm')
            .xpath('.//a/span')[0].text, 'Xem thêm')

    # --- trailing là markup THÔ, không bị bọc thêm element -----------------

    def test_trailing_is_direct_child_not_wrapped(self):
        # `wj_ajax_list` swap theo id: bọc thêm 1 lớp là hỏng slot (bài học B3a).
        root = self._root(ch_meta=Markup('<span id="m" class="wj-card-header__meta">'
                                         '0 ticket</span>'))
        self.assertEqual([c.get('id') for c in root][1:], ['m'])

    def test_trailing_keeps_multiple_top_level_nodes(self):
        root = self._root(ch_meta=Markup('<span id="a"/><span id="b"/>'))
        self.assertEqual([c.get('id') for c in root][1:], ['a', 'b'])

    # --- variant: compact là MẶC ĐỊNH (BA chốt compact-first) --------------

    def test_compact_is_default(self):
        self.assertIn('wj-card-header--compact', self._root().get('class'))

    def test_regular_only_when_asked(self):
        cls = self._root(ch_variant='regular').get('class')
        self.assertIn('wj-card-header--regular', cls)
        self.assertNotIn('wj-card-header--compact', cls)

    def test_unknown_variant_falls_back_to_compact(self):
        self.assertIn('wj-card-header--compact',
                      self._root(ch_variant='cozy').get('class'))

    # --- icon / subtitle ---------------------------------------------------

    def test_decorative_icon_is_aria_hidden(self):
        icon = self._root(ch_icon='life-buoy').xpath('.//*[@class="wj-card-header__icon"]')
        self.assertEqual(len(icon), 1)
        self.assertEqual(icon[0].get('aria-hidden'), 'true')
        self.assertIsNone(icon[0].get('role'))

    def test_meaningful_icon_gets_accessible_name(self):
        icon = self._root(ch_icon='alert-triangle', ch_icon_label='Cảnh báo') \
            .xpath('.//*[@class="wj-card-header__icon"]')[0]
        self.assertEqual(icon.get('role'), 'img')
        self.assertEqual(icon.get('aria-label'), 'Cảnh báo')
        self.assertIsNone(icon.get('aria-hidden'))

    def test_no_icon_node_when_not_asked(self):
        self.assertFalse(self._root().xpath('.//*[@class="wj-card-header__icon"]'))

    def test_subtitle_sits_under_title_inside_lead(self):
        root = self._root(ch_subtitle='Thông tin chính của cửa hàng')
        sub = root.xpath('.//p[@class="wj-card-header__subtitle"]')
        self.assertEqual(len(sub), 1)
        self.assertEqual(sub[0].text, 'Thông tin chính của cửa hàng')
        # subtitle phải là em của title trong cùng __text, không nằm ở trailing
        self.assertEqual(sub[0].getparent().get('class'), 'wj-card-header__text')

    def test_no_subtitle_node_when_not_asked(self):
        self.assertFalse(self._root().xpath('.//p[@class="wj-card-header__subtitle"]'))

    # --- divider mặc định TẮT ---------------------------------------------

    def test_divider_off_by_default(self):
        self.assertNotIn('wj-card-header--divider', self._root().get('class'))

    def test_divider_opt_in(self):
        self.assertIn('wj-card-header--divider',
                      self._root(ch_divider=True).get('class'))

    # --- visibility / id / class truyền qua --------------------------------

    def test_platform_bakes_visibility(self):
        self.assertIn('d-flex d-lg-none', self._root(ch_platform='m').get('class'))
        self.assertIn('d-none d-lg-flex', self._root(ch_platform='pc').get('class'))
        self.assertIn('d-flex', self._root().get('class'))

    def test_id_and_extra_class(self):
        root = self._root(ch_id='wj-sup-head', ch_class='wj-card-header--flush')
        self.assertEqual(root.get('id'), 'wj-sup-head')
        self.assertIn('wj-card-header--flush', root.get('class'))


@tagged('post_install', '-at_install', 'wujia_card_header_d3')
class TestCardHeaderCallSites(TransactionCase):
    """Route đã migrate (D3a + D3b) phải dùng component và bỏ được các bệnh BA nêu."""

    CALL_SITES = {
        # D3a — 4 họ markup mẫu
        'wujia_portal_support.portal_support_list': 1,
        'wujia_portal_delivery.portal_delivery_detail': 3,
        'wujia_portal_base.portal_franchise_information': 2,
        'wujia_portal_return.portal_return_form': 4,
        # D3b — nhóm màn kế tiếp
        'wujia_portal_base.portal_home_page': 5,
        'wujia_portal_base.portal_franchise_profile_full': 4,
        'wujia_portal_knowledge.portal_knowledge_list': 2,
        'wujia_portal_knowledge.portal_knowledge_detail': 3,
        'wujia_portal_notification.portal_notification_results_part': 1,
        'wujia_portal_notification.portal_notification_detail': 4,
        'wujia_portal_report.portal_report_orders': 3,
        'wujia_portal_sale.pc_cart_panel': 1,
        'wujia_portal_sale.portal_order_product_detail': 1,
        'wujia_portal_info_request.portal_info_request_list': 1,
        'wujia_portal_return.portal_return_list': 1,
    }

    # Count phải hiện cả khi = 0 ⇒ khối trailing KHÔNG được bọc `t-if` theo recordset.
    ZERO_COUNT_VIEWS = {
        'wujia_portal_support.portal_support_list': 'tickets',
        'wujia_portal_knowledge.portal_knowledge_list': 'articles',
        'wujia_portal_report.portal_report_orders': 'top_products',
        'wujia_portal_info_request.portal_info_request_list': 'requests',
        'wujia_portal_return.portal_return_list': 'returns',
    }

    # Họ Bootstrap `.card-header` giữ wrapper (đã có padding + border) ⇒ header phải
    # `--flush`, nếu không là cộng chồng margin (spec cấm).
    FLUSH_VIEWS = {
        'wujia_portal_base.portal_franchise_profile_full': 4,
        'wujia_portal_knowledge.portal_knowledge_list': 1,
        'wujia_portal_knowledge.portal_knowledge_detail': 1,
    }

    # Class heading cũ đã migrate hết trong CHÍNH view đó ⇒ không được tái xuất hiện.
    RETIRED_IN_VIEW = {
        'wujia_portal_base.portal_home_page': ('wujia-content-card-header-title',
                                               'wujia-mhome-window-title'),
        'wujia_portal_base.portal_franchise_profile_full': ('card-title',),
        'wujia_portal_knowledge.portal_knowledge_detail': ('wujia-mknow-h',),
        'wujia_portal_notification.portal_notification_detail': ('wujia-mnoti-detail-sectitle',),
        'wujia_portal_report.portal_report_orders': ('wj-pc-card__title',),
        'wujia_portal_sale.pc_cart_panel': ('wj-pc-cart-title',),
        'wujia_portal_info_request.portal_info_request_list': ('wujia-content-card-header-title',),
        'wujia_portal_return.portal_return_list': ('wujia-content-card-header-title',),
    }

    # View KHÔNG tách PC/mobile (không có `d-none d-lg-*`) ⇒ một markup phục vụ cả hai
    # nền tảng. Bake `ch_platform` ở đây là nuốt mất tiêu đề ở nền tảng còn lại —
    # đo được ở D3b: /portal/info-request mất hẳn header khi ≤991px.
    SHARED_MARKUP_VIEWS = ('wujia_portal_info_request.portal_info_request_list',)

    def _arch(self, xmlid):
        return self.env.ref(xmlid).arch_db

    def test_shared_markup_views_do_not_bake_platform(self):
        for xmlid in self.SHARED_MARKUP_VIEWS:
            with self.subTest(view=xmlid):
                arch = self._arch(xmlid)
                self.assertNotIn('d-lg-none', arch, 'view này phải là markup dùng chung')
                # bám directive, KHÔNG bám chữ: comment giải thích cũng chứa "ch_platform"
                self.assertNotIn('t-set="ch_platform"', arch)

    def test_call_sites_use_component(self):
        for xmlid, count in self.CALL_SITES.items():
            with self.subTest(view=xmlid):
                self.assertEqual(
                    self._arch(xmlid).count('wujia_portal_layout.wj_card_header'),
                    count)

    def test_count_not_hidden_when_zero(self):
        # Spec: "Count 0 vẫn hiển thị" ⇒ khối count không được bọc `t-if` theo recordset.
        for xmlid, recordset in self.ZERO_COUNT_VIEWS.items():
            with self.subTest(view=xmlid):
                root = html.fromstring('<div>%s</div>' % self._arch(xmlid))
                counts = root.xpath('.//t[@t-set="ch_meta"]')
                self.assertTrue(counts, 'view phải có slot count')
                for node in counts:
                    for el in [node] + node.xpath('.//*'):
                        self.assertNotIn(recordset, el.get('t-if') or '')

    def test_flush_on_legacy_card_header_wrapper(self):
        for xmlid, count in self.FLUSH_VIEWS.items():
            with self.subTest(view=xmlid):
                self.assertEqual(
                    self._arch(xmlid).count('wj-card-header--flush'), count)

    def test_retired_heading_classes_gone_from_migrated_views(self):
        for xmlid, classes in self.RETIRED_IN_VIEW.items():
            arch = self._arch(xmlid)
            for cls in classes:
                with self.subTest(view=xmlid, cls=cls):
                    self.assertNotIn('class="%s' % cls, arch)

    def test_migrated_headers_drop_stacking_margin(self):
        # Spec cấm cộng chồng margin header với body ⇒ `mb-3`/`mb-1` phải biến mất
        # khỏi CHÍNH dòng tiêu đề (component tự quyết nhịp 8/12).
        root = html.fromstring(
            '<div>%s</div>' % self._arch('wujia_portal_return.portal_return_form'))
        self.assertEqual(root.xpath('.//p[contains(@class,"wujia-mdash-title")]'), [])

    def test_no_pseudo_heading_left_in_migrated_views(self):
        for xmlid in self.CALL_SITES:
            with self.subTest(view=xmlid):
                root = html.fromstring('<div>%s</div>' % self._arch(xmlid))
                self.assertEqual(
                    root.xpath('.//p[contains(@class,"wujia-mdash-title")]'
                               '|.//p[contains(@class,"card-title")]'), [])
