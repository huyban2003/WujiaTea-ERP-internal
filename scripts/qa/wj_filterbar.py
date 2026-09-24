#!/usr/bin/env python3
"""Guard hành vi thanh lọc portal — cụm E4c (`CMP-FB-001` / `UI-FILTER-001`).

Ba câu hỏi, đo trên DOM thật chứ không đọc mã:

  1. NGÀY NGƯỢC  `?date_from > ?date_to` phải trả 200 KÈM đúng một thông điệp
     nhìn thấy được trong thanh lọc. Màn trả 0 bản ghi mà không nói gì là
     "im lặng" — đúng lỗi BA nêu.
  2. ĐỔI LỌC     submit bộ lọc mới khi đang ở `?page=3` phải rơi về trang 1.
  3. SANG TRANG  bấm số trang phải giữ nguyên mọi điều kiện đang lọc.

    python3 scripts/qa/wj_filterbar.py --base http://127.0.0.1:8090 \
        --portal-login em.hcm --json out.json

Vùng chạm đo theo cách ĐÃ VÁ của `wj_filterbar_inventory.py`: `closest()` trả
tổ tiên gần nhất khớp BẤT KỲ selector nào trong danh sách — và khớp cả chính
nó — nên phải leo từng bậc một, nếu không 44 đọc ra thành 38.
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from wj_measure import login  # noqa: E402

# Màn có ô ngày + tham số ngày của chính nó. Khảo sát không có ngày ⇒ vắng mặt.
DATE_ROUTES = [
    ('/portal/purchase-history', 'date_from', 'date_to'),
    ('/portal/delivery', 'date_from', 'date_to'),
    ('/portal/notification', 'date_from', 'date_to'),
    ('/portal/return', 'date_from', 'date_to'),
    ('/portal/exam', 'date_from', 'date_to'),
    ('/portal/reports/orders', 'date_from', 'date_to'),
]

# Màn có phân trang để kiểm mục 2 + 3, kèm tên tham số cỡ trang của chính màn
# đó: ép cỡ nhỏ nhất để LUÔN có nhiều trang, nếu không mẫu một trang làm phép đo
# "sang trang giữ lọc" ra Pass rỗng (bẫy mẫu mỏng, bài học E3 trên UAT).
PAGED_ROUTES = [('/portal/purchase-history', 'page_size'),
                ('/portal/delivery', 'page_size'),
                ('/portal/notification', 'limit'),
                ('/portal/return', 'page_size'),
                ('/portal/exam', 'limit')]
SMALL_PAGE = 10

REVERSED = ('2026-09-30', '2026-09-01')     # from > to
VALID = ('2026-01-01', '2026-12-31')
# Khoảng quá khứ xa, chắc chắn không bản ghi nào rơi vào: màn nào vẫn trả đủ
# bản ghi tức là ô ngày KHÔNG được gửi đi (đúng lỗi BA nêu ở mobile Đăng ký thi).
EMPTY_WINDOW = ('2001-01-01', '2001-01-02')
MOBILE_WIDTH = 390

JS_ERRORS = """() => {
  const out = [];
  document.querySelectorAll('.wj-filter-error').forEach(el => {
    const cs = getComputedStyle(el);
    out.push({
      id: el.id || '',
      text: (el.textContent || '').trim(),
      shown: !el.hasAttribute('hidden') && cs.display !== 'none'
             && cs.visibility !== 'hidden' && el.offsetParent !== null,
      role: el.getAttribute('role') || '',
      inForm: !!el.closest('form'),
    });
  });
  return out;
}"""

JS_RECORDS = """() => {
  const vis = el => {
    const r = el.getBoundingClientRect();
    return r.width > 0 && r.height > 0;
  };
  return Array.from(document.querySelectorAll('.wj-data-item, tbody tr'))
              .filter(vis).length;
}"""

JS_BANNER = """() => {
  // Thông điệp NGOÀI thanh lọc (banner đầu trang) — để phân biệt "im lặng hoàn
  // toàn" với "có báo nhưng sai chỗ", đừng quy oan màn đang báo ở banner.
  const out = [];
  document.querySelectorAll('.alert, .wj-empty-state-title').forEach(el => {
    const t = (el.textContent || '').trim();
    if (t && el.offsetParent !== null) out.push(t.slice(0, 60));
  });
  return out;
}"""

JS_TOTALS = """() => {
  // Màn Báo cáo không có danh sách bản ghi — số đo của nó là ô KPI.
  return Array.from(document.querySelectorAll('.wj-rep-mkpi__value, .wj-rep-kpi__value'))
              .map(el => (el.textContent || '').trim()).join('|');
}"""

JS_PAGER = """() => {
  const cur = document.querySelector('.wj-pagination [aria-current="page"]');
  const links = Array.from(document.querySelectorAll('.wj-pagination a[href]'))
                     .map(a => a.getAttribute('href'));
  return {current: cur ? (cur.textContent || '').trim() : '', links: links};
}"""


def _goto(page, base, path, settle):
    page.goto(base + path, wait_until='domcontentloaded')
    page.wait_for_timeout(settle)


def check_reversed_dates(page, base, settle):
    """Mục 1 — ngày ngược phải 200 + thông điệp, không im lặng trả rỗng."""
    rows = []
    for path, pfrom, pto in DATE_ROUTES:
        sep = '&' if '?' in path else '?'
        url = '%s%s%s=%s&%s=%s' % (path, sep, pfrom, REVERSED[0], pto, REVERSED[1])
        resp = page.goto(base + url, wait_until='domcontentloaded')
        page.wait_for_timeout(settle)
        errs = page.evaluate(JS_ERRORS)
        shown = [e for e in errs if e['shown'] and e['text']]
        rows.append({
            'route': path,
            'status': resp.status if resp else 0,
            'records': page.evaluate(JS_RECORDS),
            'errors_shown': len(shown),
            'message': shown[0]['text'] if shown else '',
            'in_form': shown[0]['inForm'] if shown else False,
            'role_alert': shown[0]['role'] == 'alert' if shown else False,
            'kept_from': page.evaluate(
                "n => { const el = document.querySelector(`[name='${n}']`);"
                " return el ? el.value : null; }", pfrom),
            'kept_to': page.evaluate(
                "n => { const el = document.querySelector(`[name='${n}']`);"
                " return el ? el.value : null; }", pto),
            'banner': page.evaluate(JS_BANNER),
        })
    return rows


def check_filter_resets_page(page, base, settle):
    """Mục 2 — đang ở trang 3 mà đổi lọc thì phải về trang 1."""
    rows = []
    for path, size_param in PAGED_ROUTES:
        _goto(page, base, '%s?%s=%d&page=3' % (path, size_param, SMALL_PAGE), settle)
        form = page.locator('form[method="get"]').first
        if not form.count():
            rows.append({'route': path, 'skipped': 'không có form lọc'})
            continue
        # Submit y như người dùng: gõ khoảng ngày hợp lệ rồi bấm nút tìm.
        filled = page.evaluate(
            """([f, t]) => {
                 const a = document.querySelector(`[name='date_from']`);
                 const b = document.querySelector(`[name='date_to']`);
                 if (!a || !b) return false;
                 a.value = f; b.value = t; return true;
               }""", list(VALID))
        if not filled:
            rows.append({'route': path, 'skipped': 'không có ô ngày'})
            continue
        form.locator('button[type="submit"]').first.click()
        page.wait_for_timeout(settle)
        rows.append({
            'route': path,
            'url_after': page.url.replace(base, ''),
            'has_page_param': 'page=' in page.url.split('?')[-1],
            'pager': page.evaluate(JS_PAGER),
        })
    return rows


def check_pager_keeps_filter(page, base, settle):
    """Mục 3 — sang trang không được rơi điều kiện đang lọc."""
    rows = []
    for path, size_param in PAGED_ROUTES:
        url = '%s?%s=%d&date_from=%s&date_to=%s' % (
            path, size_param, SMALL_PAGE, VALID[0], VALID[1])
        _goto(page, base, url, settle)
        pager = page.evaluate(JS_PAGER)
        keeps = [l for l in pager['links']
                 if 'date_from' in (l or '') and 'date_to' in (l or '')]
        rows.append({
            'route': path,
            'links': len(pager['links']),
            'links_keeping_dates': len(keeps),
            # Không có link nào = mẫu một trang ⇒ KHÔNG kết luận được, phải nói
            # rõ thay vì tính là Pass (bài học "Pass rỗng").
            'inconclusive': not pager['links'],
            'ok': bool(pager['links']) and len(keeps) == len(pager['links']),
        })
    return rows


def check_dates_really_filter(page, base, settle):
    """Mục 4 — ô ngày ở KHỔ ĐIỆN THOẠI phải lọc thật, không chỉ nằm cho đẹp."""
    rows = []
    for path, pfrom, pto in DATE_ROUTES:
        _goto(page, base, path, settle)
        before = page.evaluate(JS_RECORDS)
        totals_before = page.evaluate(JS_TOTALS)
        # Điền + bấm đúng thanh lọc đang NHÌN THẤY ở khổ này, không phải thanh PC
        # ẩn cùng trang — bấm nhầm thanh ẩn là phép đo nói dối.
        submitted = page.evaluate(
            """([f, t, nf, nt]) => {
                 const seen = el => el && el.offsetParent !== null;
                 const a = Array.from(document.querySelectorAll(`[name='${nf}']`))
                                .find(seen);
                 const b = Array.from(document.querySelectorAll(`[name='${nt}']`))
                                .find(seen);
                 if (!a || !b || !a.form) return false;
                 a.value = f; b.value = t;
                 a.form.requestSubmit();
                 return true;
               }""", [EMPTY_WINDOW[0], EMPTY_WINDOW[1], pfrom, pto])
        if not submitted:
            rows.append({'route': path, 'skipped': 'khổ này không có ô ngày'})
            continue
        page.wait_for_load_state('domcontentloaded')
        page.wait_for_timeout(settle)
        qs = page.url.split('?')[-1]
        after = page.evaluate(JS_RECORDS)
        sent = pfrom in qs and pto in qs
        moved = after < before
        if before == 0:
            # Màn không có danh sách (Báo cáo) thì đo KPI — vẫn phải đổi số.
            moved = totals_before != page.evaluate(JS_TOTALS)
        rows.append({
            'route': path,
            'sent_dates': sent,
            'records_before': before,
            'records_after': after,
            'totals_before': totals_before,
            'totals_after': page.evaluate(JS_TOTALS),
            # Không danh sách LẪN không KPI thì không chứng minh được gì — nói
            # thẳng, đừng Pass rỗng.
            'inconclusive': before == 0 and not totals_before,
            'ok': sent and moved,
        })
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--base', default='http://127.0.0.1:8090')
    ap.add_argument('--portal-login', required=True)
    ap.add_argument('--password', default='wujia@test123')
    ap.add_argument('--width', type=int, default=1440)
    ap.add_argument('--settle', type=int, default=450)
    ap.add_argument('--json')
    args = ap.parse_args()

    from playwright.sync_api import sync_playwright
    out = {'base': args.base, 'login': args.portal_login, 'width': args.width}
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        ctx = browser.new_context(viewport={'width': args.width, 'height': 900})
        page = ctx.new_page()
        login(page, args.base, args.portal_login, args.password)
        out['reversed_dates'] = check_reversed_dates(page, args.base, args.settle)
        out['filter_resets_page'] = check_filter_resets_page(page, args.base, args.settle)
        out['pager_keeps_filter'] = check_pager_keeps_filter(page, args.base, args.settle)
        page.set_viewport_size({'width': MOBILE_WIDTH, 'height': 900})
        out['dates_really_filter'] = check_dates_really_filter(
            page, args.base, args.settle)
        browser.close()

    silent = [r for r in out['reversed_dates'] if not r['errors_shown']]
    multi = [r for r in out['reversed_dates'] if r['errors_shown'] > 1]
    lost = [r for r in out['pager_keeps_filter']
            if not r['ok'] and not r['inconclusive']]
    blind = [r for r in out['pager_keeps_filter'] if r['inconclusive']]
    kept_page = [r for r in out['filter_resets_page'] if r.get('has_page_param')]
    dead = [r for r in out['dates_really_filter']
            if not r.get('skipped') and not r['ok']]
    dead_blind = [r for r in out['dates_really_filter'] if r.get('inconclusive')]

    print('\n=== 1. NGÀY NGƯỢC (%d màn) ===' % len(out['reversed_dates']))
    for r in out['reversed_dates']:
        say = r['message'][:46] if r['message'] else (
            ('[banner] ' + r['banner'][0][:36]) if r['banner'] else '— IM LẶNG —')
        print('  %-28s status=%s rec=%-3s lỗi hiện=%s  %s'
              % (r['route'], r['status'], r['records'], r['errors_shown'], say))
    print('\n=== 2. ĐỔI LỌC → TRANG 1 ===')
    for r in out['filter_resets_page']:
        print('  %-28s %s' % (r['route'], r.get('skipped') or r['url_after']))
    print('\n=== 3. SANG TRANG GIỮ LỌC ===')
    for r in out['pager_keeps_filter']:
        print('  %-28s %s/%s link giữ ngày%s' %
              (r['route'], r['links_keeping_dates'], r['links'],
               '  ← KHÔNG KẾT LUẬN ĐƯỢC (một trang)' if r['inconclusive'] else ''))

    print('\n=== 4. NGÀY LỌC THẬT Ở KHỔ %dpx ===' % MOBILE_WIDTH)
    for r in out['dates_really_filter']:
        if r.get('skipped'):
            print('  %-28s %s' % (r['route'], r['skipped']))
            continue
        so = ('rec %s → %s' % (r['records_before'], r['records_after'])
              if r['records_before'] else
              'KPI %s → %s' % (r['totals_before'][:18], r['totals_after'][:18]))
        print('  %-28s gửi ngày=%s  %s%s'
              % (r['route'], 'có' if r['sent_dates'] else 'KHÔNG', so,
                 '  ← KHÔNG KẾT LUẬN ĐƯỢC (mẫu rỗng)' if r['inconclusive'] else ''))

    print('\nIM LẶNG          : %d màn  %s' % (len(silent), [r['route'] for r in silent]))
    print('THÔNG ĐIỆP TRÙNG : %d màn  %s' % (len(multi), [r['route'] for r in multi]))
    print('CÒN page= SAU LỌC: %d màn  %s' % (len(kept_page), [r['route'] for r in kept_page]))
    print('RƠI LỌC KHI SANG TRANG: %d màn %s' % (len(lost), [r['route'] for r in lost]))
    print('KHÔNG ĐỦ DỮ LIỆU ĐỂ ĐO : %d màn %s' % (len(blind), [r['route'] for r in blind]))
    print('NGÀY KHÔNG LỌC THẬT    : %d màn %s' % (len(dead), [r['route'] for r in dead]))
    print('MẪU RỖNG (mục 4)       : %d màn %s'
          % (len(dead_blind), [r['route'] for r in dead_blind]))
    ok = not (silent or multi or lost or kept_page or blind or dead or dead_blind)
    print('\nKẾT LUẬN: %s' % ('ĐẠT' if ok else 'CHƯA ĐẠT'))

    if args.json:
        with open(args.json, 'w', encoding='utf-8') as fh:
            json.dump(out, fh, ensure_ascii=False, indent=1)
        print('→ %s' % args.json)
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
