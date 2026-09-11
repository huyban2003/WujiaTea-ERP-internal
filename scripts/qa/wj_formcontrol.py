#!/usr/bin/env python3
"""Guard control form mobile — cụm D6c (UAT-BH-009).

Không guard nào hiện có nhìn thấy ô nhập: `wj_datalist.py` đo dáng item,
`wj_returncard.py` soi phân cấp trong card, `wj_nesting.py` đo lồng khung.
Script này duyệt MỌI `input/select/textarea` nằm trong khối mobile
`.wujia-mpage` (đổi được bằng `--scope`) và trả lời ba câu của BA:

  chiều cao chạm  — ≥48px (BA: 44–48; chủ dự án chốt 48 cho bằng CTA)
  bo góc          — 12px, cùng token với card/nút
  nhãn ↔ ô nhập   — mỗi control có `id` và có `<label for>` trỏ đúng

Cột `cols` = số cột thật của khối cha (đếm bộ `left` khác nhau của các ô
cùng cha) — dùng cho vế "360px trường chật xuống một cột".

Nhóm giám sát (`.wj-inspection-container`) KHÔNG dùng `.wujia-mpage` nên tự
nằm ngoài phạm vi đo, đúng quyết định 08/09.

    python3 scripts/qa/wj_formcontrol.py --base http://127.0.0.1:8080 \
        --portal-login anh.owner [--breakpoints 390 360] [--json out.json]
"""
import argparse
import json
import sys

ROUTES = [
    '/portal', '/portal/order', '/portal/purchase-history', '/portal/delivery',
    '/portal/return', '/portal/return/new', '/portal/notification',
    '/portal/knowledge', '/portal/support', '/portal/support/new',
    '/portal/exam', '/portal/exam/register', '/portal/debt',
    '/portal/debt/payment-history', '/portal/info-request',
    '/portal/info-request/new', '/portal/reports/orders',
    '/portal/franchise-information', '/portal/profile',
]

MIN_FORM_H = 48       # control trong <form class="wj-mform">
MIN_TOUCH_H = 44      # mọi control khác — ngưỡng chạm BA
WANT_RADIUS = 12

JS = r"""
(scope) => {
  const px = v => Math.round(parseFloat(v) * 100) / 100;
  const vis = el => {
    const r = el.getBoundingClientRect();
    return r.width > 0 && r.height > 0 && getComputedStyle(el).visibility !== 'hidden';
  };
  const path = el => {
    const bits = [];
    for (let n = el; n && n.nodeType === 1 && bits.length < 4; n = n.parentElement) {
      const cls = (n.className || '').toString().trim().split(/\s+/).filter(Boolean);
      bits.unshift(n.tagName.toLowerCase() + (cls.length ? '.' + cls[0] : ''));
    }
    return bits.join('>');
  };
  const out = [];
  document.querySelectorAll(scope).forEach((page) => {
    if (!vis(page)) return;
    page.querySelectorAll('input, select, textarea').forEach((el) => {
      const type = (el.getAttribute('type') || '').toLowerCase();
      if (type === 'hidden' || !vis(el)) return;
      const cs = getComputedStyle(el);
      const r = el.getBoundingClientRect();
      let labelFor = null;
      if (el.id) {
        const lb = document.querySelector(`label[for="${CSS.escape(el.id)}"]`);
        if (lb) labelFor = (lb.textContent || '').trim().slice(0, 40);
      }
      const wrapped = el.closest('label');
      const parent = el.parentElement && el.parentElement.parentElement;
      let cols = null;
      if (parent && getComputedStyle(parent).display === 'grid') {
        const lefts = new Set([...parent.children].filter(vis)
          .map(c => Math.round(c.getBoundingClientRect().left)));
        cols = lefts.size;
      }
      const hit = el.closest('label, .wj-filter-date, .wj-filter-select') || el;
      out.push({
        inForm: !!el.closest('.wj-mform'),
        hitH: Math.round(hit.getBoundingClientRect().height * 100) / 100,
        tag: el.tagName.toLowerCase(), type: type || null,
        name: el.getAttribute('name'), id: el.id || null,
        cls: (el.className || '').toString().trim(),
        h: px(r.height), radius: px(cs.borderTopLeftRadius),
        labelFor, wrappedInLabel: !!wrapped,
        aria: el.getAttribute('aria-label') || el.getAttribute('aria-labelledby'),
        cols, path: path(el),
      });
    });
  });
  return out;
}
"""


def judge(route, rows):
    """Hai chuẩn: control trong `wj-mform` theo spec form (48/r12), còn lại chỉ đòi
    ngưỡng chạm 44 — dáng riêng (bo góc, cỡ chữ) của FilterBar chờ `UI-FILTER-001`.
    Ô trần nằm trong pill (`.wj-filter-date`) đo vùng chạm THẬT là pill, không phải ô."""
    bad = []
    n_small = n_radius = n_nolabel = 0
    for c in rows:
        who = f"{route} {c['tag']}[{c['name'] or c['cls'][:22]}]"
        h = max(c['h'], c.get('hitH') or 0)
        need = MIN_FORM_H if c.get('inForm') else MIN_TOUCH_H
        if h + 0.5 < need:
            n_small += 1
            bad.append(f"{who}: chạm {h}px (<{need})")
        if c.get('inForm') and abs(c['radius'] - WANT_RADIUS) > 0.5:
            n_radius += 1
            bad.append(f"{who}: radius {c['radius']}px (≠{WANT_RADIUS})")
        if not (c['labelFor'] or c['wrappedInLabel'] or c['aria']):
            n_nolabel += 1
            bad.append(f"{who}: không có nhãn liên kết (id={c['id']})")
    return bad, {
        'control': len(rows), 'dưới_ngưỡng_chạm': n_small,
        'lệch_radius': n_radius, 'thiếu_nhãn': n_nolabel,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--base', default='http://127.0.0.1:8080')
    ap.add_argument('--portal-login', required=True)
    ap.add_argument('--password', default='wujia@test123')
    ap.add_argument('--routes', nargs='*', default=ROUTES)
    ap.add_argument('--breakpoints', nargs='*', type=int, default=[390, 360])
    ap.add_argument('--scope', default='.wujia-mpage',
                    help='khối bao control cần đo (mặc định khối mobile)')
    ap.add_argument('--settle', type=int, default=500)
    ap.add_argument('--json')
    args = ap.parse_args()

    from playwright.sync_api import sync_playwright
    result, total_bad, total_ctl, redirects = {}, 0, 0, 0
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_context(viewport={'width': 390, 'height': 900}).new_page()
        page.goto(f'{args.base}/web/login', wait_until='domcontentloaded')
        page.fill('input[name="login"]', args.portal_login)
        page.fill('input[name="password"]', args.password)
        page.press('input[name="password"]', 'Enter')
        page.wait_for_load_state('domcontentloaded')
        if '/web/login' in page.url:
            sys.exit(f'ĐĂNG NHẬP HỎNG cho {args.portal_login!r} — mọi số đo sẽ là Pass rỗng.')

        for w in args.breakpoints:
            page.set_viewport_size({'width': w, 'height': 900})
            per_route = {}
            print(f"\n=== {w}px ===")
            for route in args.routes:
                page.goto(f'{args.base}{route}', wait_until='load')
                page.wait_for_timeout(args.settle)
                landed = page.url.split(args.base)[-1].split('?')[0]
                if landed.rstrip('/') != route.rstrip('/'):
                    redirects += 1
                    print(f'  ~ {route} → redirect {landed} (bỏ qua)')
                    continue
                rows = page.evaluate(JS, args.scope)
                bad, stats = judge(route, rows)
                total_bad += len(bad)
                total_ctl += stats['control']
                per_route[route] = {'stats': stats, 'findings': bad, 'controls': rows}
                if stats['control']:
                    flag = '✗' if bad else '✓'
                    print(f"  {flag} {route:<34} {stats}")
            result[w] = per_route
        browser.close()

    if args.json:
        with open(args.json, 'w', encoding='utf-8') as fh:
            json.dump(result, fh, ensure_ascii=False, indent=1)
        print(f'\n→ {args.json}')
    print(f'\nTỔNG control đo: {total_ctl} · vi phạm: {total_bad} · redirect: {redirects}')
    return 1 if total_bad else 0


if __name__ == '__main__':
    sys.exit(main())
