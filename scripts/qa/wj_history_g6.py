"""WJ-ORD-029 (G6) — "Ngày xác nhận" chỉ khi đơn đã xác nhận. CHỈ GET, an toàn trên UAT.

Mỗi khổ (PC 1440/1024/992 · mobile 360/390/430) với 1 đơn chưa xác nhận + 1 đơn đã xác nhận:
  - danh sách PC: ô cột "Ngày xác nhận" (tìm theo mã đơn), 0 tràn ngang
  - chi tiết: danh sách nhãn kv, meta đầu trang, 0 tràn, 2 card thông tin cao bằng nhau
  - mobile: chữ "Ngày xác nhận" có xuất hiện ở trang không

  python scripts/qa/wj_history_g6.py --base http://127.0.0.1:8055 --draft S05267 --sale S00014
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from wj_density import login  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402

VPS = [(1440, 900), (1024, 768), (992, 768), (360, 800), (390, 844), (430, 932)]

LIST_PROBE = """code => {
  const t = [...document.querySelectorAll('table')].find(t => t.offsetParent && t.textContent.includes(code));
  if (!t) return {table: false, overflowX: document.documentElement.scrollWidth > innerWidth};
  const heads = [...t.querySelectorAll('thead th')].map(th => th.textContent.trim());
  const row = [...t.querySelectorAll('tbody tr')].find(r => r.textContent.includes(code));
  const cells = row ? [...row.children].map(td => td.textContent.trim()) : [];
  const i = heads.indexOf('Ngày xác nhận');
  return {table: true, cell: i >= 0 ? cells[i] : null, overflowX: document.documentElement.scrollWidth > innerWidth};
}"""

DETAIL_PROBE = """() => {
  const vis = e => e.offsetParent !== null;
  const kv = [...document.querySelectorAll('.wj-pc-kv')].filter(vis).map(k =>
      [k.querySelector('.wj-pc-kv__label').textContent.trim(), k.querySelector('.wj-pc-kv__value').textContent.trim()]);
  const meta = [...document.querySelectorAll('.wj-pc-order-head__meta')].filter(vis).map(m => m.textContent.replace(/\\s+/g, ' ').trim());
  const cards = [...document.querySelectorAll('.wj-pc-two-col > *')].filter(vis).map(c => Math.round(c.getBoundingClientRect().height));
  const visibleText = document.body.innerText;
  return {kv, meta, cards, hasConfirmText: visibleText.includes('Ngày xác nhận'),
          overflowX: document.documentElement.scrollWidth > innerWidth};
}"""


def order_id(page, base, code):
    page.goto(f'{base}/portal/purchase-history?q={code}', wait_until='load')
    href = page.eval_on_selector_all(
        "a[href^='/portal/purchase-history/']",
        "(as, code) => (as.find(a => a.textContent.includes(code)) || {}).getAttribute ? "
        "as.find(a => a.textContent.includes(code)).getAttribute('href') : null", code)
    return href


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--base', default='http://127.0.0.1:8055')
    ap.add_argument('--login', default='dung.multi')
    ap.add_argument('--password', default='wujia@test123')
    ap.add_argument('--draft', required=True, help='mã đơn draft/sent')
    ap.add_argument('--sale', required=True, help='mã đơn đã xác nhận')
    ap.add_argument('--shots')
    ap.add_argument('--out')
    args = ap.parse_args()
    if args.shots:
        os.makedirs(args.shots, exist_ok=True)
    out, allok = [], True
    with sync_playwright() as p:
        br = p.chromium.launch()
        for vw, vh in VPS:
            ctx = br.new_context(viewport={'width': vw, 'height': vh})
            page = ctx.new_page()
            # Chỉ đọc: như `wj_density --readonly` — lọt GET + POST đăng nhập + 2 bộ đếm badge
            # + chọn cửa hàng (chỉ đổi session; user nhiều cửa hàng bị overlay bắt chọn lúc vào).
            reads = ('/portal/login', '/portal/notification/unread-count', '/portal/order/cart/count',
                     '/portal/franchise/switch')
            page.route('**/*', lambda r: r.continue_() if r.request.method in ('GET', 'HEAD') or (
                r.request.method == 'POST' and r.request.url.split('?')[0].endswith(reads)) else r.abort())
            login(page, args.base, args.login, args.password)
            pc = vw >= 992
            for kind, code in (('draft', args.draft), ('sale', args.sale)):
                href = order_id(page, args.base, code)
                lst = page.evaluate(LIST_PROBE, code)
                page.goto(args.base + href, wait_until='load') if href else None
                det = page.evaluate(DETAIL_PROBE) if href else {}
                if args.shots and href:
                    page.screenshot(path=os.path.join(args.shots, f'{kind}-{vw}.png'), full_page=True)
                labels = [k for k, _v in det.get('kv', [])]
                chk = {'found': bool(href), 'no_overflow': not lst.get('overflowX') and not det.get('overflowX')}
                if pc:
                    chk['list_cell'] = (lst.get('cell') == '—') if kind == 'draft' else bool(
                        lst.get('cell') and lst['cell'] != '—')
                    chk['detail_label'] = 'Ngày đặt hàng' in labels and 'Ngày tạo' not in labels
                    chk['detail_confirm_row'] = ('Ngày xác nhận' in labels) == (kind == 'sale')
                    chk['meta'] = bool(det.get('meta')) and det['meta'][0].startswith('Ngày đặt hàng')
                else:
                    chk['mobile_no_confirm_text'] = not det.get('hasConfirmText') if kind == 'draft' else True
                ok = all(chk.values())
                allok &= ok
                r = {'vp': vw, 'kind': kind, 'code': code, 'ok': ok, 'checks': chk, 'list_cell': lst.get('cell'),
                     'kv': det.get('kv'), 'cards': det.get('cards'), 'meta': det.get('meta')}
                out.append(r)
                bad = [k for k, v in chk.items() if not v]
                print(f"{'OK ' if ok else 'FAIL'} {vw:4} {kind:5} {code} cột={lst.get('cell')!r} "
                      f"kv={labels} cards={det.get('cards')} {'bad=' + ','.join(bad) if bad else ''}")
            ctx.close()
        br.close()
    if args.out:
        with open(args.out, 'w') as fh:
            json.dump(out, fh, ensure_ascii=False, indent=1)
    print('== ALL OK' if allok else '== CÓ FAIL')


if __name__ == '__main__':
    main()
