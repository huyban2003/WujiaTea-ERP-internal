#!/usr/bin/env python3
"""W5c — smoke portal 391×844: portal phải Y NGUYÊN tiếng Việt sau sprint 44.

Sprint 44 chuyển nhãn backend sang tiếng Anh. Portal (chủ tiệm) KHÔNG được đổi. Ba chỗ
portal đọc thẳng selection của model đã được bịt bằng hằng nhãn VN pin trong controller
(W2a franchise status · W2b priority popup chuông · W2c request_type).

Script chạy 2 lượt: admin ở vi_VN và ở en_US. Lượt en_US mới là lượt QUAN TRỌNG —
W5e sẽ đổi hẳn admin sang en_US, portal vẫn phải ra tiếng Việt.

Kiểm mỗi trang:
  1. HTTP 200 (không trắng, không lỗi Odoo).
  2. Không rò token tiếng Anh của backend (danh sách LEAK dưới).
  3. Overflow ngang = 0 (scrollWidth <= clientWidth + 1).

Chạy: python3 portal_vi_smoke.py            (server 8019, admin/admin là owner 3 cửa hàng)
Script TRẢ admin về lang ban đầu khi kết thúc.
"""
import re
import sys
import xmlrpc.client

from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:8019"
DB, USER, PWD = "wujia_tea_19", "admin", "admin"
VW, VH = 391, 844

# Token backend tiếng Anh; nếu xuất hiện trong text portal nghĩa là seam bị hở.
# Dùng \b để không dính chữ trong URL/class (vd "active" trong class CSS đã bị loại
# vì chỉ soi innerText, không soi HTML).
# "Email" KHÔNG tính là rò: đó là nhãn tiếng Việt thật của loại thông tin (từ mượn),
# y hệt trước sprint. Xem REQUEST_TYPE_LABELS trong wujia_portal_info_request/controllers.
VI_OK = {"Email"}

# Nhãn VN đúng của W2b (PORTAL_PRIORITY_LABELS trong wujia_portal_notification/controllers).
WANT_PRIORITY_VI = {"Thông thường", "Quan trọng", "Cần làm"}

# TỒN TRƯỚC SPRINT (không phải hồi quy sprint 44), đã đối chiếu `git show HEAD`:
#   portal_franchise_information.xml:248-249 — badge thành viên hardcode "Active"/"Inactive"
#     (bản PC dòng 124 lại ghi "Đang hoạt động" -> lệch nhau sẵn).
# Cùng loại với portal_support.xml:430 ("Normal/Urgent"). Ghi danh sách tồn, ngoài scope.
PREEXISTING = {("/portal/franchise-information", "Active"),
               ("/portal/franchise-information", "Inactive")}

LEAK = ["Active", "Inactive", "Locked", "Expired", "Closed",   # W2a franchise status
        "Important", "Urgent", "Regular", "Action required",   # W2b priority
        "Address", "Phone number", "Bank information", "Owner name",  # W2c request_type
        "Representative", "Other",
        "Rejected", "Reject", "Archived", "Archive",    # W1
        "Draft", "Submitted", "Approved", "Cancelled"]

PAGES = [
    ("Trang chủ", "/portal", None),
    ("Lịch sử đặt hàng", "/portal/purchase-history", None),
    ("Đặt hàng", "/portal/order", None),
    ("Đổi trả / bù hàng", "/portal/return", None),
    ("Thông báo", "/portal/notification", "bell"),
    ("Công nợ", "/portal/debt", None),
    ("Thông tin cửa hàng", "/portal/franchise-information", None),   # seam W2a
    ("Hồ sơ cửa hàng", "/portal/franchises/1/profile", None),        # seam W2a
    ("Yêu cầu cập nhật", "/portal/info-request", None),              # seam W2c
]

common = xmlrpc.client.ServerProxy(f"{BASE}/xmlrpc/2/common")
uid = common.authenticate(DB, USER, PWD, {})
models = xmlrpc.client.ServerProxy(f"{BASE}/xmlrpc/2/object")


def rpc(model, method, *args, **kw):
    return models.execute_kw(DB, uid, PWD, model, method, list(args), kw)


ORIG_LANG = rpc("res.users", "read", [uid], fields=["lang"])[0]["lang"]
ACTIVE_FID = rpc("wujia.franchise.member", "search_read",
                 [("user_id", "=", uid)], fields=["franchise_id"],
                 limit=1)[0]["franchise_id"][0]

# Thêm 1 trang chi tiết yêu cầu cập nhật nếu DB có bản ghi (template đọc request_type_labels).
detail_ids = rpc("wujia.info.update.request", "search", [], limit=1)
if detail_ids:
    PAGES.append(("Chi tiết yêu cầu cập nhật", f"/portal/info-request/{detail_ids[0]}", None))
else:
    print("LƯU Ý: DB local không có bản ghi wujia.info.update.request "
          "-> bỏ qua trang chi tiết (seam W2c chỉ soi được ở trang danh sách).")


def login(ctx):
    p = ctx.new_page()
    p.goto(f"{BASE}/web/login", wait_until="domcontentloaded")
    p.fill("input[name=login]", USER)
    p.fill("input[name=password]", PWD)
    p.press("input[name=password]", "Enter")   # nút submit trùng nút Search -> Enter
    try:
        p.wait_for_url(lambda u: "/web/login" not in u, timeout=25000)
    except Exception:
        pass
    p.wait_for_timeout(1200)
    p.close()
    # BẪY: admin là owner của 3 cửa hàng và chưa chọn cửa hàng nào -> overlay
    # #wujiaStoreOverlay che TOÀN BỘ trang, innerText chỉ ra text của overlay và
    # mọi assert đều pass rỗng. Phải set sẵn cookie cửa hàng đang active.
    ctx.add_cookies([{
        "name": "wujia_active_franchise_id",   # ACTIVE_FRANCHISE_COOKIE
        "value": str(ACTIVE_FID),
        "url": BASE,
    }])


def scan(lang):
    rpc("res.users", "write", [uid], {"lang": lang})
    bad = 0
    with sync_playwright() as pw:
        br = pw.chromium.launch()
        ctx = br.new_context(viewport={"width": VW, "height": VH})
        login(ctx)
        p = ctx.new_page()
        for label, url, extra in PAGES:
            resp = p.goto(f"{BASE}{url}", wait_until="load")   # KHÔNG networkidle: bus.bus long-poll
            p.wait_for_timeout(2000)
            status = resp.status if resp else 0
            if extra == "bell":
                # seam W2b: nhãn mức độ nằm trong popup chuông, không có trên trang
                btn = p.query_selector(".wj-bell, #wj_bell, [data-wj-bell], .wj-header-bell")
                if btn:
                    btn.click()
                    p.wait_for_timeout(1800)
                else:
                    print("       (không tìm thấy nút chuông - soi text trang thay thế)")
            txt = p.inner_text("body")
            found = {w for w in LEAK if re.search(rf"\b{re.escape(w)}\b", txt)}
            known = sorted(w for w in found if (url, w) in PREEXISTING)
            leaks = sorted(found - set(known))
            ovf = p.evaluate(
                "() => Math.max(0, document.documentElement.scrollWidth "
                "- document.documentElement.clientWidth)")
            ok = status == 200 and not leaks and ovf <= 1
            bad += 0 if ok else 1
            print(f"  [{'OK  ' if ok else 'FAIL'}] {label:28s} {url:36s} "
                  f"http={status} overflow={ovf}px leak={leaks or '-'}"
                  + (f"  (tồn trước sprint: {known})" if known else ""))
            p.screenshot(path=f"/tmp/w5c_{lang}_{url.strip('/').replace('/', '_')}.png",
                         full_page=True)
        br.close()
    return bad


def scan_seams(lang):
    """2 seam KHÔNG soi được bằng innerText ở 391×844 — phải soi riêng.

    W2b: popup chuông chỉ dựng ở desktop ≥992px (header_bell_badge.js: mobile giữ bell
         là link thường) => phải mở ở 1440px, không phải 391px.
    W2c: <option> của <select> không nằm trong innerText của body => đọc thẳng DOM.
    """
    rpc("res.users", "write", [uid], {"lang": lang})
    bad = 0
    with sync_playwright() as pw:
        br = pw.chromium.launch()
        ctx = br.new_context(viewport={"width": 1440, "height": 900})
        login(ctx)
        p = ctx.new_page()

        # --- W2b: popup chuông ---
        p.goto(f"{BASE}/portal", wait_until="load")
        p.wait_for_timeout(2000)
        bell = p.query_selector("[data-wj-noti-bell]")
        popup_txt = ""
        if bell:
            bell.click()
            p.wait_for_timeout(2500)
            pop = p.query_selector("#wj-noti-popup")   # id thật, xem header_bell_badge.js
            popup_txt = pop.inner_text() if pop else ""
        en_leak = sorted({w for w in ("Important", "Urgent", "Regular", "Action required")
                          if re.search(rf"\b{re.escape(w)}\b", popup_txt)})
        ok = bool(bell) and not en_leak
        bad += 0 if ok else 1
        print(f"  [{'OK  ' if ok else 'FAIL'}] popup chuông (W2b, 1440px)  "
              f"bell={'có' if bell else 'KHÔNG'} leak={en_leak or '-'} "
              f"text={popup_txt[:90]!r}")
        p.screenshot(path=f"/tmp/w5c_{lang}_bell_popup.png")

        # --- W2b bis: endpoint trả nhãn cho FE ---
        recent = p.evaluate("""async () => {
            const r = await fetch('/portal/notification/recent', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({jsonrpc: '2.0', method: 'call', params: {}})
            });
            return await r.json();
        }""")
        # key là 'notifications' (không phải 'items') — xem controller portal.py:292
        labels = sorted({(i or {}).get("priority_label", "")
                         for i in ((recent.get("result") or {}).get("notifications") or [])})
        ok = bool(labels) and set(labels) <= set(WANT_PRIORITY_VI)
        bad += 0 if ok else 1
        print(f"  [{'OK  ' if ok else 'FAIL'}] /portal/notification/recent priority_label "
              f"= {labels or '(KHÔNG có bản ghi -> seam W2b chưa được soi)'}")

        # --- W2c: <option> loại thông tin ---
        for label, url in (("danh sách", "/portal/info-request"),
                           ("form tạo mới", "/portal/info-request/new")):
            p.goto(f"{BASE}{url}", wait_until="load")
            p.wait_for_timeout(1500)
            opts = p.eval_on_selector_all(
                "select[name=request_type] option, select#request_type option",
                "els => els.map(e => e.textContent.trim())")
            en_leak = sorted({o for o in opts
                              if o and o not in VI_OK
                              and re.match(r"^[A-Za-z][A-Za-z ]*$", o)})
            ok = bool(opts) and not en_leak
            bad += 0 if ok else 1
            print(f"  [{'OK  ' if ok else 'FAIL'}] select loại thông tin ({label}) "
                  f"= {opts or 'KHÔNG THẤY SELECT'} leak={en_leak or '-'}")
        br.close()
    return bad


total = 0
for lang in ("vi_VN", "en_US"):
    print(f"\n=== W5c — portal 391×844, admin lang = {lang} ===")
    total += scan(lang)
    print(f"--- seam soi riêng (1440px / DOM), lang = {lang} ---")
    total += scan_seams(lang)

rpc("res.users", "write", [uid], {"lang": ORIG_LANG})
print(f"\nFAIL = {total}   (admin đã trả về {ORIG_LANG})")
sys.exit(1 if total else 0)
