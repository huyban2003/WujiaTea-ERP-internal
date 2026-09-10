"""Guard phân cấp card Bù hàng — cụm D6 (UAT-BH-007 · UAT-BH-008).

Vì sao phải có guard RIÊNG: `wj_datalist.py` đo *dáng* của item (đệm, bo, cao),
`wj_nesting.py` đo *quan hệ lồng nhau* của khung. Cả hai đều **mù với phân cấp
BÊN TRONG card** — đúng loại lỗ đã để lọt hồi quy "thẻ trắng lồng thẻ trắng"
của D5h.2. Ba đích dưới đây không guard nào hiện có trả lời được.

Ba câu hỏi:

  BH-007  Dòng tên sản phẩm chiếm mấy dòng? Có bị cắt ngay dòng 1 không?
          Acceptance: **tối đa 2 dòng**, `…` chỉ ở cuối dòng 2.
  BH-008  Badge trạng thái phê duyệt và badge tiến độ bù có nằm CÙNG hàng
          không? Acceptance: khác hàng (`top` khác nhau).
  BH-008  Hai ô metadata có thẳng cột giữa các card không? Acceptance: mọi
          card có cùng bộ `left`.

    python3 scripts/qa/wj_returncard.py --base http://127.0.0.1:8080 \
        --portal-login anh.owner [--breakpoints 390 360 991] [--json out.json]
"""
import argparse
import json
import sys

# Nhãn tiến độ bù — nguồn DUY NHẤT là COMPENSATION_STATUS_LABELS
# (wujia_portal_return/controllers/portal.py:69). Chép cứng ở đây thì guard sẽ
# nói dối khi nhãn đổi, nên test Python đọc thẳng hằng đó; script trình duyệt
# này chỉ cần nhận diện badge, và nhận bằng nhãn là cách duy nhất chạy được ở
# mốc "trước" (lúc chưa có class riêng).
COMP_LABELS = ['Chưa xử lý', 'Đã lên đơn bù', 'Đang bù một phần', 'Đã bù đủ']

JS = r"""
(compLabels) => {
  const out = [];
  document.querySelectorAll('.wujia-mreturn-row.wj-data-item').forEach((row) => {
    const code = row.querySelector('.wujia-mreturn-row-code');
    const prod = row.querySelector('.wujia-mreturn-row-product');
    let product = null;
    if (prod) {
      const cs = getComputedStyle(prod);
      let lh = parseFloat(cs.lineHeight);
      if (!isFinite(lh)) lh = parseFloat(cs.fontSize) * 1.2;
      product = {
        text: (prod.textContent || '').trim(),
        clientH: prod.clientHeight,
        scrollH: prod.scrollHeight,
        lineHeight: lh,
        lines: lh > 0 ? Math.round(prod.clientHeight / lh) : null,
        // cắt = nội dung thật cao/rộng hơn ô hiển thị
        truncated: prod.scrollHeight > prod.clientHeight + 1
                   || prod.scrollWidth > prod.clientWidth + 1,
        whiteSpace: cs.whiteSpace,
        lineClamp: cs.webkitLineClamp || cs.lineClamp || 'none',
      };
    }
    const badges = [...row.querySelectorAll('.wujia-badge')].map((b) => {
      const r = b.getBoundingClientRect();
      const label = (b.textContent || '').trim();
      return {
        label,
        kind: compLabels.includes(label) ? 'progress' : 'state',
        top: Math.round(r.top - row.getBoundingClientRect().top),
        h: Math.round(r.height),
      };
    });
    const cells = [...row.querySelectorAll('.wujia-mreturn-row-metacell')].map((c) => {
      const r = c.getBoundingClientRect();
      return { left: Math.round(r.left), label: (c.querySelector('.lbl') || {}).textContent };
    });
    out.push({ code: code ? code.textContent.trim() : null, product, badges, cells });
  });
  return out;
}
"""


def probe(page, base, width, settle):
    page.set_viewport_size({'width': width, 'height': 900})
    page.goto(f'{base}/portal/return', wait_until='load')
    page.wait_for_timeout(settle)
    if '/portal/return' not in page.url:
        raise SystemExit(f'redirect ngầm về {page.url} — số đo sẽ là Pass rỗng')
    return page.evaluate(JS, COMP_LABELS)


def judge(rows):
    """Trả (findings, stats). finding = chuỗi mô tả một vi phạm."""
    bad = []
    n_prod = n_clip = 0
    n_same_row = n_pairs = 0
    for r in rows:
        p = r['product']
        if p and p['text']:
            n_prod += 1
            if p['lines'] and p['lines'] > 2:
                bad.append(f"{r['code']}: tên sản phẩm {p['lines']} dòng (>2)")
            if p['truncated'] and p['lines'] == 1:
                n_clip += 1
                bad.append(f"{r['code']}: tên cắt ngay DÒNG 1 — {p['text'][:38]}…")
        prog = [b for b in r['badges'] if b['kind'] == 'progress']
        state = [b for b in r['badges'] if b['kind'] == 'state']
        if prog and state:
            n_pairs += 1
            if any(abs(a['top'] - b['top']) <= 2 for a in prog for b in state):
                n_same_row += 1
                bad.append(f"{r['code']}: badge tiến độ bù CÙNG hàng với trạng thái")
    # cột metadata: mọi card phải cùng bộ `left`
    layouts = {tuple(c['left'] for c in r['cells']) for r in rows if r['cells']}
    if len(layouts) > 1:
        bad.append(f"metadata lệch cột: {len(layouts)} bố cục khác nhau {sorted(layouts)}")
    return bad, {
        'cards': len(rows), 'có_tên_sp': n_prod, 'cắt_dòng_1': n_clip,
        'cặp_badge': n_pairs, 'badge_cùng_hàng': n_same_row,
        'bố_cục_metadata': len(layouts),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--base', default='http://127.0.0.1:8080')
    ap.add_argument('--portal-login', required=True)
    ap.add_argument('--password', default='wujia@test123')
    ap.add_argument('--breakpoints', nargs='*', type=int, default=[991, 390, 360])
    ap.add_argument('--settle', type=int, default=600)
    ap.add_argument('--json')
    args = ap.parse_args()

    from playwright.sync_api import sync_playwright
    result, total_bad = {}, 0
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_context(viewport={'width': 390, 'height': 900}).new_page()
        page.goto(f'{args.base}/web/login', wait_until='domcontentloaded')
        page.fill('input[name="login"]', args.portal_login)
        page.fill('input[name="password"]', args.password)
        page.press('input[name="password"]', 'Enter')
        page.wait_for_load_state('domcontentloaded')
        if '/web/login' in page.url:
            sys.exit(f'ĐĂNG NHẬP HỎNG cho {args.portal_login!r} — mọi số đo sẽ là Pass rỗng.')

        for w in args.breakpoints:
            rows = probe(page, args.base, w, args.settle)
            bad, stats = judge(rows)
            result[w] = {'stats': stats, 'findings': bad, 'rows': rows}
            total_bad += len(bad)
            print(f"\n=== {w}px === {stats}")
            for b in bad[:12]:
                print('   ✗', b)
            if len(bad) > 12:
                print(f'   … và {len(bad) - 12} vi phạm nữa')
            if not bad:
                print('   ✓ sạch')
        browser.close()

    if args.json:
        with open(args.json, 'w', encoding='utf-8') as fh:
            json.dump(result, fh, ensure_ascii=False, indent=1)
        print(f'\n→ {args.json}')
    print(f'\nTỔNG vi phạm: {total_bad}')
    return 1 if total_bad else 0


if __name__ == '__main__':
    sys.exit(main())
