# Review nhánh `thai` khi merge vào `main` — 2026-08-19

Gửi anh Thái. Nhánh `origin/thai` (`d0391b2`) đã được merge vào `main` qua nhánh
`dev/2026-08-19-merge-thai`. Merge **không có conflict**, tính năng giám sát giữ nguyên
100% thiết kế của anh. Dưới đây là những chỗ em sửa lại kèm **lý do**, để lần sau khỏi
vướng lại. Xếp theo mức độ nghiêm trọng.

---

## A. Chặn deploy — phải sửa trước khi lên UAT

### A1. ACL mở toang cho toàn bộ user (nghiêm trọng nhất)

`custom/wujia_franchise/security/ir.model.access.csv` bị thay 6 dòng phân quyền theo group
bằng 2 dòng:

```csv
access_franchise_member_all,...,model_wujia_franchise_member,,1,1,1,1
access_franchise_management_all,...,model_wujia_franchise_management,,1,1,1,1
```

Cột `group_id` **để trống** trong `ir.model.access.csv` nghĩa là "áp cho MỌI user", không
phải "chưa gán ai". Kèm `1,1,1,1` ⇒ **~1500 portal user được sửa và xoá cửa hàng bất kỳ**.

Đã khôi phục 6 dòng cũ (`group_franchise_user` read · `group_franchise_manager` full ·
`base.group_portal` read). **22 dòng ACL mới cho các model inspection/supervision của anh
giữ nguyên** — phần đó anh viết đúng chuẩn, kể cả `ir.rule` "inspector chỉ thấy phiếu của
mình".

Đo lại bằng máy trên DB copy: portal user `em.hcm` → `read` 3 cửa hàng của mình (đúng),
`write` và `create` đều **AccessError**.

> Mẹo: cần "ai cũng đọc được" thì viết 1 dòng cho `base.group_user` + 1 dòng cho
> `base.group_portal`, đừng để trống `group_id`.

### A2. Cài mới thất bại — seed dữ liệu trong `init()`

`wujia_franchise_inspection_template.py:227` ghi đè `init()` để gọi `_init_demo_template()`,
mà hàm này `create()` bản ghi `wujia.franchise.inspection.template.line`.

`init()` chạy **trong lúc Odoo đang dựng bảng, theo thứ tự từng model** — lúc model template
chạy `init()` thì bảng `..._template_line` **chưa tồn tại**:

```
psycopg2.errors.UndefinedTable: relation "wujia_franchise_inspection_template_line" does not exist
```

Build `-i wujia_portal_inspection` RC=255 vì lỗi này. Đã gỡ cả 3 chỗ ghi đè `init()`
(template, category, grade) — **vốn đã thừa**, vì file XML data của anh đã gọi đúng 3 hàm
đó bằng `<function>`, và XML data chạy **sau khi mọi bảng đã có**.

### A3. Bản seed không bao giờ chạy trên server đã cài sẵn module

Đây là lý do sâu xa khiến anh phải nhét vào `init()`. Hai file data đều mở bằng
`<odoo noupdate="1">`. `noupdate="1"` ⇒ nội dung **chỉ chạy lần cài đầu tiên**; UAT đã cài
`wujia_franchise` từ lâu nên `-u` sẽ **không** chạy 3 hàm seed ⇒ lên server sẽ là
**0 mẫu khảo sát, 0 xếp hạng, 0 danh mục** — tính năng không dùng được.

Đã bỏ `noupdate="1"` ở cả 2 file. An toàn vì cả 3 hàm đều idempotent sẵn
(`existing = search(...); if not existing: create(...)`).

Đo trên DB copy đã cài sẵn `wujia_franchise`, chạy `-u`: **1 mẫu MM01 + 77 tiêu chí +
4 xếp hạng + 4 danh mục** — trước khi sửa là 0/0/0/0.

Kèm: đổi tên `wujia_inspection_template_demo.xml` → `wujia_inspection_bootstrap.xml`. Đây là
dữ liệu cấu hình chạy thật trên production, gọi là "demo" dễ bị người sau xoá nhầm.

### A4. `vi_VN.po` bị đạp mất bản dịch + hỏng cú pháp

Script dịch có nhánh:

```python
if not translated_val and lang_col == 'VN':
    translated_val = full_msgid          # ← lấy chính chuỗi nguồn làm bản dịch
```

Nhánh này **đã chạy và đã commit**: `msgid "Store code"` giờ có `msgstr "Store code"`,
trong khi bản trên `main` là `"Mã cửa hàng"`. Sprint 44 dịch 636 nhãn / 81 file — chạy
script này lên 14 file `vi_VN.po` sẽ xoá sạch công đó.

Ngoài ra chính file đó **không parse được**. `msgfmt -c` báo hàng chục lỗi
`end-of-line within string`, do bộ parse regex:

- `re.findall(r'"(.*?)"', block)` cắt chuỗi tại dấu `\"` ⇒
  `msgid "<span id=\"lineModalPrevBadge\"...>"` biến thành `msgstr "<span id=\"` (cụt).
- `.replace('\n', '\\n"\n"')` chèn **xuống dòng thật** vào giữa chuỗi ⇒ file `.po` sai cú pháp.

Đã khôi phục `vi_VN.po` về bản `main` và viết lại script (mục C).
`zh_CN.po` của anh **giữ nguyên** — file đó parse sạch, 174 chuỗi đã dịch, dùng tốt.

---

## B. Bảo mật & ảnh hưởng diện rộng

### B1. Kiểm quyền portal fail-open (IDOR)

`wujia_portal_inspection/controllers/portal.py` và module remediation:

```python
franchise_ids = get_active_franchise_ids_filter()
if franchise_ids and insp.franchise_id.id not in franchise_ids:
    return request.redirect('/portal/inspection')
```

`franchise_ids` **rỗng** thì mệnh đề `and` ngắn mạch ⇒ **bỏ qua luôn kiểm tra**. Mà rỗng
chính là ca "user không thuộc cửa hàng nào" — đúng ca cần chặn nhất. Kết quả: user đó xem
được phiếu của **mọi cửa hàng**. Cùng lỗi ở domain danh sách (`if franchise_ids:` mới thêm
điều kiện lọc ⇒ rỗng thì liệt kê sạch).

Đã đảo thành fail-closed:

```python
if insp.franchise_id.id not in (franchise_ids or ()):        # chi tiết
inspection_domain.append(('franchise_id', 'in', list(franchise_ids or ())))   # danh sách
```

Đo thật (tạo 1 phiếu cho cửa hàng ngoài rồi rollback):

| Ca | Bản cũ | Bản mới |
|---|---|---|
| user có cửa hàng | CHẶN | CHẶN |
| **user KHÔNG có cửa hàng** | **LỌT** | **CHẶN** |
| danh sách phiếu trả về cho user không cửa hàng | **1 phiếu** | **0 phiếu** |

> Nguyên tắc: kiểm quyền viết theo hướng **mặc định từ chối**. `if <có dữ liệu> and <kiểm>`
> luôn là fail-open.

### B2. `try/except ImportError` che mất lỗi thật

```python
try:
    from odoo.addons.wujia_portal_base.controllers.portal import get_active_franchise_ids_filter
except ImportError:
    def get_active_franchise_ids_filter():
        return []
```

Module đã `depends` `wujia_portal_base` nên import không thể fail. Nhưng nếu có ngày fail
thật (đổi tên hàm chẳng hạn), fallback trả `[]` sẽ **im lặng tắt toàn bộ phân quyền** thay
vì báo lỗi. Đã bỏ `try/except`, import thẳng.

### B3. `csrf=False` trên route POST nhận file upload

`/portal/inspection/remediation/submit` đang `csrf=False`. Template của anh **đã render sẵn**
`<input type="hidden" name="csrf_token">` và JS dùng `new FormData(form)` (tự kèm token) ⇒
chỉ cần bật lên là chạy. Đã đổi `csrf=True`. Chuẩn repo: `wujia_portal_support` dùng
`csrf=True` cho mọi form POST.

### B4. Đổi `_order` của model dùng chung toàn hệ thống

`wujia.franchise.management._order` bị đổi `'code, name'` → `'latest_inspection_date desc,
code, name'`. Model này được ~20 file dùng: bộ chọn cửa hàng portal, targeting thông báo,
report giao hàng… ⇒ đổi `_order` là đổi thứ tự cửa hàng **ở mọi màn hình**, không chỉ màn
giám sát.

Đã trả về `'code, name'`. Không mất gì: list view giám sát của anh **đã có sẵn**
`default_order="latest_inspection_date desc"` (`wujia_franchise_management_views.xml:9`) —
đó mới đúng chỗ để đặt.

---

## C. Bộ script dịch — đã tổng quát hoá (đây là phần giá trị nhất của nhánh)

**Ý tưởng gốc của anh đúng và được giữ nguyên**: lấy `.pot` THẬT từ DB bằng
`odoo-bin i18n export -l pot` (nên có cả `model_terms:ir.ui.view` ⇒ dịch được cả chữ trong
template QWeb, thứ mà `_()` không với tới) → điền `msgstr` từ glossary CSV →
`odoo-bin i18n import -w`.

`scripts/sync_franchise_translations.py` + `sync_translations_franchise.sh` →
**`scripts/sync_translations.py`** (một file, có `--help`).

Thay đổi:

1. **Hết hard-code.** `--modules a,b,c` (hoặc `all`) · `--langs vi_VN,zh_CN,th_TH` · `--db`
   · `--glossary` · `--config` · `--dry-run` · `--import`. Python lấy từ `sys.executable`,
   DB lấy từ `odoo.conf`. Bản cũ ghim cứng `/home/dev/miniconda3/...` (máy anh) và
   `wujia_tea_19`.
   `--modules` **bắt buộc truyền tường minh** để không ai lỡ tay chạy diện rộng.
2. **Không bao giờ lấy msgid làm msgstr.** Thứ tự ưu tiên: glossary → **msgstr cũ trong file
   `.po` hiện có** → để rỗng. Không có trong glossary thì giữ nguyên bản dịch cũ.
3. **Dùng `babel.messages.pofile`** thay regex tự chế. Escape, chuỗi nhiều dòng, plural do
   thư viện lo — hết hẳn lớp lỗi ở A4.
4. **Luôn ghi `.pot` cùng lượt với `.po`** vào `custom/<mod>/i18n/`. Odoo tự merge `<mod>.pot`
   khi nạp `.po`; `.pot` cũ làm msgid mới thành obsolete — **không lỗi, không cảnh báo**,
   chỉ là bản dịch không lên. Trước đó `.pot` chỉ được ghi ra `/tmp` rồi vứt.
5. **Cổng `msgfmt -c`**: file nào hỏng cú pháp thì script **dừng, không nạp vào DB**, exit ≠ 0.
6. **Tự bật ngôn ngữ chưa cài** (`res.lang._activate_lang`) — `i18n import` từ chối lang chưa
   active, trước đây phải vào UI bật tay.
7. **Bỏ giá trị glossary trùng chính chuỗi nguồn** (glossary cũ có 78 ô như vậy) — đó không
   phải bản dịch, để rỗng cho rõ còn bao nhiêu chưa dịch.
8. 🔑 **Bắc cầu qua `vi_VN.po`.** Glossary đánh khoá theo **tiếng Việt**, nhưng từ Sprint 44
   msgid trong code là **tiếng Anh** ⇒ tra thẳng `glossary[msgid]` trượt hết nhãn field và
   menu. Nay tra 3 nấc: `glossary[msgid]` → `glossary[bản dịch vi_VN của msgid]` → msgstr cũ.
   Nhờ đó `zh_CN` từ 174 lên **183 chuỗi**, và nhãn `Store code` mới ra `店號` / `รหัสร้านค้า`
   thay vì đứng nguyên tiếng Anh.

**Glossary** dời từ `custom/wujia_franchise/data/wujia_franchise_export.csv` về
**`docs/i18n-glossary.csv`** (nó dùng chung cho mọi module, không phải data của riêng
`wujia_franchise`), thêm cột **`TH`**. `controllers/main.py` đã trỏ theo đường dẫn mới; thiếu
file thì `t()` tự rơi về default nên trang khảo sát vẫn chạy.

**Cách dùng:**

```bash
# xem trước, không đụng repo
python3 scripts/sync_translations.py --modules wujia_franchise --langs zh_CN --dry-run

# sinh .po + .pot rồi nạp vào DB
python3 scripts/sync_translations.py --modules wujia_franchise \
    --langs vi_VN,zh_CN,th_TH --db wujia_tea_19 --import
```

### Tiếng Thái đã chạy luôn

`th_TH` đã bật sẵn trên UAT và bộ chọn ngôn ngữ (C10) đã hiện mục tiếng Thái, chỉ thiếu file
dịch. Em đã điền **cột `TH` cho cả 250 dòng glossary** và sinh
`custom/wujia_franchise/i18n/th_TH.po` (183/487 chuỗi).

Đo trên DB copy, nhãn `code` của `wujia.franchise.management` theo từng ngôn ngữ:

| Ngôn ngữ | Kết quả | |
|---|---|---|
| vi_VN | `Mã cửa hàng` | ✓ |
| zh_CN | `店號` | ✓ |
| th_TH | `รหัสร้านค้า` | ✓ |
| en_US | `Store code` | ✓ |

Tên model + menu gốc cũng ra đúng 3 thứ tiếng. **Bản tiếng Thái là máy dịch, cần BA rà lại.**
Các module khác chạy đúng 1 lệnh là ra, chỉ cần BA điền thêm cột `TH`.

---

## D. Vệ sinh repo

- **Trả 6 script về bản `main`**: `start.sh` `init-db.sh` `upgrade.sh` `reseed_full.sh`
  `build-doc.sh` `build-brief.sh` đang trỏ `/home/dev/WujiaTea-ERP-internal` và
  `/home/dev/miniconda3/envs/odoo19` (máy anh) ⇒ ai pull về cũng không chạy được. Bit thực
  thi cũng bị mất (755→644), đã `chmod +x` lại.
  > Đường dẫn riêng của máy thì để trong `config/` hoặc biến môi trường, đừng sửa file chung.
- **Bỏ 8 file tạm**: `scratch/test_save.py`, `scripts/test_distinct_on.py`,
  `test_read_group.py`, `get_table.py`, `recompute_latest.py`, `qkill.sh`, **`clear_data.py`**,
  **`reset-db.sh`**. Hai cái cuối xoá dữ liệu / drop DB — nằm trong repo chung là rủi ro thật.
- **`wujia_core/__init__.py`**: bộ chia log theo `năm/tháng/ngày.log` **giữ nguyên**, tiện.
  Chỉ thêm 1 dòng ghi vào `logfile` gốc chỉ đường sang thư mục mới — vì handler này **gỡ hẳn**
  handler cũ, ai mở đúng file trong `odoo.conf` sẽ thấy file rỗng và tưởng server không chạy
  (em mất kha khá thời gian ở đúng chỗ này lúc debug A2).
- **`wj_ks_dashboard_ninja` `unlink()`** thêm guard `'ks_dashboard_item_id' in _fields` —
  đúng, giữ nguyên.
- `wujia_franchise` bump `19.0.2.1.0` → **`19.0.3.0.0`** (8 model mới).

---

## E. Chưa sửa — cần anh xác nhận (em không tự đổi thiết kế nghiệp vụ của anh)

1. **`wujia.franchise.inspection.confirmed_member_id` đang `required=True`.** Nghĩa là không
   thể tạo phiếu khảo sát nếu chưa chỉ định trước người xác nhận của cửa hàng. Nhưng theo
   luồng `draft → in_progress → done` thì việc xác nhận nằm ở **cuối**. Nếu ý anh là "chọn
   trước ai sẽ ký" thì giữ nguyên; nếu không thì nên bỏ `required` và ràng buộc ở
   `action_confirm` thay vì ở cột DB.
2. **`custom/wujia_franchise/controllers/main.py` dịch bằng CSV runtime**, chạy song song với
   i18n của Odoo. Nó hoạt động, nhưng nghĩa là trang khảo sát nằm ngoài mọi công cụ dịch
   chuẩn (`.po`, giao diện dịch của Odoo). Về lâu dài nên gom về một mối. Chưa đụng lần này.
3. Còn **304/487 chuỗi chưa có trong glossary** — chờ BA bổ sung, script chạy lại là ra.

---

## F. Đã đo gì trước khi merge

DB copy cô lập `wujia_tea_merge_thai`, cổng 8059 — **không đụng `wujia_tea_19`/8019**.

| Hạng mục | Kết quả |
|---|---|
| `git merge-tree main origin/thai` | 0 conflict |
| 5 mốc C1–C10 còn sau merge | 5/5 |
| `-u wujia_core,wujia_franchise,wujia_sale -i wujia_portal_inspection,wujia_portal_remediation` | **RC=0**, 0 ERROR |
| Test hồi quy 11 module × 12 tag | **171 test, 0 failed, 0 error** |
| ACL portal: `write` / `create` cửa hàng | AccessError (đúng) |
| IDOR user không cửa hàng | cũ LỌT → mới CHẶN, danh sách 1 → 0 phiếu |
| Seed sau `-u` trên DB đã cài sẵn | 0/0/0/0 → **1 mẫu + 77 tiêu chí + 4 hạng + 4 danh mục** |
| `msgfmt -c` mọi `.po`/`.pot` trong `custom/` | sạch |
| Nhãn 4 ngôn ngữ | 4/4 |

## G. Lệnh deploy UAT

```
-u wujia_core,wujia_franchise,wujia_sale
-i wujia_portal_inspection,wujia_portal_remediation
```

⚠️ Module MỚI phải `-i` một lần, restart không tự cài. `-u` chạm `wujia_portal_return` thì
bắt buộc kèm `wujia_sale` (rename `description_ecommerce` từ S52). Có asset frontend mới ⇒
bump `?v=`.
