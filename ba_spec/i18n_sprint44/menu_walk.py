#!/usr/bin/env python3
"""W5d — đi hết menu backend Wujia ở en_US: không menu nào 500 / OwlError / error dialog.

Sprint 44 đổi 636 nhãn sang tiếng Anh trên 81 file view. Rủi ro là gõ hỏng XML attr hoặc
lệch key selection => view không dựng được. Script mở TỪNG action gắn với menu của 15
module Wujia rồi soi console error + error dialog.

Chạy: python3 menu_walk.py     (server 8019)
Script TRẢ admin về lang ban đầu khi kết thúc.
"""
import sys
import xmlrpc.client

from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:8019"
DB, USER, PWD = "wujia_tea_19", "admin", "admin"
LANG = "en_US"

MODULES = [
    "wujia_core", "wujia_delivery", "wujia_fleet", "wujia_franchise", "wujia_sale",
    "wujia_portal_exam", "wujia_portal_notification", "wujia_portal_return",
    "wujia_portal_info_request", "wujia_portal_knowledge", "wujia_portal_support",
    "wujia_portal_order_window", "wujia_portal_debt", "wujia_portal_purchase_history",
    "wujia_portal_base",
]

common = xmlrpc.client.ServerProxy(f"{BASE}/xmlrpc/2/common")
uid = common.authenticate(DB, USER, PWD, {})
models = xmlrpc.client.ServerProxy(f"{BASE}/xmlrpc/2/object")


def rpc(model, method, *args, **kw):
    return models.execute_kw(DB, uid, PWD, model, method, list(args), kw)


ORIG_LANG = rpc("res.users", "read", [uid], fields=["lang"])[0]["lang"]

# Menu của module Wujia CÓ action (menu cha không action thì không có gì để dựng).
imd = rpc("ir.model.data", "search_read",
          [("model", "=", "ir.ui.menu"), ("module", "in", MODULES)],
          fields=["module", "name", "res_id"])
menu_ids = [r["res_id"] for r in imd]
menus = rpc("ir.ui.menu", "read", menu_ids, fields=["complete_name", "action"],
            context={"lang": LANG})
xmlid = {r["res_id"]: f"{r['module']}.{r['name']}" for r in imd}

targets = []
for m in menus:
    if not m["action"]:
        continue
    kind, _, act_id = m["action"].partition(",")
    targets.append((xmlid[m["id"]], m["complete_name"], kind, int(act_id)))
targets.sort(key=lambda t: t[1])

print(f"=== W5d — {len(targets)} menu có action (trên tổng {len(menus)} menu Wujia), "
      f"lang={LANG} ===")

rpc("res.users", "write", [uid], {"lang": LANG})
bad = 0
with sync_playwright() as pw:
    br = pw.chromium.launch()
    ctx = br.new_context(viewport={"width": 1600, "height": 1000})
    p = ctx.new_page()
    p.goto(f"{BASE}/web/login", wait_until="domcontentloaded")
    p.fill("input[name=login]", USER)
    p.fill("input[name=password]", PWD)
    p.press("input[name=password]", "Enter")
    try:
        p.wait_for_url(lambda u: "/web/login" not in u, timeout=25000)
    except Exception:
        pass
    p.wait_for_timeout(1500)

    errors = []
    p.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
    p.on("pageerror", lambda e: errors.append(str(e)))

    for xid, name, kind, act_id in targets:
        errors.clear()
        if kind != "ir.actions.act_window":
            # client action / report: vẫn mở được bằng cùng URL pattern
            pass
        resp = p.goto(f"{BASE}/odoo/action-{act_id}", wait_until="load")
        p.wait_for_timeout(2200)
        status = resp.status if resp else 0
        dialog = p.query_selector(".o_error_dialog, .o_dialog_error")
        hard = [e for e in errors
                if "OwlError" in e or "Missing" in e or "Traceback" in e
                or "500" in e or "lifecycle" in e]
        ok = status == 200 and not dialog and not hard
        bad += 0 if ok else 1
        print(f"  [{'OK  ' if ok else 'FAIL'}] {name[:60]:60s} {xid}")
        if not ok:
            print(f"         http={status} dialog={'YES' if dialog else 'no'} "
                  f"errors={hard[:2]}")
            p.screenshot(path=f"/tmp/w5d_fail_{xid.replace('.', '_')}.png")
    br.close()

rpc("res.users", "write", [uid], {"lang": ORIG_LANG})
print(f"\nFAIL = {bad} / {len(targets)}   (admin đã trả về {ORIG_LANG})")
sys.exit(1 if bad else 0)
