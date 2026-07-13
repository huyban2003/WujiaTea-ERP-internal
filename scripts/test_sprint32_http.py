"""HTTP smoke Sprint 32 — Controller Thông báo qua server local (routes + quyền + render).

Chạy khi server local đang bật (scripts/start.sh, port 8019) VÀ sau test_sprint32.py:
    /home/huyban/miniconda3/envs/odoo/bin/python odoo-bin shell ... < scripts/test_sprint32.py
    /home/huyban/miniconda3/envs/odoo/bin/python scripts/test_sprint32_http.py

User demo: anh.owner, password wujia@test123.
"""
import json
import re

import requests

BASE = 'http://127.0.0.1:8019'
PASSWORD = 'wujia@test123'
FIXTURE = ('/tmp/claude-1000/-home-huyban-odoo-dev/'
           '8e2a3da0-d53a-494c-8971-b50bb299556b/scratchpad/s32_fixture.json')

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
print("=== SPRINT 32 HTTP SMOKE ===")
print(f"  fixture: {fx}")
s = login('anh.owner')
NB = f'{BASE}/portal/notification'


def get(path):
    r = s.get(path)
    return r.status_code, r.text


def rpc(path, params=None):
    r = s.post(f'{BASE}{path}', json={'jsonrpc': '2.0', 'method': 'call',
                                      'params': params or {}})
    return r.json().get('result')


# ---------- 1. list route + lịch sử gồm hết hạn + badge ----------
print("\n[1] list route + badge hết hiệu lực")
sc, html = get(NB)
check(sc == 200, 'GET /portal/notification → 200')
check(fx['eff_name'] in html, 'list chứa thông báo còn hiệu lực')
check(fx['exp_name'] in html, 'list (lịch sử) chứa cả thông báo hết hạn')
check('Đã hết hiệu lực' in html, 'badge "Đã hết hiệu lực" render cho noti hết hạn')

# ---------- 2. filter read_status + priority + date range ----------
print("\n[2] filters")
sc, html = get(f'{NB}?priority=urgent')
check(sc == 200 and fx['eff_name'] in html, 'filter priority=urgent trả noti urgent')
sc, html = get(f'{NB}?read_status=unread')
check(sc == 200 and fx['eff_name'] in html, 'filter read_status=unread chứa noti chưa đọc')
sc, html = get(f'{NB}?date_from=2030-01-01&date_to=2020-01-01')
check(sc == 200, 'date_from > date_to → 200 (INVALID_DATE_RANGE xử lý, không 500)')

# ---------- 3. popup recent (JSON) loại hết hạn ----------
print("\n[3] popup recent")
res = rpc('/portal/notification/recent')
ids = [n['id'] for n in (res or {}).get('notifications', [])]
check(res is not None and 'total_unread' in res, 'recent trả total_unread')
check(fx['exp_id'] not in ids, 'popup KHÔNG chứa thông báo hết hạn')

# ---------- 4. detail mark-read theo store → unread giảm ----------
print("\n[4] detail mark-read (store-scoped)")
u0 = (rpc('/portal/notification/unread-count') or {}).get('count', 0)
sc, html = get(f"{NB}/{fx['eff_id']}")
check(sc == 200 and fx['eff_name'] in html, 'GET detail eff → 200')
u1 = (rpc('/portal/notification/unread-count') or {}).get('count', 0)
check(u1 == max(0, u0 - 1), f'unread giảm 1 sau khi đọc detail ({u0} → {u1})')

# ---------- 5. attachment guarded (đóng IDOR) ----------
print("\n[5] attachment download có kiểm quyền")
r_ok = s.get(f"{NB}/{fx['att_noti_id']}/attachment/{fx['attA_id']}")
check(r_ok.status_code == 200, 'attachment đúng thông báo → 200')
r_idor = s.get(f"{NB}/{fx['att_noti_id']}/attachment/{fx['attB_id']}")
check(r_idor.status_code in (403, 404),
      f'attachment của thông báo KHÁC → {r_idor.status_code} (IDOR đóng)')

# ---------- 6. mark-all-read → unread về 0 ----------
print("\n[6] mark-all-read")
res = rpc('/portal/notification/mark-all-read')
check(res is not None and res.get('success') and res.get('unread_count') == 0,
      f"mark-all-read success, unread_count=0 (updated {res and res.get('updated_count')})")
u2 = (rpc('/portal/notification/unread-count') or {}).get('count', 0)
check(u2 == 0, f'unread-count = 0 sau mark-all ({u2})')

print(f"\n=== RESULT: {PASS} PASS / {FAIL} FAIL ===")
