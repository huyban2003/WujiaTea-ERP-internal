"""E4a — CMP-FB-001 FilterBar: hợp đồng template `wj_filter_bar` + 2 route mẫu.

Bám cột `Kết quả mong muốn` của `UI-FILTER-001` (STT 139): một component chung,
PC control 42 / mobile visual 38 + chạm 44, nhãn "Tìm kiếm"/"Xóa lọc", nhãn ngày
đọc được sau khi chọn (FB-05), không thêm/bớt điều kiện giữa PC và mobile (FB-10),
mobile không có reset (FB-03).

Call site của 2 route mẫu đã dời sang `wujia_portal_base/tests/test_scan_e4_filter_bar.py`
ở F5b — khung chỉ giữ hợp đồng template + CSS của chính nó (gallery `pc_preview` là
trang của khung).
"""
import os
import re

from lxml import etree, html

from odoo.tests import TransactionCase, tagged

TMPL = 'wujia_portal_layout.wj_filter_bar'
HERE = os.path.dirname(__file__)
CSS_DIR = os.path.join(HERE, '..', 'static', 'assets', 'css')
CUSTOM = os.path.abspath(os.path.join(HERE, '..', '..'))


def _css(name):
    with open(os.path.join(CSS_DIR, name), encoding='utf-8') as fh:
        return re.sub(r'/\*.*?\*/', '', fh.read(), flags=re.S)


def _block(css, selector):
    """Lấy nguyên khối rule theo selector đúng chữ — không regex mờ (bẫy M9)."""
    i = css.find(selector + ' {')
    assert i >= 0, 'không thấy selector %r' % selector
    return css[i:css.index('}', i) + 1]


def _view(module, filename):
    with open(os.path.join(CUSTOM, module, 'views', filename), 'rb') as fh:
        return etree.fromstring(fh.read())


@tagged('post_install', '-at_install', 'wujia_filter_e4')
class TestFilterBarTemplate(TransactionCase):

    def _render(self, slots=None, **ctx):
        sets = ''.join(
            '<t t-set="%s" t-value="%s"/>' % (k, v) for k, v in ctx.items())
        # Slot thô đi qua t-set CÓ THÂN (Markup), y như 2 call site thật.
        sets += ''.join('<t t-set="%s">%s</t>' % (k, v)
                        for k, v in (slots or {}).items())
        arch = ('<t t-name="wujia_portal_layout.wj_fb_probe"><div>'
                '<t t-call="%s">%s</t></div></t>') % (TMPL, sets)
        view = self.env['ir.ui.view'].create({
            'name': 'wj_fb_probe', 'type': 'qweb',
            'key': 'wujia_portal_layout.wj_fb_probe', 'arch_db': arch,
        })
        return html.fromstring(self.env['ir.qweb']._render(view.id, {}))

    def _pc(self, slots=None, **extra):
        ctx = {
            'fb_platform': "'pc'", 'fb_action': "'/portal/x'",
            'fb_search': "{'name': 'q', 'value': 'A', 'placeholder': 'Tìm mã'}",
            'fb_dates': "{'from': '2026-09-01', 'to': '2026-09-30'}",
            'fb_selects': ("[{'name': 'state', 'value': 'sale',"
                           " 'all_label': 'Tất cả trạng thái',"
                           " 'options': [('draft', 'Nháp'), ('sale', 'Đã xác nhận')]}]"),
            'fb_reset_url': "'/portal/x'",
        }
        ctx.update(extra)
        return self._render(slots, **ctx)

    def _mobile(self, slots=None, **extra):
        ctx = {
            'fb_platform': "'m'", 'fb_action': "'/portal/x'",
            'fb_search': "{'name': 'q', 'value': '', 'placeholder': 'Tìm mã'}",
            'fb_dates': "{'from': '', 'to': ''}",
            'fb_reset_url': "'/portal/x'",
        }
        ctx.update(extra)
        return self._render(slots, **ctx)

    # ---- khung + nền -------------------------------------------------
    def test_pc_dung_vo_filterbar_va_mobile_dung_vo_surface_card(self):
        self.assertIn('wj-pc-filterbar', self._pc().xpath('.//form')[0].get('class'))
        cls = self._mobile().xpath('.//form')[0].get('class')
        self.assertIn('wj-filter-card', cls)
        self.assertIn('wj-surface-card', cls)

    def test_form_luon_la_get_va_giu_action_cua_man(self):
        form = self._pc().xpath('.//form')[0]
        self.assertEqual(form.get('method'), 'get')
        self.assertEqual(form.get('action'), '/portal/x')

    # ---- FB-02 / FB-03 nhãn ------------------------------------------
    def test_pc_nhan_submit_la_tim_kiem_va_reset_la_xoa_loc(self):
        root = self._pc()
        self.assertEqual(
            ' '.join(root.xpath('.//button[@type="submit"]')[0]
                     .text_content().split()), 'Tìm kiếm')
        self.assertEqual(
            root.xpath('.//a[contains(@class, "wj-pc-btn--secondary")]')[0]
            .text_content().strip(), 'Xóa lọc')

    def test_mobile_khong_co_reset_du_truyen_reset_url(self):
        """FB-03: 'Không thêm hàng/nút/link Xóa lọc vào Filter' ở mobile."""
        root = self._mobile()
        self.assertEqual(root.xpath('.//a'), [])
        self.assertNotIn('Xóa lọc', root.text_content())

    def test_mobile_co_o_tim_thi_khong_them_hang_hanh_dong(self):
        """FB-03: mobile đã có nút kính lúp cạnh ô tìm — không thêm hàng nút thứ hai."""
        root = self._mobile()
        self.assertEqual(len(root.xpath('.//button[@type="submit"]')), 1)
        self.assertEqual(
            root.xpath('.//*[contains(@class, "wj-filter-actions")]'), [])

    def test_mobile_khong_co_reset_ca_khi_man_khong_co_o_tim(self):
        """Màn mobile không có ô tìm vẫn render hàng hành động — reset vẫn phải vắng."""
        root = self._mobile(fb_search='False')
        self.assertEqual(len(root.xpath('.//button[@type="submit"]')), 1)
        self.assertEqual(root.xpath('.//a'), [])

    def test_pc_khong_co_reset_khi_man_khong_truyen_reset_url(self):
        root = self._pc(fb_reset_url='False')
        self.assertEqual(root.xpath('.//a'), [])

    # ---- FB-04 SearchField -------------------------------------------
    def test_o_tim_boc_trong_label_de_vung_cham_44_khong_no_hop_38(self):
        for root in (self._pc(), self._mobile()):
            field = root.xpath('.//label[@class="wj-filter-search-field"]')
            self.assertEqual(len(field), 1)
            self.assertEqual(len(field[0].xpath('./input[@type="text"]')), 1)

    def test_nut_tim_icon_only_cua_mobile_co_ten_doc_duoc(self):
        btn = self._mobile().xpath('.//button[@class="wj-filter-search-btn"]')
        self.assertEqual(len(btn), 1)
        self.assertEqual(btn[0].get('aria-label'), 'Tìm kiếm')
        self.assertEqual(btn[0].text_content().strip(), '')

    def test_o_tim_giu_gia_tri_va_placeholder_cua_man(self):
        inp = self._pc().xpath('.//input[@name="q"]')[0]
        self.assertEqual(inp.get('value'), 'A')
        self.assertEqual(inp.get('placeholder'), 'Tìm mã')

    # ---- FB-05 khoảng ngày -------------------------------------------
    def test_o_ngay_co_nhan_chu_doc_duoc_ca_khi_da_chon_gia_tri(self):
        root = self._pc()
        labels = [e.text_content().strip()
                  for e in root.xpath('.//span[@class="wj-filter-date__label"]')]
        self.assertEqual(labels, ['Từ', 'Đến'])
        self.assertEqual(root.xpath('.//input[@name="date_from"]')[0].get('value'),
                         '2026-09-01')

    def test_o_ngay_co_aria_label_phan_biet(self):
        root = self._mobile()
        self.assertEqual(
            [root.xpath('.//input[@name="date_from"]')[0].get('aria-label'),
             root.xpath('.//input[@name="date_to"]')[0].get('aria-label')],
            ['Từ ngày', 'Đến ngày'])

    def test_hop_nhin_thay_38_nam_trong_wrapper_cham_44(self):
        """Vùng chạm ở wrapper `--hit`, hộp nhìn thấy là `__box` — đo được."""
        for root in (self._pc(), self._mobile()):
            hit = root.xpath('.//label[contains(@class, "wj-filter-date--hit")]')
            self.assertEqual(len(hit), 2)
            for h in hit:
                self.assertEqual(len(h.xpath('./span[@class="wj-filter-date__box"]')), 1)

    def test_chi_kep_min_max_khi_man_yeu_cau(self):
        root = self._pc(fb_dates="{'from': '2026-09-01', 'to': '2026-09-30',"
                                 " 'clamp': True}")
        self.assertEqual(root.xpath('.//input[@name="date_from"]')[0].get('max'),
                         '2026-09-30')
        self.assertEqual(root.xpath('.//input[@name="date_to"]')[0].get('min'),
                         '2026-09-01')
        plain = self._pc()
        self.assertIsNone(plain.xpath('.//input[@name="date_from"]')[0].get('max'))

    def test_khong_truyen_ngay_thi_khong_render_o_ngay(self):
        root = self._pc(fb_dates='False')
        self.assertEqual(root.xpath('.//input[@type="date"]'), [])

    # ---- select + slot thô -------------------------------------------
    def test_select_giu_gia_tri_dang_chon_va_dong_tat_ca(self):
        opts = self._pc().xpath('.//select[@name="state"]/option')
        self.assertEqual([o.get('value') for o in opts], ['', 'draft', 'sale'])
        self.assertEqual(opts[0].text_content().strip(), 'Tất cả trạng thái')
        self.assertEqual([o.get('selected') for o in opts],
                         [None, None, 'selected'])

    def test_select_chi_tu_submit_khi_man_yeu_cau(self):
        auto = self._pc(fb_selects="[{'name': 'state', 'auto': True,"
                                   " 'options': [('a', 'A')]}]")
        self.assertEqual(auto.xpath('.//select[@name="state"]')[0].get('onchange'),
                         'this.form.requestSubmit()')
        self.assertIsNone(
            self._pc().xpath('.//select[@name="state"]')[0].get('onchange'))

    def test_slot_tho_hidden_chips_error_giu_nguyen_markup_cua_man(self):
        root = self._mobile(slots={
            'fb_hidden': '<input type="hidden" name="bs" value=""/>',
            'fb_chips': '<div class="wj-filter-chips">'
                        '<a class="wj-filter-chip" href="#">X</a></div>',
            'fb_error': '<p class="wj-filter-error">Sai ngày</p>',
        })
        form = root.xpath('.//form')[0]
        self.assertEqual(len(form.xpath('./input[@name="bs"][@type="hidden"]')), 1)
        self.assertEqual(len(form.xpath('.//a[@class="wj-filter-chip"]')), 1)
        self.assertEqual(len(form.xpath('./p[@class="wj-filter-error"]')), 1)


@tagged('post_install', '-at_install', 'wujia_filter_e4')
class TestFilterBarCallSites(TransactionCase):
    """FB-09: trang gallery của chính khung không được là nguồn dáng thứ hai."""

    def test_gallery_pc_preview_khong_la_nguon_dang_thu_hai(self):
        root = _view('wujia_portal_layout', 'pc_preview.xml')
        self.assertEqual(
            len(root.xpath('.//t[@t-call="wujia_portal_layout.wj_filter_bar"]')), 1)
        self.assertEqual(
            [e for e in root.iter() if 'wj-pc-filter-control' in (e.get('class') or '')],
            [])


@tagged('post_install', '-at_install', 'wujia_filter_e4')
class TestFilterBarCss(TransactionCase):
    """Token đo được của FB-02/FB-03 phải nằm ở CSS component, không rải theo màn."""

    def test_hop_nhin_thay_38_va_vung_cham_44(self):
        css = _css('_components.css')
        box = _block(css, '.wj-filter-date__box')
        self.assertIn('height: 38px', box)
        hit = _block(css, '.wj-filter-date--hit,\n.wj-filter-selectwrap')
        self.assertIn('min-height: 44px', hit)
        self.assertIn('border: 0', hit)
        self.assertIn('label.wj-filter-search-field input { height: 38px; }', css)
        self.assertIn('label.wj-filter-search-field { min-height: 44px; }', css)

    def test_nut_tim_38_co_vung_cham_44_bang_pseudo(self):
        css = _css('_components.css')
        visible = _block(
            css, '.wj-filter-search > label.wj-filter-search-field + '
                 '.wj-filter-search-btn')
        self.assertIn('height: 38px', visible)
        self.assertIn('width: 38px', visible)
        pseudo = _block(
            css, '.wj-filter-search > label.wj-filter-search-field + '
                 '.wj-filter-search-btn::before')
        self.assertIn('width: 44px', pseudo)
        self.assertIn('height: 44px', pseudo)

    def test_gap_hang_loc_mobile_la_8(self):
        css = _css('_components.css')
        self.assertIn('.wj-filter-search { display: flex; gap: 8px; }', css)

    def test_control_pc_cao_42_bang_token_chung(self):
        css = _css('_pc_components.css')
        blk = _block(css, '.wj-pc-filterbar .wj-filter-date__box,\n'
                          '.wj-pc-filterbar .wj-filter-selectwrap > .wj-filter-select')
        self.assertIn('height: var(--wj-pc-input-h)', blk)
        self.assertIn('height: var(--wj-pc-input-h)',
                      _block(css, '.wj-pc-filterbar label.wj-filter-search-field input'))
        self.assertNotIn('#', blk)


@tagged('post_install', '-at_install', 'wujia_filter_e4')
class TestFilterBarE4b1Contract(TransactionCase):
    """E4b1 — hai điểm hợp đồng mới khi nhân component ra 9 thanh lọc PC."""

    _render = TestFilterBarTemplate._render
    _pc = TestFilterBarTemplate._pc

    def test_o_ngay_mac_dinh_la_type_date(self):
        doc = self._pc()
        kinds = [i.get('type') for i in doc.xpath('//input[starts-with(@name, "date_")]')]
        self.assertEqual(kinds, ['date', 'date'])

    def test_kind_text_giu_duoc_o_ngay_dang_chu_cua_man_thi(self):
        """Màn Thi còn ô ngày dạng chữ; đổi sớm sang date là đổi hành vi lọc (E4c)."""
        doc = self._pc(fb_dates="{'kind': 'text'}")
        kinds = [i.get('type') for i in doc.xpath('//input[starts-with(@name, "date_")]')]
        self.assertEqual(kinds, ['text', 'text'])
        # Nhãn "Từ"/"Đến" vẫn đọc được (FB-05) dù ô là chữ.
        self.assertEqual(
            [s.text for s in doc.xpath('//span[@class="wj-filter-date__label"]')],
            ['Từ', 'Đến'])

    def test_fb_class_di_thang_vao_vo_form(self):
        doc = self._pc(fb_class="'wj-pc-filterbar--dense'")
        cls = doc.xpath('//form')[0].get('class')
        self.assertIn('wj-pc-filterbar', cls)
        self.assertIn('wj-pc-filterbar--dense', cls)

    def test_dense_hep_hon_mac_dinh_o_ca_ba_loai_control(self):
        css = _css('_pc_components.css')
        for sel, wider in (
                ('.wj-pc-filterbar--dense .wj-filter-search',
                 '.wj-pc-filterbar .wj-filter-search'),
                ('.wj-pc-filterbar--dense .wj-filter-date--hit',
                 '.wj-pc-filterbar .wj-filter-date--hit'),
                ('.wj-pc-filterbar--dense .wj-filter-selectwrap',
                 '.wj-pc-filterbar .wj-filter-selectwrap')):
            px = lambda blk: int(re.search(r'flex:[^;]*?(\d+)px', blk).group(1))
            self.assertLess(px(_block(css, sel)), px(_block(css, wider)),
                            '%s phải hẹp hơn mặc định' % sel)

    def test_select_pc_trung_hoa_padding_important_cua_shell(self):
        """dashboard.css có `select { padding: 5px !important }` — rule thường thua."""
        blk = _block(_css('_pc_components.css'),
                     '.wj-pc-filterbar select.wj-filter-select')
        self.assertIn('!important', blk)
