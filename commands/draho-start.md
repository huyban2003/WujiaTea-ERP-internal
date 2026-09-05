---
description: Load Draho kickoff context — focus kế toán Việt Nam (l10n_vn + beesuite_account + draho_account), TT99 định hướng
---

You are starting a **Draho** session. Do these steps **in order**, no shortcut:

**Step 1.** Read the compact summary file directly:

```
Read tool → /home/huyban/odoo-dev/draho/docs/draho-compact-summary.md
```

It has 5 sections: §1 overview, §2 modules (11 nhóm A–K), §3 conventions, §4 gotchas, §5 credentials-pointer.

**Step 2.** Apply §3 (conventions) as the operating rules for **the entire conversation**, đặc biệt 3 quy tắc hard-coded:

1. **Module guardrail (TUYỆT ĐỐI):** chỉ tham chiếu module có trong §2 whitelist. KHÔNG suy đoán module ngoài list. Cụ thể:
   - HĐĐT: CHỈ VNPT (`beesuite_account_einvoice_vnpt`). KHÔNG nói "Viettel", "S-Invoice", "MISA".
   - KHÔNG nói "báo cáo tuổi nợ tự động" → `beesuite_aged_partner_balance` chưa cài.
   - KHÔNG nói "tờ khai hải quan tự động" → Foreign Trade module chưa cài.
   - KHÔNG nói "Cash Book / Bank Book chuyên dụng" → `om_account_daily_reports` chưa cài.
   - KHÔNG nói "spot rate x_rate trên invoice" → `z_invoice_customize` chưa cài.
   - Tạm ứng: CHỈ `draho_account_advance`. `z_account_advance` deprecated, KHÔNG nhắc.

2. **Scope edit:**
   - ✅ Sửa được: `draho_*`, `z_*` trong [draho/addons/](/home/huyban/odoo-dev/draho/addons/).
   - ⚠️ Override-only (KHÔNG sửa upstream code): `beesuite_*` trong [draho/accounting/](/home/huyban/odoo-dev/draho/accounting/), `om_*`, `viin_*`, `to_*`, `mrp_account*`. Ưu tiên override trong `draho_*` thay vì sửa thẳng vendor.
   - ❌ Tuyệt đối không đụng: VTM (vietthuong), WujiaTea, PGI, gotco, vietthanh, các dự án khác trên cùng máy.

3. **TT99 mindset:** mọi mô tả báo cáo tài chính (BCTC) dùng tinh thần **Thông tư 99/2025/TT-BTC** — đây là định hướng cuối cùng của Draho. Hiện tại đang chạy template **TT200 tạm thời** (`beesuite_report_template_vas200` + `beesuite_account_financial_data`). Khi mention BCTC luôn flag: "Hiện đang chạy mẫu TT200, sẽ thay khi cài `beesuite_l10n_vn_tt99` + `beesuite_account_financial_data_tt99`".

Ngoài ra:
- **Read-before-write:** đọc model + view hiện tại trước khi sửa, nhất là vùng `draho_account` (Fee Code) và `draho_account_advance` (workflow tạm ứng).
- **Ask-don't-assume:** nghiệp vụ phức tạp (kết chuyển cuối kỳ, điều chỉnh giá vốn / landed cost hồi tố, phê duyệt đa cấp, HĐĐT VNPT điều chỉnh/thay thế) → hỏi user, đừng đoán.
- **Commit:** Tiếng Việt, ngắn gọn, đủ ý.
- **Credentials:** không bao giờ ghi vào markdown — lưu agentmemory `type="secret"` với concepts `["draho","credentials",<service>]`.

**Step 3.** Echo cho user 6 dòng status snapshot (rút từ §1 + §2):

```
✓ Draho session ready — DB draho_1305 (Odoo 16 CE).
  Focus: Kế toán VN — l10n_vn + beesuite_account* + draho_account*.
  5 trụ cột: Fee Code | Tạm ứng (draho_account_advance) | HĐĐT VNPT | Báo cáo VAS (TT99-ready) | Budget + TSCĐ.
  Kế toán shared: beesuite_account_einvoice_vnpt, beesuite_account_vas_report, beesuite_account_regularization. COGS real-time chuẩn Odoo perpetual AVCO (module beesuite_stock_account_cogs cài nhưng KHÔNG dùng nhánh periodical — xem §4.6 gotchas).
  HDSD: 10 file Word — draho/docs/DRH - HDSD - ACCOUNTING/ (BA đang điền dần).
  Bộ prompt HDSD: draho/docs/hdsd-prompts/ — 00-master + 01..10 + README.
```

Nếu số/module trong summary đã update → echo theo số mới (đọc từ §1 + §2), không bịa.

**Step 4.** Optionally call `memory_smart_search` (agentmemory MCP) nếu user nhắc đến topic cần ad-hoc recall (vd bug session trước, quirk module Fee Code, decision về workflow tạm ứng). Skip nếu task fresh.

**Step 5.** Hỏi user 2 nhánh rõ ràng:

```
Hôm nay làm gì?

(A) Dev task — mô tả feature/bug bạn muốn implement.
(B) Soạn HDSD — chọn số file:
    5.0  Master Data
    5.1  Kế Toán Bán Hàng
    5.2  Kế Toán Mua Hàng
    5.3  Kế Toán Kho
    5.4  Kế Toán Tổng Hợp
    5.6a Ngân sách & TK phân tích   (TOC chưa cập nhật — prompt sẽ đề xuất TOC chờ BA confirm)
    5.6b Tài Sản
    5.7  Tạm ứng & Quyết toán       (TOC chưa cập nhật — prompt sẽ đề xuất TOC chờ BA confirm)
    5.8  Báo Cáo VAS                (mục Tuổi nợ cần BA xác nhận scope — chưa có module tự động)
    5.9  Báo Cáo Quản Trị & BCTC   (TOC chưa cập nhật — prompt sẽ đề xuất TOC chờ BA confirm)
```

Nếu user chọn (B) + số file → instruct ngay:
> "Mở `draho/docs/hdsd-prompts/00-master-context.md`, paste toàn bộ vào chat. Sau khi tôi confirm, paste tiếp `0X-...md` tương ứng."

Đợi user trả lời trước khi làm gì khác.

---

**Why đọc file trực tiếp thay vì gọi agentmemory recall:**

Tool agentmemory MCP trả `mode: compact` (titles only) by default, không reliably fetch body trong v0.9.16. Đọc markdown deterministic — luôn được full content. agentmemory vẫn dùng để **save/search ad-hoc insight** trong session (vd `memory_save` lưu decision, session sau `memory_smart_search` ít nhất thấy title).

**Khi scope đổi (thêm/bớt module accounting, đổi key workflow, TT99 module được cài, …):**
- Edit thẳng [draho-compact-summary.md](/home/huyban/odoo-dev/draho/docs/draho-compact-summary.md) §2 hoặc §4.
- Re-verify whitelist với DB: `PGPASSWORD=1 psql -h localhost -U odoo16 -d draho_1305 -At -c "SELECT name FROM ir_module_module WHERE state='installed' ORDER BY name"`.
- Mọi module mention trong summary phải nằm trong list này.

**Nếu summary file mất** → fallback:
1. `ls /home/huyban/odoo-dev/draho/addons/` → biết custom addons.
2. `ls /home/huyban/odoo-dev/draho/accounting/` → biết Beesuite accounting.
3. Query DB trên → re-build context, đề xuất user tạo lại summary.
