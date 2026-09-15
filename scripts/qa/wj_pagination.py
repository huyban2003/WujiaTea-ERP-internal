"""Guard Pagination `CMP-PGNT-001` — cụm E3 (`UI-PAGINATION-001`).

Bốn câu hỏi không guard nào hiện có trả lời được:

  PG-1  Nút phân trang có đúng hình học BA không? (visual 36 · bo 10 · gap 8 ·
        14/20/600 · chevron 16 · màu default/active/disabled)
  PG-2  Mobile vùng chạm có đạt 44 mà KHÔNG nở visual không? (đo hộp chạm qua
        `::before` bằng elementFromPoint ở 4 mép)
  PG-3  Còn họ pager riêng theo route nào không? Khảo sát defer, đếm riêng.
  PG-4  Đổi trang có GIỮ bộ lọc không? So query-string của link trang với URL
        hiện tại — đây là rủi ro số 2 BA nêu, và info-request vi phạm thật.

🔴 `--scope body` là mặc định và cố ý (bẫy D6d: thu hẹp scope ⇒ bỏ sót vỏ trang).
🔴 Mẫu rỗng là hỏng: pager chỉ render khi >1 trang ⇒ phải seed trước
   (`scripts/seed_e3_pager_demo.py`), nếu không bảng Pass này vô nghĩa.

    python3 scripts/qa/wj_pagination.py --base http://127.0.0.1:8087 \
        --portal-login em.hcm --out after.json
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from wj_measure import login  # noqa: E402

ROUTES = [
    '/portal/purchase-history', '/portal/support', '/portal/knowledge',
    '/portal/notification', '/portal/delivery', '/portal/return',
    '/portal/info-request', '/portal/exam', '/portal/debt', '/portal/order',
]
BREAKPOINTS = [1440, 1024, 992, 991, 390, 360]

SEL_NEW = '.wj-pagination'
SEL_LEGACY = ('.wj-pc-pagination, .wj-debt-pc-pagination, .wujia-pagination, '
              '.wujia-mhist-pager, .wujia-mknow-pager, .wujia-mnoti-pager, '
              '.wj-exam-pc-pagination, .wj-pc-order-pager, .wj-pc-page-btn')
SEL_DEFER = '.page-nav-btn'   # Khảo sát — luật 08/09, đếm riêng, không tính vi phạm

SPEC = {'size': 36.0, 'radius': 10.0, 'gap': 8.0, 'font': 14.0,
        'line': 20.0, 'weight': '600', 'chev': 16.0, 'touch': 44.0}

JS = r"""
([selNew, selLegacy, selDefer]) => {
  const vis = (el) => { const r = el.getBoundingClientRect();
                        return r.width > 0 && r.height > 0; };
  const touchBox = (el) => {
    const cs = getComputedStyle(el, '::before');
    return { h: parseFloat(cs.height) || 0, w: parseFloat(cs.minWidth) || 0,
             pos: cs.position };
  };
  const btn = (el) => {
    const cs = getComputedStyle(el);
    const r = el.getBoundingClientRect();
    const chev = el.querySelector('.wj-pagination__chev');
    return {
      tag: el.tagName.toLowerCase(),
      text: (el.textContent || '').trim().slice(0, 24),
      cls: el.className,
      h: Math.round(r.height * 100) / 100,
      w: Math.round(r.width * 100) / 100,
      radius: parseFloat(cs.borderTopLeftRadius),
      font: parseFloat(cs.fontSize),
      line: parseFloat(cs.lineHeight),
      weight: cs.fontWeight,
      bg: cs.backgroundColor, fg: cs.color, border: cs.borderTopColor,
      chev: chev ? parseFloat(getComputedStyle(chev).fontSize) : null,
      touch: touchBox(el),
      href: el.getAttribute('href'),
      ariaCurrent: el.getAttribute('aria-current'),
      ariaDisabled: el.getAttribute('aria-disabled'),
      tabbable: el.tagName === 'A' && el.hasAttribute('href'),
      name: (el.querySelector('.wj-pagination__label') || {}).textContent || '',
    };
  };
  const navs = [...document.querySelectorAll(selNew)].filter(vis).map((nav) => {
    const cs = getComputedStyle(nav);
    const btns = [...nav.querySelectorAll('.wj-pagination__btn')].filter(vis);
    const links = btns.filter((b) => b.tagName === 'A').map((b) => b.getAttribute('href'));
    const count = nav.querySelector('.wj-pagination__count');
    const status = nav.querySelector('.wj-pagination__status');
    const sizeSel = nav.querySelector('.wj-pagination__size');
    return {
      label: nav.getAttribute('aria-label'),
      // Gap BA nói là gap GIỮA CÁC NÚT (khối __nav), không phải gap của vỏ
      // ngoài vốn chia count | page-size | nav.
      gap: parseFloat(getComputedStyle(
        nav.querySelector('.wj-pagination__nav') || nav).gap) || 0,
      btns: btns.map(btn),
      links,
      countShown: !!(count && vis(count)),
      statusShown: !!(status && vis(status)),
      sizeShown: !!(sizeSel && vis(sizeSel)),
      current: btns.filter((b) => b.getAttribute('aria-current') === 'page').length,
    };
  });
  return {
    navs,
    legacy: [...document.querySelectorAll(selLegacy)].filter(vis)
      .map((e) => e.className),
    defer: document.querySelectorAll(selDefer).length,
    overflowX: document.documentElement.scrollWidth > window.innerWidth + 1,
    url: location.pathname + location.search,
  };
}
"""


def _qs(url):
    """Bộ lọc trong URL, bỏ `page`. URL không có '?' thì KHÔNG có param —
    `split('?')[-1]` trả nguyên đường dẫn ⇒ báo động giả (vá 15/09)."""
    query = url.split('?', 1)[1] if '?' in url else ''
    return sorted(p for p in query.split('&') if p and not p.startswith('page='))


def judge(data, width):
    """Vi phạm của MỘT ô (route × khổ), đối chiếu thẳng acceptance BA."""
    bad, mobile = [], width < 992
    here = _qs(data['url'])
    for nav in data['navs']:
        if nav['label'] != 'Phân trang':
            bad.append(f"nav thiếu nhãn (aria-label={nav['label']!r})")
        if abs(nav['gap'] - SPEC['gap']) > 0.5:
            bad.append(f"gap {nav['gap']} ≠ 8")
        if nav['current'] > 1:
            bad.append(f"{nav['current']} nút mang aria-current cùng lúc")
        # Bố cục theo khổ — BA: mobile CHỈ Prev + Trang x/y + Next.
        if mobile:
            if nav['countShown'] or nav['sizeShown']:
                bad.append('mobile vẫn hiện count/page-size')
            if not nav['statusShown']:
                bad.append('mobile thiếu nhãn "Trang x / y"')
            if len([b for b in nav['btns'] if b['text'].isdigit()]) > 0:
                bad.append('mobile vẫn hiện dãy số trang')
        else:
            if not nav['countShown']:
                bad.append('PC thiếu dòng count')
            if nav['statusShown']:
                bad.append('PC vẫn hiện nhãn "Trang x / y" của mobile')
        for b in nav['btns']:
            tag = repr(b['text'][:12])
            if abs(b['h'] - SPEC['size']) > 0.5:
                bad.append(f"{tag}: cao {b['h']} ≠ 36")
            if b['w'] < SPEC['size'] - 0.5:
                bad.append(f"{tag}: rộng {b['w']} < 36")
            if abs(b['radius'] - SPEC['radius']) > 0.5:
                bad.append(f"{tag}: bo {b['radius']} ≠ 10")
            if abs(b['font'] - SPEC['font']) > 0.5 or b['weight'] != SPEC['weight']:
                bad.append(f"{tag}: chữ {b['font']}/{b['weight']} ≠ 14/600")
            if abs(b['line'] - SPEC['line']) > 0.5:
                bad.append(f"{tag}: line-height {b['line']} ≠ 20")
            if b['chev'] is not None and abs(b['chev'] - SPEC['chev']) > 0.5:
                bad.append(f"{tag}: chevron {b['chev']} ≠ 16")
            if b['href'] == '#':
                bad.append(f"{tag}: href=\"#\"")
            if b['ariaDisabled'] == 'true' and b['tabbable']:
                bad.append(f"{tag}: disabled mà vẫn vào được tab order")
            if b['chev'] is not None and not b['name'].strip():
                bad.append(f"{tag}: nút icon không có tên đọc được")
            if mobile:
                t = b['touch']
                if t['pos'] != 'absolute' or t['h'] < SPEC['touch'] - 0.5 \
                        or t['w'] < SPEC['touch'] - 0.5:
                    bad.append(f"{tag}: vùng chạm {t['w']}×{t['h']} ({t['pos']}) < 44")
        # PG-4 — đổi trang phải giữ nguyên bộ lọc.
        for href in nav['links']:
            if href and _qs(href) != here:
                bad.append(f"link trang rơi bộ lọc: {href}")
                break
    if data['overflowX']:
        bad.append('TRÀN NGANG')
    return bad


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--base', default='http://127.0.0.1:8087')
    ap.add_argument('--portal-login')
    ap.add_argument('--password', default='wujia@test123')
    ap.add_argument('--routes', nargs='*', default=ROUTES)
    ap.add_argument('--breakpoints', nargs='*', type=int, default=BREAKPOINTS)
    ap.add_argument('--scope', default='body')
    ap.add_argument('--settle', type=int, default=600)
    ap.add_argument('--out')
    args = ap.parse_args()
    if not args.portal_login:
        sys.exit('--portal-login BẮT BUỘC (admin không thấy bề mặt portal).')

    sel_new = SEL_NEW if args.scope == 'body' else f'{args.scope} {SEL_NEW}'
    from playwright.sync_api import sync_playwright
    result, total_bad, n_new, n_legacy, n_defer = {}, 0, 0, 0, 0
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_context(viewport={'width': 1440, 'height': 900}).new_page()
        errors = []
        page.on('pageerror', lambda e: errors.append(str(e)))
        login(page, args.base, args.portal_login, args.password)

        for route in args.routes:
            for w in args.breakpoints:
                page.set_viewport_size({'width': w, 'height': 900})
                page.goto(f'{args.base}{route}', wait_until='load')
                page.wait_for_timeout(args.settle)
                data = page.evaluate(JS, [sel_new, SEL_LEGACY, SEL_DEFER])
                bad = judge(data, w)
                nb = sum(len(n['btns']) for n in data['navs'])
                key = f'{route}@{w}'
                result[key] = {'navs': len(data['navs']), 'btns': nb,
                               'legacy': data['legacy'], 'defer': data['defer'],
                               'findings': bad, 'detail': data['navs']}
                total_bad += len(bad)
                n_new += nb
                n_legacy += len(data['legacy'])
                n_defer += data['defer']
                print(f"{'✗' if bad else 'OK'} {route:26s} @{w:5d}  "
                      f"pager={len(data['navs'])} nút={nb:3d} "
                      f"cũ={len(data['legacy']):3d} vi phạm={len(bad):3d}")
                for b in bad[:6]:
                    print('     ✗', b)
        browser.close()

    print(f"\n=== TỔNG ===\n  nút component (mẫu đo) : {n_new}"
          f"\n  họ pager CŨ còn lại    : {n_legacy}"
          f"\n  Khảo sát (defer)       : {n_defer}"
          f"\n  vi phạm                : {total_bad}"
          f"\n  lỗi JS                 : {len(errors)}")
    if n_new == 0:
        print('  🔴 MẪU RỖNG — chưa seed >1 trang thì bảng Pass này vô nghĩa.')
    if args.out:
        json.dump(result, open(args.out, 'w', encoding='utf-8'),
                  ensure_ascii=False, indent=1)
        print(f'\n→ {args.out}')
    return 1 if (total_bad or errors or n_new == 0) else 0


if __name__ == '__main__':
    sys.exit(main())
