#!/usr/bin/env python3
"""Cụm C — đo vỏ mobile portal: UI-04 · RESP-MOB-SHELL-003 · RESP-MOB-ORDER-001.

Chạy 2 lần (BEFORE khi chưa sửa, AFTER sau khi sửa). BEFORE phải tái hiện đúng dãy
162/163/166/168/169/176 mà BA đo trên UAT — không tái hiện thì harness sai, sửa harness
trước rồi mới sửa code (L7: nguồn chân lý là số đo của BA, không phải kỳ vọng mình gõ ra).

Mốc chuẩn: dải chọn cửa hàng kết ở y=152, content bắt đầu y=152+16=168, x=16.
"""
import os
import sys
from playwright.sync_api import sync_playwright

# Mặc định = DB copy cô lập local. Đo trên UAT thì:
#   WJ_BASE=http://113.161.187.126:8019 WJ_USER=admin WJ_PWD=Wujia@2026 python3 … --readonly
# --readonly BẮT BUỘC khi chạy trên UAT: bỏ bước bấm thêm vào giỏ (giới hạn QA — không
# tạo dữ liệu thật trên máy chủ kiểm thử).
BASE = os.environ.get("WJ_BASE", "http://127.0.0.1:8103").rstrip("/")
USER = os.environ.get("WJ_USER", "em.hcm")
PWD = os.environ.get("WJ_PWD", "demo123")
READONLY = "--readonly" in sys.argv
MOB, PC = (391, 844), (1920, 1080)
EXPECT_Y, TOL = 168, 1

FAIL = []

# 10 route BA liệt kê + 3 route họ A ngoài danh sách nhưng cùng bị ảnh hưởng.
ROUTES = [
    "/portal",
    "/portal/order",
    "/portal/order/cart",
    "/portal/purchase-history",
    "/portal/delivery",
    "/portal/notification",
    "/portal/knowledge",
    "/portal/support",
    "/portal/profile",
    "/portal/return",
]
ROUTES_EXTRA = [
    "/portal/exam",
    "/portal/franchise-information",
    "/portal/change-password",
    "/portal/reports/orders",
]

# Lỗi 500 CÓ SẴN ngoài phạm vi cụm C (tz user 'Asia/Saigon' không được Postgres nhận —
# §5 "Pre-existing"). Không tính FAIL, nhưng vẫn in ra để không lặng lẽ bỏ qua.
KNOWN_500 = {"/portal/reports/orders"}


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
    # Overlay chọn cửa hàng che trang ⇒ mọi assert nội dung pass rỗng (L8). Overlay CHỈ
    # xuất hiện ở /portal — sau login tài khoản admin rơi về /odoo (backend), soi overlay
    # ngay tại đó sẽ không thấy gì và tưởng là đã chọn cửa hàng rồi.
    p.goto(f"{BASE}/portal", wait_until="domcontentloaded")
    p.wait_for_timeout(1500)
    if p.query_selector("#wujiaStoreOverlay"):
        radio = p.query_selector("input.wujia-store-radio")
        if radio:
            radio.check()
            p.eval_on_selector("form.wujia-store-form", "f => f.submit()")
            p.wait_for_timeout(3000)
    if not p.query_selector(".wujia-store-mobile-strip"):
        sys.exit("CHƯA CHỌN ĐƯỢC CỬA HÀNG — dải cửa hàng không có thì mốc y không so được")
    p.close()


# Mốc "bắt đầu nội dung" = phần tử đầu tiên NHÌN THẤY sau khi đã đi xuyên hết các lớp
# wrapper trang. Bỏ qua header/overlay/shadow/dải cửa hàng; wrapper PC (.content-wrapper
# d-none) tự loại vì display:none. Phải đi xuyên nhiều lớp: /portal lồng
# .content-wrapper > .wujia-mhome > <nội dung>, /portal/order lồng
# .content-wrapper > .wujia-morder > .wujia-morder-titlerow — đo lớp bọc sẽ ra 152/176
# thay vì mốc BA thật sự nhìn thấy.
FIRST_CONTENT_JS = """() => {
  const vis = el => {
    const cs = getComputedStyle(el);
    if (cs.display === 'none' || cs.visibility === 'hidden') return false;
    return el.getBoundingClientRect().height > 0;
  };
  const firstVisChild = el => {
    for (const c of el.children) if (vis(c)) return c;
    return null;
  };
  const WRAPPER = /(^|\\s)(content-wrapper|wujia-home-wrapper|wujia-mreport-wrap|wujia-mpage|wujia-mhome|wujia-morder|wujia-mcart|wujia-mhist)(\\s|$)/;
  const skip = ['wujia-mheader', 'content-overlay', 'header-navbar-shadow',
                'wujia-store-mobile-strip', 'wujia-store-overlay'];
  const root = document.querySelector('.app-content.content');
  if (!root) return null;
  let node = null;
  for (const el of root.children) {
    if (skip.some(c => el.classList.contains(c)) || el.id === 'wujiaStoreOverlay') continue;
    if (!vis(el)) continue;
    node = el; break;
  }
  if (!node) return null;
  const chain = [];
  for (let i = 0; i < 4; i++) {
    const cn = node.className.toString();
    chain.push({cls: cn.trim().slice(0, 48), padTop: getComputedStyle(node).paddingTop});
    if (!WRAPPER.test(cn)) break;
    const nxt = firstVisChild(node);
    if (!nxt) break;
    node = nxt;
  }
  const r = node.getBoundingClientRect();
  return {
    chain: chain.map(c => c.cls + '[' + c.padTop + ']').join(' > '),
    first: node.className.toString().trim().slice(0, 48) || node.tagName,
    firstMarginTop: getComputedStyle(node).marginTop,
    y: +r.y.toFixed(1), x: +r.x.toFixed(1),
  };
}"""

STRIP_JS = """() => {
  const el = document.querySelector('.wujia-store-mobile-strip');
  if (!el) return null;
  const r = el.getBoundingClientRect();
  return {top: +r.top.toFixed(1), bottom: +r.bottom.toFixed(1)};
}"""

HEADER_JS = """() => {
  const h = document.querySelector('.wujia-mheader');
  const acts = [...document.querySelectorAll('.wujia-mheader-actions .wujia-mheader-action')];
  const box = el => { const r = el.getBoundingClientRect();
    return {x: +r.x.toFixed(1), y: +r.y.toFixed(1), w: +r.width.toFixed(1), h: +r.height.toFixed(1),
            cx: +((r.x + r.width / 2)).toFixed(1), cy: +((r.y + r.height / 2)).toFixed(1)}; };
  const glyph = document.querySelector('.wujia-mheader-avatar > svg, .wujia-mheader-avatar > i, .wujia-mheader-avatar > img');
  const cart = document.querySelector('.wujia-mheader-action[href="/portal/order/cart"] > svg, .wujia-mheader-action[href="/portal/order/cart"] > i');
  const badge = document.querySelector('.wujia-mheader-action .wujia-header-badge');
  const g = el => el ? {tag: el.tagName.toLowerCase(),
                        stroke: el.getAttribute('stroke-width') || getComputedStyle(el).strokeWidth,
                        mr: getComputedStyle(el).marginRight, ...box(el)} : null;
  return {
    header: h ? box(h) : null,
    actions: acts.map(box),
    avatarGlyph: g(glyph),
    cartGlyph: g(cart),
    badge: badge ? box(badge) : null,
  };
}"""

CLAMP_JS = """() => {
  const rows = [...document.querySelectorAll('.wujia-morder-row')];
  const out = [];
  for (const row of rows) {
    const name = row.querySelector('.wujia-morder-row-name');
    if (!name) continue;
    const cs = getComputedStyle(name);
    const lh = parseFloat(cs.lineHeight) || parseFloat(cs.fontSize) * 1.2;
    // shown = số dòng THẤY được (đã clamp); full = số dòng nếu không clamp.
    const lines = Math.round(name.clientHeight / lh);
    out.push({text: name.textContent.trim().slice(0, 40),
              lines, fullLines: Math.round(name.scrollHeight / lh), clamp: cs.webkitLineClamp,
              clipped: name.scrollHeight > name.clientHeight + 1,
              nameH: +name.getBoundingClientRect().height.toFixed(1),
              rowH: +row.getBoundingClientRect().height.toFixed(1)});
  }
  return out;
}"""

OVERFLOW_JS = "() => document.documentElement.scrollWidth - document.documentElement.clientWidth"


def measure_routes(ctx, routes, label):
    page = ctx.new_page()
    page.set_viewport_size({"width": MOB[0], "height": MOB[1]})
    print(f"\n===== {label} @391×844 =====")
    for route in routes:
        resp = page.goto(BASE + route, wait_until="domcontentloaded")
        page.wait_for_timeout(1200)
        if resp and resp.status != 200 and route in KNOWN_500:
            print(f"  SKIP  {route} HTTP {resp.status} — lỗi tz có sẵn, ngoài phạm vi cụm C")
            continue
        info = page.evaluate(FIRST_CONTENT_JS)
        strip = page.evaluate(STRIP_JS)
        ovf = page.evaluate(OVERFLOW_JS)
        if not info:
            ok(False, f"{route} — không tìm được wrapper nội dung")
            continue
        detail = (f"y={info['y']} x={info['x']} mt={info['firstMarginTop']} | {info['chain']}")
        ok(abs(info["y"] - EXPECT_Y) <= TOL, f"{route} content y=168", detail)
        ok(abs(info["x"] - 16) <= TOL, f"{route} content x=16", f"x={info['x']}")
        # Không có dải cửa hàng thì mốc 168 vô nghĩa (104+16=120) — phải FAIL, đừng skip.
        ok(strip is not None and abs(strip["bottom"] - 152) <= TOL,
           f"{route} strip kết y=152", str(strip))
        ok(ovf == 0, f"{route} overflow ngang=0", f"ovf={ovf}")
    page.close()


def measure_header(ctx):
    page = ctx.new_page()
    page.set_viewport_size({"width": MOB[0], "height": MOB[1]})
    page.goto(BASE + "/portal", wait_until="domcontentloaded")
    page.wait_for_timeout(1200)
    h = page.evaluate(HEADER_JS)
    print("\n===== UI-04 header mobile =====")
    print("  raw:", h)
    ok(h["header"] and (h["header"]["x"], h["header"]["y"], h["header"]["w"], h["header"]["h"]) == (0, 0, 391, 104),
       "header 0,0,391×104", str(h["header"]))
    want = [(247, 58), (301, 58), (355, 58)]
    ok(len(h["actions"]) == 3, "3 nút tròn", f"n={len(h['actions'])}")
    for i, a in enumerate(h["actions"][:3]):
        ok(a["w"] == 38 and a["h"] == 38, f"circle #{i+1} 38×38", f"{a['w']}×{a['h']}")
        ok(abs(a["cx"] - want[i][0]) <= TOL and abs(a["cy"] - want[i][1]) <= TOL,
           f"circle #{i+1} tâm {want[i]}", f"({a['cx']},{a['cy']}) y={a['y']}")
    g = h["avatarGlyph"]
    if g:
        # Doc cụm C ghi "tâm x = 356" theo vị trí TRƯỚC khi dịch cụm nút −1px; điều kiện
        # thật là glyph trùng tâm nút (L7 — đo cái đang được style, không tin số đã cũ).
        circle_cx = h["actions"][2]["cx"] if len(h["actions"]) > 2 else 0
        ok(abs(g["cx"] - circle_cx) <= 0.5, "tâm x glyph avatar trùng tâm circle",
           f"glyph={g['cx']} circle={circle_cx} mr={g['mr']} tag={g['tag']}")
    else:
        ok(False, "glyph avatar tồn tại")
    for key, name in (("avatarGlyph", "avatar"), ("cartGlyph", "giỏ")):
        el = h[key]
        if el and el["tag"] == "img":
            print(f"  SKIP  glyph {name} là ảnh thật (không phải icon)")
            continue
        ok(el is not None and el["tag"] == "svg", f"glyph {name} là svg",
           str(el["tag"]) if el else "None")
        if el:
            ok(str(el["stroke"]).startswith("2.4"), f"glyph {name} stroke-width 2.4", str(el["stroke"]))
    # Badge số lượng ẩn khi giỏ rỗng ⇒ phải bỏ 1 SP vào giỏ mới soi được vị trí của nó
    # so với nút đã dịch (badge neo theo .wujia-mheader-action, không theo glyph).
    page.goto(BASE + "/portal/order", wait_until="domcontentloaded")
    page.wait_for_timeout(1500)
    # Lần chạy sau giỏ đã có hàng ⇒ nút "Thêm" biến thành stepper (ẩn); chỉ bấm khi thấy nút.
    btn = None if READONLY else page.query_selector(".wujia-morder-add-btn")
    if READONLY:
        b = page.evaluate("""() => {
            const el = document.querySelector('.wujia-mheader-action .wujia-header-badge');
            const a = document.querySelector('.wujia-mheader-action[href="/portal/order/cart"]');
            if (!el || !a) return null;
            const r = el.getBoundingClientRect(), ra = a.getBoundingClientRect();
            return {text: el.textContent.trim(), w: +r.width.toFixed(1), h: +r.height.toFixed(1),
                    dTop: +(r.top - ra.top).toFixed(1), dRight: +(ra.right - r.right).toFixed(1)};
        }""")
        print("  badge (readonly, không bỏ hàng vào giỏ):", b)
        if b and b["w"] > 0:
            ok(abs(b["dTop"] + 3) <= 1 and abs(b["dRight"] + 3) <= 1,
               "badge vẫn neo top/right −3px so với nút", str(b))
        else:
            print("  SKIP  giỏ đang rỗng nên badge ẩn — không đo được vị trí (chế độ chỉ đọc)")
    if btn and btn.is_visible():
        btn.click()
        page.wait_for_timeout(2000)
    if btn:
        page.goto(BASE + "/portal", wait_until="domcontentloaded")
        page.wait_for_timeout(1500)
        b = page.evaluate("""() => {
            const el = document.querySelector('.wujia-mheader-action .wujia-header-badge');
            const a = document.querySelector('.wujia-mheader-action[href="/portal/order/cart"]');
            if (!el || !a) return null;
            const r = el.getBoundingClientRect(), ra = a.getBoundingClientRect();
            return {text: el.textContent.trim(), w: +r.width.toFixed(1), h: +r.height.toFixed(1),
                    dTop: +(r.top - ra.top).toFixed(1), dRight: +(ra.right - r.right).toFixed(1)};
        }""")
        print("  badge (giỏ có hàng):", b)
        ok(b is not None and b["w"] > 0, "badge giỏ hiện khi có hàng", str(b))
        ok(b is not None and abs(b["dTop"] + 3) <= 1 and abs(b["dRight"] + 3) <= 1,
           "badge vẫn neo top/right −3px so với nút", str(b))
    elif not READONLY:
        ok(False, "tìm được nút thêm vào giỏ để soi badge")
    page.close()


def measure_clamp(ctx):
    page = ctx.new_page()
    page.set_viewport_size({"width": MOB[0], "height": MOB[1]})
    page.goto(BASE + "/portal/order", wait_until="domcontentloaded")
    page.wait_for_timeout(1500)
    rows = page.evaluate(CLAMP_JS)
    print("\n===== RESP-MOB-ORDER-001 clamp tên SP =====")
    ok(len(rows) > 0, "có hàng sản phẩm", f"n={len(rows)}")
    for r in rows[:12]:
        print(f"  {r['lines']}/{r['fullLines']} dòng (thấy/đủ) · clamp={r['clamp']} · cắt={r['clipped']} · "
              f"nameH={r['nameH']} rowH={r['rowH']} · {r['text']}")
    # Demo data không có tên nào đủ dài để BỊ cắt ⇒ nhồi tên dài bằng JS (chỉ đổi DOM,
    # không đụng dữ liệu) để soi đúng hành vi "dài hơn 2 dòng thì cắt bằng …".
    long_name = page.evaluate("""() => {
      const n = document.querySelector('.wujia-morder-row-name');
      if (!n) return null;
      n.textContent = 'Trà sữa trân châu đường đen thượng hạng size cực đại kèm topping '
                    + 'phô mai macchiato và thạch dừa nguyên chất nhập khẩu';
      const cs = getComputedStyle(n);
      const lh = parseFloat(cs.lineHeight) || parseFloat(cs.fontSize) * 1.2;
      return {clipped: n.scrollHeight > n.clientHeight + 1,
              shownLines: Math.round(n.clientHeight / lh),
              fullLines: Math.round(n.scrollHeight / lh),
              nameH: +n.getBoundingClientRect().height.toFixed(1),
              rowH: +n.closest('.wujia-morder-row').getBoundingClientRect().height.toFixed(1)};
    }""")
    print("  tên dài (nhồi JS):", long_name)
    if long_name:
        ok(long_name["shownLines"] == 2 and long_name["clipped"],
           "tên dài bị cắt còn đúng 2 dòng (có …)", str(long_name))

    if rows:
        ok(all(r["clamp"] in ("2", 2) for r in rows), "line-clamp = 2 mọi hàng")
        ok(all(r["lines"] <= 2 for r in rows), "không hàng nào HIỆN quá 2 dòng",
           str([r["lines"] for r in rows]))
        # Hàng có stepper (đã vào giỏ) cột tên hẹp hơn ⇒ tên dài hơn phải bị cắt, đúng spec.
        for r in rows:
            if r["fullLines"] > 2:
                ok(r["clipped"], f"tên dài bị cắt: {r['text']}",
                   f"thấy {r['lines']}/{r['fullLines']} dòng")
        two = [r for r in rows if r["lines"] == 2]
        print(f"  → {len(two)}/{len(rows)} hàng ăn 2 dòng; "
              f"rowH 2 dòng = {sorted({r['rowH'] for r in two})}, "
              f"rowH 1 dòng = {sorted({r['rowH'] for r in rows if r['lines'] == 1})}")
    page.close()


def measure_pc(ctx):
    page = ctx.new_page()
    page.set_viewport_size({"width": PC[0], "height": PC[1]})
    errs = []
    page.on("pageerror", lambda e: errs.append(str(e)))
    print("\n===== PC 1920×1080 bất biến =====")
    for route in ("/portal", "/portal/order", "/portal/notification"):
        page.goto(BASE + route, wait_until="domcontentloaded")
        page.wait_for_timeout(1200)
        cs = page.evaluate("""() => {
            const el = document.querySelector('.content .content-wrapper');
            if (!el) return null;
            const c = getComputedStyle(el);
            return {padTop: c.paddingTop, padLeft: c.paddingLeft, marginTop: c.marginTop};
        }""")
        ovf = page.evaluate(OVERFLOW_JS)
        ok(cs is not None and cs["padTop"] == "24px", f"PC {route} content-wrapper padding-top 24px", str(cs))
        ok(cs is not None and cs["marginTop"] == "72px", f"PC {route} margin-top 72px", str(cs))
        ok(ovf == 0, f"PC {route} overflow ngang=0", f"ovf={ovf}")
    ok(not errs, "0 JS pageerror", str(errs[:3]))
    page.close()


def main():
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        ctx = browser.new_context(viewport={"width": MOB[0], "height": MOB[1]})
        login(ctx)
        measure_routes(ctx, ROUTES, "10 route BA")
        measure_routes(ctx, ROUTES_EXTRA, "3 route họ A ngoài danh sách BA")
        measure_header(ctx)
        measure_clamp(ctx)
        measure_pc(ctx)
        browser.close()
    print("\n================ TỔNG KẾT ================")
    if FAIL:
        print(f"FAIL = {len(FAIL)}")
        for f in FAIL:
            print("  -", f)
        sys.exit(1)
    print("FAIL = 0")


if __name__ == "__main__":
    main()
