---
description: Load GNF kickoff context — POS + ecommerce (Haravan/Grab), Odoo 16, focus ECOM scope
---

You are starting a **GNF** session. Do these steps **in order**, no shortcut:

**Step 1.** Read the compact summary file directly:
  Read tool → /home/huyban/odoo-dev/gkitchen/docs/gnf-compact-summary.md

It has 5 sections: §1 overview, §2 modules (nhóm A–H + NEGATIVE LIST + ECOM docs), §3 conventions, §4 gotchas, §5 credentials-pointer.

**Step 2.** Apply §3 (conventions) as operating rules for the entire session. Key rules:
- Server root: /home/huyban/odoo-dev/gkitchen/ (Odoo 16). Custom code in gkitchen/addons/.
- Scope: ✅ gkitchen_* | ⚠️ beesuite_* in gkitchen/ (override-only) | ❌ NEVER touch vietthuong/, draho/, odoo16/, pgi/, gotco/, landed_cost_*/, wujia_tea_*/
- Focus: ecommerce scope (Nhóm B: Haravan + beesuite_sale_ecommerce; Nhóm C: Grab). Don't proactively touch POS/purchase/kho unless user asks explicitly.
- Commit in English. Read-before-write. Ask-don't-assume (code GNF has inconsistent patterns — always read before writing).

**Step 3.** Echo a 6-line status snapshot:
```
Project : GNF — POS bán lẻ + ecommerce (Haravan, GrabMart, GrabExpress), Odoo 16
Status  : POS golive ✓  |  Ecommerce đang hoàn thiện (chưa golive)
DB      : gnf_staging (localhost, odoo16/1)  |  2 instances: B1 prod + B2 ecom
Focus   : Nhóm B ECOM (beesuite_ecom_haravan_api, beesuite_sale_ecommerce, gkitchen_sap_product)
Caution : odoo_data_sync + gkitchen_sale_allocation chưa cài — B1↔B2 sync chưa active
Docs    : gkitchen/docs/ có 4 file ECOM binary — đọc thủ công nếu cần nghiệp vụ chi tiết
```

**Step 4.** Optionally call memory_smart_search if user mentions a past topic (e.g. "hôm qua mình làm Haravan sync"). Skip if fresh task.

**Step 5.** Ask user: **"Task gì hôm nay?"** — wait for the answer before doing anything else.

---

**Fallback** (nếu compact summary file bị mất hoặc không đọc được):
1. List addons: `ls /home/huyban/odoo-dev/gkitchen/addons/`
2. Query DB installed modules:
   ```
   PGPASSWORD=1 psql -h localhost -U odoo16 -d gnf_staging -At \
     -c "SELECT name FROM ir_module_module WHERE state='installed' ORDER BY name"
   ```
3. Notify user: "gnf-compact-summary.md bị mất — đang rebuild từ DB. Sau khi rebuild xong cần lưu lại file."
