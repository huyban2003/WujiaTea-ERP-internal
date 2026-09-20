"""E6 (quét nhiều module) — call site Button CMP-BTN-001 (`UI-BUTTON-001`).

Khung `wujia_portal_layout` giữ hợp đồng atom (luật F5b); ở đây là sổ "màn nào đã
về atom" cộng bốn luật không màn nào được phá:

  · đủ số call site — đếm >= (bài học E5b2 #2: "có ít nhất một" xanh giả khi màn
    nhiều nút mà rơi mất lớp ở một chỗ);
  · họ class cũ của màn đã migrate biến mất khỏi CẢ view lẫn CSS module;
  · module không tự khai lại `.wj-btn*`/`.wj-iconbtn*` dáng — một implementation;
  · icon-only phải có tên đọc được ngay tại call site.

E6b/E6c thêm màn chỉ bằng cách thêm một dòng vào MIGRATED.
"""
import os
import re

from odoo.tests import TransactionCase, tagged

from odoo.addons.wujia_portal_base.tests.css_probe import (
    CUSTOM, _css, _mod_css, _strip_comments, _view,
)

# (module, file view, số call site .wj-btn, số .wj-iconbtn, họ cũ phải biến mất,
#  file CSS module)
MIGRATED = [
    ('wujia_portal_support', 'portal_support.xml', 7, 1,
     ('wj-pc-btn', 'wj-pc-btn--primary', 'wj-pc-btn--secondary', 'btn-primary',
      'btn-secondary', 'btn-sm', 'wj-empty-state-btn'), 'portal_support.css'),
    ('wujia_portal_return', 'portal_return_list.xml', 2, 1,
     ('btn-outline-primary', 'btn-sm', 'wj-empty-state-btn'), 'portal_return.css'),
    ('wujia_portal_return', 'portal_return_form.xml', 5, 0,
     ('wujia-mreturn-btn-cancel', 'wujia-mreturn-btn-submit', 'wj-pc-btn',
      'wj-pc-btn--primary', 'wj-pc-btn--secondary'), 'portal_return.css'),
    ('wujia_portal_notification', 'portal_notification.xml', 4, 0,
     ('wj-pc-btn', 'wj-pc-btn--primary', 'btn-primary', 'btn-sm',
      'wj-empty-state-btn'), 'portal_notification.css'),
    ('wujia_portal_notification', 'header_bell_inherit.xml', 1, 0,
     ('btn-primary', 'btn-sm'), 'portal_notification.css'),
    # --- E6b1 ---
    ('wujia_portal_delivery', 'portal_delivery.xml', 6, 0,
     ('wj-pc-btn', 'wj-pc-btn--primary', 'wj-pc-btn--secondary',
      'wj-pc-dlv-btn-xem', 'wj-empty-state-btn'), 'portal_delivery.css'),
    ('wujia_portal_knowledge', 'portal_knowledge.xml', 3, 0,
     ('btn-secondary', 'wj-empty-state-btn'), 'portal_knowledge.css'),
    ('wujia_portal_info_request', 'portal_info_request_form.xml', 3, 0,
     ('btn-primary', 'btn-secondary', 'btn-outline-primary'), None),
    ('wujia_portal_info_request', 'portal_info_request_list.xml', 0, 1,
     ('btn-sm', 'btn-outline-primary'), None),
    ('wujia_portal_info_request', 'portal_info_request_detail.xml', 1, 0,
     ('btn-outline-danger',), None),
    ('wujia_portal_purchase_history', 'portal_history.xml', 2, 0,
     ('wj-empty-state-btn',), 'portal_history.css'),
    ('wujia_portal_base', 'store_picker_modal.xml', 2, 1,
     ('btn-outline-secondary', 'wj-cta-btn'), 'store_picker.css'),
    ('wujia_portal_base', 'portal_franchises_in_layout.xml', 1, 0,
     ('btn-sm', 'wj-cta-btn'), 'portal_dashboard.css'),
    ('wujia_portal_base', 'portal_franchise_profile.xml', 1, 0,
     ('btn-outline-primary',), 'portal_dashboard.css'),
    # Công nợ: 10 call site về atom. `wj-pc-btn` KHÔNG nằm trong danh sách họ cũ —
    # 3 nút của thanh lọc còn giữ họ đó theo FB-08, và `wj-debt-cta`/`-copy`/
    # `-pc-copy`/`-pc-modal__close` ở lại làm hook bố cục (dáng đã gỡ khỏi CSS).
    ('wujia_portal_debt', 'portal_debt.xml', 5, 5,
     ('wj-debt-pc-pdf',), 'portal_debt.css'),
]

VARIANT = ('primary', 'secondary', 'outline', 'danger', 'ghost')
SIZE = ('sm', 'lg', 'block')


def _atoms(root, base):
    """Phần tử mang ĐÚNG token lớp gốc — `contains()` sẽ khớp cả `wj-btn--primary`
    lẫn `wj-iconbtn` (bẫy tên con BEM đã dính ở D4e/D5c)."""
    out = []
    for el in root.iter():
        cls = ((el.get('class') or '') + ' ' + (el.get('t-attf-class') or '')).split()
        if base in cls:
            out.append((el, cls))
    return out


@tagged('post_install', '-at_install', 'wujia_button_e6')
class TestButtonCallSites(TransactionCase):

    def test_du_so_call_site(self):
        for module, filename, n_btn, n_icon, _cu, _css in MIGRATED:
            root = _view(module, filename)
            self.assertGreaterEqual(
                len(_atoms(root, 'wj-btn')), n_btn,
                '%s/%s: thiếu call site wj-btn' % (module, filename))
            self.assertGreaterEqual(
                len(_atoms(root, 'wj-iconbtn')), n_icon,
                '%s/%s: thiếu call site wj-iconbtn' % (module, filename))

    def test_moi_atom_mang_dung_mot_variant(self):
        """Không variant ⇒ nút trong suốt không viền; hai variant ⇒ cái sau đè."""
        for module, filename, _nb, _ni, _cu, _css in MIGRATED:
            root = _view(module, filename)
            for base in ('wj-btn', 'wj-iconbtn'):
                for _el, cls in _atoms(root, base):
                    co = [v for v in VARIANT if '%s--%s' % (base, v) in cls]
                    self.assertEqual(len(co), 1,
                                     '%s/%s: %s mang %d variant (%s)'
                                     % (module, filename, base, len(co), ' '.join(cls)))

    def test_icon_only_co_ten_doc_duoc(self):
        """BT-6: 40 link icon-only của PC trước E6 không có tên đọc được nào —
        migrate xong thì cấm tái phạm ngay tại call site."""
        for module, filename, _nb, _ni, _cu, _css in MIGRATED:
            for el, cls in _atoms(_view(module, filename), 'wj-iconbtn'):
                ten = (el.get('aria-label') or el.get('t-att-aria-label')
                       or el.get('t-attf-aria-label') or '')
                self.assertTrue(ten.strip(),
                                '%s/%s: icon button thiếu aria-label (%s)'
                                % (module, filename, ' '.join(cls)))

    def test_khong_con_ho_class_cu(self):
        """Hai bộ dáng cùng sống là nguồn hồi quy specificity đã trả giá ở D3/D4."""
        for module, filename, _nb, _ni, cu, css_file in MIGRATED:
            with open(os.path.join(CUSTOM, module, 'views', filename), encoding='utf-8') as fh:
                view = fh.read()
            css = _strip_comments(_mod_css(module, css_file)) if css_file else ''
            for ho in cu:
                self.assertNotRegex(view, r'%s(?![-\w])' % re.escape(ho),
                                    '%s/%s: họ cũ %s còn trong view' % (module, filename, ho))
                self.assertNotRegex(css, r'\.%s(?![-\w])' % re.escape(ho),
                                    '%s: họ cũ %s còn rule CSS' % (module, ho))

    def test_module_khong_khai_lai_dang_cua_atom(self):
        """BT-11 một implementation: module chỉ được khai BỐ CỤC (flex/margin/
        width trong ngữ cảnh của mình), cấm giành dáng (cao/bo/nền/viền/chữ)."""
        cam = ('height', 'border-radius', 'background', 'border', 'font-size',
               'font-weight', 'padding', 'color')
        thay = []
        for root, _dirs, files in os.walk(CUSTOM):
            if '/static/' not in root or not root.endswith('css'):
                continue
            if os.sep + 'wujia_portal_layout' + os.sep in root:
                continue
            for fn in files:
                if not fn.endswith('.css'):
                    continue
                css = _strip_comments(open(os.path.join(root, fn), encoding='utf-8').read())
                for sel, body in re.findall(r'([^{}]+)\{([^{}]*)\}', css):
                    if not re.search(r'\.wj-(icon)?btn(?![-\w])|\.wj-(icon)?btn--', sel):
                        continue
                    khai = {d.split(':')[0].strip() for d in body.split(';') if ':' in d}
                    xau = sorted(k for k in khai if any(k == c or k.startswith(c + '-')
                                                        for c in cam))
                    if xau:
                        thay.append('%s: %s { %s }' % (fn, sel.strip(), ', '.join(xau)))
        self.assertFalse(thay, 'module giành dáng của atom:\n' + '\n'.join(thay))

    def test_ho_cu_cua_khao_sat_khong_bi_dung(self):
        """LIMIT E6: `wujia_portal_inspection` (code anh Thái) còn dùng `.wj-pc-btn`
        ở 3 template + 1 JS ⇒ E6 thu hẹp, KHÔNG xoá."""
        con = []
        for root, _dirs, files in os.walk(os.path.join(CUSTOM, 'wujia_portal_inspection')):
            for fn in files:
                if fn.endswith(('.xml', '.js')):
                    txt = open(os.path.join(root, fn), encoding='utf-8').read()
                    if re.search(r'wj-pc-btn(?![-\w])', txt):
                        con.append(fn)
        self.assertTrue(con, 'Khảo sát hết dùng .wj-pc-btn ⇒ gỡ LIMIT và xoá họ cũ')


# Thanh lọc mà E4 đã đo và ký duyệt (`docs/e4-filter-inventory.md`): nút bên trong
# giữ chiều cao của Filter (FB-08) chứ KHÔNG về bậc size của CMP-BTN-001. Ba màn
# đầu tự dựng thanh lọc, phần còn lại gọi component `wj_filter_bar`.
FILTER_FORMS = (
    ('wujia_portal_debt', 'portal_debt.xml', 'wj-debt-filter'),
    ('wujia_portal_debt', 'portal_debt.xml', 'wj-debt-pc-filter'),
    ('wujia_portal_sale', 'portal_order_catalog.xml', 'wujia-morder-search'),
)


@tagged('post_install', '-at_install', 'wujia_button_e6')
class TestRanhGioiThanhLoc(TransactionCase):
    """Cùng một tên class `wj-pc-btn--primary` trong `portal_debt.xml` vừa là nút
    *Tìm kiếm* của thanh lọc (giữ 42) vừa là nút *Thanh toán số còn lại* (về 40).
    Tên class không phân biệt được hai vai trò ⇒ luật phải đọc theo NGỮ CẢNH, và
    phải canh cả hai chiều để không lượt nào kéo nhầm nút của cụm kia."""

    def _trong_thanh_loc(self, module, filename, moc):
        root = _view(module, filename)
        for node in root.iter():
            cls = (node.get('class') or '').split()
            if moc in cls:
                yield node

    def test_nut_thanh_loc_khong_bi_keo_ve_atom(self):
        """Chiều A — E6 không được migrate nút nằm trong thanh lọc."""
        for module, filename, moc in FILTER_FORMS:
            for form in self._trong_thanh_loc(module, filename, moc):
                for el in form.iter():
                    cls = ((el.get('class') or '') + ' '
                           + (el.get('t-attf-class') or '')).split()
                    self.assertNotIn(
                        'wj-btn', cls,
                        '%s: nút trong thanh lọc %s đã bị kéo về atom, mất 42/38 của FB-08'
                        % (filename, moc))
                    self.assertNotIn('wj-iconbtn', cls, filename)

    def test_nut_thanh_loc_doc_token_dung_chung(self):
        """Chiều B — ba nút lọc tự dựng phải đọc token chiều cao của Filter, để
        đổi FB-08 một chỗ là cả 21 thanh lọc theo, không sót màn tự dựng.

        Kiểm TỪNG khối, không chỉ kiểm "file có nhắc token": một mũi mutation đổi
        riêng nút lọc PC của Công nợ về 40px vẫn lọt nếu chỉ tìm chuỗi cả file."""
        khoi = (('wujia_portal_debt', 'portal_debt.css', '.wj-debt-filter__go'),
                ('wujia_portal_debt', 'portal_debt.css', '.wj-debt-pc-filter .wj-pc-btn'),
                ('wujia_portal_sale', 'portal_order.css', '.wujia-morder-search-btn'))
        for module, css_file, selector in khoi:
            css = _strip_comments(_mod_css(module, css_file))
            self.assertIn(selector, css, '%s: mất khối %s' % (css_file, selector))
            body = css[css.index(selector):]
            body = body[body.index('{'):body.index('}')]
            self.assertIn('--wj-filter-btn-h-', body,
                          '%s %s: khai chiều cao bằng số cứng, đổi FB-08 sẽ sót màn này'
                          % (css_file, selector))
            self.assertNotRegex(body, r'(height|width):\s*\d+px',
                                '%s %s: vẫn còn số cứng cạnh token' % (css_file, selector))


@tagged('post_install', '-at_install', 'wujia_button_e6')
class TestNutNavbarLaBoundary(TransactionCase):
    """LIMIT E6b1 — nút chuông/giỏ trên navbar là nút ĐIỀU HƯỚNG của shell: tròn
    40 (bo 20), nền kính trên navbar màu (`_pc_account.css`, @≥1200). Kéo về atom
    thì hoặc mất dáng navbar, hoặc phải khai đè cao/bo/nền — tức giành dáng của
    atom. Cùng loại với BottomNavigation mà BA đã liệt là boundary."""

    def test_nut_navbar_khong_mang_atom(self):
        for module, filename in (('wujia_portal_notification', 'header_bell_inherit.xml'),
                                 ('wujia_portal_sale', 'header_cart_inherit.xml')):
            for el, cls in _atoms(_view(module, filename), 'wj-iconbtn'):
                self.assertNotIn('wujia-header-icon-btn', cls,
                                 '%s: nút navbar bị kéo về atom' % filename)

    def test_dang_cua_nut_navbar_van_o_mot_cho(self):
        """Nếu ngày nào navbar bỏ dáng riêng thì test đỏ để nhắc gỡ boundary."""
        css = _strip_comments(_css('_pc_account.css'))
        self.assertIn('wujia-header-icon-btn', css)


@tagged('post_install', '-at_install', 'wujia_button_e6')
class TestKhungPortalGocLaBoundary(TransactionCase):
    """LIMIT E6b1 — `/my/franchises` dựng bằng `portal.portal_layout` của Odoo.
    CSS design system nạp bằng `<link>` trong vỏ Wujia, khung gốc không có ⇒ atom
    ở đó ra nút trần (thước đo E6b1 bắt: bo 0, chữ 14/400). Màn Vuexy tương đương
    là `/portal/franchises` — nút ở đó mới phải là atom."""

    def test_man_khung_goc_khong_dung_atom(self):
        view = _view('wujia_portal_base', 'portal_templates.xml')
        self.assertFalse(_atoms(view, 'wj-btn') + _atoms(view, 'wj-iconbtn'),
                         'portal_templates.xml dùng khung Odoo gốc, atom sẽ không có dáng')

    def test_ban_vuexy_cua_cung_danh_sach_van_la_atom(self):
        """Chiều ngược: bỏ atom ở màn Vuexy thì test đỏ, tránh lấy LIMIT này làm cớ."""
        view = _view('wujia_portal_base', 'portal_franchises_in_layout.xml')
        self.assertTrue(_atoms(view, 'wj-btn'))

