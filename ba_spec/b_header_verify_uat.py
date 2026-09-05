#!/usr/bin/env python3
"""Cụm B — verify: toạ độ 4 phần tử × 5 route PC, 2 dropdown, badge, regression mobile."""
import sys
from playwright.sync_api import sync_playwright

BASE = "http://113.161.187.126:8019"
USER, PWD = "admin", "Wujia@2026"
PC, MOB, TABLET = (1920, 1080), (391, 844), (1100, 800)
ROUTES = ["/portal", "/portal/order", "/portal/purchase-history",
          "/portal/notification", "/portal/knowledge"]
FAIL = []

# source v1.5: (selector, x, y, w, h)
EXPECT = [
    ("language pill", "li.dropdown-language > a.nav-link", 1450, 16, 118, 40),
    ("cart circle", "li.wujia-header-icon-item a[href='/portal/order']", 1590, 16, 40, 40),
    ("bell circle", "li.wujia-header-icon-item a[href='/portal/notification']", 1642, 16, 40, 40),
    ("account pill", "li.dropdown-user > a.dropdown-user-link", 1696, 10, 204, 52),
]
TOL = 1.0

BOX_JS = """(sel) => {
  const el = document.querySelector(sel);
  if (!el) return null;
  const r = el.getBoundingClientRect(); const cs = getComputedStyle(el);
  return {x:+r.x.toFixed(1), y:+r.y.toFixed(1), w:+r.width.toFixed(1), h:+r.height.toFixed(1),
          radius: cs.borderRadius, bg: cs.backgroundColor};
}"""


def ok(cond, label, detail=""):
    print(("  OK   " if cond else "  FAIL ") + label + ("  " + detail if detail else ""))
    if not cond:
        FAIL.append(f"{label} {detail}")


def login(ctx):
    p = ctx.new_page()
    p.goto(f"{BASE}/web/login", wait_until="domcontentloaded")
    p.fill("input[name=login]", USER)
    p.fill("input[name=password]", PWD)
    p.press("input[name=password]", "Enter")
    p.wait_for_timeout(2500)
    if "/web/login" in p.url:
        sys.exit("LOGIN FAILED")
    p.close()


def open_page(ctx, url, size):
    p = ctx.new_page()
    p.set_viewport_size({"width": size[0], "height": size[1]})
    errs = []
    p.on("pageerror", lambda e: errs.append(str(e)))
    r = p.goto(BASE + url, wait_until="load")
    p.wait_for_timeout(1800)
    # UAT: admin thuộc nhiều cửa hàng → overlay #wujiaStoreOverlay che trang, mọi
    # assert nội dung sẽ pass rỗng nếu bỏ qua (bẫy L8).
    if p.locator("#wujiaStoreOverlay").count() and p.evaluate(
            "() => getComputedStyle(document.querySelector('#wujiaStoreOverlay')).display !== 'none'"):
        p.locator("input.wujia-store-radio").first.check()
        p.evaluate("() => document.querySelector('form.wujia-store-form').submit()")
        p.wait_for_timeout(2500)
    return p, r, errs


def main():
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        ctx = b.new_context(viewport={"width": PC[0], "height": PC[1]})
        login(ctx)

        # ---------------------------------------------- 1. toạ độ 5 route PC ---
        print("\n=== 1. Toạ độ cụm action, PC 1920×1080, 5 route ===")
        for route in ROUTES:
            p, resp, errs = open_page(ctx, route, PC)
            print(f"-- {route}  HTTP {resp.status}")
            ok(resp.status == 200, f"{route} status", str(resp.status))
            for label, sel, ex, ey, ew, eh in EXPECT:
                box = p.evaluate(BOX_JS, sel)
                if not box:
                    ok(False, f"{route} {label}", "MISSING")
                    continue
                good = (abs(box["x"] - ex) <= TOL and abs(box["y"] - ey) <= TOL
                        and abs(box["w"] - ew) <= TOL and abs(box["h"] - eh) <= TOL)
                ok(good, f"{route} {label}",
                   f"{box['x']},{box['y']} {box['w']}×{box['h']} (exp {ex},{ey} {ew}×{eh})")
            # glass + radius chỉ cần kiểm 1 lần, ở route đầu
            if route == ROUTES[0]:
                for label, sel, *_ in EXPECT[1:]:
                    box = p.evaluate(BOX_JS, sel)
                    ok("255, 255, 255, 0.18" in box["bg"], f"{label} glass", box["bg"])
                av = p.evaluate(BOX_JS, "li.dropdown-user > a.dropdown-user-link img.round")
                cx, cy = av["x"] + av["w"] / 2, av["y"] + av["h"] / 2
                ok(abs(cx - 1724) <= TOL and abs(cy - 36) <= TOL,
                   "avatar tâm (1724,36)", f"({cx},{cy}) {av['w']}×{av['h']}")
                ok(abs(av["w"] - 36) <= TOL, "avatar 36px", str(av["w"]))
                order = p.evaluate("""() => [...document.querySelector(
                    'li.dropdown-user > a.dropdown-user-link').children].map(c=>c.tagName)""")
                ok(order[0] == "SPAN", "avatar đứng trước tên", str(order))
                edge = p.evaluate("""() => {
                    const a=document.querySelector("li.dropdown-user > a.dropdown-user-link");
                    const r=a.getBoundingClientRect(); return +(r.x+r.width).toFixed(1);}""")
                ok(abs(edge - 1900) <= TOL, "mép phải cụm = 1900", str(edge))
            ovf = p.evaluate("() => document.documentElement.scrollWidth - "
                             "document.documentElement.clientWidth")
            ok(ovf <= 0, f"{route} overflow ngang", str(ovf))
            ok(not errs, f"{route} JS error", str(errs[:1]))
            p.close()

        # ------------------------------------------------------ 2. dropdown ---
        print("\n=== 2. Dropdown ngôn ngữ + tài khoản còn mở được ===")
        p, _, _ = open_page(ctx, "/portal", PC)
        p.click("li.dropdown-language > a.nav-link")
        p.wait_for_timeout(500)
        vis = p.evaluate("""() => {
            const m=document.querySelector('li.dropdown-language .dropdown-menu');
            return m && getComputedStyle(m).display !== 'none';}""")
        ok(vis, "dropdown ngôn ngữ mở")
        items = p.locator("li.dropdown-language .dropdown-menu a.dropdown-item")
        ok(items.count() == 2, "2 mục ngôn ngữ", str(items.count()))
        p.keyboard.press("Escape")
        p.wait_for_timeout(300)
        p.click("li.dropdown-user > a.dropdown-user-link")
        p.wait_for_timeout(500)
        vis2 = p.evaluate("""() => {
            const m=document.querySelector('li.dropdown-user .wj-pc-acct-menu');
            return m && getComputedStyle(m).display !== 'none';}""")
        ok(vis2, "dropdown tài khoản mở")
        links = p.evaluate("""() => [...document.querySelectorAll(
            'li.dropdown-user .wj-pc-acct-menu a.dropdown-item')].map(a=>a.getAttribute('href'))""")
        ok("/portal/profile" in links and "/portal/logout" in links,
           "menu tài khoản đủ mục", str(links))
        p.close()

        # --------------------------------------------------------- 3. badge ---
        print("\n=== 3. Badge cart/bell ===")
        p, _, _ = open_page(ctx, "/portal", PC)
        badges = p.evaluate("""() => [...document.querySelectorAll(
            '.wujia-navbar .wujia-header-badge')].map(b => {
              const r=b.getBoundingClientRect(); const btn=b.closest('a').getBoundingClientRect();
              return {cls:b.className, txt:b.textContent.trim(),
                      shown:getComputedStyle(b).display!=='none',
                      inside: r.x>=btn.x-4 && r.x+r.width<=btn.x+btn.width+4};})""")
        for bd in badges:
            print(f"  {bd}")
        ok(len(badges) == 2, "đủ 2 badge (cart + bell)", str(len(badges)))
        ok(all(bd["inside"] for bd in badges if bd["shown"]),
           "badge nằm trong circle, không lệch")
        p.close()

        # ---------------------------------------------------- 4. regression ---
        print("\n=== 4. Regression mobile 391×844 + tablet 1100 ===")
        for route in ROUTES:
            p, resp, errs = open_page(ctx, route, MOB)
            h = p.evaluate("""() => {
                const e=document.querySelector('.wujia-mheader'); if(!e) return null;
                const r=e.getBoundingClientRect();
                return {x:+r.x.toFixed(1), y:+r.y.toFixed(1), w:+r.width.toFixed(1), h:+r.height.toFixed(1)};}""")
            ovf = p.evaluate("() => document.documentElement.scrollWidth - "
                             "document.documentElement.clientWidth")
            pc_nav = p.evaluate("""() => {
                const u=document.querySelector('.wj-pc-navactions');
                return u ? getComputedStyle(u).gap : 'no-ul';}""")
            ok(resp.status == 200 and h and h["x"] == 0 and h["w"] == 391 and ovf <= 0,
               f"mobile {route}", f"header={h} overflow={ovf} navactions.gap={pc_nav}")
            p.close()
        p, resp, errs = open_page(ctx, "/portal", TABLET)
        ovf = p.evaluate("() => document.documentElement.scrollWidth - "
                         "document.documentElement.clientWidth")
        ok(resp.status == 200 and ovf <= 0 and not errs,
           "tablet 1100 /portal", f"overflow={ovf} errs={errs[:1]}")
        p.close()

        b.close()

    print(f"\n===== FAIL: {len(FAIL)} =====")
    for f in FAIL:
        print("  -", f)
    sys.exit(1 if FAIL else 0)


if __name__ == "__main__":
    main()
