# Prompt cho session merge nhánh `thai` (khảo sát 2026-08-19)

Dán khối dưới sau `/wujia-start`. Số liệu trong đây lấy từ `git fetch` ngày 19/08/2026
(`origin/thai` = `d0391b2` "add bản đã dịch rồi"), merge-base với `main` = `7e139bb` (11/08).

```
Session này em merge nhánh `origin/thai` (anh Thái) vào `main`, KHÔNG làm cụm C8.

Bối cảnh đã khảo sát 19/08 (đừng khảo sát lại từ đầu, chỉ verify lại số):
- `origin/thai` = d0391b2, lệch `main` 74 file. Hai nhóm nội dung:
  (a) TÍNH NĂNG MỚI: giám sát / chấm điểm cửa hàng — thêm 6 model vào `wujia_franchise`
      (`wujia.franchise.inspection`, `.inspection.grade`, `.inspection.question`,
      `.inspection.template`, `wujia.supervision.schedule`) + module MỚI
      `wujia_portal_inspection` + controller + view + security + CSS/JS + data seed.
  (b) BỘ SCRIPT DỊCH: `scripts/sync_franchise_translations.py` + `sync_translations_franchise.sh`
      và `custom/wujia_franchise/i18n/zh_CN.po` (đã dịch thật, chạy được).
- Nhánh thai CHƯA có C1–C7/C9/C10 ⇒ phải merge `main` VÀO thai (hoặc rebase thai lên main),
  KHÔNG merge ngược làm mất C1–C7.
- Điểm đụng độ với main kể từ merge-base CHỈ 2 file — đọc kỹ trước khi giải conflict:
  · `custom/wujia_franchise/__manifest__.py` (thai thêm data/view; main bump version)
  · `custom/wujia_franchise/models/wujia_franchise_management.py` — chỗ C1 thêm
    `_wujia_unique_franchise()` + index `partner_id`. Giữ ĐỦ cả hai bên.

Việc:
1. Merge: `git checkout -b dev/<ngày>-merge-thai origin/thai` rồi `git merge main`, giải 2
   conflict trên. Sau merge phải grep lại `_wujia_unique_franchise` và index partner_id còn đủ.
2. Build trên DB copy cô lập (port riêng, KHÔNG đụng 8019/wujia_tea_19):
   `-u wujia_franchise -i wujia_portal_inspection` RC=0. ⚠️ Module MỚI phải `-i` một lần
   (§6), và `-u` chạm `wujia_portal_return` thì bắt buộc kèm `wujia_sale` (rename S52).
3. Chạy toàn bộ test hiện có của các module bị chạm + lưới B4 (282/286 là mốc chuẩn) —
   tính năng mới của anh Thái không được làm đỏ cái đang xanh.
4. Đọc `scripts/sync_franchise_translations.py` rồi TỔNG QUÁT HOÁ nó (đây là mục tiêu chính
   về lâu dài — BA khỏi phải dịch tay từng file .po):
   - Luồng hiện tại ĐÚNG và giữ nguyên: `odoo-bin i18n export -l pot` lấy .pot THẬT từ DB
     (có cả `model_terms:ir.ui.view` ⇒ dịch được chữ trong template QWeb) → điền `msgstr`
     từ CSV glossary → `odoo-bin i18n import -w` nạp vào DB.
   - Phải sửa: đang hard-code 1 module `wujia_franchise`, 2 ngôn ngữ VN/CN, python
     `/home/dev/miniconda3/...` (máy anh Thái), DB `wujia_tea_19`. Đổi thành tham số
     `--modules --langs --db`, đọc python/conf từ `config/odoo.conf`.
   - 🔴 BẪY PHẢI SỬA TRƯỚC KHI CHẠY DIỆN RỘNG: nhánh
     `if not translated_val and lang_col == 'VN': translated_val = full_msgid`
     ghi đè TOÀN BỘ `vi_VN.po`. Chạy như hiện tại lên 14 file `vi_VN.po` sinh ở S44 sẽ đạp
     bản dịch thành msgid. Phải giữ msgstr cũ khi CSV không có khoá.
   - Thêm cột `TH` cho tiếng Thái: `th_TH` ĐÃ bật sẵn trên UAT (đo 19/08: en_US + th_TH +
     vi_VN active) và bộ chọn ngôn ngữ C10 tự hiện, chỉ thiếu file dịch.
   - Nhớ L8/3: sinh `.po` phải sinh `.pot` cùng lúc, không thì Odoo merge `.pot` cũ và bản
     dịch mới thành obsolete — im lặng, không lỗi.
5. Hỏi chủ dự án ở mọi fork: phạm vi module đem đi dịch, ai giữ file CSV glossary (BA hay
   repo), có đưa `wujia_portal_inspection` vào hàng đợi deploy UAT ngay không.

Ngoài phạm vi: cụm C8, viết chapter .tex, deploy UAT.
```

## Ghi chú kỹ thuật kèm theo (để khỏi mở lại git)

- Định dạng CSV glossary hiện tại: `key,VN,CN` — `key` là mã kỹ thuật (vd `menu_wujia_root`)
  hoặc chính chuỗi nguồn; script map cả hai chiều (`trans_map[key]` và `trans_map[vn]`).
- File CSV: `custom/wujia_franchise/data/wujia_franchise_export.csv` (448 dòng).
- Nhánh thai cũng sửa `custom/wj_ks_dashboard_ninja/models/wj_ks_dashboard_ninja_items.py`
  — không đụng gì của mình, nhưng nhớ chạy lại dashboard sau merge.
