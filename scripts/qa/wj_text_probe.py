#!/usr/bin/env python3
"""Probe CHỮ portal theo ngôn ngữ — thước nghiệm thu Phần V (Việt hoá source, next-session-clusters-J.md §6).

Mỗi trang lấy: mọi text node (kể cả modal/sheet đang ẩn, trừ <script>/<style>), các attribute dịch được
(placeholder, title, aria-label, alt, value nút) và `data-wj-msg-*` (chuỗi JS theo quy ước §6), theo thứ tự DOM.
Chữ số che thành `#` ⇒ đồng hồ đếm ngược / ngày / số lượng không gây lệch giả.

    python3 scripts/qa/wj_text_probe.py --base http://127.0.0.1:8095 --lang vi_VN --out before.json
    (sửa source, -u, khởi động lại server)
    python3 scripts/qa/wj_text_probe.py --base http://127.0.0.1:8095 --lang vi_VN --out after.json
    python3 scripts/qa/wj_text_probe.py --diff before.json after.json      # nghiệm thu: 0 trang lệch

Đăng nhập bằng user portal (mặc định anh.owner); `--lang` ghi vào user qua /portal/set-lang trước khi đo,
khách chưa đăng nhập đo /portal/login. Cần playwright (env odoo19 hoặc python có playwright).
"""
import argparse
import difflib
import json
import pathlib
import re
import sys

ROUTES = [
    '/portal', '/portal/order', '/portal/order/cart', '/portal/purchase-history',
    '/portal/delivery', '/portal/return', '/portal/return/new', '/portal/notification',
    '/portal/knowledge', '/portal/support', '/portal/support/new', '/portal/exam',
    '/portal/exam/register',
    '/portal/debt', '/portal/debt/payment-history', '/portal/debt/pay',
    '/portal/info-request', '/portal/info-request/new', '/portal/reports/orders',
    '/portal/profile', '/portal/change-password',
]
# (trang danh sách, mẫu link chi tiết) — lấy bản ghi đầu tiên tìm thấy.
DETAILS = [
    ('/portal/order', r'^/portal/order/product/\d+$'),
    ('/portal/purchase-history', r'^/portal/purchase-history/\d+$'),
    ('/portal/delivery', r'^/portal/delivery/\d+$'),
    ('/portal/return', r'^/portal/return/\d+$'),
    ('/portal/notification', r'^/portal/notification/\d+$'),
    ('/portal/support', r'^/portal/support/\d+$'),
    ('/portal/info-request', r'^/portal/info-request/\d+$'),
]
WIDTHS = [1440, 390]

PROBE = r"""
() => {
  const out = [];
  const SKIP = new Set(['SCRIPT', 'STYLE', 'NOSCRIPT', 'TEMPLATE', 'svg']);
  const ATTRS = ['placeholder', 'title', 'aria-label', 'alt'];
  const walk = (el) => {
    if (SKIP.has(el.tagName)) return;
    for (const a of ATTRS) { const v = el.getAttribute && el.getAttribute(a); if (v && v.trim()) out.push('@' + a + ': ' + v); }
    if (el.tagName === 'INPUT' && ['submit', 'button'].includes(el.type) && el.value) out.push('@value: ' + el.value);
    for (const a of el.attributes || []) if (a.name.startsWith('data-wj-msg-')) out.push('@' + a.name + ': ' + a.value);
    for (const n of el.childNodes) {
      if (n.nodeType === 3) { const t = n.textContent.replace(/\s+/g, ' ').trim(); if (t) out.push(t); }
      else if (n.nodeType === 1) walk(n);
    }
  };
  walk(document.body);
  out.unshift('#title: ' + document.title);
  return out;
}
"""


def mask(lines):
    return [re.sub(r'\d+', '#', l) for l in lines]


def measure(a):
    from playwright.sync_api import sync_playwright
    out = {}
    with sync_playwright() as p:
        b = p.chromium.launch()
        for w in WIDTHS:
            ctx = b.new_context(viewport={'width': w, 'height': 900 if w > 500 else 844},
                                locale='en-US' if a.guest_en else 'vi-VN')
            page = ctx.new_page()
            page.goto(a.base + '/portal/login', wait_until='domcontentloaded')
            page.wait_for_timeout(a.settle)
            out['anon:/portal/login@%d' % w] = mask(page.evaluate(PROBE))
            page.fill('#wj-auth-login', a.login)
            page.fill('#wj-auth-password', a.password)
            page.press('#wj-auth-password', 'Enter')
            page.wait_for_load_state('domcontentloaded')
            if '/portal/login' in page.url:
                sys.exit('đăng nhập thất bại (%s)' % a.login)
            page.goto(a.base + '/portal/set-lang/' + a.lang, wait_until='domcontentloaded')
            routes = list(ROUTES)
            for list_url, pat in DETAILS:
                page.goto(a.base + list_url, wait_until='domcontentloaded')
                hrefs = page.eval_on_selector_all('a[href]', 'as => as.map(a => a.getAttribute("href"))')
                hit = next((h for h in hrefs if h and re.match(pat, h.split('?')[0])), None)
                if hit:
                    routes.append(hit.split('?')[0])
            for r in routes:
                resp = page.goto(a.base + r, wait_until='domcontentloaded')
                page.wait_for_timeout(a.settle)
                key = '%s@%d' % (r, w)
                out[key] = mask(page.evaluate(PROBE)) if resp and resp.status < 400 else ['#status: %s' % (resp and resp.status)]
            ctx.close()
        b.close()
    meta = {'lang': a.lang, 'login': a.login, 'base': a.base}
    pathlib.Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    pathlib.Path(a.out).write_text(json.dumps({'meta': meta, 'pages': out}, ensure_ascii=False, indent=1))
    print('ghi %s: %d trang, %d dòng chữ' % (a.out, len(out), sum(len(v) for v in out.values())))


def diff(path_a, path_b, show=12):
    A = json.loads(pathlib.Path(path_a).read_text())['pages']
    B = json.loads(pathlib.Path(path_b).read_text())['pages']
    changed = 0
    for k in sorted(set(A) | set(B)):
        x, y = A.get(k), B.get(k)
        if x is None or y is None:
            print('THIẾU %s (trước %s · sau %s)' % (k, x is not None, y is not None))
            changed += 1
            continue
        if x == y:
            continue
        changed += 1
        lines = [l for l in difflib.unified_diff(x, y, lineterm='', n=0) if l[:1] in '+-' and l[:3] not in ('+++', '---')]
        print('LỆCH %s (%d dòng)' % (k, len(lines)))
        for l in lines[:show]:
            print('   ', l[:160])
    print('%d/%d trang lệch' % (changed, len(set(A) | set(B))))
    return changed


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--base', default='http://127.0.0.1:8095')
    ap.add_argument('--login', default='anh.owner')
    ap.add_argument('--password', default='wujia@test123')
    ap.add_argument('--lang', default='vi_VN')
    ap.add_argument('--guest-en', action='store_true', help='trình duyệt khách gửi Accept-Language en-US')
    ap.add_argument('--out', default='text_probe.json')
    ap.add_argument('--settle', type=int, default=400)
    ap.add_argument('--diff', nargs=2)
    a = ap.parse_args()
    sys.exit(1 if diff(*a.diff) else 0) if a.diff else measure(a)
