# C1 — Bảng đối chiếu acceptance (2026-08-15)

Nguồn: cột `Kết quả mong muốn` của WJ-FRANCHISE-001 (STT 85), WJ-FRANCHISE-002 (STT 89),
WJ-DEBT-006 (STT 103) trên tab `5. Issue List`.

Môi trường đo: **DB copy cô lập** `wujia_tea_c1` / `wujia_tea_c1m` (port 8061/8063, KHÔNG
đụng `wujia_tea_19`/8019). Công cụ: 15 unit test ORM (`wujia_account/tests/`), harness
Playwright trên form backend thật, harness `odoo-bin shell` trên dữ liệu seed công nợ.

## WJ-FRANCHISE-001

| Yêu cầu (GIVEN/WHEN/THEN) | Đo được | Pass |
|---|---|---|
| Chọn partner trên SO → tự điền `franchise_id` | Form backend: `[HCM-01] Cửa hàng 125 Điện Biên Phủ, Q.3, TP.HCM` | ✅ |
| … tự điền partner cửa hàng | `Wujia Tea — TP HCM Quận 1` | ✅ |
| … tự điền khu vực | `area_id` = C1 Area HCM (test ORM) | ✅ |
| Chọn partner trên picking → tự điền | test ORM: picking mới = HCM | ✅ |
| Chọn partner trên hoá đơn → tự điền | test ORM: invoice mới = HCM | ✅ |
| SO có franchise → picking/hoá đơn sinh ra kế thừa | test `confirm_allowed_after_fix`: picking = HCM | ✅ |
| Đổi partner phải tính lại | Form backend: HCM-01 → HN-01 | ✅ |
| Không giữ franchise cũ khi partner mới thuộc cửa hàng khác | Đo giá trị sau đổi: không còn HCM-01 | ✅ |
| Partner map nhiều cửa hàng → cảnh báo rõ, không đoán | `franchise_id` trống + cảnh báo liệt kê C1-M1, C1-M2 | ✅ |
| Partner không map → cảnh báo | **Im lặng** (quyết định chủ dự án 08-15) | ⚠️ LIMIT |

**9,5/10 ≈ 95% Pass** (dòng cuối ghi LIMIT tường minh, đã nêu lý do trong ledger).

## WJ-FRANCHISE-002

| Yêu cầu | Đo được | Pass |
|---|---|---|
| Chặn khi xác nhận SO (franchise trống) | Form backend hiện hộp chặn, SO ở `draft` | ✅ |
| Chặn khi franchise lệch mapping | test ORM `confirm_blocked_when_franchise_mismatch` | ✅ |
| Chặn khi validate picking | test ORM `picking_validate_blocked` | ✅ |
| Chặn khi post hoá đơn | test ORM `invoice_post_blocked_then_allowed` | ✅ |
| Thông báo nêu partner | `Partner 'Wujia Tea — Hà Nội Cầu Giấy'…` | ✅ |
| Thông báo nêu tình trạng mapping + việc cần sửa | `…thuộc cửa hàng '[HN-01]…' — hãy điền trường Cửa hàng nhượng quyền` | ✅ |
| Không sinh chứng từ kế tiếp với franchise trống | `picking_ids` rỗng sau khi bị chặn | ✅ |
| Hoạt động cả khi tạo/sửa qua UI, import, API | Chặn nằm ở `action_confirm`/`button_validate`/`action_post` — mọi đường xác nhận đều đi qua | ✅ |
| Sau khi franchise hợp lệ thì tiếp tục được | Form backend: trạng thái → `Sales Order` | ✅ |
| Hoá đơn nhà cung cấp không bị vạ lây | test ORM `vendor_bill_not_blocked` post OK | ✅ |

**10/10 = 100% Pass.**

## WJ-DEBT-006

| Yêu cầu | Đo được (dữ liệu thật, seed công nợ) | Pass |
|---|---|---|
| Credit note nháp tự có franchise của hoá đơn gốc | INV/2026/00002 → nháp mang `[HCM-01]` | ✅ |
| Giữ đúng franchise sau khi ghi sổ | `posted` + `[HCM-01]` | ✅ |
| Portal HCM-01 nhìn thấy credit note | có trong `search([('franchise_id','=',HCM-01)])` | ✅ |
| Portal cửa hàng khác không nhìn thấy | không có trong tập của HN-01 | ✅ |
| Không phải nhập lại store thủ công | 0 thao tác tay trong kịch bản đo | ✅ |
| Áp cho cả "Đảo" và "Đảo ngược và tạo hóa đơn" | cả 2 nhánh đều mang `[HCM-01]` | ✅ |

**6/6 = 100% Pass.**

## Hồi quy

| Hạng mục | Kết quả |
|---|---|
| Build `-u wujia_franchise,wujia_sale,wujia_delivery,wujia_account` | RC=0, 0 ERROR/Traceback |
| Test 7 module (`wujia_*` + portal debt/return/notification) | **106 test, 0 failed, 0 error** — chạy trên **cả** DB đã upgrade lẫn DB chạy migration |
| Migration backfill | 9 SO trống được điền, 14 SO điền partner cửa hàng; **S00025 lệch giữ nguyên**; 1 SO còn trống vì partner không map (đúng ý) |
| Portal 3 trang × 2 viewport (1920×1080, 391×844) | 6/6: status 200, overflow ngang 0, 0 lỗi JS |
| Backend form SO | 0 lỗi JS |
| Index `wujia_franchise_management.partner_id` | `wujia_franchise_management__partner_id_index` đã tạo |

## Ghi chú kỹ thuật cần nhớ

1. **Odoo KHÔNG tự backfill** khi field thường chuyển thành stored compute — đo thật: sau `-u`
   dữ liệu cũ y nguyên. Muốn sửa dữ liệu cũ phải viết post-migrate.
2. Harness Playwright: dropdown Many2one hiện **danh sách mặc định trước khi lọc xong** ⇒ click
   `li:first-child` bắt nhầm bản ghi (lần đo đầu chọn trúng "Administrator"). Phải chờ item
   chứa đúng chuỗi.
3. `pkill -f 'odoo[-]bin'` gộp chung dòng với lệnh chạy `odoo-bin` ⇒ shell tự giết mình
   (exit 144) — lỗi L8 lặp lại, tách lệnh ra.
4. `res.area` yêu cầu `code` khi tạo (fixture test).
5. `remaining` âm sau credit note là **WJ-DEBT-007** (cụm C2), không phải lỗi C1.
