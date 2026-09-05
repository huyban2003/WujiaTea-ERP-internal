#!/usr/bin/env python3
"""qa_visual_check — TỰ verify Issue List bằng headless Chromium (đo computed-style
/ bounding-box y như BA), thay vì đoán. Dev-only, gitignored.

TẠI SAO: nhiều issue UI/responsive BA đo bằng DevTools (getComputedStyle,
getBoundingClientRect). Trước đây agent không có browser nên phải ghi LIMIT "không
verify headless được". Env `odoo` ĐÃ có `playwright` + chromium → chạy được thật.

DÙNG:
    # đo nhanh 1 URL 1 viewport, in computed-style vài selector
    python3 qa_visual_check.py --url /portal/order --w 1920 --h 1080 \
        --measure ".header-navbar:box" ".wj-page-header__title:fontFamily,fontWeight"

    # inject 1 rule để THỬ fix trước khi sửa code (xem cascade có thắng không)
    python3 qa_visual_check.py --url /portal/order --w 1920 --h 1080 \
        --measure ".main-menu:width" --inject ".main-menu{width:300px!important}"

MẸO / GOTCHA:
- Portal có long-poll (bus.bus) -> KHÔNG dùng wait_until="networkidle" (treo);
  dùng "load" + wait_for_timeout.
- Login admin/Wujia@2026 trên UAT; submit bằng Enter (nút login trùng nút Search).
- CSS đổi mà computed không đổi kể cả inject !important ultra-spec -> element bị
  JS/plugin (Vuexy Waves, PerfectScrollbar) hoặc structural điều khiển, KHÔNG fix
  được bằng CSS (vd sidebar .main-menu width, nút .btn-primary.waves-effect). Defer.
- `:box` = getBoundingClientRect (x/y/width/height); còn lại = getComputedStyle[prop].
"""
import argparse
import json

from playwright.sync_api import sync_playwright

DEFAULT_BASE = "http://113.161.187.126:8019"   # UAT; đổi --base http://127.0.0.1:8019 cho local
USER, PWD = "admin", "Wujia@2026"


def login(ctx, base):
    p = ctx.new_page()
    p.goto(f"{base}/web/login", wait_until="domcontentloaded")
    p.fill("input[name=login]", USER)
    p.fill("input[name=password]", PWD)
    p.press("input[name=password]", "Enter")     # nút submit trùng nút Search -> Enter chắc ăn
    try:
        p.wait_for_url(lambda u: "/web/login" not in u, timeout=20000)
    except Exception:
        pass
    p.wait_for_timeout(1200)
    p.close()


def measure(page, spec):
    """spec = 'selector:prop1,prop2' hoặc 'selector:box'. Trả dict."""
    sel, _, props = spec.partition(":")
    el = page.query_selector(sel)
    if not el:
        return {"_": "NOT FOUND"}
    if props == "box":
        b = el.bounding_box() or {}
        return {k: round(v, 1) for k, v in b.items()}
    plist = [p.strip() for p in props.split(",") if p.strip()]
    return page.evaluate(
        "([el,ps])=>Object.fromEntries(ps.map(p=>[p,getComputedStyle(el)[p]]))",
        [el, plist])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default=DEFAULT_BASE)
    ap.add_argument("--url", default="/portal/order")
    ap.add_argument("--w", type=int, default=1920)
    ap.add_argument("--h", type=int, default=1080)
    ap.add_argument("--measure", nargs="+", required=True,
                    help="mỗi arg = 'selector:prop1,prop2' hoặc 'selector:box'")
    ap.add_argument("--inject", help="CSS rule tiêm thử trước khi đo (test cascade)")
    a = ap.parse_args()

    out = {}
    with sync_playwright() as pw:
        br = pw.chromium.launch(headless=True)
        ctx = br.new_context(viewport={"width": a.w, "height": a.h})
        login(ctx, a.base)
        pg = ctx.new_page()
        pg.set_viewport_size({"width": a.w, "height": a.h})
        pg.goto(f"{a.base}{a.url}", wait_until="load")
        pg.wait_for_timeout(1200)
        if a.inject:
            pg.add_style_tag(content=a.inject)
            pg.wait_for_timeout(200)
        for spec in a.measure:
            out[spec] = measure(pg, spec)
        br.close()
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
