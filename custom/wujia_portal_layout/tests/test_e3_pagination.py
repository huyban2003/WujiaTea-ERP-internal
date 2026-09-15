"""E3a — CMP-PGNT-001 Pagination: hợp đồng của `build_pager` + `wj_pagination`.

Bám cột `Kết quả mong muốn` của `UI-PAGINATION-001` (STT 130): một component chung,
ẩn khi `totalPages <= 1`, giữ filter khi đổi trang, token 36/10/8 + chạm 44, a11y
`nav[aria-label]` + `aria-current` + tên cho nút icon, không `href="#"`.
"""
import os
import re

from lxml import etree, html

from odoo.tests import TransactionCase, tagged

from odoo.addons.wujia_portal_base.controllers.utils import ELLIPSIS, build_pager

TMPL = 'wujia_portal_layout.wj_pagination'
HERE = os.path.dirname(__file__)
CSS_DIR = os.path.join(HERE, '..', 'static', 'assets', 'css')
CUSTOM = os.path.abspath(os.path.join(HERE, '..', '..'))


def _css(name):
    with open(os.path.join(CSS_DIR, name), encoding='utf-8') as fh:
        return re.sub(r'/\*.*?\*/', '', fh.read(), flags=re.S)


def _view(module, filename):
    with open(os.path.join(CUSTOM, module, 'views', filename), 'rb') as fh:
        return etree.fromstring(fh.read())


@tagged('post_install', '-at_install', 'wujia_pagination_e3')
class TestBuildPager(TransactionCase):
    """Phép toán phân trang — trước E3 bị chép tay ở 7 controller."""

    def test_so_trang_va_khoang_hien_thi(self):
        p = build_pager(11, 1, 10, path='/x')
        self.assertEqual((p['total_pages'], p['from_'], p['to']), (2, 1, 10))
        p = build_pager(11, 2, 10, path='/x')
        self.assertEqual((p['page'], p['from_'], p['to']), (2, 11, 11))

    def test_trang_vuot_nguong_ve_trang_cuoi(self):
        self.assertEqual(build_pager(11, 99, 10, path='/x')['page'], 2)

    def test_trang_rac_va_am_ve_mot(self):
        for bad in ('abc', 0, -5, None):
            self.assertEqual(build_pager(50, bad, 10, path='/x')['page'], 1)

    def test_khong_co_ban_ghi_van_mot_trang_va_khoang_rong(self):
        p = build_pager(0, 1, 10, path='/x')
        self.assertEqual((p['total_pages'], p['from_'], p['to']), (1, 0, 0))

    def test_page_size_bi_kep_va_rac_ve_mac_dinh(self):
        self.assertEqual(build_pager(10, 1, 9999, path='/x')['page_size'], 100)
        self.assertEqual(build_pager(10, 1, 'x', path='/x')['page_size'], 20)

    def test_numbers_rut_gon_bang_dau_ba_cham(self):
        nums = build_pager(200, 10, 10, path='/x')['numbers']
        self.assertEqual(nums[0], 1)
        self.assertEqual(nums[-1], 20)
        self.assertIn(ELLIPSIS, nums)
        self.assertIn(10, nums)

    def test_chi_dung_url_cho_so_trang_thuc_su_hien(self):
        """1500 user: 500 trang mà dựng 500 URL là phí — chỉ dựng chỗ render."""
        p = build_pager(5000, 1, 10, path='/x')
        self.assertEqual(p['total_pages'], 500)
        self.assertEqual(set(p['urls']), {n for n in p['numbers'] if n != ELLIPSIS})

    def test_url_mang_so_trang(self):
        p = build_pager(30, 2, 10, path='/portal/x')
        self.assertTrue(p['prev_url'].startswith('/portal/x?'))
        self.assertIn('page=1', p['prev_url'])
        self.assertIn('page=3', p['next_url'])


@tagged('post_install', '-at_install', 'wujia_pagination_e3')
class TestPaginationTemplate(TransactionCase):

    def _render(self, pgn):
        arch = ('<t t-name="wujia_portal_layout.wj_pgn_probe">'
                '<div><t t-call="%s"/></div></t>') % TMPL
        view = self.env['ir.ui.view'].create({
            'name': 'wj_pgn_probe', 'type': 'qweb',
            'key': 'wujia_portal_layout.wj_pgn_probe', 'arch_db': arch,
        })
        rendered = self.env['ir.qweb']._render(view.id, {'pgn': pgn})
        return html.fromstring(rendered)

    def test_mot_trang_thi_khong_render_gi(self):
        root = self._render(build_pager(5, 1, 10, path='/x'))
        self.assertEqual(root.xpath('.//nav'), [])

    def test_khong_co_pgn_thi_khong_no(self):
        self.assertEqual(self._render(None).xpath('.//nav'), [])

    def test_nav_co_nhan_va_trang_hien_tai_co_aria_current(self):
        root = self._render(build_pager(30, 2, 10, path='/x'))
        nav = root.xpath('.//nav[@class="wj-pagination"]')
        self.assertEqual(len(nav), 1)
        self.assertEqual(nav[0].get('aria-label'), 'Phân trang')
        cur = root.xpath('.//*[@aria-current="page"]')
        self.assertEqual([e.text.strip() for e in cur], ['2'])

    def test_nut_truoc_sau_co_ten_doc_duoc(self):
        root = self._render(build_pager(30, 2, 10, path='/x'))
        labels = [e.text.strip()
                  for e in root.xpath('.//span[@class="wj-pagination__label"]')]
        self.assertEqual(labels, ['Trang trước', 'Trang sau'])

    def test_trang_dau_thi_nut_truoc_khong_phai_link(self):
        root = self._render(build_pager(30, 1, 10, path='/x'))
        disabled = root.xpath('.//*[@aria-disabled="true"]')
        self.assertEqual(len(disabled), 1)
        self.assertEqual(disabled[0].tag, 'span')
        self.assertIn('is-disabled', disabled[0].get('class'))

    def test_trang_cuoi_thi_nut_sau_khong_phai_link(self):
        root = self._render(build_pager(30, 3, 10, path='/x'))
        disabled = root.xpath('.//*[@aria-disabled="true"]')
        self.assertEqual(len(disabled), 1)
        self.assertEqual(
            disabled[0].xpath('.//span[@class="wj-pagination__label"]')[0].text.strip(),
            'Trang sau')

    def test_khong_bao_gio_dung_href_thang(self):
        root = self._render(build_pager(30, 2, 10, path='/x'))
        hrefs = root.xpath('.//a/@href')
        self.assertTrue(hrefs)
        self.assertNotIn('#', ''.join(hrefs))

    def test_nhan_trang_x_tren_y_cho_mobile(self):
        root = self._render(build_pager(30, 2, 10, path='/x'))
        status = root.xpath('.//span[@class="wj-pagination__status"]')
        self.assertEqual(len(status), 1)
        self.assertEqual(' '.join(status[0].text_content().split()), 'Trang 2 / 3')

    def test_count_dung_don_vi_cua_man_hinh(self):
        root = self._render(build_pager(30, 1, 10, path='/x', item_label='yêu cầu'))
        count = root.xpath('.//span[@class="wj-pagination__count"]')[0]
        self.assertEqual(' '.join(count.text_content().split()),
                         'Hiển thị 1–10 / 30 yêu cầu')

    def test_o_page_size_chi_hien_khi_vuot_option_nho_nhat(self):
        it = dict(path='/x', page_size_options=(10, 20, 50))
        # Biên 10 là chỗ phân biệt "> min" với ">= min" — bỏ biên là assert rỗng.
        for total in (9, 10):
            self.assertEqual(self._render(build_pager(total, 1, 10, **it)).xpath('.//select'),
                             [], 'total=%d không được hiện ô page-size' % total)
        self.assertEqual(
            len(self._render(build_pager(11, 1, 10, **it)).xpath('.//select')), 1)

    def test_mot_trang_ma_con_o_page_size_thi_an_o_mobile(self):
        """Chọn 50 còn 20 bản ghi: PC vẫn bấm về 10 được, mobile không để ô trống."""
        root = self._render(build_pager(20, 1, 50, path='/x',
                                        page_size_options=(10, 20, 50)))
        nav = root.xpath('.//nav')[0]
        self.assertIn('is-navless', nav.get('class'))
        self.assertEqual(nav.xpath('.//div[@class="wj-pagination__nav"]'), [])

    def test_o_page_size_mang_ten_param_cua_route(self):
        root = self._render(build_pager(30, 1, 10, path='/x', size_param='limit',
                                        page_size_options=(10, 20)))
        self.assertEqual(root.xpath('.//select')[0].get('name'), 'limit')


@tagged('post_install', '-at_install', 'wujia_pagination_e3')
class TestPaginationCallSites(TransactionCase):
    """Call site lượt E3a — không còn họ pager riêng, đi qua component."""

    MIGRATED = [
        ('wujia_portal_purchase_history', 'portal_history.xml', 2),
        ('wujia_portal_support', 'portal_support.xml', 2),
    ]
    LEGACY = ('wj-pc-pagination', 'wujia-mhist-pager', 'wujia-pagination',
              'wj-pc-page-btn')

    def test_call_site_di_qua_component(self):
        for module, filename, n in self.MIGRATED:
            root = _view(module, filename)
            calls = root.xpath('//t[@t-call="wujia_portal_layout.wj_pagination"]')
            self.assertEqual(len(calls), n, '%s: số call site pager đổi' % module)

    def test_khong_con_ho_pager_cu(self):
        for module, filename, _n in self.MIGRATED:
            raw = etree.tostring(_view(module, filename), encoding='unicode')
            for cls in self.LEGACY:
                self.assertNotIn(cls, raw, '%s còn họ cũ %s' % (module, cls))


@tagged('post_install', '-at_install', 'wujia_pagination_e3')
class TestPaginationTokens(TransactionCase):
    """Số BA đo được: 36 / radius 10 / gap 8 / chạm 44."""

    def test_token_dung_so_ba(self):
        css = _css('_variables.css')
        for token, value in (('--wj-pgn-size', '36px'), ('--wj-pgn-radius', '10px'),
                             ('--wj-pgn-gap', '8px'), ('--wj-pgn-touch', '44px'),
                             ('--wj-pgn-disabled-fg', '#9CA3AF')):
            self.assertRegex(css, re.escape(token) + r':\s*' + re.escape(value) + r';')

    def test_nut_dung_token_khong_go_so_cung(self):
        body = _css('_components.css').split('.wj-pagination__btn {')[1].split('}')[0]
        self.assertIn('height: var(--wj-pgn-size);', body)
        self.assertIn('min-width: var(--wj-pgn-size);', body)
        self.assertIn('border-radius: var(--wj-pgn-radius);', body)

    def test_vung_cham_44_khong_no_visual(self):
        """BA: chạm >=44 nhưng KHÔNG được tăng chiều cao danh sách."""
        css = _css('_components.css')
        before = css.split('.wj-pagination__btn::before {')[1].split('}')[0]
        self.assertIn('var(--wj-pgn-touch)', before)
        self.assertIn('position: absolute;', before)

    def test_content_card_khong_khoa_chieu_cao(self):
        """height:100% khoá card ⇒ bảng dài tràn ra đè lên pager (bắt được ở E3a)."""
        body = _css('_components.css').split('.wujia-content-card {')[1].split('}')[0]
        self.assertIn('min-height: 100%;', body)
        self.assertNotRegex(body, r'(?<!min-)height:\s*100%')
