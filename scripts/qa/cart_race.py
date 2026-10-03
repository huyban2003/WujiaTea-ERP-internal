"""Đua 2 request cùng lúc trên giỏ chung của một cửa hàng (WJ-ORD-002 · submit NOWAIT).

Cần server chạy trên DB có seed: cửa hàng mã F6RACE, 2 user portal owner
f6race_a / f6race_b (mật khẩu = login), sản phẩm F6RACE1 (min 1). Chỉ chạy trên DB copy.

  python scripts/qa/cart_race.py --url http://127.0.0.1:8096 --db wujia_f6 [--rounds 5]

(a) từ qty 4, hai user cùng bấm giảm  → cuối phải còn 2.
(b) hai user cùng Gửi đơn             → đúng 1 đơn mới, người kia CART_IS_PROCESSING/CART_EMPTY, giỏ trống;
    ít nhất 1 vòng phải ra CART_IS_PROCESSING (khoá NOWAIT thật sự bị chạm).
"""
import argparse
import json
import re
import threading

import psycopg2
import requests

CSRF = re.compile(r'name="csrf_token"\s+value="([^"]+)"')


def login(url, db, user):
    s = requests.Session()
    r = s.post(f'{url}/web/session/authenticate', json={
        'jsonrpc': '2.0', 'params': {'db': db, 'login': user, 'password': user}}, timeout=30)
    r.raise_for_status()
    assert r.json().get('result', {}).get('uid'), f'login {user} thất bại'
    return s


def rpc(s, url, route, **params):
    r = s.post(f'{url}{route}', json={'jsonrpc': '2.0', 'params': params}, timeout=60)
    r.raise_for_status()
    return r.json()['result']


def together(fns):
    barrier = threading.Barrier(len(fns))
    out = [None] * len(fns)

    def run(i, fn):
        barrier.wait()
        out[i] = fn()

    ts = [threading.Thread(target=run, args=(i, fn)) for i, fn in enumerate(fns)]
    for t in ts:
        t.start()
    for t in ts:
        t.join()
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--url', default='http://127.0.0.1:8096')
    ap.add_argument('--db', required=True)
    ap.add_argument('--rounds', type=int, default=5)
    a = ap.parse_args()

    pg = psycopg2.connect(dbname=a.db, host='127.0.0.1', user='odoo19')
    pg.autocommit = True
    cur = pg.cursor()
    cur.execute("SELECT id FROM wujia_franchise_management WHERE code = 'F6RACE'")
    fid = cur.fetchone()[0]
    cur.execute("SELECT id FROM product_product WHERE default_code = 'F6RACE1'")
    pid = cur.fetchone()[0]

    def so_ids():
        cur.execute("SELECT id FROM sale_order WHERE franchise_id = %s AND state != 'cancel'", (fid,))
        return {r[0] for r in cur.fetchall()}

    sa, sb = login(a.url, a.db, 'f6race_a'), login(a.url, a.db, 'f6race_b')
    result = {'step': [], 'submit': []}

    for _ in range(a.rounds):
        st = rpc(sa, a.url, '/portal/order/cart/add', product_id=pid)
        line_id = st['line_id']
        rpc(sa, a.url, '/portal/order/cart/update', line_id=line_id, qty=4)
        together([lambda s=s: rpc(s, a.url, '/portal/order/cart/step', line_id=line_id, direction='dec')
                  for s in (sa, sb)])
        cur.execute('SELECT qty FROM wujia_portal_cart_line WHERE id = %s', (line_id,))
        result['step'].append(cur.fetchone()[0])

    for _ in range(a.rounds):
        st = rpc(sa, a.url, '/portal/order/cart/add', product_id=pid)
        tokens = [CSRF.search(s.get(f'{a.url}/portal/order/cart', timeout=60).text).group(1) for s in (sa, sb)]
        before = so_ids()
        locs = together([lambda s=s, t=t: s.post(f'{a.url}/portal/order/submit', data={'csrf_token': t},
                                                 allow_redirects=False, timeout=60).headers.get('Location', '')
                         for s, t in zip((sa, sb), tokens)])
        cur.execute('SELECT count(*) FROM wujia_portal_cart_line l JOIN wujia_portal_cart c ON c.id = l.cart_id '
                    'WHERE c.franchise_id = %s', (fid,))
        left = cur.fetchone()[0]
        outcome = sorted('ok' if '/portal/purchase-history/' in loc
                         else loc.split('?')[-1] if 'error=' in loc else f'?{loc}'
                         for loc in locs)
        result['submit'].append({'new_orders': len(so_ids() - before), 'outcome': outcome, 'cart_lines_left': left})

    ok_step = all(q == 2 for q in result['step'])
    ok_submit = all(r['new_orders'] == 1 and r['cart_lines_left'] == 0 and r['outcome'].count('ok') == 1
                    for r in result['submit'])
    # Ít nhất 1 vòng người thua phải gặp khoá NOWAIT — không thì phép đo chưa chạm tới khoá.
    result['nowait_hits'] = sum('error=CART_IS_PROCESSING' in r['outcome'] for r in result['submit'])
    result['verdict'] = 'PASS' if ok_step and ok_submit and result['nowait_hits'] else 'FAIL'
    print(json.dumps(result, ensure_ascii=False, indent=1))


if __name__ == '__main__':
    main()
