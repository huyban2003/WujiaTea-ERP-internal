# Prompt phiên E5 — ListCard `CMP-LC-001` (`UI-LISTCARD-001`, STT 136, dòng tuyệt đối **129**)

> Dán khối dưới đây sau `/wujia-start`. Điều kiện tiên quyết: **E4c đã xong**
> (`docs/e4c-acceptance-matrix.md`, `UI-FILTER-001` → `Ready for Retest`).
> E5 là cụm *tiêu thụ* D4 SurfaceCard / D5 DataList / E2 StatusBadge — **không dựng lớp khung thứ ba**.

---

Làm **cụm E5** — `UI-LISTCARD-001` (STT 136, dòng tuyệt đối **129** tab `5. Issue List`,
`Ready for Dev`, Owner Dev, Need BA Confirm = No). Đặc tả BA: **LC-01–LC-32** tại
`gid=488333015&range=A41:Q41` (BA đã gộp bảng riêng A44:E76 vào dòng này ngày 06/09 — mã LC giữ để
truy vết).

## Gốc rễ (đã soi ở phiên phân cụm, kiểm lại trước khi code)

D5 đã đưa 22 danh sách mobile về `wj_data_list` với variant `compact-row` (16) / `detail-card` (6) —
tức **dáng NGOÀI** của item đã chuẩn (cao 64–76 / 96–120, gap 8, r12). Cái D5 chưa làm là **anatomy
BÊN TRONG** item: tên trái + trạng thái phải, 2–3 hàng phụ, cột linh hoạt. Đó là việc của E5.

Đếm lại trước khi tin bảng:

```
grep -rcE "dl_variant\" t-value=\"'(compact-row|detail-card)'" custom/wujia_portal_*/views/*.xml
```

| File | số call site | Ghi chú mapping |
|---|---|---|
| `portal_home.xml` | 8 | **LC-23: Home preview GIỮ grouped rows** — chỉ đồng bộ token, không tách 1 record 1 card |
| `portal_exam.xml` | 3 | LC-19 — phải có bản ghi thật mới đo được |
| `portal_knowledge.xml` · `portal_delivery.xml` · `portal_debt.xml` | 2 mỗi file | LC-17 không state giả, giữ nhóm Nổi bật/Mới · LC-14 bỏ nhãn "Chuyến xe" + divider, đơn liên quan wrap · LC-21 retest bằng role được phép |
| `portal_support.xml` · `portal_return_list.xml` · `portal_history.xml` · `portal_notification.xml` · `portal_franchise_information.xml` | 1 mỗi file | LC-18 · LC-15 (nhãn "Ngày yêu cầu", **đủ năm**) · LC-13 · LC-16 (read state) |
| `wujia_portal_inspection` | — | LC-20 → **defer vĩnh viễn** (code anh Thái, luật 08/09) |

## Việc

1. **Field inventory TRƯỚC khi đụng markup** (LC-09/LC-18): mỗi route một bảng *trường đang hiển thị ·
   khổ màn · nguồn dữ liệu*. Đây là mốc để chứng minh **trường trước = trường sau**. Màn nào rỗng dữ
   liệu thì **gieo trước** (mở rộng `scripts/seed_d6_return_demo.py` / `scripts/seed_e4c_dates_demo.py`
   — idempotent, lái state bằng nghiệp vụ thật, **chỉ chạy máy local**). Support / Đăng ký thi / Công nợ
   chắc chắn cần gieo; BA cũng ghi rõ điều này ở cột Ghi chú.
2. **Một implementation + adapter nội dung theo route**, tuyệt đối không CSS theo route: slot chuẩn
   trong item của `wj_data_list` = `name / state? / meta rows / actions?`.
   Token BA: p12 · r12 · gap8 · header–body 8 · gap hàng 6–8 · title 15–16/600 · **badge 12** (variant
   compact của E2, đặt ở component) · metadata 13–14 · **không** divider/shadow/icon trang trí lớn.
   Trường ngắn cùng hàng, trường dài chiếm cả hàng, thiếu → "—"; **không** cắt mã/tiền/badge, **không**
   hạ cỡ chữ để vừa.
3. **Gutter danh sách mobile = 12** (Q2 đã chốt) — và **không** cộng dồn 12 + 16.
4. **Trả nợ nhịp G2 mang từ E4a/E4b/E4c sang**: `.wj-filter-card { margin-bottom: 16px }` chồng lên
   `gap: 8px` của khung trang ⇒ khoảng *thanh lọc → danh sách* thành **24px ở 7 màn**. Gỡ là đổi nhịp
   cả 7 màn cùng lúc nên đã hoãn tới đây; E5 là cụm nhịp danh sách nên **giải nợ này trong phiên**, đo
   trước/sau bằng `wj_measure` và ghi rõ 7 màn vào matrix.
5. **Guard `scripts/qa/wj_listcard.py`** — **mở rộng `wj_returncard.py` (D6b)**, không viết mới: 1 record
   = 1 khung (dùng lại định nghĩa "khung" của `wj_nesting.py`), tên trái / badge phải cùng hàng hoặc
   badge xuống hàng căn phải khi hẹp, không ellipsis mã, không tách chữ số tiền, **số field trước = sau**.
6. **Regression 8 khổ**: 320 · 360 · 390 · 430 · 991 · 992 · 1024 · 1440, kèm keyboard/touch ≥44 và
   thanh sticky không che record cuối. **Bảng PC và Home không đổi một byte DOM.**

## Ràng buộc

- Không đụng `wujia_portal_inspection` · `wujia_franchise*` · `wujia_mobile_*` (code anh Thái).
- Không đổi quyền / ngày / tiền / state / filter / pager / workflow — E5 chỉ là anatomy hiển thị.
- Không hardcode hex (dùng `var(--wujia-*)`), **comment tối đa 1 dòng**.
- DB copy **có 2 module Khảo sát như UAT** + chép `data/filestore/`; **không** đụng `wujia_tea_19`/8019;
  luôn truyền `--http-port` tường minh; **không** `pkill -f "<cổng>"` (mẫu khớp cả shell đang chạy).
- Test đặt đúng chủ theo **F5b**: hợp đồng component → `wujia_portal_layout/tests/`; quét chéo nhiều
  module → `wujia_portal_base/tests/`; hành vi của một màn → test của chính module đó.
- Suite phải chạy kèm `--log-handler "odoo.tests.result:INFO"` (mức `warn` **nuốt** dòng tổng kết).
- Mutation-proof: mỗi mũi phá đỏ đúng guard của nó; dùng lại harness `scratchpad/e4c/mutations.py`
  (`atexit` + `SIGTERM`/`SIGINT`, **không** bắt `SIGHUP`).

## Nghiệm thu (đo bằng máy, ngưỡng ≥90%)

| # | Phép đo | Ngưỡng |
|---|---|---|
| 1 | Field inventory trước/sau từng route | **0 trường mất**, 0 trường thêm |
| 2 | `wj_listcard.py` | 1 record = 1 khung ở mọi route; 0 ellipsis mã/tiền |
| 3 | `wj_nesting.py` | giữ **0** khung lồng khung |
| 4 | 8 khổ | 0 tràn ngang · 0 lỗi JS · 0 màn mất record |
| 5 | Nhịp *lọc → danh sách* 7 màn | **24 → 16**, đo trước/sau |
| 6 | Home + bảng PC | **0 byte DOM đổi** |
| 7 | `-u` gộp `--stop-after-init` | RC=0, 0 ERROR mới |
| 8 | Suite | 0 đỏ |
| 9 | `check_layers.py` | đúng 3 R1–R5 + 2 R7 có sẵn, không thêm |
| 10 | Mutation | mỗi mũi đỏ đúng guard của nó |

Rồi đối chiếu **từng gạch** cột `Kết quả mong muốn` của STT 136 (5 nhóm gạch, đã trích ở trên), đạt
≥90% mới ghi `docs/qa-issue-ledger.yaml` → `cd scripts/ba_spec && python3 qa_sync.py --dry-run` →
`--apply` → **verify bằng `export?format=csv`, đối chiếu cột ID của chính dòng 129** (bẫy row-offset
§12). Dev **không** đặt `Done`, chỉ `Ready for Retest`.

## Chốt lượt

- Bump version **mọi module bị đụng** + `?v=` của file CSS nào có sửa.
- Ghi `docs/e5-acceptance-matrix.md` + một mục vào `docs/f-progress.md`; commit + push `main`,
  ghi rõ lệnh `-u` gộp. **Không tự deploy UAT.**
- Cuối phiên trình bày một vòng nghiệp vụ.
