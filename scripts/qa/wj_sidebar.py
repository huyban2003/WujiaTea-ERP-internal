#!/usr/bin/env python3
"""Thước đo SidebarNavigation CMP-SN-001 (UI-SIDEBAR-001) — E8b.

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

        out['widths'] = {}
        for w in WIDTHS:
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
