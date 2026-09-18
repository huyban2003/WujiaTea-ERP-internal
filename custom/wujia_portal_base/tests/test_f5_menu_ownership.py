"""F5a — danh sách vàng của menu + QUYỀN SỞ HỮU từng mục (guard nhiều module ⇒ L3a).

Vì sao ở `wujia_portal_base`: mỗi phép kiểm ở đây đụng 9–11 module cùng lúc; cắt nhỏ
về từng module thì không còn chỗ nào đo được THỨ TỰ và tính TOÀN VẸN của menu.
Mỗi module vẫn có test riêng cho mục của mình (`test_f5_nav_item.py`).

Ý nghĩa: gỡ một module portal ⇒ mục của nó biến mất, khung không gãy. Bằng chứng là
mỗi <li> mục menu thuộc `ir.model.data` của MODULE SỞ HỮU, không phải của khung.
"""
import re

from lxml import etree

from odoo.tests import tagged
from odoo.tests.common import HttpCase

# (id của <li>, module sở hữu, href, icon, nhãn) — thứ tự đúng như sidebar PC hiển thị.
GOLDEN_SIDENAV = [
    ('nav_item_home', 'wujia_portal_base', '/portal', 'feather icon-home', 'Trang chủ'),
    ('nav_item_order', 'wujia_portal_sale', '/portal/order', 'feather icon-shopping-cart', 'Đặt hàng'),
    ('nav_item_history', 'wujia_portal_purchase_history', '/portal/purchase-history', 'feather icon-clock', 'Lịch sử đặt hàng'),
    ('nav_item_delivery', 'wujia_portal_delivery', '/portal/delivery', 'feather icon-truck', 'Giao hàng'),
    ('nav_item_debt', 'wujia_portal_debt', '/portal/debt', 'feather icon-credit-card', 'Công nợ'),
    ('nav_item_notification', 'wujia_portal_notification', '/portal/notification', 'feather icon-bell', 'Thông báo'),
    ('nav_item_knowledge', 'wujia_portal_knowledge', '/portal/knowledge', 'feather icon-book', 'Kiến thức'),
    ('nav_item_support', 'wujia_portal_support', '/portal/support', 'feather icon-life-buoy', 'Hỗ trợ'),
    ('nav_item_exam', 'wujia_portal_exam', '/portal/exam', 'feather icon-edit', 'Đăng ký thi'),
    # Khảo sát: view của anh Thái (priority 101), chèn sau mục Đăng ký thi.
    ('nav_item_inspection', 'wujia_portal_inspection', '/portal/inspection', 'feather icon-clipboard', 'Khảo sát'),
    # Tài khoản: /portal/profile + /portal/change-password là route của CHÍNH khung.
    ('nav_item_account', 'wujia_portal_layout', '/portal/profile', 'feather icon-user', 'Tài khoản'),
]

# Đường dẫn con ⇒ mục nào phải sáng.
ACTIVE_CASES = [
    ('/portal', 'nav_item_home'),
    ('/portal/order', 'nav_item_order'),
    ('/portal/purchase-history', 'nav_item_history'),
    ('/portal/profile', 'nav_item_account'),
    # route của wujia_portal_base nhưng sáng ở mục Tài khoản của khung —
    # base tự khai qua `_nav_acct_extra`, khung không biết đường dẫn này.
    ('/portal/franchise-information', 'nav_item_account'),
]


@tagged('post_install', '-at_install', 'wujia_f5')
class TestMenuOwnership(HttpCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        env = cls.env
        cls.franchise = env['wujia.franchise.management'].create({
            'code': 'F5MN', 'name': 'F5 menu store', 'franchise_end_date': '2030-01-01',
            'partner_id': env['res.partner'].create({'name': 'F5 menu partner'}).id})
        cls.user = env['res.users'].create({
            'name': 'f5_menu', 'login': 'f5_menu', 'password': 'f5_menu',
            'group_ids': [(6, 0, [env.ref('base.group_portal').id])]})
        env['wujia.franchise.member'].create({
            'user_id': cls.user.id, 'franchise_id': cls.franchise.id, 'role': 'owner'})

    def _sidenav(self, route='/portal'):
        self.authenticate('f5_menu', 'f5_menu')
        res = self.url_open(route, timeout=30)
        self.assertEqual(res.status_code, 200, route)
        html = etree.HTML(res.text)
        ul = html.xpath("//ul[@id='main-menu-navigation']")
        self.assertTrue(ul, f'không thấy sidebar ở {route}')
        return ul[0]

    def test_sidenav_golden_list(self):
        """11 mục, đúng thứ tự, đúng href + icon + nhãn."""
        items = [li for li in self._sidenav().xpath('./li')
                 if 'navigation-header' not in (li.get('class') or '')]
        self.assertEqual([li.get('id') for li in items],
                         [g[0] for g in GOLDEN_SIDENAV])
        for li, (nid, _mod, href, icon, label) in zip(items, GOLDEN_SIDENAV):
            link = li.xpath('./a')[0]
            self.assertEqual(link.get('href'), href, nid)
            text = re.sub(r'\s+', ' ', ''.join(link.itertext())).strip()
            self.assertEqual(text, label, nid)   # khớp TUYỆT ĐỐI: đổi nhãn là đỏ
            if icon:
                self.assertIn(icon, etree.tostring(link, encoding='unicode'), nid)

    def test_every_item_belongs_to_the_module_owning_the_route(self):
        """Mục menu nằm trong view của MODULE SỞ HỮU ⇒ gỡ module là mất mục."""
        for nid, module, *_rest in GOLDEN_SIDENAV:
            shell = self.env.ref('wujia_portal_layout.layout_sidenav')
            views = shell + self.env['ir.ui.view'].search([('inherit_id', '=', shell.id)])
            owners = set()
            for view in views:
                # Chỉ tính view TẠO ra mục; view chỉ NHẮC id trong xpath neo không phải
                # chủ sở hữu (wujia_portal_inspection neo vào //li[@id='nav_item_exam']).
                if not re.search(rf'<li[^>]*id="{nid}"', (view.arch or '').replace("'", '"')):
                    continue
                data = self.env['ir.model.data'].search(
                    [('model', '=', 'ir.ui.view'), ('res_id', '=', view.id)], limit=1)
                owners.add(data.module)
            self.assertEqual(owners, {module},
                             f'{nid} phải do {module} khai, đang thấy {owners}')

    def test_active_item_follows_the_route(self):
        for route, nid in ACTIVE_CASES:
            ul = self._sidenav(route)
            active = [li.get('id') for li in ul.xpath('./li')
                      if 'active' in (li.get('class') or '')]
            self.assertEqual(active, [nid], route)

    def test_bottomnav_more_button_is_active_when_no_tab_matches(self):
        """Nút "Thêm" sáng khi không tab nào sáng (hành vi Sprint 11)."""
        self.authenticate('f5_menu', 'f5_menu')
        for route, more_active in (('/portal', False), ('/portal/order', False),
                                   ('/portal/support', True)):
            html = etree.HTML(self.url_open(route, timeout=30).text)
            more = html.xpath("//button[@data-wujia-more='toggle']")[0]
            self.assertEqual('is-active' in (more.get('class') or ''), more_active, route)
