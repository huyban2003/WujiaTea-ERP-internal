# G2 — Hạ chiều cao header mobile 104 → 72 · bảng nghiệm thu (18/09/2026)

**Yêu cầu:** chủ dự án, cuối phiên "Nhịp dọc mobile", kèm ảnh chụp header: *"cái navigation này
phải hẹp cái height lại"*. Phạm vi chốt: **CHỈ header**; dải cửa hàng 48 và thanh dưới 83 để phiên sau.

**Kết quả:** đạt. Header 104 → **72**, mốc đầu nội dung 152 → **120**, mọi trang mobile ngắn đi
**đúng 32px**, PC **0 ô lệch**, và nhân tiện trả xong một nợ cũ: vùng chạm 3 nút header **38 → 44**.

## 1. Đã đổi gì

| Chỗ | Trước | Sau |
|---|---|---|
| `--wujia-mheader-height` | 104px khai ở `:root` gốc | **72px** khai trong khối `@media (max-width:991.98px)` |
| `.wujia-mheader-actions` | `align-self: flex-start; margin-top: 39px` (neo Blank Shell y=39..77) | canh giữa theo header |
| `.wujia-mheader-action::before` | không có | hộp **44×44** căn giữa, `position: absolute` |
| Logo | 116×44, canh giữa (y 30..74) | **116×44 giữ nguyên**, canh giữa (y 14..58) |

Ba ghi chú về cách làm:

1. **Token khai trong khối mobile** — header chỉ hiện `<992px` (`d-lg-none`), nên PC không đọc tới.
   Không phải chứng minh PC bất biến bằng phép đo (vẫn đo, vẫn 0 ô lệch).
2. **Neo tuyệt đối là thứ phải gỡ, không phải con số 72.** `margin-top: 39px` của cụm nút chỉ đúng
   với header 104; giữ lại thì cụm nút tràn khỏi header. Guard khoá đúng lớp này.
3. **Vùng chạm dùng `::before`, không dùng `::after`** — `::after` của chính các nút đó đã bị dành để
   tắt caret Bootstrap (`.wujia-mheader-action.dropdown-toggle::after { display: none }`). Viết vào
   `::after` là vùng chạm biến mất ở đúng 2/3 nút mà không có dấu hiệu gì. Có guard riêng cho bẫy này.

## 2. Bảng đo

| # | Phép đo | Ngưỡng | Kết quả | |
|---|---|---|---|---|
| 1 | Chiều cao header, 5 route × 2 khổ | 72 | **72 cả 10** | ✅ |
| 2 | Mốc đầu nội dung mobile | giảm 32, không hở/không đè | **152 → 120** cả 10 | ✅ |
| 3 | `wj_measure` mobile (16 ô: 8 route × 390/360) | giảm | **−32,0px mỗi ô** | ✅ |
| 4 | `wj_measure` PC 1440/1024/992 | 0 ô lệch | **0** | ✅ |
| 5 | Ô mất record | 0 | **0** (Báo cáo còn tăng 14 → 16) | ✅ |
| 6 | Dòng thấy trọn màn đầu — Kiến thức @390 | tăng | 3 → **4** | ✅ |
| 7 | Vùng chạm 3 nút header | ≥44 | **44×44**, hộp nhìn thấy vẫn 38 | ✅ |
| 8 | Bấm thật: tâm nút, mép ngoài hộp 38, avatar, logo | nhận đúng | **4/4** (bấm cao hơn hộp 2px vẫn mở dropdown ⇒ pseudo ăn thật) | ✅ |
| 9 | Tràn ngang · lỗi JS · redirect ngầm | 0 | **0 · 0 · 0** | ✅ |
| 10 | HIERARCHY | không thêm mới | 3 → **3** (nợ có sẵn FR-A3) | ✅ |
| 11 | Ảnh 4 route mobile | header cân, không vỡ | logo + 3 nút cùng hàng canh giữa | ✅ |
| 12 | Suite portal 14 module | 0 đỏ | **586/586** (579 + 7 guard mới) | ✅ |
| 13 | DB trắng chỉ cài `wujia_portal_layout` | 0 đỏ ngoài nợ cũ | **0 failed / 1 error** = `test_fra3_layer_guard` có sẵn từ FR-A3 | ✅ |
| 14 | Mutation | mỗi phép phá ≥1 test đỏ | **5/5 đỏ** | ✅ |
| 15 | `check_layers` | không thêm vi phạm | **2 R7** `_wj_ensure_contract` (code anh Thái, có sẵn) | ✅ |

**Guard mới** `wujia_portal_layout/tests/test_g2_mobile_header.py` (7 test) — đặt ở khung chứ không ở
`portal_base`: header là component của chính khung, và sau F5b khung phải tự chạy được một mình.
Mutation đã phá 5 hướng: hạ token về 104 · gõ số cứng vào `.wujia-mheader` · dựng lại `margin-top: 39px`
· bóp vùng chạm về 38 · đổi `::before` thành `::after`.

## 3. Đính chính số của phiên trước

Phiên "Nhịp dọc mobile" ghi khung cố định **235px = 26% màn hình** (header 104 + dải 48 + thanh dưới 83).
Đo lại: **chỉ thanh dưới 83px thật sự `position: fixed`**; header và dải cửa hàng nằm trong luồng
thường (`.wujia-mheader` chỉ có `display/height/padding/background`). Hệ quả:

- Không có 235px bị khoá cứng mỗi màn. Header + dải = **152px chiếm chỗ ở ĐẦU trang**; cuộn xuống là
  chúng trôi đi.
- Đổi lại, vì header nằm trong luồng nên hạ 32px **làm ngắn trang thật 32px** — điều mà phiên trước
  cho là không xảy ra. Cả hai thước (chiều cao trang và khối/dòng thấy trọn màn đầu) đều dùng được.
- Cũng vì vậy **không phải đi vá mốc đầu nội dung**: `--wujia-mcontent-top` giữ nguyên 10px, y=120 là
  72 + 48 + 10 tự ra.

Đã sửa lại §4 của `mobile-rhythm-acceptance.md` cho khớp.

## 4. Còn treo

- Chưa deploy UAT (nếp cụm F: commit + push, deploy tay riêng).
- **Một dòng FYI cho BA, gộp 2 khoản**: lệch Figma *Mobile Shell FINAL* (header 104 → **72**) và lệch
  nhịp dọc của phiên trước (gap 14→8, mép trên 16→10, tiêu đề nhóm 16/8→6/4). Chủ dự án đã chốt
  "Figma tương đối thôi" ⇒ không chặn, chỉ báo để BA cập nhật lại Figma.
- Hai cần gạt còn lại của mạch "một màn thấy nhiều hơn", **chưa làm, chờ BA**: **G1** rút dòng danh
  sách 2–3 dòng về 1 dòng (−250…350px Home, ăn theo mọi màn danh sách) · **G3** cỡ chữ/line-height.
- Phần còn lại của khung mobile nếu muốn làm tiếp: dải cửa hàng 48 (trong luồng) và thanh dưới 83
  (thứ duy nhất thật sự cố định — hạ nó mới là lấy lại chỗ ở MỌI vị trí cuộn).
