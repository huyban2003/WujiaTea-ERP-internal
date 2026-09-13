# Nghiệm thu E2b — StatusBadge `CMP-SB-001` (`UI-STATUSBADGE-001`, STT 128)

Ngày 13/09/2026 · DB đo `wujia_tea_e2b` (clone `wujia_tea_mt4`, **có** cài
`wujia_portal_inspection` + `wujia_franchise_inspection` giống UAT) · cổng 8096 ·
đối chứng `wujia_tea_e2bbase` (worktree mã `a0ff75f`, cổng 8098) · login `anh.owner`.
E2a dựng component; **E2b làm nốt phần còn lại và đóng issue tới `Ready for Retest`**.

## FIX
1. Migrate **37 call site** badge trạng thái còn lại sang `.wj-status-badge` ở 6 module:
   Thông báo (6) · Thi (11) · Công nợ (8) · Trả hàng (8) · Yêu cầu cập nhật (2) · Hỗ trợ (2).
   Kiểm kê cấu trúc (`lxml`): họ cũ **75 → 38**, component **37 → 74**.
2. Mọi map nhãn→class trong controller/model kéo về **một nguồn**
   (`STATUS_VARIANT_BY_LABEL` + `status_badge_for()`): `STATE_LABELS` của Hỗ trợ ·
   Yêu cầu cập nhật · Trả hàng, `COMPENSATION_STATUS_LABELS`, `M_REG_BADGE`,
   `PC_REG_STATES`, `PC_PUBLISH_STATES`, `STATE_BADGE`, `INVOICE_BADGE`.
   Bổ sung ~40 nhãn mới vào bảng bậc BA (đọc/chưa đọc, công bố kết quả, tiến độ bù,
   tình trạng hoá đơn, phản hồi yêu cầu cập nhật).
3. **Gỡ override ép badge nhỏ** (chốt của chủ dự án 13/09 — "theo BA, 28px"):
   - Thi: xoá 5 rule (`wujia-mexam-*-badge` 11,5px/r999; `.wj-pc-badge` min-width 118/12/700;
     `hbadge` 176 · `pbadge` 128 · `rbadge` 88) → còn **một** rule vị trí
     `.wj-exam-pc-page-header__actions .wj-status-badge { margin-top: 8px }`.
   - Công nợ: xoá hẳn hai họ `wj-debt-badge` / `wj-debt-pc-badge`; rule ngữ cảnh
     `.wj-debt-summary__head` chỉ còn định vị.
   - Thông báo: hai override ở `portal_notification.css:104` và `:429` **giữ nguyên** —
     sau migrate chúng chỉ còn chạm chip ưu tiên / "Có file" (BA loại khỏi StatusBadge).
     Gỡ là đổi thứ BA không yêu cầu đổi.
4. Hồi quy bắt được khi kiểm chéo (đúng họ lỗi `.wujia-maccount-badgerow` của E2a):
   `.wujia-mnoti-row-tags` là flex `align-items: normal` ⇒ badge 28px kéo chip
   "Quan trọng" 23,39 → 28px. Thêm `align-items: center` cho 3 hàng tag của Thông báo.
5. Ảnh chụp bắt được cái số đo không thấy: ô "Trạng thái đăng ký" của bảng Thi PC có
   `text-overflow: ellipsis`, badge vừa khít nhưng **text node trắng phía sau vẽ ra dấu "…"**.
   Thêm `td.wj-exam-pc-td--badge { text-overflow: clip }` (badge trước đây rộng 118px
   thực ra bị cắt mất 8px mà không ai thấy — nay rộng 102px, nằm trọn trong ô).

## Bằng chứng đo

| Đích | Ngưỡng | Đo được |
|---|---|---|
| Mẫu badge component | > 0 | **321** (12 route × 6 khổ: 1440/1024/992/991/390/360) + **51** ở route chi tiết |
| Cao · min-width · padding · radius | 28 · ≥84 · `0px 14px` · 14 | **321/321 đúng** |
| Font · line-height · nowrap · số dòng | 13/600 · 1 · nowrap · 1 rect | **321/321 đúng** |
| Contrast render thực | ≥ AA 4.5 | **321/321 đạt · 0 vi phạm** |
| Tràn ngang / ellipsis trên badge | 0 | **0** |
| SB-3 — 5 họ BA loại đổi computed | 0 ô | **0** |
| Ô bảng cắt badge (quét 7 route PC) | 0 | **0** (trước khi sửa: 1 — bảng Thi) |
| `wj_measure` 13 route × 5 khổ | 0 lỗi JS · 0 redirect · 0 mất record | **đạt** (0/0/0, redirect 5 = 5 như đối chứng) |
| Chiều cao trang đổi | chỉ do badge cao lên | **4 ô**: notification 390 +5 · 360 +4 · return 390 +25 · 360 +86 |
| Ảnh trước/sau `/portal/notification`, `/portal/exam` @1440 + @390 | bố cục không vỡ | **trùng khít** |
| Kiểm kê `lxml` call site họ cũ | chỉ còn Khảo sát + họ BA loại | **38** = 9 Khảo sát (defer) + 29 BA loại |
| Test 8 module bị đụng | 0 đỏ mới so đối chứng | **0 failed / 457** (đối chứng **0 failed / 450**, chênh = 7 test mới) |
| Test guard E2b mới | 7 | **7/7 xanh** (cùng 9 test E2a: 16/16) |
| Mutation (phá 1 chỗ → đỏ đúng 1 test) | 9/9 | **9/9**, mỗi mutation đúng 1 test |

Hai test cũ phải sửa theo (không phải lỗi mới): `test_d3_card_header` neo
`.wj-debt-summary__head .wj-debt-badge` và `test_return_card_d6` neo `wujia-badge` —
cả hai đổi sang `.wj-status-badge`, đúng vì call site đã về component.

## Đối chiếu ô `Kết quả mong muốn` của STT 128

| Yêu cầu BA | Đo được | Kết |
|---|---|---|
| Toàn Portal dùng MỘT StatusBadge component cho PC/mobile | 74 call site component; 0 StatusBadge thật nằm ngoài component (38 họ cũ còn lại = Khảo sát defer + họ BA loại) | **Pass** |
| height 28 · min-width 84 · padding `0 14px` · radius 14 · font 13/600 · rộng theo nội dung | 321/321 đúng ở 12 route × 6 khổ (rộng 84→176 theo chữ) | **Pass** |
| Mapping màu 7 cặp hex | **7/7 NỀN đúng hex BA**; chữ: 2/7 giữ nguyên, 5/7 làm đậm tối thiểu cùng tông để đạt WCAG AA mà chính BA đòi (E2a, Dev tự quyết) | **Partial** |
| Không overflow/clipping tại 1440 · 1024 · 992/991 · 390 · 360 | 0 tràn ngang, 0 badge xuống dòng, 0 ô bảng cắt badge (sửa 1 chỗ ở bảng Thi) | **Pass** |
| Text VI/EN đọc đầy đủ | VI 321 mẫu · EN 61 mẫu (4 route × 2 khổ) — 0 vi phạm cả hai | **Pass** |
| Không ảnh hưởng Role/Count/Filter/Category/Alert badge hay nghiệp vụ | SB-3 = 0 ô đổi; 457 test 0 đỏ | **Pass** |

⇒ **5,5/6 ≈ 92% Pass** (ngưỡng §13 là ≥90%). Ô Partial là mâu thuẫn trong chính spec BA,
đã nêu ở LIMIT và xin BA chốt lúc retest.

## IMPACT (báo BA lúc retest)
- Badge trạng thái trong hàng thông báo và popup PC nay **28px/13px** thay vì chip 11px ⇒
  trang thông báo mobile cao thêm 4–5px. Đây là hệ quả trực tiếp của chốt "theo BA".
- `/portal/return` mobile cao thêm 25px (390) / 86px (360): mỗi card có thêm 1 badge
  tiến độ bù cao 28px.
- Badge Thi PC hết `min-width 118` → 84–102px, cột "Trạng thái đăng ký" nhìn hẹp hơn.
- Badge công nợ đổi dáng (hai họ `wj-debt-*badge` biến mất), màu theo bậc BA:
  "Chưa thanh toán" pending · "Thanh toán một phần" processing · "Có quá hạn" danger.
- Nhãn cạnh nhau có thể trùng màu khi BA xếp cùng bậc ("Đã lên đơn bù" và
  "Đang bù một phần" đều processing) — phân biệt bằng chữ, đúng luật USAGE của BA.

## RETEST (đề nghị BA)
1. `/portal/notification` PC + mobile — "Chưa đọc" xanh dương, "Đã đọc" xám,
   "Đã hết hiệu lực" xám; chip ưu tiên và "Có file" **không đổi**.
2. `/portal/exam` PC 1440 + mobile — badge đăng ký / công bố kết quả cùng dáng với
   các màn khác; bảng PC không cắt chữ.
3. `/portal/debt`, `/portal/return`, `/portal/info-request`, `/portal/support` —
   cùng trạng thái = cùng màu, cùng dáng.
4. Badge vai trò · chip khu vực · badge đếm chưa đọc · Category kiến thức ·
   phương án xử lý trả hàng — **không được đổi**.
5. Xác nhận hàng thông báo cao thêm 4–5px và trang trả hàng mobile cao thêm là chấp nhận được.

## LIMIT
1. `wujia_portal_inspection` 9 call site: **defer** theo luật 08/09 (module khảo sát của
   anh Thái, cấm đụng). Vì thế `.wj-pc-badge` vẫn không xoá được.
2. 29 call site họ cũ còn lại là **BA loại khỏi StatusBadge** (Role · Count · FilterChip ·
   Category · Alert · priority · loại thông báo · đính kèm · phương án xử lý) — giữ nguyên
   là ĐÚNG spec, không phải việc chưa làm.
3. Chưa deploy UAT (chủ dự án chạy tay) ⇒ BA retest sau khi deploy.
4. Ô `Kết quả mong muốn` đòi đọc đủ **VI/EN/ZH**; hệ thống hiện chỉ bật `vi_VN` và `en_US`,
   **không có gói tiếng Trung** ⇒ chỉ đo được hai thứ tiếng. Badge `white-space: nowrap` +
   `min-width` co theo nội dung nên chuỗi ZH (ngắn hơn VI) không có rủi ro tràn, nhưng đây
   là suy luận chứ không phải số đo — xin BA bật `zh_CN` nếu muốn nghiệm thu đủ ba thứ tiếng.
5. Màu chữ 5/7 variant lệch hex BA (làm đậm cùng tông) — xem FIX 5 của `e2a-acceptance-matrix.md`.

## Odoo Fit
Không thêm model/field; không override core. Hằng + helper ở
`wujia_portal_base/controllers/utils.py`, template chỉ đọc `t-attf-class`, dáng ở tầng
dùng chung `wujia_portal_layout`. Bump `__manifest__.py` 7 module: base `19.0.7.14.0` ·
notification `19.0.2.12.0` · exam `19.0.5.14.0` · return `19.0.3.2.0` · debt `19.0.4.7.0` ·
info_request `19.0.1.9.0` · support `19.0.3.20.0`. Không bump `?v=` vì E2b chỉ đụng CSS
đóng gói theo module (bundle tự băm lại), `_variables.css` / `_components.css` không đổi.

## Build / Deploy
Chưa deploy. Khi deploy UAT (gộp cả E2a vì E2a chưa lên):

```
-u wujia_portal_layout,wujia_portal_base,wujia_portal_purchase_history,wujia_portal_delivery,
   wujia_portal_sale,wujia_portal_support,wujia_portal_notification,wujia_portal_exam,
   wujia_portal_return,wujia_portal_debt,wujia_portal_info_request
```

(**-u**, không `-i`), restart, hard-refresh. `wujia_portal_knowledge` không nằm trong lệnh:
8 call site của nó đều là CategoryBadge/AlertBadge — BA loại, không sửa gì.

## Bẫy môi trường ghi lại
Clone DB bằng `createdb -T` **không** chép filestore ⇒ hàng `ir_attachment` của bundle JS
trỏ vào file không tồn tại, `/web/assets/…frontend.min.js` trả 500, toàn bộ JS frontend
chết im lặng (ApexCharts không vẽ, `pageerror` vẫn 0). Biểu hiện: `/portal/reports/orders`
lệch chiều cao giữa hai mốc dù không đụng file nào của báo cáo. Xử lý:
`delete from ir_attachment where url like '/web/assets/%'` rồi để Odoo sinh lại.
