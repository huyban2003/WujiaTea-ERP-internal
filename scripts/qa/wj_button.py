#!/usr/bin/env python3
"""Guard Button/IconButton portal — cụm E6 (`CMP-BTN-001` / `UI-BUTTON-001`).

Sáu câu hỏi, đo trên DOM thật vì cả sáu chỉ tồn tại lúc chạy:

  BT-1  SIZE      cao đúng 32/40/46 (PC ≥992) · 36/44/48 (mobile) theo size class.
  BT-2  HÌNH HỌC  radius 8 (sm) / 12 (md,lg); typo 13/18/600 · 14/20/700 · 15/22/700.
  BT-3  CHẠM      ở <992 hộp chạm THẬT (kể cả pseudo nới ra) ≥44×44.
  BT-4  PRIMARY   mỗi action area tối đa MỘT primary.
  BT-5  SEMANTIC  icon-only phải có tên đọc được; disabled không nhận focus;
                  focus-visible có ring nhìn thấy (tab-walk thật, không đọc CSS).
  BT-6  LOADING   thêm `.is-loading` không được đổi bề rộng nút.

Ranh giới với hàng xóm: `wj_measure.py` đo khung card, `wj_datalist`/`wj_listcard`
đo danh sách, `wj_filterbar` đo hành vi lọc — không cái nào nhìn thấy nút.

Route nằm trong MIGRATED mà không có `.wj-btn` nào ⇒ in **CHƯA MIGRATE** và tính
là vi phạm: đó là cách chặn bảng "Pass rỗng" đã trả giá ở D4/E5c.

    python3 scripts/qa/wj_button.py --base http://127.0.0.1:8090 \
        --portal-login em.hcm [--routes ...] [--breakpoints 360 390 992 1024 1440] [--json out.json]
"""
import argparse
import json
from urllib.parse import unquote
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from wj_measure import login  # noqa: E402

BREAKPOINTS = [360, 390, 992, 1024, 1440]

# Route ĐÃ migrate sang atom — cộng dồn qua E6a → E6b → E6c.
# Route ở đây phải THỰC SỰ dựng call site đã migrate. Biến thể `?q=…` là cố ý:
# khối rỗng ("Xóa lọc" / "Tải lại") chỉ dựng khi bộ lọc không khớp gì, đo route
# trần thì màn có dữ liệu và bảng ra 0 nút — đúng bẫy "Pass rỗng" của D4/E5c.
NO_MATCH = 'zzzq-khong-khop'
MIGRATED = [
    # E6a
    '/portal/support',
    '/portal/support/new',
    '/portal/return',
    '/portal/return/new',
    '/portal/notification',
    # E6b1
    '/portal/delivery',
    '/portal/delivery?q=' + NO_MATCH,
    '/portal/knowledge?keyword=' + NO_MATCH,
    '@knowledge_detail',
    '/portal/info-request',
    '@info_request_detail',
    '/portal/info-request/new',
    '/portal/purchase-history?q=' + NO_MATCH,
    '/portal/debt',
    '/portal/debt/pay',
    '/portal/franchises',
    '/portal/franchises/3/profile',
]

# Route đo kèm để bắt hồi quy (chưa migrate hoặc không có nút hành động nào:
# chỉ in kiểm kê, không tính vi phạm).
WATCH = [
    '/portal',
    # /my/franchises dựng bằng khung portal gốc Odoo (`portal.portal_layout`),
    # CSS design system không nạp ở đó ⇒ boundary, chỉ kiểm kê.
    '/my/franchises',
    '/portal/knowledge',
    '/portal/purchase-history',
    '/portal/debt/payment-history',
    '/portal/franchise-information',
    '/portal/order',
    '/portal/order/cart',
]

# Màn chi tiết phụ thuộc dữ liệu (slug bài viết, id yêu cầu). Ghi cứng vào sổ thì
# sổ chết theo bộ dữ liệu mẫu — E6b1 đã dính đúng thế: slug ghi cứng trỏ vào bài
# đã lưu trữ, route chuyển hướng, bảng ra "Pass rỗng". Dò từ trang danh sách.
DYNAMIC = {
    '@knowledge_detail': ('/portal/knowledge', '/portal/knowledge/'),
    '@info_request_detail': ('/portal/info-request', '/portal/info-request/'),
}


def resolve_dynamic(page, base, routes):
    """Thay placeholder bằng URL thật; không dò ra thì giữ nguyên để báo lỗi to."""
    for key, (list_route, prefix) in DYNAMIC.items():
        if key not in routes and key not in MIGRATED:
            continue
        page.goto(base + list_route, wait_until='load')
        page.wait_for_timeout(300)
        hrefs = page.eval_on_selector_all(
            'a[href^="%s"]' % prefix, 'els => els.map(e => e.getAttribute("href"))')
        hit = next((h for h in hrefs
                    if h and '?' not in h and '/attachment/' not in h
                    and not h.rstrip('/').endswith('/new')
                    and h.rstrip('/') != prefix.rstrip('/')), None)
        if not hit:
            print('!! %s: không dò được màn chi tiết từ %s' % (key, list_route))
            continue
        for seq in (MIGRATED, routes):
            if key in seq:
                seq[seq.index(key)] = hit
        print('   %s → %s' % (key, hit))


PROBE = r"""
(args) => {
  const px = v => Math.round(parseFloat(v) * 100) / 100;
  const vis = el => {
    const r = el.getBoundingClientRect();
    return r.width > 0 && r.height > 0 && getComputedStyle(el).visibility !== 'hidden';
  };

  // Boundary BA liệt kê: Pagination · BottomNavigation · nút tìm của FilterBar ·
  // QuantityStepper · BackPageHeader. Cộng màn Khảo sát (code anh Thái).
  // `wj-filter*` là CẢ thanh lọc, không riêng nút tìm: FB-08 cho Filter giữ
  // 42/38/32 và nói rõ ưu tiên hơn size mặc định của CMP-BTN-001.
  const BOUNDARY = ['wj-pagination', 'wujia-mhome-bottomnav', 'wujia-msheet',
                    'wj-filter', 'wj-pc-filterbar', 'wujia-mcart-step', 'wujia-morder-mstep',
                    'wj-pc-cart-step', 'wj-pc-stepper', 'wujia-mcart-stepper',
                    'wujia-morder-mstepper', 'wj-page-header__back',
                    'wujia-header-icon', 'wj-pc-navactions',
                    'wj-inspection', 'wujia-minspection'];
  const clsOf = el => (el.className || '').toString().split(/\s+/).filter(Boolean);
  // E6b1: nhận theo NGỮ CẢNH, không theo tên họ class. Trong cùng một màn Công
  // nợ, `wj-pc-btn--primary` vừa là nút *Tìm kiếm* của thanh lọc (FB-08 giữ 42)
  // vừa là nút *Thanh toán số còn lại* (CMP-BTN-001 về 40): tên class không
  // phân biệt được hai vai trò, chỗ đứng trong cây DOM thì có.
  const inFilter = el => {
    for (let n = el; n && n.nodeType === 1; n = n.parentElement) {
      if (clsOf(n).some(c => /(^|-)filter(-|$)/.test(c) || /(^|-)search$/.test(c))) return true;
      if (n.tagName === 'FORM' && /filter|search/i.test(n.className || '')) return true;
    }
    return false;
  };
  const isBoundary = el => {
    if (inFilter(el)) return true;
    for (let n = el; n && n.nodeType === 1; n = n.parentElement) {
      if (clsOf(n).some(c => BOUNDARY.some(b => c === b || c.startsWith(b + '-')))) return true;
    }
    return false;
  };

  // Hộp chạm thật: rect của nút, nới ra theo pseudo tuyệt đối có inset âm
  // (cách tăng vùng chạm mà KHÔNG phình visual — spec BA size mobile 36 + chạm 44).
  const hitBox = el => {
    const r = el.getBoundingClientRect();
    let t = r.top, l = r.left, rg = r.right, b = r.bottom;
    for (const p of ['::before', '::after']) {
      const cs = getComputedStyle(el, p);
      if (cs.content === 'none' || cs.position !== 'absolute') continue;
      const num = v => (v === 'auto' ? null : parseFloat(v));
      const it = num(cs.top), il = num(cs.left), ir = num(cs.right), ib = num(cs.bottom);
      if (it !== null && it < 0) t = Math.min(t, r.top + it);
      if (il !== null && il < 0) l = Math.min(l, r.left + il);
      if (ir !== null && ir < 0) rg = Math.max(rg, r.right - ir);
      if (ib !== null && ib < 0) b = Math.max(b, r.bottom - ib);
    }
    // Nút nằm trong <label>/<a> bọc ngoài thì vùng chạm là cái bọc (khuôn E4a).
    const wrap = el.parentElement;
    if (wrap && ['LABEL', 'A'].includes(wrap.tagName) && wrap.children.length === 1) {
      const w = wrap.getBoundingClientRect();
      t = Math.min(t, w.top); l = Math.min(l, w.left);
      rg = Math.max(rg, w.right); b = Math.max(b, w.bottom);
    }
    return { w: px(rg - l), h: px(b - t) };
  };

  const AREA = 'form, .wj-pc-form-actions, .wj-lc__actions, .wj-empty-state, ' +
               '.wj-page-header__actions, .wj-card-header__actions, .wj-filter-card, ' +
               '[data-wj-action-area]';
  const areaKey = el => {
    const a = el.closest(AREA);
    if (!a) return 'page';
    const c = clsOf(a).filter(x => !/^(is-|has-|d-|row|col)/.test(x)).slice(0, 2).join('.');
    return (c || a.tagName.toLowerCase()) + '#' + (a.dataset.wjArea || '');
  };

  const accName = el => (el.getAttribute('aria-label') || el.getAttribute('title')
    || (el.querySelector('.sr-only, .visually-hidden') || {}).textContent
    || el.textContent || '').replace(/\s+/g, ' ').trim();

  const SEL = 'button, input[type=submit], input[type=button], a[class*="btn"], ' +
              '.wj-btn, .wj-iconbtn';
  const seen = new Set();
  const items = [];
  document.querySelectorAll(SEL).forEach(el => {
    if (seen.has(el) || !vis(el) || isBoundary(el)) return;
    seen.add(el);
    const cs = getComputedStyle(el);
    const cls = clsOf(el);
    const has = c => cls.includes(c);
    const size = has('wj-btn--sm') || has('wj-iconbtn--sm') ? 'sm'
               : has('wj-btn--lg') ? 'lg' : 'md';
    // phải soi CẢ hai họ: icon button cũng mang variant (bẫy đã dính một lần —
    // chỉ dò `wj-btn--` thì 120 icon đọc ra null, luật ≤1 Primary hụt).
    const variant = ['primary', 'secondary', 'outline', 'danger', 'ghost']
      .find(v => has('wj-btn--' + v) || has('wj-iconbtn--' + v)) || null;
    const hb = hitBox(el);
    const txt = (el.textContent || '').replace(/\s+/g, ' ').trim();
    items.push({
      tag: el.tagName.toLowerCase(),
      cls: cls.filter(c => /btn|wj-cta|action/.test(c)).join(' ') || cls.slice(0, 2).join(' '),
      atom: has('wj-btn') || has('wj-iconbtn'),
      icon: has('wj-iconbtn'),
      size: size, variant: variant, area: areaKey(el),
      h: px(cs.height), w: px(cs.width),
      r: px(cs.borderTopLeftRadius), fs: px(cs.fontSize), fw: cs.fontWeight,
      lh: cs.lineHeight === 'normal' ? null : px(cs.lineHeight),
      gap: cs.columnGap === 'normal' ? 0 : px(cs.columnGap),
      hitW: hb.w, hitH: hb.h,
      text: txt.slice(0, 40),
      name: accName(el).slice(0, 40),
      disabled: el.disabled === true || el.getAttribute('aria-disabled') === 'true',
      tabindex: el.getAttribute('tabindex'),
      href: el.tagName === 'A' ? (el.getAttribute('href') || '') : null,
    });
  });

  // BT-6: `.is-loading` không được đổi bề rộng (spec: giữ width + chặn submit lặp).
  const loading = [];
  if (args.loading) {
    document.querySelectorAll('.wj-btn').forEach(el => {
      if (!vis(el) || isBoundary(el)) return;
      const before = px(el.getBoundingClientRect().width);
      el.classList.add('is-loading');
      const after = px(el.getBoundingClientRect().width);
      el.classList.remove('is-loading');
      loading.push({ text: (el.textContent || '').trim().slice(0, 24), before: before, after: after });
    });
  }
  return { items: items, loading: loading };
}
"""

# Bảng số của BA (dòng 40 tab `UI Component`, BA Confirmed 26/08/2026).
SIZE_PC = {'sm': 32, 'md': 40, 'lg': 46}
SIZE_M = {'sm': 36, 'md': 44, 'lg': 48}
RADIUS = {'sm': 8, 'md': 12, 'lg': 12}
TYPO = {'sm': (13, 18, 600), 'md': (14, 20, 700), 'lg': (15, 22, 700)}
TOL = 0.6
# Họ nút cũ — còn thấy ở route đã migrate là chưa dọn sạch.
LEGACY = ('wj-pc-btn', 'btn-primary', 'btn-secondary', 'btn-outline', 'btn-sm', 'btn-xs',
          'btn-success', 'btn-danger', 'btn-light', 'btn-block', 'wujia-mexam-btn',
          'wj-cta-btn', 'wujia-mreturn-btn', 'btn-add-cart', 'wujia-morder-add-btn')


def check(route, width, data, migrated):
    """Trả danh sách vi phạm dạng (mã, mô tả)."""
    bad = []
    items = data['items']
    pc = width >= 992
    table = SIZE_PC if pc else SIZE_M
    atoms = [i for i in items if i['atom']]

    # Màn danh sách mobile không có nút nào (mọi thao tác nằm trong ListCard/
    # boundary) — đó là sự thật, không phải lỗi. Chỉ báo CHƯA MIGRATE khi có
    # action thật mà chưa có atom nào; route không atom ở MỌI khổ do `run` bắt.
    if migrated and items and not atoms:
        bad.append(('CHƯA MIGRATE', '%d action, 0 phần tử .wj-btn' % len(items)))
        return bad

    for it in items:
        tag = '%s "%s"' % (it['cls'] or it['tag'], it['text'] or it['name'])
        if not it['atom']:
            if migrated and any(l in it['cls'] for l in LEGACY):
                bad.append(('HỌ CŨ', '%s còn class cũ' % tag))
            continue
        if it['icon']:
            want = (32 if pc else 36) if it['size'] == 'sm' else (40 if pc else 44)
            if abs(it['h'] - want) > TOL or abs(it['w'] - want) > TOL:
                bad.append(('SIZE', '%s %.1f×%.1f ≠ %d×%d' % (tag, it['w'], it['h'], want, want)))
            if not it['name']:
                bad.append(('TÊN ĐỌC ĐƯỢC', '%s icon-only không có aria-label/title' % tag))
        else:
            want = table[it['size']]
            if abs(it['h'] - want) > TOL:
                bad.append(('SIZE', '%s cao %.1f ≠ %d (%s/%s)'
                            % (tag, it['h'], want, it['size'], 'PC' if pc else 'mobile')))
            fs, lh, fw = TYPO[it['size']]
            if abs(it['fs'] - fs) > TOL:
                bad.append(('TYPO', '%s font %.1f ≠ %d' % (tag, it['fs'], fs)))
            if int(it['fw']) != fw:
                bad.append(('TYPO', '%s weight %s ≠ %d' % (tag, it['fw'], fw)))
            if it['lh'] is not None and abs(it['lh'] - lh) > TOL:
                bad.append(('TYPO', '%s line-height %.1f ≠ %d' % (tag, it['lh'], lh)))
        if not it['variant']:
            bad.append(('VARIANT', '%s là atom nhưng không mang variant nào' % tag))
        if abs(it['r'] - RADIUS[it['size']]) > TOL:
            bad.append(('RADIUS', '%s radius %.1f ≠ %d' % (tag, it['r'], RADIUS[it['size']])))
        if not pc and (it['hitH'] < 44 - TOL or it['hitW'] < 44 - TOL):
            bad.append(('CHẠM', '%s hộp chạm %.1f×%.1f < 44' % (tag, it['hitW'], it['hitH'])))
        if it['tag'] == 'a' and not it['href']:
            bad.append(('SEMANTIC', '%s là <a> không href — hành động tại chỗ phải là <button>' % tag))

    areas = {}
    for it in atoms:
        if it['variant'] == 'primary':
            areas.setdefault(it['area'], []).append(it['text'] or it['name'])
    for area, names in areas.items():
        if len(names) > 1:
            bad.append(('PRIMARY', '%s có %d primary: %s' % (area, len(names), ', '.join(names))))

    for lo in data.get('loading', []):
        if abs(lo['after'] - lo['before']) > TOL:
            bad.append(('LOADING', '"%s" đổi bề rộng %.1f → %.1f' % (lo['text'], lo['before'], lo['after'])))
    return bad


def keyboard_probe(page, items_selector='.wj-btn, .wj-iconbtn'):
    """BT-5 tab-walk thật: mỗi atom phải nhận được focus và có ring nhìn thấy;
    nút disabled thì KHÔNG được nhận focus."""
    return page.evaluate(r"""
    (sel) => {
      const out = {noRing: [], focusableDisabled: [], n: 0};
      document.querySelectorAll(sel).forEach(el => {
        const r = el.getBoundingClientRect();
        if (!r.width || !r.height) return;
        out.n += 1;
        const dis = el.disabled === true;
        el.focus();
        const got = document.activeElement === el;
        if (dis && got) { out.focusableDisabled.push((el.textContent || '').trim().slice(0, 24)); return; }
        if (dis) return;
        const cs = getComputedStyle(el);
        const ring = (parseFloat(cs.outlineWidth) >= 1.5 && cs.outlineStyle !== 'none')
                  || (cs.boxShadow && cs.boxShadow !== 'none');
        if (!got || !ring) out.noRing.push((el.textContent || '').trim().slice(0, 24));
        el.blur();
      });
      return out;
    }
    """, items_selector)


def run(args):
    from playwright.sync_api import sync_playwright
    result = {'base': args.base, 'login': args.portal_login, 'routes': {}}
    total_bad = 0
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        ctx = browser.new_context(viewport={'width': 1440, 'height': 900})
        page = ctx.new_page()
        errors = []
        page.on('pageerror', lambda e: errors.append(str(e)))
        login(page, args.base, args.portal_login, args.password)
        resolve_dynamic(page, args.base, args.routes)

        for route in args.routes:
            result['routes'][route] = {}
            migrated = route in MIGRATED
            for w in args.breakpoints:
                page.set_viewport_size({'width': w, 'height': 900})
                resp = page.goto(args.base + route, wait_until='load')
                page.wait_for_timeout(args.settle)
                landed = unquote(page.url.split(args.base)[-1].split('?')[0])
                if landed.rstrip('/') != unquote(route.split('?')[0]).rstrip('/'):
                    print('!! %-28s @%-5d CHUYỂN HƯỚNG → %s' % (route, w, landed))
                    result['routes'][route][str(w)] = {'redirect': landed}
                    total_bad += 1
                    continue
                data = page.evaluate(PROBE, {'loading': bool(args.loading)})
                kb = keyboard_probe(page) if args.keyboard else None
                bad = check(route, w, data, migrated)
                if kb:
                    if kb['noRing']:
                        bad.append(('FOCUS', '%d nút không nhận focus/không có ring: %s'
                                    % (len(kb['noRing']), ', '.join(kb['noRing'][:3]))))
                    if kb['focusableDisabled']:
                        bad.append(('DISABLED', 'nút disabled vẫn focus được: %s'
                                    % ', '.join(kb['focusableDisabled'][:3])))
                data['violations'] = bad
                data['kb'] = kb
                result['routes'][route][str(w)] = data
                total_bad += len(bad)
                atoms = sum(1 for i in data['items'] if i['atom'])
                print('%s%-28s @%-5d action=%-3d atom=%-3d vi phạm=%d'
                      % ('OK ' if not bad else '!! ', route, w, len(data['items']), atoms, len(bad)))
                for code, msg in bad:
                    print('      · %-13s %s' % (code, msg))
        browser.close()

    co_desktop = any(int(w) >= 992 for w in args.breakpoints)
    for route, by_w in result['routes'].items():
        if route not in MIGRATED:
            continue
        # Chỉ là Pass rỗng khi route CÓ action mà không khổ nào ra atom; màn danh
        # sách ở khổ hẹp vốn 0 nút hành động nên "0 atom" ở đó là đúng, không phải lỗi.
        co_action = any(d.get('items') for d in by_w.values())
        co_atom = any(sum(1 for i in d.get('items', []) if i['atom']) for d in by_w.values())
        if not co_action:
            # Route ghi trong sổ mà KHÔNG dựng nổi một nút hành động nào: hoặc sổ ghi
            # sai route, hoặc dữ liệu mẫu rỗng. Cả hai đều khiến bảng "Pass" vô nghĩa.
            # Chỉ kết luận khi lượt đo CÓ khổ desktop: màn danh sách vốn không có nút
            # hành động ở khổ hẹp, chạy riêng 720/512 mà tính vi phạm là báo oan.
            if not co_desktop:
                print('   %-28s bỏ qua (lượt đo không có khổ ≥992)' % route)
                continue
            print('!! %-28s KHÔNG CÓ NÚT HÀNH ĐỘNG NÀO (sổ MIGRATED sai route / thiếu dữ liệu mẫu)'
                  % route)
            total_bad += 1
        elif not co_atom:
            print('!! %-28s KHÔNG CÓ ATOM Ở BẤT KỲ KHỔ NÀO (bảng Pass rỗng)' % route)
            total_bad += 1
    result['jsErrors'] = errors
    if errors:
        print('\n!! %d lỗi JS: %s' % (len(errors), errors[:2]))
    print('\nTỔNG: %d vi phạm · %d lỗi JS' % (total_bad, len(errors)))
    if args.json:
        json.dump(result, open(args.json, 'w'), ensure_ascii=False, indent=1)
        print('→ %s' % args.json)
    return 1 if (total_bad or errors) else 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--base', default='http://127.0.0.1:8090')
    ap.add_argument('--portal-login', default='em.hcm')
    ap.add_argument('--password', default='wujia@test123')
    ap.add_argument('--routes', nargs='*', default=MIGRATED + WATCH)
    ap.add_argument('--breakpoints', nargs='*', type=int, default=BREAKPOINTS)
    ap.add_argument('--settle', type=int, default=450)
    ap.add_argument('--keyboard', action='store_true', default=True)
    ap.add_argument('--no-keyboard', dest='keyboard', action='store_false')
    ap.add_argument('--loading', action='store_true', default=True)
    ap.add_argument('--json')
    sys.exit(run(ap.parse_args()))


if __name__ == '__main__':
    main()
