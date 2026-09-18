"""D5 — DataList trên màn Công nợ.

F5b dời khỏi `wujia_portal_layout`: guard này kiểm chính màn của module này.
"""
import os
import re

from lxml import html

from odoo.tests import TransactionCase, tagged

from odoo.addons.wujia_portal_base.tests.css_probe import (
    CSS_DIR, CUSTOM, _chu_the, _css, _mod_css, _rule, _rule_in_media, _strip_comments,
    _view,
)

TMPL = 'wujia_portal_layout.wj_data_list'


@tagged('post_install', '-at_install', 'wujia_data_list_d5')
class TestDataListDebt(TransactionCase):
    """D5g — Công nợ: 2 bảng PC + 2 danh sách mobile (`wj-debt-inv` compact-row,
    `wj-debt-pay` detail-card). Variant chọn theo SỐ ĐO trước khi sửa (62 → dải
    64–76; 96 → dải 96–120), không theo tên gọi."""

    VIEW = ('wujia_portal_debt', 'portal_debt.xml')

    def _root(self):
        return _view(*self.VIEW)

    def _css(self):
        with open(os.path.join(CUSTOM, 'wujia_portal_debt', 'static', 'src', 'css',
                               'portal_debt.css'), encoding='utf-8') as fh:
            return fh.read()

    def _calls(self, variant=None):
        """Call site DataList của riêng view công nợ. `variant=None` ⇒ bảng
        (không khai dl_variant)."""
        out = []
        for call in self._root().xpath('//t[@t-call="wujia_portal_layout.wj_data_list"]'):
            got = call.xpath('./t[@t-set="dl_variant"]/@t-value')
            got = got[0].strip("'") if got else None
            if got == variant:
                out.append(call)
        return out

    def test_bon_call_site(self):
        """2 bảng PC + 1 compact-row + 1 detail-card = đúng 4."""
        self.assertEqual(len(self._calls(None)), 2, 'bảng PC công nợ không còn đủ 2')
        self.assertEqual(len(self._calls('compact-row')), 1, 'mobile hoá đơn')
        self.assertEqual(len(self._calls('detail-card')), 1, 'mobile thanh toán')

    def _bang(self):
        """Chọn theo CẤU TRÚC (có thead), không theo variant — nếu chọn theo
        variant thì một mutation đổi dl_variant làm đỏ ba test (bài học D5f #3)."""
        return [c for c in self._root().xpath(
            '//t[@t-call="wujia_portal_layout.wj_data_list"]') if c.xpath('.//thead')]

    def _mobile(self, ho):
        """Chọn theo lớp item, độc lập với dl_variant — cùng lý do trên."""
        out = []
        for call in self._root().xpath('//t[@t-call="wujia_portal_layout.wj_data_list"]'):
            for el in call.iter():
                cls = el.get('class') or el.get('t-attf-class') or ''
                if re.match(r'%s(?![-\w])' % re.escape(ho), cls):
                    out.append((call, cls))
                    break
        return out

    def test_moi_th_deu_co_scope(self):
        """Yêu cầu SEMANTIC của BA: trước D5g là 0/14."""
        tong = 0
        for call in self._bang():
            ths = call.xpath('.//thead//th')
            self.assertTrue(ths, 'bảng PC mất thead')
            for th in ths:
                self.assertEqual(th.get('scope'), 'col',
                                 'th thiếu scope="col": %s' % (th.text or '').strip())
            tong += len(ths)
        self.assertEqual(tong, 14, 'số cột 2 bảng công nợ đổi (8 + 6)')

    def test_item_mobile_mang_ca_hai_lop(self):
        """Mỗi danh sách mobile đúng 1 item mẫu, mang CẢ lớp cũ lẫn wj-data-item."""
        # Ranh giới từ: __name/__badge/--overdue là con BEM, không phải item (D5e #1).
        for ho in ('wj-debt-inv', 'wj-debt-pay'):
            found = self._mobile(ho)
            self.assertEqual(len(found), 1, '%s: phải đúng 1 danh sách' % ho)
            self.assertIn('wj-data-item', found[0][1].split(),
                          '%s: item thiếu wj-data-item' % ho)

    def test_pager_hai_bang_di_qua_component(self):
        """Vi phạm kiểm kê D5a (debt ×2 chỉ cần `có record` là hiện pager) nay được
        chặn ở TRONG component: E3c bỏ họ `wj-debt-pc-pagebtn`, guard ">1 trang" nằm
        ở `wj_pagination` (test_e3_pagination). Ở đây ghim: không ai dựng lại pager."""
        thay = 0
        for call in self._bang():
            pagers = call.xpath('./t[@t-set="dl_pager"]')
            self.assertEqual(len(pagers), 1, 'bảng PC công nợ phải truyền dl_pager')
            self.assertEqual(
                len(pagers[0].xpath('.//t[@t-call="wujia_portal_layout.wj_pagination"]')), 1,
                'bảng PC công nợ không gọi component pager')
            self.assertFalse(
                pagers[0].xpath('.//*[contains(@t-attf-class, "pagebtn")]'
                                ' | .//*[contains(@class, "pagebtn")]'),
                'nút trang cũ quay lại màn công nợ')
            thay += 1
        self.assertGreaterEqual(thay, 2, 'không quét trúng bảng nào — guard rỗng')

    def test_mot_chu_so_huu_dang_hai_ho(self):
        """Sau migrate, dáng (padding/nền/radius/height) chỉ được khai ở tầng
        `.wj-data-item`. Rule cũ phải bị khoá bằng `:not(.wj-data-item)`."""
        css = _strip_comments(self._css())
        DANG = ('padding', 'background', 'border-radius', 'height')
        kiem = 0
        for khoi in re.finditer(r'([^{}]+)\{([^{}]*)\}', css):
            sel, than = khoi.group(1).strip(), khoi.group(2)
            for phan in sel.split(','):
                # Bóc :not(...) TRƯỚC khi xét, nếu không điều kiện tự chứa
                # '.wj-data-item' và guard xanh rỗng (bẫy D5e #2).
                chu = _chu_the(re.sub(r':not\([^)]*\)', '', phan))
                if not re.match(r'\.(wj-debt-inv|wj-debt-pay)(?![-\w])', chu):
                    continue
                kiem += 1
                if ':not(.wj-data-item)' in phan or '.wj-data-item' in phan:
                    continue
                for prop in DANG:
                    self.assertNotRegex(
                        than, r'(^|;)\s*%s\s*:' % prop,
                        'rule cũ "%s" còn khai %s mà chưa khoá :not(.wj-data-item)'
                        % (phan.strip(), prop))
        # F4 xoá 2 rule vỏ `:not(.wj-data-item)`; còn 2 rule layout của hai họ.
        self.assertGreaterEqual(kiem, 2, 'không quét trúng rule nào — guard rỗng')

    def test_layout_khong_gianh_lai_dang(self):
        """Tầng layout của từng họ chỉ được khai LAYOUT. portal_debt.css không có
        @media cho mobile (khối mobile ẩn bằng d-lg-none ở XML) nên phạm vi đến từ
        chính lớp variant — khác D5e/D5f, phải kiểm ở tầng gốc."""
        css = self._css()
        for variant, ho in (('compact-row', 'wj-debt-inv'), ('detail-card', 'wj-debt-pay')):
            sel = '.wj-data-list--%s .%s.wj-data-item' % (variant, ho)
            than = _rule(css, sel)
            self.assertIsNotNone(than, 'thiếu rule layout %s' % sel)
            for prop in ('padding', 'background', 'border-radius', 'height', 'min-height'):
                self.assertNotRegex(than, r'(^|;)\s*%s\s*:' % prop,
                                    '%s giành lại dáng bằng %s' % (sel, prop))
            self.assertRegex(than, r'display\s*:\s*grid', '%s mất layout grid' % sel)

    def test_radius_khong_dung_token_chung(self):
        """Radius 12 của variant phải đè TẠI rule variant; token dùng chung
        --wj-debt-radius (alias --wujia-card-radius) giữ nguyên (bài học D5f)."""
        than = _rule(self._css(), '.wj-debt')
        self.assertIsNotNone(than, 'mất khối token .wj-debt')
        self.assertRegex(than, r'--wj-debt-radius:\s*var\(--wujia-card-radius\)',
                         'token radius dùng chung đã bị sửa')

    def test_summary_meta_khong_phai_danh_sach(self):
        """Bộ đo nhận `.wj-debt-summary__meta` (2 con, xếp dọc, cao 15px) là
        "danh sách" ở khổ mobile — nó KHÔNG phải danh sách record. Ghim như 10
        hàng mdash của D5e."""
        for el in self._root().iter():
            cls = el.get('class') or el.get('t-attf-class') or ''
            if 'wj-debt-summary__meta' in cls:
                self.assertNotIn('wj-data-item', cls.split(),
                                 'ô tóm tắt bị gắn nhầm wj-data-item')
