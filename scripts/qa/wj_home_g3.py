#!/usr/bin/env python3
"""Đo Home PC cụm G3 — issue 142 UI-PC-HOME-REDESIGN-001 (mockup V4 1440×1019).

PC  /portal × 1440/1280/1024/992: hộp hàng đầu (Cửa hàng | Khung giờ), 4 KPI (nhãn + href + hộp),
    mũi tên còn sót, tràn ngang, chữ bị cắt (scrollWidth > clientWidth), ảnh toàn trang.
991 phải ra bố cục mobile (khối PC ẩn).
Mobile /portal × 360/390/430: vân tay bố cục (LAYOUT_PROBE của wj_density) ⇒ `--diff` chứng minh Δ0.

    python3 scripts/qa/wj_home_g3.py --base http://127.0.0.1:8033 --login dung.multi --out after.json --shots DIR
    python3 scripts/qa/wj_home_g3.py --diff before.json after.json
"""
import argparse
import hashlib
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from wj_density import LAYOUT_PROBE, login  # noqa: E402

PC = [(1440, 1019), (1280, 900), (1200, 900), (1199, 900), (1024, 800), (992, 800)]
MOBILE = [(360, 800), (390, 844), (430, 932)]

PC_PROBE = r"""
() => {
  const R = e => { if (!e) return null; const b = e.getBoundingClientRect();
    return [Math.round(b.left), Math.round(b.top + scrollY), Math.round(b.width), Math.round(b.height)]; };
  const pc = document.querySelector('.wujia-home-wrapper > .d-lg-block, .wujia-home-pc');
  if (!pc || !pc.getBoundingClientRect().height) return {pcVisible: false,
      mobileVisible: !!document.querySelector('.wujia-mhome') && document.querySelector('.wujia-mhome').getBoundingClientRect().height > 0};
  const kpis = [...pc.querySelectorAll('.wujia-home-kpi, .wujia-kpi-card')];
  const label = k => { const l = k.querySelector('.wujia-home-kpi-label, .wujia-kpi-label'); return l && l.textContent.trim(); };
  const value = k => { const v = k.querySelector('.wujia-home-kpi-value, .wujia-kpi-value'); return v && v.textContent.trim(); };
  const clipped = [...pc.querySelectorAll('*')].filter(e => {
      const r = e.getBoundingClientRect(); if (!r.width || !e.textContent.trim()) return false;
      return e.scrollWidth > e.clientWidth + 1 && getComputedStyle(e).overflowX !== 'visible';
    }).map(e => ({cls: (e.className || '').toString().split(' ')[0], text: e.textContent.trim().slice(0, 40),
                  ellipsis: getComputedStyle(e).textOverflow === 'ellipsis'}));
  const store = pc.querySelector('.wujia-home-store'), win = pc.querySelector('.wujia-home-window');
  return {
    pcVisible: true,
    overflowX: document.documentElement.scrollWidth > document.documentElement.clientWidth + 1,
    store: R(store), window: R(win),
    storeText: store && store.innerText.replace(/\s+/g, ' ').trim(),
    windowText: win && win.innerText.replace(/\s+/g, ' ').trim(),
    kpis: kpis.map(k => ({label: label(k), value: value(k), box: R(k),
                          href: (k.closest('a') || k.querySelector('a') || {}).getAttribute
                                ? (k.closest('a') || k.querySelector('a')).getAttribute('href') : null})),
    arrows: pc.querySelectorAll('.wujia-kpi-arrow, .wujia-kpi-card .icon-chevron-right').length,
    headings: [...pc.querySelectorAll('h1,h2,h3,h4')].map(h => h.textContent.trim()),
    clipped,
    // G3b — 7 block: tiêu đề, link "Xem tất cả", hộp, số cột theo hàng, badge đè chữ.
    blocks: [...pc.querySelectorAll('.wujia-home-block')].map(b => {
      const t = b.querySelector('.wj-card-header__title');
      const a = b.querySelector('.wj-card-header__action');
      const rows = [...b.querySelectorAll('.wujia-mdash-row')].map(r => {
        const main = r.querySelector('.wujia-mdash-row-main'), badge = r.querySelector('.wj-status-badge, .wujia-badge');
        let hit = 0;
        if (main && badge) { const m = main.getBoundingClientRect(), g = badge.getBoundingClientRect();
          hit = Math.max(0, Math.min(m.right, g.right) - Math.max(m.left, g.left)) *
                Math.max(0, Math.min(m.bottom, g.bottom) - Math.max(m.top, g.top)); }
        return {text: r.innerText.replace(/\s+/g, ' ').trim().slice(0, 60), h: Math.round(r.getBoundingClientRect().height),
                badgeHit: Math.round(hit), icon: (r.querySelector('.wujia-mdash-tile i, .wujia-mdash-ico i') || {}).className || null};
      });
      return {title: t && t.textContent.trim(), action: a && a.textContent.trim(), href: a && a.getAttribute('href'),
              sub: (b.querySelector('.wj-card-header__subtitle') || {}).textContent || null,
              box: R(b), rows, empty: !!b.querySelector('.wj-empty-state')};
    }),
    oldBlocks: pc.querySelectorAll('.wujia-content-card').length,
    chevrons: pc.querySelectorAll('.icon-chevron-right, .icon-arrow-right').length,
    pageH: document.documentElement.scrollHeight,
  };
}
"""


def measure(args):
    from playwright.sync_api import sync_playwright
    res = {'base': args.base, 'login': args.login, 'pc': {}, 'mobile': {}}
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        ctx = browser.new_context(viewport={'width': 1440, 'height': 1019}, device_scale_factor=1)
        page = ctx.new_page()
        login(page, args.base, args.login, args.password)
        for w, h in PC + [(991, 800)]:
            page.set_viewport_size({'width': w, 'height': h})
            page.goto(args.base + '/portal', wait_until='load')
            page.wait_for_timeout(args.settle)
            res['pc'][str(w)] = page.evaluate(PC_PROBE)
            if args.shots:
                page.screenshot(path=f'{args.shots}/home_pc_{w}.png', full_page=True,
                                animations='disabled', caret='hide')
        for w, h in MOBILE:
            page.set_viewport_size({'width': w, 'height': h})
            page.goto(args.base + '/portal', wait_until='load')
            page.wait_for_timeout(args.settle)
            lay = page.evaluate(LAYOUT_PROBE)
            res['mobile'][str(w)] = {'md5': hashlib.md5(json.dumps(lay).encode()).hexdigest(),
                                     'n': len(lay), 'layout': lay,
                                     'pageH': page.evaluate('document.documentElement.scrollHeight')}
            if args.shots:
                page.screenshot(path=f'{args.shots}/home_m_{w}.png', full_page=True,
                                animations='disabled', caret='hide')
        browser.close()
    with open(args.out, 'w') as f:
        json.dump(res, f, ensure_ascii=False, indent=1)
    summary(res)


def summary(res):
    print(f"== {res['login']} @ {res['base']}")
    for w, d in res['pc'].items():
        if not d.get('pcVisible'):
            print(f'  PC {w}: khối PC ẩn, mobile hiện={d.get("mobileVisible")}')
            continue
        s, win = d.get('store'), d.get('window')
        row = (f'store {s} | window {win} Δh={abs(s[3] - win[3]) if s and win else "-"}') if s else 'không có hàng đầu'
        print(f'  PC {w}: tràn={d["overflowX"]} mũi tên={d["arrows"]} {row}')
        print('         KPI:', ' · '.join(f"{k['label']}={k['value']}→{k['href']} {k['box'][2]}×{k['box'][3]}@y{k['box'][1]}"
                                          for k in d['kpis']))
        bl = d.get('blocks') or []
        if bl:
            tops = sorted({b['box'][1] for b in bl})
            per_row = [[b for b in bl if b['box'][1] == y] for y in tops]
            print('         block:', ' | '.join(
                f"{len(r)} cột Δh={max(b['box'][3] for b in r) - min(b['box'][3] for b in r)}" for r in per_row),
                  f"chevron={d['chevrons']} cũ={d['oldBlocks']}",
                  'badge đè=%d' % sum(x['badgeHit'] for b in bl for x in b['rows']))
            for b in bl:
                print(f"           · {b['title']} [{b['action']}→{b['href']}] sub={b['sub']!r} "
                      f"{b['box'][2]}×{b['box'][3]} rows={len(b['rows'])} rỗng={b['empty']}")
        bad = [c for c in d['clipped'] if not c['ellipsis']]
        if d['clipped']:
            print('         cắt chữ:', d['clipped'][:6], '(KHÔNG ellipsis: %d)' % len(bad))
    for w, d in res['mobile'].items():
        print(f'  mobile {w}: md5 {d["md5"][:10]} n={d["n"]} pageH={d["pageH"]}')


def diff(a_path, b_path):
    a, b = json.load(open(a_path)), json.load(open(b_path))
    for w, v in a['mobile'].items():
        v2 = b['mobile'].get(w)
        if v2 and v2['md5'] == v['md5']:
            print(f'  mobile {w}: Δ0 ({v["n"]} phần tử)')
            continue
        print(f'  mobile {w}: LỆCH pageH {v["pageH"]} → {v2 and v2["pageH"]}, n {v["n"]} → {v2 and v2["n"]}')
        for x, y in zip(v['layout'], (v2 or {}).get('layout', [])):
            if x != y:
                print('     ', x, '\n   →', y)
                break


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--base', default='http://127.0.0.1:8033')
    ap.add_argument('--login', default='dung.multi')
    ap.add_argument('--password', default='wujia@test123')
    ap.add_argument('--settle', type=int, default=400)
    ap.add_argument('--shots')
    ap.add_argument('--out', default='wj_home_g3.json')
    ap.add_argument('--diff', nargs=2)
    args = ap.parse_args()
    if args.diff:
        return diff(*args.diff)
    if args.shots:
        os.makedirs(args.shots, exist_ok=True)
    measure(args)


if __name__ == '__main__':
    main()
