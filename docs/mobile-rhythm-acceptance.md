# Nhịp dọc mobile về một bộ token — bảng nghiệm thu (18/09/2026)

**Yêu cầu:** BA muốn một màn hình điện thoại hiển thị được nhiều thông tin hơn; chủ dự án chốt
giảm 30–35% và làm theo kiểu component (sửa một nơi, cả portal ăn theo).

**Kết quả ngắn gọn:** phần **chuẩn hoá đạt** (một nguồn duy nhất cho nhịp dọc mobile, có guard +
mutation). Phần **chỉ tiêu −30…35% KHÔNG đạt và không thể đạt bằng khoảng trắng** — đo được trần
của hướng này là **≈ −13%**. Lý do và các cần gạt còn lại: §4.

## 1. Đã đổi gì

| Chỗ | Trước | Sau |
|---|---|---|
| `--wujia-mshell-content-gap` (khe giữa các khối) | 14px | **8px** |
| `--wujia-mcontent-top` (mép trên nội dung) | 16px | **10px** |
| `.wj-section-header--m/--any` margin | 16 / 8 | **6 / 4** (qua token `--wujia-m-sechead-mt/mb`) |
| Home `.wujia-mhome` | gap 18 · padding 16 | ăn rule chung · chỉ còn lề ngang |
| Công nợ `.wj-debt` | gap 12 | ăn rule chung |
| Báo cáo `.wujia-mreport` | gap 12 | ăn rule chung |
| Đặt hàng / Giỏ / Lịch sử | dàn con bằng `margin-bottom` 10/14/16 | ăn rule chung (gỡ 5 margin) |
| 3 rule bù trừ âm cho PageHeader (−6 / −4 / −4) | có | **gỡ hẳn** — gap chung nay đúng 8px của CMP-PG-001 |

**Khoảng trắng trước tiêu đề nhóm trên Home: 34px → 14px (−59%)** — đúng chỗ ảnh chụp của chủ dự án.

Nhịp dọc mobile nay khai ở **một chỗ duy nhất**: khối `:root` trong `@media (max-width: 991.98px)`
của `_variables.css`. Đặt trong khối mobile nên PC không thể bị ảnh hưởng — khỏi phải chứng minh.

## 2. Bảng đo (13 route × 5 khổ, `wj_measure.py`, login `anh.owner`)

| # | Phép đo | Ngưỡng | Kết quả | |
|---|---|---|---|---|
| 1 | Chiều cao Home @390 | giảm | 2613 → **2405 (−8,0%)** | ✅ |
| 2 | Chiều cao Home @360 | giảm | 2647 → **2439 (−7,9%)** | ✅ |
| 3 | Chỉ tiêu −30…35% | −30% | **−8%** | ❌ (§4) |
| 4 | Số record thấy trong viewport | không giảm | **0 ô mất record** | ✅ |
| 5 | Khối thấy TRỌN trong màn đầu, Home @390 | tăng | 3 → **4** | ✅ |
| 6 | Dòng thấy TRỌN trong màn đầu (Home / Thông báo) | tăng | 1→2 · 4→5 | ✅ |
| 7 | PC 1440 / 1024 / 992 | 0 ô lệch | **0** | ✅ |
| 8 | Tràn ngang | 0 | **0** | ✅ |
| 9 | Lỗi JS | 0 | **0** | ✅ |
| 10 | Redirect ngầm | 0 | **0** | ✅ |
| 11 | Nhịp PageHeader → khối đầu (7 route) | đúng 8px | **8px cả 7** | ✅ |
| 12 | Suite portal 14 module | 0 đỏ | **579/579** (574 + 5 guard mới) | ✅ |
| 13 | Mutation guard mới | mỗi phép phá 1 test đỏ | **5/5 đỏ** | ✅ |
| 14 | HIERARCHY | không thêm mới | 3 → **3** (nợ có sẵn FR-A3) | ✅ |

**Guard mới** `wujia_portal_base/tests/test_mobile_rhythm.py` (5 test): token phải nằm trong khối
mobile · PC vẫn giữ 16/8 · đúng MỘT rule cấp gap cho mọi trang · không trang nào tự khai gap riêng ·
không còn rule bù trừ âm. Mutation đã phá đủ 5 hướng, cả 5 đều đỏ.

## 3. Bẫy gặp trong phiên

1. **Rule tiêu đề nhóm nằm NGOÀI `@media`** — PC cũng đọc token đó. Nếu chỉ khai token trong khối
   mobile thì PC mất margin (token không định nghĩa → khai báo hỏng → về 0). Đã khai giá trị nền
   16/8 ở `:root` gốc; test `test_pc_van_giu_16_8_cho_tieu_de_nhom` khoá lại.
2. **Gom `padding` vào rule chung là cộng dồn hai lần** — trang dựng trong `.content-wrapper` đã
   được wrapper cấp pad-top; Home còn bị mất lề ngang 16 (vì `.wujia-home-wrapper` cố ý bỏ pad
   ngang). Rule chung nay CHỈ cấp nhịp; padding vẫn là chuyện riêng từng trang.
3. **Một pseudo, hai chủ** (bài học G2, ghi ở đây vì cùng vùng mobile shell): `::after` của
   `.wujia-mheader-action` đã bị dành để tắt caret Bootstrap. Viết vùng chạm 44 vào đó là mất vùng
   chạm ở 2/3 nút, không báo gì. Trước khi dùng một pseudo để nới vùng chạm, phải grep xem nó đã có
   chủ chưa. Kèm theo: **bộ đo chỉ đọc một pseudo sẽ ra số sai** và suýt làm sửa code lành — đo vùng
   chạm phải đọc cả `::before` lẫn `::after`.
4. **Guard D4d khoá `margin-bottom` của `.wujia-mhist-card`** như "không phải dáng khung nên giữ".
   Nay nhịp giữa các thẻ là của trang, không của thẻ ⇒ đã sửa test kèm lý do, không phải nới guard.
5. **Server đang chạy DB `wujia_f0`** (mốc F0 sót lại) khiến `/portal` trả 500 và bộ đo ra bảng
   "Pass rỗng" toàn 900px. Luôn kiểm DB của tiến trình đang nghe cổng trước khi tin số đo.
6. **1 error trên DB trắng chỉ cài khung** (`test_fra3_layer_guard`, 130 test) — đã chạy **đối chứng
   bằng `git stash`**: lỗi y hệt khi chưa có thay đổi của phiên này ⇒ **nợ có sẵn thuộc F6**
   (self-test `portal_base`); FR-A3 là phiên phát hiện, không phải phiên gây ra.

## 4. Vì sao −30% không đạt được bằng khoảng trắng (số đo, không phải phỏng đoán)

Đo phân rã Home @390 (2405px):

| Khối | Cao |
|---|---|
| Hero cửa hàng | 197 |
| Khung giờ đặt hàng | 97 |
| Hành động nhanh (6 ô) | 164 |
| 7 khối danh sách (mỗi khối = tiêu đề 28 + thẻ 186…282) | ~1690 |
| Khung: header 104 + dải cửa hàng 48 (trong luồng, ở đầu trang) + thanh dưới 83 (fixed) | 235 |

**8 dòng danh sách trên Home cao tổng 698px**, và đo từng dòng ra 66 · 67 · 86 · 94 · 113 — tức
**phần lớn dòng CAO HƠN `min-height` 64 vì nội dung 2–3 dòng chữ**, không phải vì đệm. Thử nghiệm
tiêm CSS trực tiếp trên trình duyệt (không sửa code) cho thấy trần của hướng nén khoảng trắng:

| Kịch bản | Chiều cao Home | so với ban đầu |
|---|---|---|
| A. sau phiên này | 2405 | −8,0% |
| B. + gap mục 10→8, đệm thẻ 14→12, hero/khung giờ mỏng hơn | 2373 | −9,2% |
| C. B + dòng danh sách `min-height` 64→56 | 2309 | −11,6% |
| D. C + dòng 48 + ô hành động thấp hơn | 2277 | **−12,9%** |

Kịch bản D đã bóp tới mức phá chuẩn D5 (dòng 64–76) lẫn ngưỡng vùng chạm, mà vẫn chỉ −12,9%.
⇒ **Muốn ngắn 30% phải giảm NỘI DUNG hoặc cỡ chữ, không phải khoảng trắng.**

Ba cần gạt còn lại, đều là quyết định BA/thiết kế (chưa làm, chờ chốt):

- **G1 — dòng danh sách 2–3 dòng chữ → 1 dòng** (bỏ/ghép dòng phụ ngày giờ, badge về cùng hàng).
  Ước tính −250…350px trên Home, và ăn theo mọi màn danh sách. Lệch Figma nhiều nhất.
- **G2 — hạ header mobile 104 → 72 · ĐÃ LÀM 18/09**, xem `docs/g2-header-acceptance.md`. Mọi trang
  mobile ngắn đi đúng 32px, mốc đầu nội dung 152 → 120, PC 0 ô lệch, vùng chạm nút header 38 → 44.
  **Đính chính của phiên G2**: mục này từng ghi "khung cố định 235px"; đo lại thì **chỉ thanh dưới 83
  mới thật sự `position: fixed`** — header và dải cửa hàng nằm trong luồng, chiếm chỗ ở ĐẦU trang rồi
  trôi đi khi cuộn. Kéo theo: hạ header LÀ làm ngắn trang thật 32px (câu "co khung không đổi chiều
  cao trang" ở trên là sai), và không phải vá mốc đầu nội dung.
- **G3 — cỡ chữ/line-height mobile** (tiêu đề dòng 14px/21). Hạ 1px line-height × ~30 dòng ≈ −30px.
  Rẻ nhưng chạm accessibility, cần BA duyệt.

## 5. Còn treo

- Chưa deploy UAT (theo nếp cụm F: commit + push, deploy tay riêng).
- Một dòng FYI gửi BA: nhịp dọc mobile lệch Figma RESP-MOB-SHELL-003 (gap 14→8, top 16→10,
  tiêu đề nhóm 16/8→6/4) — BA yêu cầu nên không chặn, chỉ cần cập nhật lại Figma.
