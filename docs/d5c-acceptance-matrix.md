# D5c — bảng nghiệm thu DataList lượt 2 (họ bảng PC `wj-pc-table`)

**Ngày:** 2026-09-07 · **Cơ sở:** `d5d2335` (D5b) · **Spec:** `CMP-DL-001`, `UI-DATALIST-001` (STT 126)
· **Phạm vi:** 3 call site — `/portal/purchase-history` · `/portal/delivery` · `/portal/notification`.

D5a xếp đây là **lượt nặng nhất cụm**, và đúng vì một lý do cơ chế chứ không phải số: row 58 của
họ này đến từ `height` trên `<td>` với `padding: 0 22px`, tức chiều cao do **thuộc tính bảng**
quyết chứ không do đệm. Đổi con số là không đủ — phải đổi hẳn sang `height` trên `<tr>` +
padding thật trên `<td>`, đúng cơ chế D5b đã chứng minh.

---

## 1. Đã làm

| | |
|---|---|
| Call site | 3/3 chuyển sang `t-call="wujia_portal_layout.wj_data_list"`, lớp cũ giữ qua `dl_table_class` |
| CSS | 9 rule hình học của `.wj-pc-table` khoá bằng `:not(.wj-data-table)` ⇒ `.wj-data-table` là chủ sở hữu DUY NHẤT dáng của 3 bảng đã migrate. **Cố ý KHÔNG khoá** 3 rule `.wj-pc-td--code/--muted/--amount` (biến thể ô, không phải hình học) |
| Semantic | `th[scope="col"]` cho **20/20** ô tiêu đề (7 + 8 + 5) |
| Guard pager | history + notification **tách đôi**; delivery `page_total` → `page_count > 1` |
| Component | thêm tham số `dl_table_id` (cộng thêm, hợp đồng D5b không đổi) để call site giữ `id` cũ của `<table>` |
| Kèm | skeleton loading của delivery về `52px` / `10px 16px` cho khớp hàng thật; vá hover bị zebra nuốt ở bảng notification |
| `-u` | `wujia_portal_layout,wujia_portal_purchase_history,wujia_portal_delivery,wujia_portal_notification` — RC=0, **0 ERROR** (kiểm cả file log thật, bẫy L15) |
| Version | layout `19.0.39.0.0 → 19.0.40.0.0` · history `19.0.3.8.0` · delivery `19.0.3.10.0` · notification `19.0.2.10.0` · `_pc_components.css?v=1220 → 1230` |

Môi trường: DB copy cô lập **`wujia_tea_d5b`** (cổng **8077**, `--db-filter '^wujia_tea_d5b$'`) —
không đụng `wujia_tea_19`/8019. Trước khi đo đã so `latest_version` ↔ `__manifest__.py` của
**từng** module: 21/21 khớp (bài học D5a #4). Mốc "trước" đo lại ra đúng con số D5b để lại
(thiếu `th[scope]` 18/27 · header `50×18 · 44×9`) ⇒ môi trường nhất quán, không phải mốc trôi.

## 2. Số đo trước–sau — 9 lượt đo bảng (3 call site × 3 khổ có bảng)

| Route | Khổ | `th[scope]` | Header (BA 44) | Row (BA ≥52) | Cell padding (BA `10px 16px`) |
|---|---:|---|---|---|---|
| `/portal/purchase-history` | 1440 | **0/7 → 7/7** | 50 → **44** | 58 → **54–55** | `0 22px` → **`10px 16px`** |
| `/portal/purchase-history` | 1024 · 992 | **0/7 → 7/7** | 50 → **44** | 58–68.5 → **55–89** | `0 22px` → **`10px 16px`** |
| `/portal/delivery` | 1440 · 1024 · 992 | **0/8 → 8/8** | 50 → **44** | 58 → **54–55** | `0 22px` → **`10px 16px`** |
| `/portal/notification` | 1440 · 1024 · 992 | **0/5 → 5/5** | 50 → **44** | 58 → **58–77** | `0 22px` → **`10px 16px`** |

Tổng bộ đo: bảng thiếu `th[scope]` **18/27 → 9/27** (9 lượt còn lại là exam · khảo sát · công nợ,
thuộc D5g/D5h); header `50×18 → 44×18`; cell padding `0 22px ×18 → 10px 16px ×18`.

Ở 3 khổ `991/390/360` cả 6 khổ đều **0 bảng render** như trước — ngưỡng 992/991 không bị đụng
(D5a đã kết luận chỗ này đúng sẵn).

**Vì sao row NỞ ra chứ không co lại.** Đây là điều dễ đọc nhầm thành hồi quy: `0 22px` là đệm dọc
**bằng 0**, nên 58px cũ là con số cứng do `height` áp lên `<td>`, và mọi hàng — một dòng hay hai
dòng — đều bị ép đúng 58. Padding `10px 16px` của BA cộng thật 20px đệm dọc, nên hàng một dòng ra
54–55 (thấp hơn 58) còn hàng hai dòng của notification/history được **nở ra** 77 và 89 thay vì bị
ép. Hàng nở là hàng trước đây đang bị nén; đổi lại là đúng ý spec, không phải phình.

## 3. Acceptance #9 — số record thấy trong viewport

**27/27 ô đo, 0 ô mất record, 0 ô giảm.** `wj_datalist.py` được bổ sung trường
`rowsInViewport` (đếm hàng có mép trên nằm trong viewport) — cộng thêm, không đổi trường cũ nên
`d5-datalist-before.json` của D5a vẫn so được.

Chiều cao trang: delivery **1354 → 1247** (−107, đặc hơn) · notification 1092 → 1113 (+21, do
hàng hai dòng được nở) · purchase-history không đổi (3 bản ghi, chưa chạm đáy khung).

## 4. Nhịp trong card — RULE 1 + RULE 2 chạy lại

| | D5b công bố | D5c sau |
|---|---|---|
| RULE 1 `HIERARCHY` vi phạm | 0 | **0** |
| RULE 2 histogram cỡ tiêu đề card | `14.7×10 · 16×8 · 18×39 · 22×6 · 24×3` | **giống hệt** |
| Nhịp header→body | `8×2 · 12×33` | **giống hệt** |
| Tràn ngang · lỗi JS · redirect ngầm · non-200 | 0 · 0 · 0 · 0 | **0 · 0 · 0 · 0** |

Phép so là chính hai con số D5b công bố, **không** phải `d5-baseline.json`: baseline đó chụp
TRƯỚC khi bổ seed nên chênh lệch chiều cao ở đó là do dữ liệu (delivery mobile 1 → 14 bản ghi),
không do lượt này.

## 5. Guard pager — chứng minh trên trang chạy, không chỉ trên file

BA đòi `page_count > 1`, nhưng `UI-PC-BASE-005` cố ý để `> 10` vì **ô chọn 10/20/50 nằm chung
khối**: ẩn cả khối thì user chọn 50 rồi còn 20 bản ghi sẽ không bấm về 10 được. Chủ dự án chốt
**tách đôi** — ô chọn số dòng/trang giữ guard `> 10`, riêng nút điều hướng theo BA.

| URL | page_count | Ô chọn số dòng/trang | Nút điều hướng |
|---|---:|---|---|
| `/portal/notification` (30 bản ghi, 10/trang) | 3 | **còn** | **5 nút** |
| `/portal/notification?limit=50` (30 bản ghi, 1 trang) | 1 | **còn** ✅ | **0** ✅ |
| `/portal/delivery` (14 chuyến, `PAGE_SIZE=20`) | 1 | — | **cả khối biến mất** ✅ |

Delivery là lỗi BA nêu, nay đo được: trước đây in ra `Hiển thị 1–14 / 14 chuyến · 10 / trang · ‹ 1 ›`
— một pager một trang, kèm ô "10 / trang" `disabled` nói sai số thật (`PAGE_SIZE` là 20).

## 6. Trạng thái dữ liệu — 6 lượt kiểm sau khi đổi cấu trúc

| Trạng thái | Kết quả |
|---|---|
| history empty sau lọc | ✅ hiện empty, ẩn bảng |
| history **filter_error** | ✅ **không** hiện empty (2 thông điệp mâu thuẫn), giữ đúng chủ ý cũ |
| delivery loading skeleton | ✅ 7 hàng, cao **52** khớp hàng thật (trước là 58) |
| delivery empty · error | ✅ · ✅ |
| notification empty | ✅ |

## 7. Guard — chứng minh bằng mutation

23 test (`--test-tags wujia_data_list_d5`), 0 failed / 0 error. Mỗi phép thay neo vào **cả
selector**, hoàn tác bằng **ảnh chụp byte lấy ngay trước khi thay** + đối chiếu `sha256`
(không `git checkout` — bẫy D5b #2).

| Mutation | Test đỏ |
|---|---|
| Gỡ `scope="col"` của **một** `th` trong delivery | `test_moi_th_deu_co_scope` |
| Nới guard nút điều hướng notification về `pager` | `test_pager_dieu_huong_guard_page_count` |
| Trả guard delivery về `page_total` | `test_pager_delivery_khong_hien_khi_mot_trang` |
| Bỏ `:not(.wj-data-table)` ở `.wj-pc-table … tbody td` | `test_pc_mot_chu_so_huu_dang` + `test_bang_khong_migrate_giu_nguyen_50_58` |
| Đổi token `--wj-pc-table-row-h` 58 → 52 | `test_bang_khong_migrate_giu_nguyen_50_58` |
| Gỡ `dl_table_id` ở call site notification | `test_noti_giu_lop_va_id_cu` |
| Đổi lớp `wj-pc-noti-row` trên `<tr>` | `test_noti_giu_lop_va_id_cu` |
| Trả skeleton delivery về 58 / `0 22px` | `test_skeleton_delivery_khop_row_that` |
| Gỡ rule hover nâng độ đặc hiệu của notification | `test_hover_noti_khong_bi_zebra_nuot` |
| Gỡ `t-att-id="dl_table_id"` khỏi component | `test_component_chuyen_duoc_id_bang` |

## 8. Phép kiểm quan trọng nhất: 12 bảng KHÔNG migrate

`wj-pc-table` xuất hiện **15 lần** trong mã nguồn, chỉ **5** là danh sách record. Khoá
`:not(.wj-data-table)` sai tay là 12 bảng còn lại đổi dáng theo. Đo lại sau `-u`:

| Bảng không thuộc lượt này | Header | Row | Padding |
|---|---:|---:|---|
| `/portal/exam` `wj-exam-pc-list-table` | 50 | 68 | `0 22px` |
| `/portal/inspection` | 50 | 58 | `0 22px` |
| `/portal/debt` `wj-debt-pc-table` | 50 | 58 | `0 22px` |
| `/portal` · `/portal/return` · `/portal/support` (D5b) | 44 | 52–89 | `10px 16px` |

**Không ô nào đổi** so với trước lượt này.

## 9. Ba bẫy đã trả giá trong phiên

1. 🔴 **`pkill -f "http-port=8077"` khớp luôn dòng lệnh đang chạy ⇒ tự giết shell** (exit 144),
   và cú `-u` phía sau chưa từng chạy dù tôi tưởng đã chạy. Dừng server phải theo **PID**
   (`ss -ltnp | grep :8077`), không theo pattern chứa chính chuỗi mình đang gõ.
2. 🔴 **Mutation thay bằng chuỗi RỖNG thì phép thay ngược phá file.** `replace('', a, 1)` chèn
   mảnh vào **đầu file** — `portal_notification.xml` mở đầu bằng một thẻ `<t t-set>` đứng trước
   cả khai báo XML. Đối chiếu `sha256` bắt được ngay, nhưng bài học là: hoàn tác phải là **ghi
   lại ảnh chụp byte**, không phải phép thay ngược, khi một vế là rỗng.
3. 🔴 **`contains()` trong XPath là guard chứng-minh-rỗng khi tên lớp có biến thể BEM.**
   `tr[contains(@t-attf-class,"wj-pc-noti-row")]` vẫn khớp sau khi đã đổi tên lớp gốc, vì chuỗi
   con `wj-pc-noti-row--unread` nằm trong nhánh `#{...}` của cùng thuộc tính. Mutation M7 chạy ra
   **0 test đỏ** và suýt được ghi là guard đạt. Phải neo vào **token đứng đầu**
   (`assertRegex(..., r'^wj-pc-noti-row(\s|$)')`). Cùng họ với bẫy D5b #3, nhưng ở tầng XPath
   chứ không phải `sed`.

Thêm một điều **chính lượt này tạo ra và tự bắt được bằng đo**: `.wj-data-table tbody tr:hover`
và zebra `.wj-pc-noti-table tbody tr:nth-child(even)` **cùng độ đặc hiệu (0,2,2)**, nên hover chỉ
ăn ở hàng lẻ. Trước migrate `.wj-pc-table` không có rule hover nào nên không ai thấy; sau migrate
thì hàng chẵn "chết" hover — bất nhất do mình gây ra. Vá bằng một rule nâng độ đặc hiệu
`.wj-data-table.wj-pc-noti-table tbody tr:hover` (0,3,2). Số đo không bắt được chỗ này; chỉ có
phép dò `getComputedStyle` sau `hover` mới bắt.

## 10. LIMIT

1. **`/portal/purchase-history` chỉ có 3 bản ghi** trên DB dev (seed D5b đẻ ticket/bù hàng/hoá
   đơn/khảo sát/chuyến giao, **không** đẻ đơn bán). Ba con số dáng đo được đủ, nhưng pager của
   route này **không hiện** ở mốc này ⇒ guard tách đôi của nó chứng minh bằng test + mutation và
   bằng notification (30 bản ghi), không bằng ảnh chạy của chính nó.
2. **Hàng hai dòng vượt băng 64–72 của BA**: notification tới **77**, purchase-history @1024 tới
   **89**. Đó là nội dung tự xuống dòng (tiêu đề + tóm tắt), ép trần lại là cắt mất dữ liệu
   nghiệp vụ. Cùng loại với `/portal/support` **88–89** mà D5b đã nghiệm thu theo cột `≥52`.
3. **DataState của `/portal/delivery` nằm ở tầng TRÊN DataList** — empty/loading/error do
   `view_state` quyết ở controller, là khối anh em của bảng. Không gò vào `dl_state` vì làm vậy
   là đổi luồng trạng thái ngoài phạm vi BA.
4. **Pagination vẫn NGOÀI card** ở cả 3 call site, y như LIMIT #1 của D5b.
5. Đo trên **DB copy `wujia_tea_d5b`**, chưa soi UAT — deploy dồn một lượt cuối cụm D5.
6. `/portal/reports/orders` vẫn 500 trên máy Linux (PostgreSQL không biết bí danh `Asia/Saigon`).
   Việc của cụm **R3**, đã ghi ở D5a, không thuộc D5.

**Tiến độ cụm: 6/31 call site.** Kế tiếp: **D5d** — danh sách PC không phải bảng
(`li.wujia-content-card-row`): 3 khối preview `/portal` + `/portal/knowledge`.
