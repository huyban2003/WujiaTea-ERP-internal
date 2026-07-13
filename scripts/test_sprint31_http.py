"""HTTP smoke Sprint 31 — Controller Lịch sử đơn hàng qua server local (routes + quyền + render).

Chạy khi server local đang bật (scripts/start.sh, port 8019) VÀ sau test_sprint31.py (tạo fixture):
    /home/huyban/miniconda3/envs/odoo/bin/python scripts/test_sprint31.py  (odoo shell — tạo fixture)
    /home/huyban/miniconda3/envs/odoo/bin/python scripts/test_sprint31_http.py

User demo: anh.owner (store HN-01), password wujia@test123.
"""
import json
import re

import requests

BASE = 'http://127.0.0.1:8019'
PASSWORD = 'wujia@test123'
FIXTURE = '/tmp/claude-1000/-home-huyban-odoo-dev/70cc0c63-b725-40bf-bb0e-6d6ce2f8a665/scratchpad/s31_fixture.json'

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


fx = json.load(open(FIXTURE))
print("=== SPRINT 31 HTTP SMOKE ===")
print(f"  fixture: {fx}")
owner = login('anh.owner')
LIST = f'{BASE}/portal/purchase-history'


def get(path):
    r = owner.get(path)
    return r.status_code, r.text


# ---------- 1. list route + ẩn cancel ----------
print("\n[1] list route + ẩn đơn huỷ")
sc, html = get(LIST)
check(sc == 200, 'GET /portal/purchase-history → 200')
check(fx['own_sale_name'] in html, f"list chứa đơn own sale ({fx['own_sale_name']})")
check(fx['own_backend_name'] in html, f"list chứa đơn own backend ({fx['own_backend_name']})")
check(fx['cancel_name'] not in html, f"list KHÔNG chứa đơn huỷ ({fx['cancel_name']})")
check(fx['foreign_name'] and fx['foreign_name'] not in html, "list KHÔNG chứa đơn cửa hàng khác")

# ---------- 2. detail route + giá đã thuế + requester ----------
print("\n[2] detail — giá đã thuế + người đặt")
sc, html = get(f"{LIST}/{fx['own_sale_id']}")
check(sc == 200, 'GET detail own sale → 200')
check(fx['own_sale_name'] in html, 'detail hiển thị mã đơn')
check('Đã xác nhận' in html, 'badge trạng thái "Đã xác nhận"')
check('21.600' in html, 'thành tiền/tổng đã gồm thuế (21.600)')
check('10.800' in html, 'đơn giá đã thuế = price_total/qty (10.800), KHÔNG phải 10.000 chưa thuế')

sc, html = get(f"{LIST}/{fx['own_backend_id']}")
check(sc == 200, 'GET detail own backend → 200')
check('Ngô Gia tạo đơn' in html, "đơn backend: người đặt = 'Ngô Gia tạo đơn' (không lộ user nội bộ)")

# ---------- 3. IDOR: đơn cửa hàng khác + đơn huỷ → cùng message, không lộ ----------
print("\n[3] chống IDOR + đơn huỷ")
if fx['foreign_id']:
    sc, html = get(f"{LIST}/{fx['foreign_id']}")
    check(sc == 200, 'GET detail đơn cửa hàng khác → 200 (render error, không 500)')
    check('không có quyền xem' in html, 'hiện message không-lộ-tồn-tại')
    check(fx['foreign_name'] not in html, 'KHÔNG lộ mã đơn cửa hàng khác')
sc, html = get(f"{LIST}/{fx['cancel_id']}")
check('không có quyền xem' in html, 'đơn huỷ mở detail → cùng message (ẩn khỏi lịch sử)')

# ---------- 4. filter state + search ----------
print("\n[4] filter state + search q")
sc, html = get(f"{LIST}?state=sale")
check(sc == 200 and fx['own_sale_name'] in html, 'filter state=sale trả đơn confirmed')
sc, html = get(f"{LIST}?state=cancel")
check(fx['cancel_name'] not in html, 'filter state=cancel bị bỏ qua → không lộ đơn huỷ')
sc, html = get(f"{LIST}?q={fx['own_sale_name']}")
check(sc == 200 and fx['own_sale_name'] in html, 'search q theo mã đơn trả đúng đơn')

print(f"\n=== RESULT: {PASS} PASS / {FAIL} FAIL ===")
