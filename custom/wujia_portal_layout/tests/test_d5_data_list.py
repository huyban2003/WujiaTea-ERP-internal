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


def _rule_in_media(css, selector):
    """Thân của rule nằm TRONG @media. `_rule()` cố ý chỉ đọc tầng gốc (bẫy D4a)
    nên gọi thẳng cho mknow/mnoti trả None ⇒ guard chứng-minh-rỗng (D5e)."""
    css = _strip_comments(css)
    depth, i, out = 0, 0, None
    while i < len(css):
        c = css[i]
        if c == '{':
            depth += 1
        elif c == '}':
            depth -= 1
        elif depth == 1 and css.startswith(selector, i):
            after = css[i + len(selector)]
            if after in ' ,{\n':
                j = css.index('{', i)
                if css[i:j].strip() == selector:
                    out = css[j + 1:css.index('}', j)]
                    break
        i += 1
    return out


def _chu_the(selector_part):
    """Compound CUỐI của một selector — phần thực sự bị style. Bỏ pseudo-element
    (::before) vì đó là con sinh ra, không phải chính hàng."""
    if '::' in selector_part:
        return ''
    return re.split(r'[ >+~]+', selector_part.strip())[-1]


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
            # D5d: portal_home.xml nay có 4 DataList (3 preview + bảng top SP) ⇒ chọn
            # theo cấu trúc chứ không theo số lượng.
            calls = root.xpath('//t[@t-call="wujia_portal_layout.wj_data_list"][.//thead]')
            self.assertEqual(len(calls), 1, '%s: phải có đúng 1 DataList dạng bảng' % module)
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
        """BA: preview dashboard dùng "Xem tất cả" ở CardHeader, KHÔNG pager.
        D5d: ghim cho CẢ BA khối preview, không chỉ khối top sản phẩm."""
        root = _view('wujia_portal_base', 'portal_home.xml')
        previews = root.xpath(
            '//t[@t-call="wujia_portal_layout.wj_data_list"][not(.//thead)]'
            '[.//ul[@class="wujia-content-card-body"]]')
        self.assertEqual(len(previews), 3, 'phải đủ 3 khối preview dashboard')
        for call in previews:
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


@tagged('post_install', '-at_install', 'wujia_data_list_d5')
class TestDataListCompactRow(TransactionCase):
    """D5d — danh sách PC không phải bảng (`li.wujia-content-card-row`): variant
    compact-row, một chủ sở hữu dáng, và call site đầu tiên dùng `dl_pager`."""

    COMPACT_SITES = [
        ('wujia_portal_base', 'portal_home.xml', 3),
        ('wujia_portal_knowledge', 'portal_knowledge.xml', 1),
    ]

    def _compact_calls(self, module, filename):
        root = _view(module, filename)
        # D5e: mobile cũng dùng compact-row ⇒ neo vào container PC thật, không
        # chỉ vào variant (nếu không phép chọn vớ luôn 6 call site mobile).
        return root.xpath(
            '//t[@t-call="wujia_portal_layout.wj_data_list"]'
            '[t[@t-set="dl_variant"][@t-value="\'compact-row\'"]]'
            '[.//ul[@class="wujia-content-card-body"]]')

    def test_bon_call_site_dung_variant_compact_row(self):
        for module, filename, n in self.COMPACT_SITES:
            calls = self._compact_calls(module, filename)
            self.assertEqual(len(calls), n, '%s: số call site compact-row đổi' % module)
            for call in calls:
                self.assertTrue(call.xpath('.//ul[@class="wujia-content-card-body"]'),
                                '%s: mất container danh sách' % module)

    def test_item_mang_ca_hai_lop(self):
        """Neo vào TOKEN, không `contains()` — bẫy D5c #3 (tên lớp có biến thể BEM)."""
        for module, filename, n in self.COMPACT_SITES:
            for call in self._compact_calls(module, filename):
                ul = './/ul[@class="wujia-content-card-body"]'
                lis = call.xpath(ul + '/li') + call.xpath(ul + '/t/li')
                self.assertEqual(len(lis), 1, '%s: mỗi danh sách đúng 1 item mẫu' % module)
                tokens = (lis[0].get('class') or '').split()
                self.assertIn('wj-data-item', tokens, '%s: item thiếu wj-data-item' % module)
                self.assertIn('wujia-content-card-row', tokens,
                              '%s: item mất lớp cũ (CSS con bullet/content/date đứt)' % module)

    def test_mot_chu_so_huu_dang_compact_row(self):
        """Mọi rule chạm CHÍNH lớp `.wujia-content-card-row` — kể cả trong @media —
        phải mang `:not(.wj-data-item)`. Regex loại tên con BEM bằng ranh giới ký tự."""
        css = _strip_comments(_css('_components.css'))
        selectors = re.findall(r'([^{}]*\.wujia-content-card-row(?![-\w])[^{}]*)\{', css)
        self.assertTrue(selectors, 'không còn rule nào của lớp cũ — sai phép đo')
        for sel in selectors:
            for part in sel.split(','):
                # D5e: rule layout MỚI của chính item đã migrate mang `.wj-data-item`
                # ngoài `:not()` — đó không phải rule cũ.
                if '.wj-data-item' in re.sub(r':not\([^)]*\)', '', part):
                    continue
                if re.search(r'\.wujia-content-card-row(?![-\w])', part):
                    self.assertIn(':not(.wj-data-item)', part,
                                  'rule cũ còn chạm item đã migrate: %s' % part.strip())

    def test_so_ba_cua_compact_row(self):
        body = _rule(_css('_components.css'), '.wj-data-list--compact-row .wj-data-item')
        self.assertIsNotNone(body, 'không tìm thấy rule item ở tầng gốc')
        self.assertRegex(body, r'min-height:\s*64px')       # BA 64–76
        self.assertRegex(body, r'padding:\s*12px 14px')     # BA 10–12px 12–14px
        self.assertRegex(body, r'border-radius:\s*12px')    # BA 12
        gap = _rule(_css('_components.css'),
                    '.wj-data-list--compact-row .wj-data-item + .wj-data-item')
        self.assertIsNotNone(gap, 'thiếu rule gap giữa hai item')
        self.assertRegex(gap, r'margin-top:\s*8px')         # BA gap 8

    def test_knowledge_pager_di_qua_dl_pager(self):
        """Pager vào TRONG DataList (sơ đồ BA), guard `page_count > 1` giữ nguyên,
        và khối PC không còn nav nào nằm ngoài."""
        root = _view('wujia_portal_knowledge', 'portal_knowledge.xml')
        call = self._compact_calls('wujia_portal_knowledge', 'portal_knowledge.xml')[0]
        navs = call.xpath('./t[@t-set="dl_pager"]//nav')
        self.assertEqual(len(navs), 1, 'pager phải nằm trong dl_pager')
        cond = (navs[0].get('t-if') or '').replace(' ', '')
        self.assertRegex(cond, r'page_count[^)]*\)?>1', 'guard pager phải là > 1')
        pc = root.xpath('//div[@id="wj-know-pc-body"]')[0]
        ngoai = [n for n in pc.xpath('.//nav')
                 if not n.xpath('ancestor::t[@t-set="dl_pager"]')]
        self.assertEqual(ngoai, [], 'còn pager cũ nằm ngoài DataList')

    def test_dl_pager_render_duoc_khoi_co_t_foreach(self):
        """Call site đầu tiên dùng dl_pager: chứng minh markup có `t-foreach` đi qua
        `t-set` ra đủ nút, không rơi vào họ bẫy D5b #1 (Odoo 19 bỏ values['0'])."""
        arch = ('<t t-name="wujia_portal_layout.wj_dl_pager_probe">'
                '<t t-call="wujia_portal_layout.wj_data_list">'
                '<t t-set="dl_variant" t-value="\'compact-row\'"/>'
                '<t t-set="dl_pager">'
                '<nav class="pager"><t t-foreach="range(1, 4)" t-as="pn">'
                '<a class="page-link" t-out="pn"/></t></nav>'
                '</t>'
                '<ul><li class="wj-data-item">x</li></ul>'
                '</t></t>')
        view = self.env['ir.ui.view'].create({
            'name': 'wj_dl_pager_probe', 'type': 'qweb',
            'key': 'wujia_portal_layout.wj_dl_pager_probe', 'arch_db': arch,
        })
        root = html.fromstring(self.env['ir.qweb']._render(view.id))
        links = root.xpath('.//nav[@class="pager"]/a')
        self.assertEqual([a.text for a in links], ['1', '2', '3'])
        self.assertFalse(root.xpath('.//nav[@class="pager"]'
                                    '/ancestor::div[contains(@class,"wj-data-viewport")]'),
                         'Pagination phải NGOÀI DataViewport')


@tagged('post_install', '-at_install', 'wujia_data_list_d5')
class TestDataListCompactRowMobile(TransactionCase):
    """D5e — 9 call site mobile (mdash ×6 · mhist · mnoti · mknow): một chủ sở hữu
    dáng cho CẢ BỐN họ, layout riêng từng họ, và bộ số BA của compact-row."""

    MOBILE_SITES = [
        ('wujia_portal_base', 'portal_home.xml', 5),
        ('wujia_portal_support', 'portal_support.xml', 1),
        ('wujia_portal_purchase_history', 'portal_history.xml', 1),
        ('wujia_portal_notification', 'portal_notification.xml', 1),
        ('wujia_portal_knowledge', 'portal_knowledge.xml', 1),
    ]
    HO = ('wujia-mdash-row', 'wujia-mhist-row', 'wujia-mnoti-row', 'wujia-mknow-row')

    def _mobile_calls(self, module, filename):
        """Call site compact-row KHÔNG phải của D5d (D5d dùng ul.wujia-content-card-body)."""
        root = _view(module, filename)
        return root.xpath(
            '//t[@t-call="wujia_portal_layout.wj_data_list"]'
            '[t[@t-set="dl_variant"][@t-value="\'compact-row\'"]]'
            '[not(.//ul[@class="wujia-content-card-body"])]')

    def _items(self, call):
        out = []
        for el in call.iter():
            cls = el.get('class') or el.get('t-attf-class') or ''
            if any(re.match(r'%s(\s|$)' % h, cls) for h in self.HO):
                out.append((el, cls))
        return out

    def test_chin_call_site_mobile(self):
        tong = 0
        for module, filename, n in self.MOBILE_SITES:
            calls = self._mobile_calls(module, filename)
            self.assertEqual(len(calls), n, '%s: số call site mobile đổi' % module)
            tong += len(calls)
        self.assertEqual(tong, 9, 'D5e phủ đúng 9 call site')

    def test_item_mang_ca_hai_lop(self):
        """Neo TOKEN ĐỨNG ĐẦU — `contains()` khớp cả tên con BEM (bẫy D5c #3)."""
        for module, filename, _n in self.MOBILE_SITES:
            for call in self._mobile_calls(module, filename):
                items = self._items(call)
                self.assertEqual(len(items), 1,
                                 '%s: mỗi danh sách đúng 1 item mẫu' % module)
                self.assertIn('wj-data-item', items[0][1].split(),
                              '%s: item thiếu wj-data-item' % module)

    def test_is_stacked_con_du_ba_cho(self):
        """3/6 khối mdash là biến thể nhiều dòng phụ — mất modifier là icon/badge
        tụt về giữa khối mà không số đo nào đỏ."""
        stacked = [cls for call in self._mobile_calls('wujia_portal_base', 'portal_home.xml')
                   for _el, cls in self._items(call) if 'is-stacked' in cls.split()]
        self.assertEqual(len(stacked), 3, 'số khối is-stacked đổi')

    def test_muoi_hang_mdash_khong_phai_danh_sach_giu_nguyen(self):
        """`wujia-mdash-row` còn 10 chỗ KHÔNG phải danh sách record (lối tắt Home,
        hàng thông tin tĩnh Home/support) — đụng vào là đổi dáng 10 chỗ ngoài phạm vi."""
        con_lai = 0
        for module, filename in (('wujia_portal_base', 'portal_home.xml'),
                                 ('wujia_portal_support', 'portal_support.xml')):
            root = _view(module, filename)
            for el in root.iter():
                cls = el.get('class') or el.get('t-attf-class') or ''
                if re.match(r'wujia-mdash-row(\s|$)', cls) and 'wj-data-item' not in cls.split():
                    con_lai += 1
        self.assertEqual(con_lai, 10, 'số hàng mdash ngoài phạm vi đổi')

    def test_mot_chu_so_huu_dang_bon_ho(self):
        """Rule cũ chỉ được chạm hàng CHƯA migrate. Xét compound CUỐI của mỗi
        selector (rule của lớp con và ::before là biến thể ô, cố ý giữ)."""
        for filename, ho in ((os.path.join(CSS_DIR, '_components.css'),
                              ('wujia-mdash-row', 'wujia-mhist-row', 'wujia-mknow-row')),
                             (os.path.join(CUSTOM, 'wujia_portal_notification', 'static', 'src',
                                           'css', 'portal_notification.css'),
                              ('wujia-mnoti-row',))):
            with open(filename, encoding='utf-8') as fh:
                css = _strip_comments(fh.read())
            for lop in ho:
                pat = re.compile(r'\.%s(?![-\w])' % lop)
                selectors = re.findall(r'([^{}]*\.%s(?![-\w])[^{}]*)\{' % lop, css)
                self.assertTrue(selectors, 'không còn rule nào của %s — sai phép đo' % lop)
                kiem = 0
                for sel in selectors:
                    for part in sel.split(','):
                        if not pat.search(_chu_the(part)):
                            continue
                        # `:not(.wj-data-item)` cũng chứa chuỗi `.wj-data-item` ⇒ phải
                        # bóc `:not()` trước, nếu không guard tự chứng minh rỗng.
                        if '.wj-data-item' in re.sub(r':not\([^)]*\)', '', part):
                            continue
                        kiem += 1
                        self.assertIn(':not(.wj-data-item)', part,
                                      'rule cũ còn chạm item đã migrate: %s' % part.strip())
                self.assertGreaterEqual(kiem, 1, 'quét hụt rule của %s' % lop)

    def test_layout_tung_ho_tach_khoi_dang(self):
        """Dáng dùng chung ở .wj-data-item; layout (flex/grid) ở từng họ — gộp lại
        là ép lưới 4 cột của PC lên hàng mobile, vỡ cả 9 chỗ."""
        css = _css('_components.css')
        dang = _rule(css, '.wj-data-list--compact-row .wj-data-item')
        self.assertIsNotNone(dang)
        self.assertNotIn('display: grid', dang, 'dáng chung không được mang layout')
        self.assertNotIn('grid-template-columns', dang)
        for sel in ('.wj-data-list--compact-row .wujia-mdash-row.wj-data-item',
                    '.wj-data-list--compact-row .wujia-mhist-row.wj-data-item'):
            body = _rule(css, sel)
            self.assertIsNotNone(body, 'thiếu rule layout: %s' % sel)
            self.assertRegex(body, r'display:\s*flex')
        pc = _rule(css, '.wj-data-list--compact-row .wujia-content-card-row.wj-data-item')
        self.assertIsNotNone(pc, 'D5d mất rule layout lưới 4 cột')
        self.assertRegex(pc, r'grid-template-columns:\s*auto 1fr auto auto')

    def test_layout_hai_ho_nam_trong_media(self):
        """mknow và mnoti khai trong @media ⇒ phải đọc bằng _rule_in_media, gọi
        _rule sẽ trả None và assert thành guard chứng-minh-rỗng."""
        css = _css('_components.css')
        sel = '.wj-data-list--compact-row .wujia-mknow-row.wj-data-item'
        self.assertIsNone(_rule(css, sel), 'rule mknow không còn trong @media?')
        body = _rule_in_media(css, sel)
        self.assertIsNotNone(body, 'thiếu rule layout mknow trong @media')
        self.assertRegex(body, r'align-items:\s*flex-start')
        with open(os.path.join(CUSTOM, 'wujia_portal_notification', 'static', 'src', 'css',
                               'portal_notification.css'), encoding='utf-8') as fh:
            noti = fh.read()
        body = _rule_in_media(noti, '.wj-data-list--compact-row .wujia-mnoti-row.wj-data-item')
        self.assertIsNotNone(body, 'thiếu rule layout mnoti trong @media')
        # Thanh accent is-unread rộng 4px nằm sát mép trái: về 14 là chữ đè lên nó.
        self.assertRegex(body, r'padding-left:\s*16px')
        self.assertRegex(body, r'position:\s*relative')

    def test_thanh_accent_chua_doc_van_song(self):
        """::before của .is-unread là con sinh ra, cố ý KHÔNG khoá :not() — khoá
        nhầm là mất dấu 'chưa đọc' mà không số đo nào bắt."""
        with open(os.path.join(CUSTOM, 'wujia_portal_notification', 'static', 'src', 'css',
                               'portal_notification.css'), encoding='utf-8') as fh:
            css = _strip_comments(fh.read())
        self.assertIn('.wujia-mnoti-row.is-unread::before', css)
        self.assertNotIn('.wujia-mnoti-row.is-unread:not(.wj-data-item)::before', css)


@tagged('post_install', '-at_install', 'wujia_data_list_d5')
class TestDataListDetailCard(TransactionCase):
    """D5f — variant `detail-card`: 2 call site record (`mreturn` · `mdelivery`)
    + khối skeleton dùng chung dáng nhưng KHÔNG phải record."""

    SITES = [
        ('wujia_portal_return', 'portal_return_list.xml', 'wujia-mreturn-row'),
        ('wujia_portal_delivery', 'portal_delivery.xml', 'wujia-mdelivery-row'),
    ]
    CSS_HO = {
        'wujia-mreturn-row': ('wujia_portal_return', 'portal_return.css'),
        'wujia-mdelivery-row': ('wujia_portal_delivery', 'portal_delivery.css'),
    }

    def _calls(self, module, filename):
        root = _view(module, filename)
        return root.xpath(
            '//t[@t-call="wujia_portal_layout.wj_data_list"]'
            '[t[@t-set="dl_variant"][@t-value="\'detail-card\'"]]')

    def _items(self, call, ho):
        out = []
        for el in call.iter():
            cls = el.get('class') or el.get('t-attf-class') or ''
            if re.match(r'%s(\s|$)' % ho, cls):
                out.append(cls)
        return out

    def _la_skeleton(self, call):
        return bool(call.xpath('.//*[contains(@class, "wujia-mdelivery-skel")]'))

    def _css_ho(self, ho):
        module, filename = self.CSS_HO[ho]
        with open(os.path.join(CUSTOM, module, 'static', 'src', 'css', filename),
                  encoding='utf-8') as fh:
            return fh.read()

    def test_hai_call_site_record(self):
        """2 call site RECORD. Khối skeleton cũng đi qua component nhưng không
        phải record ⇒ đếm phải loại nó ra, nếu không inventory sai."""
        record = 0
        for module, filename, _ho in self.SITES:
            calls = self._calls(module, filename)
            self.assertTrue(calls, '%s: mất call site detail-card' % module)
            record += len([c for c in calls if not self._la_skeleton(c)])
        self.assertEqual(record, 2, 'số call site record của D5f đổi')

    def test_item_mang_ca_hai_lop(self):
        """Chỉ xét call site RECORD — skeleton là việc của test riêng, để mỗi
        phép mutation làm đỏ đúng một test."""
        for module, filename, ho in self.SITES:
            for call in self._calls(module, filename):
                if self._la_skeleton(call):
                    continue
                items = self._items(call, ho)
                self.assertEqual(len(items), 1, '%s: mỗi danh sách đúng 1 item mẫu' % module)
                self.assertIn('wj-data-item', items[0].split(),
                              '%s: item thiếu wj-data-item' % module)

    def test_so_ba_cua_detail_card(self):
        body = _rule(_css('_components.css'), '.wj-data-list--detail-card .wj-data-item')
        self.assertIsNotNone(body, 'không tìm thấy rule dáng detail-card ở tầng gốc')
        self.assertRegex(body, r'min-height:\s*96px')       # BA 96–120
        self.assertRegex(body, r'padding:\s*12px 14px')
        self.assertRegex(body, r'border-radius:\s*12px')    # BA 12
        gap = _rule(_css('_components.css'),
                    '.wj-data-list--detail-card .wj-data-item + .wj-data-item')
        self.assertIsNotNone(gap, 'thiếu rule gap giữa hai item')
        self.assertRegex(gap, r'margin-top:\s*8px')         # BA gap 8

    def test_mot_chu_so_huu_dang_hai_ho(self):
        """Rule cũ chỉ được chạm hàng CHƯA migrate. Miễn trừ theo TÍNH CHẤT chứ
        không theo tên: rule chỉ khai `color` không phải rule dáng."""
        for ho in self.CSS_HO:
            css = _strip_comments(self._css_ho(ho))
            pat = re.compile(r'\.%s(?![-\w])' % ho)
            rules = re.findall(r'([^{}]*\.%s(?![-\w])[^{}]*)\{([^{}]*)\}' % ho, css)
            self.assertTrue(rules, 'không còn rule nào của %s — sai phép đo' % ho)
            kiem = 0
            for sel, body in rules:
                khai = {d.split(':')[0].strip() for d in body.split(';') if ':' in d}
                if khai and khai <= {'color'}:
                    continue
                for part in sel.split(','):
                    if not pat.search(_chu_the(part)):
                        continue
                    # `:not(.wj-data-item)` cũng chứa chuỗi `.wj-data-item` (bẫy D5e #2).
                    if '.wj-data-item' in re.sub(r':not\([^)]*\)', '', part):
                        continue
                    kiem += 1
                    self.assertIn(':not(.wj-data-item)', part,
                                  'rule cũ còn chạm item đã migrate: %s' % part.strip())
            self.assertGreaterEqual(kiem, 1, 'quét hụt rule của %s' % ho)

    def test_layout_hai_ho_nam_trong_media(self):
        """Cả hai rule layout khai TRONG @media ⇒ `_rule()` (chỉ đọc tầng gốc) trả
        None và guard tự chứng minh rỗng."""
        for ho in self.CSS_HO:
            sel = '.wj-data-list--detail-card .%s.wj-data-item' % ho
            css = self._css_ho(ho)
            self.assertIsNone(_rule(css, sel), '%s: rule layout phải ở trong @media' % ho)
            body = _rule_in_media(css, sel)
            self.assertIsNotNone(body, '%s: thiếu rule layout trong @media' % ho)
            self.assertRegex(body, r'display:\s*flex')
            # Dáng là việc của .wj-data-item — layout không được giành lại.
            for cam in ('padding', 'border-radius', 'background'):
                self.assertNotRegex(body, r'\b%s\s*:' % cam,
                                    '%s: layout giành lại dáng (%s)' % (ho, cam))

    def test_skeleton_cung_dang_nhung_khong_phai_record(self):
        """Skeleton là placeholder của CHÍNH hàng đó ⇒ phải mang `wj-data-item` để
        không lệch dáng lúc đang tải; nhưng nó không phải bản ghi."""
        calls = self._calls('wujia_portal_delivery', 'portal_delivery.xml')
        skel = [c for c in calls if self._la_skeleton(c)]
        self.assertEqual(len(skel), 1, 'khối skeleton phải đi qua DataList')
        self.assertTrue(skel[0].xpath('.//t[@t-foreach="[1, 2, 3]"]'),
                        'skeleton không còn là 3 hàng giả')
        cls = skel[0].xpath('.//div[contains(@class, "wujia-mdelivery-skel")]')[0].get('class')
        self.assertIn('wj-data-item', cls.split(), 'skeleton lệch dáng với hàng thật')

    def test_pager_hai_cho_giu_guard_page_count(self):
        """Pager cố ý ở NGOÀI DataList lượt này (dồn về lượt dọn Pagination) —
        nhưng guard `page_count > 1` phải còn nguyên."""
        for module, filename, _ho in self.SITES:
            root = _view(module, filename)
            navs = [n for n in root.xpath('//nav[@class="wujia-mhist-pager"]')]
            self.assertTrue(navs, '%s: mất pager mobile' % module)
            for nav in navs:
                cond = (nav.get('t-if') or '').replace(' ', '')
                self.assertRegex(cond, r'page_count[^)]*\)?>1',
                                 '%s: guard pager phải là > 1' % module)

    def test_radius_khong_dung_token_chung(self):
        """`--wujia-morder-radius` còn dùng ở 3 chỗ khác; đè radius tại rule
        detail-card, KHÔNG sửa token."""
        token = _rule(_css('_variables.css'), ':root')
        self.assertRegex(token, r'--wujia-morder-radius:\s*14px')
        body = _rule(_css('_components.css'), '.wj-data-list--detail-card .wj-data-item')
        self.assertNotIn('--wujia-morder-radius', body)
