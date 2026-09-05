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
