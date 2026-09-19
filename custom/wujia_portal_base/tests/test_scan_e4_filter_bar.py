"""E4a (quét nhiều module) — call site FilterBar CMP-FB-001 của 2 route mẫu BA.

F5b dời khỏi `wujia_portal_layout`: khung không được biết màn nào. Hợp đồng template
+ CSS của component vẫn ở layout.
"""
import os
import re

from lxml import etree

from odoo.tests import TransactionCase, tagged

CUSTOM = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))


def _view(module, filename):
    path = os.path.join(CUSTOM, module, 'views', filename)
    with open(path, 'rb') as fh:
        return etree.fromstring(fh.read())


def _raw(module, filename):
    with open(os.path.join(CUSTOM, module, 'views', filename),
              encoding='utf-8') as fh:
        return fh.read()


def _css(module, relpath):
    with open(os.path.join(CUSTOM, module, *relpath.split('/')),
              encoding='utf-8') as fh:
        return fh.read()


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
        # E4b1 thêm call site PC cùng view ⇒ phải lọc đúng cái mobile.
        self.assertEqual(len(calls), 2)
        call = [c for c in calls
                if c.xpath('.//t[@t-set="fb_platform"]')[0].get('t-value') == "'m'"][0]
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


# --------------------------------------------------------------------------
# E4b1 — 9 thanh lọc PC về component. Quét nhiều module ⇒ ở `portal_base` (F5b).
# --------------------------------------------------------------------------

# (module, file view, bộ `name` PHẢI có — FB-10 "điều kiện trước = sau")
PC_CALL_SITES = [
    ('wujia_portal_support', 'portal_support.xml', {'state'}),
    ('wujia_portal_knowledge', 'portal_knowledge.xml', {'keyword'}),
    ('wujia_portal_return', 'portal_return_list.xml',
     {'q', 'state', 'date_from', 'date_to'}),
    ('wujia_portal_info_request', 'portal_info_request_list.xml',
     {'state', 'request_type'}),
    ('wujia_portal_delivery', 'portal_delivery.xml',
     {'q', 'bs', 'date_from', 'date_to'}),
    ('wujia_portal_notification', 'portal_notification.xml',
     {'keyword', 'type_id', 'unread', 'date_from', 'date_to', 'tab'}),
    ('wujia_portal_exam', 'portal_exam.xml',
     {'q', 'state', 'result', 'date_from', 'date_to'}),
    ('wujia_portal_report', 'portal_report_orders.xml', {'date_from', 'date_to'}),
    ('wujia_portal_sale', 'portal_order_catalog.xml', {'keyword', 'category_id'}),
]

# Họ class bản địa đã xoá ở E4b1 — còn sót là có màn dựng lại thanh lọc riêng.
DEAD_FAMILIES = ('wj-pc-noti-filter', 'wj-pc-noti-field', 'wj-rep-pcfilter__',
                 'wj-exam-pc-fc--', 'wj-exam-pc-filterbar')


def _pc_call(root):
    """t-call component mang fb_platform='pc' (mỗi view tối đa một cái)."""
    for call in root.xpath('.//t[@t-call="wujia_portal_layout.wj_filter_bar"]'):
        plat = call.xpath('.//t[@t-set="fb_platform"]')
        if plat and plat[0].get('t-value') == "'pc'":
            return call
    return None


def _names_of(call):
    """Bộ `name` mà call site khai — gom cả search/dates/selects/hidden."""
    names = set()
    for setter in call.xpath('.//t[@t-set]'):
        key, val = setter.get('t-set'), setter.get('t-value') or ''
        if key == 'fb_search':
            names |= set(re.findall(r"'name':\s*'([^']+)'", val))
        elif key == 'fb_selects':
            names |= set(re.findall(r"'name':\s*'([^']+)'", val))
        elif key == 'fb_dates':
            for side in ('from', 'to'):
                m = re.search(r"'%s_name':\s*'([^']+)'" % side, val)
                names.add(m.group(1) if m else 'date_' + side)
    names |= {i.get('name') for i in call.xpath('.//input[@type="hidden"][@name]')}
    return names


@tagged('post_install', '-at_install', 'wujia_filter_e4')
class TestFilterBarPcCallSitesE4b1(TransactionCase):
    """E4b1: mọi thanh lọc PC của portal phải là MỘT component."""

    def test_chin_man_pc_deu_goi_component(self):
        for module, fn, _names in PC_CALL_SITES:
            call = _pc_call(_view(module, fn))
            self.assertIsNotNone(call, '%s: thanh lọc PC chưa gọi wj_filter_bar' % fn)

    def test_giu_nguyen_bo_dieu_kien_loc_tung_man(self):
        """FB-10 — acceptance chính: không thêm/bớt điều kiện nào."""
        for module, fn, names in PC_CALL_SITES:
            call = _pc_call(_view(module, fn))
            self.assertEqual(_names_of(call), names, '%s: bộ điều kiện lọc lệch' % fn)

    def test_khong_con_thanh_loc_tu_dung_o_chin_man(self):
        for module, fn, _names in PC_CALL_SITES:
            root = _view(module, fn)
            for form in root.iter('form'):
                cls = form.get('class') or ''
                if 'wj-filter-card' in cls or 'morder-search' in cls:
                    continue        # thanh lọc mobile — lượt E4b2
                self.assertNotIn('row g-2', cls, '%s: còn thanh lọc Bootstrap' % fn)
                self.assertNotIn('wj-pc-filterbar', cls,
                                 '%s: còn thanh lọc PC tự dựng' % fn)

    def test_khong_con_ho_class_ban_dia_cua_thanh_loc(self):
        for module, fn, _names in PC_CALL_SITES:
            raw = _raw(module, fn)
            for dead in DEAD_FAMILIES:
                self.assertNotIn(dead, raw, '%s: còn họ class %s' % (fn, dead))

    def test_nhan_nut_ve_chuan_fb02(self):
        """Không call site nào được đè nhãn về 'Tìm'/'Lọc'/'Áp dụng'/'Đặt lại'."""
        for module, fn, _names in PC_CALL_SITES:
            call = _pc_call(_view(module, fn))
            for key in ('fb_submit_label', 'fb_reset_label'):
                self.assertEqual(call.xpath('.//t[@t-set="%s"]' % key), [],
                                 '%s: đè nhãn %s, phải dùng mặc định' % (fn, key))

    def test_hai_thanh_nam_control_dung_bien_the_dense(self):
        """Thông báo + Thi có 5 control: thiếu --dense là tụt xuống 2 hàng ở 1440."""
        for module, fn in (('wujia_portal_notification', 'portal_notification.xml'),
                           ('wujia_portal_exam', 'portal_exam.xml')):
            call = _pc_call(_view(module, fn))
            cls = call.xpath('.//t[@t-set="fb_class"]')
            self.assertTrue(cls and 'wj-pc-filterbar--dense' in cls[0].get('t-value'),
                            '%s: thiếu wj-pc-filterbar--dense' % fn)

    def test_man_thi_giu_o_ngay_dang_chu_cho_e4c(self):
        """E4c mới đổi sang type=date + wire; đổi sớm là lệch FB-10 của lượt này."""
        call = _pc_call(_view('wujia_portal_exam', 'portal_exam.xml'))
        dates = call.xpath('.//t[@t-set="fb_dates"]')[0].get('t-value')
        self.assertIn("'kind': 'text'", dates)


@tagged('post_install', '-at_install', 'wujia_filter_e4')
class TestFilterBarLegacyCssNarrowed(TransactionCase):
    """Luật 4: họ class cũ chỉ còn nhóm Khảo sát dùng ⇒ thu hẹp, KHÔNG xoá."""

    def test_ho_class_cu_thu_hep_vao_man_khao_sat(self):
        css = _css('wujia_portal_layout',
                   'static/assets/css/_pc_components.css')
        for sel in ('.wj-pc-filter-control', '.wj-pc-filter-search'):
            for line in css.splitlines():
                if line.lstrip().startswith(sel):
                    self.fail('%s còn rule toàn cục, phải nằm dưới .wj-inspection-pc'
                              % sel)
            self.assertIn('.wj-inspection-pc %s' % sel, css,
                          '%s bị xoá hẳn — màn Khảo sát sẽ gãy ngầm' % sel)

    def test_man_khao_sat_khong_bi_dung_toi(self):
        raw = _raw('wujia_portal_inspection',
                   'portal_inspection_list_templates.xml')
        self.assertIn('wj-pc-filter-control', raw)

    def test_bien_the_dense_ton_tai_trong_css(self):
        css = _css('wujia_portal_layout',
                   'static/assets/css/_pc_components.css')
        self.assertIn('.wj-pc-filterbar--dense', css)
