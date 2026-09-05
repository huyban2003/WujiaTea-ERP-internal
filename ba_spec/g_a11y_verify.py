#!/usr/bin/env python3
"""Cụm G — harness đo thật: contrast 4 state · touch-target 44×44 · tab-walk · regression."""
import sys
from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:8033"
USER, PWD = "em.hcm", "demo123"
MOB, PC = (391, 844), (1920, 1080)
FAIL = []


def ok(cond, label, detail=""):
    print(("  OK   " if cond else "  FAIL ") + label + ("  " + detail if detail else ""))
    if not cond:
        FAIL.append(label + " " + detail)


def srgb(c):
    c = c / 255
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def lum(rgb):
    r, g, b = rgb
    return 0.2126 * srgb(r) + 0.7152 * srgb(g) + 0.0722 * srgb(b)


def parse(css):
    nums = [float(x) for x in css.replace("rgba", "").replace("rgb", "")
            .strip("() ").split(",")]
    return tuple(nums[:3]), (nums[3] if len(nums) > 3 else 1.0)


def ratio(fg_css, bg_css):
    fg, _ = parse(fg_css)
    bg, a = parse(bg_css)
    if a == 0:                      # nền trong suốt → coi như trắng (card portal)
        bg = (255, 255, 255)
    l1, l2 = lum(fg), lum(bg)
    hi, lo = max(l1, l2), min(l1, l2)
    return round((hi + 0.05) / (lo + 0.05), 2)


def login(ctx):
    p = ctx.new_page()
    p.goto(f"{BASE}/web/login", wait_until="domcontentloaded")
    p.fill("input[name=login]", USER)
    p.fill("input[name=password]", PWD)
    p.press("input[name=password]", "Enter")
    p.wait_for_timeout(2500)
    p.close()


def goto(ctx, url, size):
    p = ctx.new_page()
    p.set_viewport_size({"width": size[0], "height": size[1]})
    errs = []
    p.on("pageerror", lambda e: errs.append(str(e)))
    r = p.goto(BASE + url, wait_until="load")
    p.wait_for_timeout(1200)
    return p, r, errs


# ---------------------------------------------------------------- contrast ---
CONTRAST_JS = """(sel) => {
  const el = document.querySelector(sel);
  if (!el) return null;
  const cs = getComputedStyle(el);
  return {bg: cs.backgroundColor, fg: cs.color, opacity: cs.opacity,
          w: el.getBoundingClientRect().width,
          h: el.getBoundingClientRect().height};
}"""


def check_contrast(page, sel, label, force=None):
    """force = 'hover' | 'focus' | 'disabled' (dùng CSS state simulate qua JS)."""
    if force == "disabled":
        # setAttribute chứ không phải .disabled=true — property chưa reflect kịp
        # trong cùng tick, đo ra màu default (bẫy đã dính 1 lần)
        page.evaluate("(s)=>{const e=document.querySelector(s);"
                      " if(e) e.setAttribute('disabled','disabled');}", sel)
        page.wait_for_timeout(300)
    if force == "hover":
        el = page.query_selector(sel)
        if el:
            el.hover()
            page.wait_for_timeout(200)
    if force == "focus":
        page.evaluate("(s)=>{const e=document.querySelector(s); if(e) e.focus();}", sel)
        page.wait_for_timeout(200)
    d = page.evaluate(CONTRAST_JS, sel)
    if d is None:
        ok(False, f"contrast {label} [{force or 'default'}]", "NOT FOUND")
        return
    r = ratio(d["fg"], d["bg"])
    ok(r >= 4.5 and d["opacity"] == "1", f"contrast {label} [{force or 'default'}]",
       f"{r}:1  fg={d['fg']} bg={d['bg']} opacity={d['opacity']}")
    if force == "disabled":
        page.evaluate("(s)=>{const e=document.querySelector(s);"
                      " if(e) e.removeAttribute('disabled');}", sel)


# ------------------------------------------------------------ touch target ---
HIT_JS = """(sel) => {
  const out = [];
  document.querySelectorAll(sel).forEach((el) => {
    const b = el.getBoundingClientRect();
    if (b.width === 0 || b.height === 0) return;   // nút của nhánh không render (qty=0/qty>0)
    const a = getComputedStyle(el, '::after');
    // hit-area = hợp của box nút và box ::after (::after absolute, đã centered)
    let hw = b.width, hh = b.height;
    if (a && a.content !== 'none') {
      const aw = parseFloat(a.width) || 0, ah = parseFloat(a.height) || 0;
      hw = Math.max(hw, aw); hh = Math.max(hh, ah);
    }
    out.push({cls: el.className, w: +b.width.toFixed(1), h: +b.height.toFixed(1),
              hw: +hw.toFixed(1), hh: +hh.toFixed(1),
              cx: b.x + b.width / 2, cy: b.y + b.height / 2});
  });
  return out;
}"""

HITTEST_JS = """(args) => {
  const [sel, dx, dy] = args;
  const out = [];
  document.querySelectorAll(sel).forEach((el) => {
    const b = el.getBoundingClientRect();
    if (b.width === 0 || b.height === 0) return;
    const pt = document.elementFromPoint(b.x + b.width / 2 + dx, b.y + b.height / 2 + dy);
    out.push({cls: el.className, hit: pt ? (pt === el || el.contains(pt) ||
              (pt.parentElement === el)) : false,
              got: pt ? pt.className || pt.tagName : 'null'});
  });
  return out;
}"""


def check_hit(page, sel, label, minw, minh):
    items = page.evaluate(HIT_JS, sel)
    if not items:
        ok(False, f"touch {label}", "NOT FOUND (giỏ rỗng?)")
        return
    for i, it in enumerate(items):
        ok(it["hw"] >= minw and it["hh"] >= minh, f"touch {label}#{i}",
           f"visual {it['w']}x{it['h']} → hit {it['hw']}x{it['hh']} (cần ≥{minw}x{minh})")


# --------- so TRƯỚC/SAU: tắt đúng 2 rule mới rồi đo lại, phải y hệt ----------
REVERT_CSS = """
.wujia-morder-row-add::after, .wujia-morder-mstep::after,
.wujia-mcart-step::after, .wujia-mcart-del::after { display: none !important; }
.wujia-morder-mstepper, .wujia-mcart-stepper { overflow: hidden !important; }
"""

BOXES_JS = """(sel) => Array.from(document.querySelectorAll(sel))
    .map(e => { const b = e.getBoundingClientRect();
                return [+b.width.toFixed(1), +b.height.toFixed(1)]; })"""


def no_regress(page, sel, label):
    """Đo box với rule mới, tắt rule mới, đo lại → phải giống hệt (layout không đổi)."""
    after = page.evaluate(BOXES_JS, sel)
    page.add_style_tag(content=REVERT_CSS)
    page.wait_for_timeout(250)
    before = page.evaluate(BOXES_JS, sel)
    page.evaluate("()=>{const s=document.querySelectorAll('style');"
                  " s[s.length-1].remove();}")
    page.wait_for_timeout(250)
    ok(bool(after) and after == before, f"layout {label} không đổi trước/sau",
       f"sau={after[:3]} trước={before[:3]}")


def main():
    with sync_playwright() as pw:
        br = pw.chromium.launch()
        ctx = br.new_context()
        login(ctx)

        # ============================ 1. WJ-ORD-012 contrast CTA ==============
        print("\n== WJ-ORD-012 · contrast nút CTA ==")
        # trang chi tiết SP (mobile + PC)
        p, r, _ = goto(ctx, "/portal/order", MOB)
        href = p.evaluate("()=>{const a=document.querySelector('.wujia-morder-row-link,"
                          " a[href*=\"/portal/order/product/\"]'); return a? a.getAttribute('href'):null;}")
        p.close()
        for size, tag in ((MOB, "mobile"), (PC, "pc")):
            if not href:
                ok(False, f"product detail {tag}", "không tìm được link SP")
                continue
            p, r, errs = goto(ctx, href, size)
            ok(r.status == 200, f"product detail {tag} HTTP", str(r.status))
            for st in (None, "hover", "focus", "disabled"):
                check_contrast(p, ".btn-add-cart-detail", f"Thêm vào giỏ ({tag})", st)
            cls = p.evaluate("()=>{const e=document.querySelector('.btn-add-cart-detail');"
                             " return e? e.className : '';}")
            ok("btn-primary" not in cls, f"btn-primary đã gỡ khỏi CTA ({tag})", cls)
            p.close()

        # nút "Đổi cửa hàng" trong store picker + 2 nút "Vào cửa hàng"
        p, r, _ = goto(ctx, "/portal", PC)
        n = p.evaluate("()=>document.querySelectorAll('.wj-cta-btn').length")
        print(f"  info  .wj-cta-btn trên /portal = {n}")
        p.close()
        p, r, _ = goto(ctx, "/portal/franchises", PC)
        if p.query_selector(".wj-cta-btn"):
            for st in (None, "hover"):
                check_contrast(p, ".wj-cta-btn", "Vào cửa hàng (pc)", st)
        else:
            print("  info  /portal/franchises không có nút (user 1 cửa hàng) — bỏ qua")
        p.close()

        # .btn-primary ở nơi khác PHẢI giữ nguyên brand #28A9DF (không đụng Bootstrap)
        p, r, _ = goto(ctx, "/portal", PC)
        bp = p.evaluate("""()=>{const e=document.querySelector('.btn-primary');
            if(!e) return null; const c=getComputedStyle(e); return c.backgroundColor;}""")
        if bp:
            ok(bp.replace(" ", "") in ("rgb(40,169,223)",), ".btn-primary GIỮ NGUYÊN brand", str(bp))
        else:
            print("  info  không còn .btn-primary nào render trên /portal")
        p.close()

        # nút "Đổi cửa hàng" của store picker chỉ hiện với user nhiều cửa hàng
        ctx2 = br.new_context()
        p = ctx2.new_page()
        p.goto(f"{BASE}/web/login", wait_until="domcontentloaded")
        p.fill("input[name=login]", "dung.multi")
        p.fill("input[name=password]", "demo123")
        p.press("input[name=password]", "Enter")
        p.wait_for_timeout(2500)
        p.set_viewport_size({"width": PC[0], "height": PC[1]})
        p.goto(BASE + "/portal", wait_until="load")
        p.wait_for_timeout(1200)
        if p.query_selector(".wujia-store-footer .wj-cta-btn"):
            for st in (None, "hover"):
                check_contrast(p, ".wujia-store-footer .wj-cta-btn", "store picker (pc)", st)
        else:
            ok(False, "store picker CTA", "không tìm thấy .wujia-store-footer .wj-cta-btn")
        p.close()
        ctx2.close()

        # ============================ 2. WJ-ORD-011 touch target =============
        print("\n== WJ-ORD-011 · vùng chạm ==")
        p, r, errs = goto(ctx, "/portal/order", MOB)
        ok(r.status == 200, "/portal/order mobile HTTP", str(r.status))
        check_hit(p, ".wujia-morder-row-add", "catalog Thêm (mobile)", 44, 44)
        check_hit(p, ".wujia-morder-mstep", "catalog stepper (mobile)", 44, 44)
        # nút − và + phải nhận đúng cú chạm của chính nó
        for dx in (-14, 0, 14):
            res = p.evaluate(HITTEST_JS, [".wujia-morder-mstep", dx, 0])
            for i, h in enumerate(res):
                ok(h["hit"], f"hittest catalog step#{i} dx={dx}", h["got"])
        no_regress(p, ".wujia-morder-row", "row catalog")
        no_regress(p, ".wujia-morder-mstepper", "stepper catalog")
        ovf = p.evaluate("()=>document.documentElement.scrollWidth - window.innerWidth")
        ok(ovf <= 0, "overflow ngang /portal/order mobile", str(ovf))
        ok(not errs, "0 JS pageerror /portal/order", str(errs[:1]))
        p.close()

        p, r, errs = goto(ctx, "/portal/order/cart", MOB)
        ok(r.status == 200, "/portal/order/cart mobile HTTP", str(r.status))
        check_hit(p, ".wujia-mcart-step", "giỏ stepper (mobile)", 44, 44)
        check_hit(p, ".wujia-mcart-del", "giỏ xoá (mobile)", 44, 44)
        for dx in (-14, 0, 14):
            res = p.evaluate(HITTEST_JS, [".wujia-mcart-step", dx, 0])
            for i, h in enumerate(res):
                ok(h["hit"], f"hittest cart step#{i} dx={dx}", h["got"])
        no_regress(p, ".wujia-mcart-row", "card giỏ")
        no_regress(p, ".wujia-mcart-stepper", "stepper giỏ")
        ovf = p.evaluate("()=>document.documentElement.scrollWidth - window.innerWidth")
        ok(ovf <= 0, "overflow ngang giỏ mobile", str(ovf))
        p.close()

        p, r, _ = goto(ctx, "/portal/order/cart", PC)
        check_hit(p, ".wj-pc-cart-step", "giỏ stepper (PC)", 32, 32)
        check_hit(p, ".wj-pc-cart-del", "giỏ xoá (PC)", 32, 32)
        p.close()

        # ============================ 3. WJ-ORD-019 focus ====================
        print("\n== WJ-ORD-019 · focus ring + Enter submit + tab-walk ==")
        for size, sel, tag in ((MOB, ".wujia-morder-search-input input", "mobile"),
                               (PC, ".wj-pc-order-search input", "pc")):
            p, r, _ = goto(ctx, "/portal/order", size)
            p.evaluate("""(s)=>{const e=document.querySelector(s); if(e){e.focus();
                e.dispatchEvent(new Event('focus'));}}""", sel)
            # focus-visible chỉ bật khi focus bằng bàn phím → dùng Tab thật
            p.keyboard.press("Tab")
            o = p.evaluate("""(s)=>{const e=document.querySelector(s); if(!e) return null;
                e.focus({focusVisible:true});
                const c=getComputedStyle(e);
                return {w:c.outlineWidth, st:c.outlineStyle, col:c.outlineColor,
                        matches: e.matches(':focus-visible')};}""", sel)
            if o is None:
                ok(False, f"search input {tag}", "NOT FOUND")
            else:
                w = float(o["w"].replace("px", "") or 0)
                ok(w >= 2 and o["st"] != "none", f"focus ring search {tag}",
                   f"{o['w']} {o['st']} {o['col']} (:focus-visible={o['matches']})")
                if o["col"]:
                    rr = ratio(o["col"], "rgb(255,255,255)")
                    ok(rr >= 3, f"ring contrast vs trắng {tag}", f"{rr}:1")
            # Enter submit
            p.fill(sel, "Tra")
            p.press(sel, "Enter")
            p.wait_for_timeout(1500)
            ok("keyword=Tra" in p.url, f"Enter submit {tag}", p.url.split("?")[-1][:60])
            p.close()

        # tab-walk thật trên mobile
        p, r, _ = goto(ctx, "/portal/order", MOB)
        p.evaluate("()=>document.body.focus()")
        walk = []
        for _ in range(22):
            p.keyboard.press("Tab")
            info = p.evaluate("""()=>{const e=document.activeElement; if(!e) return null;
                const c=getComputedStyle(e); const b=e.getBoundingClientRect();
                return {tag:e.tagName, cls:(e.className||'').toString().slice(0,46),
                        out:c.outlineWidth+' '+c.outlineStyle,
                        vis: b.width>0 && b.height>0};}""")
            walk.append(info)
        print("  tab-walk mobile:")
        hidden = 0
        for i, w in enumerate(walk):
            if not w:
                continue
            print(f"    {i:2d} {w['tag']:8s} {w['cls']:46s} out={w['out']:14s} visible={w['vis']}")
            if not w["vis"]:
                hidden += 1
        ok(hidden == 0, "tab KHÔNG chạm control ẩn", f"{hidden} control ẩn nhận focus")
        # mọi control CỦA TRANG ĐẶT HÀNG phải có ring ≥2px (shell/header ngoài scope)
        noring = [w["cls"] for w in walk if w and ("morder" in w["cls"] or "mcart" in w["cls"])
                  and (w["out"].split()[1] == "none" or float(w["out"].split()[0].rstrip("px")) < 2)]
        ok(not noring, "mọi control trang đặt hàng có ring ≥2px", str(noring))
        p.close()

        # ============================ 4. regression ==========================
        print("\n== Regression smoke ==")
        for url in ("/portal", "/portal/order", "/portal/order/cart",
                    "/portal/notification", "/portal/debt"):
            for size, tag in ((MOB, "391"), (PC, "1920")):
                p, r, errs = goto(ctx, url, size)
                ovf = p.evaluate("()=>document.documentElement.scrollWidth - window.innerWidth")
                ok(r.status == 200 and ovf <= 0 and not errs,
                   f"smoke {url} @{tag}", f"http={r.status} overflow={ovf} err={len(errs)}")
                p.close()

        br.close()

    print("\n" + "=" * 70)
    print(f"TỔNG: {len(FAIL)} FAIL")
    for f in FAIL:
        print("  ✗ " + f)
    sys.exit(1 if FAIL else 0)


main()
