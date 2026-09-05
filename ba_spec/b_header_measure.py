#!/usr/bin/env python3
"""Cụm B — đo cụm hành động bên phải của header PC (UI-03 · UI-PC-BASE-011 · UI-02).

Đo `<a>` bên trong mỗi `<li>`, KHÔNG đo `<li>`: doc cụm B ghi "actual" theo bbox của
`<li>` (cao 62.3 vì nav-item ăn hết chiều cao navbar) nên tưởng pill sai, trong khi
CSS đã ép `<a>` về đúng size. L7 — đo cái đang được style, không đo cái bọc ngoài.
"""
import sys
from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:8102"
USER, PWD = "em.hcm", "demo123"
PC, MOB = (1920, 1080), (391, 844)
FAIL = []


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
        sys.exit("LOGIN FAILED — dừng ngay, đừng để mọi assert pass rỗng")
    p.close()


BOX_JS = """(sel) => {
  const el = document.querySelector(sel);
  if (!el) return null;
  const r = el.getBoundingClientRect();
  const cs = getComputedStyle(el);
  return {x: +r.x.toFixed(1), y: +r.y.toFixed(1),
          w: +r.width.toFixed(1), h: +r.height.toFixed(1),
          radius: cs.borderRadius, bg: cs.backgroundColor,
          pad: cs.padding, display: cs.display, gap: cs.gap,
          mr: cs.marginRight, order: cs.order};
}"""

TARGETS = [
    ("language pill", "li.dropdown-language > a.nav-link"),
    ("cart circle", "li.wujia-header-icon-item a[href='/portal/order']"),
    ("bell circle", "li.wujia-header-icon-item a[href='/portal/notification']"),
    ("account pill", "li.dropdown-user > a.dropdown-user-link"),
    ("avatar img", "li.dropdown-user > a.dropdown-user-link img.round"),
    ("navbar-container", ".wujia-navbar .navbar-container"),
    ("ul actions", ".wujia-navbar ul.nav.navbar-nav.float-right"),
]


def measure(page, tag):
    print(f"\n--- {tag} ---")
    out = {}
    for label, sel in TARGETS:
        box = page.evaluate(BOX_JS, sel)
        out[label] = box
        if box is None:
            print(f"  {label:18s} MISSING ({sel})")
            continue
        print(f"  {label:18s} {box['x']},{box['y']} {box['w']}×{box['h']}  "
              f"r={box['radius']} bg={box['bg']} pad={box['pad']} mr={box['mr']}")
    # thứ tự DOM trong account pill: avatar trước hay sau khối tên?
    order = page.evaluate("""() => {
      const a = document.querySelector('li.dropdown-user > a.dropdown-user-link');
      if (!a) return null;
      return [...a.children].map(c => c.tagName.toLowerCase() + '.' + (c.className || ''));
    }""")
    print(f"  DOM order account : {order}")
    out["_order"] = order
    return out


def main():
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        ctx = b.new_context(viewport={"width": PC[0], "height": PC[1]})
        login(ctx)
        p = ctx.new_page()
        p.set_viewport_size({"width": PC[0], "height": PC[1]})
        p.goto(BASE + "/portal", wait_until="load")
        p.wait_for_timeout(1500)
        # overlay chọn cửa hàng chặn đo — chọn cửa hàng đầu tiên nếu có
        if p.locator("#wujiaStoreOverlay").count():
            vis = p.evaluate("() => !!document.querySelector('#wujiaStoreOverlay') && "
                             "getComputedStyle(document.querySelector('#wujiaStoreOverlay')).display !== 'none'")
            if vis:
                p.locator("input.wujia-store-radio").first.check()
                p.evaluate("() => document.querySelector('form.wujia-store-form').submit()")
                p.wait_for_timeout(2000)
        pc = measure(p, "PC 1920×1080 /portal")

        print("\n--- source v1.5 expected ---")
        print("  language pill      1450,16 118×40")
        print("  cart circle        1590,16 40×40 r20 glass")
        print("  bell circle        1642,16 40×40 r20 glass")
        print("  account pill       1696,10 204×52 r18 glass")
        print("  avatar             36×36, tâm (1724,36), BÊN TRÁI tên")
        print("  mép phải cụm       1900 (padding-right 20)")

        acct = pc.get("account pill")
        if acct:
            print(f"\n  mép phải cụm hiện tại = {acct['x'] + acct['w'] + float(acct['mr'].rstrip('px') or 0)}")

        # mobile baseline
        p2 = ctx.new_page()
        p2.set_viewport_size({"width": MOB[0], "height": MOB[1]})
        p2.goto(BASE + "/portal", wait_until="load")
        p2.wait_for_timeout(1200)
        mob = p2.evaluate("""() => {
          const h = document.querySelector('.wujia-mheader') || document.querySelector('.header-navbar');
          if (!h) return null;
          const r = h.getBoundingClientRect();
          return {cls: h.className, x:+r.x.toFixed(1), y:+r.y.toFixed(1),
                  w:+r.width.toFixed(1), h:+r.height.toFixed(1),
                  overflow: document.documentElement.scrollWidth - document.documentElement.clientWidth};
        }""")
        print(f"\n--- mobile 391×844 baseline ---\n  {mob}")

        b.close()
    print("\nFAIL:", len(FAIL))


if __name__ == "__main__":
    main()
