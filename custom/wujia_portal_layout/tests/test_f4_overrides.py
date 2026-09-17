# -*- coding: utf-8 -*-
"""F4 — module không viết đè dáng component chung.

Rule đè đã thành biến thể ở layout (`wujia-badge--sm`, `wj-pc-badge--sm`,
`wj-card-header--eyebrow`) hoặc về dáng chuẩn. `_interaction.css` liệt kê theo
component + class đánh dấu `wj-state-surface`, không theo tên màn.
"""
import os
import re

from odoo.tests import TransactionCase, tagged

CUSTOM = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', '..'))
LAYOUT_CSS = os.path.join(CUSTOM, 'wujia_portal_layout', 'static', 'assets', 'css')


def _read(*parts):
    with open(os.path.join(CUSTOM, *parts), encoding='utf-8') as fh:
        return fh.read()


def _nocomment(css):
    return re.sub(r'/\*.*?\*/', '', css, flags=re.S)


@tagged('post_install', '-at_install', 'wujia_f4')
class TestF4Variants(TransactionCase):

    def test_badge_sm_variants_live_in_layout(self):
        comp = _nocomment(_read('wujia_portal_layout', 'static', 'assets', 'css', '_components.css'))
        self.assertRegex(comp, r'\.wujia-badge--sm\s*\{[^}]*font-size:\s*11px[^}]*padding:\s*3px 8px')
        pc = _nocomment(_read('wujia_portal_layout', 'static', 'assets', 'css', '_pc_components.css'))
        self.assertRegex(pc, r'\.wj-pc-badge--sm\s*\{[^}]*height:\s*auto[^}]*font-size:\s*11px')
        noti = _nocomment(_read('wujia_portal_notification', 'static', 'src', 'css', 'portal_notification.css'))
        self.assertNotRegex(noti, r'\.wujia-mnoti-row-tags \.wujia-badge\s*\{')
        self.assertNotRegex(noti, r'popup__item-tags \.wj-pc-badge\s*\{')
        xml = _read('wujia_portal_notification', 'views', 'portal_notification.xml')
        self.assertEqual(xml.count('wujia-badge wujia-badge--sm'), 2)
        js = _read('wujia_portal_notification', 'static', 'src', 'js', 'header_bell_badge.js')
        self.assertEqual(js.count('wj-pc-badge wj-pc-badge--sm'), 2)

    def test_eyebrow_variant_beats_compact_title(self):
        # Rule cỡ chữ compact là (0,3,0)!important ⇒ biến thể phải (0,4,0)!important.
        comp = _nocomment(_read('wujia_portal_layout', 'static', 'assets', 'css', '_components.css'))
        for plat in ('any', 'm', 'pc'):
            with self.subTest(plat=plat):
                self.assertIn('.wj-card-header.wj-card-header--%s.wj-card-header--eyebrow '
                              '.wj-card-header__title' % plat, comp)
        self.assertRegex(comp, r'--eyebrow \.wj-card-header__title\s*\{[^}]*font-size:\s*11px\s*!important')

    def test_pc_page_header_title_weight_beats_shell_h1(self):
        pc = _nocomment(_read('wujia_portal_layout', 'static', 'assets', 'css', '_pc_components.css'))
        self.assertRegex(pc, r'\.wj-pc-page-header \.wj-pc-page-header__title\s*\{[^}]*font-weight:\s*800\s*!important')
        exam = _nocomment(_read('wujia_portal_exam', 'static', 'src', 'css', 'portal_exam.css'))
        self.assertNotIn('.wj-exam-pc .wj-pc-page-header__title', exam)

    def test_no_legacy_shell_rules_left(self):
        files = (('wujia_portal_debt', 'portal_debt.css'), ('wujia_portal_delivery', 'portal_delivery.css'),
                 ('wujia_portal_exam', 'portal_exam.css'), ('wujia_portal_knowledge', 'portal_knowledge.css'),
                 ('wujia_portal_notification', 'portal_notification.css'),
                 ('wujia_portal_purchase_history', 'portal_history.css'), ('wujia_portal_return', 'portal_return.css'))
        for module, name in files:
            with self.subTest(file=name):
                css = _nocomment(_read(module, 'static', 'src', 'css', name))
                self.assertNotIn(':not(.wj-data-item)', css)


@tagged('post_install', '-at_install', 'wujia_f4')
class TestF4InteractionList(TransactionCase):

    def _lists(self):
        css = _nocomment(_read('wujia_portal_layout', 'static', 'assets', 'css', '_interaction.css'))
        return css, re.findall(r':is\(([^{]*?)\)\s*:not\(\.is-disabled\)', css)

    def test_state_lists_name_components_not_screens(self):
        css, lists = self._lists()
        self.assertEqual(len(lists), 3, 'transition + hover + active')
        for body in lists:
            self.assertIn('.wj-state-surface', body)
            self.assertIn('a.wj-data-item', body)
            self.assertNotRegex(body, r'\.wujia-m(?!account)[a-z]+-|\.wj-(debt|exam|pc-cart|pc-dlv|inspection)')
        # Nhóm Khảo sát tách rule riêng — không kéo đặc hiệu của cả danh sách.
        self.assertEqual(css.count('.wj-inspection-pc .wj-pc-page-btn:not(.is-active):not(.is-disabled)'), 3)
        self.assertNotIn(':is(.article-content', css)
        self.assertIn('.wj-richtext a', css)

    def test_screen_surfaces_carry_the_marker(self):
        sites = (
            (('wujia_portal_base', 'views', 'portal_home.xml'), 'wujia-mhome-kpi wj-state-surface', 4),
            (('wujia_portal_base', 'views', 'portal_home.xml'), 'wujia-mhome-action wj-state-surface', 6),
            (('wujia_portal_base', 'views', 'portal_home.xml'), 'wujia-kpi-card-link wj-state-surface', 4),
            (('wujia_portal_debt', 'views', 'portal_debt.xml'), 'wj-debt-pc-tab wj-state-surface', 2),
            (('wujia_portal_debt', 'views', 'portal_debt.xml'), 'wj-debt-actionrow wj-state-surface', 1),
            (('wujia_portal_debt', 'views', 'portal_debt.xml'), 'wj-debt-pc-pdf wj-state-surface', 1),
            (('wujia_portal_delivery', 'views', 'portal_delivery.xml'), 'wj-pc-dlv-chip wj-state-surface', 4),
            (('wujia_portal_knowledge', 'views', 'portal_knowledge.xml'), 'wujia-mknow-feat wj-state-surface', 1),
            (('wujia_portal_exam', 'views', 'portal_exam.xml'), 'wj-exam-pc-navbtn wj-state-surface', 2),
            (('wujia_portal_sale', 'views', 'pc_cart_panel.xml'), 'wj-state-surface', 3),
            (('wujia_portal_sale', 'views', 'portal_order_cart.xml'), 'wj-state-surface', 3),
            (('wujia_portal_sale', 'views', 'portal_order_catalog.xml'), 'wj-state-surface', 4),
            (('wujia_portal_return', 'views', 'portal_return_form.xml'), 'wujia-mreturn-btn-cancel wj-state-surface', 1),
            (('wujia_portal_base', 'views', 'store_picker_navbar.xml'), 'wujia-store-mobile-strip--clickable wj-state-surface', 1),
        )
        for parts, needle, n in sites:
            with self.subTest(file=parts[-1], needle=needle):
                self.assertEqual(_read(*parts).count(needle), n)
