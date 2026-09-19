#!/usr/bin/env python3
"""Kiểm kê TRƯỜNG của từng record trên trang danh sách — mốc trước/sau cụm E5.

Vì sao phải có: `UI-LISTCARD-001` đổi ANATOMY bên trong item, còn BA đòi
"giữ toàn bộ dữ liệu hiện có" (LC-09) và "có checklist field trước/sau mỗi
route". `wj_datalist.py` đo DÁNG item, `wj_nesting.py` đo quan hệ lồng nhau —
cả hai đều mù với việc một trường biến mất khi dựng lại ruột card.

Ba thứ tool này ghi cho mỗi route × khổ:
  1. items[]  — mỗi record: lớp CSS, văn bản của mọi nút LÁ (= trường nhìn thấy),
                badge, link. So sánh trước/sau bằng ĐA TẬP văn bản, không theo
                thứ tự (LC-05 cho phép đổi bố cục, không cho mất trường).
  2. dom_sha  — sha256 của outerHTML đã chuẩn hoá khoảng trắng, cho những vùng
                PHẢI không đổi một byte: Home preview (LC-23) + bảng PC.
  3. gap/nhịp — khoảng cách thanh lọc → danh sách (nợ G2) và gutter trái/phải.

    python3 scripts/qa/wj_listcard_inventory.py --base http://127.0.0.1:8090 \
        --portal-login em.hcm --out docs/e5-field-inventory.json
    python3 scripts/qa/wj_listcard_inventory.py ... --diff docs/e5-field-inventory.json
"""
import argparse
import hashlib
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from wj_datalist import login  # noqa: E402

BREAKPOINTS = [390, 1440]
ROUTES = [
    '/portal',
    '/portal/purchase-history',
    '/portal/delivery',
    '/portal/notification',
    '/portal/support',
    '/portal/return',
    '/portal/knowledge',
    '/portal/exam',
    '/portal/exam/register',
    '/portal/debt',
    '/portal/debt/payment-history',
    '/portal/franchise-information',
    '/portal/order',
]

PROBE = r"""
() => {
  const norm = s => (s || '').replace(/\s+/g, ' ').trim();
  const vis = el => {
    const r = el.getBoundingClientRect();
    const cs = getComputedStyle(el);
    return r.width > 0 && r.height > 0 && cs.visibility !== 'hidden' && cs.display !== 'none';
  };
  // Trường nhìn thấy = nút LÁ có chữ. Lấy cả nút có con nhưng chỉ chứa text node
  // trực tiếp (vd <span>Mã: <b>X</b></span> ⇒ vẫn tách được hai mảnh).
  const leaves = (root) => {
    const out = [];
    root.querySelectorAll('*').forEach(el => {
      if (!vis(el)) return;
      const own = [...el.childNodes]
        .filter(n => n.nodeType === 3)
        .map(n => norm(n.textContent))
        .filter(Boolean)
        .join(' ');
      if (!own) return;
      const cls = (el.className || '').toString().trim();
      // Nhãn vs GIÁ TRỊ: LC-15 bắt đổi nhãn ("Ngày YC" → "Ngày yêu cầu") nên so
      // chung một rổ là báo động giả. Giá trị mới là thứ cấm mất (LC-09).
      const isLabel = /(^|[\s-])(lbl|label|collabel)([\s-]|$)|__label|-label\b/.test(cls)
                      || /:$/.test(own);
      out.push({ cls: cls, text: own, kind: isLabel ? 'label' : 'value' });
    });
    return out;
  };

  const out = { items: [], regions: [], rhythm: null, errors: [] };

  document.querySelectorAll('.wj-data-item').forEach(it => {
    if (!vis(it)) return;
    const cs = getComputedStyle(it);
    const r = it.getBoundingClientRect();
    out.items.push({
      cls: (it.className || '').toString().trim(),
      tag: it.tagName.toLowerCase(),
      box: { w: Math.round(r.width), h: Math.round(r.height),
             left: Math.round(r.left), top: Math.round(r.top) },
      pad: cs.padding, radius: cs.borderRadius,
      fields: leaves(it),
      badges: [...it.querySelectorAll('.wj-status-badge, .wujia-badge')]
        .filter(vis).map(b => ({ text: norm(b.textContent),
                                 cls: (b.className || '').toString().trim(),
                                 font: getComputedStyle(b).fontSize,
                                 left: Math.round(b.getBoundingClientRect().left),
                                 top: Math.round(b.getBoundingClientRect().top) })),
      links: [...it.querySelectorAll('a[href]')].map(a => a.getAttribute('href')),
      href: it.tagName === 'A' ? it.getAttribute('href') : null,
    });
  });

  // Vùng phải bất biến: mọi .wj-data-list + mọi bảng PC.
  document.querySelectorAll('.wj-data-list, table.wj-data-table').forEach(z => {
    if (!vis(z)) return;
    out.regions.push({
      cls: (z.className || '').toString().trim(),
      html: z.outerHTML.replace(/\s+/g, ' ').trim(),
    });
  });
  // Màn không có danh sách nào (Đặt hàng) thì chữ ký vùng là RỖNG — so hai mốc
  // rỗng luôn bằng nhau, tức "trước = sau" ở đó không chứng minh gì (E5b2 ghi
  // nhận). Lấy chữ ký CẢ VÙNG NỘI DUNG, trừ những chỗ vốn đổi theo phiên.
  if (!out.regions.length) {
    const main = document.querySelector('.wujia-mpage, .content-wrapper, .app-content');
    if (main && vis(main)) {
      const c = main.cloneNode(true);
      // Biểu đồ dựng bằng JS (ApexCharts) có id ngẫu nhiên + toạ độ theo hoạt hình
      // ⇒ không bao giờ trùng byte giữa hai lượt; bỏ ra khỏi chữ ký.
      c.querySelectorAll('[data-wj-volatile], .wj-cart-count, .wujia-mheader-badge, time,'
                       + ' .apexcharts-canvas, canvas, .resize-triggers, .resize-sensor')
       .forEach(e => e.remove());
      out.regions.push({
        cls: 'WHOLE:' + (main.className || '').toString().trim(),
        html: c.outerHTML.replace(/\s+/g, ' ').trim(),
      });
    }
  }

  // Nhịp G2: đáy thẻ lọc → đỉnh PHẦN TỬ KẾ TIẾP (đo tới danh sách thì dính cả
  // count-meta/section-header xen giữa, ra 52/55/70 và che mất con số thật 24).
  const fc = [...document.querySelectorAll('.wj-filter-card')].filter(vis)[0];
  const dl = [...document.querySelectorAll('.wj-data-list')].filter(vis)[0];
  if (fc) {
    const a = fc.getBoundingClientRect();
    let sib = fc.nextElementSibling;
    while (sib && !vis(sib)) sib = sib.nextElementSibling;
    out.rhythm = {
      filter_to_next: sib ? Math.round(sib.getBoundingClientRect().top - a.bottom) : null,
      next_cls: sib ? (sib.className || '').toString().trim() : null,
      filter_to_list: dl ? Math.round(dl.getBoundingClientRect().top - a.bottom) : null,
      filter_mb: getComputedStyle(fc).marginBottom,
    };
  }
  // Gutter trang: lấy từ chính item (ListCard không được tự thêm gutter — LC-08).
  const first = [...document.querySelectorAll('.wj-data-item')].filter(vis)[0];
  if (first) {
    const r = first.getBoundingClientRect();
    out.gutter = {
      left: Math.round(r.left),
      right: Math.round(document.documentElement.clientWidth - r.right),
    };
  }
  return out;
}
"""


def sha(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()[:16]


def run(args):
    from playwright.sync_api import sync_playwright
    result = {'base': args.base, 'login': args.portal_login, 'routes': {}}
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        ctx = browser.new_context(viewport={'width': 1440, 'height': 900})
        page = ctx.new_page()
        js_errors = []
        page.on('pageerror', lambda e: js_errors.append(str(e)))
        login(page, args.base, args.portal_login, args.password)

        for route in args.routes:
            result['routes'][route] = {}
            for w in args.breakpoints:
                page.set_viewport_size({'width': w, 'height': 900})
                before = len(js_errors)
                resp = page.goto(args.base + route, wait_until='load')
                page.wait_for_timeout(args.settle)
                data = page.evaluate(PROBE)
                data['status'] = resp.status if resp else None
                data['final_url'] = page.url
                data['js_errors'] = js_errors[before:]
                data['scroll_x'] = page.evaluate(
                    '() => document.documentElement.scrollWidth - document.documentElement.clientWidth')
                for reg in data['regions']:
                    reg['sha'] = sha(reg.pop('html'))
                result['routes'][route][str(w)] = data
        browser.close()
    return result


def _fields(data, kind='value'):
    """Đa tập văn bản của trường trong mọi item của một route×khổ."""
    bag = {}
    for it in data.get('items', []):
        for f in it.get('fields', []):
            if f.get('kind', 'value') != kind:
                continue
            bag[f['text']] = bag.get(f['text'], 0) + 1
    return bag


def diff(old, new, frozen):
    rows = []
    for route, widths in new['routes'].items():
        for w, data in widths.items():
            prev = old.get('routes', {}).get(route, {}).get(w)
            if prev is None:
                rows.append((route, w, 'MỚI', 'không có ở mốc trước'))
                continue
            a, b = _fields(prev), _fields(data)
            lost = {k: v for k, v in a.items() if b.get(k, 0) < v}
            added = {k: v for k, v in b.items() if a.get(k, 0) < v}
            if lost:
                rows.append((route, w, 'MẤT GIÁ TRỊ', '; '.join(list(lost)[:5])))
            if added:
                rows.append((route, w, 'THÊM GIÁ TRỊ', '; '.join(list(added)[:5])))
            la, lb = _fields(prev, 'label'), _fields(data, 'label')
            if set(la) != set(lb):
                gone = sorted(set(la) - set(lb))
                new_ = sorted(set(lb) - set(la))
                rows.append((route, w, 'nhãn đổi (ok)',
                             f"-{gone} +{new_}"))
            if len(prev.get('items', [])) != len(data.get('items', [])):
                rows.append((route, w, 'LỆCH SỐ RECORD',
                             f"{len(prev.get('items', []))} → {len(data.get('items', []))}"))
            # So KHỚP ĐÚNG route, không theo tiền tố: `--frozen /portal` mà so tiền tố
            # thì mọi route portal đều bị coi là đóng băng.
            if route.split('?')[0] in {f.split('?')[0] for f in frozen}:
                pa = [r['sha'] for r in prev.get('regions', [])]
                pb = [r['sha'] for r in data.get('regions', [])]
                if not pa and not pb:
                    rows.append((route, w, 'MỐC RỖNG',
                                 'route đóng băng không có vùng nào để so — phép đo vô nghĩa'))
                elif pa != pb:
                    rows.append((route, w, 'DOM ĐỔI', 'vùng phải bất biến đã đổi byte'))
            if data.get('scroll_x', 0) > 0:
                rows.append((route, w, 'TRÀN NGANG', str(data['scroll_x'])))
            if data.get('js_errors'):
                rows.append((route, w, 'LỖI JS', data['js_errors'][0][:60]))
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--base', default='http://127.0.0.1:8090')
    ap.add_argument('--portal-login', required=True)
    ap.add_argument('--password', default='wujia@test123')
    ap.add_argument('--routes', nargs='*', default=ROUTES)
    ap.add_argument('--breakpoints', nargs='*', type=int, default=BREAKPOINTS)
    ap.add_argument('--settle', type=int, default=400)
    ap.add_argument('--out')
    ap.add_argument('--diff', help='file mốc trước để so')
    ap.add_argument('--frozen', nargs='*', default=['/portal/order'],
                    help='route mà DOM phải không đổi một byte')
    args = ap.parse_args()

    res = run(args)
    n_items = sum(len(d.get('items', []))
                  for r in res['routes'].values() for d in r.values())
    print(f"Đã đo {len(res['routes'])} route × {len(args.breakpoints)} khổ — {n_items} record.")
    for route, widths in res['routes'].items():
        for w, d in widths.items():
            n = len(d.get('items', []))
            # @>=992 không có card là ĐÚNG (PC dùng bảng) — chỉ cảnh báo khổ mobile.
            flag = '' if (n or int(w) >= 992) else '  ⚠ MẪU RỖNG'
            print(f"  {route:38s} @{w:>4}  status={d['status']}  items={n:<3}{flag}")

    if args.out:
        pathlib.Path(args.out).write_text(json.dumps(res, ensure_ascii=False, indent=1))
        print(f"→ {args.out}")
    if args.diff:
        old = json.loads(pathlib.Path(args.diff).read_text())
        rows = diff(old, res, args.frozen)
        print(f"\n=== DIFF với {args.diff}: {len(rows)} vấn đề ===")
        for r in rows:
            print('  {:38s} @{:>4}  {:<16s} {}'.format(*r))
        return 1 if rows else 0
    return 0


if __name__ == '__main__':
    sys.exit(main())
