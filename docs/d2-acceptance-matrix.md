# D2 — bảng đối chiếu acceptance (WJ-PORTAL-UI-002, STT 115)

**Ngày đo:** 2026-08-26 · **Kết quả: 14/14 Pass (100%)** · Kiểm kê gốc rễ →
`docs/d2-font-inventory.md`.

**Môi trường:**
- **Đo font trước–sau:** chỉ-đọc **trên chính UAT** `http://113.161.187.126:8019`
  (admin, cookie `wujia_active_franchise_id=3`), **16 route × 5 breakpoint = 80 ô**;
  bản "sau" nhúng CSS bằng `page.add_style_tag` (phương pháp C6) vì local không có
  `website`/`website_sale` nên **không tái hiện được lỗi** (L14/L10).
- **Build + hồi quy:** DB copy cô lập **`wujia_tea_d2`** (nền `wujia_tea_d1`), **port 8066**,
  `--db-filter='^wujia_tea_d2$'` — KHÔNG đụng `wujia_tea_19`/8019.
- Harness: `scratchpad/d2_font_audit.py` · `d2_compare.py` · `d2_tabwalk.py`.

---

## 🔬 Run ĐỐI CHỨNG — tách "lệch do bản vá" khỏi "lệch do việc nhúng"

Bẫy C6: nhúng lặp `_variables.css` tự nó làm đổi vài px chiều cao. Đã chạy **3 lượt**:

| Lượt | Nội dung nhúng | Font còn lệch | Chiều cao khác lượt gốc |
|---|---|---|---|
| `before` | không nhúng gì (UAT nguyên trạng) | 49 hiện / 145 kể cả ẩn | — |
| **`control`** | nhúng lặp bản **HEAD** (chưa vá) | **y hệt `before`** | **8 ô lệch +3…+16px** |
| `after` | nhúng bản **đã vá** | **0** | **y hệt `control`** |

⇒ 8 ô lệch chiều cao + 1 heading `h 17→19` là **artifact của việc nhúng lặp**, không phải của
bản vá — chứng minh bằng run đối chứng, không phải suy đoán. Bảng dưới so **`control` ↔ `after`**
(cùng điều kiện nhúng, khác nhau đúng bản vá).

## Bảng acceptance

| # | Yêu cầu BA (`Kết quả mong muốn`) | Đo được | Pass |
|---|---|---|---|
| 1 | Mở bất kỳ màn Portal trên PC/mobile | 16 route × 5 bp (360/390/430/500/1440) = **80 ô, HTTP 200 cả 80** | ✅ |
| 2 | Font chính của tiêu đề/nhãn/nội dung/bảng/card/menu/form/nút đều là **Inter** | quét **mọi text node**: chỗ ≠ Inter **49 → 0** (hiện), **145 → 0** (kể cả ẩn); **80/80 ô sạch** | ✅ |
| 3 | Không còn component nội dung dùng **Inter Tight** | `"Inter Tight"` xuất hiện **0** lần trong computed của mọi text node, 80/80 ô | ✅ |
| 4 | …hoặc font chữ khác | 0 Montserrat / Helvetica / Arial (đã đúng từ trước, giữ nguyên) | ✅ |
| 5 | **Icon font không bị ảnh hưởng** | đếm `::before`/`::after` có `content`: `feather` + `FontAwesome` **giống hệt 80/80 ô** | ✅ |
| 6 | Font fallback Unicode chỉ dùng khi Inter thiếu glyph | `Hồ sơ cá nhân — 1.234.000 đ` → `getPlatformFontsForNode` = **Inter** (không rơi fallback); Inter khai `unicode-range` Latin nên fallback **chỉ** nhận glyph ngoài dải | ✅ |
| 7 | Fallback có tác dụng thật với ngôn ngữ đang bật | Thái `ข้อมูลส่วนตัว` → **Noto Sans Thai**; Trung `个人资料` → **Noto Sans CJK SC** (trước vá là **CJK JP** — sai biến thể vùng) | ✅ |
| 8 | Không đổi **xuống dòng** ở 360/390/430/500 + desktop | `getClientRects().length` của mọi heading: **80/80 ô giống hệt** | ✅ |
| 9 | Không đổi **chiều cao** | `scrollHeight` từng trang: **80/80 ô bằng nhau** | ✅ |
| 10 | Không **tràn ngang** | `scrollWidth − clientWidth`: **0 ở cả 80 ô**, trước cũng 0 | ✅ |
| 11 | Không đổi **căn chỉnh** | chiều cao + `font-weight` từng heading: **80/80 ô giống hệt** (weight giữ 700/800 đúng `CMP-SH-001`) | ✅ |
| 12 | Build sạch | `-u wujia_portal_layout --stop-after-init` trên `wujia_tea_d2` → **RC=0, 0 ERROR/Traceback**; view arch xác nhận `_variables.css?v=1177` + `_wujia_theme.css?v=1177`, module `19.0.32.4.0` | ✅ |
| 13 | Hồi quy lưới B4 | `b4_regression.py --base :8066` → **286/286 PASS** | ✅ |
| 14 | Hồi quy a11y | tab-walk A/B 6 route × 2 viewport = **331 stop**: thứ tự stop **12/12 route y hệt**, focus ring **12/12 route y hệt** (327/331 stop có ring, 4 chỗ thiếu là **có sẵn từ trước**, không phải hồi quy) | ✅ |

**Regression thêm:** 0 `pageerror` trên cả 80 ô; 16 route đều 200 (gồm 4 trang ngoài 12 màn BA
rà: `/portal/debt/payment-history`, `/portal/reports/orders`, `/portal/info-request`,
`/portal/franchise-information`).

## LIMIT (ghi rõ cho BA khi retest)

1. **Fallback là TÊN font hệ thống, không tự host** (chủ dự án chốt 26/08): máy user không có
   `Noto Sans Thai`/`Leelawadee UI`/`Noto Sans CJK SC`/`Microsoft YaHei`/`PingFang SC` thì vẫn
   rơi về `sans-serif` như hiện nay — không tệ hơn, nhưng **không đảm bảo giống nhau tuyệt đối
   giữa các máy**. Muốn đồng nhất 100% phải tự host Noto Sans SC (~vài MB) — trái perf-first
   1500 user, đã bỏ.
2. **Đo fallback trên Linux headless** (máy dev) — Windows/macOS của tester sẽ chọn tên khác
   trong stack (`Leelawadee UI` / `Microsoft YaHei` / `PingFang SC`). Chữ Latin + Việt thì
   **chắc chắn** là Inter ở mọi máy vì font tự host.
3. **`zh_CN` chưa bật trên UAT** (§5) nên nhánh chữ Trung đo bằng probe dựng client-side, chưa
   đo được trên trang thật. `.po` đã có sẵn trong repo, bật lang là chạy.
4. **Cố ý không nới rule `font-weight:700 !important`** (`_wujia_theme.css:35-40`) dù nó cũng
   neo `.content-wrapper`: nới sẽ ép heading mobile về 700 và **phá weight 800 của `CMP-SH-001`**
   (C8a/C8b). Nếu BA muốn thống nhất weight thì mở issue riêng.
5. **`H4.wj-pc-noti-popup__title`** (popup chuông, có mặt ở cả 16 route) trước đây là Inter Tight
   nhưng **ẩn** cho tới khi bấm chuông — BA không thấy nên không ghi vào issue; nay đã về Inter
   cùng lượt.
6. **Bản vá đo trên UAT bằng cách nhúng CSS**, chưa deploy. Sau khi chủ dự án chạy
   `-u wujia_portal_layout` cần **đo lại chỉ-đọc trên UAT** để chốt (asset `?v=1177` phải ăn).

## Lệnh deploy

```
-u wujia_portal_layout
```
Không module mới · không cập nhật dữ liệu · `?v=1177` đã bump (còn thấy font cũ = cache trình
duyệt/proxy).
