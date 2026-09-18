"""D5 — DataList trên màn Đăng ký thi.

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
class TestDataListExam(TransactionCase):
    """D5h — Thi: 1 bảng PC + 3 danh sách mobile (`wujia-mexam-card` detail-card,
    `wujia-mexam-course` detail-card, `wujia-mexam-rrow` compact-row). Variant
    chọn theo SỐ ĐO trước khi sửa (109,25 và 116,25 → dải 96–120; 70 → dải 64–76).
    Hai call site nằm ở MÀN CON (/portal/exam/register, /portal/exam/registration/N)
    nên bộ đo 10 route BA không nhìn thấy — guard là chỗ duy nhất ghim chúng."""

    VIEW = ('wujia_portal_exam', 'portal_exam.xml')

    def _root(self):
        return _view(*self.VIEW)

    def _css(self):
        with open(os.path.join(CUSTOM, 'wujia_portal_exam', 'static', 'src', 'css',
                               'portal_exam.css'), encoding='utf-8') as fh:
            return fh.read()

    def _calls(self, variant=None):
        out = []
        for call in self._root().xpath('//t[@t-call="wujia_portal_layout.wj_data_list"]'):
            got = call.xpath('./t[@t-set="dl_variant"]/@t-value')
            got = got[0].strip("'") if got else None
            if got == variant:
                out.append(call)
        return out

    def _bang(self):
        """Chọn theo CẤU TRÚC (có thead) — bất biến trước mọi phép thay dl_variant
        (bài học D5g #3)."""
        return [c for c in self._root().xpath(
            '//t[@t-call="wujia_portal_layout.wj_data_list"]') if c.xpath('.//thead')]

    def _mobile(self, ho):
        """Quét TOKEN ở bất kỳ vị trí nào: item thi mở đầu bằng lớp wj-surface-card
        của D4 nên `re.match` từ đầu chuỗi (cách D5g) bỏ sót đúng call site này."""
        out = []
        for call in self._root().xpath('//t[@t-call="wujia_portal_layout.wj_data_list"]'):
            for el in call.iter():
                cls = el.get('class') or el.get('t-attf-class') or ''
                if re.search(r'(^|\s)%s(?![-\w])' % re.escape(ho), cls):
                    out.append((call, cls))
                    break
        return out

    def _bang_theo_lop(self, lop):
        """Chọn bảng theo LỚP CŨ ở dl_table_class — hai bảng PC của màn Thi khác
        nhau ở chỗ đó, còn cấu trúc (có thead) thì giống hệt."""
        out = []
        for call in self._bang():
            got = call.xpath('./t[@t-set="dl_table_class"]/@t-value')
            if got and re.search(r'(^|\s)%s(?![-\w])' % re.escape(lop), got[0]):
                out.append(call)
        return out

    def test_bon_call_site(self):
        self.assertEqual(len(self._bang()), 2, 'bảng PC lịch sử đăng ký + bảng kết quả')
        self.assertEqual(len(self._bang_theo_lop('wj-exam-pc-list-table')), 1)
        self.assertEqual(len(self._bang_theo_lop('wj-exam-pc-res-table')), 1,
                         'bảng kết quả thi (D5h.1) phải nằm trong wj_data_list')
        self.assertEqual(len(self._calls('detail-card')), 2, 'mexam-card + mexam-course')
        self.assertEqual(len(self._calls('compact-row')), 1, 'mexam-rrow')

    def test_moi_th_deu_co_scope(self):
        """0/8 trước lượt này. Bảng `wj-exam-pc-part-table` của form nhập KHÔNG
        nằm trong DataList nên cố ý ngoài phạm vi — ghi ở LIMIT."""
        tong = 0
        for call in self._bang():
            ths = call.xpath('.//thead//th')
            self.assertTrue(ths, 'bảng PC mất thead')
            for th in ths:
                self.assertEqual(th.get('scope'), 'col',
                                 'th thiếu scope="col": %s' % (th.text or '').strip())
            tong += len(ths)
        self.assertEqual(tong, 15, 'số cột hai bảng PC màn Thi đổi (8 + 7)')

    def test_item_mobile_mang_ca_hai_lop(self):
        for ho in ('wujia-mexam-card', 'wujia-mexam-course', 'wujia-mexam-rrow'):
            found = self._mobile(ho)
            self.assertEqual(len(found), 1, '%s: phải đúng 1 danh sách' % ho)
            self.assertIn('wj-data-item', found[0][1].split(),
                          '%s: item thiếu wj-data-item' % ho)

    def test_pager_di_qua_component(self):
        """Trước D5 pager màn Thi hiện dù chỉ 1 trang; E3c đưa cả guard đó vào
        component nên ở đây chỉ ghim: bảng PC thi phân trang bằng `wj_pagination`."""
        thay = 0
        for call in self._bang_theo_lop('wj-exam-pc-list-table'):
            pagers = call.xpath('./t[@t-set="dl_pager"]')
            self.assertEqual(len(pagers), 1, 'bảng PC thi phải truyền dl_pager')
            self.assertEqual(
                len(pagers[0].xpath('.//t[@t-call="wujia_portal_layout.wj_pagination"]')), 1,
                'bảng PC thi không gọi component pager')
            self.assertFalse(pagers[0].xpath('.//*[contains(@t-attf-class, "wj-pc-page-btn")]'),
                             'nút trang cũ quay lại màn thi')
            thay += 1
        self.assertGreaterEqual(thay, 1, 'không quét trúng bảng nào — guard rỗng')

    def test_bang_ket_qua_khong_de_pager_va_co_empty_state(self):
        """D5h.1 — bảng kết quả thi render trọn theo `pc_detail['lines']`, KHÔNG
        phân trang ⇒ không được đẻ pager giả (bài học pager giả ở D5h)."""
        # Chọn theo CẤU TRÚC (thead 7 cột) — đổi tên lớp là phép của
        # test_bon_call_site, không được kéo test này đỏ theo (bài học D5g #3).
        bang = [c for c in self._bang() if len(c.xpath('.//thead//th')) == 7]
        self.assertEqual(len(bang), 1)
        call = bang[0]
        self.assertFalse(call.xpath('./t[@t-set="dl_pager"]'),
                         'bảng kết quả không phân trang mà vẫn truyền dl_pager')
        self.assertFalse(call.xpath('.//t[@t-call="wujia_portal_layout.wj_pagination"]'
                                    ' | .//*[contains(@class, "wj-pagination")]'))
        empty = call.xpath('./t[@t-set="dl_empty"]/@t-value')
        self.assertEqual(len(empty), 1, 'thiếu dl_empty ⇒ 0 dòng vẫn vẽ khung bảng rỗng')
        self.assertIn("pc_detail['lines']", empty[0])
        self.assertTrue(call.xpath('./t[@t-set="dl_state"]//*[contains(@class, "wj-pc-empty")]'),
                        'thiếu DataState cho bảng kết quả')

    def test_bang_ket_qua_khoa_dang_cu(self):
        """Hai tầng: `.wj-exam-pc-res-table` cũ ép cứng header 46 / row 62 / đệm 20;
        phải khoá bằng :not(.wj-data-table) mới nhường số BA cho component."""
        css = _strip_comments(self._css())
        kiem = 0
        for khoi in re.finditer(r'([^{}]+)\{([^{}]*)\}', css):
            sel, than = khoi.group(1).strip(), khoi.group(2)
            for phan in sel.split(','):
                if not re.search(r'\.wj-exam-pc-res-table(?![-\w])', phan):
                    continue
                kiem += 1
                if ':not(.wj-data-table)' in phan:
                    continue
                for prop in ('height', 'padding'):
                    self.assertNotRegex(
                        than, r'(^|;)\s*%s\s*:' % prop,
                        'rule cũ "%s" còn ép %s mà chưa khoá :not(.wj-data-table)'
                        % (phan.strip(), prop))
        self.assertGreaterEqual(kiem, 3, 'không quét trúng rule nào — guard rỗng')

    def test_mot_chu_so_huu_dang_ba_ho(self):
        css = _strip_comments(self._css())
        DANG = ('padding', 'background', 'border-radius', 'height')
        kiem = 0
        for khoi in re.finditer(r'([^{}]+)\{([^{}]*)\}', css):
            sel, than = khoi.group(1).strip(), khoi.group(2)
            for phan in sel.split(','):
                chu = _chu_the(re.sub(r':not\([^)]*\)', '', phan))
                if not re.match(r'\.(wujia-mexam-card|wujia-mexam-course|wujia-mexam-rrow)(?![-\w])', chu):
                    continue
                kiem += 1
                if ':not(.wj-data-item)' in phan or '.wj-data-item' in phan:
                    continue
                for prop in DANG:
                    self.assertNotRegex(
                        than, r'(^|;)\s*%s\s*:' % prop,
                        'rule cũ "%s" còn khai %s mà chưa khoá :not(.wj-data-item)'
                        % (phan.strip(), prop))
        self.assertGreaterEqual(kiem, 3, 'không quét trúng rule nào — guard rỗng')

    def test_layout_hai_ho_nam_trong_media(self):
        """Rule layout phải nằm TRONG @media của portal_exam.css (khối mobile của
        file này bọc trong @media max-width 991.98) và không giành lại dáng."""
        css = self._css()
        for variant, ho in (('detail-card', 'wujia-mexam-course'),
                            ('compact-row', 'wujia-mexam-rrow')):
            sel = '.wj-data-list--%s .%s.wj-data-item' % (variant, ho)
            than = _rule_in_media(css, sel)
            self.assertIsNotNone(than, 'thiếu rule layout %s trong @media' % sel)
            for prop in ('padding', 'background', 'border-radius', 'height', 'min-height'):
                self.assertNotRegex(than, r'(^|;)\s*%s\s*:' % prop,
                                    '%s giành lại dáng bằng %s' % (sel, prop))
            self.assertRegex(than, r'display\s*:\s*flex', '%s mất layout flex' % sel)

    def test_surface_card_khong_bi_sua(self):
        """`wujia-mexam-card` mang cả wj-surface-card (D4) lẫn wj-data-item (D5).
        D5 đè dáng bằng ĐỘ ĐẶC HIỆU tại call site — component D4 phải bất biến."""
        css = _css('_components.css')
        than = _rule(css, '.wj-surface-card')
        self.assertIsNotNone(than, 'mất rule .wj-surface-card')
        self.assertRegex(than, r'border-radius:\s*var\(--wujia-surface-radius\)',
                         'CSS của SurfaceCard đã bị sửa ở lượt D5h')
        found = self._mobile('wujia-mexam-card')
        self.assertEqual(len(found), 1)
        self.assertIn('wj-surface-card', found[0][1].split(),
                      'item thi mất lớp wj-surface-card của D4')
