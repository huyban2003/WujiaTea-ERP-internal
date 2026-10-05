# `scripts/qa/` — bộ đo nghiệm thu portal

Hai script, dùng cho mọi cụm UI (D3 CardHeader, D4 SurfaceCard, D5 DataList…).

| Script | Trả lời câu gì |
|---|---|
| `wj_inventory.py` | Còn bao nhiêu call site **shell** của một họ lớp? |
| `wj_measure.py` | Thay đổi có làm vỡ gì không — đo bằng trình duyệt thật, 5 khổ |

## Vì sao nằm trong repo

Ba script đo của cụm D3/D4 (`d3_review.py`, `d4b_rhythm.py`, `d4_inventory.py`) từng
sống trong `scratchpad/`, vốn gitignored. Đổi sang máy khác là mất trắng, phải dựng
lại từ đầu — chính là việc của phiên 05/09/2026. Bộ đo là **bằng chứng nghiệm thu**,
không phải file nháp.

Khác `scripts/ba_spec/` (dev-only, gitignored, không lên server): hai script này chỉ
đọc mã nguồn và gọi HTTP, không giữ khoá hay token nào.

## `wj_inventory.py`

```
python3 scripts/qa/wj_inventory.py wj-pc-metric-card wj-rep-mcard
python3 scripts/qa/wj_inventory.py --sites --css wujia-mdash-card
```

Đếm **hai** dạng call site, và phải đếm cả hai:

- `class="wujia-mdash-card …"` — chưa migrate;
- `<t t-set="sc_class" t-value="'wujia-mdash-card …'"/>` — **đã** migrate, lớp cũ giữ
  lại để CSS con và ba danh sách `:is()` hover ở `_interaction.css` không đứt.

Bỏ dạng thứ hai thì càng migrate con số càng tụt: D4d đo ra 9 thay vì 50.

Loại tên con BEM bằng ranh giới từ, vì đây là nguồn của **hai** lần sai số bàn giao
liên tiếp — D4d bàn giao 51 (thật 50), D4e bàn giao 36 (thật 7).

**Đã kiểm chứng:** chạy trên 10 họ mobile của D4d ra đúng `30·7·4·2·2·1·1·1·1·1 = 50`,
khớp tuyệt đối bảng §4 của `docs/d4-surfacecard-inventory.md`.

## `wj_measure.py`

```
python3 scripts/qa/wj_measure.py --portal-login anh.owner --out before.json
#  … sửa code, upgrade module …
python3 scripts/qa/wj_measure.py --portal-login anh.owner --out after.json
python3 scripts/qa/wj_measure.py --diff before.json after.json
```

Bốn lớp bằng chứng trong một lượt, vì từng lớp một đều đã có tiền lệ lọt lỗi:

1. **RULE 1 `HIERARCHY`** — nhãn phụ có cỡ ≥ tiêu đề mở đầu của *chính card đó*.
2. **RULE 2 `CROSS`** — histogram cỡ tiêu đề card toàn portal (lệch chuẩn giữa các màn).
3. **Nhịp header→body TUYỆT ĐỐI** — RULE 1/2 đo sự *không đều*, nên sai số **đều tay**
   lọt qua sạch (D4b: `gap` cộng chồng margin thành 24px, hai rule kia vẫn xanh).
4. **Chiều cao trang + số record thấy trong viewport** ở 5 khổ `1440·1024·992·390·360`
   (acceptance #11 của BA: số record thấy được **không được giảm**).

Cộng thêm: redirect ngầm (vẫn trả 200 ⇒ "Pass rỗng" biến tướng), lỗi JS, tràn ngang,
và `--screenshots` — vì số đo Pass hết mà bố cục vẫn vỡ đã xảy ra hai lần (D3e badge
trôi 966px, D3d mất 28px nhịp).

### Ba điều đã trả giá, đừng gỡ

- `--portal-login` **không có mặc định**. Chạy bằng `admin` cho 0 bề mặt portal mà vẫn
  báo "xong" — bẫy "Pass rỗng", luật D4 #3.
- **Không** `wait_until='networkidle'`: portal mở long-poll `bus.bus` nên mạng không bao
  giờ rảnh, mọi trang timeout 30s. Dùng `load` + `--settle`.
- Nhịp **chỉ** đo khi có `.wj-card-header` thật. Bản đầu lấy `lead.parentElement` làm
  header dự phòng và ở `/portal/inspection` vớ phải div bao lớn có anh em nằm *phía trên*
  ⇒ in ra `-48.91px`, một con số không tồn tại.

### Giới hạn đã biết

Chỉ quét **13 route danh sách**. Các bảng nghiệm thu D3/D4 cũ có thêm route chi tiết
(`/portal/support/<id>`, `/portal/order/product/<id>`, `/portal/exam/register`…) nên tổng
số bề mặt **không so thẳng được** với chúng: mốc 05/09 ở đây là **127 bề mặt / 65 ô**,
còn `d4d-acceptance-matrix.md` ghi 225. Truyền `--routes` để thêm route chi tiết khi cần.

## `css_owner.py` (cụm F)

```
python3 scripts/qa/css_owner.py --layout-domain --overrides --json out.json
python3 scripts/qa/css_owner.py --who wujia-msheet-item
```

Cần `lxml` (chạy bằng python env Odoo). Hai câu hỏi:

- `--layout-domain`: mỗi **nhóm class gốc BEM** (bỏ `__x`, `--x`) khai trong
  `wujia_portal_layout/static/assets/css/_*.css` đang được **module nào dùng** (view XML qua
  lxml, JS `static/src`, chuỗi Python `controllers/`). ≥2 module ⇒ `component` (giữ layout) ·
  1 module ⇒ CSS của màn đó (F2/F3 dời ra) · chỉ layout ⇒ `khung` · không ai ⇒ `orphan`.
- `--overrides`: rule trong module portal (trừ Khảo sát) mà **phần tử đích** của selector mang
  class component/khung, tách "bố cục" (margin/padding/gap/flex/grid/kích thước/vị trí/display)
  và "đổi dáng" (phần còn lại). Class chỉ ở tổ tiên (`.wujia-mpage .x`) là ngữ cảnh, không tính.

Bẫy đã trả giá khi dựng (F0): đếm từng class lẻ ra 253 "CSS màn" thay vì 193 nhóm; tính cả
component ở tổ tiên ra 46 rule đè thay vì 41.

## `check_layers.py` (ADR-027)

```
python3 scripts/qa/check_layers.py            # báo cáo, exit 0
python3 scripts/qa/check_layers.py --strict   # exit 1 nếu vi phạm — bật sau khi mục D chốt
```

Đọc `__manifest__.py` của `custom/wujia_*`, bảng tầng khai tay trong script (module mới chưa
khai ⇒ báo "chưa phân tầng", không đoán theo tên cho tầng L1/L2). Luật R1–R5 theo chapter 74.

## Phần V — Việt hoá source (quy trình 1 phiên, chốt J-V0 05/10)

Quy ước + lý do: `docs/next-session-clusters-J.md` §6. Python env Odoo (cần lxml/playwright).

1. `vn_to_en_pairs.py draft --module X` → `docs/i18n-pairs/X.csv`; điền cột `en` (câu ngắn, rõ nghĩa nghiệp vụ). Dòng muốn tự sửa
   thì `mode=manual`. Đo mốc trước: `wj_text_probe.py --lang vi_VN --out before.json` (hoặc dùng `docs/i18n-baseline/vi_VN.json`).
2. `vn_to_en_pairs.py check --module X` → 0 lỗi.
3. `vn_to_en_pairs.py apply --module X` → thay QWeb text/attr dịch được + `_()`/`string=` + thêm glossary; in danh sách sửa tay.
4. Sửa tay theo §6: `t-out="… or 'Chưa có'"` → `<t t-set>`; hằng nhãn Python → `_lt()`; chuỗi JS → `data-wj-msg-*` + `wjMsg()`;
   attr không dịch (`data-*`, `value` không phải input) → `<t t-set>`. Test assert nhãn VN → chạy với `lang=vi_VN`.
5. `-u X` trên DB đo rồi `scripts/sync_translations.py --modules X --langs vi_VN --db <DB> --import` → `i18n/vi_VN.po` + `.pot` (tự tạo
   `i18n/`). **Liệt kê msgid chưa dịch** của `.po` (babel) — bắt tiếng Việt KHÔNG dấu mà máy quét sót (J-V1: `Trang sau`, `/ trang`) và
   term Odoo gom cả thẻ inline (`<span>…</span>`) ⇒ thêm glossary đúng msgid đó rồi chạy lại.
6. `-u X` + **restart** (server đang chạy giữ cache template ⇒ probe ra chữ cũ) ⇒ `vn_hardcode_scan.py --module X --fail-on-any` = 0 · `wj_text_probe.py --diff before after` = 0 trang lệch ·
   chụp en_US/th_TH không vỡ layout · suite module 0 đỏ mới · app "Bản dịch" độ phủ vi_VN ≈100%.
