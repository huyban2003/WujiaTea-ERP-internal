#!/usr/bin/env python3
"""B4 — kiểm hành vi Back (CMP-BPH-001) + đổi cửa hàng mobile (FUNC-MOB-SHELL-005).

    python3 b4_behavior.py [--base http://127.0.0.1:8055]
"""
import argparse
import sys
from urllib.parse import quote

from playwright.sync_api import sync_playwright

PWD = "wujia@test123"
BACK = ".wj-page-header__back"
results = []


def check(name, ok, detail=""):
    results.append((ok, name, detail))
    print(f"[{'PASS' if ok else 'FAIL'}] {name} — {detail}")


def login(page, base, user):
    page.goto(f"{base}/portal/login", wait_until="domcontentloaded")
    page.fill("#wj-auth-login", user)
    page.fill("#wj-auth-password", PWD)
    page.press("#wj-auth-password", "Enter")
    page.wait_for_url(lambda u: "/portal/login" not in u, timeout=20000)


def visible_back(page):
    return page.locator(BACK).locator("visible=true").first


def back_href(page):
    return page.evaluate(
        """() => {const a=[...document.querySelectorAll('.wj-page-header__back')]
             .find(e=>getComputedStyle(e).display!=='none'&&e.offsetParent!==null);
             return a && a.getAttribute('href');}"""
    )


def run_back(base, br):
    ctx = br.new_context(viewport={"width": 1920, "height": 1080})
    p = ctx.new_page()
    login(p, base, "anh.owner")

    # 1. Vào detail TỪ list có filter/page → giữ nguyên query
    p.goto(f"{base}/portal/support?page=1&status=open", wait_until="load")
    p.goto(f"{base}/portal/support/40", wait_until="load",
           referer=f"{base}/portal/support?page=1&status=open")
    href = back_href(p)
    check("return_url: referer list cha giữ filter/page",
          href == "/portal/support?page=1&status=open", f"href={href}")

    # 2. Deep-link (không referer) → list cha
    p.goto(f"{base}/portal/support/40", wait_until="load")
    href = back_href(p)
    check("deep-link không referer → list cha", href == "/portal/support", f"href={href}")

    # 3. Referer là trang KHÁC list cha → vẫn về list cha
    p.goto(f"{base}/portal/support/40", wait_until="load", referer=f"{base}/portal")
    href = back_href(p)
    check("referer ngoài list cha → fallback list cha", href == "/portal/support", f"href={href}")

    # 4. return_url ngoài phạm vi → bị bỏ
    for bad in ("https://evil.tld", "//evil.tld", "/web/database/manager", "/portal/../web"):
        p.goto(f"{base}/portal/support/40?return_url={bad}", wait_until="load")
        href = back_href(p)
        check(f"return_url ngoài phạm vi bị bỏ ({bad})", href == "/portal/support", f"href={href}")

    # 5. return_url nội bộ hợp lệ → dùng
    good = "/portal/support?status=closed&page=3"
    p.goto(f"{base}/portal/support/40?return_url={quote(good, safe='')}", wait_until="load")
    href = back_href(p)
    check("return_url nội bộ hợp lệ được dùng", href == good, f"href={href}")

    # 6. Tab/Enter điều hướng thật
    p.goto(f"{base}/portal/support/40", wait_until="load")
    for _ in range(60):
        p.keyboard.press("Tab")
        if p.evaluate("() => document.activeElement.classList.contains('wj-page-header__back')"):
            break
    focused = p.evaluate("() => document.activeElement.classList.contains('wj-page-header__back')")
    with p.expect_navigation(wait_until="load", timeout=15000):
        p.keyboard.press("Enter")
    check("Tab tới Back rồi Enter điều hướng",
          focused and p.url.endswith("/portal/support"), f"focused={focused} url={p.url}")

    # 7. Unsaved guard — form ĐÃ đổi thì hỏi, Cancel giữ nguyên trang
    p.goto(f"{base}/portal/return/new", wait_until="load")
    p.evaluate("""() => {const f=document.querySelector('form[data-wj-dirty-guard]');
        const t=f.querySelector('textarea, input[type=text]'); t.value='thay đổi thử';
        t.dispatchEvent(new Event('input', {bubbles:true}));}""")
    p.once("dialog", lambda d: d.dismiss())
    visible_back(p).click()
    p.wait_for_timeout(800)
    check("form chưa lưu: Cancel giữ nguyên màn",
          "/portal/return/new" in p.url, f"url={p.url}")
    check("form chưa lưu: dữ liệu vừa gõ còn nguyên",
          p.evaluate("""() => {const f=document.querySelector('form[data-wj-dirty-guard]');
              const t=f.querySelector('textarea, input[type=text]'); return t.value;}""") == "thay đổi thử")

    # 8. Unsaved guard — OK thì rời
    p.once("dialog", lambda d: d.accept())
    visible_back(p).click()
    p.wait_for_load_state("load")
    check("form chưa lưu: OK thì rời về list cha", p.url.endswith("/portal/return"), f"url={p.url}")

    # 9. Form KHÔNG đổi → không hỏi, đi thẳng
    p.goto(f"{base}/portal/return/new", wait_until="load")
    asked = []
    p.on("dialog", lambda d: (asked.append(d.message), d.accept()))
    visible_back(p).click()
    p.wait_for_load_state("load")
    check("form không đổi: KHÔNG hỏi, Back đi thẳng",
          not asked and p.url.endswith("/portal/return"), f"asked={asked} url={p.url}")
    ctx.close()


def strip_state(page):
    return page.evaluate(
        """() => {const s=document.querySelector('.wujia-store-mobile-strip');
          if(!s) return null;
          const cs=getComputedStyle(s), r=s.getBoundingClientRect();
          return {tag:s.tagName, clickable:s.classList.contains('wujia-store-mobile-strip--clickable'),
                  code:(s.querySelector('.wujia-store-strip-code')||{}).textContent,
                  name:(s.querySelector('.wujia-store-mobile-strip-name')||{}).textContent,
                  role:(s.querySelector('.wujia-store-strip-role')||{}).textContent,
                  h:+r.height.toFixed(1), display:cs.display};}"""
    )


def overlay_shown(page):
    return page.evaluate(
        """() => {const o=document.getElementById('wujiaStoreOverlay');
          if(!o) return null;
          const cs=getComputedStyle(o), r=o.querySelector('.wujia-store-card').getBoundingClientRect();
          return {shown: cs.display!=='none',
                  card:{x:+r.x.toFixed(1), y:+r.y.toFixed(1), w:+r.width.toFixed(1), h:+r.height.toFixed(1)},
                  items:[...o.querySelectorAll('.wujia-store-item')].map(i=>({
                      txt:i.innerText.replace(/\\s+/g,' ').trim(),
                      active:i.classList.contains('wujia-store-item--active'),
                      checked:i.querySelector('input').checked, val:i.querySelector('input').value})),
                  title:o.querySelector('.wujia-store-header').innerText.trim()};}"""
    )


def run_store(base, br):
    ctx = br.new_context(viewport={"width": 391, "height": 844})
    p = ctx.new_page()
    errs = []
    p.on("pageerror", lambda e: errs.append(str(e)))
    login(p, base, "dung.multi")
    p.goto(f"{base}/portal/order", wait_until="load")

    # nếu chưa chọn cửa hàng thì overlay bật sẵn (must_pick) → chọn cửa hàng đầu
    if (overlay_shown(p) or {}).get("shown"):
        p.locator(".wujia-store-item").first.click()
        p.locator("#wujiaStoreOverlay button[type=submit]").click()
        p.wait_for_load_state("load")

    st0 = strip_state(p)
    check("strip mobile là link bấm được", st0 and st0["tag"] == "A" and st0["clickable"], str(st0))
    check("strip giữ nguyên chiều cao 48", st0 and st0["h"] >= 48, f"h={st0['h'] if st0 else None}")

    # (1) bấm strip mở popup
    p.click(".wujia-store-mobile-strip")
    p.wait_for_timeout(300)
    ov = overlay_shown(p)
    check("(1) bấm Current Store mở popup", ov["shown"], ov["title"])
    check("(1) popup đúng tiêu đề", "Đổi cửa hàng đang thao tác" in ov["title"], ov["title"])

    # (2) đủ cửa hàng được phép + đánh dấu cửa hàng hiện tại
    check("(2) popup liệt kê đủ cửa hàng được phép", len(ov["items"]) == 3, f"{len(ov['items'])} item")
    cur = [i for i in ov["items"] if i["active"]]
    check("(2) đánh dấu đúng 1 cửa hàng hiện tại", len(cur) == 1 and st0["code"].strip() in cur[0]["txt"],
          f"active={cur}")

    # (6) không tràn ở 391×844
    vw = p.evaluate("() => [innerWidth, document.documentElement.scrollWidth]")
    check("(6) popup không tràn ngang ở 391×844",
          ov["card"]["x"] >= 0 and ov["card"]["x"] + ov["card"]["w"] <= 391.5 and vw[1] <= vw[0],
          f"card={ov['card']} scrollW={vw[1]}")

    # (3) Hủy không đổi cửa hàng
    p.click("[data-action='close-store-picker']:not(.wujia-store-close)")
    p.wait_for_timeout(300)
    check("(3) Hủy đóng popup", not overlay_shown(p)["shown"])
    st_cancel = strip_state(p)
    check("(3) Hủy KHÔNG đổi cửa hàng", st_cancel["code"] == st0["code"],
          f"{st0['code']} -> {st_cancel['code']}")

    # (3b) nút × cũng không đổi
    p.click(".wujia-store-mobile-strip")
    p.wait_for_timeout(200)
    p.click(".wujia-store-close")
    p.wait_for_timeout(200)
    check("(3b) nút × đóng, không đổi cửa hàng", strip_state(p)["code"] == st0["code"])

    # (4)(5) chọn cửa hàng khác + xác nhận
    cart_js = """() => {const b=document.querySelector('.wujia-header-cart-count');
             return b ? {txt: b.innerText.trim(), hidden: b.hasAttribute('hidden')} : null;}"""
    cart_before = p.evaluate(cart_js)
    p.click(".wujia-store-mobile-strip")
    p.wait_for_timeout(200)
    items = [i for i in overlay_shown(p)["items"] if not i["active"]]
    other = next((i for i in items if i["val"] == "2"), items[0])   # HN-02: role manager ≠ staff
    p.click(f".wujia-store-item:has(input[value='{other['val']}'])")
    p.click("#wujiaStoreOverlay button[type=submit]")
    p.wait_for_load_state("load")
    st1 = strip_state(p)
    check("(4) xác nhận đổi được cửa hàng", st1["code"] != st0["code"], f"{st0['code']} -> {st1['code']}")
    check("(4) ở lại đúng trang đang xem", "/portal/order" in p.url, p.url)
    r0, r1 = st0["role"].strip(), st1["role"].strip()
    check("(5) strip cập nhật mã/tên/role",
          st1["code"].strip() in other["txt"] and st1["name"].strip() and r1 == "Manager" and r0 == "Staff",
          f"{st0['code'].strip()}/{r0} -> {st1['code'].strip()}/{r1}")
    cookie = [c for c in ctx.cookies() if c["name"] == "wujia_active_franchise_id"]
    check("(4) cookie active franchise đổi theo", cookie and cookie[0]["value"] == other["val"],
          str(cookie))
    cart_after = p.evaluate(cart_js)
    # giỏ là của CỬA HÀNG: HCM-01 có 1 dòng (badge hiện), HN-02 giỏ rỗng (badge ẩn)
    check("(4) giỏ hàng đổi theo cửa hàng (badge hiện → ẩn)",
          cart_before and not cart_before["hidden"] and cart_after and cart_after["hidden"],
          f"badge {cart_before} -> {cart_after}")
    check("0 JS pageerror suốt luồng", not errs, str(errs[:2]))
    ctx.close()


def run_pc_baseline(base, br):
    """PC là baseline hành vi: strip mobile phải dùng đúng popup/route này."""
    ctx = br.new_context(viewport={"width": 1920, "height": 1080})
    p = ctx.new_page()
    login(p, base, "dung.multi")
    p.goto(f"{base}/portal/order", wait_until="load")
    if (overlay_shown(p) or {}).get("shown"):
        p.locator(".wujia-store-item").first.click()
        p.locator("#wujiaStoreOverlay button[type=submit]").click()
        p.wait_for_load_state("load")
    p.click("[data-action='open-store-picker']")
    p.wait_for_timeout(300)
    ov = overlay_shown(p)
    check("PC baseline: badge mở cùng popup, cùng danh sách",
          ov["shown"] and len(ov["items"]) == 3, f"{len(ov['items'])} item")
    check("PC baseline: cùng form POST /portal/franchise/switch",
          p.evaluate("() => document.querySelector('#wujiaStoreOverlay form').getAttribute('action')")
          == "/portal/franchise/switch")
    ctx.close()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="http://127.0.0.1:8055")
    a = ap.parse_args()
    with sync_playwright() as pw:
        br = pw.chromium.launch()
        print("=== UI-BACKPAGEHEADER-001 · behavior ===")
        run_back(a.base, br)
        print("\n=== FUNC-MOB-SHELL-005 · PC baseline ===")
        run_pc_baseline(a.base, br)
        print("\n=== FUNC-MOB-SHELL-005 · mobile end-to-end ===")
        run_store(a.base, br)
        br.close()
    bad = [r for r in results if not r[0]]
    print(f"\nTOTAL {len(results) - len(bad)}/{len(results)} PASS")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
