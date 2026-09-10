"""D6b — phân cấp card Bù hàng: UAT-BH-008 (tách badge) + UAT-BH-007 (tên 2 dòng).

Bám cột `Kết quả mong muốn` của hai issue:

  BH-008  "Người dùng phân biệt ngay trạng thái phê duyệt và tiến độ bù; card có
          thứ bậc thông tin rõ, cân đối và nhất quán với hệ thống Portal."
  BH-007  "…tên song ngữ dễ đọc, không bị cắt giữa nội dung và không tạo cảm giác
          dùng font rời rạc."

Đo *dáng* là việc của `scripts/qa/wj_returncard.py` (trình duyệt thật). Ở đây khoá
**hợp đồng cấu trúc + CSS nguồn**, thứ mà bảng đo không giữ được qua các sprint sau.
"""
import os
import re

from lxml import etree

from odoo.tests import TransactionCase, tagged

HERE = os.path.dirname(__file__)
MOD = os.path.abspath(os.path.join(HERE, '..'))
VIEW = os.path.join(MOD, 'views', 'portal_return_list.xml')
CSS = os.path.join(MOD, 'static', 'src', 'css', 'portal_return.css')


def _view():
    return etree.parse(VIEW)


def _css():
    with open(CSS, encoding='utf-8') as fh:
        return fh.read()


def _strip_comments(css):
    return re.sub(r'/\*.*?\*/', '', css, flags=re.S)


def _rule(css, selector):
    """Thân rule của `selector`, tìm ở MỌI tầng (file này bọc trong @media)."""
    css = _strip_comments(css)
    for m in re.finditer(re.escape(selector) + r'\s*\{([^}]*)\}', css):
        return m.group(1)
    return None


def _has_class(el, name):
    return name in (el.get('class') or '').split()


@tagged('post_install', '-at_install', 'wujia_return_d6')
class TestReturnCardD6(TransactionCase):

    def setUp(self):
        super().setUp()
        self.root = _view()
        rows = self.root.xpath('//a[@t-foreach="returns"]')
        self.assertEqual(len(rows), 1, 'card mobile phải là DUY NHẤT 1 mẫu record')
        self.row = rows[0]

    # ------------------------------------------------------------ BH-008
    def test_dong_dau_khong_con_badge_tien_do_bu(self):
        """Gốc rễ BH-008: trước D6b cả hai badge nằm trong `row-badges` của
        `row-head`. Dòng đầu chỉ được còn trạng thái phê duyệt."""
        heads = self.row.xpath('.//span[@class="wujia-mreturn-row-head"]')
        self.assertEqual(len(heads), 1)
        head = heads[0]
        # `comp_status_labels` là nguồn DUY NHẤT của nhãn tiến độ bù ⇒ dấu vết
        # của nó bên trong dòng đầu nghĩa là badge vẫn còn ở đó.
        dau_vet = [el for el in head.iter()
                   if 'comp_status_labels' in (el.get('t-value') or '')
                   or 'clbl' in (el.get('t-attf-class') or '')
                   or 'clbl' in (el.get('t-out') or '')]
        self.assertFalse(
            dau_vet, 'badge tiến độ bù vẫn nằm trong dòng đầu — BH-008 chưa đạt')

    def test_co_dong_tien_do_bu_rieng_co_nhan(self):
        """BA đòi rõ: dòng riêng, **nhãn "Tiến độ bù"**."""
        progs = self.row.xpath('.//span[@class="wujia-mreturn-row-progress"]')
        self.assertEqual(len(progs), 1, 'thiếu dòng riêng cho tiến độ bù')
        prog = progs[0]
        nhan = prog.xpath('.//span[@class="lbl"]')
        self.assertEqual(len(nhan), 1, 'dòng tiến độ bù phải có đúng 1 nhãn')
        self.assertEqual((nhan[0].text or '').strip(), 'Tiến độ bù')
        # dòng này là anh em của row-head, không lồng vào trong nó
        self.assertNotIn('wujia-mreturn-row-head',
                         [c.get('class') for c in prog.iterancestors()])

    def test_nhan_tien_do_bu_lay_tu_hang_controller(self):
        """Không hardcode 4 nhãn: nguồn phải là `comp_status_labels`, vốn chính là
        `COMPENSATION_STATUS_LABELS` truyền qua qcontext. Hardcode thì đổi nhãn ở
        controller mà card vẫn in nhãn cũ."""
        prog = self.row.xpath('.//span[@class="wujia-mreturn-row-progress"]')[0]
        badge = prog.xpath('.//span[contains(@t-attf-class, "wujia-badge")]')
        self.assertEqual(len(badge), 1)
        self.assertIn('clbl', badge[0].get('t-out') or '',
                      'badge tiến độ bù phải in từ biến clbl')
        nguon = self.row.xpath('.//t[contains(@t-value, "comp_status_labels")]')
        self.assertTrue(nguon, 'mất tham chiếu tới comp_status_labels')

        from ..controllers.portal import COMPENSATION_STATUS_LABELS
        for nhan, _lop in COMPENSATION_STATUS_LABELS.values():
            self.assertNotIn(
                nhan, etree.tostring(self.row, encoding='unicode'),
                'nhãn %r bị chép cứng vào template' % nhan)

    def test_metadata_hai_cot_on_dinh(self):
        """`flex` cho ô thứ hai trôi theo độ dài ô thứ nhất (đo trước D6b: 2 bố
        cục left khác nhau). BA đòi "bố cục hai cột ổn định"."""
        than = _rule(_css(), '.wujia-mreturn-row-meta')
        self.assertIsNotNone(than)
        self.assertIn('grid', than)
        self.assertRegex(than, r'grid-template-columns:\s*1fr\s+1fr')

    # ------------------------------------------------------------ BH-007
    def test_ten_san_pham_toi_da_hai_dong(self):
        than = _rule(_css(), '.wujia-mreturn-row-product')
        self.assertIsNotNone(than)
        self.assertRegex(than, r'-webkit-line-clamp:\s*2\b')
        self.assertNotIn('nowrap', than,
                         'còn `nowrap` ⇒ vẫn cắt ngay dòng 1, BH-007 chưa đạt')

    def test_khong_khai_lai_stack_font(self):
        """Fallback CJK đã nằm trên `--wujia-font-family` từ D2. Khai stack thứ hai
        ở module là nguồn của chính lỗi "font rời rạc" mà BH-007 phàn nàn."""
        self.assertNotIn('font-family', _strip_comments(_css()))

    # --------------------------------------------------- giao cắt D5f
    def test_giu_nguyen_hop_dong_datalist_d5f(self):
        """D6b sửa phân cấp BÊN TRONG card, KHÔNG đụng khung — nếu không sẽ tái
        tạo hồi quy "thẻ trắng lồng thẻ trắng" mà D5h.2 vừa vá."""
        self.assertTrue(_has_class(self.row, 'wujia-mreturn-row'))
        self.assertTrue(_has_class(self.row, 'wj-data-item'))
        calls = self.root.xpath(
            '//t[@t-call="wujia_portal_layout.wj_data_list"]'
            '[t[@t-set="dl_variant"][@t-value="\'detail-card\'"]]')
        self.assertEqual(len(calls), 1, 'call site DataList detail-card bị đổi')
        than = _rule(_css(), '.wj-data-list--detail-card .wujia-mreturn-row.wj-data-item')
        self.assertIsNotNone(than, 'mất rule layout của họ mreturn')
        for dang in ('border', 'background', 'border-radius'):
            self.assertNotIn(dang, than,
                             'D6b khai lại dáng khung %r — phải để component giữ' % dang)
