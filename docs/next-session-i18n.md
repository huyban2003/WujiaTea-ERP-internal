# Phiên sau — dịch `.po` cho các module còn lại

## Trả lời 2 câu hỏi của chủ dự án (19/08)

**1. Các module portal còn lại dịch sau phải không?** — Đúng. Phiên 19/08 chỉ làm
**pilot 1 module `wujia_franchise`** (3 thứ tiếng, 183 chuỗi/thứ) để chứng minh
toolchain chạy đúng. Các module còn lại làm ở (các) phiên sau.

**2. Chạy local hay server?** — **CHẠY LOCAL, KHÔNG chạy trên server.** Lý do:

- Script cần `odoo-bin i18n export` → mở DB, tốn RAM/CPU; UAT đang có ~1500 user.
- Kết quả của script là **file `.po` nằm trong repo**, không phải thứ chỉ sống trong DB.
  Chạy local → commit file → deploy code → trên server chỉ cần `-u <module>` là Odoo
  **tự nạp `.po`** cho các ngôn ngữ đã cài. Không ai phải chạy script trên server.
- Chạy trên server còn nguy hiểm: `--import` ghi thẳng vào `ir.translation` của DB thật,
  sai một chỗ là hỏng cả 3 thứ tiếng đang chạy.

Quy trình chuẩn: **local sinh file → commit → deploy `-u` → xong.**

---

## Hiện trạng đo được 19/08

| Module | vi_VN | zh_CN | th_TH |
|---|---|---|---|
| wujia_franchise | 160 | 183 | 183 |
| wujia_fleet | 107 | – | – |
| wujia_portal_exam | 117 | – | – |
| wujia_portal_return | 139 | – | – |
| wujia_portal_notification | 91 | – | – |
| wujia_delivery | 88 | – | – |
| wujia_sale | 50 | – | – |
| wujia_portal_info_request | 37 | – | – |
| wujia_core | 28 | – | – |
| wujia_portal_support | 26 | – | – |
| wujia_portal_order_window | 24 | – | – |
| wujia_portal_knowledge | 20 | – | – |
| wujia_portal_debt | 1 | – | – |
| wujia_portal_purchase_history | 0 | – | – |
| **CHƯA CÓ `i18n/` nào** | – | – | – |
| wujia_portal_base, wujia_portal_layout, wujia_portal_sale, wujia_portal_delivery, wujia_portal_report, wujia_portal_inspection, wujia_portal_remediation, wujia_account, wj_ks_dashboard_ninja, wj_ks_dn_advance, mcp_server | | | |

Tổng ước lượng còn phải dịch: **3.500–4.000 chuỗi** × 2 thứ tiếng (CN, TH) + vá vi_VN
cho 10 module trống.

**Điểm chặn thật sự KHÔNG phải là chạy lệnh** — lệnh chạy 30 giây/module. Chặn ở chỗ
`docs/i18n-glossary.csv` mới có **250 dòng, toàn từ vựng mảng giám sát cửa hàng**.
Module khác (đơn hàng, giao hàng, công nợ) chưa có từ ⇒ chạy xong file vẫn trống.
Việc thật của phiên sau = **mở rộng glossary**.

---

## Cách làm — CHỦ DỰ ÁN ĐÃ CHỐT 19/08

> **"dịch và BA rà kèm file excel"** — agent dịch máy, **kèm file Excel cho BA rà**,
> BA rà xong mới coi là xong. Không hỏi lại.

Nghĩa là mỗi đợt có **2 sản phẩm**, không phải 1:

1. File `.po`/`.pot` trong repo (máy dịch, nạp được ngay).
2. **File Excel bàn giao BA** — mỗi dòng 1 chuỗi, cột:
   `Module | Chuỗi gốc (EN) | Tiếng Việt | 中文 | ไทย | Nguồn | BA sửa thành | Ghi chú BA`
   - Cột **Nguồn** ghi bản dịch từ đâu ra: `glossary` (BA đã duyệt trước đó) /
     `máy dịch` (cần rà kỹ) / `giữ bản cũ`. BA rà cột `máy dịch` trước.
   - Cột **BA sửa thành** để trống cho BA điền. BA trả file về → agent đọc ngược,
     **ghi vào glossary** rồi sinh lại `.po` ⇒ lần sau không phải rà lại chuỗi đó nữa.
   - Đây là vòng lặp: mỗi đợt BA rà, glossary dày lên, đợt sau máy dịch đúng hơn.

⚠️ **Chưa có code cho phần Excel** — phiên sau phải viết, đề xuất thêm 2 cờ vào
`scripts/sync_translations.py`:
`--review-out <file.xlsx>` (xuất file cho BA) và `--review-in <file.xlsx>`
(đọc cột "BA sửa thành" ngược vào `docs/i18n-glossary.csv`).
Dùng `openpyxl` (đã có trong env `odoo`, Odoo phụ thuộc sẵn).

Theo QA Operating Standard: đợt nào cũng chỉ tới **`Ready for Retest`**, BA rà xong
mới `Done`.

---

## Thứ tự làm — mỗi đợt 1 phiên

**Đợt 1 — khung portal** (1500 khách nhìn mỗi ngày, ưu tiên cao nhất):
`wujia_portal_layout`, `wujia_portal_base`, `wujia_portal_sale`, `wujia_portal_delivery`,
`wujia_portal_report`. Ước ~600–800 chuỗi.

**Đợt 2 — nghiệp vụ đã có vi_VN, thêm CN + TH:**
`wujia_portal_exam`, `_return`, `_notification`, `_support`, `_knowledge`,
`_order_window`, `_info_request`, `_debt`, `wujia_sale`, `wujia_delivery`,
`wujia_fleet`, `wujia_core`.

**Đợt 3 — 2 module portal mới của anh Thái + phần lẻ:**
`wujia_portal_inspection`, `wujia_portal_remediation`, `wujia_account`,
`wujia_portal_purchase_history` (đang 0 chuỗi vi_VN).

`wj_ks_dashboard_ninja` / `wj_ks_dn_advance` / `mcp_server` là module bên thứ ba — **không dịch**.

---

## Lệnh (chạy trong `/home/huyban/odoo-dev/WujiaTea`, env conda `odoo`)

Xem trước, không ghi file, không đụng DB:
```bash
python3 scripts/sync_translations.py --modules wujia_portal_base --langs th_TH --dry-run
```

Sinh file thật + nạp vào DB copy:
```bash
python3 scripts/sync_translations.py \
    --modules wujia_portal_base,wujia_portal_layout \
    --langs vi_VN,zh_CN,th_TH \
    --db <DB_COPY> --import
```

**Dùng DB copy, không dùng `wujia_tea_19`.** Phiên 19/08 dùng `wujia_tea_merge_thai`
(cổng 8059) — chủ dự án chốt **giữ lại**, tái dùng được ngay.

Script tự lo: bật ngôn ngữ chưa cài trong DB · ghi `.pot` cạnh `.po` · chạy `msgfmt -c`
và **từ chối import nếu có lỗi cú pháp**.

---

## 4 cái bẫy đã trả giá rồi — đừng dẫm lại

1. **Glossary đánh khoá bằng TIẾNG VIỆT, msgid trong code là TIẾNG ANH** (từ sau S44).
   Tra thẳng là trượt gần hết. Script đã bắc **cầu nối qua `vi_VN.po`**: msgid tiếng Anh →
   tra `vi_VN.po` ra chuỗi Việt → tra glossary. Hệ quả: **module nào chưa có `vi_VN.po`
   thì phải làm vi_VN TRƯỚC**, rồi mới sinh được CN/TH. Đúng thứ tự: `--langs vi_VN`
   chạy trước, xong mới `--langs zh_CN,th_TH`.
2. **Nhiều ô trong glossary chép lại y nguyên chuỗi gốc** — đó không phải bản dịch.
   Script đã bỏ qua (`val == msg.id` ⇒ coi như trống). Khi thêm dòng mới vào glossary,
   **đừng copy cột nguồn sang cột đích cho đủ ô**.
3. **`.pot` cũ làm msgid mới thành obsolete, im lặng không báo lỗi** (L8/3). Script đã
   luôn ghi lại `.pot`. Đừng sửa tay `.po` mà quên `.pot`.
4. **Ngôn ngữ chưa active trong DB thì `i18n import` từ chối** với thông báo mơ hồ
   `No valid language has been provided`. Script đã tự `_activate_lang`.

---

## Nghiệm thu mỗi đợt

| Hạng mục | Cách đo | Mốc |
|---|---|---|
| Cú pháp | `msgfmt -c custom/*/i18n/*.po` | 0 lỗi |
| Không đạp bản cũ | `msgid "Store code"` trong vi_VN.po | vẫn `"Mã cửa hàng"` |
| Không có ô dịch = chuỗi gốc | đếm `msgstr` trùng `msgid` | 0 |
| Ra đúng tiếng | mở portal, đổi ngôn ngữ, 3 màn bất kỳ | ra đúng thứ tiếng |
| Không lây sang tiếng khác | so `vi_VN`/`en_US` trước–sau | không đổi một chữ |

`th_TH.po` ghi rõ `Last-Translator: machine-assisted, cần BA rà` — **BA rà là bắt buộc**,
agent dịch máy không tự đóng Done (QA Operating Standard).

---

## Bối cảnh phiên trước (19/08)

Merge nhánh `thai` xong, đã lên `main` (`538f75e`) và push. Chi tiết 8 điểm sửa hộ
anh Thái: `docs/merge-thai-review.md`. **Hàng đợi deploy UAT còn nợ** — xem §5
`docs/wujia-compact-summary.md`.
