"""E2 / UI-STATUSBADGE-001 — StatusBadge CMP-SB-001 là MỘT component.

BA khoá bốn quan hệ, mỗi cái một test:
  1. Một class nền duy nhất, hình học đúng spec (28 · ≥84 · 0 14px · r14 · 13/600).
  2. Không biến thể theo route/breakpoint — mọi rule dáng nằm ở một chỗ.
  3. "Đã xác nhận" là INFO (lỗi gốc BA nêu: Python gán success xanh lá).
  4. Năm họ BA loại (Role · Count · FilterChip · Category · Alert) không bị kéo theo.
"""

import colorsys
import os
import re

from lxml import html

from odoo.addons.wujia_portal_base.controllers.utils import (
    MOBILE_BATCH_BADGES,
    MOBILE_ORDER_BADGES,
    MOBILE_RETURN_BADGES,
    MOBILE_TICKET_BADGES,
    STATUS_BADGE_VARIANTS,
    status_badge,
    status_badge_for,
)
from odoo.tests import tagged
from odoo.tests.common import TransactionCase

CSS = 'wujia_portal_layout/static/assets/css/_components.css'
VARS = 'wujia_portal_layout/static/assets/css/_variables.css'
# Hex BA chốt ở tab UI Component dòng 37. NỀN giữ nguyên; CHỮ 5/7 mã của BA đo
# dưới AA 4.5 nên đã làm đậm tối thiểu — test dưới khoá nền + ngưỡng AA + tông.
BA_TOKENS = {
    'neutral': ('#F3F4F6', '#6B7280'), 'info': ('#EAF7FD', '#168FC2'),
    'pending': ('#FFF7E6', '#D97706'), 'processing': ('#FEF3C7', '#B45309'),
    'success': ('#EAF8EF', '#16A34A'), 'danger': ('#FEECEC', '#DC2626'),
    'feedback': ('#F3E8FF', '#7C3AED'),
}


def _rgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


def _contrast(fg, bg):
    def lum(h):
        out = 0
        for c, w in zip(_rgb(h), (0.2126, 0.7152, 0.0722)):
            c /= 255.0
            out += w * (c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4)
        return out
    a, b = sorted((lum(fg), lum(bg)), reverse=True)
    return (a + 0.05) / (b + 0.05)


def _hue_gap(a, b):
    ha, hb = (colorsys.rgb_to_hls(*[c / 255.0 for c in _rgb(x)])[0] * 360 for x in (a, b))
    d = abs(ha - hb) % 360
    return min(d, 360 - d)


@tagged('post_install', '-at_install', 'wujia_status_badge_e2')
class TestStatusBadgeIsOneComponent(TransactionCase):

    def _read(self, rel):
        with open(os.path.join(os.path.dirname(__file__), '..', '..', rel),
                  encoding='utf-8') as fh:
            return fh.read()

    def _rule(self, css, selector):
        m = re.search(r'(?<![\w.-])' + re.escape(selector) + r'\s*\{([^}]*)\}', css)
        self.assertTrue(m, 'không tìm thấy rule %s' % selector)
        return m.group(1)

    # --- 1. hình học -------------------------------------------------------
    def test_base_class_carries_the_whole_geometry(self):
        body = self._rule(self._read(CSS), '.wj-status-badge')
        self.assertRegex(body, r'height:\s*var\(--wj-sb-h\)')
        self.assertRegex(body, r'min-width:\s*var\(--wj-sb-min-w\)')
        self.assertRegex(body, r'padding:\s*0 14px')
        self.assertRegex(body, r'border-radius:\s*var\(--wj-sb-radius\)')
        self.assertRegex(body, r'font-size:\s*13px')
        self.assertRegex(body, r'font-weight:\s*600')
        self.assertRegex(body, r'line-height:\s*1\s*;')
        self.assertRegex(body, r'white-space:\s*nowrap')
        self.assertRegex(body, r'border:\s*0')
        self.assertRegex(body, r'box-shadow:\s*none')

    def test_tokens_keep_ba_background_and_reach_wcag_aa(self):
        """Nền = hex BA. Chữ: AA 4.5 (13px không phải chữ lớn) + giữ tông của BA."""
        css = self._read(VARS)
        for variant, (bg, ba_fg) in BA_TOKENS.items():
            self.assertRegex(css, r'--wj-sb-%s-bg:\s*%s;' % (variant, bg))
            m = re.search(r'--wj-sb-%s-fg:\s*(#[0-9A-Fa-f]{6});' % variant, css)
            self.assertTrue(m, 'thiếu token chữ %s' % variant)
            fg = m.group(1)
            self.assertGreaterEqual(
                round(_contrast(fg, bg), 2), 4.5,
                '%s: %s trên %s chỉ %.2f — dưới WCAG AA' % (variant, fg, bg, _contrast(fg, bg)))
            self.assertLessEqual(
                _hue_gap(fg, ba_fg), 12,
                '%s: %s lệch tông khỏi hex BA %s — chỉ được làm đậm, không đổi màu'
                % (variant, fg, ba_fg))
        for name, value in (('h', '28px'), ('min-w', '84px'), ('radius', '14px')):
            self.assertRegex(css, r'--wj-sb-%s:\s*%s;' % (name, value))

    # --- 2. một chủ sở hữu dáng -------------------------------------------
    def test_no_route_or_breakpoint_variant_owns_the_shape(self):
        """Mọi rule chạm .wj-status-badge chỉ được sửa MÀU hoặc VỊ TRÍ, không sửa dáng."""
        shape = re.compile(r'\b(height|min-width|padding|border-radius|font-size|'
                           r'font-weight|line-height)\s*:')
        offenders = []
        for root, _dirs, files in os.walk(os.path.join(os.path.dirname(__file__), '..', '..')):
            if '/static/' not in root or not root.endswith('css'):
                continue
            for fn in files:
                if not fn.endswith('.css'):
                    continue
                path = os.path.join(root, fn)
                # bỏ comment trước khi tách rule: /* … */ dính vào selector làm
                # test đọc nhầm rule gốc thành rule có tổ tiên.
                text = re.sub(r'/\*.*?\*/', '', open(path, encoding='utf-8').read(), flags=re.S)
                for selector, body in re.findall(r'([^{}]+)\{([^}]*)\}', text):
                    if 'wj-status-badge' not in selector:
                        continue
                    # chỉ rule GỐC (tên lớp đứng một mình) được khai dáng
                    bare = selector.strip().startswith('.wj-status-badge')
                    if bare and '--' not in selector and ' ' not in selector.strip():
                        continue
                    if shape.search(body):
                        offenders.append('%s → %s' % (os.path.basename(path), selector.strip()))
        self.assertEqual(offenders, [], 'dáng badge bị ghi đè theo route/breakpoint')

    # --- 3. lỗi gốc BA nêu -------------------------------------------------
    def test_confirmed_label_is_info_not_success(self):
        self.assertEqual(MOBILE_ORDER_BADGES['sale'],
                         ('Đã xác nhận', 'wj-status-badge--info'))
        self.assertEqual(status_badge_for('Đã xác nhận'), 'wj-status-badge--info')

    def test_every_shared_map_emits_a_component_class(self):
        for name, mapping in (('order', MOBILE_ORDER_BADGES), ('batch', MOBILE_BATCH_BADGES),
                              ('return', MOBILE_RETURN_BADGES), ('ticket', MOBILE_TICKET_BADGES)):
            for state, (label, cls) in mapping.items():
                self.assertTrue(label, '%s/%s thiếu nhãn' % (name, state))
                self.assertRegex(cls, r'^wj-status-badge--(%s)$' % '|'.join(STATUS_BADGE_VARIANTS),
                                 '%s/%s còn class cũ: %s' % (name, state, cls))

    def test_unknown_variant_falls_back_to_neutral(self):
        self.assertEqual(status_badge('khong-co-that'), 'wj-status-badge--neutral')
        self.assertEqual(status_badge_for('Nhãn lạ chưa map'), 'wj-status-badge--neutral')

    # --- 4. họ ngoài phạm vi ----------------------------------------------
    def test_excluded_families_keep_their_own_class(self):
        """RoleBadge/AreaBadge/CodeBadge/loại thông báo KHÔNG được migrate (BA loại)."""
        arch = self.env.ref('wujia_portal_base.portal_franchise_information').arch_db
        root = html.fromstring('<div>%s</div>' % arch)
        role = root.xpath('.//span[contains(@t-attf-class,"wj-pc-badge--staff")]')
        area = root.xpath('.//span[contains(@class,"wj-pc-badge--area")]')
        self.assertEqual(len(role), 1, 'RoleBadge phải giữ nguyên hệ cũ')
        self.assertEqual(len(area), 1, 'AreaBadge phải giữ nguyên hệ cũ')

    def test_badge_row_does_not_stretch_the_excluded_chip(self):
        # `align-items` mặc định là stretch ⇒ chip mã cửa hàng 26,8px bị kéo lên 28px
        # theo StatusBadge. Kiểm chéo E2 đã bắt đúng lỗi này.
        self.assertRegex(self._rule(self._read(CSS), '.wujia-maccount-badgerow'),
                         r'align-items:\s*center')

    # --- 5. call site đã về component --------------------------------------
    def test_audited_screens_have_no_legacy_status_badge_left(self):
        """Màn BA chụp ảnh (Lịch sử đặt hàng) + Giao hàng + Kết quả gửi đơn: 0 họ cũ."""
        legacy = re.compile(r'(?<![\w-])(wujia-badge|wj-pc-badge|wujia-mdelivery-badge|'
                            r'wujia-mres-badge)(?![\w-])')
        for rel in ('wujia_portal_purchase_history/views/portal_history.xml',
                    'wujia_portal_delivery/views/portal_delivery.xml',
                    'wujia_portal_sale/views/portal_order_result.xml'):
            self.assertEqual(legacy.findall(self._read(rel)), [],
                             '%s còn badge họ cũ' % rel)
