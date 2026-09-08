# D5h — bảng nghiệm thu DataList lượt 7, lượt KHÉP cụm D5 (Thi ×4 + kề cận ×3)

`CMP-DL-001` · issue `UI-DATALIST-001` (STT 126) · ngày **08/09/2026** · DB đo `wujia_tea_d5g`,
cổng 8077 (KHÔNG đụng `wujia_tea_19` / 8019).

Số đo: `docs/d5h-before.json` · `docs/d5h-after.json` · `docs/d5h-rule-after.json` ·
`docs/d5h-hover.json`. Bộ đo `scripts/qa/wj_datalist.py` +`wj_measure.py`,
đăng nhập `anh.owner` / `wujia@test123`, **15 route × 6 khổ** (1440 · 1024 · 992 · 991 · 390 · 360).

> ⚠️ **Bộ số của cụm D5 vẫn là `provisional`.** BA chưa trả lời 6 câu treo trong
> `docs/ba-questions-d5-datalist.md` — đọc thẳng tab `5. Issue List` dòng 119 lúc bắt đầu lượt:
> `Ready for Dev` · 25/08/2026 · cột *Ghi chú* rỗng. Vì vậy lượt này **giữ nguyên bộ số D5d–D5g**,
> không sửa gộp, và chuyển issue sang `Ready for Retest` với tư cách **đề xuất của Dev** —
> Dev không tự đóng `Done`.

## 0. Phạm vi lượt này đã ĐỔI so với kế hoạch gốc — hai quyết định của chủ dự án

| | Kế hoạch gốc D5h | Quyết định 08/09/2026 |
|---|---|---|
| 2 call site Khảo sát (`wujia_portal_inspection`) | migrate | **DEFER** — module merge từ nhánh `thai`, lối code khác hẳn portal. Luật thường trực đã ghi vào skill `wujia-start`. |
| 3 call site kề cận ngoài 10 route BA | không có trong kế hoạch | **LÀM** — `/portal/info-request` (bảng PC) + `/portal/franchise-information` (bảng PC thành viên + list mobile) |

⇒ **7 call site** thực làm. Tiến độ cụm: **29/31 trong phạm vi BA** (2 defer có chủ đích) ·
**32/34** kể cả kề cận.

## 1. Bốn việc kiểm chứng TRƯỚC khi code

1. **BA đã trả lời chưa** — chưa (dòng 119 như trên) ⇒ số giữ `provisional`.
2. **Môi trường khớp code** — 24/24 module `latest_version` == `__manifest__.py`; `HEAD = a7b24a2`
   hơn D5g (`2e23eb7`) đúng 1 commit **docs-only** ⇒ không dính bẫy D5g #4.
3. **Mốc "trước" khớp D5g** — giao 12 route chung với `docs/d5g-after.json`: **2064/2064 ô, 0 lệch**.
   (Phép so ngây thơ ban đầu báo 378 ô lệch chỉ vì `d5g-after.json` có 12 route còn lượt đo
   mặc định 10 — phải giao tập route rồi mới so.)
4. **Dữ liệu đủ để guard nói được điều gì** — chưa: 1 khoá thi · 3 phiếu đăng ký (1 trang, không
   thử được guard pager) · 0 yêu cầu cập nhật thông tin ⇒ phải seed trước (mục 5).

## 2. Đã làm

| # | Call site | File | Việc |
|---|---|---|---|
| 1 | Bảng PC lịch sử đăng ký thi | `wujia_portal_exam/views/portal_exam.xml` | bọc `wj_data_list` variant `table` · 8 `th scope="col"` |
| 2 | Pager PC thi | nt | vào `dl_pager` · guard `pc_pager['pages'] &gt; 1` (**key là `pages`**, không phải `page_count`) |
| 3 | Danh sách phiếu thi mobile `wujia-mexam-card` | nt | variant `detail-card` |
| 4 | Danh sách khoá thi `wujia-mexam-course` (`/portal/exam/register`) | nt | variant `detail-card` |
| 5 | Danh sách người dự thi `wujia-mexam-rrow` (`/portal/exam/registration/N`) | nt | variant `compact-row` |
| 6 | Bảng PC `/portal/info-request` | `wujia_portal_info_request/views/portal_info_request_list.xml` | variant `table` · 8 `th scope` · bỏ `.table-responsive` (viewport của component đã `overflow-x:auto`) |
| 7 | `/portal/franchise-information` | `wujia_portal_base/views/portal_franchise_information.xml` | bảng PC thành viên → `table` · 4 `th scope` · **gỡ pager giả** · list mobile `wujia-mdash-row` → `compact-row` |

CSS hai tầng (kiến trúc D5e/D5f) trong `wujia_portal_exam/static/src/css/portal_exam.css`:
dáng do `.wj-data-item` của variant sở hữu, rule cũ khoá bằng `:not(.wj-data-item)` và chỉ còn
layout (`display/gap/align`). **Không sửa token dùng chung. Không sửa CSS của `wj-surface-card`.**

Phiên bản: `wujia_portal_layout` 19.0.44.0.0 → **19.0.45.0.0** · `wujia_portal_exam`
19.0.5.11.2 → **19.0.5.12.0** · `wujia_portal_base` 19.0.7.10.0 → **19.0.7.11.0** ·
`wujia_portal_info_request` 19.0.1.6.2 → **19.0.1.7.0**.
`_components.css?v=1270` **cố ý không bump** — file không đổi một byte nào ở lượt này.

## 3. Số đo trước–sau — 3 bảng PC (khổ 1440 · 1024 · 992)

| Bảng | `th[scope]` | Header | Row | Padding ô |
|---|---|---|---|---|
| Thi `wj-exam-pc-list-table` | 0/8 → **8/8** | 50 → **44** | 58 cứng → **68** | `0px 22px` → **`10px 16px`** |
| Info-request `wujia-content-card-table` | 0/8 → **8/8** | 46 → **44** | 62–63 → **54–55** | `14px 20px` → **`10px 16px`** |
| Thành viên `wj-pc-acct-members` | 0/4 → **4/4** | 50 → **44** | 58 → **52** | `0px 22px` → **`10px 16px`** |

Cả ba khớp bộ DataTable của BA (header 44 · row ≥52 · `10px 16px` · mọi `th` có `scope`).
Hàng bảng thi **68px** là hệ quả của việc bỏ `height:58px` cứng: nội dung ô (badge trạng thái +
badge kết quả + nút thao tác) tự quyết chiều cao. Vẫn ≥52 nên **đạt spec**, nhưng làm thủng
acceptance #9 một ô — xem mục 6.

## 4. Số đo trước–sau — 4 danh sách mobile (khổ 991 · 390 · 360)

| Danh sách | Variant chọn (theo SỐ ĐO trước khi sửa) | Cao | Gap | Radius | Padding |
|---|---|---|---|---|---|
| `wujia-mexam-card` `/portal/exam` | `detail-card` (109,25 nằm trong 96–120) | 109,25 → **109,25** (khổ 360: **109,25–135,25**) | 12 → **8** | 14 → **12** | `12px` → **`12px 14px`** |
| `wujia-mexam-course` `/portal/exam/register` | `detail-card` (116,25 trong 96–120) | 116,25 → **108,25** | 12 → **8** | 14 → **12** | `16px` → **`12px 14px`** |
| `wujia-mexam-rrow` `/portal/exam/registration/15` | `compact-row` (70 trong 64–76) | 70 → **70** | 10 → **8** | 14 → **12** | `12px 14px` (giữ) |
| `wujia-mdash-row` `/portal/franchise-information` | `compact-row` (64,5 trong 64–76) | 64,5–65,5 → **66,5** | 0 → **8** | 0 → **12** | `12px 0` → **`12px 14px`** |

**Giao cắt D4 ↔ D5 ở `wujia-mexam-card`:** item là
`<a class="wj-surface-card wj-surface-card--record wj-surface-card--compact wj-surface-card--padded wujia-mexam-card wj-data-item">`
— nó mang **cả** component SurfaceCard (đã nghiệm thu ở D4) **lẫn** `wj-data-item` của D5.
Quyết định: gắn `wj-data-item` vào **chính thẻ `<a>` đó** (nó là con trực tiếp của container,
đúng thứ bộ đo đo và đúng 25 call site trước), và **để D5 thắng bằng độ đặc hiệu tại rule variant**
(`.wj-data-list--detail-card .wj-data-item`, (0,2,0)) thay vì sửa `wj-surface-card` (0,1,0).
Đo xác nhận tầng thắng: radius **14 → 12**, padding `12px` → `12px 14px` (số của D5),
trong khi `_components.css` **không đổi một byte** — ghim bằng `test_surface_card_khong_bi_sua`.

## 5. Ngã ba seed — quyết định và lý do

Guard chỉ nói được điều gì khi có dữ liệu (bẫy D5e #2). Bổ vào **chính**
`scripts/seed_d5_datalist_demo.py` (không viết script rời, giữ idempotent), đi qua **cơ chế
nghiệp vụ** chứ không ghi thẳng field tính toán (bài học D5g #5):

| Bảng | Trước | Sau | Cách tạo |
|---|---:|---:|---|
| `wujia.exam.course` | 1 | **12** | `create` + `time_slot_ids` rồi `action_publish()`; 3 khoá không có ca sắp tới ⇒ item ra lớp `is-closed` do `_course_meta()` tự suy; 1 khoá `capacity=1` ⇒ badge "Hết chỗ" |
| `wujia.exam.registration` | 3 | **13** | `sudo().create(state='submitted', requester_user_id=…, line_ids=…)` — đi qua `_check_booking_allowed` + `_lock_and_check_capacity` |
| `wujia.info.update.request` | 0 | **24** | `create` + `action_submit()` / `action_start_review()` / `action_approve()` / `action_reject()` để rải đủ trạng thái |

13 phiếu × `PAGE_SIZE=10` ⇒ `/portal/exam` có **2 trang** ⇒ guard pager thử được **cả hai chiều**.
Bộ đếm bản ghi của mọi màn khác **không đổi** (in trước–sau trong log seed).

Hai bẫy đã sập khi seed và cách gỡ: `action_publish()` báo *"cần ít nhất 1 ca thi"* ⇒ phải
`time_slot_ids` ngay lúc `create`; `with_user(owner_user)` (portal) không đọc được `ir.sequence`
⇒ dùng `.sudo()` kèm `requester_user_id` / `created_by_user_id` tường minh, đúng đường controller
`custom/wujia_portal_exam/controllers/portal.py:472`.

## 6. Acceptance #9 — số record đọc được không cần cuộn (ghép theo **VỊ TRÍ** call site)

Ghép theo **chỉ số vị trí**, không theo tên lớp container — vì tên lớp đổi khi bọc component
(`wujia-mexam-list` → `wj-data-viewport`) và ghép theo tên sẽ in ra "0 ô thủng" trong khi thật
ra có thủng (bài học D5g #1).

**11 ô đổi trên 15 route × 6 khổ: 4 ô GIẢM, 7 ô TĂNG.**

| Route | Khổ | Call site | Trước → Sau | Nguyên nhân đo được |
|---|---|---|---:|---|
| `/portal/exam` | 1440 | bảng PC | **8 → 7** | bỏ `height:58px` cứng ⇒ hàng 68px |
| `/portal/exam?limit=50` | 1440 | bảng PC | **8 → 7** | nt (cùng bảng) |
| `/portal/exam` | 360 | list mobile | **5 → 4** | đệm ngang 14px ⇒ tiêu đề xuống dòng ⇒ hàng 109,25 → tối đa 135,25 |
| `/portal/exam?limit=50` | 360 | list mobile | **5 → 4** | nt |
| `/portal/exam/register` | 991·390·360 | khoá thi | 5 → **6** | đệm 16 → `12px 14px` |
| `/portal/info-request` | 991·992 | bảng PC | 6 → **7** | hàng 62 → 54 |
| `/portal/info-request` | 1024 | bảng PC | 6 → **8** | nt |
| `/portal/info-request` | 1440 | bảng PC | 9 → **10** | nt |

**Không tự vá, không đổi số của BA.** Hai ô giảm ở màn Thi được báo lên câu 7 gửi BA
(`docs/ba-questions-d5-datalist.md`) — cùng loại mâu thuẫn nội tại đã nêu ở câu 3, 4c và 6:
"đúng bộ số BA" và "không giảm record trong viewport" không đồng thời thoả ở màn nhiều nội dung.

**Chiều cao trang** (trước → sau): `/portal/exam/register` **−152** ở cả 3 khổ mobile ·
`/portal/exam/registration/15` −6 · `/portal/franchise-information` −36 ở PC, +38…+77 ở mobile ·
`/portal/exam` +94 ở PC (hàng cao hơn) và +172 ở khổ 360.

## 7. Pager — guard thử được cả hai chiều

| Màn | Dữ liệu | Nút trang trước | Nút trang sau |
|---|---|---:|---:|
| `/portal/exam` | 13 phiếu, 10/trang ⇒ **2 trang** | 2 | **2** (giữ — đúng) |
| `/portal/exam?limit=50` | 13 phiếu, 50/trang ⇒ **1 trang** | 1 | **0** ✅ |
| `/portal/franchise-information` | 5 thành viên, **không phân trang server** | "1 ›" cứng | **0** ✅ |

**Tách guard (tiền lệ D5c/D5g giữ nguyên):** nút trang là **điều hướng** ⇒ ẩn khi 1 trang;
dòng đếm *"Hiển thị 1–13 / 13 bản ghi"* và ô `<select>` cỡ trang là **thông tin / điều khiển**
⇒ **giữ nguyên** ở 1 trang. Đo xác nhận: chuỗi `"Hiển thị 1–13 / 13 bản ghi  10/20/50 / trang"`
còn nguyên sau khi `pageBtns` về 0.

**Lỗi thật tìm thấy ở `/portal/franchise-information`:** "pager" của bảng thành viên là **3 thẻ
`<span>` cứng** (`1`, `›`) — không hề có phân trang phía server, nên nó **luôn** hiện với đúng
một trang, vi phạm thẳng acceptance *"pager chỉ hiện khi >1 trang"*. Đã gỡ nút trang ở **cả hai
nhánh** (có thành viên / rỗng), giữ ô cỡ trang. Ghim bằng `test_pager_gia_cua_thanh_vien_da_go`.

## 8. Tương tác — hover đo thật (`docs/d5h-hover.json`)

Đo `getComputedStyle` sau `mouse.move` thật; **"trước"** lấy bằng cách gỡ lớp `wj-data-item`
ngay trên trang rồi đo lại (không có ảnh chụp trước migrate cho màn con).

| Item | Thẻ | Hover TRƯỚC | Hover SAU | Kết luận |
|---|---|---|---|---|
| `wujia-mexam-card` | `<a>` **bấm được** | nền `#EAF7FD` + viền `#28A9DF` + shadow | **y hệt** | ✅ variant **không** đè mất chữ ký D4 (`_interaction.css:61`, `:is()` (0,4,0)) |
| `wujia-mexam-course` | `<div>` không bấm được | không có | **không có** | ✅ `detail-card` không kèm `:hover` |
| `wujia-mexam-rrow` | `<div>` **không** bấm được | **không có** | **nền `rgba(40,169,223,.04)` + viền xanh** | ⚠️ **mọc thêm hover** — gợi ý sai "bấm được", báo BA (câu 6 nay có ca thứ hai) |
| `wujia-mdash-row` | `<div>` không bấm được | **đã có sẵn** nền `#EAF7FD` + shadow (tên nó nằm trong `:is()` từ trước D5h) | y hệt | không phải hệ quả của lượt này |
| `wujia-mhist-row` (đối chứng D5e) | `<a>` | có | có | không đổi |
| `.inspection-card-item` (đối chứng SurfaceCard chưa migrate) | `<div>` | không | không | không đổi |

> Bẫy đã sập ngay trong lượt này: rê vào **tâm** item thì thanh điều hướng dưới màn che mất điểm,
> `elementFromPoint` trả về thanh nav ⇒ đọc ra "KHÔNG ĐỔI" **sai** ở `wujia-mdash-row`. Bộ đo nay
> thử 4 điểm và **chỉ lấy số khi `elementFromPoint` rơi đúng trong item**.

## 9. Guard — chứng minh bằng mutation

14 test mới (`TestDataListExam` ×9, `TestDataListAdjacent` ×5) trong
`custom/wujia_portal_layout/tests/test_d5_data_list.py`, tag `wujia_data_list_d5`.
Chọn call site theo **CẤU TRÚC** (có `thead` / có lớp item), **không** theo `dl_variant`
(bài học D5g #3). Mọi so tên lớp dùng ranh giới `(?![-\w])`.

**13 phép, mỗi phép làm đỏ ĐÚNG MỘT test** (tổng thể `1 failed, 0 error(s) of 66 tests` mỗi lần):

| Phép | Đổi gì | Test đỏ |
|---|---|---|
| 1 | `dl_variant` compact-row → detail-card (thi) | `test_bon_call_site` |
| 2 | bỏ `scope` một `th` bảng thi | `test_moi_th_deu_co_scope` |
| 3 | bỏ `wj-data-item` khỏi `wujia-mexam-rrow` | `test_item_mobile_mang_ca_hai_lop` (Exam) |
| 4 | guard `pc_pager['pages']>1` → `pc_regs` | `test_pager_guard_theo_pages` |
| 5 | bọc `<form>` cỡ trang vào guard điều hướng | `test_o_co_trang_la_dieu_khien_khong_bi_guard` |
| 6 | gỡ `:not(.wj-data-item)` của `.wujia-mexam-course` | `test_mot_chu_so_huu_dang_ba_ho` |
| 7 | thêm `padding` vào rule layout của `rrow` | `test_layout_hai_ho_nam_trong_media` |
| 8 | bỏ lớp `wj-surface-card` khỏi item thi | `test_surface_card_khong_bi_sua` |
| 9 | `dl_variant` compact-row → detail-card (thành viên) | `test_ba_call_site` |
| 10 | bỏ `scope` một `th` bảng thành viên | `test_th_scope_du_muoi_hai_cot` |
| 11 | bỏ `wj-data-item` khỏi `wujia-mdash-row` | `test_item_mobile_mang_ca_hai_lop` (Adjacent) |
| 12 | trả lại một `<span class="wj-pc-page-btn">` | `test_pager_gia_cua_thanh_vien_da_go` |
| 13 | nới guard `page_count>1` → `pager` (info-request) | `test_pager_info_request_giu_guard_page_count` |

Hoàn tác bằng **ảnh chụp byte + `sha256`** (không `git checkout`): **13/13 khớp sha256**.
Bộ chạy đọc **file log THẬT** `logs/2026/09/2026-09-08.log` theo byte offset, regex
`(?:FAIL|ERROR): (?:\S*\.)?(test_\w+)`, và in kèm dòng tổng kết thô.
Chạy sạch cuối cùng: **`RC=0 | 0 failed, 0 error(s) of 66 tests`** (53 test cũ + 13 mới).

Hai sửa test trong lượt (guard sai, không phải code sai):
- `_mobile()` của D5g dùng `re.match` neo đầu chuỗi ⇒ **bỏ sót** item thi vì lớp của nó **mở đầu
  bằng `wj-surface-card`**; đổi sang `re.search(r'(^|\s)…(?![-\w])')`.
- `test_item_mobile_mang_ca_hai_lop` (Adjacent) ban đầu chọn call site theo `dl_variant` ⇒ phép 9
  làm đỏ **hai** test. Đổi sang chọn theo cấu trúc — đúng bài học D5g #3.

## 10. RULE 1 + RULE 2 (`docs/d5h-rule-after.json`)

`RULE 1 HIERARCHY vi phạm: **0**` · `tràn ngang: **0**` · `lỗi JS: **0**` · `redirect ngầm: **0**`.

Histogram cỡ tiêu đề card: `14.7×10 · **16×22** · 18×39 · 22×6 · 24×3`
(D5c–D5g công bố `16×8`). Chênh **+14** quy hết về **seed**, không phải code: diff theo từng route
giữa `d5g-rule-after.json` và `d5h-rule-after.json` chỉ có `/portal/exam` đổi
(`{18:3, 16:6}` → `{18:3, 16:20}`), đúng `(13−3) × 2 khổ mobile − 6 = 14` tiêu đề 16px sinh thêm
từ 3 → 13 phiếu đăng ký. Nhịp header→body: `8×2 · 12×33` — **không đổi**.

## 11. Hồi quy

9 route không đụng tới: **1896/1896 ô, 0 lệch** — trong đó có `/portal/inspection`, xác nhận
**hai module của anh Thái không bị chạm** một byte nào.

## 12. LIMIT (đã ghi vào ledger, gửi BA cùng issue)

1. **2 call site Khảo sát DEFER có chủ đích** (bảng PC + list mobile của
   `wujia_portal_inspection`) — quyết định của chủ dự án 08/09/2026, **không phải sót**.
   ⇒ cụm khép ở **29/31** trong phạm vi BA.
2. **Bộ số cả cụm là `provisional`** — 6 câu trong `docs/ba-questions-d5-datalist.md` chưa có
   trả lời; lùi lại chỉ là một khối CSS.
3. **Acceptance #9 thủng 2 chỗ ở màn Thi** (PC 1440: 8→7 · mobile 360: 5→4) — đã báo ở câu 7.
4. **Khổ 360, hàng phiếu thi cao tới 135,25px**, vượt trần `detail-card` 96–120 do nội dung xuống
   dòng — cùng loại LIMIT BA đã nghiệm thu ở D5c/D5f (`/portal/delivery` 128,98).
   Ép về 120 phải bỏ bớt field ⇒ Dev không tự cắt.
5. **`wujia-mexam-rrow` mọc thêm hover** dù không bấm được — chờ BA chốt (câu 6 ca thứ hai).
6. **Còn 2 bảng chưa đủ `th[scope]`**, cả hai **ngoài phạm vi 31 call site**:
   `/portal/inspection` `wj-pc-table` 0/5 (defer theo mục 1) và `/portal/exam/register`
   `wj-exam-pc-part-table` 0/6 — bảng **nhập liệu** của form, không phải danh sách bản ghi.
7. `/portal/reports/orders` trả 500 — lỗi có sẵn của cụm **R3**, không thuộc D5.
