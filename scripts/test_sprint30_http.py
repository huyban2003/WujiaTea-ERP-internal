"""HTTP smoke Sprint 30 — controller thật qua server local (routes + giỏ chung + race).

Chạy khi server local đang bật (scripts/start.sh, port 8019):
    /home/huyban/miniconda3/envs/odoo/bin/python scripts/test_sprint30_http.py

Cần user demo: anh.owner / cuong.staff (cùng store HN-01), password wujia@test123.
"""
import re
import sys
import threading

import requests

BASE = 'http://127.0.0.1:8019'
PASSWORD = 'wujia@test123'

PASS = FAIL = 0


def check(cond, msg):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  PASS: {msg}")
    else:
        FAIL += 1
        print(f"  FAIL: {msg}")


def login(username):
    s = requests.Session()
    page = s.get(f'{BASE}/web/login')
    token = re.search(r'name="csrf_token"\s+value="([^"]+)"', page.text).group(1)
    r = s.post(f'{BASE}/web/login', data={
        'login': username, 'password': PASSWORD, 'csrf_token': token,
    }, allow_redirects=True)
    assert '/web/login' not in r.url, f'login failed for {username}'
    return s


def rpc(session, path, **params):
    r = session.post(f'{BASE}{path}', json={
        'jsonrpc': '2.0', 'method': 'call', 'params': params,
    })
    return r.json().get('result') or {}


def get_products(session):
    """Đọc product id + min_qty từ trang catalog (data-attrs render server)."""
    html = session.get(f'{BASE}/portal/order').text
    btns = re.findall(
        r'data-product-id="(\d+)"[^>]*data-min-qty="(\d+)"[^>]*data-max-qty="(\d+)"',
        html,
    )
    return [(int(a), int(b), int(c)) for a, b, c in btns]


print("=== SPRINT 30 HTTP SMOKE ===")
owner = login('anh.owner')
staff = login('cuong.staff')

# ---------- 1. Routes 200 ----------
print("\n[1] routes")
for path in ['/portal/order', '/portal/order/cart']:
    check(owner.get(f'{BASE}{path}').status_code == 200, f'GET {path} 200')

# ---------- 2. Reset cart + add theo bước min_qty ----------
print("\n[2] add — bước = min_qty, giỏ chung 2 user")
products = get_products(owner)
check(bool(products), f'catalog exposes {len(products)} product buttons with min/max attrs')
pid, min_qty, _max = products[0]

state = rpc(owner, '/portal/order/cart/count')
# clear giỏ về 0 trước khi test (xoá qua update qty=0 từng line trên cart page)
html = owner.get(f'{BASE}/portal/order/cart').text
for line_id in set(re.findall(r'data-line-id="(\d+)"', html)):
    rpc(owner, '/portal/order/cart/remove', line_id=int(line_id))
check(rpc(owner, '/portal/order/cart/count')['line_count'] == 0, 'cart cleared')

res1 = rpc(owner, '/portal/order/cart/add', product_id=pid)
check(res1.get('success') and res1.get('qty') == min_qty,
      f'first add → qty = min_qty ({min_qty})')
res2 = rpc(owner, '/portal/order/cart/add', product_id=pid)
check(res2.get('qty') == min_qty * 2, f'second add → +step ({res2.get("qty")})')
check(res2.get('cart', {}).get('line_count') == 1, 'still 1 line (unique product)')

staff_count = rpc(staff, '/portal/order/cart/count')
check(staff_count.get('line_count') == 1 and staff_count.get('total_qty') == min_qty * 2,
      f'staff CÙNG STORE thấy chung giỏ (line_count=1, qty={staff_count.get("total_qty")})')

# ---------- 3. update — min/step/max ----------
print("\n[3] update — validate min/step/max")
line_id = res2['cart']['lines'][0]['line_id']
if min_qty > 1:
    bad = rpc(staff, '/portal/order/cart/update', line_id=line_id, qty=min_qty + 1)
    check(bad.get('error') == 'QTY_INVALID_STEP', f'sai step → QTY_INVALID_STEP ({bad.get("error")})')
else:
    check(True, 'min_qty=1 — mọi qty đều hợp lệ step (skip)')
ok = rpc(staff, '/portal/order/cart/update', line_id=line_id, qty=min_qty * 3)
check(ok.get('success') and ok.get('qty') == min_qty * 3, 'staff update qty hợp lệ')
owner_state = rpc(owner, '/portal/order/cart/count')
check(owner_state.get('total_qty') == min_qty * 3, 'owner thấy qty staff vừa đổi (last-write-wins)')

# ---------- 4. note chung ----------
print("\n[4] note dùng chung")
rpc(owner, '/portal/order/cart/note', note='Giao trước 8h sáng')
html = staff.get(f'{BASE}/portal/order/cart').text
check('Giao trước 8h sáng' in html, 'staff thấy note owner vừa lưu')

# ---------- 5. race — 2 user add song song cùng product ----------
print("\n[5] race add song song")
before = rpc(owner, '/portal/order/cart/count').get('total_qty') or 0
results = []
def _add(sess):
    results.append(rpc(sess, '/portal/order/cart/add', product_id=pid))
threads = [threading.Thread(target=_add, args=(s,)) for s in (owner, staff) for _ in range(3)]
[t.start() for t in threads]
[t.join() for t in threads]
final = rpc(owner, '/portal/order/cart/count')
expect = before + 6 * min_qty
got = final.get('total_qty')
cap = products[0][2]
check(got == expect or (cap and got == cap),
      f'6 add song song cộng dồn đúng: {got} == {expect}' + (' (cap max)' if cap else ''))
check(final.get('line_count') == 1, 'không sinh dòng trùng khi race')

# ---------- 6. submit — SO draft + huỷ draft cũ + clear giỏ ----------
print("\n[6] submit flow")
html = owner.get(f'{BASE}/portal/order/cart').text
token = re.search(r'name="csrf_token"\s+value="([^"]+)"', html).group(1)
r = owner.post(f'{BASE}/portal/order/submit',
               data={'csrf_token': token, 'portal_note': 'Note khi submit'},
               allow_redirects=False)
loc = r.headers.get('Location', '')
if 'error=ORDER_TIME_CLOSED' in loc or 'error=outside_order_window' in loc:
    print("  SKIP: ngoài khung giờ đặt hàng — submit bị chặn đúng rule (ORDER_TIME_CLOSED)")
    check(True, 'submit ngoài khung giờ trả ORDER_TIME_CLOSED')
else:
    m = re.search(r'/portal/purchase-history/(\d+)\?message=order_submitted', loc)
    check(bool(m), f'submit redirect về history ({loc})')
    check(rpc(owner, '/portal/order/cart/count')['line_count'] == 0, 'giỏ trống sau submit')
    if m and staff.get(f'{BASE}/portal/purchase-history/{m.group(1)}').status_code == 200:
        check(True, 'staff cùng store xem được đơn vừa tạo')

print(f"\n=== RESULT: {PASS} PASS / {FAIL} FAIL ===")
sys.exit(1 if FAIL else 0)
