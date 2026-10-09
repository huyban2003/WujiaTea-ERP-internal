#!/usr/bin/env python3
"""Đo độ tương phản chữ toàn portal (WCAG AA) — thước nghiệm thu I13 #170 WJ-PORTAL-UI-006.

Mỗi trang: mọi phần tử có text node thấy được (kể cả placeholder ô nhập) → màu chữ thật × nền đặc
gộp từ chính nó ngược lên tổ tiên (alpha cộng dồn, opacity tổ tiên nhân vào chữ). Gặp gradient/ảnh nền
⇒ `skip_bg` (đúng ghi chú BA "chỉ dùng mẫu nền đặc xác định"), không tính vào kết luận.

Ngưỡng: chữ thường 4.5; chữ lớn (≥24px, hoặc ≥18.66px và đậm ≥700) 3.0 — liệt kê riêng.
Trạng thái: default cho mọi chữ; hover + focus cho phần tử tương tác (a, button, nav, chip, phân trang…);
disabled đo chung (BA yêu cầu ≥4.5 cả disabled). Focus ring (outline/box-shadow) đo riêng, ngưỡng 3.0.

    python3 scripts/qa/wj_contrast.py --base http://127.0.0.1:8113 --login anh.owner --out before.json
    python3 scripts/qa/wj_contrast.py --diff before.json after.json

Cần playwright (env odoo19 hoặc python có playwright).
"""
import argparse
import collections
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
    '/portal/profile', '/portal/change-password', '/portal/franchise-information',
]
# (trang danh sách, mẫu link chi tiết) — lấy bản ghi đầu tiên tìm thấy.
DETAILS = [
    ('/portal/order', r'^/portal/order/product/\d+$'),
    ('/portal/purchase-history', r'^/portal/purchase-history/\d+$'),
    ('/portal/delivery', r'^/portal/delivery/\d+$'),
    ('/portal/return', r'^/portal/return/\d+$'),
    ('/portal/notification', r'^/portal/notification/\d+$'),
    ('/portal/support', r'^/portal/support/\d+$'),
    ('/portal/knowledge', r'^/portal/knowledge/(?!search$)[\w-]+$'),
    ('/portal/info-request', r'^/portal/info-request/\d+$'),
]
WIDTHS = [1440, 390]

# Tắt transition để màu hover/focus đọc ngay, không phải chờ 150ms.
NO_ANIM = '*,*::before,*::after{transition:none!important;animation:none!important;caret-color:transparent!important}'

PROBE = r"""
(opts) => {
  const parse = s => {
    const m = s && s.match(/rgba?\(([^)]+)\)/);
    if (!m) return null;
    const p = m[1].split(/[ ,/]+/).filter(Boolean).map(Number);
    return [p[0], p[1], p[2], p.length > 3 ? p[3] : 1];
  };
  const over = (top, under) => {           // top (rgba) phủ lên under (rgb đặc)
    const a = top[3];
    return [0, 1, 2].map(i => top[i] * a + under[i] * (1 - a));
  };
  const lum = c => {
    const f = v => { v /= 255; return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); };
    return 0.2126 * f(c[0]) + 0.7152 * f(c[1]) + 0.0722 * f(c[2]);
  };
  const ratio = (a, b) => { const x = lum(a), y = lum(b); return (Math.max(x, y) + 0.05) / (Math.min(x, y) + 0.05); };
  const hex = c => '#' + c.slice(0, 3).map(v => Math.round(v).toString(16).padStart(2, '0')).join('').toUpperCase();

  // Nền đặc dưới phần tử: gom lớp nền từ nó lên gốc, dừng khi đủ đục.
  const background = el => {
    const layers = [];
    for (let e = el; e; e = e.parentElement) {
      const cs = getComputedStyle(e);
      if (cs.backgroundImage && cs.backgroundImage !== 'none') return {skip: cs.backgroundImage.slice(0, 40)};
      const c = parse(cs.backgroundColor);
      if (c && c[3] > 0) { layers.push(c); if (c[3] >= 1) break; }
    }
    let base = [255, 255, 255];
    for (let i = layers.length - 1; i >= 0; i--) base = over(layers[i], base);
    return {rgb: base};
  };
  const opacityChain = el => { let o = 1; for (let e = el; e; e = e.parentElement) o *= parseFloat(getComputedStyle(e).opacity); return o; };
  const visible = el => {
    const r = el.getBoundingClientRect();
    if (r.width < 2 || r.height < 2) return false;
    if (r.right <= 0 || r.left >= innerWidth) return false;             // off-canvas (sidebar mobile đóng)
    const cs = getComputedStyle(el);
    if (cs.visibility !== 'visible') return false;
    for (let e = el; e; e = e.parentElement) {
      const s = getComputedStyle(e);
      if (s.display === 'none') return false;
      if (s.clip === 'rect(0px, 0px, 0px, 0px)' || (s.position === 'absolute' && s.overflow === 'hidden' && e.getBoundingClientRect().width <= 1)) return false;
    }
    return true;
  };
  const path = el => {
    const seg = e => e.tagName.toLowerCase() + (typeof e.className === 'string' && e.className.trim()
      ? '.' + e.className.trim().split(/\s+/).filter(c => !/^(d-|col-|m[trblxy]?-|p[trblxy]?-|align-|justify-|flex-|text-truncate)/.test(c)).slice(0, 2).join('.') : '');
    const p = el.parentElement;
    return (p && p !== document.body ? seg(p) + ' > ' : '') + seg(el);
  };
  const disabledOf = el => !!el.closest('[disabled],.disabled,[aria-disabled="true"]');

  const measureEl = (el, fgCss, text, kind) => {
    const bg = background(el);
    const cs = getComputedStyle(el);
    const fs = parseFloat(cs.fontSize), fw = parseInt(cs.fontWeight, 10) || 400;
    const large = fs >= 24 || (fs >= 18.66 && fw >= 700);
    const fg0 = parse(fgCss);
    if (!fg0) return null;
    const item = {sel: path(el), text: text.slice(0, 40), fs, fw, large, disabled: disabledOf(el), kind};
    if (bg.skip) { item.skip_bg = bg.skip; item.fg = hex(fg0); return item; }
    const fg = [fg0[0], fg0[1], fg0[2], fg0[3] * opacityChain(el)];
    const fgRgb = over(fg, bg.rgb);
    item.fg = hex(fgRgb); item.bg = hex(bg.rgb);
    item.ratio = Math.round(ratio(fgRgb, bg.rgb) * 100) / 100;
    item.need = large ? 3 : 4.5;
    return item;
  };

  const out = [];
  const scope = opts.root ? [opts.root] : [document.body];
  const seen = new Set();
  for (const root of scope) {
    const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
    for (let n = walker.nextNode(); n; n = walker.nextNode()) {
      const t = n.nodeValue.replace(/\s+/g, ' ').trim();
      if (!t || !/[\p{L}\p{N}]/u.test(t)) continue;
      const el = n.parentElement;
      if (!el || seen.has(el) || ['SCRIPT', 'STYLE', 'NOSCRIPT', 'OPTION', 'TEMPLATE'].includes(el.tagName)) continue;
      seen.add(el);
      if (!visible(el)) continue;
      // Chữ SVG (nhãn trục biểu đồ) vẽ bằng `fill`, `color` chỉ là giá trị kế thừa không hiển thị.
      const svg = el instanceof SVGElement;
      const it = measureEl(el, svg ? getComputedStyle(el).fill : getComputedStyle(el).color, t, svg ? 'svg' : 'text');
      if (it) out.push(it);
    }
    for (const el of root.querySelectorAll('input[placeholder]:not([type=hidden]), textarea[placeholder]')) {
      if (el.value || !visible(el) || !el.placeholder.trim()) continue;
      const it = measureEl(el, getComputedStyle(el, '::placeholder').color, el.placeholder, 'placeholder');
      if (it) out.push(it);
    }
  }
  return out;
}
"""

# Phần tử tương tác cần đo hover/focus. Đánh dấu bằng data-wjc để lấy lại handle ổn định.
MARK_INTERACTIVE = r"""
(limit) => {
  const sel = 'a[href], button, [role=tab], [role=button], .nav-link, .page-link, [class*=chip], [class*=pill], label.btn';
  const ok = el => { const r = el.getBoundingClientRect(); if (r.width < 4 || r.height < 4 || r.right <= 0 || r.left >= innerWidth) return false;
    for (let e = el; e; e = e.parentElement) { const s = getComputedStyle(e); if (s.display === 'none' || s.visibility === 'hidden') return false; }
    return /[\p{L}\p{N}]/u.test(el.textContent); };
  // Gom theo "dáng" (tag + class) để không đo 50 link cùng loại.
  const byShape = new Map();
  for (const el of document.querySelectorAll(sel)) {
    if (!ok(el)) continue;
    const shape = el.tagName + '|' + (typeof el.className === 'string' ? el.className.trim().split(/\s+/).sort().join('.') : '');
    if (!byShape.has(shape)) byShape.set(shape, el);
  }
  let i = 0;
  for (const el of byShape.values()) { if (i >= limit) break; el.setAttribute('data-wjc', String(i++)); }
  return i;
}
"""

RING = r"""
(el) => {
  const parse = s => { const m = s && s.match(/rgba?\(([^)]+)\)/); if (!m) return null;
    const p = m[1].split(/[ ,/]+/).filter(Boolean).map(Number); return [p[0], p[1], p[2], p.length > 3 ? p[3] : 1]; };
  const lum = c => { const f = v => { v /= 255; return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); };
    return 0.2126 * f(c[0]) + 0.7152 * f(c[1]) + 0.0722 * f(c[2]); };
  const ratio = (a, b) => { const x = lum(a), y = lum(b); return (Math.max(x, y) + 0.05) / (Math.min(x, y) + 0.05); };
  const hex = c => '#' + c.slice(0, 3).map(v => Math.round(v).toString(16).padStart(2, '0')).join('').toUpperCase();
  const cs = getComputedStyle(el);
  let ring = null;
  if (cs.outlineStyle !== 'none' && parseFloat(cs.outlineWidth) >= 1) ring = parse(cs.outlineColor);
  else if (cs.boxShadow && cs.boxShadow !== 'none') ring = parse(cs.boxShadow);
  if (!ring || ring[3] === 0) return {ring: null};
  // Nền bên ngoài phần tử: nền của cha (ring vẽ ngoài viền).
  let bg = [255, 255, 255];
  const layers = [];
  for (let e = el.parentElement; e; e = e.parentElement) {
    const c = parse(getComputedStyle(e).backgroundColor);
    if (c && c[3] > 0) { layers.push(c); if (c[3] >= 1) break; }
  }
  for (let i = layers.length - 1; i >= 0; i--) { const t = layers[i]; bg = [0, 1, 2].map(k => t[k] * t[3] + bg[k] * (1 - t[3])); }
  const rr = [0, 1, 2].map(k => ring[k] * ring[3] + bg[k] * (1 - ring[3]));
  return {ring: hex(rr), bg: hex(bg), ratio: Math.round(ratio(rr, bg) * 100) / 100};
}
"""


# Hàm JS gọi lại trong ngữ cảnh 1 phần tử: "return" + chuỗi bắt đầu bằng xuống dòng ⇒ ASI trả undefined ⇒ strip.
PROBE, RING, MARK_INTERACTIVE = PROBE.strip(), RING.strip(), MARK_INTERACTIVE.strip()
CALL = '(el, fn) => (new Function("return " + fn))()(%s)'


def login(page, a):
    page.goto(a.base + '/portal/login', wait_until='domcontentloaded')
    page.fill('#wj-auth-login', a.login)
    page.fill('#wj-auth-password', a.password)
    page.press('#wj-auth-password', 'Enter')
    page.wait_for_load_state('domcontentloaded')
    if '/portal/login' in page.url:
        sys.exit('đăng nhập thất bại (%s)' % a.login)


def measure_page(page, a):
    page.add_style_tag(content=NO_ANIM)
    page.mouse.move(0, 0)
    items = page.evaluate(PROBE, {})
    for it in items:
        it['state'] = 'default'
    if a.no_states:
        return items, [], []
    n = page.evaluate(MARK_INTERACTIVE, a.interactive)
    rings, skipped = [], []
    for i in range(n):
        loc = page.locator('[data-wjc="%d"]' % i)
        try:
            loc.scroll_into_view_if_needed(timeout=1500)
            loc.hover(timeout=1500, force=True)
            page.wait_for_timeout(30)
            h = loc.evaluate(CALL % '{root: el}', PROBE)
            for it in h:
                it['state'] = 'hover'
            items += h
            page.mouse.move(0, 0)
            loc.focus(timeout=1500)
            # :focus-visible chỉ bật khi focus bằng bàn phím ⇒ ép qua Tab từ phần tử trước không ổn định;
            # Chromium coi focus() sau phím là focus-visible ⇒ nhấn Shift (không dịch focus) rồi focus lại.
            page.keyboard.press('Shift')
            loc.focus(timeout=1500)
            f = loc.evaluate(CALL % '{root: el}', PROBE)
            for it in f:
                it['state'] = 'focus'
            items += f
            r = loc.evaluate(CALL % 'el', RING)
            if r.get('ring'):
                r['sel'] = loc.evaluate('el => el.tagName.toLowerCase() + "." + (el.className || "").toString().trim().split(/\\s+/).slice(0, 2).join(".")')
                rings.append(r)
            loc.evaluate('el => el.blur()')
        except Exception as e:  # phần tử biến mất/che khuất — bỏ, không làm hỏng cả trang, nhưng đếm
            skipped.append(str(e).splitlines()[0][:120])
    return items, rings, skipped


def measure(a):
    from playwright.sync_api import sync_playwright
    pages = {}
    with sync_playwright() as p:
        b = p.chromium.launch()
        for w in a.widths:
            ctx = b.new_context(viewport={'width': w, 'height': 900 if w > 500 else 844}, locale='vi-VN')
            page = ctx.new_page()
            login(page, a)
            routes = list(a.routes)
            if not a.no_details:
                for list_url, pat in DETAILS:
                    page.goto(a.base + list_url, wait_until='load')
                    hrefs = page.eval_on_selector_all('a[href]', 'as => as.map(a => a.getAttribute("href"))')
                    hit = next((h for h in hrefs if h and re.match(pat, h.split('?')[0])), None)
                    if hit:
                        routes.append(hit.split('?')[0])
            for r in routes:
                resp = page.goto(a.base + r, wait_until='load')
                page.wait_for_timeout(a.settle)
                key = '%s@%d' % (r, w)
                if not resp or resp.status >= 400:
                    pages[key] = {'status': resp and resp.status}
                    continue
                items, rings, skipped = measure_page(page, a)
                pages[key] = {'items': items, 'rings': rings, 'state_errors': skipped}
                if a.shots:
                    pathlib.Path(a.shots).mkdir(parents=True, exist_ok=True)
                    page.screenshot(path='%s/%s_%d.png' % (a.shots, r.strip('/').replace('/', '_') or 'home', w), full_page=True)
            ctx.close()
        b.close()
    data = {'meta': {'login': a.login, 'base': a.base}, 'pages': pages}
    pathlib.Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    pathlib.Path(a.out).write_text(json.dumps(data, ensure_ascii=False, indent=0))
    report(data)


def fails(data):
    """→ list (key, item) chữ dưới ngưỡng + list (key, ring) ring dưới 3."""
    bad, rings = [], []
    for key, pg in data['pages'].items():
        for it in pg.get('items', []):
            if 'ratio' in it and it['ratio'] < it['need']:
                bad.append((key, it))
        for r in pg.get('rings', []):
            if r['ratio'] < 3:
                rings.append((key, r))
    return bad, rings


def report(data, top=60):
    bad, rings = fails(data)
    total = sum(len(pg.get('items', [])) for pg in data['pages'].values())
    skipped = sum(1 for pg in data['pages'].values() for it in pg.get('items', []) if 'skip_bg' in it)
    errs = {k: v['status'] for k, v in data['pages'].items() if 'status' in v}
    serr = sum(len(pg.get('state_errors', [])) for pg in data['pages'].values())
    states = collections.Counter(it['state'] for pg in data['pages'].values() for it in pg.get('items', []))
    print('trang %d · mẫu chữ %d %s (bỏ nền gradient/ảnh %d) · dưới ngưỡng %d · focus ring <3: %d · HTTP lỗi %s · lỗi đo trạng thái %d'
          % (len(data['pages']), total, dict(states), skipped, len(bad), len(rings), errs or 0, serr))
    groups = collections.defaultdict(lambda: {'n': 0, 'pages': set(), 'states': set(), 'text': ''})
    for key, it in bad:
        g = groups[(it['fg'], it['bg'], it['ratio'], it['sel'])]
        g['n'] += 1
        g['pages'].add(key)
        g['states'].add(it['state'] + ('/dis' if it['disabled'] else ''))
        g['text'] = g['text'] or it['text']
    for (fg, bg, ratio, sel), g in sorted(groups.items(), key=lambda kv: -kv[1]['n'])[:top]:
        print('  %5.2f %s/%s ×%-3d %-55s [%s] «%s» %s'
              % (ratio, fg, bg, g['n'], sel[:55], ','.join(sorted(g['states'])), g['text'][:24], sorted(g['pages'])[0]))
    if len(groups) > top:
        print('  … +%d nhóm' % (len(groups) - top))
    rg = collections.Counter((r['ring'], r['bg'], r['ratio'], r['sel']) for _, r in rings)
    for (ring, bg, ratio, sel), n in rg.most_common(20):
        print('  ring %5.2f %s/%s ×%d %s' % (ratio, ring, bg, n, sel))
    return len(bad), len(rings)


def diff(a_path, b_path):
    a, b = (json.loads(pathlib.Path(p).read_text()) for p in (a_path, b_path))
    print('TRƯỚC:')
    na = report(a, top=0)
    print('SAU:')
    nb = report(b)
    print('\ndưới ngưỡng %d → %d · ring %d → %d' % (na[0], nb[0], na[1], nb[1]))
    ka, kb = set(a['pages']), set(b['pages'])
    if ka != kb:
        print('trang chỉ có ở một mốc:', sorted(ka ^ kb))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--base', default='http://127.0.0.1:8113')
    ap.add_argument('--login', default='anh.owner')
    ap.add_argument('--password', default='wujia@test123')
    ap.add_argument('--routes', nargs='*', default=ROUTES)
    ap.add_argument('--widths', nargs='*', type=int, default=WIDTHS)
    ap.add_argument('--no-details', action='store_true', help='không tự thêm trang chi tiết')
    ap.add_argument('--no-states', action='store_true', help='chỉ đo default (nhanh)')
    ap.add_argument('--interactive', type=int, default=40, help='tối đa số phần tử tương tác đo hover/focus mỗi trang')
    ap.add_argument('--settle', type=int, default=500)
    ap.add_argument('--shots', help='thư mục chụp ảnh full trang')
    ap.add_argument('--out', default='wj_contrast.json')
    ap.add_argument('--report', metavar='JSON', help='in lại báo cáo từ file đã đo')
    ap.add_argument('--diff', nargs=2, metavar=('TRƯỚC', 'SAU'))
    a = ap.parse_args()
    if a.diff:
        diff(*a.diff)
    elif a.report:
        report(json.loads(pathlib.Path(a.report).read_text()), top=200)
    else:
        measure(a)


if __name__ == '__main__':
    main()
