#!/usr/bin/env python3
"""B4 — smoke UAT sau deploy (CHỈ ĐỌC: không tạo/sửa/xoá dữ liệu, không đổi cửa hàng).

Kiểm nút Quay lại CMP-BPH-001 + strip cửa hàng mobile là trigger + trang
info-request hết lỗi JS, trên chính UAT.

    python3 b4_uat_smoke.py [--base http://113.161.187.126:8019]
"""
import argparse
import re
import sys

from playwright.sync_api import sync_playwright

USER, PWD = "admin", "Wujia@2026"

# Route detail/form của CMP-BPH-001 — id lấy động, không hardcode
LIST_TO_DETAIL = [
    ("/portal/purchase-history", r"/portal/purchase-history/(\d+)"),
    ("/portal/delivery", r"/portal/delivery/(\d+)"),
    ("/portal/notification", r"/portal/notification/(\d+)"),
    ("/portal/support", r"/portal/support/(\d+)"),
    ("/portal/return", r"/portal/return/(\d+)"),
]
FORM_ROUTES = ["/portal/support/new", "/portal/return/new"]

MEASURE = """
() => {
  const vis = el => {const s=getComputedStyle(el);
    return s.display!=='none' && s.visibility!=='hidden' && el.offsetParent!==null;};
  const a = [...document.querySelectorAll('.wj-page-header__back')].filter(vis)[0];
  const out = {overflow_x: document.documentElement.scrollWidth
                           - document.documentElement.clientWidth,
               strip_a: !!document.querySelector(
                   'a.wujia-store-mobile-strip[data-action="open-store-picker"]'),
               strip_div: !!document.querySelector('div.wujia-store-mobile-strip')};
  if (!a) return out;
  const r = a.getBoundingClientRect(), s = getComputedStyle(a);
  const i = a.querySelector('i');
  const hdr = a.closest('.wj-page-header');
  Object.assign(out, {
    w: +r.width.toFixed(1), h: +r.height.toFixed(1), radius: s.borderRadius,
    bg: s.backgroundColor, border: s.borderColor,
    icon: getComputedStyle(i, '::before').content,
    icon_color: getComputedStyle(i).color,
    hit: getComputedStyle(a, '::after').width + 'x' + getComputedStyle(a, '::after').height,
    href: a.getAttribute('href'),
    header_h: +hdr.getBoundingClientRect().height.toFixed(1),
  });
  return out;
}
"""

res = []


def check(name, ok, detail=""):
    res.append(ok)
    print(("[PASS] " if ok else "[FAIL] ") + name + ("" if ok else f" — {detail}"))


def login(ctx, base):
    p = ctx.new_page()
    p.goto(f"{base}/web/login", wait_until="domcontentloaded")
    p.fill("input[name=login]", USER)
    p.fill("input[name=password]", PWD)
    p.press("input[name=password]", "Enter")
    p.wait_for_load_state("load")
    p.close()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="http://113.161.187.126:8019")
    a = ap.parse_args()

    with sync_playwright() as pw:
        br = pw.chromium.launch()
        boot = br.new_context()
        login(boot, a.base)
        state = boot.storage_state()

        # gom id thật từ trang list (chỉ đọc)
        probe = br.new_context(storage_state=state,
                               viewport={"width": 1920, "height": 1080})
        pp = probe.new_page()
        routes = []
        for lst, pat in LIST_TO_DETAIL:
            pp.goto(a.base + lst, wait_until="load")
            hrefs = pp.eval_on_selector_all("a[href]", "els => els.map(e => e.getAttribute('href'))")
            hit = next((h for h in hrefs if h and re.fullmatch(pat, h.split("?")[0])), None)
            if hit:
                routes.append((hit.split("?")[0], lst))
            else:
                print(f"  (bỏ qua {lst}: UAT chưa có bản ghi nào để mở chi tiết)")
        for f in FORM_ROUTES:
            routes.append((f, f.rsplit("/", 1)[0]))
        probe.close()
        print(f"Route đo được trên UAT: {[r for r, _ in routes]}\n")

        for vname, w, h in [("mobile", 391, 844), ("pc", 1920, 1080)]:
            ctx = br.new_context(viewport={"width": w, "height": h}, storage_state=state)
            for path, parent in routes:
                p = ctx.new_page()
                errs = []
                p.on("pageerror", lambda e: errs.append(str(e)))
                r = p.goto(a.base + path, wait_until="load")
                m = p.evaluate(MEASURE)
                check(f"{vname} {path} 200", r.status == 200, str(r.status))
                check(f"{vname} {path} 0 lỗi JS", not errs, str(errs[:1]))
                check(f"{vname} {path} overflow 0", m["overflow_x"] <= 0, str(m["overflow_x"]))
                if "w" not in m:
                    check(f"{vname} {path} có nút Quay lại", False, "không thấy")
                    p.close()
                    continue
                if vname == "pc":
                    check(f"pc {path} 122×40 radius 12",
                          (m["w"], m["h"]) == (122.0, 40.0) and m["radius"] == "12px",
                          f"{m['w']}x{m['h']} {m['radius']}")
                    check(f"pc {path} icon arrow-left (U+E828)",
                          "" in m["icon"], m["icon"])
                else:
                    check(f"mobile {path} tròn 42×42",
                          (m["w"], m["h"]) == (42.0, 42.0) and m["radius"] == "999px",
                          f"{m['w']}x{m['h']} {m['radius']}")
                    check(f"mobile {path} vùng chạm 44×44", m["hit"] == "44pxx44px", m["hit"])
                    check(f"mobile {path} hàng header 52", abs(m["header_h"] - 52) < 0.6,
                          str(m["header_h"]))
                check(f"{vname} {path} href về list cha", m["href"] == parent,
                      f"{m['href']} ≠ {parent}")
                check(f"{vname} {path} nền trắng + viền #E5E7EB",
                      m["bg"] == "rgb(255, 255, 255)" and m["border"] == "rgb(229, 231, 235)",
                      f"{m['bg']} / {m['border']}")
                check(f"{vname} {path} icon #28A9DF", m["icon_color"] == "rgb(40, 169, 223)",
                      m["icon_color"])
                p.close()
            ctx.close()

        # strip cửa hàng mobile + info-request (chỉ mở popup rồi ĐÓNG, không đổi cửa hàng)
        ctx = br.new_context(viewport={"width": 391, "height": 844}, storage_state=state)
        p = ctx.new_page()
        errs = []
        p.on("pageerror", lambda e: errs.append(str(e)))
        p.goto(a.base + "/portal", wait_until="load")
        m = p.evaluate(MEASURE)
        if m["strip_a"]:
            check("mobile strip là <a> mở popup", True)
            p.click("a.wujia-store-mobile-strip")
            p.wait_for_timeout(700)
            shown = p.evaluate(
                "() => {const o=document.getElementById('wujiaStoreOverlay');"
                "return o ? getComputedStyle(o).display !== 'none' : false;}")
            check("mobile bấm strip → popup hiện", shown, "không hiện")
            p.keyboard.press("Escape")
            p.wait_for_timeout(400)
            after = p.evaluate(
                "() => {const o=document.getElementById('wujiaStoreOverlay');"
                "return o ? getComputedStyle(o).display !== 'none' : false;}")
            check("đóng popup không đổi gì (chỉ đọc)", not after, "vẫn mở")
        elif m["strip_div"]:
            print("  (tài khoản UAT chỉ có ≤1 cửa hàng ⇒ strip cố ý vẫn là <div> trơ)")
            check("mobile strip trơ đúng thiết kế 1 cửa hàng", True)
        else:
            print("  (tài khoản UAT không có cửa hàng đang thao tác ⇒ không render strip)")

        r = p.goto(a.base + "/portal/info-request/new", wait_until="load")
        p.wait_for_timeout(600)
        check("info-request/new 200", r.status == 200, str(r.status))
        check("info-request/new 0 lỗi JS (lỗi &amp;&amp; đã hết)", not errs, str(errs[:1]))
        check("info-request/new không còn thực thể trong <script>",
              "&amp;&amp;" not in p.content(), "vẫn còn")
        ctx.close()
        br.close()

    bad = res.count(False)
    print(f"\nTOTAL {len(res) - bad}/{len(res)} PASS")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
