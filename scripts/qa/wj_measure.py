#!/usr/bin/env python3
"""Đo portal Wujia bằng trình duyệt thật — bảng trước/sau cho cụm D3/D4.

Vì sao nằm trong repo chứ không phải scratchpad: ba script đo của cụm D3/D4
(`d3_review.py`, `d4b_rhythm.py`, `d4_inventory.py`) từng sống trong
`scratchpad/` vốn gitignored, nên khi đổi sang máy khác là mất trắng và phải
dựng lại từ đầu. Bộ đo là bằng chứng nghiệm thu, không phải file nháp.

Bốn lớp bằng chứng, gom trong MỘT lượt chạy — vì từng lớp một đều đã có tiền lệ
lọt lỗi:

1. RULE 1 `HIERARCHY` — nhãn phụ trong card có cỡ ≥ tiêu đề mở đầu của CHÍNH
   card đó. Bắt được cái mà "so từng số với chuẩn" không bao giờ bắt.
2. RULE 2 `CROSS` — histogram cỡ tiêu đề mở đầu card toàn portal, để thấy lệch
   chuẩn GIỮA các màn.
3. Nhịp header→body TUYỆT ĐỐI. RULE 1/2 đo sự KHÔNG ĐỀU, nên một sai số đều tay
   trên mọi card lọt qua sạch sẽ — đúng chuyện đã xảy ra ở D4b (`gap` cộng chồng
   margin thành 24px trong khi D3 vừa hội tụ 12px, hai rule kia vẫn xanh).
4. Chiều cao trang + SỐ RECORD THẤY TRONG VIEWPORT ở đủ 5 khổ BA chỉ định
   (acceptance #11: số record thấy được không được giảm).

Kèm ảnh chụp: số đo Pass hết mà bố cục vẫn vỡ là chuyện đã xảy ra hai lần
(D3e badge trôi 966px, D3d nhịp mất 28px), chỉ ảnh mới bắt được.

    # chụp mốc trước khi sửa
    python3 scripts/qa/wj_measure.py --portal-login anh.owner --out before.json
    # sau khi sửa
    python3 scripts/qa/wj_measure.py --portal-login anh.owner --out after.json
    # so hai mốc
    python3 scripts/qa/wj_measure.py --diff before.json after.json
"""
import argparse
import json
import pathlib
import re
import sys

BREAKPOINTS = [1440, 1024, 992, 390, 360]

ROUTES = [
    '/portal', '/portal/order', '/portal/purchase-history', '/portal/delivery',
    '/portal/return', '/portal/notification', '/portal/knowledge',
    '/portal/support', '/portal/exam', '/portal/debt', '/portal/info-request',
    '/portal/reports/orders', '/portal/inspection',
]

# Lớp khung card đang là hợp đồng (component mới + các họ chưa migrate).
CARD_SELECTOR = (
    '.wj-surface-card, .wj-pc-card, .wj-pc-metric-card, .wj-rep-mcard, '
    '.wujia-content-card, .wujia-kpi-card, .card'
)

# JS chạy trong trang: trả về toàn bộ số đo của một khổ.
PROBE = r"""
(cardSel) => {
  const px = v => Math.round(parseFloat(v) * 100) / 100;
  const vis = el => {
    const r = el.getBoundingClientRect();
    return r.width > 0 && r.height > 0 &&
           getComputedStyle(el).visibility !== 'hidden';
  };
  const HEAD = 'h1,h2,h3,h4,h5,h6,.wj-card-header__title';

  const cards = [...document.querySelectorAll(cardSel)].filter(vis);
  const surfaces = [], hierarchy = [], rhythm = [], titles = [], noHeader = [];

  cards.forEach((card, idx) => {
    const cs = getComputedStyle(card);
    const rect = card.getBoundingClientRect();
    // Khoá nhận dạng bền hơn chỉ số: lớp + chữ đầu tiên trong card.
    const key = (card.className || '').toString().trim().split(/\s+/).slice(0, 3).join('.')
              + '#' + (card.innerText || '').trim().slice(0, 24).replace(/\s+/g, ' ');
    surfaces.push({
      key, idx,
      w: px(rect.width), h: px(rect.height),
      radius: cs.borderRadius, border: cs.borderTopWidth + ' ' + cs.borderTopColor,
      pad: cs.padding, bg: cs.backgroundColor, shadow: cs.boxShadow,
      gap: cs.gap,
    });

    const heads = [...card.querySelectorAll(HEAD)].filter(vis);
    if (!heads.length) return;
    const lead = heads[0];
    const leadSize = px(getComputedStyle(lead).fontSize);
    titles.push(leadSize);

    // RULE 1 — nhãn phụ không được ≥ tiêu đề mở đầu của chính card này.
    heads.slice(1).forEach(h => {
      const s = px(getComputedStyle(h).fontSize);
      if (s >= leadSize) {
        hierarchy.push({ key, lead: leadSize, inner: s,
                         text: (h.innerText || '').trim().slice(0, 40) });
      }
    });

    // Nhịp TUYỆT ĐỐI header -> khối nội dung ngay sau nó.
    // CHỈ đo khi có .wj-card-header thật. Bản đầu lấy `lead.parentElement` làm
    // header dự phòng, và ở /portal/inspection nó vớ phải một div bao lớn có
    // anh em nằm PHÍA TRÊN ⇒ in ra nhịp -48.91px, một con số không tồn tại.
    // Thà không đo còn hơn đo ra số sai (bài học "harness đo sai nguy hơn không đo").
    const header = card.querySelector('.wj-card-header');
    if (!header) noHeader.push(key);
    if (header && header.nextElementSibling && vis(header.nextElementSibling)) {
      const a = header.getBoundingClientRect().bottom;
      const b = header.nextElementSibling.getBoundingClientRect().top;
      rhythm.push({ key, gap: px(b - a) });
    }
  });

  // Số record thấy được trong viewport (acceptance #11 của BA).
  const recSel = 'tr, li, .wj-surface-card--record, .wujia-mdash-card, ' +
                 '.wj-pc-card, .wujia-content-card';
  const vh = window.innerHeight;
  const inView = [...document.querySelectorAll(recSel)].filter(el => {
    const r = el.getBoundingClientRect();
    return r.height > 0 && r.top < vh && r.bottom > 0;
  }).length;

  return {
    pageH: px(document.documentElement.scrollHeight),
    overflowX: document.documentElement.scrollWidth > window.innerWidth + 1,
    recordsInView: inView,
    surfaces, hierarchy, rhythm, titles, noHeader,
  };
}
"""


def login(page, base, user, password):
    page.goto(f'{base}/web/login', wait_until='domcontentloaded')
    page.fill('input[name="login"]', user)
    page.fill('input[name="password"]', password)
    page.click('button[type="submit"]')
    page.wait_for_load_state('domcontentloaded')


def run(args):
    from playwright.sync_api import sync_playwright

    shots = pathlib.Path(args.shots)
    shots.mkdir(parents=True, exist_ok=True)
    result = {'base': args.base, 'login': args.portal_login, 'routes': {}}

    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        ctx = browser.new_context(viewport={'width': 1440, 'height': 900})
        page = ctx.new_page()
        errors = []
        page.on('pageerror', lambda e: errors.append(str(e)))
        login(page, args.base, args.portal_login, args.password)

        for route in args.routes:
            result['routes'][route] = {}
            for w in args.breakpoints:
                page.set_viewport_size({'width': w, 'height': 900})
                before = len(errors)
                # KHÔNG dùng 'networkidle': portal mở long-poll bus.bus nên
                # mạng không bao giờ 'rảnh', mọi trang sẽ timeout 30s.
                resp = page.goto(args.base + route, wait_until='load')
                page.wait_for_timeout(args.settle)
                data = page.evaluate(PROBE, CARD_SELECTOR)
                data['status'] = resp.status if resp else None
                # Redirect ngầm vẫn trả 200 — "Pass rỗng" biến tướng, phải ghi lại.
                data['landed'] = re.sub(r'^https?://[^/]+', '', page.url)
                data['redirected'] = data['landed'].split('?')[0] != route
                data['jsErrors'] = errors[before:]
                if args.screenshots:
                    name = route.strip('/').replace('/', '_') or 'root'
                    shot = shots / f'{name}@{w}.png'
                    page.screenshot(path=str(shot), full_page=True)
                    data['shot'] = str(shot)
                result['routes'][route][str(w)] = data
                flag = 'OK ' if data['status'] == 200 and not data['jsErrors'] else '!! '
                print(f"{flag}{route:32s} @{w:5d}  "
                      f"h={data['pageH']:8.1f}  card={len(data['surfaces']):3d}  "
                      f"rec={data['recordsInView']:3d}  "
                      f"HIER={len(data['hierarchy'])}  "
                      f"{'REDIR' if data['redirected'] else ''}"
                      f"{' OVERFLOW' if data['overflowX'] else ''}")
        browser.close()

    pathlib.Path(args.out).write_text(json.dumps(result, indent=1, ensure_ascii=False))
    summarise(result)
    print(f'\n→ {args.out}')


def summarise(result):
    hier = cross = over = jse = redir = 0
    rhythm, titles = {}, {}
    for route, by_w in result['routes'].items():
        for w, d in by_w.items():
            hier += len(d['hierarchy'])
            over += bool(d['overflowX'])
            jse += len(d['jsErrors'])
            redir += bool(d['redirected'])
            for r in d['rhythm']:
                rhythm[r['gap']] = rhythm.get(r['gap'], 0) + 1
            for t in d['titles']:
                titles[t] = titles.get(t, 0) + 1
    print('\n=== TỔNG ===')
    print(f'  RULE 1 HIERARCHY vi phạm : {hier}')
    print(f'  tràn ngang               : {over}')
    print(f'  lỗi JS                   : {jse}')
    print(f'  redirect ngầm            : {redir}')
    print(f'  RULE 2 histogram cỡ tiêu đề card : '
          + ' · '.join(f'{k}×{v}' for k, v in sorted(titles.items())))
    print(f'  histogram nhịp header→body       : '
          + ' · '.join(f'{k}×{v}' for k, v in sorted(rhythm.items())))


def diff(a_path, b_path):
    a = json.loads(pathlib.Path(a_path).read_text())
    b = json.loads(pathlib.Path(b_path).read_text())
    print(f'{"route":34s} {"khổ":>6s} {"cao trước":>10s} {"cao sau":>9s} '
          f'{"Δ":>8s} {"rec":>9s}')
    worse = 0
    for route, by_w in b['routes'].items():
        for w, nb in by_w.items():
            na = a['routes'].get(route, {}).get(w)
            if not na:
                continue
            dh = nb['pageH'] - na['pageH']
            dr = nb['recordsInView'] - na['recordsInView']
            # Acceptance #11: số record thấy được KHÔNG ĐƯỢC giảm.
            mark = ' ⚠ MẤT RECORD' if dr < 0 else ''
            if dr < 0:
                worse += 1
            if abs(dh) > 0.5 or dr:
                print(f'{route:34s} {w:>6s} {na["pageH"]:10.1f} {nb["pageH"]:9.1f} '
                      f'{dh:+8.1f} {na["recordsInView"]:4d}→{nb["recordsInView"]:<4d}{mark}')
    print(f'\nô mất record: {worse}')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--base', default='http://127.0.0.1:8019')
    # KHÔNG có mặc định: chạy bằng admin cho 0 bề mặt portal mà vẫn báo "xong"
    # — bẫy "Pass rỗng" đã ghi ở luật D4 #3.
    ap.add_argument('--portal-login', help='BẮT BUỘC khi đo, ví dụ anh.owner')
    ap.add_argument('--password', default='demo123')
    ap.add_argument('--routes', nargs='*', default=ROUTES)
    ap.add_argument('--breakpoints', nargs='*', type=int, default=BREAKPOINTS)
    ap.add_argument('--out', default='wj_measure.json')
    ap.add_argument('--shots', default='scratchpad/qa-shots')
    ap.add_argument('--screenshots', action='store_true')
    ap.add_argument('--settle', type=int, default=400, help='ms chờ sau khi tải')
    ap.add_argument('--diff', nargs=2, metavar=('TRƯỚC', 'SAU'))
    args = ap.parse_args()

    if args.diff:
        diff(*args.diff)
        return
    if not args.portal_login:
        sys.exit('--portal-login là bắt buộc (admin cho 0 bề mặt portal → Pass rỗng)')
    run(args)


if __name__ == '__main__':
    main()
