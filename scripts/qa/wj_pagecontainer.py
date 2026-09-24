#!/usr/bin/env python3
"""Guard PageContainer portal — cụm E7 (`CMP-PC-001` / `UI-PAGECONTAINER-001`).

Đo trên DOM thật, vì lề là tổng padding của cả chuỗi lớp bọc — đọc CSS không ra:

  PC-1  ĐẾM      mỗi route đúng MỘT `.wj-page-container`, không lồng nhau.
  PC-2  GUTTER   5 khối đầu (header/filter/section/card/list) bắt đầu cách mép
                 `.app-content` đúng 24 (≥992) / 16 (<992) / 12 (<992, biến thể `list`).
  PC-3  CHUỖI    giữa khối đó và `.app-content` chỉ MỘT lớp có padding ngang
                 (container) — không 30,8 / 14 / lề đôi.
  PC-4  TRỤC     5 khối cùng một x (± 0,5px).
  PC-5  TRÀN     `scrollWidth == innerWidth` (không dùng overflow-x:hidden để che).
  PC-6  ĐÁY      <992: cuộn tới đáy, nội dung cuối không nằm dưới bottom-nav.
  PC-7  NỀN      container trong suốt.
  PC-8  WIDTH    (E7b, ≥992) bề rộng trong = min(chỗ trống, 1440 standard | 960 narrow),
                 fluid = hết chỗ trống; standard/narrow căn giữa; header + khối đầu nằm
                 trong bề rộng trong (PageHeader không full-width riêng).

Trục x đo từ mép container (không phải `.app-content`): narrow/standard căn giữa nên
mép container dời vào trong, lề vẫn là gutter của container.

Kèm kiểm kê cho so sánh trước/sau (không tính vi phạm): số record thấy trong khung
nhìn đầu (tiêu chí 13 — mật độ không giảm), khoảng header → khối kế, padding trên/dưới.

    python3 scripts/qa/wj_pagecontainer.py --base http://127.0.0.1:8090 \
        --portal-login em.hcm [--routes ...] [--breakpoints ...] [--json out.json]
    python3 scripts/qa/wj_pagecontainer.py --diff before.json after.json
"""
import argparse
import json
import os
import sys
from urllib.parse import unquote

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from wj_measure import login  # noqa: E402

BREAKPOINTS = [360, 390, 991, 992, 1024, 1440]

# 14 route BA audit 26/08 (cột Build/Deploy của issue).
BA_ROUTES = [
    '/portal', '/portal/order', '/portal/order/cart', '/portal/purchase-history',
    '/portal/return', '/portal/return/new', '/portal/delivery', '/portal/debt',
    '/portal/notification', '/portal/knowledge', '/portal/support', '/portal/exam',
    '/portal/inspection', '/portal/profile',
]
# Mọi route còn lại dựng dưới `app_layout` — khung áp cho tất cả nên đo tất cả.
EXTRA_ROUTES = [
    '/portal/support/new', '/portal/info-request', '/portal/info-request/new',
    '/portal/reports/orders', '/portal/change-password', '/portal/franchise-information',
    '/portal/franchises', '/portal/debt/payment-history', '/portal/debt/pay',
    '/portal/exam/register',
    '@knowledge_detail', '@info_request_detail', '@product_detail', '@exam_detail',
    '@return_detail', '@support_detail', '@delivery_detail', '@inspection_detail',
]

# Màn chi tiết dò từ trang danh sách (ghi cứng id là sổ chết theo dữ liệu mẫu — E6b1).
DYNAMIC = {
    '@knowledge_detail': ('/portal/knowledge', '/portal/knowledge/'),
    '@info_request_detail': ('/portal/info-request', '/portal/info-request/'),
    '@product_detail': ('/portal/order', '/portal/order/product/'),
    '@exam_detail': ('/portal/exam', '/portal/exam/registration/'),
    '@return_detail': ('/portal/return', '/portal/return/'),
    '@support_detail': ('/portal/support', '/portal/support/'),
    '@delivery_detail': ('/portal/delivery', '/portal/delivery/'),
    '@inspection_detail': ('/portal/inspection', '/portal/inspection/'),
}

TOL = 0.5
WIDTH = {'standard': 1440, 'narrow': 960}


def resolve_dynamic(page, base, routes):
    for key, (list_route, prefix) in DYNAMIC.items():
        if key not in routes:
            continue
        page.goto(base + list_route, wait_until='load')
        page.wait_for_timeout(300)
        hrefs = page.eval_on_selector_all(
            'a[href^="%s"]' % prefix, 'els => els.map(e => e.getAttribute("href"))')
        hit = next((h for h in hrefs
                    if h and '?' not in h and '/attachment/' not in h
                    and not h.rstrip('/').endswith('/new')
                    and h.rstrip('/') != prefix.rstrip('/')), None)
        if hit:
            routes[routes.index(key)] = hit
            print('   %s → %s' % (key, hit))
        else:
            print('   %s: không dò được màn chi tiết từ %s — bỏ' % (key, list_route))
            routes.remove(key)


PROBE = r"""
() => {
  const r2 = v => Math.round(v * 100) / 100;
  const inFixed = el => {
    for (let p = el; p && p !== document.body; p = p.parentElement) {
      const pos = getComputedStyle(p).position;
      if (pos === 'fixed' || pos === 'sticky') return true;
      if (p.matches('.modal, .offcanvas, [role=dialog], .dropdown-menu, .wujia-mheader')) return true;
    }
    return false;
  };
  const vis = el => {
    const r = el.getBoundingClientRect();
    const cs = getComputedStyle(el);
    return r.width > 0 && r.height > 0 && cs.visibility !== 'hidden' && !inFixed(el);
  };
  window.scrollTo(0, 0);
  const app = document.querySelector('.app-content');
  if (!app) return {noApp: true};
  const ar = app.getBoundingClientRect();
  const c0 = document.querySelector('.wj-page-container');
  const cr = c0 ? c0.getBoundingClientRect() : ar;
  const containers = [...document.querySelectorAll('.wj-page-container')];
  const nested = containers.filter(c => c.parentElement && c.parentElement.closest('.wj-page-container')).length;

  const SEL = {
    header: '.wj-page-header, .wj-pc-page-header',
    filter: '.wj-pc-filterbar, .wj-filter-card',
    section: '.wj-section-header',
    card: '.wj-surface-card',
    list: '.wj-data-list, .wj-lc',
  };
  // Chuỗi padding ngang từ khối lên tới .app-content (bỏ chính khối): lề là TỔNG chuỗi này.
  const chain = el => {
    const out = [];
    for (let p = el.parentElement; p && p !== document.body && p !== app; p = p.parentElement) {
      // Lưới Bootstrap (.row âm + .col-* dương) là bố cục TRONG trang, tự triệt tiêu.
      if (p.matches('.row, [class*="col-"]')) continue;
      const cs = getComputedStyle(p);
      const pl = parseFloat(cs.paddingLeft) + parseFloat(cs.marginLeft) + parseFloat(cs.borderLeftWidth);
      const pr = parseFloat(cs.paddingRight) + parseFloat(cs.marginRight) + parseFloat(cs.borderRightWidth);
      if (Math.abs(pl) > 0.05 || Math.abs(pr) > 0.05) {
        const cls = (p.className && typeof p.className === 'string') ? p.className.split(/\s+/).filter(Boolean).slice(0, 3).join('.') : p.tagName;
        out.push({cls: cls || p.tagName.toLowerCase(), l: r2(pl), r: r2(pr)});
      }
    }
    return out;
  };
  // Khối ở cột 2+ của lưới/hàng (có anh em hiển thị nằm hẳn bên TRÁI, bắt đầu phía trên)
  // là bố cục trong trang, không phải "nội dung trực tiếp" — ví dụ card nội dung của
  // màn Tài khoản đứng sau cột menu. Không xét trục trang cho nó.
  const notFirstColumn = el => {
    const er = el.getBoundingClientRect();
    for (let p = el; p && p !== app; p = p.parentElement) {
      for (let q = p.previousElementSibling; q; q = q.previousElementSibling) {
        const qr = q.getBoundingClientRect();
        if (qr.width > 0 && qr.height > 0 && qr.right <= er.left + 0.5 &&
            qr.top < er.bottom) return true;
      }
    }
    return false;
  };
  const firsts = {};
  for (const [k, s] of Object.entries(SEL)) {
    // Khối "đầu trang" = khối ngoài cùng: bỏ khối nằm trong một khối cùng họ đã đếm
    // (card lồng card, list trong card) — chúng có đệm của component cha, không phải lề trang.
    const el = [...app.querySelectorAll(s)].find(e => vis(e) &&
      !Object.values(SEL).some(ss => e.parentElement && e.parentElement.closest(ss)) &&
      !notFirstColumn(e));
    if (!el) continue;
    const r = el.getBoundingClientRect();
    firsts[k] = {x: r2(r.left - cr.left), right: r2(cr.right - r.right), top: r2(r.top + scrollY),
                 cls: el.className.split(/\s+/).slice(0, 2).join('.'), chain: chain(el)};
  }
  const title = [...app.querySelectorAll('.wj-page-header__title, .wj-pc-page-header__title')].find(vis);
  const tr = title && title.getBoundingClientRect();

  // Khoảng header → khối kế tiếp (đo từ đáy header tới đỉnh phần tử hiển thị kế sau nó).
  let headerGap = null;
  const hdr = [...app.querySelectorAll(SEL.header)].find(vis);
  if (hdr) {
    const hb = hdr.getBoundingClientRect().bottom;
    const after = [...app.querySelectorAll('*')].filter(e => vis(e) &&
      (hdr.compareDocumentPosition(e) & Node.DOCUMENT_POSITION_FOLLOWING) && !hdr.contains(e) &&
      e.getBoundingClientRect().top >= hb - 0.5 && e.getBoundingClientRect().height > 8);
    if (after.length) headerGap = r2(Math.min(...after.map(e => e.getBoundingClientRect().top)) - hb);
  }

  const REC = '.wj-data-item, .wj-data-table tbody tr, .wj-lc, .wj-surface-card--list, table tbody tr';
  const recs = [...app.querySelectorAll(REC)].filter(vis);
  const seen = new Set();
  let recVisible = 0;
  for (const e of recs) {
    if ([...seen].some(s => s.contains(e))) continue;
    seen.add(e);
    const r = e.getBoundingClientRect();
    if (r.top < innerHeight && r.bottom > 0) recVisible++;
  }

  const c = containers[0];
  const ccs = c && getComputedStyle(c);
  const res = {
    containers: containers.length, nested,
    list: !!(containers[0] && containers[0].classList.contains('wj-page-container--list')),
    width: !c0 ? null : (c0.classList.contains('wj-page-container--narrow') ? 'narrow'
           : c0.classList.contains('wj-page-container--standard') ? 'standard' : 'fluid'),
    sticky: !!(c0 && c0.classList.contains('wj-page-container--sticky')),
    box: c0 ? {appW: r2(ar.width), left: r2(cr.left - ar.left), right: r2(ar.right - cr.right),
               inner: r2(cr.width - parseFloat(getComputedStyle(c0).paddingLeft)
                             - parseFloat(getComputedStyle(c0).paddingRight))} : null,
    appLeft: r2(ar.left),
    titleX: tr ? r2(tr.left - cr.left) : null,
    firsts, headerGap,
    scrollW: document.documentElement.scrollWidth, innerW: innerWidth,
    pageH: document.documentElement.scrollHeight,
    recVisible,
    container: c ? {pl: ccs.paddingLeft, pr: ccs.paddingRight, pt: ccs.paddingTop,
                    pb: ccs.paddingBottom, bg: ccs.backgroundColor, ov: ccs.overflowX} : null,
    bodyBg: getComputedStyle(document.body).backgroundColor,
    appBg: getComputedStyle(app).backgroundColor,
  };
  // Đáy: cuộn hết rồi so nội dung cuối với đỉnh bottom-nav.
  const nav = document.querySelector('.wujia-mhome-bottomnav');
  const navVisible = nav && nav.getBoundingClientRect().height > 0 && getComputedStyle(nav).display !== 'none';
  if (navVisible) {
    window.scrollTo(0, document.documentElement.scrollHeight);
    const navTop = nav.getBoundingClientRect().top;
    const root = c || app;
    const leaves = [...root.querySelectorAll('*')].filter(e => vis(e) && !e.closest('.wujia-mhome-bottomnav')
      && e.children.length === 0 && e.getBoundingClientRect().height > 4);
    const lastBottom = leaves.length ? Math.max(...leaves.map(e => e.getBoundingClientRect().bottom)) : null;
    res.bottom = {navTop: r2(navTop), lastBottom: lastBottom === null ? null : r2(lastBottom),
                  clear: lastBottom === null ? null : r2(navTop - lastBottom)};
    window.scrollTo(0, 0);
  }
  return res;
}
"""


def check(w, d):
    bad = []
    # <992 màn danh sách (biến thể `list`) = 12 theo LC-08 (BA Q2), còn lại 16.
    want = 24 if w >= 992 else (12 if d.get('list') else 16)
    if d.get('containers') != 1:
        bad.append(('PC-1', '%s .wj-page-container (cần đúng 1)' % d.get('containers')))
    if d.get('nested'):
        bad.append(('PC-1', '%d container lồng nhau' % d['nested']))
    xs = []
    for k, f in d.get('firsts', {}).items():
        xs.append(f['x'])
        if abs(f['x'] - want) > TOL:
            bad.append(('PC-2', '%s x=%s (cần %d) chuỗi=%s' % (k, f['x'], want, f['chain'])))
        pads = [c for c in f['chain'] if abs(c['l']) > 0.05]
        if len(pads) > 1:
            bad.append(('PC-3', '%s lề đôi: %s' % (k, pads)))
        for c in pads:
            if abs(c['l'] - 30.8) < 0.3 or abs(c['l'] - 14) < 0.3:
                bad.append(('PC-3', '%s lề cấm %.1f ở %s' % (k, c['l'], c['cls'])))
    if xs and max(xs) - min(xs) > TOL:
        bad.append(('PC-4', 'lệch trục: %s' % {k: f['x'] for k, f in d['firsts'].items()}))
    if d.get('scrollW', 0) > d.get('innerW', 0):
        bad.append(('PC-5', 'tràn ngang %s > %s' % (d['scrollW'], d['innerW'])))
    b = d.get('bottom')
    if b and b.get('clear') is not None and b['clear'] < -0.5:
        bad.append(('PC-6', 'nội dung cuối nằm dưới bottom-nav %spx' % b['clear']))
    bx, wd = d.get('box'), d.get('width')
    if w >= 992 and bx:
        avail = bx['appW'] - 2 * 24
        want_w = min(avail, WIDTH[wd]) if wd in WIDTH else avail
        if abs(bx['inner'] - want_w) > TOL:
            bad.append(('PC-8', '%s bề rộng trong %s (cần %s)' % (wd, bx['inner'], want_w)))
        if abs(bx['left'] - bx['right']) > TOL:
            bad.append(('PC-8', 'không căn giữa: trái %s phải %s' % (bx['left'], bx['right'])))
        for k, f in d.get('firsts', {}).items():
            if f['right'] < want - TOL:
                bad.append(('PC-8', '%s tràn ra ngoài bề rộng trong (phải=%s)' % (k, f['right'])))
    c = d.get('container')
    if c and c['bg'] not in ('rgba(0, 0, 0, 0)', 'transparent'):
        bad.append(('PC-7', 'container có nền %s' % c['bg']))
    if c and c['ov'] == 'hidden':
        bad.append(('PC-7', 'container overflow-x:hidden'))
    return bad


def run(args):
    from playwright.sync_api import sync_playwright
    routes = list(args.routes)
    result = {'breakpoints': args.breakpoints, 'routes': {}}
    total = 0
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        ctx = browser.new_context(viewport={'width': 1440, 'height': 900})
        page = ctx.new_page()
        errors = []
        page.on('pageerror', lambda e: errors.append(str(e)))
        login(page, args.base, args.portal_login, args.password)
        resolve_dynamic(page, args.base, routes)
        for route in routes:
            result['routes'][route] = {}
            for w in args.breakpoints:
                page.set_viewport_size({'width': w, 'height': args.height})
                resp = page.goto(args.base + route, wait_until='load')
                page.wait_for_timeout(args.settle)
                if args.collapsed and w >= 1200:
                    page.evaluate("document.body.classList.add('menu-collapsed');"
                                  "document.body.classList.remove('menu-expanded')")
                    page.wait_for_timeout(300)
                landed = unquote(page.url.split(args.base)[-1].split('?')[0])
                if landed.rstrip('/') != unquote(route.split('?')[0]).rstrip('/'):
                    print('!! %-34s @%-5d CHUYỂN HƯỚNG → %s' % (route, w, landed))
                    result['routes'][route][str(w)] = {'redirect': landed}
                    total += 1
                    continue
                d = page.evaluate(PROBE)
                bad = check(w, d)
                if resp is not None and resp.status != 200:
                    bad.insert(0, ('HTTP', str(resp.status)))
                d['violations'] = bad
                result['routes'][route][str(w)] = d
                total += len(bad)
                xs = ' '.join('%s=%s' % (k[0], f['x']) for k, f in d.get('firsts', {}).items())
                print('%s%-34s @%-5d %-8s in=%-7s title=%-6s %-28s rec=%-3s vi phạm=%d'
                      % ('OK ' if not bad else '!! ', route, w, d.get('width'),
                         (d.get('box') or {}).get('inner'), d.get('titleX'), xs,
                         d.get('recVisible'), len(bad)))
                if args.verbose:
                    for code, msg in bad:
                        print('      · %-5s %s' % (code, msg))
        browser.close()
    result['jsErrors'] = errors
    if errors:
        print('\n!! %d lỗi JS: %s' % (len(errors), errors[:2]))
    print('\nTỔNG: %d vi phạm · %d lỗi JS' % (total, len(errors)))
    if args.json:
        json.dump(result, open(args.json, 'w'), ensure_ascii=False, indent=1)
        print('→ %s' % args.json)
    return 1 if (total or errors) else 0


def diff(a_path, b_path):
    """So trước/sau: số record thấy + trục x + chiều cao trang, theo từng ô route×khổ."""
    a, b = json.load(open(a_path)), json.load(open(b_path))
    fewer = 0
    for route, by_w in a['routes'].items():
        for w, da in by_w.items():
            db = b['routes'].get(route, {}).get(w)
            if not db or 'redirect' in da or 'redirect' in db:
                continue
            ra, rb = da.get('recVisible'), db.get('recVisible')
            xa = {k: f['x'] for k, f in da.get('firsts', {}).items()}
            xb = {k: f['x'] for k, f in db.get('firsts', {}).items()}
            mark = ''
            if rb is not None and ra is not None and rb < ra:
                mark = '  ⚠ MẬT ĐỘ GIẢM'
                fewer += 1
            if xa != xb or ra != rb or da.get('titleX') != db.get('titleX'):
                print('%-34s @%-5s rec %s→%s  title %s→%s  x %s → %s  h %s→%s%s'
                      % (route, w, ra, rb, da.get('titleX'), db.get('titleX'), xa, xb,
                         da.get('pageH'), db.get('pageH'), mark))
    print('\nÔ mật độ giảm: %d' % fewer)
    return 1 if fewer else 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--base', default='http://127.0.0.1:8090')
    ap.add_argument('--portal-login', default='em.hcm')
    ap.add_argument('--password', default='wujia@test123')
    ap.add_argument('--routes', nargs='*', default=BA_ROUTES + EXTRA_ROUTES)
    ap.add_argument('--breakpoints', nargs='*', type=int, default=BREAKPOINTS)
    ap.add_argument('--height', type=int, default=900)
    ap.add_argument('--settle', type=int, default=450)
    ap.add_argument('--collapsed', action='store_true', help='đo PC ở trạng thái sidebar thu gọn')
    ap.add_argument('--verbose', '-v', action='store_true')
    ap.add_argument('--json')
    ap.add_argument('--diff', nargs=2, metavar=('BEFORE', 'AFTER'))
    args = ap.parse_args()
    if args.diff:
        sys.exit(diff(*args.diff))
    sys.exit(run(args))


if __name__ == '__main__':
    main()
