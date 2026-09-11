# D6a — Kiểm kê cụm Bù hàng (UAT-BH-007 · 008 · 009)

**Ngày:** 2026-09-10 · **DB đo:** `wujia_tea_d6` (copy `wujia_tea_d5h2`, port 8080) ·
**Nhánh:** `dev/2026-09-10-d6` · **0 dòng code sản phẩm trong lượt này.**

Lượt kiểm kê không migrate call site nào ⇒ ba issue **giữ `Ready for Dev`**, không chạy
`qa_sync.py` (tiền lệ D3a/D4a/D5a).

---

## 1. Vì sao D6 không phải cụm chuẩn component

D3 (CardHeader) · D4 (SurfaceCard) · D5 (DataList) là ba mắt xích *dựng* component.
**D6 là cụm nghiệp vụ TIÊU THỤ component.** Kiểm kê bằng `lxml` xác nhận điều đó bằng số:

| File | D3 CardHeader | D4 SurfaceCard | D5 DataList | B3 PageHeader | C8 SectionHeader | Khung dựng tay |
|---|---:|---:|---:|---:|---:|---:|
| `portal_return_list.xml` | 1 | 1 | 2 | 2 | 1 | **0** |
| `portal_return_form.xml` | 4 | 4 | 0 | 2 | 0 | **0** |
| `portal_return_detail.xml` | 10 | 8 | 0 | 2 | 0 | **0** |
| **Tổng** | **15** | **13** | **2** | **6** | **1** | **0** |

**37 call site component, 0 chỗ dựng khung tay.** Màn Bù hàng đã đi hết qua component ⇒
D6 chỉ còn việc sửa **phân cấp bên trong**, không được dựng lớp thứ ba đè lên.

⚠️ **Fork SC↔DL — đã chốt.** Sheet BH-008 ghi *"card về `CMP-SC-001` variant record"*, nhưng
D5f đã đưa chính card này về `wj_data_list` variant `detail-card`, và D5h.2 vừa vá xong hồi quy
*thẻ trắng lồng thẻ trắng*. Bọc thêm một `wj_surface_card` quanh mỗi record là **tái tạo đúng
hồi quy vừa vá**. Chủ dự án chốt 10/09: **giữ theo fix mới nhất** — card ở lại `detail-card`,
D6b chỉ sửa phân cấp, **không đụng khung**. Ghi thành LIMIT trong ledger.

## 2. Ba đích, khoanh đúng call site

| Issue | Chỗ sửa thật | Chỗ KHÔNG phải sửa (đã kiểm) |
|---|---|---|
| **BH-007** | `portal_return_list.xml:265` (card mobile) + `wj-return-line` ở form (**D6c**) | Bảng PC `:114-133` **không in tên sản phẩm**. Chi tiết PC `:120` và mobile `:285` in tên nhưng **không có `nowrap`/`ellipsis`** ⇒ wrap tự do, không cắt. |
| **BH-008** | `portal_return_list.xml:255-262` — hai badge chung một `<span class="wujia-mreturn-row-badges">` | — |
| **BH-009** (D6c) | `portal_return_form.xml` — **0/14 label có `for`**, 0 control có `id`; control mobile cao 38px (nợ LIMIT từ D1) | — |

Nguồn nhãn tiến độ bù = `COMPENSATION_STATUS_LABELS`
(`controllers/portal.py:69-74`), đã truyền vào qcontext tên `comp_status_labels` (`:289`)
⇒ **tái dùng, không khai lại nhãn**.

## 3. 🔴 Ba chặn phải gỡ trước khi đo — không gỡ thì bảng đo là "Pass rỗng"

**(a) 35/35 phiếu bù hàng có `product_id` RỖNG.** `product_id` là related+store **readonly**
từ `sale_order_line_id` (`wujia_return_request.py:71-75`); seed D5 ghi thẳng
`'product_id': products[i]` nên ORM **bỏ qua** và tính lại ra `False`. Card rơi vào nhánh
fallback `issue_type_id.name` ⇒ đo tên sản phẩm là **đo nhầm ô**. Cùng họ với 3 seed hỏng
lặng lẽ tìm thấy 05/09 — seed chỉ hỏng khi có ai chạy lại.

**(b) Không có tên nào đủ dài để tràn.** Tên sản phẩm dài nhất toàn DB = **25 ký tự**
("Topping Phô Mai Macchiato"), 0 tên song ngữ/CJK ⇒ `white-space:nowrap` **chưa hề cắt**.

**(c) 3/4 biến thể badge "Tiến độ bù" không có bản ghi.** `compensation_status` là computed
store từ `allocation_ids`; DB chỉ có 1 phiếu `partial`.

⇒ **`scripts/seed_d6_return_demo.py`** (mới): 3 sản phẩm mốc dài 17/39/91 ký tự có CJK, 1 đơn
gốc `draft`, 10 phiếu phủ **4/4 `compensation_status`** — lái bằng allocation thật
(`allocated_qty`, `delivered_qty`) chứ không ghi thẳng field computed. Mọi bản ghi mang dấu
`SEED-D6`, idempotent, **local-only**.

## 4. 🔴 Hai lỗi công cụ lộ ra khi dựng mốc đo — đã vá vào repo

**(a) `wj_measure.py` in ra bảng đo GIẢ khi login hỏng.** Mặc định `--password demo123` sai
(DB seed dùng `wujia@test123`): **78/78 ô redirect về `/web/login`**, mọi ô trả
`h=900 · card=1 · rec=0`, script vẫn ghi file và in `→ docs/d6-before.json`. Đúng bẫy
"Pass rỗng" của luật D4 #3 — chỉ dòng tổng `redirect ngầm: 78` tố cáo. Đã vá: **dừng ngay
trong `login()`** khi còn ở `/web/login`, và đổi mặc định thành `wujia@test123`. Kiểm chứng
bằng mật khẩu sai: guard nổ đúng.

**(b) Bundle `web.assets_frontend.min.css` trả 500 trên mọi DB copy.** `wujia_tea_d5h2`
**không có thư mục filestore**, nên 75 `ir_attachment` của bundle trỏ vào file không tồn tại
⇒ `FileNotFoundError` ⇒ **toàn bộ CSS của module không nạp**. Card hiện ra không có dáng, chữ
chồng nhau. Nguy hiểm ở chỗ: `_variables/_components/_pc_*` nạp bằng `<link ?v=>` nên **vẫn
chạy** — bảng đo vẫn ra `RULE 1 = 0`, `tràn ngang = 0`, histogram đẹp, chỉ **ảnh chụp mới tố
cáo**. Lại đúng bài học D3e. Gỡ bằng `DELETE FROM ir_attachment WHERE url LIKE '/web/assets/%'`
rồi restart; verify bundle 200 + đếm rule `.wujia-mreturn-row` = 13 trong bundle.

## 5. Nhánh `t-if` theo trạng thái (chọn bản ghi để đo)

Card mobile rẽ nhánh ở `resolution_type == 'compensation'` (`:256`) — badge tiến độ bù **chỉ
hiện** ở nhánh này, và chỉ khi `clbl[0]` khác rỗng. Ma trận seed phủ: 4 `compensation_status`
× 3 độ dài tên × 6 `state` ⇒ 5 card có **cặp** badge (đo được BH-008), 8 card tên tràn ở
390/360 (đo được BH-007).

## 6. Mốc đo "trước" — `docs/d6-before.json`

Toàn portal, 13 route × 6 khổ: **RULE 1 = 0 · tràn ngang = 0 · lỗi JS = 0 · redirect ngầm = 0**.
Histogram cỡ tiêu đề card `14.7×15 · 16×33 · 18×39 · 22×6 · 24×3`; nhịp header→body `8×3 · 12×33`.

`/portal/return`:

| Khổ | pageH | record trong viewport | bề mặt |
|---:|---:|---:|---:|
| 1440 | 1211 | 29 | 2 |
| 1024 | 1223 | 31 | 2 |
| 992 | 1223 | 31 | 2 |
| 991 | 3160 | 14 | 1 |
| 390 | 3251 | 14 | 1 |
| 360 | 3378 | 14 | 1 |

## 7. Guard mới `scripts/qa/wj_returncard.py` — mốc trước

`wj_datalist.py` đo *dáng*, `wj_nesting.py` đo *lồng nhau*; **cả hai mù với phân cấp bên
trong card** — đúng loại lỗ đã để lọt hồi quy D5h.2. Guard mới trả lời 3 câu: tên sản phẩm mấy
dòng / có cắt ngay dòng 1 không · hai badge có cùng hàng không · hai ô metadata có thẳng cột không.

| Khổ | card | cắt ngay dòng 1 | cặp badge | badge **cùng hàng** | bố cục metadata | vi phạm |
|---:|---:|---:|---:|---:|---:|---:|
| 991 | 20 | 0 | 5 | **5** | **2** | 6 |
| 390 | 20 | **8** | 5 | **5** | **2** | 14 |
| 360 | 20 | **8** | 5 | **5** | **2** | 14 |
| | | | | | **TỔNG** | **34** |

Bố cục metadata `2` = hai bộ `left` khác nhau `(31, 122)` và `(31, 165)`: ô thứ hai trôi theo
độ dài nội dung ô thứ nhất (`Đơn gốc —` vs `Đơn gốc S00086`) vì `.wujia-mreturn-row-meta` là
`flex; gap:18px`. Đúng câu BA *"metadata dùng bố cục hai cột ổn định"*.

## 8. Việc còn lại của cụm

- **D6b** (lượt kế) — màn danh sách mobile: BH-008 trọn + nửa card của BH-007.
- **D6c** — màn form: BH-009 trọn + nửa dropdown của BH-007.
- **Kề cận, chưa thuộc issue nào:** `portal_return_detail.xml:188` (bảng đơn bù PC) và `:344`
  (`wujia-mreturn-so-row` mobile) là hai danh sách **chưa qua `wj_data_list`** — kiểm kê D5a
  không đếm chúng. Ghi nhận, **không tự làm** trong D6; đề xuất gộp vào lứa D7+.
