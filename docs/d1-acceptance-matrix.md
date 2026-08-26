# D1 — bảng đối chiếu acceptance (UAT-BH-001 · 003 · 005 · 006)

**Ngày đo:** 2026-08-25 · **Môi trường:** DB copy cô lập `wujia_tea_d1`, port 8065
(KHÔNG đụng `wujia_tea_19`/8019) · **Harness:** Playwright + chromium (env `odoo`),
1920×1080 và 391×844 · **Kết quả:** **26/26 Pass (100%)**.

Build: `-u wujia_portal_return,wujia_sale,wujia_portal_layout --stop-after-init` → RC=0.
Test: `--test-tags wujia_return_d1,wujia_return_ct` → **0 failed, 0 error / 39 test**
(6 test D1 mới + 33 test hồi quy).
Hồi quy: lưới B4 **286/286 PASS** · tab-walk a11y `/portal/return` 2 viewport sạch.

⚠️ Khi chạy trên DB copy phải thêm `--db-filter='^wujia_tea_d1$'`: `config/odoo.conf` ghi
cứng `dbfilter = ^wujia_tea_19$`, thiếu cờ này thì `HttpCase` bị đăng xuất giữa chừng và
4 test controller fail vì môi trường chứ không phải vì code (đã trả giá 1 lần trong phiên).

---

## UAT-BH-001 — không tạo được SO bù (High)

**Gốc rễ:** các field wizard khai `readonly=True` ở tầng Python ⇒ web client **không gửi lại**
khi `create` (`_getChanges` bỏ field readonly không `force_save`) ⇒ wizard lúc bấm nút mang
nhóm rỗng/0.0 ⇒ `_lock_and_revalidate()` luôn `raise UserError("Dữ liệu đã thay đổi…")`.
Không phải race condition. Sửa: readonly chuyển về **view + `force_save="1"`**, và
`action_confirm` **tự dựng lại nhóm + rải FIFO từ recordset sống** (`_live_buckets()`),
không tin dữ liệu client gửi lên.

Đo bằng trình duyệt thật (`d1_bh001.py`): mở list "Compensation requests" → chọn 2 yêu cầu đã
duyệt → Actions → *Process compensation* → *Create compensation SO*. TRƯỚC = tạm ghi arch view
đã gỡ hết `force_save` (đúng trạng thái BA gặp), SAU = arch bản vá; mỗi lần một context mới.

| Yêu cầu (cột "Kết quả mong muốn") | Đo được | Pass |
|---|---|---|
| Tạo đúng **1 SO bù** | TRƯỚC: 0 SO (dialog "Dữ liệu đã thay đổi"). SAU: đúng 1 SO `S00227` cho 2 yêu cầu cùng cửa hàng | ✅ |
| **Giá trị 0** | `amount_total = 0.0`, cả 2 dòng `price_unit = 0.0`, state `sent` | ✅ |
| **Đúng sản phẩm** | dòng 1 `D1 Hồng Trà Đài Loan KHÔNG Đường - 台灣無糖紅茶`; dòng 2 `D1 Trà sữa thùng` | ✅ |
| **Đúng đơn vị giao bù** | ca ĐVT trùng: `2.0 kg` (20kg ÷ 10). Ca ĐVT khác: `2.0 Units` = floor(25kg ÷ 10) | ✅ |
| **Tạo allocation tương ứng** | `RTN/26/00096 → 20.0`, `RTN/26/00097 → 20.0`, cùng trỏ `S00227`; phần lẻ 5kg còn `unallocated_qty = 5.0` | ✅ |
| **Không phát sinh lỗi stale data** | 0 dialog lỗi, 0 JS pageerror ở lần SAU | ✅ |
| **Idempotent — thao tác lại không tạo trùng** | Yêu cầu đã hết quyền lợi rơi khỏi `_is_eligible` ⇒ mở wizard lần 2 báo "Không có yêu cầu hợp lệ", không sinh SO thứ 2 (`test_reprocess_does_not_create_duplicate_order`) | ✅ |
| Wizard cũ/đã đổi dữ liệu phải bị chặn | Đổi trạng thái yêu cầu sau khi mở wizard → `UserError`, không tạo allocation (`test_stale_wizard_is_rejected`) | ✅ |

**Chống tái phát:** `test_view_keeps_force_save_on_every_readonly_field` quét arch, fail ngay
nếu có field `readonly` nào thiếu `force_save`; và `action_confirm` báo lỗi kỹ thuật rõ ràng
nếu nhóm về rỗng. Bộ test mới được chứng minh là **có ý nghĩa**: stash bản vá rồi chạy lại →
1 failed + 4 error / 6.

## UAT-BH-003 — màn "Đơn bù hàng" hiện SO demo `REF0001…REF0010` (High)

**Gốc rễ:** domain action đã đúng (`[('is_return_order','=',True)]`) và dữ liệu cũng đúng —
UAT **thật sự chưa có SO bù nào** vì BH-001 chặn tạo. `REF0001…` là **sample data của Odoo**:
list view mặc định của `sale` khai `sample="1"`, tập kết quả rỗng thì `SampleServer` dựng bản
ghi giả *cạnh* empty state → đúng cái mâu thuẫn BA thấy. Sửa: view list riêng
`view_wujia_return_order_list` (`sample="0"`, `create="false"`) và gắn vào action qua `view_ids`.

| Yêu cầu | Đo được | Pass |
|---|---|---|
| **Chỉ hiển thị SO bù** | Có dữ liệu thật: pager `1-3 / 3`, đúng 3 SO `is_return_order=True` trong khi DB có 35 SO | ✅ |
| **Không lộ SO thường/demo** | TRƯỚC (view `sale` mặc định): 10 dòng `REF0001…REF0010`. SAU (view riêng): 0 dòng giả, 0 chuỗi `REF####` | ✅ |
| **Empty state chỉ khi tập dữ liệu thực sự rỗng** | Gỡ cờ hết SO bù → 0 dòng + empty state hiện, không kèm dòng giả. Có dữ liệu → 3 dòng, empty state ẩn | ✅ |
| Cột đúng view mới | `Order Reference · Franchise store · Customer · Order Date · Total · Status` (view `sale` mặc định là 8 cột khác) | ✅ |

⚠️ **Bẫy đo, ghi lại để phiên sau khỏi trả giá:** web client cache action/view trong session, và
sau khi xoá attachment asset thì bundle cần ~8s để sinh lại. Đo TRƯỚC–SAU **phải dùng context
trình duyệt mới cho mỗi lần** và chờ đủ, nếu không kết quả "SAU" vẫn ra 10 dòng giả (hoặc 0
dòng khi thật ra có 3) và kết luận sai.

## UAT-BH-005 — bộ lọc PC/mobile không đồng nhất (Medium)

Controller vốn đã nhận đủ `q` · `state` · `date_from` · `date_to`; chỉ template thiếu control:
PC thiếu ô từ khoá, mobile thiếu select trạng thái. Bổ sung đúng 2 chỗ, **cùng query param**,
không đẻ logic mới.

| Yêu cầu | Đo được (1920×1080 · 391×844) | Pass |
|---|---|---|
| **Tìm kiếm từ khoá dùng được trên desktop** | PC: `input[name=q]` hiển thị, 383.8×26.7px, có `<label for>` | ✅ |
| **… và trên mobile** | Mobile: `input[name=q]` 285×38px, có placeholder + nhãn | ✅ |
| **Lọc trạng thái dùng được trên desktop** | PC: `select[name=state]` 383.8×28.1px | ✅ |
| **… và trên mobile** | Mobile: `select[name=state]` 333×38px, `aria-label="Lọc theo trạng thái"`, `onchange` submit | ✅ |
| **Kết quả trả về nhất quán** | 2 viewport có **cùng 4 control** (`q`/`state`/`date_from`/`date_to`) và **cùng 9 value** trong select | ✅ |
| Giữ lựa chọn sau khi lọc | 8/8 giá trị: HTTP 200, select giữ đúng value đã chọn | ✅ |
| Không vỡ layout | `overflow_x = 0` ở cả 2 viewport và ở cả 8 lần lọc, 0 JS pageerror | ✅ |
| Tới được bằng bàn phím | Tab-walk: đủ 4 control ở cả 2 viewport, **không** chạm control của khối đang bị ẩn | ✅ |

Placeholder ô từ khoá được thống nhất `Mã YC / mã đơn / sản phẩm` ở cả 2 khối — trước đó mobile
ghi `Tìm mã YC / mã đơn`, hụt so với domain thật (`q` còn tìm `batch_id.name`,
`product_id.name`, `product_id.default_code`).

**LIMIT:** control mobile đang cao **38px**, chưa đạt touch target 44–48px. Đây đúng phạm vi
**UAT-BH-009** (cụm D6), cố tình chưa đụng ở D1 để không trộn hai issue.

## UAT-BH-006 — mapping trạng thái sai/thiếu (Medium)

`STATE_LABELS` có **hai key cùng nhãn "Đang xử lý"** (`reviewing`, `processing`) và "Đang bù một
phần" là **pseudo-state** chỉ tồn tại trong `state_label()` nên không vào được filter. Sửa bằng
**một nguồn duy nhất** `FILTER_OPTIONS` + `state_filter_domain()`: `partial` →
`state='processing' AND compensation_status='partial'`; `processing` →
`state in (reviewing, processing)` **trừ** phần partial (domain Odoo 19:
`[A, B, '!', C]` = `A AND B AND NOT C`).

Dữ liệu đo: seed đủ 8 trạng thái cho cửa hàng của `anh.owner`, gồm cả 1 yêu cầu `processing` đã
phân bổ nhưng **chưa giao** và 1 yêu cầu `processing` **đã giao một phần** — đúng cặp khó.

| Yêu cầu | Đo được | Pass |
|---|---|---|
| Đủ 7 nhãn BA liệt kê | `Đã gửi · Đang xử lý · Đã duyệt · Đang bù một phần · Hoàn tất · Từ chối · Đã huỷ` có đủ trong select ở cả 2 viewport | ✅ |
| **Mỗi value một label duy nhất** | 9 option = 9 value phân biệt, 0 nhãn trùng chữ (trước đây 2 dòng "Đang xử lý") | ✅ |
| Bổ sung nhãn **"Đang bù một phần"** | Lọc `state=partial` → đúng 1 yêu cầu `RTN/26/00104` (`compensation_status='partial'`) | ✅ |
| Nhãn lọc = nhãn hiển thị (theo selection thực tế) | 8/8 nhãn: **mọi dòng trả về đều hiện đúng chữ của nhãn vừa lọc** | ✅ |
| Các nhãn **rời nhau** | `1+2+2+1+1+2+1+1 = 11` = tổng số dòng khi không lọc = 11 ⇒ không trùng, không sót | ✅ |
| `reviewing` gộp đúng vào "Đang xử lý" | Lọc `processing` → 2 dòng (`reviewing` + `processing` đã phân bổ), **loại** dòng partial | ✅ |

**Sai lệch có chủ đích so với danh sách BA (cần BA xác nhận khi retest):** thêm nhãn **`Nháp`**
(`draft`). BA liệt kê 7 nhãn nhưng portal thực tế **có** liệt kê yêu cầu nháp; thiếu nhãn này
thì tổng các bộ lọc không phủ hết dữ liệu (11 dòng chỉ lọc ra được 10). Nếu BA muốn ẩn nháp
khỏi danh sách thì đó là thay đổi nghiệp vụ, không phải sửa filter.

---

## Hồi quy

| Hạng mục | Kết quả |
|---|---|
| Lưới B4 (17 route × 2 breakpoint + 5 trang ngoài matrix × 2 + 6 chiều rộng) | **286/286 PASS** |
| Test tự động 2 module (`wujia_return_d1` + `wujia_return_ct`) | 39 test — 0 failed, 0 error |
| Tab-walk a11y `/portal/return` | PC + mobile: đủ control, 0 control ẩn nhận focus |
| JS pageerror / tràn ngang | 0 / 0 trên mọi trang đã đo |

Nhiễu môi trường đã loại trừ, **không** phải lỗi sản phẩm: (a) `web_tour.interactive.min.js`
404 và `ir_attachment._to_http_stream` `os.stat` lỗi — filestore không đi kèm khi copy DB, xoá
attachment asset là tự sinh lại; (b) `wujia_portal_remediation` "inconsistent states" — module
đã được gỡ có chủ đích từ trước.

## Tệp đã đổi

| Tệp | Nội dung |
|---|---|
| `wizards/compensation_process_wizard.py` | bỏ `readonly` tầng Python; thêm `_bucket_requests` / `_group_key` / `_live_buckets` / `_total_claim`; `action_confirm` rải FIFO trên recordset sống |
| `wizards/compensation_process_wizard_views.xml` | mọi field chỉ-đọc thêm `force_save="1"` (+ `unit_qty` ẩn cột) |
| `views/backend_return_request_views.xml` | view list riêng `sample="0"` + gắn `view_ids` vào action |
| `controllers/portal.py` | `FILTER_OPTIONS` + `state_filter_domain()` |
| `views/portal_return_list.xml` | ô từ khoá PC · select trạng thái mobile · thống nhất placeholder |
| `wujia_portal_layout/static/assets/css/_components.css` | thêm `.wj-filter-select` (class mới, không đụng selector cũ) — `?v=1176` |
| `tests/test_compensation_wizard_d1.py` | 6 test mô phỏng đúng đường web client |

---

## 🔁 Đo lại CHỈ-ĐỌC trên chính UAT SAU KHI DEPLOY (27/08/2026)

XML-RPC xác nhận **`wujia_portal_return 19.0.2.7.0` · `wujia_sale 19.0.4.3.0` ·
`wujia_portal_layout 19.0.32.4.0`** — cả 3 `installed`, khớp manifest trên đĩa.
Harness: `scratchpad/d1_uat_verify.py`. **Kết quả 27/28 Pass**, 1 Fail là **phát hiện thật**
(xem cuối mục).

🔴 **UAT-BH-001 CỐ Ý KHÔNG ĐO ở đây**: chạy wizard "Create compensation SO" sẽ **sinh SO +
allocation thật** trên server — vi phạm giới hạn QA §10 (không tạo đơn thật). Để BA retest.
Bằng chứng của BH-001 nằm ở phần đo trên DB copy phía trên (SO `S00227`, 8/8 Pass) + 6 unit test.

| Hạng mục | Đo trên UAT | Kết quả |
|---|---|---|
| **BH-005** PC có ô từ khoá `q` | 383.8×28.3px, có `<label for>` | ✅ |
| **BH-005** mobile có ô từ khoá `q` | 285×38px | ✅ |
| **BH-005** PC có select trạng thái | 383.8×30.4px | ✅ |
| **BH-005** mobile có select trạng thái | 333×38px, `aria-label="Lọc theo trạng thái"` | ✅ |
| **BH-005** cả 2 viewport có `date_from` + `date_to` | 1/1 ở cả hai | ✅ |
| **BH-005** placeholder ô từ khoá thống nhất | `Mã YC / mã đơn / sản phẩm` ở cả hai | ✅ |
| **BH-005** tràn ngang + `pageerror` | 0 / 0 ở cả 2 viewport | ✅ |
| **BH-006** 8 trạng thái, mỗi value một nhãn duy nhất | 8 value / 8 nhãn phân biệt (trước đây 2 dòng "Đang xử lý") | ✅ |
| **BH-006** đủ 7 nhãn BA liệt kê | `Đã gửi · Đang xử lý · Đã duyệt · Đang bù một phần · Hoàn tất · Từ chối · Đã huỷ` | ✅ |
| **BH-006** lọc từng trạng thái | 8/8 HTTP 200 **và giữ đúng lựa chọn** trong select | ✅ |
| **BH-006** các nhãn rời nhau, phủ hết dữ liệu | `2+0+0+2+0+0+2+0 = 6` = đúng 6 dòng khi không lọc | ✅ |
| **BH-003** danh sách "Compensation orders" | **0 dòng mẫu `REF####`**, 0 SO bù thật, empty state đứng một mình | ✅ |
| **BH-003** dùng view riêng của module | đúng **6 cột** `Mã đơn hàng · Cửa hàng nhượng quyền · Khách hàng · Ngày đặt hàng · Tổng · Trạng thái` (view `sale` mặc định là 8 cột, **không** có cột cửa hàng) | ✅ |

**Dữ liệu UAT lúc đo:** 12 yêu cầu bù hàng (cửa hàng 1: 2 `done` + 2 `submitted`; cửa hàng 2:
2 `approved`; **cửa hàng 3: 2 `approved` + 2 `draft` + 2 `rejected`**) · **0 SO bù**
(`is_return_order=True`) — đúng như BH-003 mô tả: UAT chưa từng tạo được SO bù vì BH-001 chặn.
⚠️ Vì vậy 4 trạng thái `submitted/processing/partial/done` **chưa có dữ liệu ở cửa hàng 3**
⇒ phép thử "nhãn rời nhau" mới phủ 3/8 trạng thái. Nhờ BA retest trên cửa hàng 1 để phủ nốt.

### 🔴 Phát hiện thật (1 Fail) — nhãn option "tất cả" lệch giữa PC và mobile

| Nơi | Chuỗi |
|---|---|
| PC (`portal_return_list.xml:42`) | `— Tất cả —` |
| Mobile (`portal_return_list.xml:187`) | `— Tất cả trạng thái —` |

8 nhãn trạng thái thật thì **khớp 100%** (đều sinh từ nguồn duy nhất `FILTER_OPTIONS` mà D1
dựng), riêng option rỗng bị **gõ tay ở hai chỗ** nên trôi chữ. Đúng loại lệch mà UAT-BH-005
đang dẹp, nhưng chỉ là chữ hiển thị, **không ảnh hưởng kết quả lọc** (cùng `value=""`).
**Chưa sửa** — chờ chủ dự án chốt vì sửa là phải deploy lại; đề xuất đưa vào chung chuyến
deploy của cụm D3.

⚠️ **3 lần harness sai, không phải code sai (L7/L9 lặp lại)**: (1) `b4_regression.py` login bằng
form `anh.owner` — UAT không dùng được, phải admin + POST authenticate; (2) đếm dòng bằng
selector đoán (`.wujia-mreturn-card`, `.wj-pc-table`) ⇒ ra **0 dòng, suýt kết luận "UAT rỗng"**,
tên thật là `table.wujia-content-card-table tbody tr` (PC) và `a.wujia-mreturn-row` (mobile);
(3) assert tên cột bằng tiếng Anh trong khi **UAT chạy `vi_VN`** ⇒ báo Fail giả.
