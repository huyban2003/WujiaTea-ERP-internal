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
    CUSTOM, _mod_css, _strip_comments, _view,
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
            css = _strip_comments(_mod_css(module, css_file))
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
