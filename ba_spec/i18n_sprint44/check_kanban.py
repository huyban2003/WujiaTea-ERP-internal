#!/usr/bin/env python3
"""Verify 2 kanban backend render được, không còn OwlError 'Missing card template'."""
import sys
from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:8019"
USER, PWD = "admin", "admin"

TARGETS = [
    ("Support tickets (kanban mặc định)", "wujia_portal_support.action_support_ticket"),
    ("Knowledge articles (tab kanban)", "wujia_portal_knowledge.action_knowledge_article"),
]

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

    failed = False
    for label, xmlid in TARGETS:
        errors = []
        p.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
        p.on("pageerror", lambda e: errors.append(str(e)))
        p.goto(f"{BASE}/odoo/action-{xmlid}", wait_until="load")
        p.wait_for_timeout(2500)
        # ép sang kanban nếu list là view mặc định
        btn = p.query_selector("button.o_switch_view.o_kanban, .o_switch_view.o_kanban")
        if btn:
            btn.click()
            p.wait_for_timeout(2000)
        recs = len(p.query_selector_all(".o_kanban_record:not(.o_kanban_ghost)"))
        cols = len(p.query_selector_all(".o_kanban_group"))
        view = len(p.query_selector_all(".o_kanban_renderer"))
        dialog = p.query_selector(".modal-title, .o_error_dialog")
        owl = [e for e in errors if "Missing" in e or "OwlError" in e or "lifecycle" in e]
        ok = view and not owl and not dialog
        failed |= not ok
        print(f"[{'OK ' if ok else 'FAIL'}] {label}")
        print(f"       kanban_renderer={view} columns={cols} records={recs} "
              f"error_dialog={'YES' if dialog else 'no'} owl_errors={len(owl)}")
        for e in owl[:3]:
            print("       !!", e[:160])
        p.screenshot(path=f"/tmp/kanban_{xmlid.split('.')[-1]}.png")
        p.remove_listener("console", lambda m: None) if False else None

    br.close()
sys.exit(1 if failed else 0)
