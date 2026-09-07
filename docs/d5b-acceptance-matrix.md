# D5b — bảng nghiệm thu DataList lượt 1 (nền `wj_data_list` + họ `wujia-content-card-table`)

**Ngày:** 2026-09-07 · **Cơ sở:** `3c9d9d1` · **Spec:** `CMP-DL-001`, `UI-DATALIST-001` (STT 126)
· **Phạm vi:** 3 call site — `/portal` top sản phẩm · `/portal/return` · `/portal/support`.

Đúng khuôn D4b: lượt đầu chọn theo **đo được**, không theo số file, để hiệu chỉnh chính bảng đo
trước khi đụng họ lớn (D5c).

---

## 1. Đã làm

| | |
|---|---|
| Seed | `scripts/seed_d5_datalist_demo.py` — 52 ticket · 28 phiếu bù hàng · 14 hoá đơn có `franchise_id` · 14 phiếu khảo sát · 14 chuyến giao cho **HN-01** |
| Component mới | `wujia_portal_layout/views/wj_data_list.xml` — `DataViewport + DataItem(s) + DataState + Pagination`, 3 biến thể `table`/`compact-row`/`detail-card` |
| CSS | `.wj-data-table` là **chủ sở hữu duy nhất** dáng bảng danh sách; rule cũ `.wujia-content-card-table` bị khoá bằng `:not(.wj-data-table)` |
| Call site | 3/3 chuyển sang `t-call`, lớp cũ giữ qua `dl_table_class` |
| Semantic | `th[scope="col"]` cho **19/19** ô tiêu đề (4 + 7 + 8) |
| Guard pager | `page_count > 1` ở return + support — ghim bằng test, cả hai pager nay **thật sự chạy** (2 và 3 trang) |
| `-u` | `wujia_portal_layout,wujia_portal_base,wujia_portal_return,wujia_sale,wujia_portal_support` — RC=0, 0 ERROR |
| Version | layout `19.0.38.0.0 → 19.0.39.0.0` · base `19.0.7.8.0` · return `19.0.2.12.0` · support `19.0.3.15.0` · `_components.css?v=1220 → 1230` |

Môi trường: DB copy cô lập **`wujia_tea_d5b`** (cổng **8077**, `--db-filter '^wujia_tea_d5b$'`) —
không đụng `wujia_tea_19`/8019. Trước khi đo đã so `latest_version` ↔ `__manifest__.py` của
**từng** module: 21/21 khớp `3c9d9d1`, không cần cú `-u` đồng bộ (bài học D5a #4).

## 2. Số đo trước–sau — 9 lượt đo bảng (3 call site × 3 khổ có bảng)

| Route | Khổ | `th[scope]` | Header (BA 44) | Row (BA ≥52) | Cell padding (BA `10px 16px`) |
|---|---:|---|---|---|---|
| `/portal` | 1440 · 1024 · 992 | **0/4 → 4/4** | 46 → **44** | 45–46 → **52** | `14px 20px` → **`10px 16px`** |
| `/portal/return` | 1440 | **0/7 → 7/7** | 46 → **44** | 60–61 → **52–53** | `14px 20px` → **`10px 16px`** |
| `/portal/return` | 1024 · 992 | **0/7 → 7/7** | 46 → **44** | 62–63 → **54–55** | `14px 20px` → **`10px 16px`** |
| `/portal/support` | 1440 | **0/8 → 8/8** | 46 → **44** | 62–63 → **54–55** | `14px 20px` → **`10px 16px`** |
| `/portal/support` | 1024 · 992 | **0/8 → 8/8** | 46 → **44** | 113–114 → **88–89** | `14px 20px` → **`10px 16px`** |

Tổng bộ đo: bảng thiếu `th[scope]` **27/27 → 18/27** (9 lượt còn lại là họ `wj-pc-table` của D5c);
header `46×9 → 44×9`; cell padding `14px 20px ×9 → 10px 16px ×9`.

**Row cao 52 khai bằng `height` trên `<tr>`** — trên bảng, `height` hành xử như *tối thiểu*: dòng
một hàng chữ đúng 52, dòng nhiều hàng tự nở (54–55, 88–89). Padding vẫn đúng `10px 16px`, khác hẳn
cơ chế `height` cứng của `wj-pc-table` mà D5c sẽ phải gỡ.

## 3. Acceptance #9 — số record thấy trong viewport

**0 ô mất record**, và 6 ô **tăng** vì row đặc hơn:

| Route | 1440 | 1024 | 992 |
|---|---|---|---|
| `/portal/return` | 30 → **31** | 31 → **33** | 31 → **33** |
| `/portal/support` | 30 → **31** | 28 → **29** | 28 → **29** |

`/portal` không đổi: sàn 52 kéo row từ 45 lên nhưng bảng preview chỉ 2 dòng nên không ô nào tụt.
⇒ Rủi ro "sàn 52 đá nhau với acceptance #9" mà phiên này lường trước **không xảy ra**; không cần
ghi LIMIT, cũng không cần hỏi BA.

## 4. Nhịp trong card — RULE 1 + RULE 2 chạy lại

| | trước | sau |
|---|---|---|
| RULE 1 `HIERARCHY` vi phạm | 0 | **0** |
| RULE 2 histogram cỡ tiêu đề card | `14.7×10 · 16×8 · 18×39 · 22×6 · 24×3` | **giống hệt** |
| Nhịp header→body | `8×2 · 12×33` | **giống hệt** |
| Tràn ngang · lỗi JS · redirect ngầm | 0 · 0 · 0 | **0 · 0 · 0** |
| Chiều cao trang (60 ô) | — | **không ô nào đổi** |

Nhịp 12px mà D3/D4 vừa hội tụ **không bị đổi row làm lệch** — viewport không mang margin dọc,
nhịp vẫn do `gap` của card quyết định.

## 5. Guard — chứng minh bằng mutation, không bằng `assertIn`

15 test (`--test-tags wujia_data_list_d5`), 0 failed / 0 error. Gỡ từng thứ ra, **đúng** test đó đỏ:

| Mutation | Test đỏ |
|---|---|
| Gỡ `scope="col"` của **một** `th` trong support | `test_moi_th_deu_co_scope` |
| Nới guard pager return về `page_count > 0` | `test_pager_chi_hien_khi_nhieu_hon_mot_trang` |
| Header `44px → 46px` | `test_header_cao_44` |
| Gỡ sàn `height: 52px` của `tbody tr` | `test_row_san_52` |
| Cell padding `10px 16px → 14px 20px` | `test_cell_padding_10_16` |
| Bỏ `:not(.wj-data-table)` ở **một** rule cũ | `test_mot_chu_so_huu_dang` |
| Component render viewport cả khi rỗng | `test_datastate_thay_cho_viewport_khi_rong` |
| Đưa Pagination vào trong viewport | `test_pager_nam_ngoai_viewport` |
| Thôi chuyền lớp cũ qua `dl_table_class` | `test_lop_cu_cua_call_site_duoc_giu` |

## 6. Ba bẫy đã trả giá trong phiên

1. 🔴 **Odoo 19 BỎ `values['0']` khi gọi `_render`** (chỉ cảnh báo, không lỗi). Bốn test đầu "đỏ
   vì sản phẩm sai" hoá ra đỏ vì **slot không tồn tại**: template render ra khung rỗng. Slot chỉ
   sống khi đi qua thân của `t-call`, nên test phải dựng một view `qweb` tạm rồi render nó — đúng
   như call site thật. Cùng họ với bài học B3a: đừng giả lập seam, hãy đi qua seam.
2. 🔴 **`git checkout <file>` để hoàn tác một mutation đã xoá luôn cả lượt migrate của file đó.**
   `portal_support.xml` mất sạch phần D5b mà test kế tiếp chỉ báo "thiếu scope" — suýt đọc thành
   lỗi sản phẩm. Hoàn tác mutation phải bằng phép thay ngược đúng chuỗi đã đổi, không bằng `git`.
3. 🔴 **Mutation sai chỗ cho ra "guard xanh giả".** `sed '0,/height: 44px;/'` trúng rule đầu tiên
   trong file (nav item), không trúng `.wj-data-table thead th` — chạy xong 0 test đỏ và suýt kết
   luận guard header là guard giả. `height: 44px` xuất hiện **10 lần** trong `_components.css`:
   mutation phải neo vào **cả selector**, không chỉ giá trị.

Thêm một xác nhận cũ: `/portal/reports/orders` **vẫn 500** trên máy Linux vì PostgreSQL không
biết bí danh `Asia/Saigon` (`anh.owner` mang tz đó). Đúng như D5a ghi — việc của cụm **R3**,
không thuộc D5.

## 7. LIMIT

1. **Pagination vẫn nằm NGOÀI card** ở cả 3 call site: component đã có chỗ đứng `dl_pager`, nhưng
   chuyển pager vào trong card là **đổi dáng ngoài phạm vi BA** ⇒ để nguyên, `dl_pager` chờ lượt
   nào BA yêu cầu pager trong card.
2. **Trạng thái `error` ("thông báo + Thử lại") vẫn chưa tồn tại** ở route nào — `dl_state` đã có
   chỗ, nội dung là việc của `CMP-ES-001`, không thuộc D5b.
3. `/portal/info-request` còn dùng rule cũ `.wujia-content-card-table:not(.wj-data-table)` —
   cố ý, gỡ ở lượt dọn cuối cụm D5.
4. Đo trên **DB copy `wujia_tea_d5b`**, chưa soi UAT (deploy dồn cuối cụm D5 theo chốt của chủ dự án).

**Tiến độ cụm: 3/31 call site.** Kế tiếp: **D5c** — họ `wj-pc-table` (purchase-history · delivery
· notification), nặng nhất vì row 58 hiện do `height` chứ không do padding.
