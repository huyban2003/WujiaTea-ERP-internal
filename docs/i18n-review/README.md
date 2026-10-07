# Rà soát sau Phần V (Việt hoá source) — ★J-VR, 07/10/2026

Phần V đổi câu gốc trong source của team sang tiếng Anh. Bản tiếng Việt nay nằm ở `i18n/vi_VN.po`, sinh từ
`docs/i18n-glossary.csv`, nên người dùng tiếng Việt vẫn thấy đúng chữ cũ. Thư mục này có 2 danh sách cần người khác xem.

## 1. `ba-en-terms.csv` — gửi BA (rà 1 lần, theo chốt J-V0)

1 361 cặp câu "tiếng Việt cũ → tiếng Anh mới" lấy từ 26 file `docs/i18n-pairs/*.csv`; mỗi cặp ghi một lần, kèm module và
tối đa 3 vị trí trong code.

- BA chỉ cần đọc cột `en_moi`. Câu nào chưa ổn thì ghi câu đề xuất vào `ba_de_xuat_en`.
- 10 dòng đầu có cột `can_xem` khác rỗng: cùng một câu tiếng Việt đang được dịch ra 2 câu tiếng Anh (hoặc ngược lại). Ví dụ:
  "Khẩn cấp" là "Emergency" ở loại thông báo nhưng là "Critical" ở mức ưu tiên ticket. BA chốt nên giữ 2 câu hay gộp 1.
- Không cần duyệt bản tiếng Việt: câu tiếng Việt giữ y như cũ. Bản tiếng Trung và tiếng Thái sẽ dịch máy ở J-T5.

## 2. `thai-vn-hardcode.csv` — gửi anh Thái

284 chuỗi tiếng Việt còn viết thẳng trong code các module của anh Thái. Team không sửa code của anh Thái (luật cụm J §0).

| Module | Chuỗi |
|---|---|
| `wujia_portal_inspection` | 178 |
| `wujia_franchise_inspection` | 94 |
| `wujia_franchise` | 7 |
| `wujia_franchise_contract` | 3 |
| `wujia_franchise_operations` | 2 |

Nhóm chuỗi chính là chữ trong QWeb của portal Khảo sát và chuỗi Python trong `wujia_franchise_inspection`. Nếu câu tiếng Việt
đã có trong glossary, cột `en_goi_y_tu_glossary` ghi sẵn câu tiếng Anh (18 dòng). Cách đổi theo quy ước:
`scripts/qa/README.md` §Phần V.

Ngoài danh sách trên còn 2 việc cần báo anh Thái:

- **Lỗi `.po` `web_survey_ui`**: `wujia_franchise_inspection/i18n/{vi_VN,th_TH,zh_CN}.po` có 40 dòng `#: web_survey_ui`
  (`zh_TW.po` có 104). Odoo không nhận dạng tham chiếu này, nên mỗi lần `-u` ghi 120 dòng ERROR
  "malformed po file: unknown occurrence". Đề xuất: đổi thành `#: code:addons/wujia_franchise_inspection/controllers/main.py:0`.
  Controller Khảo sát đọc `.po` lúc chạy nên vẫn tìm ra câu.
- **WJ-INSPECT-001** (Issue List STT 164): trang `/portal/inspection*` không theo ngôn ngữ của phiên.

Chữ tiếng Việt còn thấy trên portal ở en/th sau Phần V chỉ còn: dữ liệu (tên cửa hàng, sản phẩm, thông báo, bài viết, thương
hiệu "Ngô Gia"), tên ngôn ngữ "Tiếng Việt", và 2 mục menu "Khảo sát" / "Xem kết quả đánh giá & khảo sát cửa hàng" của module
Thái.
