"""WJ-ORD-028 (G5) — hộp xác nhận trước khi gửi đơn, đo đầu-cuối bằng trình duyệt thật.

⚠️ TẠO ĐƠN THẬT — chỉ chạy trên DB copy (mặc định từ chối host khác 127.0.0.1/localhost).
Đếm đơn qua Postgres (không qua giao diện) để kết luận "0 đơn / đúng 1 đơn" không phụ thuộc UI.

Mỗi khổ (PC trang giỏ · PC panel ở trang Đặt hàng · mobile trang giỏ):
  1. bấm "Gửi đơn đặt hàng" → hộp hiện, 0 POST, 0 đơn mới; nội dung hộp khớp giỏ (+ ghi chú đang gõ)
  2. Hủy · Esc · bấm nền → hộp đóng, giỏ nguyên, 0 đơn; focus về nút mở
  3. Xác nhận bấm 2 lần liên tiếp → đúng 1 POST, đúng 1 đơn, giỏ rỗng, về màn kết quả
  4. Back về giỏ (bản BFCache còn hàng) → gửi lại → KHÔNG thêm đơn, về đúng đơn vừa tạo
  5. F5 màn kết quả → không thêm đơn

  python scripts/qa/wj_order_confirm.py --base http://127.0.0.1:8055 --db wujia_g5s [--shots DIR]
"""
import argparse
import os
import sys
from urllib.parse import urlparse



sys.path.insert(0, os.path.dirname(__file__))
from wj_density import login  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402

CASES = [
    # (tên, viewport, trang chứa nút gửi, selector nút mở)
    ('pc-cart', (1440, 900), '/portal/order/cart', '.wj-pc-cart-submit'),
    ('pc-catalog', (1280, 800), '/portal/order', '.wj-pc-cart-submit'),
    ('m-cart', (390, 844), '/portal/order/cart', '.wujia-mcart-submit'),
    ('m-cart-360', (360, 800), '/portal/order/cart', '.wujia-mcart-submit'),
]

MODAL_PROBE = """() => {
  const m = document.getElementById('wjOrderConfirm');
  if (!m || m.hidden) return {open: false};
  const p = m.querySelector('.wj-order-confirm__panel').getBoundingClientRect();
  const val = k => (m.querySelector("[data-wj-oc='" + k + "']") || {}).textContent;
  const btns = [...m.querySelectorAll('[data-wj-oc-action]')].map(b => {
    const r = b.getBoundingClientRect(); return {a: b.dataset.wjOcAction, h: Math.round(r.height), txt: b.textContent.trim()};
  });
  return {open: true, store: val('store'), lines: val('lines'), qty: val('qty'), total: val('total'), note: val('note'),
          panel: [Math.round(p.left), Math.round(p.top), Math.round(p.right), Math.round(p.bottom)],
          vw: innerWidth, vh: innerHeight, focus: document.activeElement && document.activeElement.dataset.wjOcAction,
          overflowX: document.documentElement.scrollWidth > innerWidth, btns};
}"""


def so_count(cr, fid):
    cr.execute("SELECT count(*) FROM sale_order WHERE franchise_id=%s AND is_portal_order", (fid,))
    return cr.fetchone()[0]


def cart_lines(cr, fid):
    cr.execute("""SELECT count(l.id) FROM wujia_portal_cart c LEFT JOIN wujia_portal_cart_line l
                  ON l.cart_id=c.id WHERE c.franchise_id=%s""", (fid,))
    return cr.fetchone()[0]


def fill_cart(page, base):
    page.goto(base + '/portal/order', wait_until='load')
    pids = page.eval_on_selector_all('[data-product-id]', 'es => [...new Set(es.map(e => e.dataset.productId))]')
    for pid in pids[:2]:
        page.evaluate("""pid => fetch('/portal/order/cart/add', {method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({jsonrpc: '2.0', method: 'call', params: {product_id: parseInt(pid)}})})
            .then(r => r.json())""", pid)


def run_case(br, args, cr, fid, name, vp, path, opener, shots):
    res = {'case': name, 'checks': {}}
    chk = res['checks']
    ctx = br.new_context(viewport={'width': vp[0], 'height': vp[1]})
    page = ctx.new_page()
    posts = []
    page.on('request', lambda r: posts.append(r.url) if r.method == 'POST' and r.url.endswith('/portal/order/submit') else None)
    login(page, args.base, args.login, args.password)
    fill_cart(page, args.base)
    page.goto(args.base + path, wait_until='load')
    page.wait_for_timeout(500)
    n0, l0 = so_count(cr, fid), cart_lines(cr, fid)
    note = page.locator('form[data-wj-confirm-form]:visible textarea[name=portal_note]')
    note.fill(f'Ghi chú G5 {name}\ndòng 2')
    page.wait_for_timeout(300)

    # 1 — mở hộp, chưa tạo gì
    page.locator(opener).click()
    page.wait_for_timeout(400)
    m = page.evaluate(MODAL_PROBE)
    form = page.locator('form[data-wj-confirm-form]:visible')
    chk['1_open_no_post'] = m['open'] and not posts and so_count(cr, fid) == n0
    chk['1_content'] = (m.get('lines') == form.get_attribute('data-oc-lines') and
                        m.get('qty') == form.get_attribute('data-oc-qty') and
                        m.get('total') == form.get_attribute('data-oc-total') and
                        m.get('store') not in ('', '—', None) and m.get('note') == f'Ghi chú G5 {name}\ndòng 2')
    chk['1_geometry'] = (m['panel'][0] >= 0 and m['panel'][2] <= m['vw'] and m['panel'][3] <= m['vh']
                         and not m['overflowX'] and all(b['h'] >= 40 for b in m['btns']))
    chk['1_focus_cancel'] = m.get('focus') == 'cancel'
    res['modal'] = m
    if shots:
        page.screenshot(path=os.path.join(shots, f'{name}-modal.png'))

    # 2 — ba cách huỷ
    closes = {}
    for how in ('cancel', 'esc', 'backdrop'):
        if how != 'cancel':
            page.locator(opener).click()
            page.wait_for_timeout(300)
        if how == 'cancel':
            page.locator("[data-wj-oc-action='cancel']").click()
        elif how == 'esc':
            page.keyboard.press('Escape')
        else:
            page.mouse.click(5, vp[1] - 5)
        page.wait_for_timeout(300)
        closes[how] = not page.evaluate(MODAL_PROBE)['open']
    focus_back = page.evaluate("() => document.activeElement && document.activeElement.hasAttribute('data-wj-confirm-open')")
    chk['2_cancel_all'] = all(closes.values()) and not posts
    chk['2_nothing_changed'] = so_count(cr, fid) == n0 and cart_lines(cr, fid) == l0 and l0 > 0
    chk['2_focus_back'] = bool(focus_back)
    res['closes'] = closes

    # 3 — xác nhận, bấm 2 lần
    page.locator(opener).click()
    page.wait_for_timeout(300)
    confirm = page.locator("[data-wj-oc-action='confirm']")
    confirm.dblclick(no_wait_after=True)
    page.wait_for_load_state('load')
    page.wait_for_timeout(1500)
    n1 = so_count(cr, fid)
    result_url = page.url
    chk['3_one_post'] = len(posts) == 1
    chk['3_one_order'] = n1 == n0 + 1
    chk['3_cart_empty'] = cart_lines(cr, fid) == 0
    exp = '/portal/order/submitted/' if name.startswith('m-') else '/portal/purchase-history/'
    chk['3_result_page'] = exp in result_url
    cr.execute("SELECT id FROM sale_order WHERE franchise_id=%s AND is_portal_order ORDER BY id DESC LIMIT 1", (fid,))
    new_id = cr.fetchone()[0]
    cr.execute("SELECT portal_note FROM sale_order WHERE id=%s", (new_id,))
    chk['3_note_saved'] = (cr.fetchone()[0] or '').startswith(f'Ghi chú G5 {name}')

    # 4 — Back (trang giỏ còn hàng) rồi gửi lại
    page.go_back(wait_until='load')
    page.wait_for_timeout(600)
    back_has_opener = page.locator(opener).count() > 0 and page.locator(opener).is_visible()
    if back_has_opener:
        page.locator(opener).click()
        page.wait_for_timeout(300)
        if page.evaluate(MODAL_PROBE)['open']:
            page.locator("[data-wj-oc-action='confirm']").click(no_wait_after=True)
            page.wait_for_load_state('load')
            page.wait_for_timeout(1500)
    chk['4_no_duplicate'] = so_count(cr, fid) == n1
    chk['4_lands_on_same_order'] = (not back_has_opener) or (f'/{new_id}' in page.url)
    res['back'] = {'opener_visible': back_has_opener, 'url': urlparse(page.url).path}

    # 5 — F5 màn kết quả
    page.goto(result_url, wait_until='load')
    page.reload(wait_until='load')
    chk['5_refresh_no_new'] = so_count(cr, fid) == n1
    res['order_id'] = new_id
    res['ok'] = all(chk.values())
    ctx.close()
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--base', default='http://127.0.0.1:8055')
    ap.add_argument('--db', default='wujia_g5s')
    ap.add_argument('--login', default='dung.multi')
    ap.add_argument('--password', default='wujia@test123')
    ap.add_argument('--shots')
    args = ap.parse_args()
    if urlparse(args.base).hostname not in ('127.0.0.1', 'localhost'):
        sys.exit('Tạo đơn thật — chỉ chạy trên máy local / DB copy.')
    if args.shots:
        os.makedirs(args.shots, exist_ok=True)
    import psycopg2  # chỉ bộ tạo-đơn-thật cần; probe chỉ-đọc import file này không cần
    conn = psycopg2.connect(dbname=args.db, user='odoo19', password='1', host='127.0.0.1')
    conn.autocommit = True
    cr = conn.cursor()
    with sync_playwright() as p:
        br = p.chromium.launch()
        # cửa hàng đang chọn của user = cửa hàng giỏ; đọc từ session sau khi login
        ctx = br.new_context()
        pg = ctx.new_page()
        login(pg, args.base, args.login, args.password)
        pg.goto(args.base + '/portal/order/cart', wait_until='load')
        fid = int(pg.eval_on_selector('#wj-cart-sync', 'e => e.dataset.franchiseId'))
        ctx.close()
        allok = True
        for name, vp, path, opener in CASES:
            r = run_case(br, args, cr, fid, name, vp, path, opener, args.shots)
            allok &= r['ok']
            bad = [k for k, v in r['checks'].items() if not v]
            print(f"{'OK ' if r['ok'] else 'FAIL'} {name:11} SO#{r['order_id']} "
                  f"modal={r['modal'].get('lines')}mh/{r['modal'].get('qty')}sl/{r['modal'].get('total')} "
                  f"panel={r['modal'].get('panel')} back={r['back']} {'bad=' + ','.join(bad) if bad else ''}")
        br.close()
    print('== ALL OK' if allok else '== CÓ FAIL')


if __name__ == '__main__':
    main()
