"""D3 — CMP-CH-001 CardHeader: hợp đồng render của component wj_card_header.

Bám từng gạch đầu dòng cột `Kết quả mong muốn` của issue UI-CARDHEADER-001 (STT 125):
title là heading THẬT theo level từng màn, TỐI ĐA một trailing, count 0 vẫn hiện,
trailing ra markup thô để `wj_ajax_list` swap được, icon trang trí có aria-hidden,
compact là mặc định và migrate KHÔNG được cộng chồng margin header với body.
"""
import os
import re

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
        'wujia_portal_return.portal_return_form': 4,
        # D3c — nốt phần còn lại của chính 4 file D3a
        'wujia_portal_delivery.portal_delivery_detail': 4,
        'wujia_portal_base.portal_franchise_information': 6,
        'wujia_portal_support.portal_support_form': 1,
        'wujia_portal_support.portal_support_detail': 5,
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
        # D3d — màn Đăng ký thi (PC + wizard mobile)
        'wujia_portal_exam.portal_exam_schedule': 2,
        'wujia_portal_exam.portal_exam_register': 9,
        'wujia_portal_exam.portal_exam_registration_detail': 3,
        # D3e — chi tiết bù hàng + lịch sử đặt hàng
        'wujia_portal_return.portal_return_detail': 15,
        'wujia_portal_purchase_history.portal_history_results_part': 1,
        'wujia_portal_purchase_history.portal_history_detail': 8,
    }

    # Count phải hiện cả khi = 0 ⇒ khối trailing KHÔNG được bọc `t-if` theo recordset.
    ZERO_COUNT_VIEWS = {
        'wujia_portal_support.portal_support_list': 'tickets',
        'wujia_portal_knowledge.portal_knowledge_list': 'articles',
        'wujia_portal_report.portal_report_orders': 'top_products',
        'wujia_portal_info_request.portal_info_request_list': 'requests',
        'wujia_portal_return.portal_return_list': 'returns',
        'wujia_portal_support.portal_support_detail': 'comments',
        'wujia_portal_purchase_history.portal_history_results_part': 'rows',
    }

    # Họ Bootstrap `.card-header` giữ wrapper (đã có padding + border) ⇒ header phải
    # `--flush`, nếu không là cộng chồng margin (spec cấm).
    FLUSH_VIEWS = {
        'wujia_portal_base.portal_franchise_profile_full': 4,
        'wujia_portal_knowledge.portal_knowledge_list': 1,
        'wujia_portal_knowledge.portal_knowledge_detail': 1,
        # D3c: 4 card Bootstrap + card "Lịch sử trao đổi" (card khai padding:0)
        'wujia_portal_support.portal_support_detail': 5,
        # khối `wj-pc-acct-staff` — dòng `__line` dưới đã tự khai margin-top 8px
        'wujia_portal_base.portal_franchise_information': 1,
        # summary head chuyến giao — `.wj-pc-order-head` đã có padding riêng
        'wujia_portal_delivery.portal_delivery_detail': 1,
        # D3e: 5 card Bootstrap của chi tiết bù hàng + summary head lịch sử đặt hàng
        'wujia_portal_return.portal_return_detail': 5,
        'wujia_portal_purchase_history.portal_history_detail': 1,
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
        # D3c
        'wujia_portal_support.portal_support_form': ('wujia-mdash-title',),
        'wujia_portal_support.portal_support_detail': ('wujia-mdash-title',),
        'wujia_portal_base.portal_franchise_information': ('wujia-maccount-cardtitle',
                                                           'wujia-maccount-store-name'),
        'wujia_portal_delivery.portal_delivery_detail': ('wj-pc-order-head__code',
                                                         'wj-pc-dlv-head-meta'),
        # D3d
        'wujia_portal_exam.portal_exam_schedule': ('wujia-mexam-card-title',),
        'wujia_portal_exam.portal_exam_register': ('wujia-mexam-course-title',
                                                   'wujia-mexam-selcard-title',
                                                   'wujia-mexam-cftitle',
                                                   'wj-exam-pc-slots__title'),
        'wujia_portal_exam.portal_exam_registration_detail': ('wujia-mexam-rsum-title',),
        # D3e
        'wujia_portal_return.portal_return_detail': ('wujia-mhist-card-head',),
        'wujia_portal_purchase_history.portal_history_results_part': ('wj-pc-card__title',),
        'wujia_portal_purchase_history.portal_history_detail': ('wujia-mhist-card-head',
                                                                'wj-pc-order-head__code',
                                                                'wj-pc-card__title'),
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

    def test_title_colour_beats_theme_card_body_rule(self):
        # Theme Vuexy có `:where(.card…) .card-body:not(…) h4 { color: inherit }` = (0,4,1);
        # bỏ `!important` là title trong `.card > .card-body` rơi về màu body — đo được ở
        # D3b trên /portal/order/product/<id> (UAT #212529, local đen).
        path = os.path.join(os.path.dirname(__file__), '..', 'static', 'assets',
                            'css', '_components.css')
        with open(path, encoding='utf-8') as fh:
            css = fh.read()
        # cắt ở `\n}` chứ không phải `}`: trong block có comment chứa `{ … !important }`
        block = css.split('.wj-card-header__title {', 1)[1].split('\n}', 1)[0]
        self.assertIn('color: var(--wujia-text-primary) !important', block)

    def test_bootstrap_card_header_wrapper_class_is_kept(self):
        # Component KHÔNG tự khai padding ⇒ 4 card Bootstrap của /portal/support/<id> phải
        # giữ class `card-header` (nguồn padding + border-bottom), nếu không header dính
        # sát mép card. Cùng lý do phải kèm biến thể flush.
        arch = self._arch('wujia_portal_support.portal_support_detail')
        self.assertEqual(arch.count("'card-header wj-card-header--flush'"), 4)

    def test_store_name_became_subtitle_not_a_second_heading(self):
        # Chủ dự án chốt 02/09: mobile xếp giống bản PC cùng card (tiêu đề → dòng phụ →
        # badge). Tên cửa hàng phải đi vào slot subtitle, KHÔNG còn là heading rời, và
        # hàng badge phải nằm SAU header.
        root = html.fromstring(
            '<div>%s</div>' % self._arch('wujia_portal_base.portal_franchise_information'))
        subs = root.xpath('.//t[@t-set="ch_subtitle"][@t-value="franchise.name or \'—\'"]')
        self.assertEqual(len(subs), 1)
        card = root.xpath('.//div[contains(@class,"wujia-mdash-card")]'
                          '[t[@t-call="wujia_portal_layout.wj_card_header"]]'
                          '[div[@class="wujia-maccount-badgerow"]]')
        self.assertEqual(len(card), 1, 'card "Cửa hàng nhượng quyền" phải còn nguyên')
        kids = [c.get('t-call') or c.get('class') for c in card[0]]
        self.assertLess(kids.index('wujia_portal_layout.wj_card_header'),
                        kids.index('wujia-maccount-badgerow'))

    def test_no_pseudo_heading_left_in_migrated_views(self):
        for xmlid in self.CALL_SITES:
            with self.subTest(view=xmlid):
                root = html.fromstring('<div>%s</div>' % self._arch(xmlid))
                self.assertEqual(
                    root.xpath('.//p[contains(@class,"wujia-mdash-title")]'
                               '|.//p[contains(@class,"card-title")]'), [])


@tagged('post_install', '-at_install', 'wujia_card_header_d3')
class TestCardHeaderD3eLayout(TransactionCase):
    """D3e — hai bẫy đã trả giá khi migrate 2 file này, khoá lại bằng test."""

    def _arch(self, xmlid):
        return self.env.ref(xmlid).arch_db

    def test_order_head_meta_stays_card_content(self):
        # Dòng meta dài hơn mã đơn; đưa nó vào `ch_subtitle` thì lead nở theo nó và
        # badge (trailing) trôi khỏi mã đơn — chỉ ẢNH CHỤP bắt được, số đo vẫn Pass.
        root = html.fromstring(
            '<div>%s</div>'
            % self._arch('wujia_portal_purchase_history.portal_history_detail'))
        head = root.xpath('.//div[@class="wj-pc-order-head"]')
        self.assertEqual(len(head), 1)
        self.assertTrue(head[0].xpath('.//p[@class="wj-pc-order-head__meta"]'))
        self.assertEqual(head[0].xpath('.//t[@t-set="ch_subtitle"]'), [])

    def test_order_head_lead_shrinks_in_shared_css(self):
        # Rule gom về gốc `.wj-pc-order-head` (2 consumer: delivery D3c + history D3e).
        path = os.path.join(os.path.dirname(__file__), '..', 'static', 'assets',
                            'css', '_pc_components.css')
        with open(path, encoding='utf-8') as fh:
            css = fh.read()
        self.assertRegex(
            css,
            r'\.wj-pc-order-head \.wj-card-header__lead\s*\{[^}]*flex:\s*0 1 auto')

    def test_return_sublabels_keep_their_own_shape(self):
        # 4 nhãn phụ trong thân card: chuẩn hoá cấu trúc nhưng KHÔNG được to bằng
        # tiêu đề card cha, nếu không một card có ba dòng chữ cùng cỡ.
        arch = self._arch('wujia_portal_return.portal_return_detail')
        # Từ D3 REVIEW, ch_class mở đầu bằng modifier chung rồi mới tới lớp module.
        self.assertEqual(arch.count("wj-card-header--sublabel wj-return-sublabel"), 4)
        path = os.path.join(os.path.dirname(__file__), '..', '..', 'wujia_portal_return',
                            'static', 'src', 'css', 'portal_return.css')
        with open(path, encoding='utf-8') as fh:
            css = fh.read()
        # Cỡ chữ đã về modifier dùng chung `wj-card-header--sublabel` (D3 REVIEW
        # 2026-09-04) — ở lại file module đúng phần MÀU riêng. Quan hệ được giữ
        # vẫn y nguyên: nhãn phụ .875rem < tiêu đề card 18px.
        self.assertRegex(
            css,
            r'\.card-body > \.wj-card-header\.wj-return-sublabel'
            r'\s+\.wj-card-header__title\s*\{[^}]*color:')
        self.assertEqual(arch.count('wj-card-header--sublabel'), 4)


class TestCardHeaderExamJsContract(TransactionCase):
    """D3d — `portal_exam_wizard.js` đọc tiêu đề khoá thi để chép sang thẻ "đã chọn".

    Migrate đổi tên class tiêu đề mà quên sửa JS thì KHÔNG có lỗi, không đỏ build:
    tên khoá thi chỉ âm thầm biến mất khỏi bước 2 và 3 (đã chứng minh bằng mutation).
    """

    def _js(self):
        path = os.path.join(os.path.dirname(__file__), '..', '..', 'wujia_portal_exam',
                            'static', 'src', 'js', 'portal_exam_wizard.js')
        with open(path, encoding='utf-8') as fh:
            return fh.read()

    def test_wizard_reads_component_title_not_retired_class(self):
        js = self._js()
        self.assertIn("card.querySelector('.wj-card-header__title')", js)
        for retired in ("'.wujia-mexam-course-title'", "'.wujia-mexam-selcard-title'"):
            self.assertNotIn(retired, js)

    def test_wizard_still_scopes_selected_card_title_to_that_card(self):
        # Bám `.wj-card-header__title` trần là quét TRÚNG mọi header khác của wizard
        # (bước 1 + bước 4) rồi ghi đè tên chúng.
        self.assertIn(".wujia-mexam-selcard .wj-card-header__title", self._js())

    def test_person_head_left_untouched_pending_ba(self):
        # 2 vùng trailing (badge "Bắt buộc" + nút xoá) > tối đa MỘT của spec ⇒ defer;
        # và JS clone chính khối này làm template, đọc `.wujia-mexam-person-name`.
        arch = self.env.ref('wujia_portal_exam.portal_exam_register').arch_db
        self.assertIn('wujia-mexam-person-name', arch)
        self.assertIn("querySelector('.wujia-mexam-person-name')", self._js())


@tagged('post_install', '-at_install', 'wujia_card_header_d3')
class TestCardHeaderD3f(TransactionCase):
    """D3f — công nợ + khảo sát. Chín call site này đều PHẢI kèm một rule scope trả
    dáng: bỏ rule đi thì component áp 18px và card 52px / 142px của Figma vỡ ngay,
    mà build vẫn xanh. Guard bám CẢ KHAI BÁO (không phải chuỗi con) vì đổi tên
    selector là kiểu chết im lặng đã bắt được ở D3e §10.
    """

    CALL_SITES = {
        'wujia_portal_debt.portal_debt_overview': 2,          # __head S43 + "Hóa đơn trong tuần"
        'wujia_portal_debt.portal_debt_payment_history': 1,
        'wujia_portal_debt.portal_debt_pay': 1,               # nhãn hint 11.5px
        'wujia_portal_inspection.portal_inspection_detail': 4,
        'wujia_portal_inspection.portal_inspection_remediation_form': 2,
    }

    def _arch(self, xmlid):
        return self.env.ref(xmlid).arch_db

    def _css(self, module, name):
        path = os.path.join(os.path.dirname(__file__), '..', '..', module,
                            'static', 'src', 'css', name)
        with open(path, encoding='utf-8') as fh:
            return fh.read()

    def test_call_sites_use_component(self):
        for xmlid, count in self.CALL_SITES.items():
            with self.subTest(view=xmlid):
                self.assertEqual(
                    self._arch(xmlid).count('wujia_portal_layout.wj_card_header'), count)

    # --- công nợ ---------------------------------------------------------

    def test_debt_summary_keeps_its_head_wrapper(self):
        # Hai rule hình học Figma S43 bám `.wj-debt-summary__head`: hàng 15px và
        # badge `position:absolute`. Gỡ div bọc là badge rơi xuống thành flex item.
        arch = self._arch('wujia_portal_debt.portal_debt_overview')
        self.assertIn('wj-debt-summary__head', arch)
        css = self._css('wujia_portal_debt', 'portal_debt.css')
        self.assertRegex(css, r'\.wj-debt-summary__head\s*\{[^}]*height:\s*15px')
        self.assertRegex(
            css,
            r'\.wj-debt-summary__head \.wj-debt-badge\s*\{[^}]*position:\s*absolute')

    def test_debt_summary_label_stays_11px(self):
        # Cần `.wj-debt-summary__head` phía trước để thắng biến thể (0,3,0) của
        # component, và !important vì component đặt font-size !important.
        self.assertRegex(
            self._css('wujia_portal_debt', 'portal_debt.css'),
            r'\.wj-debt-summary__head \.wj-card-header\.wj-debt-summary__hb'
            r'\s+\.wj-card-header__title\s*\{[^}]*font-size:\s*11px\s*!important')

    def test_debt_hint_label_stays_smaller_than_card_title(self):
        # Hộp hint chỉ cao 52px; lấy 18px của component là tràn.
        self.assertRegex(
            self._css('wujia_portal_debt', 'portal_debt.css'),
            r'\.wj-debt-hint \.wj-card-header\.wj-debt-hint-head'
            r'\s+\.wj-card-header__title\s*\{[^}]*font-size:\s*11\.5px\s*!important')

    # --- khảo sát --------------------------------------------------------

    def test_inspection_tab_buttons_keep_their_ids(self):
        # `portal_inspection_detail.js` lấy 2 nút này bằng getElementById; bọc vào
        # ch_control mà đổi id thì tab chết im lặng, không có lỗi JS.
        arch = self._arch('wujia_portal_inspection.portal_inspection_detail')
        for btn_id in ('pc_tab_btn_checklist', 'pc_tab_btn_exam'):
            self.assertIn(btn_id, arch)
        js_path = os.path.join(os.path.dirname(__file__), '..', '..',
                               'wujia_portal_inspection', 'static', 'src', 'js',
                               'portal_inspection_detail.js')
        with open(js_path, encoding='utf-8') as fh:
            js = fh.read()
        for btn_id in ('pc_tab_btn_checklist', 'pc_tab_btn_exam'):
            self.assertIn(btn_id, js)

    def test_section_head_severe_branch_repaints_the_title(self):
        # Nền đỏ đặt bằng inline style nên màu trắng KHÔNG thừa kế xuống được:
        # component khai color ngay trên `.wj-card-header__title`.
        css = self._css('wujia_portal_inspection', 'portal_inspection.css')
        self.assertRegex(
            css,
            r'\.wj-insp-sechead--severe \.wj-card-header__title\s*\{'
            r'[^}]*color:\s*#ffffff\s*!important')
        self.assertRegex(
            css,
            r'\.wj-insp-sechead--severe \.wj-card-header__subtitle\s*\{'
            r'[^}]*color:\s*rgba\(255, 255, 255, \.8\)\s*!important')
        # Bản mobile: rule màu xanh của nó đã là (0,4,0)!important nên rule severe
        # phải bám đủ `.wj-card-header.wj-insp-sechead__hb` mới thắng.
        self.assertRegex(
            css,
            r'\.wj-insp-sechead--m\.wj-insp-sechead--severe\s+'
            r'\.wj-card-header\.wj-insp-sechead__hb \.wj-card-header__title\s*\{'
            r'[^}]*color:\s*#ffffff\s*!important')

    def test_section_head_keeps_its_15px(self):
        self.assertRegex(
            self._css('wujia_portal_inspection', 'portal_inspection.css'),
            r'\.wj-insp-sechead \.wj-card-header\.wj-insp-sechead__hb'
            r'\s+\.wj-card-header__title\s*\{[^}]*font-size:\s*15px\s*!important')

    def test_inspection_sublabels_keep_their_own_shape(self):
        # Nhãn phụ giữa thân card (`Phân bổ kết quả`) và tiêu đề tiêu chí trong hộp
        # `Tiêu chí vi phạm` — mỗi cái một cỡ THIẾT KẾ, đều nhỏ hơn tiêu đề card.
        css = self._css('wujia_portal_inspection', 'portal_inspection.css')
        # `wj-insp-sublabel` nay lấy cỡ từ modifier chung `wj-card-header--sublabel`
        # (D3 REVIEW 2026-09-04) — call site phải mang kèm modifier đó.
        self.assertIn('wj-card-header--sublabel wj-insp-sublabel',
                      self._arch('wujia_portal_inspection.portal_inspection_detail'))
        self.assertRegex(
            css,
            r'\.wj-pc-card \.wj-card-header\.wj-insp-critlabel'
            r'\s+\.wj-card-header__title\s*\{[^}]*font-size:\s*14px\s*!important')

    def test_severe_flag_computed_once(self):
        # Ba chỗ (nền, màu chữ, badge) phải dùng CHUNG một điều kiện, không chép tay.
        arch = self._arch('wujia_portal_inspection.portal_inspection_detail')
        # 2 vòng lặp (PC + mobile), mỗi vòng đúng MỘT lần tính cờ.
        self.assertEqual(arch.count('_sec_sev'), 6)
        self.assertEqual(arch.count("sec.get('is_severe') and sec.get('total_deducted') &gt; 0"), 2)


@tagged('post_install', '-at_install', 'wujia_card_header_d3')
class TestCardHeaderD3Review(TransactionCase):
    """D3 REVIEW (2026-09-04) — phiên soát lại cả cụm bằng phép đo QUAN HỆ.

    Bảng đo cũ chỉ hỏi "số này có đúng chuẩn không" nên Pass sạch ba lần mà giao
    diện vẫn vỡ. Ở đây mỗi guard giữ một QUAN HỆ: nhãn phụ phải nhỏ hơn tiêu đề
    card cùng card, hai module cùng vai trò phải dùng CHUNG một khai báo, và chữ
    phải đủ tương phản với nền của chính nó.
    """

    def _read(self, rel):
        path = os.path.join(os.path.dirname(__file__), '..', '..', rel)
        with open(path, encoding='utf-8') as fh:
            return fh.read()

    def _arch(self, xmlid):
        return self.env.ref(xmlid).arch_db

    COMPONENTS = 'wujia_portal_layout/static/assets/css/_components.css'
    EXAM = 'wujia_portal_exam/static/src/css/portal_exam.css'
    INSP = 'wujia_portal_inspection/static/src/css/portal_inspection.css'
    RETURN = 'wujia_portal_return/static/src/css/portal_return.css'

    # --- nhãn phụ: một khai báo dùng chung, không chép hai bản -------------

    def test_sublabel_size_lives_in_one_shared_rule(self):
        # Trước phiên này `portal_return.css` và `portal_inspection.css` có HAI bản
        # trùng tuyệt đối cho cùng vai trò "nhãn phụ giữa thân card". Gộp về một
        # modifier ở component: sửa một chỗ là sửa hết (đồng bộ ở tầng code).
        css = self._read(self.COMPONENTS)
        self.assertRegex(
            css,
            r'\.wj-card-header\.wj-card-header--any\.wj-card-header--sublabel'
            r'\s+\.wj-card-header__title,[^{]*\{[^}]*font-size:\s*\.875rem\s*!important')
        # Đủ ba nền tảng, không thì bản mobile/pc rơi về 18px của component.
        for plat in ('any', 'm', 'pc'):
            self.assertIn('.wj-card-header.wj-card-header--%s.wj-card-header--sublabel'
                          % plat, css)

    def test_module_css_no_longer_redeclares_sublabel_size(self):
        # Còn bản chép tay nào là "đồng bộ" lại vỡ ngay lần sửa sau.
        for rel in (self.RETURN, self.INSP):
            with self.subTest(css=rel):
                self.assertNotRegex(
                    self._read(rel),
                    r'\.wj-(return|insp)-sublabel[^{}]*\.wj-card-header__title\s*\{'
                    r'[^}]*font-size')

    def test_sublabel_call_sites_carry_the_shared_modifier(self):
        # 5 chỗ: 4 ở phiếu trả hàng (D3e) + 1 ở khảo sát (D3f).
        self.assertEqual(
            self._arch('wujia_portal_return.portal_return_detail')
            .count('wj-card-header--sublabel'), 4)
        self.assertEqual(
            self._arch('wujia_portal_inspection.portal_inspection_detail')
            .count('wj-card-header--sublabel'), 1)

    # --- phân cấp trong CÙNG một card (RULE 1) ----------------------------

    def test_exam_nested_labels_step_down_from_the_card_title(self):
        # D3d hội tụ tiêu đề card 22->18 nhưng không hạ khối con theo, nên cả hai
        # cùng 18px và mất phân cấp — bảng đo D3d vẫn Pass vì so từng số với chuẩn
        # chứ không so hai số VỚI NHAU. Chủ dự án chốt khối con = 16px.
        css = self._read(self.EXAM)
        self.assertRegex(
            css,
            r'\.wj-exam-pc \.wj-card-header\.wj-exam-pc-sechead--sm'
            r'\s+\.wj-card-header__title,\s*'
            r'\.wj-exam-pc \.wj-card-header\.wj-exam-pc-sechead--2'
            r'\s+\.wj-card-header__title,\s*'
            r'\.wj-exam-pc \.wj-card-header\.wj-exam-pc-slots__head'
            r'\s+\.wj-card-header__title\s*\{[^}]*font-size:\s*16px\s*!important')
        # 16px phải NHỎ HƠN 18px của tiêu đề card exam (đang khai ngay trên nó).
        self.assertRegex(css, r'\.wj-exam-pc \.wj-pc-card__title\s*\{'
                              r'[^}]*font-size:\s*22px\s*!important')

    def test_exam_sectitle_rules_survive_because_a_call_site_is_still_live(self):
        # `wj-exam-pc-sectitle` CHƯA chết: còn 1 call site ở portal_exam.xml
        # ("Người tham gia" — chỗ defer chờ BA). Xoá rule là vỡ im lặng.
        css = self._read(self.EXAM)
        self.assertRegex(css, r'\.wj-exam-pc \.wj-exam-pc-sectitle\s*\{'
                              r'[^}]*font-size:\s*20px\s*!important')

    # --- tương phản chữ / nền (a11y) --------------------------------------

    def test_mobile_category_head_meets_wcag_aa(self):
        # #0284c7 trên #f1f5f9 chỉ được 3.74. Guard tính THẬT tỉ số tương phản
        # chứ không chỉ so chuỗi màu — đổi màu khác mà vẫn tối là vẫn đỏ.
        css = self._read(self.INSP)
        m = re.search(
            r'\.wj-insp-sechead--m \.wj-card-header\.wj-insp-sechead__hb'
            r'\s+\.wj-card-header__title\s*\{[^}]*color:\s*(#[0-9a-fA-F]{6})',
            css)
        self.assertTrue(m, 'mất rule màu head danh mục bản mobile')
        self.assertGreaterEqual(round(_contrast(m.group(1), '#f1f5f9'), 2), 4.5)

    # --- điều kiện tính một lần -------------------------------------------

    def test_category_severe_flag_computed_once_per_loop(self):
        # Bài học `_sec_sev` của D3f, áp cho vòng lặp thẻ phân bổ: 2 vòng (PC +
        # mobile), mỗi vòng đúng MỘT lần tính cờ, hai chỗ dùng lại.
        arch = self._arch('wujia_portal_inspection.portal_inspection_detail')
        self.assertEqual(arch.count('_cs_sev'), 6)
        self.assertEqual(arch.count("c_sum.get('is_severe')"), 2)

    # --- CSS chết đã xoá ----------------------------------------------------

    DEAD = (
        'wujia-content-card-header', 'wujia-mdash-title', 'wujia-mhist-card-head',
        'wujia-mknow-h', 'wujia-maccount-store-name', 'wj-pc-acct-staff__title',
        'wj-pc-order-head__code', 'wj-pc-cart-title', 'wj-pc-dlv-head-meta',
        'wujia-mexam-rsum-title', 'wujia-mnoti-detail-sectitle',
        'wj-exam-pc-sectitle--2',
    )
    DEAD_CSS = (COMPONENTS, EXAM,
                'wujia_portal_layout/static/assets/css/_pc_account.css',
                'wujia_portal_layout/static/assets/css/_pc_components.css',
                'wujia_portal_sale/static/src/css/portal_order.css',
                'wujia_portal_delivery/static/src/css/portal_delivery.css',
                'wujia_portal_notification/static/src/css/portal_notification.css')

    def test_dead_card_header_classes_stay_deleted(self):
        # Chúng đã hết call site sau khi D3 migrate 95 chỗ; để lại là mỗi phiên sau
        # lại phải đọc và đoán xem còn sống không.
        for rel in self.DEAD_CSS:
            css = self._read(rel)
            for cls in self.DEAD:
                with self.subTest(css=rel, cls=cls):
                    self.assertNotRegex(css, r'\.%s([^-_a-zA-Z0-9]|$)' % re.escape(cls))


def _contrast(fg, bg):
    """Tỉ số tương phản WCAG 2.1 giữa hai màu hex."""
    def lum(h):
        c = [int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)]
        c = [x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
        return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]
    a, b = sorted((lum(fg), lum(bg)), reverse=True)
    return (a + 0.05) / (b + 0.05)
