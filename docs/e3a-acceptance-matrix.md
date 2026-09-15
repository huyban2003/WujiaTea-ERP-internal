# E3a — Bảng nghiệm thu (nền Pagination `CMP-PGNT-001` / `UI-PAGINATION-001`)

Lượt 1/3 của cụm E3. **Không đóng issue** — issue giữ `Ready for Dev`, chỉ E3c chạy `qa_sync.py`.
Phạm vi lượt này: dựng nguồn pager duy nhất + component + guard, migrate 2 route mẫu.

- DB đo: `wujia_tea_e3a` (clone từ `wujia_tea_e2b`, có cài Khảo sát như UAT), cổng 8087.
- Tài khoản đo: `em.hcm` (chủ HCM-01) — **không** dùng `admin`, lý do ở mục Bẫy.
- Seed: `scripts/seed_e3_pager_demo.py` — 45 ticket hỗ trợ + 40 bài kiến thức (`MARK='SEED-E3'`).

## 1. Đối chiếu `Kết quả mong muốn` của BA

| # | Bullet BA | Kết quả | Bằng chứng |
|---|---|---|---|
| 1 | Một component chung, không mỗi route một kiểu | **Pass** (trong phạm vi lượt) | `wj_pagination.xml`; 2 route mẫu gọi `t-call`, 0 họ class cũ còn lại (`test_khong_con_ho_pager_cu`) |
| 2 | PC ≥992: count + page-size + numbered nav | **Pass** | đo 1440/1024/992 → 4–5 nút/route; ảnh `history_pc_pager.png` |
| 3 | Mobile <992: Prev + "Trang x / y" + Next | **Pass** | đo 991/390/360 → đúng 2 nút; ảnh `support_mb_pager.png` ("Trang 2 / 3") |
| 4 | Visual 36px / radius 10 / gap 8 / 14·20·600 / chevron 16 | **Pass** | token `_variables.css` + đo hình học 39 nút, 0 vi phạm |
| 5 | Vùng chạm ≥44 trên mobile, **không** tăng chiều cao danh sách | **Pass** | `::before` `position:absolute` + `--wj-pgn-touch`; đo cả visual 36 lẫn hộp chạm 44 |
| 6 | Ẩn hẳn khi `totalPages <= 1`, không để khoảng trắng | **Pass** | `/portal/support?state=new` (12 dòng, 1 trang) → `nav=0`; mobile thêm `is-navless` |
| 7 | Đổi trang không mất filter/sort/keyword | **Pass** | `?q=SEED-E3` → mọi link đều `?q=SEED-E3&page=N`; query-string lấy từ request hiện tại |
| 8 | a11y: `nav[aria-label]`, `aria-current`, nút có tên đọc được, không `href="#"` | **Pass** | 4 test template; đo runtime `aria-current=['2']` |
| 9 | Nút vô hiệu không phải link | **Pass** | render `<span aria-disabled="true">`, ngoài tab order |
| 10 | Không tạo variant theo route | **Pass** | một markup, hai bố cục bằng CSS breakpoint |

**10/10 bullet trong phạm vi E3a.** Hai bullet còn lại của issue (phủ hết 10 họ pager toàn portal; xoá
CSS cũ) thuộc E3b/E3c theo kế hoạch đã chốt.

## 2. Bằng chứng máy

| Phép đo | Kết quả |
|---|---|
| Test mới | 26/26 xanh (25 test E3 + 1 guard card) |
| Hồi quy 4 module đụng tới | **0 failed, 0 error / 483** |
| Run đối chứng (worktree `scratchpad/e3/base`, commit `8c458d1`) | trước: 2 failed, 3 error / 275 — sau: cùng tên đỏ, **0 đỏ mới**, +25 test |
| Đột biến | **17/17 đỏ**, mỗi guard đỏ đúng test của nó |
| Đo Playwright `wj_pagination.py` | 12/12 ô sạch — 39 nút, 0 họ cũ, 0 vi phạm, 0 lỗi JS |
| Viewport đo | 1440 · 1024 · 992 · 991 · 390 · 360 |

## 3. Lỗi bắt được bằng ẢNH, số đo không thấy (bài học D3e lặp lại)

`.wujia-content-card { height: 100% }` khoá card bằng chiều cao khung nhìn. Màn Hỗ trợ trước đây ít
dữ liệu nên không lộ; seed >1 trang (20 dòng) làm bảng cao 1143px tràn khỏi card cao 950px, **đè lên
pager**, và 214px nội dung bị `.app-content{overflow:hidden}` cắt mất, cuộn hết cỡ vẫn không tới.

- Không phải do E3a: gỡ pager bằng JS thì card vẫn khoá 950 và bảng vẫn tràn.
- Sửa tại gốc: `height` → `min-height: 100%` (giữ nguyên ý "card ngắn lấp đầy cột" của dashboard).
- Kiểm 5 màn dùng class này (`/portal`, hỗ trợ, kiến thức, đổi trả, yêu cầu thông tin): 0 card tràn,
  0 px bị cắt, trang chủ vẫn giữ 4 card bằng chiều cao.
- Guard `test_content_card_khong_khoa_chieu_cao` + đột biến đỏ đúng nó.

## 4. Quyết định Dev tự chốt (ghi lại, không hỏi BA)

1. **Giữ nguyên tên param page-size của từng route** (`page_size` ở lịch sử, `limit` ở thông báo/thi).
   Đổi tên là vỡ bookmark và vỡ `syncFilterControls` của `wj_ajax_list.js`; component đọc theo
   `size_param` truyền vào.
2. **`totalPages <= 1` mà vẫn cần ô page-size**: PC hiện khung (yêu cầu `UI-PC-BASE-005`), mobile ẩn
   hẳn bằng `is-navless` — nếu không sẽ còn một khung rỗng cao 16px trên điện thoại.
3. **`urls` chỉ dựng cho số trang thật sự hiện**, không dựng cho toàn bộ trang — 500 trang là 500 URL
   mỗi request, trái luật perf-first 1500 user.
4. **`urllib.parse.urlencode` thay `werkzeug.urls.url_encode`** — hàm werkzeug bị bỏ từ 2.3.

## 5. Bẫy gặp trong lượt (để lượt sau khỏi mất giờ)

| Bẫy | Hậu quả | Cách qua |
|---|---|---|
| `wujia_tea_mt4` hỏng sẵn (`column sl.is_export does not exist`) | registry không load | đổi DB nền sang `wujia_tea_e2b` |
| `createdb -T` không chép filestore | bundle JS 500, JS chết im | `cp -r data/filestore/<src> <dst>` |
| `dbfilter = ^wujia_tea_19$` trong `config/odoo.conf` | HTTP vào **nhầm DB**, login báo sai mật khẩu dù user đúng | chạy kèm `--db-filter='^wujia_tea_e3a$'` |
| Seed bằng `admin` | `/portal/support` lọc `created_by_id = user` ⇒ 0 dòng, pager không render, bảng đo "Pass rỗng" | seed đúng chủ cửa hàng + `portal_visible = True` |
| `--no-http` vẫn chiếm cổng | `Address already in use` | dùng `--http-port=8091` |
| Ảnh `full_page` + phần tử `position: fixed` | thanh tab mobile trông như đè lên pager | chụp ảnh **viewport thật** rồi `elementFromPoint` để kết luận (đã kiểm: không bị che) |

Hai lỗi của chính bộ đo (sửa harness, không sửa code): `_qs()` trả cả path khi URL không có `?` (báo
oan "link trang rơi bộ lọc" 6 ô); `gap` đọc nhầm ở flex ngoài (12px) thay vì `.wj-pagination__nav` (8px).

## 6. Còn lại của cụm

- **E3b**: thông báo, giao hàng, kiến thức, đổi trả, yêu cầu thông tin (PC+mobile), hỗ trợ mobile;
  **gỡ hẳn** 2 pager giả ở `portal_franchise_information.xml:137,150`; chuẩn hoá `m_pager` của giao hàng.
- **E3c**: thi, công nợ ×2, catalog, `pc_preview`; xoá 10 họ CSS cũ + test chống tái phát;
  `defer` module Khảo sát; nghiệm thu 12 tiêu chí × 5 viewport → `docs/e3-acceptance-matrix.md`;
  ledger → `qa_sync.py` → `Ready for Retest`.
