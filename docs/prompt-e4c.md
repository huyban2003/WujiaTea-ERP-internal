# Prompt phiên E4c — FilterBar `CMP-FB-001`, **wiring ngày + guard + ĐÓNG issue**

> Dán khối dưới đây sau `/wujia-start`. **Điều kiện tiên quyết: E4b1 + E4b2 đã xong**
> (`docs/e4b1-acceptance-matrix.md` — 9 thanh PC; `docs/e4b2-acceptance-matrix.md` — 6 thanh mobile
> + Đặt hàng về 38/44, FB-10 render-diff 0 lệch ở cả hai lượt).
> **E4c là lượt DUY NHẤT của cụm E4 được chạy `qa_sync.py`** và đưa issue lên `Ready for Retest`.

---

Làm **cụm E4c** — lượt cuối của `UI-FILTER-001` (STT 139, dòng 132 sheet, `Ready for Dev`, Owner Dev).
E4a/E4b1/E4b2 đã lo **dáng**; lượt này lo **hành vi lọc** rồi đóng issue.

## Phạm vi

### A. Màn Thi mobile — migrate **VÀ** wire trong cùng một lượt (chốt của chủ dự án 19/09)

`wujia_portal_exam/views/portal_exam.xml:127` là khối demo `wj-filter-dates--compact` dựng tay,
**2 ô ngày không có `name`** nên bấm tìm không gửi gì — đây chính là lỗi BA nêu *"mobile Đăng ký thi
ngày chưa áp dụng"*. E4b2 **cố ý để nguyên** vì chủ dự án chốt *"làm chuẩn, phiên này không ổn thì
phiên sau, miễn là giải quyết tới nơi"* — cấm đẻ knob tạm `fb_demo` trong component rồi phiên sau gỡ.

E4c phải làm **một lần**: thay khối demo bằng `t-call wujia_portal_layout.wj_filter_bar`
(`fb_platform='m'`, `fb_action='/portal/exam'`, `fb_dates`) **và** nối đúng tham số controller.
Controller **đã sẵn sàng**: `wujia_portal_exam/controllers/portal.py:290` nhận `date_from`/`date_to`
và `_parse_date` + `_local_day_start` đã lọc theo `request_date` — nghĩa là **chỉ thiếu markup**.

Kèm quyết định về `fb_dates={'kind': 'text'}`: màn Thi (PC) đang giữ ô ngày **dạng chữ** từ E4b1 để
không đổi hành vi sớm. E4c phải **chốt một kiểu cho cả hai viewport** (khuyến nghị: `type=date` như
8 màn còn lại) và ghi rõ vào matrix; nếu bỏ `kind='text'` thì **gỡ luôn knob** khỏi component và
test `test_kind_text_giu_duoc_o_ngay_dang_chu_cua_man_thi` — không để knob mồ côi.

### B. Ngày ngược: 200 + báo lỗi, không im lặng trả 0 record

**Tái hiện bằng Playwright TRƯỚC, đọc controller SAU** (luật cụm E). Đã có sẵn nơi làm đúng để
bắt chước — dùng lại, không viết kiểu thứ tư:

| Màn | Trạng thái hiện tại |
|---|---|
| Thông báo | ✅ `date_error = ERROR_MESSAGES['INVALID_DATE_RANGE']` (`controllers/portal.py:164`) |
| Lịch sử mua hàng | ✅ `filter_error=ERR_DATE_RANGE` (`:258`) |
| Đổi trả | ✅ gộp cả ngày sai định dạng lẫn ngày ngược (`:152`) |
| **Giao hàng** | ❓ chưa thấy nhánh ngày ngược — tái hiện rồi vá |
| **Thi** | ❓ nt (sau khi A nối xong mới đo được) |
| **Báo cáo** | ❓ nt |

Thông điệp đi qua slot `fb_error` của component (`wj-filter-error`), **không** đẻ vùng thông báo mới.
**Không** đổi bộ điều kiện lọc — FB-10 vẫn là chân lý, đo lại bằng render-diff.

### C. Đổi lọc → về trang 1; phân trang giữ lọc

Dùng `build_pager` (E3 — nguồn duy nhất, đã kẹp `?page=99` về trang cuối). Kiểm cả hai chiều:
lọc mới mà còn `?page=3` ⇒ rơi vào trang rỗng; bấm sang trang 2 mà mất `date_from` ⇒ mất lọc.

### D. Guard + đóng issue

- Guard `scripts/qa/wj_filterbar.py` (mở rộng `wj_formcontrol.py` của D6c) + **HTTP test**:
  `from > to` → **200 + thông điệp**, không phải 0 record im lặng; đổi lọc → `page=1`.
- Đối chiếu **từng gạch đầu dòng** cột `Kết quả mong muốn` của STT 139 (đọc CSV, dòng tuyệt đối) —
  ≥90% → ghi `docs/qa-issue-ledger.yaml` → `cd scripts/ba_spec && python3 qa_sync.py --dry-run` →
  `--apply` → verify CSV đúng ID dòng vừa ghi. **Dev không tự đặt `Done`**, chỉ `Ready for Retest`.

**Ngoài phạm vi:** toàn bộ dáng PC/mobile (E4b1/E4b2 — đụng lại là hồi quy) · 2 call site Khảo sát
(`wujia_portal_inspection`) **defer vĩnh viễn** (luật 08/09) · nhịp trang 16px (xem "Nợ mang sang").

## Nợ mang sang từ E4b2 (phải nhắc trong matrix, KHÔNG tự sửa trong E4c)

**`.wj-filter-card { margin-bottom: 16px }` chồng lên `gap: 8px` của khung trang** ⇒ khoảng cách
*thanh lọc → danh sách* là **24px** trong khi mọi cặp thẻ khác 8px (trái luật G2 "nhịp chỉ đến từ
gap"). Nợ có từ **E4a**, áp lên **cả 7 màn** dùng `.wj-filter-card`; E4b2 chỉ làm nó lộ ra ở màn Báo
cáo (cao thêm 14px). Gỡ 16px là đổi nhịp 7 màn một lúc ⇒ **việc của cụm nhịp E5**, không phải E4c.

## Luật bắt buộc (giữ nguyên từ E4b1/E4b2)

1. **FB-10**: không thêm/bớt điều kiện lọc nào. Đo bằng `scripts/qa/wj_filterbar_inventory.py`
   **chế độ render** (`--base … --portal-login em.hcm --routes … --widths … --json` + `--diff`),
   quét tĩnh sau migrate là **mù**.
2. Không đụng `wujia_portal_inspection` · `wujia_franchise*` · `wujia_mobile_*` (code anh Thái).
3. Không hardcode hex (`var(--wujia-*)`), **comment tối đa 1 dòng**, không đẻ modifier mới khi cái
   có sẵn đủ dùng.
4. Đặt test đúng chủ theo **F5b**: quét chéo module → `wujia_portal_base/tests/`; hợp đồng component
   → `wujia_portal_layout/tests/`; hành vi controller → test của chính module đó.
5. Test mới **mutation-proof**: mỗi mũi phá đỏ đúng test của nó, harness `assert s != before`.
6. Kết thúc: bump version **mọi module bị đụng** (bẫy D4) + `?v=` của CSS nạp bằng `<link>` tay
   (`wujia_portal_layout/views/assets.xml`, `_components.css` hiện `1302`).

## Nghiệm thu (ngưỡng ≥90%, đo bằng máy)

Dựng lại đúng bộ E4b2, chỉ đổi tên (DB copy **có 2 module Khảo sát như UAT** + chép
`data/filestore/`; **không** đụng `wujia_tea_19`/8019; luôn truyền `--http-port` tường minh;
**không** `pkill -f "<cổng>"`):

| # | Phép đo | Ngưỡng |
|---|---|---|
| 1 | FB-10 render-diff trước/sau | **0 lệch** |
| 2 | HTTP test ngày ngược ở **mọi màn có ngày** | 200 + thông điệp · **0 màn im lặng trả rỗng** |
| 3 | Đổi lọc → `page=1`; sang trang giữ lọc | đúng ở mọi màn có phân trang |
| 4 | Màn Thi mobile: lọc ngày **thật sự áp dụng** | số bản ghi đổi đúng theo khoảng ngày (Playwright, có dữ liệu thật) |
| 5 | `wj_measure --diff` ≥13 route × 5 khổ | 0 tràn ngang · 0 lỗi JS · 0 mất record · mọi lệch giải trình được |
| 6 | Mốc PC **và** mobile của E4b2 | không đổi ngoài phần cố ý của lượt này |
| 7 | `-u <mod gộp> --stop-after-init` | RC=0, 0 ERROR mới |
| 8 | Suite | 0 đỏ — **bắt buộc** `--log-handler "odoo.tests.result:INFO"` |
| 9 | `check_layers.py` | 3 R1–R5 + 2 R7 có sẵn, không thêm |
| 10 | Mutation | mỗi mũi đỏ đúng guard của nó |

## Bốn cái bẫy đã trả giá — đừng trả lần hai

1. **`log_level=warn` nuốt dòng tổng kết test** (`0 failed…` là INFO) ⇒ luôn thêm
   `--log-handler "odoo.tests.result:INFO"`. Mất 3 lần chạy lại ở E4b1.
2. **Harness mutation bị kill giữa chừng để lại file đã phá trong cây mã** — E4b2 dính đúng một lần
   (`id="wj-sup-mchips2"` nằm lại, suite đỏ ở lần chạy sau). Bản đã vá ở
   `scratchpad/e4b2/mutations.py` có `atexit` + `SIGTERM/SIGINT` phục hồi; **đừng** bắt `SIGHUP`
   (nohup đang vô hiệu nó — bắt lại là tự giết mình khi shell thoát).
3. **`closest('a, b, c')` trả tổ tiên gần nhất khớp BẤT KỲ selector nào, và khớp cả chính nó** —
   hai công cụ đo (`wj_filterbar_inventory.py`, `wj_formcontrol.py`) đều báo vùng chạm 38 thay vì 44
   vì lý do này. Đã vá ở E4b2; nếu viết `wj_filterbar.py` mới thì **kế thừa cách đo đã vá**.
4. **zsh không tách từ khi expand biến** ⇒ `--routes $R` gửi **một** chuỗi khổng lồ, script chạy xong
   vẫn "Pass" với 1 route giả. Dùng mảng: `R=(…)` rồi `--routes "${R[@]}"`, và **luôn** kiểm số route
   trong JSON trước khi tin kết quả.

## Chốt lượt

- Đây là lượt **được phép** đóng issue: ledger → `qa_sync.py --dry-run` → `--apply` →
  `Ready for Retest` (không `Done`).
- Ghi `docs/e4c-acceptance-matrix.md`, cập nhật `docs/e4-filter-inventory.md` §4 (E4c ✅) và một mục
  vào `docs/f-progress.md`.
- Commit + push `main`, ghi rõ lệnh `-u` gộp. **Không tự deploy UAT.**
- Cuối phiên trình bày một vòng nghiệp vụ.
