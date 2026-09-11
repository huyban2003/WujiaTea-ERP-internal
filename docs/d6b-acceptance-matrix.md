# D6b — Card Bù hàng: `UAT-BH-008` trọn + nửa card của `UAT-BH-007`

**Ngày:** 2026-09-10 · **Nhánh:** `dev/2026-09-10-d6` · **DB đo:** `wujia_tea_d6` (port 8080) ·
**Module:** `wujia_portal_return` `19.0.2.13.0` → **`19.0.3.0.0`**

Sửa **2 file sản phẩm**: `views/portal_return_list.xml` (khối mobile) +
`static/src/css/portal_return.css`. **Không** đụng `_components.css` ⇒ **không cần bump `?v=`**
(CSS của module đi qua bundle `web.assets_frontend`, không phải `<link ?v=>`).

---

## 1. Làm gì

| # | Issue | Thay đổi | Vì sao thế |
|---|---|---|---|
| 1 | BH-008 | Dòng đầu chỉ còn **mã phiếu + badge trạng thái phê duyệt**; badge **tiến độ bù** tách sang dòng riêng `.wujia-mreturn-row-progress` có nhãn **"Tiến độ bù"** | Trước đó cả hai badge chung một `row-badges` ⇒ hai trạng thái khác nghĩa đứng lẫn nhau |
| 2 | BH-008 | `.wujia-mreturn-row-meta`: `flex; gap:18px` → `grid; 1fr 1fr; gap:8px` | `flex` cho ô thứ hai trôi theo độ dài ô thứ nhất ⇒ đo được **2 bố cục** `left` khác nhau |
| 3 | BH-007 | `.wujia-mreturn-row-product`: `white-space:nowrap` → `-webkit-line-clamp: 2` + `overflow-wrap: anywhere` | `nowrap` cắt ngay **giữa dòng 1**. `overflow-wrap` vì tên Trung không có dấu cách ⇒ không có điểm ngắt, sẽ đẩy card tràn ngang |

**KHÔNG làm** (và vì sao):

- **Không** bọc mỗi record bằng `wj_surface_card` variant `record` như chữ trong sheet. Card này
  đã là `wj_data_list` variant `detail-card` (D5f); bọc thêm vỏ = **tái tạo đúng hồi quy "thẻ
  trắng lồng thẻ trắng"** mà D5h.2 vừa vá 09/09. Chủ dự án chốt 10/09: giữ theo fix mới nhất.
  → **LIMIT ghi vào ledger.**
- **Không** khai lại stack font CJK cho BH-007: đã nằm trên `--wujia-font-family` từ D2
  (`_variables.css:187` — Inter → Noto Sans Thai → Noto Sans SC → …). Khai lại chính là nguồn
  của cảm giác "font rời rạc" mà BH-007 phàn nàn. Có test khoá điều này.
- **Không** đụng `portal_return_form.xml` — nửa dropdown của BH-007 và toàn bộ BH-009 là **D6c**.

## 2. Guard mới `scripts/qa/wj_returncard.py` — trước → sau

`wj_datalist.py` đo *dáng*, `wj_nesting.py` đo *lồng nhau*; cả hai **mù với phân cấp bên trong
card** — đúng loại lỗ đã để lọt hồi quy D5h.2.

| Khổ | card | cắt ngay dòng 1 | cặp badge | badge cùng hàng | bố cục metadata | vi phạm |
|---:|---:|---:|---:|---:|---:|---:|
| 991 | 20 → 20 | 0 → 0 | 5 → 5 | **5 → 0** | **2 → 1** | 6 → **0** |
| 390 | 20 → 20 | **8 → 0** | 5 → 5 | **5 → 0** | **2 → 1** | 14 → **0** |
| 360 | 20 → 20 | **8 → 0** | 5 → 5 | **5 → 0** | **2 → 1** | 14 → **0** |
| | | | | | **TỔNG** | **34 → 0** |

**Không phải Pass rỗng:** mẫu đo giữ nguyên — 20 card, 20 tên sản phẩm, **5 cặp badge** ở cả hai
lượt. Guard vẫn nhìn thấy đúng chừng ấy đối tượng, chỉ phán quyết đổi.

Chi tiết đại diện ở 390px:

| Phiếu | tên SP: dòng trước → sau | cắt trước → sau | badge `top` trước → sau |
|---|---|---|---|
| `SEED-D6/01` (tên 101 ký tự) | 1 → **2** | True → True (`…` cuối **dòng 2**, đúng spec) | state 13 · prog 13 → state 13 · **prog 48** |
| `SEED-D6/04` (tên 48 ký tự) | 1 → **2** | True → **False** (hiện đủ) | state 13 · prog 13 → state 13 · **prog 48** |
| `SEED-D6/07` (tên 28 ký tự) | 1 → 1 | False → False | state 44 · prog 44 → **state 13** · prog 48 |

`SEED-D6/07` đáng chú ý: trước D6b **cả hai** badge bị đẩy xuống dòng 2 (`top 44`) vì
`row-badges` wrap; sau D6b trạng thái phê duyệt về đúng dòng đầu.

## 3. Hồi quy toàn portal — `wj_measure.py --diff`

13 route × 6 khổ (1440 · 1024 · 992 · 991 · 390 · 360) = **78 ô**.

- **RULE 1 HIERARCHY = 0 · tràn ngang = 0 · lỗi JS = 0 · redirect ngầm = 0** (giống hệt mốc trước).
- Histogram cỡ tiêu đề card **không đổi**: `14.7×15 · 16×33 · 18×39 · 22×6 · 24×3`.
- Nhịp header→body **không đổi**: `8×3 · 12×33`.
- **3/78 ô đổi**, cả ba đều là `/portal/return` mobile; **0 ô đổi ở PC** (1440/1024/992 giống hệt byte số):

| Khổ | pageH trước → sau | Δ | record trong viewport |
|---:|---|---:|---|
| 991 | 3160 → 3404 | +244 | 14 → 14 |
| 390 | 3251 → 3572 | +321 | 14 → 14 |
| 360 | 3378 → 3572 | +194 | 14 → 14 |

**0 ô mất record** — acceptance #11 của BA giữ nguyên. Trang cao thêm là hệ quả trực tiếp của
việc BA yêu cầu (thêm một dòng + tên hai dòng), không phải tác dụng phụ.

- `wj_nesting.py`: **0 chỗ lồng khung** trên 6 route × 3 khổ — hồi quy D5h.2 không tái phát.

## 4. Test — 7 test + 7 phép mutation

`custom/wujia_portal_return/tests/test_return_card_d6.py`, tag `wujia_return_d6`. Khoá **hợp đồng
cấu trúc + CSS nguồn** (bảng đo không sống qua sprint sau).

**Mutation: mỗi phép phá làm đỏ đúng test tương ứng** — không có guard chứng-minh-rỗng:

| Phép phá | Test đỏ |
|---|---|
| M1 đổi tên lớp dòng tiến độ bù | `test_co_dong_tien_do_bu_rieng_co_nhan` (+1 error dây chuyền) |
| M2 đưa badge tiến độ bù **ngược** vào dòng đầu | `test_dong_dau_khong_con_badge_tien_do_bu` |
| M3 chép cứng nhãn "Đã bù đủ" | `test_nhan_tien_do_bu_lay_tu_hang_controller` |
| M4 trả tên SP về `nowrap` | `test_ten_san_pham_toi_da_hai_dong` |
| M5 trả metadata về `flex` | `test_metadata_hai_cot_on_dinh` |
| M6 khai lại `font-family` trong module | `test_khong_khai_lai_stack_font` |
| M7 khai lại `border` ở call site · M8 gỡ `wj-data-item` | `test_giu_nguyen_hop_dong_datalist_d5f` |

- `--test-tags /wujia_portal_return`: **0 failed, 0 error / 46**.
- `wujia_return_d6 + wujia_data_list_d5 + wujia_surface_card_d4 + wujia_card_header_d3`:
  **4 failed / 211** — xem §5, **có sẵn**.

## 5. 🔴 Bốn test D3 CardHeader đỏ — CÓ SẴN, không do D6b

Chứng minh bằng **run đối chứng `git stash -u`** (bài học S57 — đã một lần suýt quy oan):
bỏ hết thay đổi D6b, chạy đúng lệnh đó ra **4 failed / 204**, **cùng bốn tên test**.

| Test | Assertion |
|---|---|
| `TestCardHeaderCallSites.test_bootstrap_card_header_wrapper_class_is_kept` | `0 != 4` |
| `TestCardHeaderCallSites.test_store_name_became_subtitle_not_a_second_heading` | `0 != 1` — card "Cửa hàng nhượng quyền" phải còn nguyên |
| `TestCardHeaderD3eLayout.test_return_sublabels_keep_their_own_shape` | regex `.card-body > .wj-card-header.wj-return-sublabel … color:` không khớp |
| `TestCardHeaderD3Review.test_exam_summary_card_keeps_the_rhythm_of_its_neighbour` | không tìm thấy `margin-top` của `.wj-exam-pc-sumlist` |

Cả bốn đều là test **đọc file nguồn của module khác**, nên độc lập với DB. Đề nghị mở issue riêng
hoặc gộp vào lứa D7+; **không tự sửa trong D6b** (ngoài phạm vi ba issue BA giao).

## 6. Hai bẫy công cụ đã trả giá trong lượt này (đã vá vào repo)

1. **`wj_measure.py` in bảng đo GIẢ khi login hỏng** — mặc định `demo123` sai (DB dùng
   `wujia@test123`), 78/78 ô redirect mà script vẫn ghi file. Đã vá: `login()` dừng ngay khi còn
   ở `/web/login`; mặc định đổi thành `wujia@test123`. Kiểm chứng bằng mật khẩu sai → guard nổ.
2. **Bundle `web.assets_frontend.min.css` trả 500 trên DB copy** — `wujia_tea_d5h2` không có
   filestore ⇒ 75 `ir_attachment` trỏ file không tồn tại ⇒ **toàn bộ CSS module không nạp**, card
   không có dáng. Nguy ở chỗ `_variables/_components` nạp bằng `<link ?v=>` nên **vẫn chạy** và
   bảng đo vẫn xanh — **chỉ ảnh chụp tố cáo** (đúng bài học D3e). Gỡ:
   `DELETE FROM ir_attachment WHERE url LIKE '/web/assets/%'` + restart, verify bundle 200.
3. Phụ: HttpCase của module đỏ 4 test khi **thiếu `--db-filter`** (gotcha Sprint 48). Ghim vào là
   **46/46 xanh**.

## 7. Đối chiếu `Kết quả mong muốn`

**BH-008** — *"Người dùng phân biệt ngay trạng thái phê duyệt và tiến độ bù; card có thứ bậc
thông tin rõ, cân đối và nhất quán với hệ thống Portal."*

| Vế | Đạt | Bằng chứng |
|---|---|---|
| phân biệt ngay 2 trạng thái | ✅ | badge cùng hàng **5 → 0** ở cả 3 khổ; tiến độ bù có nhãn riêng |
| thứ bậc thông tin rõ | ✅ | dòng 1 mã+trạng thái · dòng 2 tiến độ bù · dòng 3 tên SP · dòng 4 metadata |
| cân đối | ✅ | bố cục metadata **2 → 1** |
| nhất quán hệ thống Portal | ✅ | dáng khung vẫn của `.wj-data-item` (D5f), 0 token mới, 0 rule dáng ở call site |

⇒ **4/4 vế đạt.** Ghi LIMIT: dùng DataList `detail-card` thay vì chữ "SurfaceCard variant record".

**BH-007** — mới xong **nửa card** (2 dòng + không cắt giữa nội dung + font CJK dùng chung).
Nửa còn lại (dropdown `/portal/return/new`: xem đủ option khi mở + vùng hiện tên đầy đủ sau khi
chọn) thuộc **D6c** ⇒ **giữ `Ready for Dev`**, KHÔNG chạy `qa_sync.py` cho BH-007.
