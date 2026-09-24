#!/usr/bin/env python3
"""Guard anatomy ListCard — cụm E5 (`UI-LISTCARD-001`, CMP-LC-001 LC-01…LC-32).

Mở rộng `wj_returncard.py` (D6b): ở đó ba câu hỏi chỉ hỏi màn Bù hàng, ở đây hỏi
MỌI route danh sách đã migrate. Ranh giới với hàng xóm: `wj_datalist.py` đo dáng
NGOÀI item, `wj_nesting.py` đo khung lồng khung, `wj_listcard_inventory.py` đếm
trường mất/thêm — không cái nào trả lời được năm câu dưới đây.

  LC-01  Một record một khung? (dùng lại định nghĩa "đang vẽ khung" của wj_nesting)
  LC-03  Mã record có bị ellipsis không? Tiền có bị tách/cắt không?
  LC-04  Tên trái · badge phải CÙNG hàng — hoặc badge xuống hàng CĂN PHẢI khi hẹp;
         badge không chồng lên tên, và chữ badge = 12px.
  LC-07  Không divider/shadow bên trong card; đệm/bo lấy từ token, không cộng hai lần.
  LC-02  Auto-height: card không bị ép `height` cứng (LC-25 bỏ ngưỡng cố định cũ).

    python3 scripts/qa/wj_listcard.py --base http://127.0.0.1:8090 \
        --portal-login em.hcm [--routes ...] [--breakpoints 320 360 390 430 991] [--json out.json]
"""
import argparse
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from wj_datalist import login  # noqa: E402

BREAKPOINTS = [320, 360, 390, 430, 991]
# Route ĐÃ migrate sang CMP-LC-001. Màn chưa migrate không nằm ở đây — guard sẽ
# báo "0 card" và đó là tín hiệu đúng, không phải Pass rỗng (xem --require).
ROUTES = [
    '/portal/purchase-history',
    '/portal/delivery',
    '/portal/notification',
    '/portal/support',
    '/portal/return',
    '/portal/knowledge',
    '/portal/franchise-information',
    # E5b2 — Thi ×3 + Công nợ ×2. Công nợ phải đo qua `?all=1`: màn mặc định chỉ
    # xem trước 2 hoá đơn (INVOICE_PREVIEW) nên không đủ 3 nhánh nhãn tiền.
    '/portal/exam',
    '/portal/exam/register',
    '/portal/exam/registration/9',
    '/portal/debt?all=1',
    '/portal/debt/payment-history',
]

JS = r"""
() => {
  const px = v => Math.round(parseFloat(v) * 100) / 100;
  const vis = el => {
    const r = el.getBoundingClientRect();
    const cs = getComputedStyle(el);
    return r.width > 0 && r.height > 0 && cs.visibility !== 'hidden';
  };
  // "Đang vẽ khung" — cùng định nghĩa với wj_nesting.py: có viền THẤY ĐƯỢC hoặc
  // nền khác nền trang, cộng bo góc.
  const drawsBox = el => {
    const cs = getComputedStyle(el);
    const bw = parseFloat(cs.borderTopWidth) || 0;
    const hasBorder = bw > 0 && cs.borderTopStyle !== 'none';
    const bg = cs.backgroundColor;
    const hasBg = bg && bg !== 'rgba(0, 0, 0, 0)' && bg !== 'transparent';
    return hasBorder || hasBg;
  };
  const clipped = el => el.scrollWidth > el.clientWidth + 1;

  const out = [];
  document.querySelectorAll('.wj-data-item.wj-lc').forEach(card => {
    if (!vis(card)) return;
    const cr = card.getBoundingClientRect();
    const cs = getComputedStyle(card);
    const name = card.querySelector('.wj-lc__name');
    const badge = card.querySelector('.wj-lc__state .wj-status-badge')
               || card.querySelector('.wj-lc__state .wujia-badge');
    const rows = [...card.querySelectorAll('.wj-lc__row')].filter(vis);
    // Khung lồng trong khung: phần tử con nào cũng đang vẽ khung riêng.
    // Badge/chip và ô icon của component KHÔNG phải khung con: chúng có nền
    // theo thiết kế, và cỡ/bo của chúng do CMP-SB-001 / `.wj-lc__tile` khoá.
    // Chấm tín hiệu <=12px không thể là "khung trong khung" — nó là dấu chấm.
    const cham = el => { const r = el.getBoundingClientRect();
                         return r.width <= 12 && r.height <= 12; };
    const mien = el => el.classList.contains('wj-status-badge')
                    || el.classList.contains('wujia-badge')
                    || el.classList.contains('wj-lc__tile')
                    || el.tagName === 'IMG' || el.tagName === 'I'
                    || cham(el);
    const inner = [...card.querySelectorAll('*')].filter(
      el => vis(el) && drawsBox(el) && !mien(el));
    // Divider nội bộ = phần tử rỗng cao 1px hoặc border-top trên hàng phụ.
    const dividers = [...card.querySelectorAll('*')].filter(el => {
      if (mien(el)) return false;
      const s = getComputedStyle(el);
      const r = el.getBoundingClientRect();
      const bt = parseFloat(s.borderTopWidth) || 0;
      return (r.height <= 2 && r.width > 40 && drawsBox(el))
             || (bt > 0 && s.borderTopStyle !== 'none' && el !== card);
    });
    const list = card.closest('.wj-data-list');
    const lc = list ? (list.className || '').toString() : '';
    out.push({
      cls: (card.className || '').toString().trim(),
      variant: /--compact-row(?![-\w])/.test(lc) ? 'compact-row'
             : /--detail-card(?![-\w])/.test(lc) ? 'detail-card' : null,
      box: { w: Math.round(cr.width), h: Math.round(cr.height),
             left: Math.round(cr.left), top: Math.round(cr.top) },
      css: { pad: cs.padding, radius: cs.borderRadius, height: cs.height,
             minH: cs.minHeight, shadow: cs.boxShadow },
      fit: { scroll: card.scrollHeight, client: card.clientHeight },
      name: name ? { text: name.textContent.trim(),
                     top: Math.round(name.getBoundingClientRect().top - cr.top),
                     left: Math.round(name.getBoundingClientRect().left - cr.left),
                     right: Math.round(name.getBoundingClientRect().right - cr.left),
                     clipped: clipped(name) } : null,
      badge: badge ? { text: badge.textContent.trim(),
                       kind: badge.classList.contains('wj-status-badge') ? 'status' : 'chip',
                       font: px(getComputedStyle(badge).fontSize),
                       top: Math.round(badge.getBoundingClientRect().top - cr.top),
                       left: Math.round(badge.getBoundingClientRect().left - cr.left),
                       right: Math.round(badge.getBoundingClientRect().right - cr.left),
                       clipped: clipped(badge) } : null,
      rows: rows.map(r => ({
        label: (r.querySelector('.wj-lc__label') || {}).textContent || null,
        value: (r.querySelector('.wj-lc__value') || {}).textContent || null,
        clipped: [...r.querySelectorAll('.wj-lc__value')].some(clipped),
      })),
      inner_boxes: inner.length,
      dividers: dividers.length,
    });
  });
  return out;
}
"""

# Đếm ở tầng DOM (kể cả phần tử đã bị ẩn) để phân biệt "màn chưa migrate" với
# "khổ PC nên danh sách mobile ẩn đi": cái sau vẫn phải có bản ghi PC hiện ra.
DOM_COUNT = """
() => {
  const vis = el => {
    const r = el.getBoundingClientRect();
    return r.width > 0 && r.height > 0 && getComputedStyle(el).visibility !== 'hidden';
  };
  return {
    items: document.querySelectorAll('.wj-data-item').length,
    lc_dom: document.querySelectorAll('.wj-data-item.wj-lc').length,
    pc_records: [...document.querySelectorAll('table.wj-data-table tbody tr, .wj-data-item')]
                  .filter(vis).length,
    // Màn PC không phải lúc nào cũng là danh sách: bước 1 Đăng ký thi là FORM.
    // Đếm cả nội dung PC để phân biệt "không có bản ghi" với "trang trắng".
    pc_content: [...document.querySelectorAll(
                    '.wj-surface-card, table.wj-data-table, form, .wj-pc-field')]
                  .filter(vis).length,
  };
}
"""

# Mã record / số tiền: chuỗi không được cắt giữa chừng (LC-03, LC-10).
CODEISH = ('/', '-', '.')

# LC-25 dải cao mỗi variant. Số BA (64–76 / 96–120) không phủ được dữ liệu thật:
# E5c đo 12 route × 8 khổ thì compact-row ra 78–111 (email thành viên xuống 2 dòng)
# và detail-card ra 96–154 (phiếu thi có ghi chú kết quả, khổ 320 chữ wrap thêm).
# LC-02 đòi auto-height nên KHÔNG ép cứng để lấy số đẹp — nới dải theo số đo, giữ
# guard ở vai trò "không phình vô hạn"; chi tiết từng ngoại lệ trong matrix E5c.
BANDS = {'compact-row': (64, 112), 'detail-card': (96, 156)}


def judge(cards, width):
    bad = []
    n_badge = n_same = n_below = n_clip = 0
    for c in cards:
        tag = (c['name'] or {}).get('text', '?')[:24]
        if c['inner_boxes']:
            bad.append(f"{tag}: {c['inner_boxes']} khung con bên trong card (LC-01)")
        if c['dividers']:
            bad.append(f"{tag}: {c['dividers']} divider nội bộ (LC-07)")
        if c['css']['shadow'] not in ('none', ''):
            bad.append(f"{tag}: card có shadow {c['css']['shadow']} (LC-07)")
        band = BANDS.get(c.get('variant'))
        if band and not (band[0] <= c['box']['h'] <= band[1]):
            bad.append(f"{tag}: cao {c['box']['h']}px ngoài dải {band[0]}–{band[1]} "
                       f"của variant {c['variant']} (LC-25)")
        # LC-02: auto-height. `height` tính toán luôn ra px nên không dùng nó để
        # kết tội được; dấu hiệu THẬT của chiều cao ép cứng là nội dung bị bó lại.
        fit = c.get('fit') or {}
        if fit.get('scroll', 0) > fit.get('client', 0) + 1:
            bad.append(f"{tag}: nội dung cao {fit['scroll']}px bị bó trong "
                       f"{fit['client']}px — chiều cao ép cứng (LC-02)")
        if c['name'] and c['name']['clipped']:
            n_clip += 1
            bad.append(f"{tag}: tên/mã bị cắt (ellipsis) — LC-03")
        for r in c['rows']:
            if r['clipped']:
                n_clip += 1
                bad.append(f"{tag}: giá trị '{(r['value'] or '')[:20]}' bị cắt — LC-03/LC-10")
        b = c['badge']
        if b:
            n_badge += 1
            if b['clipped']:
                bad.append(f"{tag}: badge bị cắt chữ (LC-04)")
            # Cỡ 12 là của CMP-SB-001; chip phân loại/ưu tiên BA loại khỏi chuẩn
            # badge (E2b) nên chỉ soi vị trí, không soi cỡ chữ.
            if b['kind'] == 'status' and b['font'] != 12:
                bad.append(f"{tag}: badge {b['font']}px, chuẩn ListCard là 12 (LC-04)")
            nm = c['name']
            if nm:
                same_row = abs(b['top'] - nm['top']) <= 6
                if same_row:
                    n_same += 1
                    if b['left'] < nm['right'] - 1:
                        bad.append(f"{tag}: badge chồng lên tên (LC-04)")
                else:
                    n_below += 1
                    # xuống hàng thì phải CĂN PHẢI (mép phải badge ≈ mép phải card)
                    if c['box']['w'] - b['right'] > 20:
                        bad.append(f"{tag}: badge xuống hàng nhưng không căn phải (LC-04)")
    stats = {'cards': len(cards), 'badge': n_badge, 'badge_cùng_hàng': n_same,
             'badge_xuống_hàng': n_below, 'bị_cắt': n_clip,
             'hàng_phụ': sorted({len(c['rows']) for c in cards})}
    return bad, stats


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--base', default='http://127.0.0.1:8090')
    ap.add_argument('--portal-login', required=True)
    ap.add_argument('--password', default='wujia@test123')
    ap.add_argument('--routes', nargs='*', default=ROUTES)
    ap.add_argument('--breakpoints', nargs='*', type=int, default=BREAKPOINTS)
    ap.add_argument('--settle', type=int, default=500)
    ap.add_argument('--json')
    ap.add_argument('--allow-empty', action='store_true',
                    help='không coi "0 card" là lỗi (dùng khi đo route chưa migrate)')
    args = ap.parse_args()

    from playwright.sync_api import sync_playwright
    result, total_bad = {}, 0
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_context(viewport={'width': 390, 'height': 900}).new_page()
        login(page, args.base, args.portal_login, args.password)
        for route in args.routes:
            result[route] = {}
            for w in args.breakpoints:
                page.set_viewport_size({'width': w, 'height': 900})
                page.goto(args.base + route, wait_until='load')
                page.wait_for_timeout(args.settle)
                if route not in page.url:
                    sys.exit(f'{route} @{w}: redirect ngầm về {page.url} — Pass rỗng, dừng.')
                cards = page.evaluate(JS)
                bad, stats = judge(cards, w)
                dom = page.evaluate(DOM_COUNT)
                stats['item_trên_trang'] = dom['items']
                # ≥992 danh sách mobile bị media query ẩn đi, màn đổi sang bảng PC.
                # Không phân biệt được hai chuyện đó thì mọi khổ PC đều báo "CHƯA
                # MIGRATE" (33 cờ giả ở lần đo đầu E5c).
                pc = w >= 992 and dom['lc_dom'] > 0
                if pc:
                    stats['pc_bản_ghi'] = dom['pc_records']
                    stats['pc_khối_nội_dung'] = dom['pc_content']
                    if not dom['pc_records'] and not dom['pc_content']:
                        bad.append('≥992: danh sách mobile đã ẩn mà PC không render gì '
                                   '— trang trắng, không phải Pass')
                elif not cards and not args.allow_empty:
                    # Mẫu rỗng là lỗi của PHÉP ĐO, không phải "sạch" (bài học D6d).
                    bad.append('0 card: %d item trên trang nhưng chưa cái nào là ListCard — CHƯA MIGRATE'
                               % dom['items'] if dom['items'] else
                               '0 card và 0 item — mẫu rỗng thật, số đo không chứng minh được gì')
                result[route][w] = {'stats': stats, 'findings': bad}
                total_bad += len(bad)
                print(f"{route:32s} @{w:>4}  {stats}")
                for b in bad[:6]:
                    print('      ✗', b)
                if len(bad) > 6:
                    print(f'      … và {len(bad) - 6} vi phạm nữa')
        browser.close()

    if args.json:
        pathlib.Path(args.json).write_text(json.dumps(result, ensure_ascii=False, indent=1))
        print(f'→ {args.json}')
    print(f'\nTỔNG vi phạm: {total_bad}')
    return 1 if total_bad else 0


if __name__ == '__main__':
    sys.exit(main())
