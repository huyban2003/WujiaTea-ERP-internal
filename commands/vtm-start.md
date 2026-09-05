---
description: Load VTM (Việt Thương Music) kickoff context — đọc compact summary, áp convention, hỏi task
---

You are starting a **VTM** (Việt Thương Music) session. Do these steps **in order**, no shortcut:

**Step 1.** Read the compact summary file directly:

```
Read tool → /home/huyban/odoo-dev/vietthuong/docs/vtm-compact-summary.md
```

It has 5 sections: §1 overview, §2 modules (3 nhóm A/B/C/D), §3 conventions, §4 gotchas, §5 credentials-pointer.

**Step 2.** Apply §3 (conventions) as the operating rules for **the entire conversation**, đặc biệt:

- **Server root:** `/home/huyban/odoo-dev/vietthuong/` (Odoo 16). Custom code ở [vietthuong/addons/](/home/huyban/odoo-dev/vietthuong/addons/).
- **Scope rule (BẮT BUỘC):**
  - ✅ Sửa được: `vtm_*` trong `vietthuong/addons/`.
  - ⚠️ Override-only: `beesuite_*` trong `vietthuong/` (vendor) — ưu tiên override trong `vtm_*` thay vì sửa thẳng.
  - ❌ KHÔNG đụng `beesuite_*` ở `beesuite2.0/`, `pgi/`, `draho/`, `gotco/`, `landed_cost_*/` — đó là deployment client khác, KHÔNG phải VTM.
- **Read-before-write:** đọc model + view hiện tại trước khi sửa, nhất là khu vực POS nặng (vtm_pos, vtm_pos_cod, vtm_pos_loyalty_discount).
- **Ask-don't-assume:** nghiệp vụ phức tạp (manual discount approval/OTP/ZNS, COD ship-later flow, VNPT e-invoice) → hỏi anh, đừng đoán.
- **POS → kế toán** là vùng "chạm cẩn thận" — mọi sửa đổi pos_order/account_move/stock_move phải verify ledger khớp.
- **Commit:** Tiếng Việt, ngắn gọn, đủ ý.
- **Credentials:** không bao giờ ghi vào markdown — lưu agentmemory `type="secret"` với concepts `["vtm","credentials",<service>]`.

**Step 3.** Echo cho user 6 dòng status snapshot (rút từ §1 + §2):

```
✓ VTM session ready — Việt Thương Music, Odoo 16, production ~6 tháng / ~70 user.
  Scope: 40 module vtm_* installed + 76 beesuite_* installed + dashboard ks_dn_*/Zalo/VoIP.
  5 module nắm KỸ: vtm_pos, vtm_pos_cod, vtm_accounting, beesuite_account, beesuite_account_einvoice_vnpt.
  Hot spot: vtm_pos_loyalty_discount (manual discount + OTP + ZNS) & POS → Kế toán.
  DB tham chiếu: vtm_1205 (Postgres odoo16/1).
  Sắp build: vtm_maintenance_portal (portal khách + ZNS) — chưa installed.
```

Số trên là từ summary tại thời điểm 2026-05-17. Nếu summary đã update → echo theo số mới (đọc từ §2).

**Step 3b.** Nếu summary §4 (gotchas) hoặc §5 có ghi WIP task → echo ngắn gọn cho user biết. Không hardcode WIP ở đây — đọc từ file summary (Step 1).

**Step 4.** Optionally call `memory_smart_search` (agentmemory MCP) nếu user nhắc đến topic cần ad-hoc recall (vd bug session trước, credential VNPT, quirk module cụ thể). Skip nếu task fresh.

**Step 5.** Hỏi user: **"Task gì hôm nay?"** — đợi anh trả lời trước khi làm gì khác.

---

**Why đọc file trực tiếp thay vì gọi agentmemory recall:**

Tool agentmemory MCP trả `mode: compact` (titles only) by default, không reliably fetch body trong v0.9.16. Đọc markdown deterministic — luôn được full content. agentmemory vẫn dùng để **save/search ad-hoc insight** trong session (vd `memory_save` lưu decision, session sau `memory_smart_search` ít nhất thấy title).

**Khi scope đổi (thêm/bớt beesuite_*, đổi key module, …):**
- Edit thẳng [vtm-compact-summary.md](/home/huyban/odoo-dev/vietthuong/docs/vtm-compact-summary.md) §2 hoặc §4.
- POST lại section đó lên agentmemory (concept `["vtm","vietthuong","<section-slug>"]`).
- Hoặc re-run prompt build /vtm-start gốc.

**Nếu summary file mất** → fallback đọc thẳng [vietthuong/addons/](/home/huyban/odoo-dev/vietthuong/addons/) + query DB `vtm_1205` `SELECT name FROM ir_module_module WHERE state='installed'` → re-build context.
