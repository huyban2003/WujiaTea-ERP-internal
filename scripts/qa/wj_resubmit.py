"""WJ-ORD-027 (G5) — form lọc của mọi màn `wj_ajax_list` phải gửi được NHIỀU lần liên tiếp.

Gốc lỗi: khoá chống bấm lặp CMP-BTN-001 (`wujia_button_loading.js`) cắm cờ `data-wj-submitting`
lên form lúc submit và chỉ gỡ khi trang tải lại — form lọc AJAX không tải lại ⇒ lần 2 bị chặn im.

Mỗi màn × mỗi khổ: tìm form lọc GET đang hiện (action = đường dẫn danh sách), submit 3 lần với 3 giá
trị khác nhau, đếm request tới danh sách/fragment và đọc URL sau mỗi lần. Chỉ đọc (GET), chạy được
cả trên UAT.

  python scripts/qa/wj_resubmit.py --base http://127.0.0.1:8055 --login dung.multi [--out f.json]
"""
import argparse
import json
import sys
import os
from urllib.parse import quote_plus

sys.path.insert(0, os.path.dirname(__file__))
from wj_density import login  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402

PAGES = [
    ('/portal/order', '/portal/order/results'),
    ('/portal/purchase-history', None),
    ('/portal/delivery', None),
    ('/portal/return', None),
    ('/portal/support', None),
    ('/portal/knowledge', None),
    ('/portal/notification', None),
    ('/portal/exam', None),
    ('/portal/info-request', None),
    ('/portal/reports/orders', None),
    ('/portal/debt/payment-history', None),
]
VIEWPORTS = {'pc': (1440, 900), 'm': (390, 844)}

# Form lọc đang hiện + 1 control có thể đổi giá trị (ô chữ trước, rồi select, rồi date).
PICK = """(path) => {
  const vis = e => !!(e.offsetWidth || e.offsetHeight || e.getClientRects().length);
  const forms = [...document.querySelectorAll('form')].filter(f => {
    if ((f.getAttribute('method') || 'get').toLowerCase() !== 'get' || !vis(f)) return false;
    return new URL(f.getAttribute('action') || '', location.href).pathname === path;
  });
  for (const f of forms) {
    const ctl = [...f.querySelectorAll('input[type=text],input[type=search],input:not([type]),select,input[type=date]')]
      .find(vis);
    if (ctl) { f.setAttribute('data-probe', '1'); ctl.setAttribute('data-probe-ctl', '1');
               return {tag: ctl.tagName, type: ctl.type, name: ctl.name,
                       opts: ctl.tagName === 'SELECT' ? [...ctl.options].map(o => o.value) : null}; }
  }
  return null;
}"""


def values_for(info):
    if info['tag'] == 'SELECT':
        opts = [o for o in info['opts'] if o] or info['opts']
        seq = (opts + opts + opts)[:3]
        return seq if len(set(seq)) > 1 or len(opts) == 1 else seq
    if info['type'] == 'date':
        return ['2026-01-01', '2026-02-01', '2026-03-01']
    return ['zzprobe-a', 'zzprobe-b', 'zzprobe-c']


def run(base, user, password):
    out = []
    with sync_playwright() as p:
        br = p.chromium.launch()
        for vp_name, (w, h) in VIEWPORTS.items():
            ctx = br.new_context(viewport={'width': w, 'height': h})
            page = ctx.new_page()
            login(page, base, user, password)
            for path, frag in PAGES:
                hits = []
                page.on('request', lambda r, hits=hits, path=path, frag=frag: hits.append(r.url)
                        if r.resource_type in ('fetch', 'xhr', 'document') and
                        # Mọi request dưới đường dẫn danh sách: chính nó, hoặc fragment `<path>/results`.
                        (r.url.split('?')[0].split(base, 1)[-1] in (path, path + '/results') or
                         (frag and frag in r.url)) else None)
                page.goto(base + path, wait_until='load')
                hits.clear()
                info = page.evaluate(PICK, path)
                row = {'vp': vp_name, 'path': path, 'control': info, 'rounds': []}
                if info:
                    for v in values_for(info):
                        n0 = len(hits)
                        ctl = page.locator('[data-probe-ctl]')
                        if info['tag'] == 'SELECT':
                            ctl.evaluate('(e, v) => { e.value = v; }', v)
                        else:
                            ctl.fill(v)
                        page.locator('form[data-probe]').evaluate('f => f.requestSubmit()')
                        page.wait_for_timeout(1200)
                        if not page.locator('form[data-probe]').count():  # điều hướng thật: dò lại
                            page.evaluate(PICK, path)
                        row['rounds'].append({'value': v, 'requests': len(hits) - n0,
                                              'url': page.url.replace(base, '')})
                # Đạt = MỖI lượt có request đi VÀ URL mang đúng giá trị của chính lượt đó.
                row['ok'] = bool(info) and all(
                    r['requests'] > 0 and f"{info['name']}={quote_plus(r['value'])}" in r['url']
                    for r in row['rounds'])
                out.append(row)
                mark = 'OK ' if row['ok'] else ('-- ' if not info else 'FAIL')
                print(f"{mark} {vp_name:3} {path:30} {info and info['name']!s:14} "
                      + ' | '.join(f"{r['requests']}req {r['url'][:48]}" for r in row['rounds']))
            ctx.close()
        br.close()
    return out


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--base', default='http://127.0.0.1:8055')
    ap.add_argument('--login', default='dung.multi')
    ap.add_argument('--password', default='wujia@test123')
    ap.add_argument('--out')
    a = ap.parse_args()
    res = run(a.base, a.login, a.password)
    if a.out:
        json.dump(res, open(a.out, 'w'), ensure_ascii=False, indent=1)
    bad = [r for r in res if r['control'] and not r['ok']]
    print(f"== {len(res)} lượt, {len(bad)} FAIL, {sum(1 for r in res if not r['control'])} không có form lọc")
