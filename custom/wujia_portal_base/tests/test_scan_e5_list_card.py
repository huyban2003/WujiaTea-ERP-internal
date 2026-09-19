"""E5 (quét nhiều module) — call site ListCard CMP-LC-001 (`UI-LISTCARD-001`).

Khung `wujia_portal_layout` giữ hợp đồng template (luật F5b); ở đây là bảng
"màn nào đã về component" cộng ba luật không màn nào được phá:

  · một implementation — call site nào cũng gọi `wj_list_card`, không tự dựng ruột;
  · không CSS anatomy theo route — `.wj-lc*` chỉ được khai ở khung;
  · họ class cũ của màn đã migrate phải BIẾN MẤT khỏi cả view lẫn CSS (nếu không,
    hai bộ dáng cùng sống và cái sau đè cái trước tuỳ độ đặc hiệu).

E5b thêm route mới chỉ bằng cách thêm một dòng vào MIGRATED.
"""
import os
import re

from odoo.tests import TransactionCase, tagged

from odoo.addons.wujia_portal_base.tests.css_probe import (
    CUSTOM, _mod_css, _strip_comments, _view,
)

TMPL = 'wujia_portal_layout.wj_list_card'
ROW = 'wujia_portal_layout.wj_list_card_row'

# (module, file view, số call site record, họ class cũ phải biến mất, file CSS module)
MIGRATED = [
    ('wujia_portal_purchase_history', 'portal_history.xml', 1,
     ('wujia-mhist-row',), 'portal_history.css'),
    ('wujia_portal_delivery', 'portal_delivery.xml', 1,
     ('wujia-mdelivery-row-top', 'wujia-mdelivery-row-headmain', 'wujia-mdelivery-row-id',
      'wujia-mdelivery-row-cols', 'wujia-mdelivery-row-colval'), 'portal_delivery.css'),
]

# Màn giữ nguyên grouped rows theo LC-23 — E5 KHÔNG được đụng.
GIU_NGUYEN = [('wujia_portal_base', 'portal_home.xml')]


@tagged('post_install', '-at_install', 'wujia_list_card_e5')
class TestListCardCallSites(TransactionCase):

    def _calls(self, module, filename):
        root = _view(module, filename)
        return root.xpath('//t[@t-call="%s"]' % TMPL)

    def _items(self, module, filename):
        root = _view(module, filename)
        out = []
        for el in root.iter():
            cls = el.get('class') or el.get('t-attf-class') or ''
            if 'wj-lc' in cls.split():
                out.append((el, cls))
        return out

    def test_moi_man_da_migrate_deu_goi_component(self):
        for module, filename, n, _cu, _css in MIGRATED:
            calls = self._calls(module, filename)
            self.assertEqual(len(calls), n,
                             '%s: số call site ListCard đổi' % module)

    def test_item_mang_ca_hai_lop(self):
        """Neo TOKEN ĐỨNG ĐẦU: `contains()` khớp cả `wj-lc__name` (bẫy D5c #3)."""
        for module, filename, _n, _cu, _css in MIGRATED:
            items = self._items(module, filename)
            self.assertTrue(items, '%s: không còn item nào mang wj-lc' % module)
            for _el, cls in items:
                self.assertIn('wj-data-item', cls.split(),
                              '%s: item thiếu wj-data-item (dáng ngoài của D5)' % module)

    def test_khong_con_ho_class_cu(self):
        """Hai bộ dáng cùng sống là nguồn của mọi hồi quy specificity đã trả giá
        ở D3/D4 — nên họ cũ phải mất ở CẢ view lẫn CSS."""
        for module, filename, _n, cu, css_file in MIGRATED:
            with open(os.path.join(CUSTOM, module, 'views', filename), encoding='utf-8') as fh:
                view = fh.read()
            css = _strip_comments(_mod_css(module, css_file))
            for ho in cu:
                self.assertNotIn(ho, view, '%s: họ cũ %s còn trong view' % (module, ho))
                self.assertNotRegex(css, r'\.%s(?![-\w])' % ho,
                                    '%s: họ cũ %s còn rule CSS' % (module, ho))

    def test_khong_css_anatomy_theo_route(self):
        """LC-24: một implementation — module không được tự khai lại `.wj-lc*`."""
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
                for sel, _body in re.findall(r'([^{}]+)\{([^}]*)\}', css):
                    if re.search(r'\.wj-lc(?![-\w])|\.wj-lc__', sel):
                        thay.append('%s → %s' % (fn, sel.strip()[:60]))
        self.assertEqual(thay, [], 'anatomy ListCard bị khai lại ngoài khung')

    def test_hang_phu_dung_khuon_chung(self):
        """LC-05: hàng phụ phải đi qua `wj_list_card_row`, không viết span tay —
        viết tay là cách nhãn/giá trị lệch cỡ chữ giữa các màn."""
        for module, filename, _n, _cu, _css in MIGRATED:
            root = _view(module, filename)
            rows = root.xpath('//t[@t-call="%s"]' % ROW)
            self.assertTrue(rows, '%s: không hàng phụ nào dùng khuôn chung' % module)
            # `wj-lc__row` trần được phép: khối skeleton là thanh xám, không có
            # nhãn/giá trị. Cấm là nhãn/giá trị viết tay — đó mới là chỗ lệch cỡ chữ.
            tay = [el.get('class') for el in root.iter()
                   if (el.get('class') or '') in ('wj-lc__label', 'wj-lc__value')]
            self.assertEqual(tay, [], '%s: còn nhãn/giá trị viết tay' % module)

    def test_home_giu_grouped_rows(self):
        """LC-23: Home preview KHÔNG tách 1 record 1 card — cấm migrate nhầm."""
        for module, filename in GIU_NGUYEN:
            self.assertFalse(self._calls(module, filename),
                             '%s: Home bị migrate, trái LC-23' % module)
            self.assertFalse(self._items(module, filename),
                             '%s: Home đã mang lớp wj-lc' % module)
