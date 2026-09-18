"""E4a (quét nhiều module) — call site FilterBar CMP-FB-001 của 2 route mẫu BA.

F5b dời khỏi `wujia_portal_layout`: khung không được biết màn nào. Hợp đồng template
+ CSS của component vẫn ở layout.
"""
import os

from lxml import etree

from odoo.tests import TransactionCase, tagged

CUSTOM = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))


def _view(module, filename):
    path = os.path.join(CUSTOM, module, 'views', filename)
    with open(path, 'rb') as fh:
        return etree.fromstring(fh.read())


@tagged('post_install', '-at_install', 'wujia_filter_e4')
class TestFilterBarCallSites(TransactionCase):
    """FB-09 mục 1–2: hai route mẫu BA phải gọi component, không tự dựng lại."""

    def test_pc_lich_su_dat_hang_goi_component_va_giu_page_size(self):
        root = _view('wujia_portal_purchase_history', 'portal_history.xml')
        calls = root.xpath('.//t[@t-call="wujia_portal_layout.wj_filter_bar"]')
        self.assertEqual(len(calls), 1)
        # WJ-PH-008: mất hidden page_size là người dùng phải chọn lại số dòng.
        self.assertEqual(
            len(calls[0].xpath('.//input[@name="page_size"][@type="hidden"]')), 1)

    def test_mobile_giao_hang_goi_component_giu_id_va_hidden_bs(self):
        root = _view('wujia_portal_delivery', 'portal_delivery.xml')
        calls = root.xpath('.//t[@t-call="wujia_portal_layout.wj_filter_bar"]')
        self.assertEqual(len(calls), 1)
        call = calls[0]
        self.assertEqual(
            call.xpath('.//t[@t-set="fb_id"]')[0].get('t-value'), "'wj-dlv-mform'")
        bs = call.xpath('.//input[@name="bs"][@id="wj-dlv-bs"]')
        self.assertEqual(len(bs), 1)
        self.assertNotIn('t-if', bs[0].attrib)

    def test_hai_man_mau_khong_con_tu_dung_thanh_loc(self):
        for mod, fn, old in (
                ('wujia_portal_purchase_history', 'portal_history.xml',
                 'wj-pc-filterbar'),
                ('wujia_portal_delivery', 'portal_delivery.xml', 'wj-filter-card')):
            root = _view(mod, fn)
            forms = [f for f in root.iter('form')
                     if old in (f.get('class') or '')]
            self.assertEqual(forms, [], f'{fn}: còn form tự dựng {old}')


@tagged('post_install', '-at_install', 'wujia_filter_e4')
class TestFilterBarCallSiteStyle(TransactionCase):

    def test_khong_con_inline_style_o_thanh_loc_hai_man_mau(self):
        for mod, fn in (('wujia_portal_purchase_history', 'portal_history.xml'),
                        ('wujia_portal_delivery', 'portal_delivery.xml'),
                        ('wujia_portal_layout', 'pc_preview.xml')):
            root = _view(mod, fn)
            for call in root.xpath('.//t[@t-call="wujia_portal_layout.wj_filter_bar"]'):
                self.assertEqual(call.xpath('.//*[@style]'), [],
                                 f'{fn}: còn inline style trong thanh lọc')
