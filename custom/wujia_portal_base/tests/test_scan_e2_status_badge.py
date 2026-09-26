"""E2 / UI-STATUSBADGE-001 — phần StatusBadge chạm nhiều module.

F5b dời khỏi `wujia_portal_layout`: bảng trạng thái → badge nằm ở `portal_base`, và
việc quét call site là việc của tầng ghép. Hợp đồng dáng của component vẫn ở layout.
"""
import os
import re

from lxml import html

from odoo.addons.wujia_portal_base.controllers.utils import (
    MOBILE_BATCH_BADGES,
    MOBILE_ORDER_BADGES,
    MOBILE_RETURN_BADGES,
    STATUS_BADGE_VARIANTS,
    status_badge,
    status_badge_for,
)
from odoo.tests import tagged
from odoo.tests.common import TransactionCase

CUSTOM = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', '..'))


@tagged('post_install', '-at_install', 'wujia_status_badge_e2')
class TestStatusBadgeMapsAndCallSites(TransactionCase):

    def _read(self, rel):
        with open(os.path.join(CUSTOM, rel), encoding='utf-8') as fh:
            return fh.read()

    # --- 2. một chủ sở hữu dáng -------------------------------------------
    def test_no_route_or_breakpoint_variant_owns_the_shape(self):
        """Mọi rule chạm .wj-status-badge chỉ được sửa MÀU hoặc VỊ TRÍ, không sửa dáng."""
        shape = re.compile(r'\b(height|min-width|padding|border-radius|font-size|'
                           r'font-weight|line-height)\s*:')
        offenders = []
        for root, _dirs, files in os.walk(CUSTOM):
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
                    # LC-25 (BA 06/09): ListCard được dùng badge chữ 12 qua MỘT
                    # modifier chung. Miễn trừ hẹp: chỉ `--compact`, chỉ font-size.
                    if selector.strip() == '.wj-status-badge--compact':
                        khai = {d.split(':')[0].strip()
                                for d in body.split(';') if ':' in d}
                        if khai == {'font-size'}:
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
                              ('return', MOBILE_RETURN_BADGES)):
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
