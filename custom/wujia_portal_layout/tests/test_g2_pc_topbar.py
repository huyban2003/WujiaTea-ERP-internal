# -*- coding: utf-8 -*-
"""G2 — top bar PC ≥1200: action circle giỏ + chuông (UI-PC-TOPBAR-REG-001).

Gốc hồi quy: `.nav-link{display:block}` của web.assets_frontend nạp SAU _components.css nên
`inline-flex` của `.wujia-header-icon-btn` thua ⇒ icon dồn góc trên-trái circle, badge đè nét
khi 2 chữ số. Vuexy `.header-navbar .navbar-container ul.nav li i.ficon` (0,4,3) còn giữ cỡ
icon 1.5rem. Số đo trình duyệt: badge ∩ hộp icon = 0 với 0/4/12 món ở 1440/1280/1200.
"""
import re

from odoo.tests import TransactionCase, tagged

from .test_g1_mobile_density import _css, _media_blocks, _rules

PC_MQ = '@media (min-width: 1200px)'
BTN = ('.wujia-navbar .navbar-container ul.nav li.wujia-header-icon-item'
       ' > a.wujia-header-icon-btn')
VUEXY_ICON = (0, 4, 3)


def _specificity(selector):
    s = re.sub(r':not\(([^)]*)\)', r' \1', selector)
    ids = len(re.findall(r'#[\w-]+', s))
    classes = len(re.findall(r'\.[\w-]+|\[[^\]]+\]|:(?!:)[\w-]+', s))
    elements = len(re.findall(r'(?:^|[\s>+~])([a-z][\w-]*)', s))
    return ids, classes, elements


@tagged('post_install', '-at_install', 'wujia_pc_topbar_g2')
class TestPcTopbarG2(TransactionCase):

    def setUp(self):
        super().setUp()
        self.pc = [r for blk in _media_blocks(_css('_pc_account.css'), PC_MQ) for r in _rules(blk)]

    def _body(self, selector):
        hits = [b for s, b in self.pc if s == selector]
        self.assertTrue(hits, 'thiếu rule ≥1200: %s' % selector)
        return hits[0]

    def test_circle_tu_khai_flex_can_giua(self):
        body = self._body(BTN)
        for decl in ('display: inline-flex', 'align-items: center', 'justify-content: center',
                     'width: 40px', 'height: 40px'):
            self.assertIn(decl, body)

    def test_co_icon_thang_vuexy(self):
        for icon, size in (('i.icon-shopping-cart', '19px'), ('i.icon-bell', '20px')):
            sel = '%s > %s' % (BTN, icon)
            self.assertIn('font-size: %s' % size, self._body(sel))
            self.assertGreater(_specificity(sel), VUEXY_ICON, sel)

    def test_badge_nam_tren_hop_icon(self):
        """Circle 40, icon 20 căn giữa ⇒ đỉnh icon y=10; badge cao 18 phải có top ≤ -8."""
        body = self._body('%s > .wujia-header-badge' % BTN)
        top = int(re.search(r'top:\s*(-?\d+)px', body).group(1))
        self.assertLessEqual(top + 18, 10)
        self.assertRegex(body, r'right:\s*-\d+px')

    def test_khong_dung_rule_chung_va_mobile(self):
        """Sửa chỉ trong khối ≥1200 — `.wujia-header-badge` gốc dùng chung 8 module + header mobile."""
        comps = _css('_components.css')
        base = [b for s, b in _rules(comps) if s == '.wujia-header-badge']
        self.assertIn('top: 2px', base[0])
        self.assertIn('right: 0', base[0])
