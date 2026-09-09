#!/usr/bin/env python3
"""Đếm "thẻ trắng lồng thẻ trắng" — guard cho acceptance CMP-SC-001.

Bộ đo `wj_datalist.py` đo dáng của từng phần tử, KHÔNG thấy quan hệ lồng nhau,
nên hồi quy D5h.2 (item card nằm trong vỏ card) lọt qua. Phép đếm ở đây chỉ hỏi
một câu: có vỏ `.wj-surface-card` nào ĐANG vẽ khung mà bên trong có
`.wj-data-item` cũng ĐANG vẽ khung không.

    python3 scripts/qa/wj_nesting.py --portal-login anh.owner --out /tmp/nest.json
"""
import argparse
import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from wj_datalist import login  # noqa: E402

BREAKPOINTS = [1440, 991, 390]
ROUTES = [
    '/portal', '/portal/knowledge', '/portal/support',
    '/portal/franchise-information', '/portal/purchase-history',
    '/portal/delivery', '/portal/notification',
]

PROBE = r"""
() => {
  const cs = el => getComputedStyle(el);
  const vis = el => {
    const r = el.getBoundingClientRect();
    return r.width > 0 && r.height > 0 && cs(el).visibility !== 'hidden';
  };
  // "Đang vẽ khung" = KHUNG THẺ, không phải nét kẻ ngăn dòng. Một nét kẻ đơn
  // (border-top ngăn hai item, không nền, không bo) KHÔNG tính — nếu tính thì
  // mọi danh sách kẻ dòng đều báo động giả n-1 lần.
  const framed = el => {
    const s = cs(el);
    const sides = ['Top', 'Right', 'Bottom', 'Left'].filter(
      k => (parseFloat(s['border' + k + 'Width']) || 0) > 0 && s['border' + k + 'Style'] !== 'none');
    const bg = s.backgroundColor;
    const hasBg = bg && bg !== 'transparent' && !/rgba\(0, 0, 0, 0\)/.test(bg);
    const radius = parseFloat(s.borderTopLeftRadius) || 0;
    return hasBg || sides.length >= 3 || (sides.length > 0 && radius > 0);
  };
  const key = el => {
    const id = el.getAttribute('data-wj') || '';
    const c = (el.className || '').toString().trim().split(/\s+/)
      .filter(x => /^(wj-|wujia-)/.test(x)).join('.');
    return (id ? id + '|' : '') + c;
  };
  const out = { nested: [], shells: 0, items: 0 };
  document.querySelectorAll('.wj-surface-card').forEach(shell => {
    if (!vis(shell)) return;
    out.shells++;
    if (!framed(shell)) return;
    const inner = [...shell.querySelectorAll('.wj-data-item')].filter(i => vis(i) && framed(i));
    if (!inner.length) return;
    out.nested.push({
      shell: key(shell),
      list: key(inner[0].closest('.wj-data-list') || inner[0].parentElement),
      items: inner.length,
    });
  });
  out.items = document.querySelectorAll('.wj-data-item').length;
  return out;
}
"""


def run(args):
    from playwright.sync_api import sync_playwright
    result = {'base': args.base, 'routes': {}}
    total = 0
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        ctx = browser.new_context(viewport={'width': 1440, 'height': 900})
        page = ctx.new_page()
        login(page, args.base, args.portal_login, args.password)
        for route in args.routes:
            result['routes'][route] = {}
            for w in args.breakpoints:
                page.set_viewport_size({'width': w, 'height': 900})
                resp = page.goto(args.base + route, wait_until='load')
                page.wait_for_timeout(args.settle)
                landed = re.sub(r'^https?://[^/]+', '', page.url).split('?')[0]
                if landed != route:
                    sys.exit(f'{route} @{w} đá về {landed} — dừng, đừng đếm rỗng.')
                d = page.evaluate(PROBE)
                d['status'] = resp.status if resp else None
                result['routes'][route][str(w)] = d
                total += len(d['nested'])
                mark = '!! ' if d['nested'] else 'OK '
                print(f"{mark}{route:28s} @{w:5d}  vỏ={d['shells']:2d} "
                      f"item={d['items']:3d} LỒNG={len(d['nested'])}")
                for n in d['nested']:
                    print(f"      ↳ {n['shell']}  ⊃  {n['list']} ×{n['items']}")
        browser.close()
    result['totalNested'] = total
    pathlib.Path(args.out).write_text(json.dumps(result, indent=1, ensure_ascii=False))
    print(f"\n=== TỔNG chỗ lồng khung: {total} ===\n→ {args.out}")
    return 1 if total else 0


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--base', default='http://127.0.0.1:8019')
    p.add_argument('--portal-login', required=True)
    p.add_argument('--password', default='wujia@test123')
    p.add_argument('--routes', nargs='+', default=ROUTES)
    p.add_argument('--breakpoints', nargs='+', type=int, default=BREAKPOINTS)
    p.add_argument('--out', default='/tmp/wj-nesting.json')
    p.add_argument('--settle', type=int, default=350)
    sys.exit(run(p.parse_args()))


if __name__ == '__main__':
    main()
