# BA-spec ingestion toolchain (dev-only)

Từ Sprint 30, **mọi task controller BA gửi đều nằm trong 1 chat ChatGPT share** + đối chiếu
với `docs/Wujia_Internal ERP Master Plan.xlsm`. Bộ tool này để đọc 2 nguồn đó nhanh, tái dùng
across session.

> **KHÔNG lên server.** Thư mục `scripts/ba_spec/` được gitignore → chỉ nằm ở máy dev, không
> push, không thuộc module Odoo nào. Chỉ là dev tool.

## Khi user yêu cầu "làm controller X" — quy trình chuẩn

1. **Đọc chat BA** (user đưa link share):
   ```bash
   python3 scripts/ba_spec/fetch_ba_chat.py "<share_url>" -o /tmp/ba_X.md
   ```
   → ra Markdown bảng controller mapping (STT / Màn hình / Action / Model / Input / Rule / Field
   trả về / Ghi chú) + flow + rủi ro + câu hỏi confirm.

2. **Dump xlsm** các sheet liên quan để đối chiếu model/field/feature thật:
   ```bash
   python3 scripts/ba_spec/read_xlsm.py --sheets
   python3 scripts/ba_spec/read_xlsm.py "1. Model Field" <model_keyword>
   python3 scripts/ba_spec/read_xlsm.py "2. FE - Portal" <keyword>
   python3 scripts/ba_spec/read_xlsm.py "3. Controller" <keyword>
   python3 scripts/ba_spec/read_xlsm.py "FEATURE CHECKLIST" <keyword>
   ```

3. **Đối chiếu spec BA ↔ source model thật** rồi mới code — bước 3–5 (tên model lý tưởng hoá,
   hỏi khi gặp fork, perf-first 1500 user) mô tả đầy đủ ở **compact-summary §7 "Controller task
   (S32+)"**, không chép lại ở đây.

## Ghi chú kỹ thuật

- `fetch_ba_chat.py`: trang share render JS (turbo-stream). `backend-api/share/<id>` bị
  Cloudflare 403 → tool tải HTML page với UA trình duyệt, bóc `streamController.enqueue("…")`,
  decode, lấy message string trong mảng phẳng. Nếu ChatGPT đổi format stream → chỉnh 2 hàm
  `extract_blob` / `extract_messages`.
- `read_xlsm.py`: openpyxl read-only. Không keyword = in cả sheet.
