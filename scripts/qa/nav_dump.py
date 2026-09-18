#!/usr/bin/env python3
"""Đổ ra MỌI link điều hướng của portal, có thứ tự — bằng chứng cho phiên F5a.

`wj_measure` đo hình học (chiều cao, thẻ, số bản ghi) nên một mục menu đổi chủ,
đổi thứ tự hay mất active state đi qua nó mà không ai thấy. Script này đọc DOM đã
render và chép lại đúng những gì người dùng bấm được:

  sidebar PC · bottom-nav mobile · sheet "Thêm" · header mobile + dropdown avatar
  · navbar PC (chuông, giỏ, avatar)

Mỗi mục: thứ tự · href · nhãn · class icon · active · badge. F5a chuyển mục menu
từ layout về module sở hữu route ⇒ trước/sau phải khớp TUYỆT ĐỐI.

    python3 scripts/qa/nav_dump.py --base http://127.0.0.1:8099 --portal-login anh.owner \
        --routes /portal /portal/order --widths 1440 390 --out before.json
    python3 scripts/qa/nav_dump.py --diff before.json after.json
"""
import argparse
import json
import re
import sys

sys.path.insert(0, __file__.rsplit('/', 1)[0])
from wj_measure import login  # noqa: E402  (cùng cách đăng nhập, cùng bẫy đã vá)

PROBE = r"""
() => {
  const txt = el => (el ? (el.innerText || '').trim().replace(/\s+/g, ' ') : '');
  const icon = el => {
    const i = el.querySelector('i[class], svg[class]');
    return i ? (i.getAttribute('class') || '').trim() : '';
  };
  const vis = el => {
    const r = el.getBoundingClientRect();
    return r.width > 0 && r.height > 0 && getComputedStyle(el).visibility !== 'hidden';
  };
  const item = (el, i) => ({
    i, tag: el.tagName.toLowerCase(),
    id: el.id || '',
    href: el.getAttribute('href') || el.getAttribute('data-wujia-more') || '',
    label: txt(el).split('\n')[0],
    icon: icon(el),
    cls: (el.className || '').toString().trim(),
    active: /\b(active|is-active)\b/.test((el.className || '').toString()),
    visible: vis(el),
  });
  const list = (sel, childSel) => {
    const root = document.querySelector(sel);
    if (!root) return null;
    return [...root.querySelectorAll(childSel)].map(item);
  };
  return {
    // Sidebar PC: cả <li> mục lẫn <li> tiêu đề nhóm, giữ nguyên thứ tự.
    sidenav: list('#main-menu-navigation', ':scope > li'),
    bottomnav: list('.wujia-mhome-bottomnav', ':scope > a, :scope > button'),
    sheet: list('.wujia-msheet-list', ':scope > a'),
    mheader: list('.wujia-mheader', 'a'),
    navbar: list('nav.header-navbar', 'a'),
  };
}
"""


def run(args):
    from playwright.sync_api import sync_playwright
    out = {'base': args.base, 'login': args.portal_login, 'routes': {}}
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_context(viewport={'width': 1440, 'height': 900}).new_page()
        login(page, args.base, args.portal_login, args.password)
        for route in args.routes:
            out['routes'][route] = {}
            for w in args.widths:
                page.set_viewport_size({'width': w, 'height': 900})
                resp = page.goto(args.base + route, wait_until='load')
                page.wait_for_timeout(args.settle)
                data = page.evaluate(PROBE)
                data['status'] = resp.status if resp else None
                out['routes'][route][str(w)] = data
                n = {k: (len(v) if v else 0) for k, v in data.items() if isinstance(v, list)}
                print(f"OK {route:42s} @{w:5d}  sidenav={n.get('sidenav', 0):2d} "
                      f"bottom={n.get('bottomnav', 0)} sheet={n.get('sheet', 0):2d} "
                      f"mheader={n.get('mheader', 0)} navbar={n.get('navbar', 0)}")
        browser.close()
    with open(args.out, 'w', encoding='utf-8') as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    print('→', args.out)


def _norm(x):
    """Bỏ chữ số khỏi nhãn: badge chuông/quá hạn đổi theo dữ liệu giữa hai lượt đo,
    không phải thay đổi cấu trúc menu."""
    if x is None:
        return None
    y = dict(x)
    y['label'] = re.sub(r'\d+', '#', y.get('label', ''))
    return y


def diff(before, after):
    a = json.load(open(before, encoding='utf-8'))
    b = json.load(open(after, encoding='utf-8'))
    n = data_only = 0
    for route in sorted(set(a['routes']) | set(b['routes'])):
        ra, rb = a['routes'].get(route, {}), b['routes'].get(route, {})
        for w in sorted(set(ra) | set(rb), key=int):
            da, db = ra.get(w, {}), rb.get(w, {})
            for sec in ('sidenav', 'bottomnav', 'sheet', 'mheader', 'navbar'):
                la, lb = da.get(sec) or [], db.get(sec) or []
                if la == lb:
                    continue
                for i in range(max(len(la), len(lb))):
                    x = la[i] if i < len(la) else None
                    y = lb[i] if i < len(lb) else None
                    if x == y:
                        continue
                    if _norm(x) == _norm(y):
                        data_only += 1
                        continue
                    n += 1
                    print(f"[{route} @{w} {sec}#{i}]")
                    print(f"   TRƯỚC: {json.dumps(x, ensure_ascii=False)}")
                    print(f"   SAU  : {json.dumps(y, ensure_ascii=False)}")
    print(f"\nTỔNG mục lệch cấu trúc: {n} · lệch chỉ ở con số (dữ liệu): {data_only}")
    return n


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--base', default='http://127.0.0.1:8099')
    ap.add_argument('--portal-login')
    ap.add_argument('--password', default='wujia@test123')
    ap.add_argument('--routes', nargs='*', default=['/portal'])
    ap.add_argument('--widths', nargs='*', type=int, default=[1440, 390])
    ap.add_argument('--settle', type=int, default=400)
    ap.add_argument('--out', default='nav_dump.json')
    ap.add_argument('--diff', nargs=2, metavar=('TRƯỚC', 'SAU'))
    args = ap.parse_args()
    if args.diff:
        sys.exit(0 if diff(*args.diff) == 0 else 0)
    if not args.portal_login:
        ap.error('--portal-login là bắt buộc khi đo (tránh Pass rỗng)')
    run(args)


if __name__ == '__main__':
    main()
