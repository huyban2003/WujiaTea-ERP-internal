"""E7a (quét nhiều module) — PageContainer CMP-PC-001 (`UI-PAGECONTAINER-001`).

Khung `wujia_portal_layout` giữ hợp đồng container (luật F5b); ở đây là bốn luật
không màn nào được phá, vì lề trang chỉ có MỘT chủ:

  · vỏ route (content-wrapper, BlankShell, công nợ, Home, Khảo sát) không khai lề
    ngang — BA đo ra 30,8 / 14 / lề đôi chính vì mỗi vỏ tự đặt một số;
  · không module nào khai padding cho `.wj-page-header` (rule 16px không phạm vi của
    màn Khảo sát từng đè PageHeader của MỌI màn ⇒ tiêu đề lệch 16px so với nội dung);
  · không module nào tự chừa đáy trên `.app-content` (đáy thuộc container);
  · sổ màn danh sách (lề mobile 12, LC-08) khớp đúng cờ `pc_gutter='list'`.
"""
import os
import re

from lxml import etree

from odoo.tests import TransactionCase, tagged

from odoo.addons.wujia_portal_base.tests.css_probe import CUSTOM, _strip_comments

SHELLS = ('content-wrapper', 'wujia-mpage', 'wj-mpage', 'wj-debt', 'wujia-home-wrapper',
          'wujia-mhome', 'wj-inspection-container')

# (module, file view, template id) — màn DANH SÁCH theo LC-08 (BA Q2, chốt 24/09).
LIST_ROUTES = [
    ('wujia_portal_sale', 'portal_order_catalog.xml', 'portal_order_catalog'),
    ('wujia_portal_purchase_history', 'portal_history.xml', 'portal_history_list'),
    ('wujia_portal_return', 'portal_return_list.xml', 'portal_return_list'),
    ('wujia_portal_delivery', 'portal_delivery.xml', 'portal_delivery_tracking'),
    ('wujia_portal_debt', 'portal_debt.xml', 'portal_debt_overview'),
    ('wujia_portal_debt', 'portal_debt.xml', 'portal_debt_payment_history'),
    ('wujia_portal_notification', 'portal_notification.xml', 'portal_notification_list'),
    ('wujia_portal_knowledge', 'portal_knowledge.xml', 'portal_knowledge_list'),
    ('wujia_portal_support', 'portal_support.xml', 'portal_support_list'),
    ('wujia_portal_exam', 'portal_exam.xml', 'portal_exam_schedule'),
    ('wujia_portal_info_request', 'portal_info_request_list.xml', 'portal_info_request_list'),
    ('wujia_portal_report', 'portal_report_orders.xml', 'portal_report_orders'),
]


def _portal_css():
    """Mọi file CSS của các module portal — kể cả Khảo sát (E7a đã đưa về container)."""
    out = []
    for mod in sorted(os.listdir(CUSTOM)):
        if not mod.startswith('wujia_portal_'):
            continue
        for dirpath, _dirs, files in os.walk(os.path.join(CUSTOM, mod, 'static')):
            if os.sep + 'lib' + os.sep in dirpath + os.sep:
                continue
            for f in files:
                # Chỉ CSS của Wujia: bỏ bản Vuexy/Bootstrap gốc (components.css, core/…).
                if not f.endswith('.css') or f.endswith('.min.css'):
                    continue
                path = os.path.join(dirpath, f)
                rel = os.path.relpath(path, CUSTOM)
                if 'assets/css/' in rel and not f.startswith('_'):
                    continue
                with open(path, encoding='utf-8') as fh:
                    out.append((rel, _strip_comments(fh.read())))
    return out


def _rules(css):
    return re.findall(r'([^{}]+)\{([^{}]*)\}', css)


def _subject(part):
    """Compound cuối của một selector — phần thực sự bị style."""
    return re.split(r'[ >+~]+', part.strip())[-1]


def _horizontal_padding(body):
    """Giá trị lề ngang khác 0 mà thân rule khai, hoặc None."""
    for prop, val in re.findall(r'(?<![-\w])(padding(?:-left|-right|-inline)?)\s*:\s*([^;]+)', body):
        vals = val.replace('!important', '').split()
        if prop == 'padding':
            # 1 giá trị: cả bốn phía · 2–3: phần tử 2 là ngang · 4: phần tử 2 và 4.
            ngang = vals[:1] if len(vals) == 1 else vals[1:2] + vals[3:4]
        else:
            ngang = vals
        if any(v not in ('0', '0px') for v in ngang):
            return '%s: %s' % (prop, val.strip())
    return None


@tagged('post_install', '-at_install', 'wujia_page_container_e7')
class TestPageContainerScan(TransactionCase):

    def test_vo_route_khong_khai_le_ngang(self):
        hits = []
        for path, css in _portal_css():
            for sel, body in _rules(css):
                for part in sel.split(','):
                    subj = _subject(part)
                    if not any(re.search(r'\.%s(?![\w-])' % s, subj) for s in SHELLS):
                        continue
                    pad = _horizontal_padding(body)
                    if pad:
                        hits.append('%s: %s { %s }' % (path, part.strip()[:50], pad))
        self.assertFalse(hits, 'vỏ route tự khai lề ngang (lề thuộc PageContainer):\n  '
                         + '\n  '.join(hits))

    def test_vo_route_khong_gan_utility_le(self):
        """Lề ngang bằng class Bootstrap trên vỏ (`p-3`, `px-2`…) cũng là lề thứ hai."""
        hits = []
        for mod in sorted(os.listdir(CUSTOM)):
            vdir = os.path.join(CUSTOM, mod, 'views')
            if not mod.startswith('wujia_portal_') or not os.path.isdir(vdir):
                continue
            for fname in os.listdir(vdir):
                if not fname.endswith('.xml'):
                    continue
                for el in etree.parse(os.path.join(vdir, fname)).iter(tag=etree.Element):
                    toks = ('%s %s' % (el.get('class') or '', el.get('t-attf-class') or '')).split()
                    if not any(s in toks for s in SHELLS):
                        continue
                    bad = [t for t in toks if re.fullmatch(r'p[xse]?-(\w+-)?[1-5]', t)]
                    if bad:
                        hits.append('%s/%s:%s %s' % (mod, fname, el.sourceline, bad))
        self.assertFalse(hits, 'vỏ route gắn class lề ngang:\n  ' + '\n  '.join(hits))

    def test_khong_module_nao_de_padding_page_header(self):
        """Chỉ component (`_components.css` của khung) được khai padding cho PageHeader."""
        hits = []
        for path, css in _portal_css():
            if path.endswith('wujia_portal_layout/static/assets/css/_components.css'):
                continue
            for sel, body in _rules(css):
                for part in sel.split(','):
                    if re.fullmatch(r'\.wj-page-header(--(m|pc))?', _subject(part)) \
                            and _horizontal_padding(body):
                        hits.append('%s: %s' % (path, part.strip()[:60]))
        self.assertFalse(hits, 'module khác đè lề ngang PageHeader:\n  ' + '\n  '.join(hits))

    def test_khong_ai_chua_day_tren_app_content(self):
        hits = []
        for path, css in _portal_css():
            for sel, body in _rules(css):
                if any(_subject(p).startswith('.app-content') for p in sel.split(',')) \
                        and re.search(r'padding-bottom', body):
                    hits.append('%s: %s' % (path, sel.strip()[:60]))
        self.assertFalse(hits, 'đáy trang phải thuộc PageContainer:\n  ' + '\n  '.join(hits))

    def _template(self, module, fname, tid):
        tree = etree.parse(os.path.join(CUSTOM, module, 'views', fname))
        tpl = tree.xpath('//template[@id="%s"]' % tid)
        self.assertEqual(len(tpl), 1, '%s/%s: không thấy %s' % (module, fname, tid))
        return tpl[0]

    def _co_list(self, tpl):
        calls = tpl.xpath('.//t[@t-call="wujia_portal_layout.app_layout"]')
        return any(c.xpath('./t[@t-set="pc_gutter" and @t-value="\'list\'"]') for c in calls)

    def test_man_danh_sach_bat_bien_the_list(self):
        for module, fname, tid in LIST_ROUTES:
            with self.subTest(tid=tid):
                self.assertTrue(self._co_list(self._template(module, fname, tid)),
                                '%s thiếu pc_gutter=list (lề mobile 12, LC-08)' % tid)

    def test_chi_man_danh_sach_bat_list(self):
        """Form/chi tiết/Home/Tài khoản giữ lề 16 — bật `list` ngoài sổ là lệch chốt 24/09."""
        so = {tid for _m, _f, tid in LIST_ROUTES}
        thua = []
        for mod in sorted(os.listdir(CUSTOM)):
            vdir = os.path.join(CUSTOM, mod, 'views')
            if not mod.startswith('wujia_portal_') or not os.path.isdir(vdir):
                continue
            for fname in os.listdir(vdir):
                if not fname.endswith('.xml'):
                    continue
                for tpl in etree.parse(os.path.join(vdir, fname)).xpath('//template[@id]'):
                    if self._co_list(tpl) and tpl.get('id') not in so:
                        thua.append('%s/%s' % (mod, tpl.get('id')))
        self.assertFalse(thua, 'bật list ngoài sổ LC-08: %s' % thua)
