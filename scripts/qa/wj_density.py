#!/usr/bin/env python3
"""Đo mật độ khung mobile — PageHeader · SectionHeader · BottomNav (cụm G1).

Bằng chứng nghiệm thu cho 3 issue BA (21/09/2026):
  143 UI-MOB-HEADER-DENSITY-001  — PageHeader mobile pad dọc 8, SectionHeader 18/24
  145 UI-MOB-BOTTOMNAV-DENSITY-001 — thanh dưới 72 + safe area, nhãn 12, mục ~50
  144 WJ-ORD-MOB-SPACING-001     — /portal/order: search→chip 12, chip→danh sách 8

Mỗi route × mỗi khổ mobile đo: cao/pad PageHeader (theo biến thể), cỡ title
SectionHeader + title có đè meta không, cao thanh dưới + từng mục + cỡ nhãn,
badge có đè icon không, tràn ngang, và "cuộn tới cuối, phần tử cuối có nằm trên
thanh dưới không". Khổ PC chỉ lấy dấu vân tay (md5 ảnh chụp toàn trang + cao
trang) để chứng minh PC Δ0.

Safe area: `--safe-area 34` giả lập máy có home-indicator bằng CDP
`Emulation.setSafeAreaInsetsOverride` (Chromium ≥ 135).

    python3 scripts/qa/wj_density.py --base http://127.0.0.1:8031 --login dung.multi --out before.json
    python3 scripts/qa/wj_density.py --diff before.json after.json
"""
import argparse
import hashlib
import json
import re
import sys

MOBILE = [(360, 800), (390, 844), (430, 932)]
PC = [(1440, 900), (1024, 768), (992, 768)]

ROUTES = [
    '/portal', '/portal/order', '/portal/order/cart', '/portal/purchase-history',
    '/portal/delivery', '/portal/return', '/portal/return/new', '/portal/notification',
    '/portal/knowledge', '/portal/support', '/portal/support/new', '/portal/exam',
    '/portal/debt', '/portal/debt/payment-history', '/portal/debt/pay',
    '/portal/info-request', '/portal/info-request/new', '/portal/reports/orders',
    '/portal/profile', '/portal/change-password',
]
# Trang chi tiết: lấy link đầu tiên khớp mẫu trên trang danh sách.
DETAILS = [
    ('/portal/order', r'^/portal/order/product/\d+$'),
    ('/portal/purchase-history', r'^/portal/purchase-history/\d+$'),
    ('/portal/delivery', r'^/portal/delivery/\d+$'),
    ('/portal/return', r'^/portal/return/\d+$'),
    ('/portal/notification', r'^/portal/notification/\d+$'),
    ('/portal/knowledge', r'^/portal/knowledge/[^/]+$'),
    ('/portal/support', r'^/portal/support/\d+$'),
    ('/portal/info-request', r'^/portal/info-request/\d+$'),
]

PROBE = r"""
() => {
  const r2 = v => Math.round(v * 100) / 100;
  const vis = el => { const r = el.getBoundingClientRect();
    return r.width > 0 && r.height > 0 && getComputedStyle(el).visibility !== 'hidden'; };
  const box = el => { const r = el.getBoundingClientRect();
    return {x: r2(r.left), y: r2(r.top + scrollY), w: r2(r.width), h: r2(r.height),
            b: r2(r.bottom + scrollY)}; };
  const hit = (a, b) => a.left < b.right - 0.5 && b.left < a.right - 0.5 &&
                        a.top < b.bottom - 0.5 && b.top < a.bottom - 0.5;
  const out = {overflowX: document.documentElement.scrollWidth > document.documentElement.clientWidth + 1};
  // PageHeader mobile
  out.ph = [...document.querySelectorAll('.wj-page-header--m')].filter(vis).map(el => {
    const cs = getComputedStyle(el);
    const t = el.querySelector('.wj-page-header__title');
    const m = el.querySelector('.wj-page-header__meta');
    const variant = (el.className.match(/wj-page-header--(title|back|create)/) || [])[1];
    return {variant, h: r2(el.getBoundingClientRect().height), pt: cs.paddingTop, pb: cs.paddingBottom,
            px: cs.paddingLeft, titleFs: t && getComputedStyle(t).fontSize,
            titleLines: t ? Math.round(t.getBoundingClientRect().height / parseFloat(getComputedStyle(t).lineHeight)) : null,
            metaHit: !!(t && m && vis(m) && hit(t.getBoundingClientRect(), m.getBoundingClientRect()))};
  });
  // SectionHeader mobile/any
  out.sh = [...document.querySelectorAll('.wj-section-header--m, .wj-section-header--any')].filter(vis).map(el => {
    const t = el.querySelector('.wj-section-header__title');
    const slot = el.querySelector('.wj-section-header__meta, .wj-section-header__action, .wj-section-header__control');
    const tcs = t && getComputedStyle(t);
    return {text: t && t.textContent.trim().slice(0, 30), fs: tcs && tcs.fontSize, lh: tcs && tcs.lineHeight,
            mt: getComputedStyle(el).marginTop, mb: getComputedStyle(el).marginBottom,
            h: r2(el.getBoundingClientRect().height),
            slotHit: !!(t && slot && vis(slot) && hit(t.getBoundingClientRect(), slot.getBoundingClientRect())),
            slotOverflow: !!(slot && vis(slot) && slot.getBoundingClientRect().right > el.getBoundingClientRect().right + 0.5)};
  });
  // Bottom nav
  const nav = [...document.querySelectorAll('.wujia-mhome-bottomnav')].find(vis);
  if (nav) {
    const ncs = getComputedStyle(nav);
    const items = [...nav.querySelectorAll('.wujia-mhome-nav-item')].filter(vis);
    out.nav = {h: r2(nav.getBoundingClientRect().height), top: r2(nav.getBoundingClientRect().top),
      pt: ncs.paddingTop, pb: ncs.paddingBottom,
      items: items.map(i => r2(i.getBoundingClientRect().height)),
      itemW: items.map(i => r2(i.getBoundingClientRect().width)),
      label: (() => { const l = nav.querySelector('.wujia-mhome-nav-label'); return l && getComputedStyle(l).fontSize; })(),
      icon: (() => { const i = nav.querySelector('.wujia-mhome-nav-item i'); return i && getComputedStyle(i).fontSize; })(),
      active: items.filter(i => i.classList.contains('is-active')).map(i => i.textContent.trim()),
      overflow: nav.scrollWidth > nav.clientWidth + 1,
      badges: [...nav.querySelectorAll('.wujia-mhome-nav-badge')].filter(vis).map(b => {
        const i = b.closest('.wujia-mhome-nav-item').querySelector('i');
        const br = b.getBoundingClientRect(), ir = i.getBoundingClientRect();
        // phần giao nhau badge ∩ hộp icon (px²) — nét bell nằm trong ~70% giữa hộp 22
        const ix = Math.max(0, Math.min(br.right, ir.right) - Math.max(br.left, ir.left));
        const iy = Math.max(0, Math.min(br.bottom, ir.bottom) - Math.max(br.top, ir.top));
        const core = {left: ir.left + ir.width * .15, right: ir.right - ir.width * .15,
                      top: ir.top + ir.height * .15, bottom: ir.bottom - ir.height * .15};
        return {text: b.textContent.trim(), w: r2(br.width), overlapBox: r2(ix * iy),
                hitsGlyphCore: hit(br, core), topInItem: r2(br.top - b.closest('.wujia-mhome-nav-item').getBoundingClientRect().top)};
      })};
  }
  return out;
}
"""

# Cuộn tới cuối: phần tử nội dung thấp nhất (không fixed) phải nằm trên mép thanh dưới.
END_PROBE = r"""
() => {
  window.scrollTo(0, document.documentElement.scrollHeight);
  const nav = [...document.querySelectorAll('.wujia-mhome-bottomnav')].find(e => e.getBoundingClientRect().height > 0);
  if (!nav) return null;
  const navTop = nav.getBoundingClientRect().top;
  const fixedAnc = el => { for (let e = el; e; e = e.parentElement) {
      const p = getComputedStyle(e).position; if (p === 'fixed' || p === 'sticky') return e; } return null; };
  let low = null, lowB = -1;
  const root = document.querySelector('.content-wrapper, main') || document.body;
  root.querySelectorAll('a, button, input, textarea, select, p, span, td, h1, h2, h3, img').forEach(el => {
    const r = el.getBoundingClientRect();
    if (!r.width || !r.height || getComputedStyle(el).visibility === 'hidden' || fixedAnc(el)) return;
    if (r.bottom > lowB) { lowB = r.bottom; low = el; }
  });
  const fixedOverNav = [...document.querySelectorAll('.wujia-morder-floatbar, .wj-sticky-action, .wj-exam-mcta, [class*="sticky"]')]
    .filter(e => e.getBoundingClientRect().height > 0 && getComputedStyle(e).position === 'fixed')
    .map(e => ({cls: e.className.split(' ')[0], bottom: Math.round(e.getBoundingClientRect().bottom), navTop: Math.round(navTop)}));
  return {navTop: Math.round(navTop), lastBottom: Math.round(lowB),
          lastTag: low && (low.tagName + '.' + (low.className || '').toString().split(' ')[0]),
          clear: Math.round(navTop - lowB), fixedOverNav};
}
"""

LAYOUT_PROBE = r"""
() => [...document.body.querySelectorAll('*')].filter(e => {
    const r = e.getBoundingClientRect(); return r.width > 0 && r.height > 0 &&
      getComputedStyle(e).visibility !== 'hidden' && !e.closest('.pace, .o_loading_indicator');
  }).map(e => { const r = e.getBoundingClientRect(), s = getComputedStyle(e);
    return [e.tagName, (e.className && e.className.baseVal === undefined ? e.className : '').slice(0, 60),
            Math.round(r.left), Math.round(r.top + scrollY), Math.round(r.width), Math.round(r.height),
            s.fontSize, s.lineHeight, s.fontWeight, s.padding, s.margin, s.color, s.backgroundColor]; })
"""

ORDER_PROBE = r"""
() => {
  const root = document.querySelector('.wujia-morder');
  if (!root || !root.getBoundingClientRect().height) return null;
  const s = root.querySelector('.wujia-morder-search'), c = root.querySelector('#wj-ord-mchips');
  const h = root.querySelector('#wj-ord-mbody .wj-section-header');
  const R = e => e && e.getBoundingClientRect();
  const chipH = c && [...c.querySelectorAll('.wj-filter-chip')].map(x => Math.round(x.getBoundingClientRect().height));
  return {searchH: s && Math.round(R(s).height),
          inputH: (() => { const l = root.querySelector('.wujia-morder-search-input'); return l && Math.round(R(l).height); })(),
          searchToChip: s && c && !c.hidden ? Math.round((R(c).top - R(s).bottom) * 100) / 100 : null,
          chipToList: c && h && !c.hidden ? Math.round((R(h).top - R(c).bottom) * 100) / 100 : null,
          searchToList: s && h ? Math.round((R(h).top - R(s).bottom) * 100) / 100 : null,
          chipH: chipH && [...new Set(chipH)]};
}
"""


def login(page, base, user, password):
    page.goto(f'{base}/portal/login', wait_until='domcontentloaded')
    page.fill('#wj-auth-login', user)
    page.fill('#wj-auth-password', password)
    page.press('#wj-auth-password', 'Enter')
    page.wait_for_load_state('load')
    if '/login' in page.url:
        sys.exit(f'Login {user} hỏng')
    # User nhiều cửa hàng: overlay bắt chọn cửa hàng chặn mọi thao tác ⇒ chọn cái đầu.
    page.goto(f'{base}/portal', wait_until='load')
    if page.locator('#wujiaStoreOverlay.wujia-store-overlay--show').count():
        page.locator('#wujiaStoreOverlay .wujia-store-item').first.click()
        page.locator('#wujiaStoreOverlay form button[type=submit]').first.click()
        page.wait_for_load_state('load')


def resolve_details(page, base):
    urls = []
    for lst, pat in DETAILS:
        page.goto(base + lst, wait_until='load')
        hrefs = page.eval_on_selector_all('a[href]', 'els => els.map(e => e.getAttribute("href"))')
        hit = next((h.split('?')[0] for h in hrefs if h and re.match(pat, h.split('?')[0])), None)
        if hit:
            urls.append(hit)
    return urls


def measure(args):
    from playwright.sync_api import sync_playwright
    res = {'base': args.base, 'login': args.login, 'safe_area': args.safe_area, 'mobile': {}, 'pc': {}}
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        ctx = browser.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=1)
        if args.readonly:
            # UAT: chặn mọi lệnh gửi dữ liệu, chỉ để lọt POST đăng nhập + 2 bộ đếm badge (chỉ đọc).
            res['blocked'] = []
            reads = ('/portal/login', '/portal/notification/unread-count', '/portal/order/cart/count')

            def guard(route, req):
                if req.method in ('GET', 'HEAD') or (req.method == 'POST' and req.url.split('?')[0].endswith(reads)):
                    return route.continue_()
                res['blocked'].append(f'{req.method} {req.url}')
                route.abort()
            ctx.route('**/*', guard)
        page = ctx.new_page()
        login(page, args.base, args.login, args.password)
        routes = args.routes or (ROUTES + resolve_details(page, args.base))
        res['routes'] = routes
        cdp = ctx.new_cdp_session(page)
        if args.safe_area:
            cdp.send('Emulation.setSafeAreaInsetsOverride',
                     {'insets': {'top': 0, 'bottom': args.safe_area, 'left': 0, 'right': 0}})
        for w, h in ([] if args.no_mobile else MOBILE):
            page.set_viewport_size({'width': w, 'height': h})
            for r in routes:
                page.goto(args.base + r, wait_until='load')
                page.wait_for_timeout(args.settle)
                d = page.evaluate(PROBE)
                if r == '/portal/order':
                    d['order'] = page.evaluate(ORDER_PROBE)
                    if args.shots:
                        page.screenshot(path=f'{args.shots}/order_{w}.png')
                d['end'] = page.evaluate(END_PROBE)
                if args.shots and r in ('/portal/return', '/portal/support/new', '/portal/return/new'):
                    page.screenshot(path=f'{args.shots}/{r.strip("/").replace("/", "_")}_{w}_end.png')
                    page.evaluate('window.scrollTo(0,0)')
                    page.screenshot(path=f'{args.shots}/{r.strip("/").replace("/", "_")}_{w}.png')
                res['mobile'].setdefault(r, {})[str(w)] = d
            if args.shots:
                # Nhóm "Thêm": mở sheet trên một trang thuộc nhóm
                page.goto(args.base + '/portal/knowledge', wait_until='load')
                btn = page.locator('.wujia-mhome-bottomnav button.wujia-mhome-nav-item')
                if btn.count():
                    btn.first.click()
                    page.wait_for_timeout(400)
                    page.screenshot(path=f'{args.shots}/more_sheet_{w}.png')
                    res.setdefault('sheet', {})[str(w)] = page.evaluate(r"""() => {
                      const s = document.querySelector('.wujia-msheet'), n = document.querySelector('.wujia-mhome-bottomnav');
                      return s && n ? {sheetBottom: Math.round(s.getBoundingClientRect().bottom),
                                       navTop: Math.round(n.getBoundingClientRect().top)} : null; }""")
        if not args.no_pc:
            for w, h in PC:
                page.set_viewport_size({'width': w, 'height': h})
                for r in routes:
                    page.goto(args.base + r, wait_until='load')
                    page.wait_for_timeout(args.settle)
                    # md5 ảnh KHÔNG dùng được: thanh tiến trình góc trên-phải (56×3px) đổi
                    # pixel giữa hai lần chụp cùng code. Vân tay = hộp + chữ + khoảng cách của
                    # MỌI phần tử đang hiện ⇒ lệch 1px bố cục cũng bắt.
                    lay = page.evaluate(LAYOUT_PROBE)
                    if args.shots:
                        page.screenshot(path=f'{args.shots}/pc_{r.strip("/").replace("/", "_")[:60]}_{w}.png',
                                        full_page=True, animations='disabled', caret='hide')
                    res['pc'].setdefault(r, {})[str(w)] = {
                        'md5': hashlib.md5(json.dumps(lay).encode()).hexdigest(), 'n': len(lay),
                        'pageH': page.evaluate('document.documentElement.scrollHeight')}
                    if args.keep_layout:
                        res['pc'][r][str(w)]['layout'] = lay
        browser.close()
    with open(args.out, 'w') as f:
        json.dump(res, f, ensure_ascii=False, indent=1)
    print('ghi', args.out, '·', len(res['routes']), 'route',
          '· chặn %d request' % len(res['blocked']) if 'blocked' in res else '')


def diff(a_path, b_path):
    a, b = json.load(open(a_path)), json.load(open(b_path))
    print('== PC (md5 ảnh toàn trang) ==')
    same = tot = 0
    for r, ws in a['pc'].items():
        for w, v in ws.items():
            tot += 1
            v2 = b['pc'].get(r, {}).get(w)
            if v2 and v2['md5'] == v['md5']:
                same += 1
            else:
                print(f'  Δ {r} @{w}: pageH {v["pageH"]} → {v2 and v2["pageH"]}')
                la, lb = v.get('layout'), (v2 or {}).get('layout')
                if la and lb:
                    for x, y in zip(la, lb):
                        if x != y:
                            print('     ', x, '\n   →', y)
                            break
    print(f'  giống {same}/{tot}')
    print('== Mobile ==')
    for r, ws in a['mobile'].items():
        for w, v in ws.items():
            v2 = b['mobile'].get(r, {}).get(w, {})
            ph = lambda d: ','.join(f"{p['variant']}:{p['h']}" for p in d.get('ph', []))
            sh = lambda d: ','.join(sorted({p['fs'] + '/' + p['lh'] for p in d.get('sh', [])}))
            nv = lambda d: d.get('nav') and f"{d['nav']['h']}/{d['nav']['label']}"
            print(f'  {r:34} @{w}: PH {ph(v):16} → {ph(v2):16} SH {sh(v):10} → {sh(v2):10} NAV {nv(v)} → {nv(v2)}'
                  f"  end {v.get('end') and v['end']['clear']} → {v2.get('end') and v2['end']['clear']}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--base', default='http://127.0.0.1:8031')
    ap.add_argument('--login', default='dung.multi')
    ap.add_argument('--password', default='wujia@test123')
    ap.add_argument('--routes', nargs='*')
    ap.add_argument('--safe-area', type=int, default=0)
    ap.add_argument('--readonly', action='store_true', help='UAT: chặn mọi request không phải GET, trừ POST đăng nhập và bộ đếm badge')
    ap.add_argument('--no-pc', action='store_true')
    ap.add_argument('--no-mobile', action='store_true')
    ap.add_argument('--keep-layout', action='store_true', help='lưu cả danh sách phần tử PC để soi chỗ lệch')
    ap.add_argument('--shots')
    ap.add_argument('--settle', type=int, default=300)
    ap.add_argument('--out', default='wj_density.json')
    ap.add_argument('--diff', nargs=2)
    args = ap.parse_args()
    if args.diff:
        diff(*args.diff)
    else:
        measure(args)


if __name__ == '__main__':
    main()
