"""Guard StatusBadge `CMP-SB-001` — cụm E2 (`UI-STATUSBADGE-001`).

Ba câu hỏi không guard nào hiện có trả lời được:

  SB-1  Mọi badge TRẠNG THÁI có đúng một hình học không?
        Acceptance BA: cao 28 · rộng ≥84 · đệm `0 14px` · bo 14 · 13/600 ·
        `line-height 1` · nowrap · không border/shadow.
  SB-2  Còn badge nào nằm ngoài component không? (họ cũ `wujia-badge`,
        `wj-pc-badge`, `wj-debt*`, `wujia-mres-badge`, `wujia-mdelivery-badge`,
        `state-badge`) — Khảo sát defer, đếm riêng.
  SB-3  Năm họ BA loại khỏi phạm vi (Role · Count · FilterChip · Category ·
        Alert) có bị CSS dùng chung kéo theo không? Đo dấu vân tay computed ở
        mốc "trước", so lại ở mốc "sau" bằng `--diff`.

🔴 `--scope body` là MẶC ĐỊNH và cố ý: D6d từng đo `--scope .wujia-mpage` rồi bỏ
sót đúng một form vì portal có nhiều vỏ trang khác nhau ⇒ bảng Pass rỗng.

    python3 scripts/qa/wj_statusbadge.py --base http://127.0.0.1:8092 \
        --portal-login anh.owner --out after.json
    python3 scripts/qa/wj_statusbadge.py --diff before.json after.json
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from wj_measure import login  # noqa: E402  (nguồn duy nhất cho đường đăng nhập portal)

ROUTES = [
    '/portal', '/portal/purchase-history', '/portal/delivery',
    '/portal/franchise-information', '/portal/profile',
]
BREAKPOINTS = [1440, 1024, 992, 991, 390, 360]

SEL_NEW = '.wj-status-badge'
SEL_LEGACY = ('.wujia-badge, .wj-pc-badge, .wj-debt-badge, .wj-debt-pc-badge, '
              '.wujia-mres-badge, .wujia-mdelivery-badge, .state-badge')
# BA loại khỏi migration — phải BẤT BIẾN qua cụm E2. Gồm cả bốn họ ĐANG mượn
# tên lớp cũ (Role/Area/Code/loại thông báo): chúng nằm trong `.wujia-badge` và
# `.wj-pc-badge` nên nếu ta lỡ đổi rule cũ là lộ ra ngay ở đây.
SEL_OUT = ('.wujia-store-role-badge, .wujia-header-badge, .wj-filter-chip, '
           '.wujia-mknow-badges, .wujia-mexam-stepbadge, .wujia-mhome-nav-badge, '
           '.wujia-bnav-noti-badge, .wujia-msheet-item-badge, '
           '.wj-pc-badge--area, .wj-pc-badge--staff, '
           # --confirmed vừa là RoleBadge (chips tài khoản) vừa TỪNG là status ở
           # Lịch sử đặt hàng ⇒ phải neo theo vỏ, không theo tên modifier.
           '.wj-pc-acct-headcard__chips .wj-pc-badge--confirmed, '
           '.wj-pc-acct-field__value .wj-pc-badge--confirmed, '
           '.wujia-maccount-badgerow .wujia-badge-info, '
           '.wujia-mdash-row-tags .wujia-badge')

SPEC = {'h': 28.0, 'min_w': 84.0, 'pad': '0px 14px', 'radius': 14.0,
        'font': 13.0, 'weight': '600'}

JS = r"""
([selNew, selLegacy, selOut]) => {
  const lum = (c) => {
    const m = (c || '').match(/[\d.]+/g);
    if (!m) return null;
    const [r, g, b] = m.slice(0, 3).map(Number);
    const a = m.length > 3 ? Number(m[3]) : 1;
    if (a === 0) return null;
    const f = (v) => { v /= 255; return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); };
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b);
  };
  const bgOf = (el) => {
    let n = el;
    while (n && n !== document.documentElement) {
      const c = getComputedStyle(n).backgroundColor;
      if (lum(c) !== null) return c;
      n = n.parentElement;
    }
    return 'rgb(255, 255, 255)';
  };
  const probe = (el) => {
    const cs = getComputedStyle(el);
    const r = el.getBoundingClientRect();
    const bg = cs.backgroundColor, fg = cs.color;
    const l1 = lum(fg), l2 = lum(bgOf(el));
    const ratio = (l1 === null || l2 === null) ? null
      : Math.round(((Math.max(l1, l2) + 0.05) / (Math.min(l1, l2) + 0.05)) * 100) / 100;
    return {
      text: (el.textContent || '').trim().slice(0, 40),
      cls: el.className,
      h: Math.round(r.height * 100) / 100,
      w: Math.round(r.width * 100) / 100,
      pad: `${cs.paddingTop} ${cs.paddingRight}`.replace(/^(\S+) (\S+)$/, '$1 $2'),
      padFull: [cs.paddingTop, cs.paddingRight, cs.paddingBottom, cs.paddingLeft].join(' '),
      radius: parseFloat(cs.borderTopLeftRadius),
      font: parseFloat(cs.fontSize),
      weight: cs.fontWeight,
      lineHeight: cs.lineHeight,
      whiteSpace: cs.whiteSpace,
      border: cs.borderTopWidth,
      shadow: cs.boxShadow,
      bg, fg, contrast: ratio,
      rects: el.getClientRects().length,
      clipped: el.scrollWidth > el.clientWidth + 1,
      visible: r.width > 0 && r.height > 0,
    };
  };
  const grab = (sel) => [...document.querySelectorAll(sel)]
    .filter((el) => el.getBoundingClientRect().width > 0)
    .map(probe);
  return {
    news: grab(selNew),
    legacy: grab(selLegacy),
    out: grab(selOut),
    overflowX: document.documentElement.scrollWidth > window.innerWidth + 1,
  };
}
"""


def judge(news):
    """Trả danh sách vi phạm của MỘT khổ, đối chiếu thẳng acceptance BA."""
    bad = []
    for b in news:
        tag = f"{b['text'][:22]!r}"
        if abs(b['h'] - SPEC['h']) > 0.5:
            bad.append(f"{tag}: cao {b['h']} ≠ 28")
        if b['w'] < SPEC['min_w'] - 0.5:
            bad.append(f"{tag}: rộng {b['w']} < min-width 84")
        if b['padFull'] != '0px 14px 0px 14px':
            bad.append(f"{tag}: đệm {b['padFull']} ≠ '0px 14px'")
        if abs(b['radius'] - SPEC['radius']) > 0.5:
            bad.append(f"{tag}: bo {b['radius']} ≠ 14")
        if abs(b['font'] - SPEC['font']) > 0.5 or b['weight'] != SPEC['weight']:
            bad.append(f"{tag}: chữ {b['font']}/{b['weight']} ≠ 13/600")
        if b['rects'] != 1:
            bad.append(f"{tag}: xuống dòng ({b['rects']} hàng)")
        if b['clipped']:
            bad.append(f"{tag}: cắt chữ")
        if b['whiteSpace'] not in ('nowrap',):
            bad.append(f"{tag}: white-space {b['whiteSpace']} ≠ nowrap")
        if b['border'] != '0px' or b['shadow'] not in ('none',):
            bad.append(f"{tag}: còn border/shadow ({b['border']} · {b['shadow']})")
        if b['contrast'] is not None and b['contrast'] < 4.5:
            bad.append(f"{tag}: contrast {b['contrast']} < AA 4.5")
    return bad


def fingerprint(items):
    """Dấu vân tay so sánh được của các họ NGOÀI phạm vi (SB-3)."""
    return sorted(f"{i['cls']}|{i['text']}|{i['h']}|{i['w']}|{i['radius']}|"
                  f"{i['font']}/{i['weight']}|{i['bg']}|{i['fg']}" for i in items)


def do_diff(a_path, b_path):
    a = json.load(open(a_path, encoding='utf-8'))
    b = json.load(open(b_path, encoding='utf-8'))
    changed = 0
    for key in sorted(set(a) | set(b)):
        fa = a.get(key, {}).get('out_fp', [])
        fb = b.get(key, {}).get('out_fp', [])
        if fa != fb:
            changed += 1
            only_a = [x for x in fa if x not in fb]
            only_b = [x for x in fb if x not in fa]
            print(f"✗ {key}: họ ngoài phạm vi ĐỔI ({len(only_a)} mất / {len(only_b)} mới)")
            for x in (only_a + only_b)[:6]:
                print('     ', x)
    print(f"\nSB-3 — ô đổi: {changed} (ngưỡng: 0)")
    return 1 if changed else 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--base', default='http://127.0.0.1:8092')
    ap.add_argument('--portal-login')
    ap.add_argument('--password', default='wujia@test123')
    ap.add_argument('--routes', nargs='*', default=ROUTES)
    ap.add_argument('--breakpoints', nargs='*', type=int, default=BREAKPOINTS)
    ap.add_argument('--scope', default='body', help='CHỈ để thu hẹp khi soi; mặc định body')
    ap.add_argument('--settle', type=int, default=600)
    ap.add_argument('--out')
    ap.add_argument('--diff', nargs=2, metavar=('TRƯỚC', 'SAU'))
    args = ap.parse_args()

    if args.diff:
        return do_diff(*args.diff)
    if not args.portal_login:
        sys.exit('--portal-login BẮT BUỘC: chạy bằng admin cho 0 bề mặt portal (bẫy Pass rỗng).')

    sel_new = f'{args.scope} {SEL_NEW}' if args.scope != 'body' else SEL_NEW
    from playwright.sync_api import sync_playwright
    result, total_bad, n_new, n_legacy = {}, 0, 0, 0
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_context(viewport={'width': 1440, 'height': 900}).new_page()
        # Tái dùng login() của wj_measure: form /web/login bị theme Vuexy ẩn ⇒ fill treo 30s.
        login(page, args.base, args.portal_login, args.password)

        for route in args.routes:
            for w in args.breakpoints:
                page.set_viewport_size({'width': w, 'height': 900})
                page.goto(f'{args.base}{route}', wait_until='load')
                page.wait_for_timeout(args.settle)
                redir = route.rstrip('/') not in page.url
                data = page.evaluate(JS, [sel_new, SEL_LEGACY, SEL_OUT])
                bad = judge(data['news'])
                if data['overflowX']:
                    bad.append('TRÀN NGANG')
                key = f'{route}@{w}'
                result[key] = {
                    'n_new': len(data['news']), 'n_legacy': len(data['legacy']),
                    'legacy_cls': sorted({i['cls'] for i in data['legacy']}),
                    'findings': bad, 'redirect': redir,
                    'out_fp': fingerprint(data['out']),
                    'news': data['news'],
                }
                total_bad += len(bad)
                n_new += len(data['news'])
                n_legacy += len(data['legacy'])
                flag = ' REDIR' if redir else ''
                print(f"{'✗' if bad else 'OK'} {route:32s} @{w:5d}  "
                      f"mới={len(data['news']):3d} cũ={len(data['legacy']):3d} "
                      f"vi phạm={len(bad):3d}{flag}")
                for b in bad[:6]:
                    print('     ✗', b)
        browser.close()

    print(f"\n=== TỔNG ===\n  badge component (mẫu đo): {n_new}"
          f"\n  badge họ CŨ còn lại      : {n_legacy}"
          f"\n  vi phạm hình học/màu     : {total_bad}")
    if n_new == 0:
        print('  🔴 MẪU RỖNG — bảng Pass này vô nghĩa, kiểm lại tài khoản/route.')
    if args.out:
        json.dump(result, open(args.out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        print(f'\n→ {args.out}')
    return 1 if (total_bad or n_new == 0) else 0


if __name__ == '__main__':
    sys.exit(main())
