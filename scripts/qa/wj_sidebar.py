#!/usr/bin/env python3
"""Thước đo SidebarNavigation CMP-SN-001 (UI-SIDEBAR-001) — E8b + E8c (avatar, sheet, chuông).

    python scripts/qa/wj_sidebar.py --base http://127.0.0.1:8090 --login em.hcm --json out.json
    python scripts/qa/wj_sidebar.py --login cuong.staff --password demo123 --role staff   # không Công nợ/Báo cáo
    python scripts/qa/wj_sidebar.py --login dung.multi --store 1 --role mixed            # staff ở cửa hàng đang chọn,
                                                                                        # manager nơi khác: có Báo cáo

Kiểm (mỗi dòng lệch = 1 vi phạm, in cuối cùng; exit 1 nếu có):
  SN-1 WIDTH    ≥1200: sidebar 264, navbar left 264, content margin-left 264
  SN-2 BRAND    vùng brand cao 88, logo ≤160×64
  SN-3 ORDER    mục + nhóm đúng thứ tự BA, nhóm rỗng không hiện tiêu đề
  SN-4 ITEM     cao 44 · đệm 10/12 · bo 10 · icon 20 · gap 12 · chữ 15/22/500 ở mọi state
  SN-5 ACTIVE   route → đúng 1 mục sáng + aria-current=page (hoặc 0 mục với route không có mục)
  SN-6 DRAWER   992–1199: đóng khi tải; hamburger bấm được; mở/đóng bằng hamburger · nút Đóng ·
                Escape · backdrop; focus trả về hamburger
  SN-7 HIDDEN   <992: sidebar display:none
  SN-8 A11Y     hamburger <button> có aria-label + aria-controls; đúng 1 .sidenav-overlay
  SN-9 OVERFLOW không tràn ngang
  E8c (--only acct chạy riêng phần này):
  SN-10 ACCT    menu avatar PC (1440) + mobile (390) cùng thứ tự BA: Thông tin tài khoản · Đổi mật khẩu ·
                Ngôn ngữ · [cửa hàng/vai trò · Đổi cửa hàng (chỉ khi >1 cửa hàng) · Hồ sơ cửa hàng] · Đăng xuất;
                nút avatar có aria-label/haspopup; nút Ngôn ngữ vẫn trên header (CMP-GH-001); chữ các mục thẳng hàng
  SN-11 SHEET   sheet "Thêm" không có Hồ sơ cửa hàng / Tài khoản; Công nợ + Báo cáo theo quyền như sidebar
  SN-12 BELL    chuông PC: aria-controls + aria-expanded đổi theo popup; Escape đóng + trả focus về chuông
  SN-13 STORE   "Đổi cửa hàng" mở modal chọn cửa hàng; "Hồ sơ cửa hàng" sáng ở hồ sơ + info-request
  SN-14 KEYS    nút avatar PC + mobile: Enter mở menu, Escape đóng, focus về nút, aria-expanded=false
"""
import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from playwright.sync_api import sync_playwright  # noqa: E402
from wj_measure import login  # noqa: E402

GOLDEN = [
    ('nav_header_main', None), ('nav_item_home', None), ('nav_item_order', None),
    ('nav_item_delivery', None), ('nav_item_history', None),
    ('nav_header_finance', None), ('nav_item_debt', 'mgr_active'), ('nav_item_return', None),
    ('nav_header_ops', None), ('nav_item_exam', None), ('nav_item_knowledge', None),
    ('nav_item_support', None), ('nav_item_report', 'mgr_any'), ('nav_item_inspection', 'optional'),
]
LABELS = {
    'nav_item_home': 'Trang chủ', 'nav_item_order': 'Đặt hàng', 'nav_item_delivery': 'Giao hàng',
    'nav_item_history': 'Lịch sử đặt hàng', 'nav_item_debt': 'Công nợ & thanh toán',
    'nav_item_return': 'Đổi trả / Bù hàng', 'nav_item_exam': 'Đăng ký thi', 'nav_item_knowledge': 'Kiến thức',
    'nav_item_support': 'Hỗ trợ', 'nav_item_report': 'Báo cáo', 'nav_item_inspection': 'Khảo sát',
}
# route → id mục phải sáng (None = không mục nào). '@x' = dò id thật từ trang danh sách.
ACTIVE = [
    ('/portal', 'nav_item_home'), ('/portal/order', 'nav_item_order'), ('/portal/order/cart', 'nav_item_order'),
    ('@/portal/order|/portal/order/product/\\d+', 'nav_item_order'),
    ('/portal/purchase-history', 'nav_item_history'),
    ('@/portal/purchase-history|/portal/purchase-history/\\d+', 'nav_item_history'),
    ('/portal/delivery', 'nav_item_delivery'), ('@/portal/delivery|/portal/delivery/\\d+', 'nav_item_delivery'),
    ('/portal/debt', 'nav_item_debt'), ('/portal/debt/payment-history', 'nav_item_debt'),
    ('/portal/return', 'nav_item_return'), ('/portal/return/new', 'nav_item_return'),
    ('@/portal/return|/portal/return/\\d+', 'nav_item_return'),
    ('/portal/notification', None), ('@/portal/notification|/portal/notification/\\d+', None),
    ('/portal/knowledge', 'nav_item_knowledge'),
    ('/portal/support', 'nav_item_support'), ('/portal/support/new', 'nav_item_support'),
    ('@/portal/support|/portal/support/\\d+', 'nav_item_support'),
    ('/portal/exam', 'nav_item_exam'), ('/portal/exam/register', 'nav_item_exam'),
    ('/portal/reports/orders', 'nav_item_report'),
    ('/portal/inspection', 'nav_item_inspection'),
    ('/portal/info-request', None), ('/portal/info-request/new', None),
    ('/portal/profile', None), ('/portal/change-password', None), ('/portal/franchise-information', None),
]
WIDTHS = (1920, 1440, 1280, 1200, 1199, 1024, 992, 991, 390)

SHEET = ['Công nợ & thanh toán', 'Đổi trả / Bù hàng', 'Đăng ký thi', 'Kiến thức', 'Hỗ trợ', 'Báo cáo', 'Khảo sát']

ACCT = r"""
(sel) => {
  const m = document.querySelector(sel);
  if (!m) return null;
  const out = [];
  const text = el => (el.innerText || el.textContent || '').trim().replace(/\s+/g, ' ');
  const tx = a => {
    const n = [...a.childNodes].find(c => c.nodeType === 3 && c.textContent.trim()) || a.querySelector('span');
    if (!n) return null;
    if (n.nodeType === 3) { const r = document.createRange(); r.selectNodeContents(n); return r.getBoundingClientRect().x; }
    return n.getBoundingClientRect().x;
  };
  for (const c of m.children) {
    if (c.classList.contains('dropdown-divider') || /menu__head|menu-head/.test(c.className)) continue;
    if (c.classList.contains('wj-acct-menu__group')) {
      out.push({k: 'LANG', n: c.querySelectorAll('a[href^="/portal/set-lang/"]').length,
                cur: c.querySelectorAll('a[aria-current="true"]').length,
                x: [...c.querySelectorAll('a')].map(tx)});
    } else if (c.classList.contains('wj-acct-menu__store')) {
      out.push({k: 'STORE', label: text(c)});
    } else if (c.tagName === 'A') {
      out.push({k: text(c), active: c.classList.contains('is-active'), cur: c.getAttribute('aria-current'),
                action: c.dataset.action || null, x: tx(c)});
    } else out.push({k: '?' + c.tagName + '.' + c.className});
  }
  return out;
}
"""

TOGGLES = r"""
() => {
  const pc = document.querySelector('.wj-pc-navactions .dropdown-user-link');
  const mo = document.querySelector('.wujia-mheader .dropdown-user > a');
  const bell = document.querySelector('[data-wj-noti-bell]');
  const a = el => el ? {label: el.getAttribute('aria-label'), pop: el.getAttribute('aria-haspopup'),
                        exp: el.getAttribute('aria-expanded'), ctl: el.getAttribute('aria-controls')} : null;
  return {pc: a(pc), mobile: a(mo), bell: a(bell),
          langPc: !!document.querySelector('.wj-pc-navactions li.dropdown-language'),
          langMobile: !!document.querySelector('.wujia-mheader .dropdown-language'),
          // sheet đóng = ẩn ⇒ innerText rỗng; lấy text node trực tiếp của tiêu đề (bỏ badge đếm)
          sheet: [...document.querySelectorAll('.wujia-msheet-list > a')].map(x => {
            const t = x.querySelector('.wujia-msheet-item-title') || x;
            const own = [...t.childNodes].filter(c => c.nodeType === 3).map(c => c.textContent).join('').trim();
            return (own || (t.querySelector('span:not(.wujia-msheet-item-badge)') || t).textContent)
                     .trim().replace(/\s+/g, ' ');
          }),
          focus: document.activeElement ? document.activeElement.getAttribute('data-wj-noti-bell') : null,
          modal: !!document.querySelector('.wujia-store-overlay--show')};
}
"""


def expected_acct(multi, has_store):
    out = ['Thông tin tài khoản', 'Đổi mật khẩu', 'LANG']
    if has_store:
        out.append('STORE')
        if multi:
            out.append('Đổi cửa hàng')
        out.append('Hồ sơ cửa hàng')
    return out + ['Đăng xuất']


def check_acct(v, page, base, a):
    """SN-10…14 — menu avatar, sheet Thêm, chuông, Đổi cửa hàng, bàn phím."""
    multi = bool(a.store)
    res = {}
    for w, sel, opener in ((1440, '.wj-pc-acct-menu', '.wj-pc-navactions .dropdown-user-link'),
                           (390, '.wujia-mheader-menu', '.wujia-mheader .dropdown-user > a')):
        page.set_viewport_size({'width': w, 'height': 900 if w > 991 else 844})
        goto(page, base, '/portal/franchise-information', a.settle)
        landed = page.url.replace(base, '').split('?')[0]
        page.click(opener)
        page.wait_for_timeout(350)
        items = page.evaluate(ACCT, sel)
        tg = page.evaluate(TOGGLES)
        res[w] = {'items': items, 'toggles': tg, 'landed': landed}
        keys = [i['k'] for i in items]
        exp = expected_acct(multi, 'STORE' in keys or a.role != 'none')
        if keys != exp:
            v.append(f'SN-10 {w} thứ tự avatar {keys} ≠ {exp}')
        lang = next((i for i in items if i['k'] == 'LANG'), None)
        if not lang or lang['n'] < 1 or lang['cur'] != 1:
            v.append(f'SN-10 {w} nhóm Ngôn ngữ {lang}')
        xs = [round(i['x']) for i in items if i.get('x') and not isinstance(i['x'], list)]
        xs += [round(x) for i in items if isinstance(i.get('x'), list) for x in i['x'] if x]
        if xs and max(xs) - min(xs) > 1:
            v.append(f'SN-10 {w} chữ các mục lệch hàng {sorted(set(xs))}')
        t = tg['pc'] if w == 1440 else tg['mobile']
        if not t or not t['label'] or t['pop'] != 'true' or t['exp'] != 'true':
            v.append(f'SN-10 {w} nút avatar aria {t}')
        if not (tg['langPc'] and tg['langMobile']):
            v.append(f'SN-10 nút Ngôn ngữ trên header PC={tg["langPc"]} mobile={tg["langMobile"]}')
        if landed.endswith('/portal/franchise-information'):
            hs = next((i for i in items if i['k'] == 'Hồ sơ cửa hàng'), None)
            if hs and not (hs['active'] and hs['cur'] == 'page'):
                v.append(f'SN-13 {w} Hồ sơ cửa hàng không sáng ở route của nó {hs}')
        page.keyboard.press('Escape')
        page.wait_for_timeout(200)
        # SN-14 bàn phím: Enter mở, Escape đóng + focus về nút avatar
        page.focus(opener)
        page.keyboard.press('Enter')
        page.wait_for_timeout(300)
        kb_open = page.evaluate('(s) => { const m = document.querySelector(s); return !!m && m.classList.contains("show") '
                                '&& m.getBoundingClientRect().height > 0; }', sel)
        page.keyboard.press('Escape')
        page.wait_for_timeout(250)
        kb = page.evaluate('([s, o]) => ({open: document.querySelector(s).classList.contains("show"), '
                           'focus: document.activeElement === document.querySelector(o), '
                           'exp: document.querySelector(o).getAttribute("aria-expanded")})', [sel, opener])
        res[w]['keyboard'] = {'enterOpens': kb_open, **kb}
        if not kb_open or kb['open'] or not kb['focus'] or kb['exp'] != 'false':
            v.append(f'SN-14 {w} bàn phím avatar {res[w]["keyboard"]}')

    # SN-11 sheet
    page.set_viewport_size({'width': 390, 'height': 844})
    goto(page, base, '/portal/order', a.settle)
    sheet = page.evaluate(TOGGLES)['sheet']
    res['sheet'] = sheet
    exp = [x for x in SHEET
           if not (x == 'Công nợ & thanh toán' and a.role in ('staff', 'mixed'))
           and not (x == 'Báo cáo' and a.role == 'staff')
           and not (x == 'Khảo sát' and 'Khảo sát' not in sheet)]
    if sheet != exp:
        v.append(f'SN-11 sheet {sheet} ≠ {exp}')

    # SN-12 chuông
    page.set_viewport_size({'width': 1440, 'height': 900})
    goto(page, base, '/portal/order', a.settle)
    b0 = page.evaluate(TOGGLES)['bell']
    page.route('**/portal/notification/recent', lambda r: r.fulfill(
        status=200, content_type='application/json',
        body='{"jsonrpc":"2.0","id":1,"result":{"notifications":[],"total_unread":0}}'))
    page.click('[data-wj-noti-bell]')
    page.wait_for_timeout(300)
    b1 = page.evaluate(TOGGLES)['bell']
    page.keyboard.press('Escape')
    page.wait_for_timeout(200)
    t2 = page.evaluate(TOGGLES)
    res['bell'] = [b0, b1, t2['bell'], t2['focus']]
    if not b0 or b0['ctl'] != 'wj-noti-popup' or b0['exp'] != 'false' or b1['exp'] != 'true' \
            or t2['bell']['exp'] != 'false' or t2['focus'] != '1':
        v.append(f'SN-12 chuông {res["bell"]}')

    # SN-13 Đổi cửa hàng + info-request
    if multi:
        page.click('.wj-pc-navactions .dropdown-user-link')
        page.wait_for_timeout(300)
        page.click('.wj-pc-acct-menu [data-action="open-store-picker"]')
        page.wait_for_timeout(400)
        if not page.evaluate(TOGGLES)['modal']:
            v.append('SN-13 Đổi cửa hàng không mở modal')
    goto(page, base, '/portal/info-request', a.settle)
    if page.url.replace(base, '').split('?')[0].endswith('/portal/info-request'):
        items = page.evaluate(ACCT, '.wj-pc-acct-menu')
        hs = next((i for i in items if i['k'] == 'Hồ sơ cửa hàng'), None)
        if hs and not hs['active']:
            v.append('SN-13 info-request không sáng Hồ sơ cửa hàng')
    return res

SHELL = r"""
() => {
  const r = el => { if (!el) return null; const b = el.getBoundingClientRect();
    return {x: +b.x.toFixed(1), y: +b.y.toFixed(1), w: +b.width.toFixed(1), h: +b.height.toFixed(1)}; };
  const mm = document.querySelector('#wj-main-menu');
  const s = mm ? getComputedStyle(mm) : null;
  const rect = r(mm);
  const shown = !!(mm && s.display !== 'none' && s.visibility !== 'hidden' && s.opacity !== '0'
                   && rect.w > 0 && rect.x + rect.w > 1);
  const nav = document.querySelector('.header-navbar.wujia-navbar');
  const content = document.querySelector('.app-content.content');
  const brand = mm && mm.querySelector('.wj-sidebar__brand');
  const logo = brand && brand.querySelector('img');
  const toggle = document.querySelector('.wj-menu-toggle');
  const tr = r(toggle);
  let covered = null;
  if (toggle && tr.w > 0) {
    const top = document.elementFromPoint(tr.x + tr.w / 2, tr.y + tr.h / 2);
    covered = !toggle.contains(top);
  }
  const ovs = [...document.querySelectorAll('.sidenav-overlay')];
  return {
    vw: innerWidth, scrollW: document.documentElement.scrollWidth,
    shown, display: s && s.display, rect,
    navLeft: nav ? getComputedStyle(nav).left : null,
    contentML: content ? getComputedStyle(content).marginLeft : null,
    brand: r(brand), logo: r(logo),
    toggle: toggle ? {tag: toggle.tagName.toLowerCase(), label: toggle.getAttribute('aria-label'),
      controls: toggle.getAttribute('aria-controls'), expanded: toggle.getAttribute('aria-expanded'),
      visible: tr.w > 0, covered} : null,
    overlays: ovs.length, overlayShown: ovs.some(o => getComputedStyle(o).display !== 'none'),
    focus: document.activeElement ? (document.activeElement.className || document.activeElement.tagName) : null,
  };
}
"""

ITEMS = r"""
() => {
  const ul = document.querySelector('#main-menu-navigation');
  if (!ul) return [];
  const px = v => Math.round(parseFloat(v) * 10) / 10;
  return [...ul.children].filter(li => getComputedStyle(li).display !== 'none').map(li => {
    const a = li.querySelector(':scope > a');
    const ic = a && a.querySelector('i');
    const lab = a && a.querySelector('.menu-title');
    const s = a && getComputedStyle(a);
    const before = a && getComputedStyle(a, '::before');
    return {
      id: li.id, header: li.classList.contains('navigation-header'),
      label: (li.innerText || '').trim().replace(/\s+/g, ' '), active: li.classList.contains('active'),
      ariaCurrent: a ? a.getAttribute('aria-current') : null,
      a: s ? {h: px(a.getBoundingClientRect().height), pt: px(s.paddingTop), pl: px(s.paddingLeft),
              pr: px(s.paddingRight), radius: s.borderRadius, fs: s.fontSize, lh: s.lineHeight,
              fw: s.fontWeight, color: s.color, bg: s.backgroundColor,
              rail: before && before.content !== 'none' ? px(before.width) : 0} : null,
      icon: ic ? px(getComputedStyle(ic).fontSize) : null,
      gap: (ic && lab) ? px(lab.getBoundingClientRect().x - ic.getBoundingClientRect().right) : null,
    };
  });
}
"""


def goto(page, base, path, settle):
    resp = page.goto(base + path, wait_until='load')
    page.wait_for_timeout(settle)
    return resp.status if resp else None


def discover(page, base, spec, settle):
    lst, pat = spec[1:].split('|')
    goto(page, base, lst, settle)
    for h in page.eval_on_selector_all('main a[href]', 'els => els.map(e => e.getAttribute("href"))'):
        p = (h or '').split('?')[0].replace(base, '')
        if re.fullmatch(pat, p):
            return p
    return None


def check_item(v, it, where):
    a = it['a']
    if not a:
        return
    want = {'h': 44, 'pt': 10, 'pl': 12, 'pr': 12}
    for k, val in want.items():
        if abs(a[k] - val) > 0.6:
            v.append(f'SN-4 {where} {it["id"]} {k}={a[k]} ≠ {val}')
    if a['radius'] != '10px':
        v.append(f'SN-4 {where} {it["id"]} radius={a["radius"]} ≠ 10px')
    if it['icon'] != 20:
        v.append(f'SN-4 {where} {it["id"]} icon={it["icon"]} ≠ 20')
    if it['gap'] is not None and abs(it['gap'] - 12) > 1:
        v.append(f'SN-4 {where} {it["id"]} gap={it["gap"]} ≠ 12')
    if (a['fs'], a['lh']) != ('15px', '22px'):
        v.append(f'SN-4 {where} {it["id"]} chữ {a["fs"]}/{a["lh"]} ≠ 15/22')
    fw = '700' if it['active'] else '500'
    if a['fw'] != fw:
        v.append(f'SN-4 {where} {it["id"]} weight={a["fw"]} ≠ {fw}')
    if it['active']:
        if a['color'] != 'rgb(22, 143, 194)' or a['bg'] != 'rgb(234, 247, 253)' or a['rail'] != 3:
            v.append(f'SN-4 {where} {it["id"]} active color={a["color"]} bg={a["bg"]} rail={a["rail"]}')


def expected_ids(role, has_inspection):
    out = []
    for nid, cond in GOLDEN:
        if cond == 'mgr_active' and role in ('staff', 'mixed'):
            continue
        if cond == 'mgr_any' and role == 'staff':
            continue
        if cond == 'optional' and not has_inspection:
            continue
        out.append(nid)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--base', default='http://127.0.0.1:8090')
    ap.add_argument('--login', default='em.hcm')
    ap.add_argument('--password', default='wujia@test123')
    ap.add_argument('--role', default='owner', choices=('owner', 'manager', 'staff', 'mixed'))
    ap.add_argument('--store', type=int, default=0, help='đặt cookie cửa hàng đang thao tác (user nhiều cửa hàng)')
    ap.add_argument('--settle', type=int, default=900)
    ap.add_argument('--json', default='')
    ap.add_argument('--shots', default='')
    ap.add_argument('--quick', action='store_true', help='bỏ SN-5 (32 route)')
    ap.add_argument('--only', default='', choices=('', 'acct'), help='acct = chỉ SN-10…14 (E8c)')
    a = ap.parse_args()
    base = a.base.rstrip('/')
    v, out = [], {'base': base, 'login': a.login, 'role': a.role}
    with sync_playwright() as p:
        br = p.chromium.launch()
        ctx = br.new_context(viewport={'width': 1440, 'height': 900})
        page = ctx.new_page()
        errs = []
        page.on('pageerror', lambda e: errs.append(str(e)[:200]))
        login(page, base, a.login, a.password)
        if a.store:
            ctx.add_cookies([{'name': 'wujia_active_franchise_id', 'value': str(a.store), 'url': base}])

        out['acct'] = check_acct(v, page, base, a)
        out['widths'] = {}
        for w in (() if a.only else WIDTHS):
            page.set_viewport_size({'width': w, 'height': 900 if w >= 992 else 844})
            goto(page, base, '/portal/order', a.settle)
            d = page.evaluate(SHELL)
            out['widths'][w] = d
            if a.shots:
                page.screenshot(path=f'{a.shots}/sidebar_{w}.png')
            if d['scrollW'] > d['vw']:
                v.append(f'SN-9 {w} tràn ngang {d["scrollW"]} > {d["vw"]}')
            if w >= 1200:
                if not d['shown'] or abs(d['rect']['w'] - 264) > 0.5:
                    v.append(f'SN-1 {w} sidebar shown={d["shown"]} w={d["rect"] and d["rect"]["w"]}')
                if d['navLeft'] != '264px' or d['contentML'] != '264px':
                    v.append(f'SN-1 {w} navbar left={d["navLeft"]} content ml={d["contentML"]}')
                if abs(d['brand']['h'] - 88) > 0.5 or d['logo']['w'] > 160.5 or d['logo']['h'] > 64.5:
                    v.append(f'SN-2 {w} brand h={d["brand"]["h"]} logo={d["logo"]["w"]}×{d["logo"]["h"]}')
            elif w >= 992:
                if d['shown']:
                    v.append(f'SN-6 {w} drawer đang MỞ khi tải trang')
                t = d['toggle']
                if not t or not t['visible'] or t['covered']:
                    v.append(f'SN-6 {w} hamburger không bấm được {t}')
            else:
                if d['display'] != 'none':
                    v.append(f'SN-7 {w} sidebar display={d["display"]}')
            if w == 1024:
                t = d['toggle'] or {}
                if t.get('tag') != 'button' or not t.get('label') or t.get('controls') != 'wj-main-menu':
                    v.append(f'SN-8 hamburger {t}')
                if d['overlays'] != 1:
                    v.append(f'SN-8 có {d["overlays"]} .sidenav-overlay')

        if a.only:
            out['jsErrors'] = errs
            br.close()
            return finish(v, out, a, errs)
        # SN-3 thứ tự + SN-4 dáng (1440)
        page.set_viewport_size({'width': 1440, 'height': 900})
        goto(page, base, '/portal/order', a.settle)
        items = page.evaluate(ITEMS)
        out['items'] = items
        ids = [i['id'] for i in items]
        has_insp = 'nav_item_inspection' in ids
        exp = expected_ids(a.role, has_insp)
        if ids != exp:
            v.append(f'SN-3 thứ tự {ids} ≠ {exp}')
        for it in items:
            if not it['header'] and it['id'] in LABELS and it['label'] != LABELS[it['id']]:
                v.append(f'SN-3 nhãn {it["id"]}={it["label"]!r} ≠ {LABELS[it["id"]]!r}')
            if not it['header']:
                check_item(v, it, 'default')
        normal = next((i for i in items if not i['header'] and not i['active']), None)
        if normal:
            sel = f'#{normal["id"]} > a'
            page.hover(sel)
            page.wait_for_timeout(350)
            check_item(v, next(i for i in page.evaluate(ITEMS) if i['id'] == normal['id']), 'hover')
            page.mouse.move(1400, 880)
            page.focus(sel)
            page.wait_for_timeout(200)
            check_item(v, next(i for i in page.evaluate(ITEMS) if i['id'] == normal['id']), 'focus')

        # SN-5 active
        out['active'] = []
        if not a.quick:
            for rt, want in ACTIVE:
                path = discover(page, base, rt, a.settle) if rt.startswith('@') else rt
                if not path:
                    out['active'].append({'route': rt, 'miss': True})
                    continue
                st = goto(page, base, path, a.settle)
                landed = page.url.replace(base, '')
                its = page.evaluate(ITEMS)
                act = [(i['id'], i['ariaCurrent']) for i in its if i['active']]
                cur = [i['id'] for i in its if i['ariaCurrent'] == 'page']
                out['active'].append({'route': rt, 'path': path, 'status': st, 'landed': landed, 'active': act})
                if landed.split('?')[0] not in (path, '/vi' + path):
                    continue   # route chuyển hướng (không quyền/không dữ liệu) — không phải lỗi sidebar
                if want and want not in [i['id'] for i in its]:
                    continue   # mục bị ẩn theo quyền
                ok = ([x[0] for x in act] == ([want] if want else [])) and cur == ([want] if want else [])
                if not ok:
                    v.append(f'SN-5 {path} sáng={act} aria-current={cur} ≠ {want}')

        # SN-6 drawer
        out['drawer'] = {}
        for w in (1024, 1199, 992):
            page.set_viewport_size({'width': w, 'height': 768})
            goto(page, base, '/portal/order', a.settle)
            seq = {}

            def st():
                return page.evaluate(SHELL)

            def opened(tag):
                page.click('.wj-menu-toggle')
                page.wait_for_timeout(450)
                s = st()
                seq[tag] = s
                if not s['shown'] or not s['overlayShown'] or s['toggle']['expanded'] != 'true':
                    v.append(f'SN-6 {w} {tag}: mở không đúng shown={s["shown"]} overlay={s["overlayShown"]} '
                             f'expanded={s["toggle"]["expanded"]}')
                if 'wj-sidebar__close' not in (s['focus'] or ''):
                    v.append(f'SN-6 {w} {tag}: focus sau mở = {s["focus"]}')

            def closed(tag):
                page.wait_for_timeout(450)
                s = st()
                seq[tag] = s
                if s['shown'] or s['overlayShown'] or s['toggle']['expanded'] != 'false':
                    v.append(f'SN-6 {w} {tag}: chưa đóng shown={s["shown"]} overlay={s["overlayShown"]}')
                if 'wj-menu-toggle' not in (s['focus'] or ''):
                    v.append(f'SN-6 {w} {tag}: focus không về hamburger ({s["focus"]})')

            opened('open1')
            if a.shots and w == 1024:
                page.screenshot(path=f'{a.shots}/drawer_{w}_open.png')
            page.locator('.wj-menu-toggle').dispatch_event('click')
            closed('toggleClose')
            opened('open2')
            page.keyboard.press('Escape')
            closed('escape')
            opened('open3')
            page.mouse.click(w - 30, 600)
            closed('backdrop')
            opened('open4')
            page.click('#wj-main-menu .wj-sidebar__close')
            closed('closeBtn')
            out['drawer'][w] = seq

        out['jsErrors'] = errs
        br.close()
    finish(v, out, a, errs)


def finish(v, out, a, errs):
    if errs:
        v.append(f'JS {len(errs)} lỗi: {errs[:3]}')
    out['violations'] = v
    if a.json:
        json.dump(out, open(a.json, 'w'), ensure_ascii=False, indent=1)
    print(f'wj_sidebar {a.login} ({a.role}) — {len(v)} vi phạm')
    for x in v:
        print('  ', x)
    sys.exit(1 if v else 0)


if __name__ == '__main__':
    main()
