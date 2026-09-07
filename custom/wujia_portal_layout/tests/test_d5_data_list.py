"""D5 — CMP-DL-001 DataList: hợp đồng render của `wj_data_list` + số BA của bảng.

Bám cột `Kết quả mong muốn` của issue UI-DATALIST-001 (STT 126) cho phần lượt D5b
phủ: cấu trúc DataViewport/DataItem/DataState/Pagination, `th[scope]` ở 3 call site
đầu, guard pager `page_count > 1`, và ba con số desktop 44 / 52 / `10px 16px`.
"""
import os
import re

from lxml import etree, html

from odoo.tests import TransactionCase, tagged

TMPL = 'wujia_portal_layout.wj_data_list'
HERE = os.path.dirname(__file__)
CSS_DIR = os.path.join(HERE, '..', 'static', 'assets', 'css')
CUSTOM = os.path.abspath(os.path.join(HERE, '..', '..'))


def _css(name):
    with open(os.path.join(CSS_DIR, name), encoding='utf-8') as fh:
        return fh.read()


def _strip_comments(css):
    return re.sub(r'/\*.*?\*/', '', css, flags=re.S)


def _rule(css, selector):
    """Thân của rule ở TẦNG GỐC (ngoài mọi @media) — bẫy D4a: gộp @media vào là
    đọc ra số của bản mobile."""
    css = _strip_comments(css)
    depth, i, out = 0, 0, None
    while i < len(css):
        c = css[i]
        if c == '{':
            depth += 1
        elif c == '}':
            depth -= 1
        elif depth == 0 and css.startswith(selector, i):
            after = css[i + len(selector)]
            if after in ' ,{\n':
                j = css.index('{', i)
                if css[i:j].strip() == selector:
                    out = css[j + 1:css.index('}', j)]
                    break
        i += 1
    return out


def _view(module, filename):
    """Đọc dạng BYTES: file view có khai báo encoding, lxml từ chối chuỗi unicode."""
    with open(os.path.join(CUSTOM, module, 'views', filename), 'rb') as fh:
        return etree.fromstring(fh.read())


@tagged('post_install', '-at_install', 'wujia_data_list_d5')
class TestDataListComponent(TransactionCase):

    def _render(self, values=None, slot=''):
        """Render QUA t-call như call site thật: Odoo 19 bỏ values['0'], slot chỉ
        tồn tại khi đi qua thân của t-call."""
        sets = ''.join(
            '<t t-set="%s" t-value="%r"/>' % (k, v) if not (isinstance(v, str) and v.startswith('<'))
            else '<t t-set="%s">%s</t>' % (k, v)
            for k, v in (values or {}).items())
        arch = ('<t t-name="wujia_portal_layout.wj_dl_probe">'
                '<t t-call="%s">%s%s</t></t>') % (TMPL, sets, slot)
        view = self.env['ir.ui.view'].create({
            'name': 'wj_dl_probe', 'type': 'qweb',
            'key': 'wujia_portal_layout.wj_dl_probe', 'arch_db': arch,
        })
        rendered = self.env['ir.qweb']._render(view.id)
        return html.fromstring(rendered)

    # ---------------------------------------------------------- cấu trúc
    def test_table_variant_dung_ba_tang(self):
        """DataList > DataViewport > table — thiếu tầng nào cũng đỏ."""
        root = self._render(slot='<thead><tr><th>A</th></tr></thead>')
        self.assertEqual(root.get('class').split()[0], 'wj-data-list')
        self.assertIn('wj-data-list--table', root.get('class'))
        viewports = root.xpath('./div[contains(@class, "wj-data-viewport")]')
        self.assertEqual(len(viewports), 1, 'phải có đúng một DataViewport')
        self.assertEqual([e.tag for e in viewports[0]], ['table'])
        self.assertIn('wj-data-table', viewports[0][0].get('class'))

    def test_lop_cu_cua_call_site_duoc_giu(self):
        """Lớp cũ đi qua dl_table_class/dl_class — CSS con và :is() hover không đứt."""
        root = self._render(
            {'dl_table_class': 'wujia-content-card-table', 'dl_class': 'legacy-wrapper'},
            slot='<tbody><tr><td>x</td></tr></tbody>')
        self.assertIn('legacy-wrapper', root.get('class'))
        table = root.xpath('.//table')[0]
        self.assertEqual(
            set(table.get('class').split()), {'wj-data-table', 'wujia-content-card-table'})

    def test_variant_khong_phai_bang_thi_khong_dung_table(self):
        for variant in ('compact-row', 'detail-card'):
            root = self._render({'dl_variant': variant}, slot='<a class="item">x</a>')
            self.assertIn('wj-data-list--%s' % variant, root.get('class'))
            self.assertFalse(root.xpath('.//table'), '%s không được bọc <table>' % variant)
            self.assertTrue(root.xpath('.//a[@class="item"]'))

    def test_variant_la_khong_biet_thi_ve_table(self):
        root = self._render({'dl_variant': 'bảng-lạ'}, slot='<tbody/>')
        self.assertIn('wj-data-list--table', root.get('class'))

    # ---------------------------------------------------------- DataState
    def test_datastate_thay_cho_viewport_khi_rong(self):
        root = self._render(
            {'dl_empty': True, 'dl_state': '<div class="wujia-empty-state">Chưa có dữ liệu</div>'},
            slot='<tbody><tr><td>không được render</td></tr></tbody>')
        self.assertFalse(root.xpath('.//table'), 'rỗng thì KHÔNG render viewport')
        self.assertEqual(len(root.xpath('.//div[@class="wujia-empty-state"]')), 1)

    def test_co_du_lieu_thi_khong_render_datastate(self):
        root = self._render(
            {'dl_empty': False, 'dl_state': '<div class="wujia-empty-state">x</div>'},
            slot='<tbody><tr><td>1</td></tr></tbody>')
        self.assertTrue(root.xpath('.//table'))
        self.assertFalse(root.xpath('.//div[@class="wujia-empty-state"]'))

    # ---------------------------------------------------------- Pagination
    def test_pager_nam_ngoai_viewport(self):
        root = self._render({'dl_pager': '<nav class="pager">1/2</nav>'},
                            slot='<tbody><tr><td>1</td></tr></tbody>')
        nav = root.xpath('.//nav[@class="pager"]')
        self.assertEqual(len(nav), 1)
        self.assertFalse(nav[0].xpath('ancestor::div[contains(@class,"wj-data-viewport")]'),
                         'Pagination phải NGOÀI DataViewport')

    def test_khong_truyen_pager_thi_khong_co_the_rong(self):
        root = self._render(slot='<tbody/>')
        self.assertFalse(root.xpath('.//nav'))

    # ---------------------------------------------------------- số BA
    def test_header_cao_44(self):
        body = _rule(_css('_components.css'), '.wj-data-table thead th')
        self.assertIsNotNone(body, 'không tìm thấy rule header ở tầng gốc')
        self.assertRegex(body, r'height:\s*44px')
        self.assertRegex(body, r'padding:\s*0 16px')

    def test_row_san_52(self):
        body = _rule(_css('_components.css'), '.wj-data-table tbody tr')
        self.assertIsNotNone(body)
        self.assertRegex(body, r'height:\s*52px')

    def test_cell_padding_10_16(self):
        body = _rule(_css('_components.css'), '.wj-data-table tbody td')
        self.assertIsNotNone(body)
        self.assertRegex(body, r'padding:\s*10px 16px')

    def test_mot_chu_so_huu_dang(self):
        """Bảng đã migrate KHÔNG được chạm rule cũ: mọi rule của lớp cũ phải mang
        `:not(.wj-data-table)`."""
        css = _strip_comments(_css('_components.css'))
        selectors = re.findall(r'([^{}]*\.wujia-content-card-table[^{}]*)\{', css)
        self.assertTrue(selectors)
        for sel in selectors:
            for part in sel.split(','):
                if '.wujia-content-card-table' in part:
                    self.assertIn(':not(.wj-data-table)', part,
                                  'rule cũ còn chạm bảng đã migrate: %s' % part.strip())


@tagged('post_install', '-at_install', 'wujia_data_list_d5')
class TestDataListCallSites(TransactionCase):
    """3 call site của lượt D5b — semantic + guard pager, đọc thẳng file view."""

    CALL_SITES = [
        ('wujia_portal_base', 'portal_home.xml', 4),
        ('wujia_portal_return', 'portal_return_list.xml', 7),
        ('wujia_portal_support', 'portal_support.xml', 8),
        # D5c — họ wj-pc-table
        ('wujia_portal_purchase_history', 'portal_history.xml', 7),
        ('wujia_portal_delivery', 'portal_delivery.xml', 8),
        ('wujia_portal_notification', 'portal_notification.xml', 5),
    ]

    def test_moi_th_deu_co_scope(self):
        for module, filename, n_cols in self.CALL_SITES:
            root = _view(module, filename)
            calls = root.xpath('//t[@t-call="wujia_portal_layout.wj_data_list"]')
            self.assertEqual(len(calls), 1, '%s: phải có đúng 1 DataList' % module)
            ths = calls[0].xpath('.//thead//th')
            self.assertEqual(len(ths), n_cols, '%s: số cột đổi' % module)
            khong_scope = [html.tostring(t, encoding='unicode')[:60]
                           for t in ths if t.get('scope') != 'col']
            self.assertEqual(khong_scope, [], '%s: th thiếu scope' % module)

    def test_pager_chi_hien_khi_nhieu_hon_mot_trang(self):
        for module, filename in [('wujia_portal_return', 'portal_return_list.xml'),
                                 ('wujia_portal_support', 'portal_support.xml')]:
            root = _view(module, filename)
            navs = root.xpath('//nav[.//ul[contains(@class, "wujia-pagination")]]')
            self.assertTrue(navs, '%s: không thấy khối pager' % module)
            for nav in navs:
                cond = nav.get('t-if') or ''
                self.assertIn('page_count', cond,
                              '%s: pager không guard theo page_count' % module)
                self.assertRegex(cond.replace(' ', ''), r'page_count[^)]*\)?>1',
                                 '%s: guard pager phải là > 1' % module)

    def test_home_preview_khong_gan_pagination(self):
        """BA: preview dashboard dùng "Xem tất cả" ở CardHeader, KHÔNG pager."""
        root = _view('wujia_portal_base', 'portal_home.xml')
        call = root.xpath('//t[@t-call="wujia_portal_layout.wj_data_list"]')[0]
        self.assertFalse(call.xpath('.//t[@t-set="dl_pager"]'))
        self.assertFalse(call.xpath('.//nav'))


@tagged('post_install', '-at_install', 'wujia_data_list_d5')
class TestDataListPcTable(TransactionCase):
    """D5c — họ bảng PC `wj-pc-table`: một chủ sở hữu dáng, guard pager, dáng mượn."""

    # Biến thể Ô, không phải hình học danh sách ⇒ cố ý vẫn chạm bảng đã migrate.
    ALLOWLIST = ('.wj-pc-td--code', '.wj-pc-td--muted', '.wj-pc-td--amount')

    def test_pc_mot_chu_so_huu_dang(self):
        css = _strip_comments(_css('_pc_components.css'))
        selectors = re.findall(r'([^{}]*\.wj-pc-table[^{}]*)\{', css)
        self.assertTrue(selectors)
        kiem = 0
        for sel in selectors:
            for part in sel.split(','):
                if '.wj-pc-table' not in part:
                    continue
                if any(x in part for x in self.ALLOWLIST):
                    continue
                kiem += 1
                self.assertIn(':not(.wj-data-table)', part,
                              'rule cũ còn chạm bảng đã migrate: %s' % part.strip())
        self.assertGreaterEqual(kiem, 9, 'quét hụt rule .wj-pc-table')

    def test_bang_khong_migrate_giu_nguyen_50_58(self):
        """Khoá sai tay là 12 bảng khác (exam/debt/inspection/báo cáo…) đổi dáng theo."""
        css = _css('_pc_components.css')
        self.assertRegex(_rule(css, '.wj-pc-table:not(.wj-data-table) thead th'),
                         r'height:\s*var\(--wj-pc-table-header-h\)')
        self.assertRegex(_rule(css, '.wj-pc-table:not(.wj-data-table) tbody td'),
                         r'height:\s*var\(--wj-pc-table-row-h\)')
        var = _rule(_css('_variables.css'), ':root')
        self.assertRegex(var, r'--wj-pc-table-header-h:\s*50px')
        self.assertRegex(var, r'--wj-pc-table-row-h:\s*58px')

    def test_pager_dieu_huong_guard_page_count(self):
        """BA: điều hướng trang chỉ khi >1 trang. Ô chọn số dòng/trang là khối khác
        (UI-PC-BASE-005) nên guard `> 10` của nó KHÔNG bị coi là vi phạm."""
        cases = [
            ('wujia_portal_purchase_history', 'portal_history.xml', '/portal/purchase-history'),
            ('wujia_portal_notification', 'portal_notification.xml', '/portal/notification'),
        ]
        for module, filename, route in cases:
            root = _view(module, filename)
            nav = root.xpath('//a[contains(@t-attf-class, "wj-pc-page-btn")]')
            self.assertTrue(nav, '%s: không thấy nút phân trang' % module)
            for a in nav:
                conds = [e.get('t-if') or '' for e in a.iterancestors() if e.get('t-if')]
                self.assertTrue(
                    any(re.search(r'page_count[^)]*\)?\s*>\s*1', c.replace('&gt;', '>'))
                        for c in conds),
                    '%s: nút phân trang không guard page_count > 1' % module)

    def test_pager_delivery_khong_hien_khi_mot_trang(self):
        root = _view('wujia_portal_delivery', 'portal_delivery.xml')
        blocks = root.xpath('//div[@class="wj-pc-pagination"]')
        self.assertTrue(blocks)
        for b in blocks:
            cond = (b.get('t-if') or '').replace('&gt;', '>').replace(' ', '')
            self.assertRegex(cond, r'page_count[^)]*\)?>1',
                             'delivery: pager vẫn hiện khi chỉ có 1 trang')

    def test_noti_giu_lop_va_id_cu(self):
        """`wj-pc-noti-row` KHÔNG có rule CSS nào — dáng đến hoàn toàn từ wj-pc-table,
        nên mất lớp hay mất id là mất dáng/điểm bám mà không test nào khác bắt được."""
        root = _view('wujia_portal_notification', 'portal_notification.xml')
        call = root.xpath('//t[@t-call="wujia_portal_layout.wj_data_list"]')[0]
        self.assertEqual(call.xpath('.//t[@t-set="dl_table_id"]')[0].get('t-value'),
                         "'wj-noti-table'")
        self.assertIn('wj-pc-noti-table',
                      call.xpath('.//t[@t-set="dl_table_class"]')[0].get('t-value'))
        # `contains()` là guard RỖNG ở đây: chuỗi con "wj-pc-noti-row" vẫn khớp qua
        # nhánh "wj-pc-noti-row--unread" bên trong #{...}. Phải neo vào token đứng đầu.
        rows = call.xpath('.//tbody//tr[@t-attf-class]')
        self.assertEqual(len(rows), 1)
        self.assertRegex(rows[0].get('t-attf-class'), r'^wj-pc-noti-row(\s|$)')

    def test_component_chuyen_duoc_id_bang(self):
        arch = ('<t t-name="wujia_portal_layout.wj_dl_id_probe">'
                '<t t-call="%s"><t t-set="dl_table_id" t-value="\'x-tbl\'"/>'
                '<tbody><tr><td>1</td></tr></tbody></t></t>') % TMPL
        view = self.env['ir.ui.view'].create({
            'name': 'wj_dl_id_probe', 'type': 'qweb',
            'key': 'wujia_portal_layout.wj_dl_id_probe', 'arch_db': arch,
        })
        root = html.fromstring(self.env['ir.qweb']._render(view.id))
        self.assertEqual(root.xpath('.//table')[0].get('id'), 'x-tbl')

    def test_hover_noti_khong_bi_zebra_nuot(self):
        """Zebra và hover cùng độ đặc hiệu (0,2,2) ⇒ row chẵn mất hover nếu không nâng."""
        path = os.path.join(CUSTOM, 'wujia_portal_notification', 'static', 'src', 'css',
                            'portal_notification.css')
        with open(path, encoding='utf-8') as fh:
            css = fh.read()
        body = _rule(css, '.wj-data-table.wj-pc-noti-table tbody tr:hover')
        self.assertIsNotNone(body, 'thiếu rule hover nâng độ đặc hiệu cho bảng noti')
        self.assertIn('rgba(40, 169, 223, 0.04)', body)

    def test_skeleton_delivery_khop_row_that(self):
        """Skeleton giả hàng bảng — lệch số là loading nhảy hình khi đổ dữ liệu."""
        path = os.path.join(CUSTOM, 'wujia_portal_delivery', 'static', 'src', 'css',
                            'portal_delivery.css')
        with open(path, encoding='utf-8') as fh:
            body = _rule(fh.read(), '.wj-pc-dlv-skel-row')
        self.assertIsNotNone(body)
        self.assertRegex(body, r'height:\s*52px')
        self.assertRegex(body, r'padding:\s*10px 16px')
