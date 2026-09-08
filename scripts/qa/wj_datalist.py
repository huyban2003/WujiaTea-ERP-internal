#!/usr/bin/env python3
"""Đo danh sách nghiệp vụ portal theo spec CMP-DL-001 — mốc trước/sau cho cụm D5.

Khác `wj_measure.py` (đo KHUNG card, cụm D3/D4): ở đây đối tượng là DANH SÁCH.
Số BA đòi: header 44 · row single-line ≥52 · multi-line 64–72 · cell padding
10/16 · mobile compact-row 64–76 · detail-card 96–120 · gap item 8 · pager chỉ
hiện khi >1 trang · th có scope.

Đo bằng trình duyệt vì ba thứ chỉ tồn tại lúc chạy: chiều cao thật của row,
padding sau khi mọi tầng CSS phân xử, và số record thấy trong viewport.

    python3 scripts/qa/wj_datalist.py --portal-login anh.owner \
        --password 'wujia@test123' --out docs/d5-datalist-before.json
"""
import argparse
import json
import pathlib
import re
import sys

BREAKPOINTS = [1440, 1024, 992, 991, 390, 360]

# 10 route BA liệt kê ở "Màn hình áp dụng" của CMP-DL-001. Báo cáo KHÔNG có
# trong danh sách đó nên cố ý vắng mặt.
ROUTES = [
    '/portal', '/portal/purchase-history', '/portal/return', '/portal/delivery',
    '/portal/debt', '/portal/notification', '/portal/support', '/portal/exam',
    '/portal/knowledge', '/portal/inspection',
]

PROBE = r"""
() => {
  const px = v => Math.round(parseFloat(v) * 100) / 100;
  const vis = el => {
    const r = el.getBoundingClientRect();
    return r.width > 0 && r.height > 0 && getComputedStyle(el).visibility !== 'hidden';
  };
  const name = el => {
    const c = (el.className || '').toString().trim().split(/\s+/)
      .filter(x => !/^(is-|has-|active|text-|d-|mb-|mt-|p-|g-)/.test(x));
    return c.slice(0, 2).join('.') || el.tagName.toLowerCase();
  };

  const out = { tables: [], lists: [], pagers: [] };

  // --- PC: bảng semantic ---------------------------------------------------
  document.querySelectorAll('table').forEach(t => {
    if (!vis(t)) return;
    const body = t.tBodies[0];
    const rows = body ? [...body.rows].filter(vis) : [];
    if (rows.length < 1) return;
    const ths = [...t.querySelectorAll('th')];
    const headRow = t.tHead && t.tHead.rows[0];
    // Row nhiều dòng = cao hơn hẳn row một dòng cùng bảng.
    const hs = rows.map(r => px(r.getBoundingClientRect().height));
    const cell = rows[0].cells[0];
    const cs = cell ? getComputedStyle(cell) : null;
    out.tables.push({
      key: name(t), cols: ths.length,
      thScoped: ths.filter(x => x.getAttribute('scope')).length,
      headH: headRow && vis(headRow) ? px(headRow.getBoundingClientRect().height) : null,
      rowH: { min: Math.min(...hs), max: Math.max(...hs), n: hs.length },
      // Acceptance #9: record ĐỌC ĐƯỢC không cần cuộn — row thấp đi thì số này phải tăng.
      rowsInViewport: rows.filter(r => r.getBoundingClientRect().top < window.innerHeight).length,
      cellPad: cs ? cs.paddingTop + ' ' + cs.paddingRight + ' '
                    + cs.paddingBottom + ' ' + cs.paddingLeft : null,
      hasThead: !!t.tHead, hasTbody: !!body,
    });
  });

  // --- Mobile / PC không-bảng: chuỗi item lặp lại --------------------------
  // Một container LÀ danh sách khi có >=2 con element cùng chữ ký lớp.
  document.querySelectorAll('div,ul,ol,section').forEach(box => {
    if (!vis(box)) return;
    const all = [...box.children].filter(vis);
    if (all.length < 2) return;
    // Lấy DÃY LIÊN TIẾP dài nhất các con cùng chữ ký lớp. Bản đầu đòi cả hộp
    // đồng nhất nên bỏ sót mọi danh sách có header/pager là anh em của item
    // (support, delivery) — càng chuẩn hoá càng đo hụt, đúng chiều ngược sự thật.
    const key = k => (k.className || '').toString().trim().split(/\s+/)
                       .filter(x => !/^(is-|has-|active)/.test(x)).join(' ');
    let best = [], cur = [];
    for (const k of all) {
      if (cur.length && key(k) === key(cur[0])) { cur.push(k); }
      else { if (cur.length > best.length) best = cur; cur = [k]; }
    }
    if (cur.length > best.length) best = cur;
    const kids = best;
    if (kids.length < 2 || !key(kids[0])) return;
    // Chỉ nhận danh sách XẾP DỌC. Bản đầu nhận cả cụm chip xếp ngang và in ra
    // gap -32/-58px — con số không tồn tại; thà không đo còn hơn đo ra số sai.
    const r0 = kids[0].getBoundingClientRect(), r1 = kids[1].getBoundingClientRect();
    if (r1.top < r0.bottom - 1) return;
    const hs = kids.map(k => px(k.getBoundingClientRect().height));
    const cs = getComputedStyle(kids[0]);
    const boxCs = getComputedStyle(box);
    // gap thật = khoảng cách giữa hai item đầu, gồm cả margin lẫn gap.
    const gap = kids.length > 1
      ? px(kids[1].getBoundingClientRect().top - kids[0].getBoundingClientRect().bottom)
      : null;
    out.lists.push({
      key: name(box), itemKey: name(kids[0]), tag: kids[0].tagName.toLowerCase(),
      n: kids.length, ofChildren: all.length,
      itemH: { min: Math.min(...hs), max: Math.max(...hs) },
      // D5d: acceptance #9 cũng phải đo được ở danh sách, không chỉ ở bảng.
      rowsInViewport: kids.filter(k => k.getBoundingClientRect().top < window.innerHeight).length,
      gap, boxGap: boxCs.gap,
      pad: cs.paddingTop + ' ' + cs.paddingRight + ' ' + cs.paddingBottom
           + ' ' + cs.paddingLeft,
      radius: cs.borderRadius,
      role: box.getAttribute('role') || kids[0].getAttribute('role') || null,
    });
  });

  // --- Pager: có mấy trang, có hiện không ----------------------------------
  document.querySelectorAll('[class*="pagination"],[class*="pager"]').forEach(p => {
    if (!vis(p)) return;
    const btns = [...p.querySelectorAll('a,button')]
      .filter(b => /^\d+$/.test((b.innerText || '').trim()));
    out.pagers.push({ key: name(p), pageBtns: btns.length,
                      text: (p.innerText || '').trim().slice(0, 60).replace(/\s+/g, ' ') });
  });

  out.pageH = px(document.documentElement.scrollHeight);
  out.overflowX = document.documentElement.scrollWidth > window.innerWidth + 1;
  return out;
}
"""


def login(page, base, user, password):
    page.goto(f'{base}/web/login', wait_until='domcontentloaded')
    page.fill('input[name="login"]', user)
    page.fill('input[name="password"]', password)
    # Enter thay vì click: trang đăng nhập UAT có thêm nút submit của ô tìm kiếm
    # website (ẩn) nên `button[type=submit]` khớp 3 phần tử và click treo 30s.
    page.press('input[name="password"]', 'Enter')
    page.wait_for_load_state('domcontentloaded')
    # Đăng nhập hỏng thì MỌI route sau đó redirect về login và bảng đo ra
    # sạch bong — đúng dạng "Pass rỗng" đã trả giá ở D4. Chặn ngay tại đây.
    if '/web/login' in page.url:
        sys.exit(f'ĐĂNG NHẬP HỎNG cho {user} — dừng, đừng đo tiếp (Pass rỗng).')


def run(args):
    from playwright.sync_api import sync_playwright
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
                resp = page.goto(args.base + route, wait_until='load')
                page.wait_for_timeout(args.settle)
                d = page.evaluate(PROBE)
                d['status'] = resp.status if resp else None
                d['landed'] = re.sub(r'^https?://[^/]+', '', page.url)
                d['redirected'] = d['landed'].split('?')[0] != route
                d['jsErrors'] = errors[before:]
                result['routes'][route][str(w)] = d
                flag = 'OK ' if d['status'] == 200 and not d['redirected'] else '!! '
                print(f"{flag}{route:26s} @{w:5d}  tbl={len(d['tables']):2d} "
                      f"list={len(d['lists']):2d} pager={len(d['pagers'])} "
                      f"{'OVERFLOW' if d['overflowX'] else ''}")
        browser.close()
    pathlib.Path(args.out).write_text(json.dumps(result, indent=1, ensure_ascii=False))
    summarise(result)
    print(f'\n→ {args.out}')


def summarise(result):
    head, srow, mrow, pad, gap, noscope = {}, {}, {}, {}, {}, 0
    tables = 0
    for route, by_w in result['routes'].items():
        for w, d in by_w.items():
            wide = int(w) >= 992
            for t in d['tables']:
                tables += 1
                if t['thScoped'] < t['cols']:
                    noscope += 1
                if t['headH']:
                    head[t['headH']] = head.get(t['headH'], 0) + 1
                pad[t['cellPad']] = pad.get(t['cellPad'], 0) + 1
                srow[t['rowH']['min']] = srow.get(t['rowH']['min'], 0) + 1
            if not wide:
                for l in d['lists']:
                    mrow[l['itemH']['min']] = mrow.get(l['itemH']['min'], 0) + 1
                    if l['gap'] is not None:
                        gap[l['gap']] = gap.get(l['gap'], 0) + 1
    top = lambda h, n=8: ' · '.join(
        f'{k}×{v}' for k, v in sorted(h.items(), key=lambda kv: -kv[1])[:n])
    print('\n=== TỔNG (đối chiếu số BA) ===')
    print(f'  bảng đo được                 : {tables}')
    print(f'  bảng thiếu th[scope]         : {noscope}/{tables}')
    print(f'  chiều cao header (BA 44)     : {top(head)}')
    print(f'  row thấp nhất/bảng (BA ≥52)  : {top(srow)}')
    print(f'  cell padding (BA 10px 16px)  : {top(pad, 6)}')
    print(f'  item mobile (BA 64–76)       : {top(mrow)}')
    print(f'  gap item mobile (BA 8)       : {top(gap)}')


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--base', default='http://127.0.0.1:8019')
    ap.add_argument('--portal-login', help='BẮT BUỘC, ví dụ anh.owner')
    ap.add_argument('--password', default='wujia@test123')
    ap.add_argument('--routes', nargs='*', default=ROUTES)
    ap.add_argument('--breakpoints', nargs='*', type=int, default=BREAKPOINTS)
    ap.add_argument('--out', default='wj_datalist.json')
    ap.add_argument('--settle', type=int, default=400)
    a = ap.parse_args()
    if not a.portal_login:
        sys.exit('--portal-login là bắt buộc (admin cho 0 danh sách → Pass rỗng)')
    run(a)
