# Prompt phiên E5c — khép `UI-LISTCARD-001` (STT 136, dòng tuyệt đối **129**)

## Bối cảnh

E5a dựng component (`wj_list_card` + `wj_list_card_row` ở `wujia_portal_layout`, 2 route mẫu) ·
**E5b1** 6 call site rủi ro thấp · **E5b2** 5 call site cuối (Thi ×3 + Công nợ ×2).
⇒ **22/22 call site đã về component, ruột card coi như xong.** E5c **không migrate thêm màn nào**;
việc của nó là **trả nợ nhịp/gutter**, **regression 8 khổ**, chốt 2 câu hỏi BA, rồi **đóng issue**.

Đọc trước: `docs/e5b2-acceptance-matrix.md` (§"Còn treo sang E5c" + §"Câu hỏi cho BA") ·
`docs/e5b1-acceptance-matrix.md` · `docs/prompt-e5.md` (bảng nghiệm thu gốc 10 phép đo).

## Việc

### 1. Nợ G2 — nhịp *thanh lọc → nội dung* 24 → 16 (7 route)

Đo lại ở E5b2, **cả 7 route đều đúng 24px**, nguồn giống hệt nhau:
`.wj-filter-card { margin-bottom: 16px }` cộng `gap: 8px` của khung trang.

| Route | filter → phần tử kế | phần tử kế |
|---|---|---|
| `/portal/purchase-history` · `/portal/notification` · `/portal/support` · `/portal/return` · `/portal/knowledge` · `/portal/exam` | **24** | `.wj-ajax-slot` |
| `/portal/delivery` | **24** | `.wujia-mdelivery-body` |

Gỡ `margin-bottom` ở **một chỗ duy nhất** (khung), đừng vá từng màn. Đo trước/sau bằng
`wj_listcard_inventory.py` (trường `rhythm.filter_to_next`) — **không** dùng `filter_to_list`: giữa
thanh lọc và danh sách còn `count-meta`/`section-header` nên con số đó là 24/52/55/70, che mất nhịp thật.

### 2. Nợ LC-07 + LC-08 — đệm item và gutter trang

- Đệm item đang là **`12px 14px`**; LC-07 ghi **12**. 14 ngang là để bù gutter — nên sửa **một lượt**
  cùng món dưới, không tách hai phiên.
- Gutter trang đo được **16px** hai bên (`wj_listcard_inventory` → `gutter`), `prompt-e5.md` §3 ghi
  BA chốt **12** ở Q2. Chốt lại với chủ dự án **trước khi đổi**: đổi gutter là đổi bề ngang của
  **mọi** màn danh sách, không riêng ListCard.
- Ràng buộc: gutter là việc của **trang**, ListCard không được tự thêm (LC-08).

### 3. Hai câu hỏi BA còn treo — phải có câu trả lời mới đóng issue

1. **Ô icon `.wj-lc__tile` 32×32** (Thông báo · Kiến thức · danh sách nhân sự màn Thi) — LC-06/LC-07
   ghi "không icon trang trí lớn trước tên". Giữ hay bỏ? Bỏ thì Thông báo mất tín hiệu màu theo loại.
2. **Dải cao hai variant không còn phủ hết thực tế** (số đo E5b2):
   - `detail-card` khai 96–120 · thực tế card nhân sự **có ghi chú kết quả** = **146px**;
   - `compact-row` khai 64–76 · thực tế card hoá đơn 2 hàng phụ = **80px** — rơi đúng **khe giữa
     76 và 96**, không variant nào nhận.
   Đề xuất mang sang: nới `compact-row` → **64–84**, `detail-card` → **96–150**. LC-02 đòi auto-height
   nên **không** ép cứng chiều cao để lấy số đẹp.

### 4. Regression 8 khổ (điều kiện đóng issue)

**320 · 360 · 390 · 430 · 991 · 992 · 1024 · 1440** trên **12 route** của `wj_listcard.py`
(E5b1/E5b2 mới chạy 5 khổ mobile). Kèm: keyboard/touch ≥44 · thanh sticky không che record cuối ·
0 tràn ngang · 0 lỗi JS · 0 màn mất record.

### 5. Vá điểm mù của mốc đóng băng

`/portal/order` hiện là **mốc rỗng**: trang không có `.wj-data-list` lẫn `table.wj-data-table` nên
"chữ ký DOM trước = sau" ở đó **không chứng minh được gì** (E5b2 ghi nhận). E5c đổi sang chữ ký
**cả trang** cho route này, hoặc bỏ nó khỏi danh sách đóng băng và nói rõ lý do.

### 6. Đóng issue

Đối chiếu **từng gạch** cột `Kết quả mong muốn` của STT 136 (5 nhóm gạch), đạt **≥90%** rồi mới:
`docs/qa-issue-ledger.yaml` → `cd scripts/ba_spec && python3 qa_sync.py --dry-run` → `--apply` →
**verify bằng `export?format=csv`, đối chiếu cột ID của chính dòng 129** (bẫy row-offset §12).
Dev **không** đặt `Done`, chỉ `Ready for Retest`. **Không tự deploy UAT.**

## Không làm trong E5c

- **LC-20** (Khảo sát) — **defer vĩnh viễn**: code anh Thái, luật 08/09.
- **LC-27** — lệch dữ liệu giữa spec và thực tế, chỉ **ghi nhận**, không sửa.
- **LC-23** — Home preview giữ grouped rows, **cấm** migrate.
- Không migrate thêm call site nào: 22/22 đã xong ở E5b.

## Ràng buộc (giữ nguyên toàn cụm)

- Không đụng `wujia_portal_inspection` · `wujia_franchise*` · `wujia_mobile_*` (code anh Thái).
- Không đổi quyền / ngày / tiền / state / filter / pager / workflow — E5 chỉ là anatomy hiển thị.
- Không hardcode hex (dùng `var(--wujia-*)`), **comment tối đa 1 dòng**.
- Đo trên DB local `wujia_e4b1`, server đo **8090/8091** (+ `--dev=assets` nếu sửa JS/CSS — không có
  cờ này thì bundle nằm trong `ir.attachment` và **không** đổi theo file), server test **8098/8099**;
  **không** đụng `wujia_tea_19` / cổng 8019; luôn truyền `--http-port` tường minh;
  **không** `pkill -f "<cổng>"` (mẫu khớp cả shell đang chạy).
- Seed **chỉ chạy local**, idempotent, lái state bằng nghiệp vụ thật.
- Test đặt đúng chủ theo **F5b**: hợp đồng component → `wujia_portal_layout/tests/`; quét chéo nhiều
  module → `wujia_portal_base/tests/`; hành vi một màn → test của chính module đó.
- Suite luôn chạy kèm `-u` (tests `wujia_franchise` còn import file đã xoá) và
  `--log-handler "odoo.tests.result:INFO"` (mức `warn` **nuốt** dòng tổng kết); log xoay sang
  `logs/<năm>/<tháng>/<ngày>.log`, đọc ở đó chứ không đọc stdout.
- Mutation-proof: mỗi mũi đỏ **đúng** guard của nó; khuôn `scratchpad/e5b2/mutations.py`.
  **Guard phải đếm đủ số call site**, không đếm "có ít nhất một" (bài học M1 của E5b2).
- Call site nào có **JS đọc DOM** thì phải **chạy thật bằng trình duyệt** — guard markup không thay
  được (bài học E5b2: thẻ "đã chọn" của wizard hiện tiêu đề rỗng).

## Nghiệm thu

| # | Phép đo | Ngưỡng |
|---|---|---|
| 1 | Nhịp *lọc → phần tử kế* 7 route | **24 → 16**, đo trước/sau, 7/7 route |
| 2 | Đệm item + gutter | đúng số BA chốt lại, 0 cộng dồn |
| 3 | `wj_listcard.py` 12 route × **8 khổ** | 0 vi phạm anatomy, 0 cắt mã/tiền |
| 4 | Field inventory trước/sau 14 route | 0 giá trị mất, 0 lệch số record |
| 5 | Home + bảng PC + 7 route chưa đụng | chữ ký DOM **trước = sau** |
| 6 | `wj_nesting.py` · `wj_datalist.py` · `wj_measure.py` | 0 / 0 / 0 tràn · 0 lỗi JS |
| 7 | Suite 10 module kèm `-u` | 0 đỏ (mốc E5b2: **653 tests**) |
| 8 | `check_layers.py` | đúng 3 R1–R5 + 2 R7 có sẵn, không thêm |
| 9 | Mutation | mỗi mũi đỏ đúng guard của nó |
| 10 | Đối chiếu `Kết quả mong muốn` STT 136 | **≥90%** |

## Chốt lượt

- Bump version mọi module bị đụng + `?v=` của file CSS có sửa (`_components.css` đang `1312`).
- `docs/e5c-acceptance-matrix.md` + một mục vào `docs/f-progress.md`.
- Commit + push `main`, ghi rõ lệnh `-u` gộp. **Không tự deploy UAT.**
- **Đây là phiên đóng issue**: ledger → `qa_sync.py` → verify CSV. Sau đó mới tính tới cụm kế
  (`docs/next-session-clusters-F.md` §2 — E6 · E7 · E8 + đề xuất cụm EmptyState).
