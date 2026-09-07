# Rà soát đa ngôn ngữ toàn bộ code Wujia (20/08/2026)

> Trả lời câu hỏi của chủ dự án: *"code wujia có thuần tiếng Anh + gắn .po không, hay
> tiếng Việt vẫn nằm tè le trong view và portal?"*
>
> Báo cáo **chỉ đo và xếp ưu tiên**, không sửa module nào ngoài `wujia_franchise`.

## 1. Nói ngắn gọn kết quả

| Câu hỏi | Trả lời |
|---|---|
| `wujia_franchise` đã chuẩn chưa? | **Rồi** — 0 mã khoá tự chế, 0 nhãn tiếng Việt trong code, 506 câu nằm trong `.pot`, chạy được vi/zh/th |
| Các module còn lại? | **Chưa** — còn ~2.500 dòng chữ Việt nằm thẳng trong XML và ~1.400 chuỗi trong JS |
| Nguy hiểm nhất là chỗ nào? | **JavaScript**: 1.424 chuỗi tiếng Việt, **0 chuỗi** được bọc `_t()` ⇒ đổi ngôn ngữ vẫn ra tiếng Việt, không cách nào dịch |
| XML tiếng Việt có phải lỗi không? | **Không hẳn.** Odoo vẫn bắt được chữ trong template vào `.pot`, chỉ là khoá bằng tiếng Việt thay vì tiếng Anh. Dịch được ngay, chỉ không "đẹp chuẩn" |

## 2. Số đo theo module (đo 20/08, đếm chuỗi có dấu tiếng Việt)

| Module | XML | JS | PY | Có `.po` | Có `.pot` |
|---|---:|---:|---:|:--:|:--:|
| `wujia_portal_base` | 353 | 14 | 129 | – | – |
| `wujia_portal_layout` | 322 | **1.176** | 45 | – | – |
| `wujia_portal_exam` | 302 | 70 | 170 | 1 | – |
| `wujia_portal_debt` | 256 | 10 | 124 | 1 | – |
| `wujia_portal_sale` | 227 | 36 | 137 | – | – |
| `wujia_portal_inspection` | 179 | 6 | 27 | – | – |
| `wujia_portal_return` | 158 | 2 | 105 | 1 | – |
| `wujia_portal_purchase_history` | 130 | 0 | 71 | 1 | – |
| `wujia_portal_notification` | 127 | 13 | 125 | 1 | – |
| `wujia_portal_support` | 121 | 0 | 10 | 1 | 1 |
| `wujia_portal_delivery` | 108 | 0 | 35 | – | – |
| `wujia_portal_info_request` | 83 | 0 | 30 | 1 | – |
| `wujia_portal_knowledge` | 75 | 0 | 27 | 1 | 1 |
| `wujia_portal_report` | 67 | 10 | 21 | – | – |
| **`wujia_franchise`** | **58 (chỉ chú thích + seed data)** | **0** | **99 (chú thích + seed)** | **3** | **1** |
| `wujia_delivery` / `wujia_sale` / `wujia_account` / `wujia_fleet` / `wujia_core` | 0–12 | 0 | 4–34 | 0–1 | 0–1 |
| `wj_ks_dashboard_ninja` (module mua) | 0 | 60 | 0 | 3 | – |

Ba con số đáng chú ý:

1. **10/23 module không có file `.po` nào** — nghĩa là chưa từng dịch, chạy được tiếng Việt
   thuần tuý vì chữ nằm sẵn trong code.
2. **Chỉ 3 module có `.pot`** (`wujia_franchise`, `_portal_support`, `_portal_knowledge`).
   Không có `.pot` thì lần dịch sau không biết lấy khoá ở đâu (bài học L8/(3)).
3. **0/1.424 chuỗi JS được bọc `_t()`** trên toàn repo.

## 3. Ba nhóm vấn đề, mức độ khác nhau

### Nhóm A — JS: hỏng thật, phải sửa code (ưu tiên 1)

Chuỗi tiếng Việt viết thẳng trong `.js` **không vào `.pot`, không dịch được bằng bất kỳ
cách nào**. Khách chọn tiếng Trung thì nút vẫn hiện tiếng Việt.

Nặng nhất: `wujia_portal_layout` (1.176 chuỗi), `wujia_portal_exam` (70),
`wj_ks_dashboard_ninja` (60 — module mua, chỉ nên đụng nếu buộc phải).

Hai cách sửa, chọn theo kiểu file:

- File nằm trong asset bundle (OWL): `import { _t } from "@web/core/l10n/translation"`
  rồi bọc `_t("...")` — chuẩn Odoo, chữ tự vào `.pot`.
- File nạp bằng `<script src>` ngoài bundle (như trang khảo sát của
  `wujia_franchise`): đặt nhãn vào template dưới dạng phần tử ẩn, JS đọc ra.
  **Cách này vừa làm xong ở `wujia_franchise`, có thể copy nguyên mẫu** —
  xem `views/inspection_survey_web_templates.xml` (khối `#surveyI18n`) và
  `static/src/js/inspection_survey.js` (hàm `tr()`).

### Nhóm B — XML portal: dịch được, chỉ là khoá bằng tiếng Việt (ưu tiên 2)

~2.500 dòng chữ Việt trong template portal. Odoo **vẫn** bắt hết vào `.pot` dạng
`model_terms:ir.ui.view`, nên chỉ cần sinh `.po` là portal chạy được tiếng Trung/Thái ngay.

**Đề xuất: giữ nguyên khoá tiếng Việt cho portal, chỉ sinh `.po`.** Lý do:

- Đổi 2.500 dòng template sang tiếng Anh = một sprint riêng, đụng vào layout đang chạy
  cho 1.500 user ⇒ rủi ro vỡ giao diện lớn hơn lợi ích.
- Sinh `.po` thì không đụng một dòng template nào, rủi ro gần bằng 0.
- Khi nào portal cần làm lại giao diện thì tiện tay đổi luôn sang tiếng Anh.

Với module backend (`wujia_sale`, `wujia_account`, `wujia_delivery`, `wujia_fleet`,
`wujia_core` — mỗi cái chỉ 4–34 chuỗi) thì ngược lại: **đổi thẳng sang tiếng Anh**, ít việc
mà sạch hẳn.

### Nhóm C — Python: phần lớn không phải lỗi

Chuỗi tiếng Việt trong `.py` chia làm ba loại, chỉ loại đầu mới phải sửa:

| Loại | Ví dụ | Xử lý |
|---|---|---|
| Bọc `_()`, `string=`, `help=`, `_description` | `raise UserError(_('Cửa hàng...'))` | **Đổi sang tiếng Anh**, bản Việt vào `.po` |
| Chú thích, docstring | `# Nhân viên thực hiện giám sát` | **Giữ tiếng Việt** — người Việt đọc code |
| Dữ liệu mẫu | 15 câu hỏi công thức pha chế trong `wujia_franchise_inspection_question.py` | **Giữ tiếng Việt** — đây là nội dung nghiệp vụ, không phải nhãn giao diện |

## 4. Kế hoạch đề nghị, nối tiếp `docs/next-session-i18n.md`

| Đợt | Việc | Ước lượng | Rủi ro |
|---|---|---|---|
| **B1** | Sinh `.po` + `.pot` cho 10 module chưa có, giữ nguyên khoá tiếng Việt | 1 phiên | Thấp — không sửa code |
| **B2** | Nhóm A: bọc dịch cho JS `wujia_portal_layout` + `_exam` + `_portal_base` theo mẫu `wujia_franchise` | 2 phiên | Trung bình — có sửa JS đang chạy, cần hồi quy portal |
| **B3** | Đổi sang tiếng Anh cho 5 module backend nhỏ (`wujia_sale`, `_account`, `_delivery`, `_fleet`, `_core`) | 1 phiên | Thấp |
| **B4 (chưa cần)** | Đổi template portal sang khoá tiếng Anh | 1 sprint | Cao — gộp vào lần làm lại giao diện portal |

## 5. Nguyên tắc chốt lại cho lần sau (để khỏi lặp lại chuyện mã khoá)

1. **Không tự chế cơ chế dịch.** Không mã khoá, không CSV tra lúc chạy. Code viết tiếng
   Anh, dịch để trong `.po` — đúng như Odoo làm.
2. **Có `.po` thì phải có `.pot` cùng lượt** (L8/(3)). Thiếu `.pot` là lần sau mất khoá.
3. **Chữ trong JS phải bọc dịch** (`_t()` nếu ở bundle, đọc từ template nếu ở ngoài).
4. **Cổng bắt buộc trước khi nạp:** `msgfmt -c` cho từng file `.po`.
5. Bản dịch máy (nhất là tiếng Thái) **phải cho BA rà** trước khi lên UAT — đã có ví dụ
   sai: `Nháp` (bản nháp) bị dịch thành `ตี` (nghĩa là *đánh*).

## 6. Công cụ đã có sẵn

```bash
# sinh .po + .pot, điền bản dịch từ glossary, tự chạy msgfmt -c
python3 scripts/sync_translations.py --modules <mod> \
    --langs vi_VN,zh_CN,th_TH --glossary docs/i18n-glossary.csv --db <DB_COPY>
# thêm --import để nạp thẳng vào DB
```

`docs/i18n-glossary.csv` hiện **461 khoá tiếng Anh** (VN/CN/TH), trong đó 269 dòng dịch
CN/TH là công của anh Thái, đã được đánh khoá lại theo câu tiếng Anh chuẩn nên dùng tiếp
được cho các module sau.
