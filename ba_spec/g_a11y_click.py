"""Bấm THẬT vào rìa hit-area mới (không phải giữa nút) để chắc nút vẫn ăn."""
from playwright.sync_api import sync_playwright
BASE="http://127.0.0.1:8033"; FAIL=[]
def ok(c,l,d=""):
    print(("  OK   " if c else "  FAIL ")+l+("  "+d if d else ""));  FAIL.append(l) if not c else None
with sync_playwright() as pw:
    br=pw.chromium.launch(); ctx=br.new_context(); p=ctx.new_page()
    p.goto(f"{BASE}/web/login"); p.fill("input[name=login]","em.hcm"); p.fill("input[name=password]","demo123")
    p.press("input[name=password]","Enter"); p.wait_for_timeout(2500)
    p.set_viewport_size({"width":391,"height":844})

    # --- giỏ hàng: bấm rìa TRÁI của nút − và rìa PHẢI của nút + ---
    p.goto(BASE+"/portal/order/cart", wait_until="load"); p.wait_for_timeout(1500)
    q0=p.inner_text(".wujia-mcart-step-qty")
    b=p.query_selector(".wujia-mcart-step-plus").bounding_box()
    p.mouse.click(b["x"]+b["width"]+4, b["y"]+b["height"]/2)   # 4px NGOÀI mép phải nút
    p.wait_for_timeout(2000)
    q1=p.inner_text(".wujia-mcart-step-qty")
    ok(int(q1)==int(q0)+1, "bấm 4px ngoài mép PHẢI nút + → tăng SL", f"{q0} -> {q1}")
    b=p.query_selector(".wujia-mcart-step-minus").bounding_box()
    p.mouse.click(b["x"]-4, b["y"]+b["height"]/2)              # 4px NGOÀI mép trái nút
    p.wait_for_timeout(2000)
    q2=p.inner_text(".wujia-mcart-step-qty")
    ok(int(q2)==int(q1)-1, "bấm 4px ngoài mép TRÁI nút − → giảm SL", f"{q1} -> {q2}")
    # bấm ngay giữa 2 nút (chỗ 2 hit-area giáp nhau) không được nhảy 2 đơn vị
    bm=p.query_selector(".wujia-mcart-step-minus").bounding_box()
    bp=p.query_selector(".wujia-mcart-step-plus").bounding_box()
    mid=(bm["x"]+bm["width"]+bp["x"])/2
    who=p.evaluate("(a)=>{const e=document.elementFromPoint(a[0],a[1]); return e?e.className:'null'}",
                   [mid, bm["y"]+bm["height"]/2])
    ok("mstep" not in who or "step" in who, "điểm giữa − và + không mơ hồ", who)

    # --- danh sách: bấm rìa DƯỚI nút Thêm (hit-area cao 44 > nút 40) ---
    p.goto(BASE+"/portal/order", wait_until="load"); p.wait_for_timeout(1500)
    add=p.query_selector(".wujia-morder-add-btn")
    b=add.bounding_box()
    before=p.inner_text(".wujia-morder-floatbar") if p.query_selector(".wujia-morder-floatbar") else ""
    p.mouse.click(b["x"]+b["width"]/2, b["y"]+b["height"]+1)   # 1px DƯỚI mép nút
    p.wait_for_timeout(2500)
    after=p.inner_text(".wujia-morder-floatbar") if p.query_selector(".wujia-morder-floatbar") else ""
    ok(before!=after, "bấm 1px dưới mép nút Thêm → giỏ đổi", f"{before[:30]!r} -> {after[:30]!r}")
    br.close()
print(f"\nTỔNG: {len(FAIL)} FAIL")
