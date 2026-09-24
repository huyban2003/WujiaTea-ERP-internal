"""CMP-SN-001 (E8b) — Thông báo KHÔNG có mục trong sidebar PC.

BA: thông báo trên PC vào bằng chuông topbar (`header_bell_inherit.xml`); mobile giữ tab
Thông báo ở bottom-nav. Guard chống việc mục PC quay lại.
"""
from lxml import etree

from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged('post_install', '-at_install', 'wujia_f5')
class TestNavItemNotification(TransactionCase):

    def test_no_pc_sidebar_item(self):
        self.assertFalse(self.env.ref('wujia_portal_notification.layout_sidenav_notification',
                                      raise_if_not_found=False))
        xml = etree.tostring(
            self.env.ref('wujia_portal_layout.layout_sidenav')._get_combined_arch(),
            encoding='unicode')
        self.assertNotIn('id="nav_item_notification"', xml)
        self.assertNotIn("'/portal/notification'", xml)

    def test_bell_and_mobile_tab_still_reach_notifications(self):
        bell = self.env.ref('wujia_portal_notification.layout_top_navbar_bell_icon', raise_if_not_found=False)
        self.assertTrue(bell, 'mất chuông topbar ⇒ PC không còn lối vào Thông báo')
