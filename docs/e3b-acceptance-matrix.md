# E3b — Bảng nghiệm thu (Pagination `CMP-PGNT-001` / `UI-PAGINATION-001`)

Lượt 2/3 của cụm E3. **Không đóng issue** — issue giữ `Ready for Dev`, chỉ E3c chạy `qa_sync.py`.
Phạm vi lượt này: migrate 5 màn còn lại sang component, làm **ô số dòng/trang chạy thật** ở 4 màn,
và **phân trang thật phía server** cho bảng thành viên ở Thông tin cửa hàng.

- DB đo: `wujia_tea_e3b` (clone từ `wujia_tea_e3a`, kèm chép `data/filestore/`), cổng 8093.
- Run đối chứng: worktree `scratchpad/e3/base_e3b` @ `b9c50cc` → DB `wujia_tea_e3bbase`, cổng 8095.
- Tài khoản đo: `em.hcm` (chủ HCM-01) — không dùng `admin` (bẫy "Pass rỗng", xem §5 bảng E3a).
- Seed: `scripts/seed_e3_pager_demo.py` mở rộng → 45 thông báo · 45 chuyến giao · 45 đổi trả ·
  45 yêu cầu thông tin · 55 bài kiến thức · 25 thành viên (`MARK='SEED-E3'`).

## 1. Phạm vi đã giao — 6 màn / 11 call site

| Màn | PC | Mobile | Ô số dòng/trang | Ghi chú |
|---|---|---|---|---|
| Thông báo | ✅ component | ✅ component | đã có → giữ param `limit` | bỏ `wujia-mnoti-pager` |
| Giao hàng | ✅ | ✅ | **mới, thật** (`page_size`) | trước là `<select disabled>` khoe `10 / trang` trong khi server trả 20 |
| Kiến thức | ✅ (trong `dl_pager`) | ✅ | **mới, thật**, bậc riêng 12/24/48 | PC trước render TOÀN BỘ số trang → nay cửa sổ `1 … 4 5 6 … 20` |
| Đổi trả | ✅ | ✅ | **mới, thật** (`page_size`) | bỏ `MAX_PAGE_SIZE = 100` tự chế |
| Yêu cầu thông tin | ✅ | — (dùng chung) | **mới, thật** | ca BA nêu: trước tự nối `?page=&state=&request_type=` ⇒ rơi `q`/`date_from`/`date_to` |
| Thông tin cửa hàng | ✅ | ✅ | **mới, thật** | **phân trang server-side thật** cho bảng thành viên (trước: pager giả, đổ hết 25 dòng) |

## 2. Đối chiếu `Kết quả mong muốn` của BA

| # | Bullet BA | Kết quả | Bằng chứng |
|---|---|---|---|
| 1 | Một component chung, không mỗi route một kiểu | **Pass** | 11 call site `t-call`; quét 11 route × 6 khổ: **165 nút component, 0 vi phạm**; 3 họ cũ còn lại đều `/portal/exam` (E3c) |
| 2 | PC ≥992: count + page-size + numbered nav | **Pass** | ảnh `portal_delivery@1440`: "Hiển thị 1–20 / 45 chuyến" · ô `20 / trang` · `‹ 1 2 3 ›` |
| 3 | Mobile <992: Prev + "Trang x / y" + Next | **Pass** | ảnh `portal_knowledge@390`: "Trang 1 / 5"; `portal_franchise-information@390`: "Trang 1 / 3" |
| 4 | Visual 36 / radius 10 / gap 8 / 14·20·600 / chevron 16 | **Pass** | `wj_pagination.py` đo hình học 165 nút, 0 lệch |
| 5 | Vùng chạm ≥44 mobile, không tăng chiều cao danh sách | **Pass** | `::before` tuyệt đối; diff cao trang chỉ +9…+17px = đúng chiều cao khối pager mới |
| 6 | Ẩn hẳn khi `totalPages <= 1` | **Pass** | quét 6 khổ: ô 1 trang → `nav=0`, mobile `is-navless` |
| 7 | **Đổi trang không mất filter/sort/keyword** | **Pass** | 7 biến thể có bộ lọc (xem §3) → **0 vi phạm**; ảnh `franchise-information?page=2`: "Người phụ trách" vẫn là chủ tiệm dù chủ tiệm không nằm trong 10 dòng của trang |
| 8 | a11y: `nav[aria-label]`, `aria-current`, tên đọc được, không `href="#"` | **Pass** | kế thừa component E3a + 4 test template |
| 9 | Nút vô hiệu không phải link | **Pass** | `<span aria-disabled="true">` |
| 10 | Không tạo variant theo route | **Pass** | một markup, khác biệt duy nhất là `size_param` + bậc cỡ trang truyền vào |

**10/10 bullet trong phạm vi E3b.** Bullet còn lại (phủ nốt exam/công nợ/catalog + xoá 10 họ CSS cũ)
thuộc E3c.

## 3. Bằng chứng máy

| Phép đo | Kết quả |
|---|---|
| Build `-u` 8 module | RC=0, 0 lỗi |
| Test hồi quy 8 module đụng tới | **0 failed, 0 error / 488** |
| Đột biến 9 mũi (guard E3b mới) | **9/9 đỏ đúng guard của nó** (mỗi mũi làm đỏ 3–6 test — các guard cố ý phủ chồng lên nhau) |
| `wj_pagination.py` quét 10 route chuẩn × 6 khổ | **144 nút, 0 vi phạm, 0 lỗi JS**; 3 họ cũ còn lại **đều ở `/portal/exam`** (E3c) |
| Quét thêm 6 biến thể có bộ lọc × 6 khổ | **99 nút, 0 họ cũ, 0 vi phạm** |
| Danh sách biến thể đã quét | `franchise-information` · `franchise-information?page=2` · `info-request?state=draft&q=abc&date_from=…` · `notification?keyword=SEED-E3&limit=20&page=2` · `delivery?date_from=…&page_size=50` · `return?state=submitted&q=&page=3` · `knowledge?keyword=SEED-E3&page=2&page_size=24` |
| Đổi cỡ trang chạy thật | Kiến thức mặc định 12 → 4 trang / 6 nút; chọn 24 → 2 trang / 4 nút |
| **Run đối chứng** `b9c50cc` vs cây mới | **giống hệt**: HIER 0 · tràn ngang 0 · lỗi JS 0 · histogram tiêu đề 16×6·18×39·22×6·24×3 · nhịp 8×2·12×33 |
| Diff `m_before` ↔ `m_after` (19 ô) | **0 ô mất record**; Δcao +9…+17px nơi pager mới hiện, −9px ở Yêu cầu thông tin (khối cũ cao hơn) |
| Viewport đo | 1440 · 1024 · 992 · 991 · 390 · 360 |

## 4. Lỗi bắt được bằng ẢNH, số đo không thấy (bài học D3e/E3a lặp lần 3)

Chân bảng Thành viên có sẵn nhãn `25 thành viên` bên trái. Sau khi cắm component vào cùng hàng flex
`space-between`, nhãn bị ép còn ~60px và **xuống 2 dòng**, lại **trùng nội dung** với dòng count của
chính component ("Hiển thị 1–10 / 25 thành viên"). Mọi phép đo đều Pass — chỉ ảnh mới thấy.
→ Bỏ nhãn lặp ở nhánh có phân trang; nhánh rỗng giữ `0 thành viên` (không có pager để in count).

## 5. Quyết định Dev tự chốt (ghi lại, không hỏi BA)

1. **Bậc cỡ trang riêng cho Kiến thức: 12/24/48.** Lưới 3 cột nên mặc định là 12; nhét vào bậc chung
   10/20/50 thì ô chọn không có mục nào khớp mặc định ⇒ trình duyệt hiện sai giá trị.
2. **Giữ nguyên tên param từng route** (`limit` ở thông báo, `page_size` ở phần còn lại) — đổi tên là
   vỡ bookmark và vỡ `syncFilterControls` của `wj_ajax_list.js`. (Kế thừa quyết định E3a.)
3. **Một đường đọc cỡ trang duy nhất**: `parse_page_size(value, default, options)` cạnh `build_pager`
   — chỉ nhận giá trị **có trong ô chọn**, rác/thiếu về mặc định route. Không kẹp 1..100 kiểu cũ:
   `?page_size=99` là một truy vấn 99 dòng không ai chọn được từ giao diện (perf-first 1500 user).
4. **Chủ tiệm lấy từ `franchise.main_owner_member_id`**, không `members.filtered(role=='owner')` —
   phân trang đẩy chủ tiệm sang trang 2 là mất luôn tên người phụ trách ở panel trên.
5. **Bỏ `MAX_PAGE_SIZE = 100`** của Đổi trả — thay bằng đường chung ở (3).

## 6. Bẫy gặp trong lượt

| Bẫy | Hậu quả | Cách qua |
|---|---|---|
| `state` là `copy=False` | bản sao thông báo/bài viết rơi về `draft`, portal thấy 0 dòng, pager không render ⇒ **bảng đo "Pass rỗng"** | seed set thẳng `'state': 'published'` + publish 15 thông báo & 40 bài có sẵn |
| Odoo 19 đổi tên `groups_id` → `group_ids` | seed user portal chết `ValueError: Invalid field` | dùng `group_ids` |
| `createdb -T` khi server đang chạy | `source database is being accessed` | tắt server nguồn trước, rồi `cp -r data/filestore/<src> <dst>` |
| `--no-http` vẫn bind cổng | `Address already in use` giữa lúc chạy test | luôn truyền `--http-port` riêng |
| Harness `gap` đọc ở wrapper ngoài khi chỉ có ô cỡ trang (1 trang) | báo oan `gap 12 ≠ 8` | `gap` trả `null` khi không có `.wj-pagination__nav`, judge bỏ qua |
| Harness đột biến bắt tên test bằng `FAIL: (test_\w+)` | Odoo in `FAIL: <Lớp>.<test>` ⇒ bắt ra rỗng, **báo oan cả 9 guard là "không đỏ"** dù thực tế 3–6 test đỏ mỗi mũi | đổi regex `FAIL: [\w.]*?(test_\w+)`, và đọc log theo **offset byte** trước/sau lượt thay vì đoán mốc chuỗi |
| Chạy 2 lượt harness đột biến chồng nhau trên cùng cây mã | lượt sau chụp `before` lúc file đang bị lượt trước phá ⇒ `finally` khôi phục về **bản cũ sai**; `portal_franchise_information.xml` mất luôn call site, 3 test đỏ âm thầm | mỗi lần chỉ 1 lượt; sau đột biến **bắt buộc chạy lại suite sạch** rồi đếm lại call site trước khi commit |
| Guard `test_bac_rieng_cua_tung_man` gọi thẳng `parse_page_size` với bậc viết cứng | đổi bậc trong controller Kiến thức **không làm đỏ test nào** — guard giả | neo test vào chính `wujia_portal_knowledge.controllers.portal.PAGE_SIZE(_OPTIONS)` |
| Harness `_qs()` so cả param rỗng | báo oan "link trang rơi bộ lọc" với `?q=` rỗng mà `build_pager` cố ý bỏ | `_qs()` bỏ param rỗng |

Bốn dòng `Harness …` là **lỗi của bộ đo, sửa harness chứ không sửa code** (luật L7/L9) — riêng dòng
"guard giả" là lỗi thật của test và đã được neo lại.

## 7. Còn lại — E3c

Thi, Công nợ ×2, Catalog, `pc_preview`; xoá 10 họ CSS cũ + test chống tái phát; `defer` module Khảo
sát (luật 08/09); nghiệm thu 12 tiêu chí × 5 viewport → `docs/e3-acceptance-matrix.md`; ledger →
`qa_sync.py` → `Ready for Retest`.
