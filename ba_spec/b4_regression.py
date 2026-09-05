#!/usr/bin/env python3
"""B4 — regression: 17 route PAGE NAMING MATRIX (B3a/B3b) không vỡ + trang ngoài matrix
+ 6 chiều rộng BA yêu cầu ở cột REGRESSION của UI-BACKPAGEHEADER-001.

    python3 b4_regression.py [--base http://127.0.0.1:8055]
"""
import argparse
import sys

from playwright.sync_api import sync_playwright

USER, PWD = "anh.owner", "wujia@test123"

# (path, tên theo matrix, có Back không)
MATRIX = [
    ("/portal/order", "Đặt hàng", False),
    ("/portal/purchase-history", "Lịch sử đặt hàng", False),
    ("/portal/delivery", "Giao hàng", False),
    ("/portal/debt", "Công nợ", False),
    ("/portal/notification", "Thông báo", False),
    ("/portal/knowledge", "Kiến thức", False),
    ("/portal/support", "Hỗ trợ", False),
    ("/portal/exam", "Đăng ký thi", False),
    ("/portal/profile", "Tài khoản", False),
    ("/portal/return", "Bù hàng", False),
    ("/portal/purchase-history/28", "Chi tiết đơn hàng", True),
    ("/portal/delivery/3", "Chi tiết giao hàng", True),
    ("/portal/notification/41", "Chi tiết thông báo", True),
    ("/portal/support/40", "Chi tiết yêu cầu hỗ trợ", True),
    ("/portal/support/new", "Tạo yêu cầu hỗ trợ", True),
    ("/portal/return/12", "Chi tiết yêu cầu bù hàng", True),
    ("/portal/return/new", "Tạo yêu cầu bù hàng", True),
]

OUTSIDE = ["/portal", "/portal/order/cart", "/portal/info-request/new",
           "/portal/change-password", "/portal/exam/register"]

# Không còn miễn trừ nào: lỗi có sẵn ở /portal/info-request/new (inline script bị
# escape `&&` -> `&amp;&amp;`, portal_info_request_form.xml:122) đã được sửa hẳn
# trong cùng phiên ⇒ mọi trang phải 0 lỗi JS.
PREEXISTING_JS = {}

WIDTHS = [360, 391, 768, 1366, 1440, 1920]

PROBE = """
() => {
  const vis = el => {const s=getComputedStyle(el);
    return s.display!=='none' && s.visibility!=='hidden' && el.offsetParent!==null;};
  const hdrs = [...document.querySelectorAll('.wj-page-header')].filter(vis);
  const backs = [...document.querySelectorAll('.wj-page-header__back')].filter(vis);
  const h = hdrs[0];
  const t = h && h.querySelector('.wj-page-header__title');
  return {n_header: hdrs.length, n_back: backs.length,
          title: t ? t.textContent.trim() : null,
          header_h: h ? +h.getBoundingClientRect().height.toFixed(1) : null,
          back_w: backs[0] ? +backs[0].getBoundingClientRect().width.toFixed(1) : null,
          back_h: backs[0] ? +backs[0].getBoundingClientRect().height.toFixed(1) : null,
          overflow_x: document.documentElement.scrollWidth - document.documentElement.clientWidth};
}
"""

results = []


def check(name, ok, detail=""):
    results.append(ok)
    if not ok:
        print(f"[FAIL] {name} — {detail}")
    return ok


def login(page, base):
    page.goto(f"{base}/portal/login", wait_until="domcontentloaded")
    page.fill("#wj-auth-login", USER)
    page.fill("#wj-auth-password", PWD)
    page.press("#wj-auth-password", "Enter")
    page.wait_for_url(lambda u: "/portal/login" not in u, timeout=20000)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="http://127.0.0.1:8055")
    a = ap.parse_args()
    with sync_playwright() as pw:
        br = pw.chromium.launch()
        boot = br.new_context()
        login(boot.new_page(), a.base)
        state = boot.storage_state()

        print("=== 17 route matrix × 2 breakpoint (tên + cao 64/52 + 1 header) ===")
        for vname, w, h, exp_h in [("mobile", 391, 844, 52), ("pc", 1920, 1080, 64)]:
            ctx = br.new_context(viewport={"width": w, "height": h}, storage_state=state)
            ok_n = 0
            for path, name, has_back in MATRIX:
                p = ctx.new_page()
                errs = []
                p.on("pageerror", lambda e: errs.append(str(e)))
                r = p.goto(a.base + path, wait_until="load")
                m = p.evaluate(PROBE)
                ok = all([
                    check(f"{vname} {path} status", r.status == 200, str(r.status)),
                    check(f"{vname} {path} tên matrix", m["title"] == name, f"{m['title']!r} ≠ {name!r}"),
                    check(f"{vname} {path} đúng 1 header hiển thị", m["n_header"] == 1, str(m["n_header"])),
                    check(f"{vname} {path} cao {exp_h}", m["header_h"] and m["header_h"] >= exp_h - 0.6,
                          str(m["header_h"])),
                    check(f"{vname} {path} back {'có' if has_back else 'không'}",
                          m["n_back"] == (1 if has_back else 0), str(m["n_back"])),
                    check(f"{vname} {path} overflow 0", m["overflow_x"] <= 0, str(m["overflow_x"])),
                    check(f"{vname} {path} 0 JS error", not errs, str(errs[:1])),
                ])
                ok_n += ok
                p.close()
            print(f"  {vname}: {ok_n}/{len(MATRIX)} route sạch")
            ctx.close()

        print("=== 5 trang ngoài matrix × 2 breakpoint ===")
        for vname, w, h in [("mobile", 391, 844), ("pc", 1920, 1080)]:
            ctx = br.new_context(viewport={"width": w, "height": h}, storage_state=state)
            ok_n = 0
            for path in OUTSIDE:
                p = ctx.new_page()
                errs = []
                p.on("pageerror", lambda e: errs.append(str(e)))
                r = p.goto(a.base + path, wait_until="load")
                m = p.evaluate(PROBE)
                ok = all([
                    check(f"{vname} {path} status", r.status == 200, str(r.status)),
                    check(f"{vname} {path} overflow 0", m["overflow_x"] <= 0, str(m["overflow_x"])),
                    check(f"{vname} {path} 0 JS error",
                          not [e for e in errs if PREEXISTING_JS.get(path, "\0") not in e],
                          str(errs[:1])),
                ])
                ok_n += ok
                if errs:
                    print(f"  (miễn trừ có sẵn) {vname} {path}: {errs[:1]}")
                p.close()
            print(f"  {vname}: {ok_n}/{len(OUTSIDE)} trang sạch")
            ctx.close()

        print("=== 6 chiều rộng trên 1 route detail (BA REGRESSION) ===")
        for w in WIDTHS:
            ctx = br.new_context(viewport={"width": w, "height": 900}, storage_state=state)
            p = ctx.new_page()
            p.goto(a.base + "/portal/purchase-history/28", wait_until="load")
            m = p.evaluate(PROBE)
            exp = (122.0, 40.0) if w >= 992 else (42.0, 42.0)
            ok = all([
                check(f"{w}px đúng 1 Back hiển thị", m["n_back"] == 1, str(m["n_back"])),
                check(f"{w}px kích thước Back {exp}", (m["back_w"], m["back_h"]) == exp,
                      f"{m['back_w']}x{m['back_h']}"),
                check(f"{w}px overflow 0", m["overflow_x"] <= 0, str(m["overflow_x"])),
            ])
            print(f"  {w}px: back {m['back_w']}x{m['back_h']} header {m['header_h']} "
                  f"overflow {m['overflow_x']} → {'OK' if ok else 'FAIL'}")
            ctx.close()
        br.close()

    bad = results.count(False)
    print(f"\nTOTAL {len(results) - bad}/{len(results)} PASS")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
