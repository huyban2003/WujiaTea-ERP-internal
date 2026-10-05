# Chuỗi tiếng Việt viết cứng trong source (quét 05/10/2026)

**Kết quả:** 2 659 chuỗi tiếng Việt viết cứng (không tính comment, docstring, `i18n/`, thư viện `vendors/`) + 945 chuỗi trong
`tests/`. Code team ≈ 2 375 · code Thái 284. Đây là lý do portal không dịch được sang EN/ZH/TH: Odoo chỉ dịch được khi câu gốc
là tiếng Anh và bản dịch nằm trong `.po` — câu gốc tiếng Việt thì user tiếng Anh/Trung/Thái vẫn thấy tiếng Việt.

- Danh sách từng chuỗi: `docs/vn-hardcode-inventory.csv` (module, chủ, loại, file, dòng, câu).
- Quét lại: `python3 scripts/qa/vn_hardcode_scan.py [--csv out.csv]` (dùng làm thước nghiệm thu: về 0 với code team).
- UAT (đọc 05/10): ngôn ngữ bật `en_US, th_TH, vi_VN` (**chưa bật zh_CN**); user portal 6 vi_VN + 1 en_US; internal 1 en_US.
- `wujia_portal_layout/static/assets/js/lang.js` là code chết từ template đầu tư cũ ("investment package", "withdraw wallet") nhưng
  vẫn nạp ở `views/assets.xml:119` ⇒ xoá ở V1.

## Loại chuỗi và cách sửa

| Loại | Số | Ví dụ | Cách sửa |
|---|---|---|---|
| `qweb_text` | 1 529 | `<span>Tạm tính</span>` | Câu gốc → tiếng Anh; VN vào `vi_VN.po` (msgstr = câu cũ) |
| `qweb_attr` | 166 | `placeholder="Tìm kiếm…"` | Như trên (Odoo dịch `placeholder/title/aria-label/alt/string`) |
| `qweb_expr` | 98 | `t-out="x or 'Chưa có'"` | Tách câu ra `<t t-set>` hoặc truyền từ controller qua `_()` |
| `py_literal` | 531 | `ROLE_LABELS`, thông báo controller | `_()` lúc chạy / `_lt()` cho hằng module |
| `py_gettext` | 168 | `_('Vui lòng …')` | Đổi msgid sang tiếng Anh, VN vào `.po` |
| `js_literal` | 133 | `alert('Lỗi:')` | Portal Vuexy không có `_t` ⇒ cần chốt cơ chế (V0) |
| `data_record` | 33 | mail template, cron, menu | Câu gốc tiếng Anh + `.po` (bản ghi `noupdate` cần migration) |
| `py_field` | 1 | `string='Mã tiêu chí'` | Câu gốc tiếng Anh |
| `test` | 945 | assert theo nhãn VN | Đổi theo khi sửa nguồn (assert với `lang=vi_VN` hoặc theo key) |

## Theo module (đã trừ test)

| Chủ | Module | qweb_text | qweb_attr | qweb_expr | data_record | py_gettext | py_field | py_literal | js_gettext | js_literal | css | test | Tổng (trừ test) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| team | `wujia_portal_base` | 242 | 8 | 6 | 17 | 8 |  | 97 |  | 4 |  | 326 | **382** |
| team | `wujia_portal_exam` | 192 | 21 | 6 |  | 2 |  | 67 |  | 57 |  | 60 | **345** |
| team | `wujia_portal_layout` | 157 | 31 | 17 |  | 20 |  | 4 |  | 30 |  | 147 | **259** |
| team | `wujia_portal_sale` | 106 | 16 | 14 |  |  |  | 50 |  | 15 |  | 36 | **201** |
| team | `wujia_portal_debt` | 151 | 17 | 6 |  |  |  | 19 |  | 3 |  | 48 | **196** |
| team | `wujia_portal_return` | 135 | 8 | 6 |  |  |  | 17 |  | 2 |  | 64 | **168** |
| team | `wujia_portal_support` | 85 | 9 | 2 |  |  |  | 16 |  |  |  | 13 | **112** |
| team | `wujia_portal_purchase_history` | 76 | 2 | 10 |  |  |  | 11 |  |  |  | 43 | **99** |
| team | `wujia_portal_delivery` | 78 | 2 | 3 |  |  |  | 10 |  |  |  | 14 | **93** |
| team | `wujia_portal_notification` | 54 | 3 | 6 |  |  |  | 14 |  | 9 |  | 24 | **86** |
| team | `wujia_portal_info_request` | 58 | 6 | 1 |  | 7 |  | 13 |  |  |  | 4 | **85** |
| team | `wujia_portal_report` | 42 | 4 | 2 |  | 2 |  | 15 |  | 4 |  | 3 | **69** |
| team | `wujia_return` |  | 3 |  | 10 | 50 |  | 6 |  |  |  | 12 | **69** |
| team | `wujia_exam` |  | 6 |  |  | 49 |  | 8 |  |  |  | 15 | **63** |
| team | `wujia_portal_knowledge` | 35 | 2 | 6 |  |  |  | 3 |  |  |  | 16 | **46** |
| team | `wujia_notification` |  | 3 |  | 5 | 6 |  | 13 |  |  |  | 35 | **27** |
| team | `wujia_sale` |  |  |  |  | 12 |  | 4 |  |  |  | 10 | **16** |
| team | `wujia_delivery` |  | 11 |  |  |  |  | 4 |  |  |  |  | **15** |
| team | `wujia_fleet` |  |  |  |  | 4 |  | 7 |  |  |  |  | **11** |
| team | `wujia_core` |  |  |  |  | 1 |  | 8 |  |  |  | 2 | **9** |
| team | `wujia_order_window` |  | 2 |  |  | 2 |  | 4 |  |  |  | 15 | **8** |
| team | `wujia_info_request` |  |  |  |  | 4 |  | 3 |  |  |  | 3 | **7** |
| team | `wujia_account` |  |  |  |  |  |  | 4 |  |  |  | 12 | **4** |
| team | `wujia_knowledge` |  |  |  |  |  |  | 2 |  |  |  | 15 | **2** |
| team | `wujia_support` |  |  |  |  |  |  | 2 |  |  |  | 12 | **2** |
| team | `wujia_metabase_connector` |  | 1 |  |  |  |  |  |  |  |  |  | **1** |
| Thái | `wujia_portal_inspection` | 118 | 11 | 13 |  |  |  | 30 |  | 6 |  |  | **178** |
| Thái | `wujia_franchise_inspection` |  |  |  |  |  | 1 | 90 |  | 3 |  | 16 | **94** |
| Thái | `wujia_franchise` |  |  |  |  | 1 |  | 6 |  |  |  |  | **7** |
| Thái | `wujia_franchise_contract` |  |  |  | 1 |  |  | 2 |  |  |  |  | **3** |
| Thái | `wujia_franchise_operations` |  |  |  |  |  |  | 2 |  |  |  |  | **2** |
| | **Tổng** | 1529 | 166 | 98 | 33 | 168 | 1 | 531 |  | 133 |  | 945 | **2659** |

Kế hoạch sửa chia phiên: `docs/next-session-clusters-J.md` §6 (Phần V). Code của Thái (5 module, 284 chuỗi): KHÔNG sửa — gửi
danh sách cho Thái tự xử.
