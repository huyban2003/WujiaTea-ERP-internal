# Cụm C4 — bảng đối chiếu acceptance (WJ-KNW-001…004)

**Ngày:** 15/08/2026 · **Module:** `wujia_portal_knowledge` `19.0.3.8.0` → `19.0.3.9.0`
(không migration, deploy chỉ cần `-u wujia_portal_knowledge`).

**Cách đo:** DB copy cô lập `wujia_tea_c4` (tạo từ `wujia_tea_19`), Odoo riêng **port 8054** —
không đụng `wujia_tea_19`/8019. Đo bằng Playwright + chromium ở **391×844** và **1920×1080**
(`scratchpad/c4_measure.py`, login qua `/web/session/authenticate` rồi gắn cookie), cộng 14
unit/HTTP test mới `--test-tags wujia_knowledge`.

**Kết quả tổng:** Playwright **60/60 đạt (100%)** · test module **14/14 xanh** · hồi quy
**87 test** 3 module khác (`wujia_debt`, `wujia_notification`, `wujia_history`) 0 failed.

**Sau khi deploy UAT (15/08/2026):** đo lại trên `http://113.161.187.126:8019` — chỉ đọc,
không sửa dữ liệu — **42/42 đạt** ở 391×844 + 1920×1080 (`scratchpad/c4_uat_check.py`).
`wujia_portal_knowledge` = `19.0.3.9.0`, 26/26 bài đã có bản text để search. Bài
`uat-1208-knowledge` (KNW-000026) BA để nháp dùng luôn làm ca thử của WJ-KNW-004; giờ phát
hành kiểm bằng bài `ui12-01` (lưu 27/05/2026 17:36 UTC, portal in **28/05/2026 00:36** —
lệch múi giờ đổi cả ngày nên chứng minh chắc hơn). Khối thông báo hiện đúng **một** bản theo
bề rộng: mobile 359px, PC 1572px.

---

## WJ-KNW-001 — category/tag không hợp lệ làm lộ thông tin kỹ thuật

| Yêu cầu (Kết quả mong muốn) | Đo được | Pass |
|---|---|---|
| Không hiển thị tên model / record ID / user ID kỹ thuật | `?category_id=999999`, `?tag_id=999999`, danh mục đã ẩn: body không chứa `wujia.knowledge.category`, `wujia.knowledge.tag`, `User: `, `Traceback`, `Odoo Server Error` (6 phép đo, 2 viewport) | ✅ |
| Chuyển về `/portal/knowledge` | URL cuối = `/portal/knowledge?notice=…`, đã bỏ hẳn tham số lọc rác | ✅ |
| Trang Knowledge tải bình thường | HTTP 200, danh sách bài render đủ, tràn ngang 0, 0 lỗi JS | ✅ |
| Thông báo thân thiện "Danh mục đã chọn không còn khả dụng." | Hiện đúng nguyên văn (danh mục ẩn cũng ra câu này); tag rác ra "Thẻ đã chọn không còn khả dụng." | ✅ |
| Không stack trace / lỗi Odoo thô | Như dòng 1; chi tiết `category_id`/`tag_id`/uid chỉ ghi vào server log | ✅ |
| Lọc hợp lệ vẫn chạy | `?category_id=<hợp lệ>` → 200, ra đúng bài, không hiện thông báo | ✅ (test) |

## WJ-KNW-002 — sai múi giờ Publish date

| Yêu cầu | Đo được | Pass |
|---|---|---|
| Bài có publish 12/08/2026 16:05 giờ portal → detail hiển thị 16:05 | Đặt `publish_date` = 12/08/2026 09:05 UTC; detail in **12/08/2026 16:05** ở cả 2 viewport | ✅ |
| Không lệch 7 giờ giữa list, detail và backend | Chuỗi `12/08/2026 09:05` không còn xuất hiện; list in ngày 12/08/2026; cả 6 chỗ in ngày trong template dùng chung `wj_dt` (`fmt_local_dt` của `wujia_portal_base`, chuẩn `Asia/Ho_Chi_Minh`) | ✅ |
| Thống nhất theo timezone người dùng | Dùng đúng helper chung `portal_tz()` (tz user, rỗng/rác → `Asia/Ho_Chi_Minh`), không viết helper mới | ✅ (test `fmt_local_dt`) |

## WJ-KNW-003 — search không tìm theo summary/content

| Yêu cầu | Đo được | Pass |
|---|---|---|
| Keyword nằm trong title → ra bài | Search theo tiêu đề: ra đúng bài | ✅ |
| Keyword nằm trong summary → ra bài | "chỉ có trong summary" → ra đúng bài, 2 viewport | ✅ |
| Keyword nằm trong text content → ra bài | "Nội dung chi tiết C4" (trong nguồn bị `<strong>` cắt ngang) → ra đúng bài | ✅ |
| Search không phụ thuộc HTML markup | So khớp trên bản text đã bỏ thẻ (`html_to_inner_content`, chuẩn hoá khoảng trắng), 25/25 bài có sẵn đều được điền lúc `-u` | ✅ |
| Chỉ trả bài published, active, đã tới ngày phát hành, chưa hết hạn | Test `_visible_domain` loại đủ 5 nhánh draft / archived / inactive / hết hạn / publish_date tương lai | ✅ (test) |
| Không có kết quả → empty state bình thường | "zzz-khong-ton-tai" → hiện "Chưa có bài viết", không lỗi | ✅ |

## WJ-KNW-004 — bài đã gỡ không có thông báo

| Yêu cầu | Đo được | Pass |
|---|---|---|
| Bài draft/archived/inactive/chưa tới ngày/hết hạn → không hiển thị nội dung | Vào thẳng slug bài draft và bài hẹn ngày 2027: không có nội dung bài trong trang trả về | ✅ |
| Chuyển về `/portal/knowledge` | URL cuối `/portal/knowledge?notice=article_gone`, HTTP 200 | ✅ |
| Hiển thị "Bài viết không tồn tại hoặc không còn khả dụng." | Hiện đúng nguyên văn, 2 viewport, cả 2 tình huống | ✅ |
| Không lộ lỗi kỹ thuật / trạng thái nội bộ | Không có `Traceback`/tên model; câu thông báo giống nhau cho mọi lý do (không nói bài đang ở trạng thái nào) | ✅ |
| Áp cho cả route tải đính kèm | `/portal/knowledge/<slug đã gỡ>/attachment/<id>` → cùng thông báo thay vì 404 trần | ✅ (test) |

---

## Hồi quy

| Trang | 391×844 | 1920×1080 |
|---|---|---|
| `/portal` | 200 · tràn ngang 0 · 0 lỗi JS | 200 · 0 · 0 |
| `/portal/order` | 200 · 0 · 0 | 200 · 0 · 0 |
| `/portal/debt` (C2+C3) | 200 · 0 · 0 | 200 · 0 · 0 |

Test tự động: `wujia_knowledge` 14/14 · `wujia_history` 14/14 · `wujia_debt` + `wujia_notification`
(87 test cùng lượt) 0 failed. Build `-u wujia_portal_knowledge --stop-after-init` RC=0, 0 ERROR.

## LIMIT

- Khối "Kiến thức mới" ở **trang chủ portal** vẫn lấy 3 bài published mới nhất theo luật cũ
  (chưa loại bài hẹn ngày phát hành tương lai). Khối đó nằm ở module khác và đang thuộc phạm vi
  cụm **C7** (Home mobile) nên C4 không đụng để tránh sửa hai lần.
- Bài publish có hẹn ngày tương lai nay bị ẩn khỏi Knowledge cho tới đúng ngày — đây là thay đổi
  hành vi theo acceptance của WJ-KNW-003/004 (chủ dự án chốt 15/08/2026).
- Search so khớp trên bản gốc của nội dung; bản dịch ngôn ngữ khác của cùng bài chưa được đánh
  chỉ mục riêng. Portal đang chạy tiếng Việt nên chưa ảnh hưởng.
