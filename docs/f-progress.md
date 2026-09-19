# Cụm F — Nhật ký tiến độ

Mỗi phiên F / FR **bắt buộc** ghi 1 mục ở cuối file này trước khi kết thúc (mới nhất ở dưới),
rồi đánh ✅ ở bảng Trạng thái §2 `docs/next-session-clusters-F.md`. `/wujia-start` đọc mục cuối
để biết phiên kế và việc dở dang. Phiên dừng giữa chừng vẫn ghi, Trạng thái để `◐`.

## Mẫu

```
## <Fx> — <tên phiên> · <dd/mm/yyyy> · <máy: Mac/Linux>
- Kết quả: ✅ xong | ◐ dở (dừng ở bước …) | ⛔ chặn (lý do …)
- Đã làm: <gạch đầu dòng ngắn, theo nghiệp vụ>
- Commit: <hash — message> | chưa commit
- Deploy: chưa | UAT <version>
- Số đo: <test x/y, B4 x/286, check_layers n vi phạm, wj_measure diff …>
- Lệch plan / quyết định mới: <… hoặc "không">
- Nợ để lại: <… hoặc "không">
- Phiên kế: <Fy> — việc cần biết trước: <…>
```

---

## Nhật ký

## Lập plan — review + plan cụm F · 17/09/2026 · Mac
- Kết quả: ✅ xong
- Đã làm: chốt ADR-027 (4 tầng, L3a portal_base); review source (A/B/C/D); plan + prompt F0–F13, FR-*.
- Commit: `b33723e` — docs: ADR-027 kiến trúc tầng module + plan cụm F chuẩn hoá portal
- Deploy: chưa
- Số đo: xem §1 plan (176/380 nhóm class ở layout, 30 rule đổi dáng, 89 route)
- Lệch plan / quyết định mới: Issue List tạm dừng đến FR-A3; không đụng module anh Thái
- Nợ để lại: mục D (wujia_mobile_core bị nghiệp vụ depend) chờ chủ dự án + anh Thái chốt
- Phiên kế: F0 — cần DB copy giống UAT (có cài inspection) chạy port riêng

## F0 — Công cụ đo + mốc trước chuẩn hoá · 17/09/2026 · Mac
- Kết quả: ✅ xong
- Đã làm: 2 script mới `scripts/qa/css_owner.py` (CSS nào của màn nào đang nằm trong layout; rule module nào
  đè dáng component) + `scripts/qa/check_layers.py` (luật tầng ADR-027, report-only); dựng DB `wujia_f0`
  giống UAT (25/25 phiên bản module, có Khảo sát + mobile_core + MuK, vi_VN/th_TH, 14 seed); chụp mốc
  205 ô × 2 tài khoản; thay Phụ lục A/B bằng số script → `docs/f0-baseline.md`, `docs/f0-baseline/`.
- Commit: chưa commit
- Deploy: chưa (không có gì để deploy — 0 dòng code module)
- Số đo: test 520/520 · B4 286/286 · wj_measure anh 130 ô / em 75 ô, 0 tràn, 0 lỗi JS (3 HIERARCHY
  notification/1 PC + 10 redirect `/vi/portal/inspection` là có sẵn) · css_owner 193 nhóm CSS màn / 41 rule
  đổi dáng · check_layers 4 vi phạm (3 mục D + order_window thiếu portal_base)
- Lệch plan / quyết định mới: chủ dự án chốt dùng số script (A 176→193, B 30→41; F4 duyệt 41 rule). Tên
  script mới KHÔNG tiền tố `wj_` (chủ dự án yêu cầu) ⇒ `css_owner.py`; script cũ giữ tên.
- Nợ để lại: env Mac cần `PyJWT` (đã cài tay, chưa ghi requirements); DB `wujia_tea_19` local cũ + mật khẩu
  demo sai — dùng `wujia_f0` cho mọi phiên F; B4 viết cứng ID chi tiết (`/delivery/3`, `/support/40`…) chỉ
  đúng trên DB đã seed.
- Phiên kế: F1 — bật server `wujia_f0` port 8099 (lệnh ở `docs/f0-baseline.md` §1), suite đối chứng = 520/520;
  so ảnh/số bằng `wj_measure --diff docs/f0-baseline/measure_anh.json after.json`.

## F1 — Controller: vá an toàn + gọi đúng workflow · 17/09/2026 · Mac
- Kết quả: ✅ xong
- Đã làm: gửi hỗ trợ không còn lỗi 500 khi id rác, không nhận danh mục đã lưu trữ, đính kèm chỉ nhận ảnh/PDF ≤5MB ≤6 tệp
  (lỗi thì không tạo ticket); đổi cửa hàng + đổi ngôn ngữ không redirect ra site ngoài (helper `safe_local_path` ở
  `portal_layout/controllers/utils.py`, base import); yêu cầu cập nhật thông tin không lộ lỗi nội bộ; thông báo lỗi trong
  query string được encode (info_request cancel, hồ sơ); phiếu đổi trả gửi từ portal đi qua `action_submit()` ⇒ có dòng
  chatter "Yêu cầu đã được gửi", số ảnh tối thiểu 1 nguồn `MIN_IMAGES_BEFORE_SEND` (vẫn kiểm trước khi tạo).
- Commit: chưa commit
- Deploy: chưa — cần `-u wujia_portal_layout,wujia_portal_base,wujia_portal_support,wujia_portal_info_request,wujia_portal_return`
  (layout 19.0.51.0.1 · base 19.0.7.17.1 · support 19.0.3.21.1 · info_request 19.0.1.10.1 · return 19.0.3.3.1)
- Số đo: test 12 module portal **534/534** (520 đối chứng F0 + 14 mới, tag `wujia_f1`) · mutation **11/11** đỏ (M2b ban đầu
  sống — thêm case cùng host `//evil.com`) · wj_measure diff anh 130 ô / em 75 ô = 0 thay đổi, 0 ô mất record · B4 286/286 ·
  check_layers 1 vi phạm (order_window R4).
- Lệch plan / quyết định mới: helper redirect đặt ở layout (không phải portal_base/utils) vì layout không depend base — chủ
  dự án duyệt; giữ kiểm ≥3 ảnh trước create. Đối chứng dùng run F0 520/520: merge `c80a6e2` (sau mốc `355cae0`) không đụng
  module portal. check_layers 4→1: merge `c80a6e2` của anh Thái đã chuyển mobile ra `wujia_mobile_*` ⇒ **mục D đã xử lý**.
- Nợ để lại: (1) chatter đổi trả chỉ chứng minh bằng test HTTP — `wujia_f0` không có đơn xác nhận ≤10 ngày để gửi tay; (2)
  `attach_files_to_record` kiểm MIME theo header client (return tự sniff), support dùng header; (3) support tạo-rồi-xoá khi
  đính kèm lỗi làm hụt 1 số sequence (cùng khuôn info_request/return); (4) màn support PC không hiện khối lỗi (chỉ mobile có,
  có sẵn); (5) **code anh Thái**: `wujia_franchise/tests/__init__.py` còn import `test_wujia_franchise_mobile` đã xoá ⇒ chạy
  test không `-u` chết import — chỉ báo.
- Cập nhật sau phiên: mục D ghi ✅ ở `next-session-clusters-F.md` §1.D + skill `/wujia-start` (F7 hết bị chặn); báo Thái 2 lệch nhỏ.
- Phiên kế: F2 — CSS 8 màn nhỏ ra khỏi layout; DB `wujia_f0` đã `-u` 5 module F1 (mốc wj_measure không đổi, dùng tiếp baseline F0).

## F2 — CSS 8 màn nhỏ ra khỏi `portal_layout` · 17/09/2026 · Mac
- Kết quả: ✅ xong
- Đã làm: F1 commit+push `aebcd56`. Dời 70 rule (Kiến thức 34 · Lịch sử 21 · Hỗ trợ 14 · `wj-pc-noti-head-actions` 1) từ
  `_components.css`/`_pc_components.css` lên đầu file CSS module (module đã có file trong `web.assets_frontend`, nạp sau layout);
  dọn comment mồ côi; 4 guard test đọc thẳng `_components.css` trỏ sang file module (d3 DEAD_CSS, d4, d5). Bộ công cụ
  `scripts/qa/css_move/` (plan/apply/semdiff/cstyle/cdiff).
- Commit: `dab6f4c` (đã push — ghi chú sửa ở phiên F3)
- Deploy: chưa — `-u wujia_portal_layout,wujia_portal_knowledge,wujia_portal_purchase_history,wujia_portal_support,wujia_portal_notification`
  (layout 19.0.51.0.2 · knowledge 19.0.3.14.1 · purchase_history 19.0.3.12.1 · support 19.0.3.21.2 · notification 19.0.2.14.1; `?v=1294`)
- Số đo: semdiff 309/309 khớp · cstyle full computed style + ép :hover/:active/:focus 2550 phần tử × 28 lượt (2 tài khoản × 390/1440)
  = 0 khác · wj_measure anh 0 lệch, em 2 route lệch = dữ liệu (đối chứng CSS HEAD y hệt) · 0 ô mất record · ảnh 390/1440 chỉ lệch
  dữ liệu (lượt xem, nhãn dịch) · B4 286/286 · suite 12 module 534/534 · css_owner 380→335 nhóm.
- Lệch plan / quyết định mới: (1) KHÔNG tách class khỏi `:is()` ở `_interaction.css` — đặc hiệu :is() = đối số mạnh nhất (0,4,0),
  tách ra tụt ⇒ hover hàng compact-row đổi `primary-soft` → rgba .04; chủ dự án đồng ý để F4. ⇒ debt/exam/return/delivery (chỉ có
  mặt trong :is()) = 0 rule dời. (2) `.wujia-mknow-article > .wj-card-header{margin-top:16px}` giữ layout: đang thua
  `.wj-card-header--any.wj-card-header--compact{margin:0 0 8px}` (sau, cùng 0,2,0), dời xuống là thắng ⇒ card +16px (cstyle bắt).
  (3) `wujia-msheet-open` (JS bottom sheet layout) + `wj-filter-select` (FilterBar layout) là component — css_owner gán nhầm.
  (4) Luật `auto_install: True` cho module ghép thuần (Thái hỏi) — ghi skill mục "chưa ghi ADR".
- Nợ để lại: 22 nhóm mang tên 8 màn còn ở layout, đều giải trình (18 trong :is(), 1 rule chết, 2 component, +inspection) → F4.
  Bẫy môi trường: bundle cache cũ sau sửa CSS ⇒ xoá `ir_attachment` `/web/assets/%` + restart; deploy UAT `-u` + restart là đủ.
  Mốc F0 em.hcm `/portal` + `/portal/order` đã trôi — F3 lấy mốc mới đầu phiên.
- Phiên kế: F3 — prompt đã viết lại ở `next-session-clusters-F.md` §3 (quy trình cstyle đo cascade bắt buộc).

## F3 — CSS Đặt hàng + Home ra khỏi `portal_layout` · 17/09/2026 · Mac
- Kết quả: ✅ xong
- Đã làm: dời 160 rule từ `_components.css` lên đầu file CSS module — Đặt hàng 111 (+ `@keyframes wujia-msubmit-spin`)
  → `wujia_portal_sale/static/src/css/portal_order.css`, Home 49 → `wujia_portal_base/static/src/css/portal_dashboard.css`;
  gỡ 3 `@media {}` rỗng + comment mồ côi do chính lượt dời để lại (2 `@media` rỗng có từ trước giữ nguyên). 5 chỗ
  `test_d4_surface_card.py` đọc CSS trỏ sang file module. Bộ `scripts/qa/css_move/` nhận cấu hình `CSSMOVE_CFG` (TARGET/KEEP/
  MODCSS/ACC/PREF/SETUP), `cstyle` chịu được trang long-polling (Đặt hàng không bao giờ `networkidle`), `cdiff` có
  `CDIFF_IGNORE` cho hình học chạy theo đồng hồ (thanh tiến độ khung giờ).
- Commit: chưa commit
- Deploy: chưa — `-u wujia_portal_layout,wujia_portal_sale,wujia_portal_base`
  (layout 19.0.51.0.3 · sale 19.0.4.17.1 · base 19.0.7.17.2; `_components.css?v=1295`)
- Số đo: semdiff 711/711 khớp · cstyle 7030 phần tử × 20 lượt (2 tài khoản × 390/1440 × `/portal`, `/portal/order`, giỏ có 2 dòng,
  `/portal/order/submitted/<id>`, `/portal/order/rejected`) + ép hover/active/focus = **0 khác** (2 lượt sau) · wj_measure
  anh 130 ô 0 lệch, em 1 ô `/portal`@360 −25 = đồng hồ (cùng code đo lại 3 lần ra 2772 = mốc) · 0 mất record · 0 tràn · 0 lỗi JS ·
  ảnh chỉ lệch đồng hồ khung giờ/shimmer logo/thanh tải · B4 286/286 · suite 12 module 534/534 · css_owner nhóm 1 màn 149→46
  (sale 78→7, base 49→17).
- Lệch plan / quyết định mới: GIỮ ở layout, có giải trình — `wj-pc-acct-*` + `wujia-maccount-*` (view layout profile/đổi mật khẩu
  dùng chung), `wj-empty-state-body` (biến thể `--row` của EmptyState), `wujia-content-card-empty` (họ content-card),
  `.content-wrapper > .wujia-mhome` (`_wujia_theme.css`), 10 nhóm chỉ còn trong `:is()` `_interaction.css` → F4. Mốc wj_measure
  lấy mới đầu phiên (F0 đã trôi ở `/portal` + `/portal/order` trên code chưa sửa). Luồng giỏ đo bằng dựng giỏ qua
  `/portal/order/cart/add` + trang kết quả của đơn có sẵn — KHÔNG gửi đơn thật để giữ dữ liệu mốc.
- Nợ để lại: comment trong module mới chỉ ghi nguồn dời (comment nghiệp vụ gốc không đi theo rule — như F2); chưa chạy
  mutation cho 5 guard D4 đã trỏ lại; log test do `wujia_core` chuyển vào `<logfile dir>/<năm>/<tháng>/`.
- Phiên kế: F4 — duyệt 41 rule đổi dáng + danh sách `:is()` (dừng giữa phiên xin duyệt).


## F4 — Duyệt rule module viết đè component chung · 17/09/2026 · Mac
- Kết quả: ✅ xong
- Đã làm: bước 1 lập `docs/f4-override-review.md` (44 rule, tắt từng rule trong trình duyệt + 30 ảnh `docs/f4-img/`), chủ dự
  án duyệt: (b) theo đề xuất không cần báo BA · hover một màu primary-soft · dọn toàn bộ `:is()` · eyebrow. Bước 2: xoá 13 rule
  chết + rule chết mknow + 14 rule lệch về chuẩn; biến thể layout mới `wujia-badge--sm`, `wj-pc-badge--sm`,
  `wj-card-header--eyebrow`; sửa component (tiêu đề trang PC 800 thật sự áp, con trỏ select lọc, màu chữ hàng `<a>`
  detail-card); Công nợ "THÔNG TIN CHUYỂN KHOẢN" SectionHeader → CardHeader eyebrow; `_interaction.css` liệt kê theo
  component + class đánh dấu `wj-state-surface` ở XML (không còn tên màn), nhóm Khảo sát tách rule riêng, gạch chân dùng
  `wj-richtext`; bỏ hover rgba .04 của compact-row. 8 rule giữ có comment `F4(c)`.
- Commit: xem git log — refactor(F4)
- Deploy: chưa — `-u wujia_portal_layout,wujia_portal_base,wujia_portal_debt,wujia_portal_delivery,wujia_portal_exam,
  wujia_portal_knowledge,wujia_portal_notification,wujia_portal_purchase_history,wujia_portal_report,wujia_portal_return,
  wujia_portal_sale,wujia_portal_support` (layout 19.0.51.0.4 · `?v=` components 1296 / pc_components 1295 / interaction 1293;
  11 module còn lại +1 patch)
- Số đo: css_owner --overrides đổi dáng **44 → 9** (cả 9 là loại giữ có ghi chú) · cstyle mốc 2 lượt ổn định (A: 1 dòng
  Kiến thức lệch 0.36px đồng hồ; B: 0) → sau sửa chỉ khác đúng bảng §8 review · hover/active ép trên MỌI phần tử ứng viên
  (script mới `scratchpad hovall.py`): 0 mất/thừa, chỉ `wj-debt-inv` + `wujia-mexam-rrow` (div không bấm được) mất hover ·
  B4 286/286 · suite 12 module **540/540** (có 6 test mới `wujia_f4`; số 537 ghi ở phiên F4 là sai, FR-B đếm lại: 534 trước F4 + 6 = 540).
- Lệch plan / quyết định mới: **exam727 (a) → (c) nợ FR-B** — Vuexy `table th{16px !important}` thắng cỡ 14 của component ở
  mọi bảng PC 8 màn (kể cả Khảo sát); sửa ở component = đổi 8 màn, chưa duyệt. Sửa component tiêu đề trang PC làm **Khảo
  sát PC** tiêu đề 700→800 (đúng số component). Hàng `<a>` Đổi trả + thẻ Thi mobile chữ thừa kế #243742→#111827. Nhãn chuyển
  khoản cao +2.5px (thẻ vẫn 150px). cstyle khoá phần tử theo class ⇒ thêm class marker phải chuẩn hoá khoá khi so (cd2.py).
  7 guard cũ (C8/D3/D5) sửa theo rule/call site đã xoá.
- Nợ để lại (FR-B): (1) cỡ đầu bảng PC 16 vs 14; (2) bề mặt không bấm được vẫn có hover qua marker để giữ 0 khác —
  `wujia-mdash-card` ×33 (card thông tin), hàng `div.wujia-mdash-row` Home/Hỗ trợ/Thông tin cửa hàng, skeleton giao hàng,
  `div.wujia-mhome-kpi`.
- Phiên kế: ★FR-B — review toàn khối B (F2+F3+F4), prompt §3 "Prompt phiên review ★".

## ★FR-B — Review toàn khối B (F2+F3+F4) · 18/09/2026 · Mac
- Kết quả: ✅ xong — khối B đạt (0 lỗi mới), **và sửa luôn 2 khoản nợ F4** theo chốt của chủ dự án.
- Đã làm:
  - Đo **đi suốt F0 → `52c7650`** lần đầu; xem **205 cặp ảnh** trước/sau bằng mắt.
  - Chứng minh độc lập "dời CSS là phép giữ nguyên": nguyên tử CSS 282 file, F2+F3 **121902 → 121902, 0/0**.
  - **Trả nợ F3**: mutation 5 guard D4 → **5/5 đỏ**.
  - **Nợ (a)** — tìm ra gốc rễ khác chẩn đoán của F4: không phải Vuexy mà là `table th{16px!important}`
    trong `style.css`, **có từ commit đầu dự án**. Gỡ hẳn luật đó; Đặt hàng 13→14; bảng thô Đổi trả cho
    class riêng `wj-return-ptable` + 14px; **xoá 4 rule `!important` của F4(c)** ở màn Thi (chỉ tồn tại để
    chống luật chung). Kết quả **16/17 bảng = 14px** (bảng kết quả Thi vốn 13px, cố ý).
  - **Nợ (b)** — rút luật từ template `wj_surface_card` (có `sc_href` ⇒ `<a>`; không ⇒ `<div>` thuần)
    rồi **gỡ marker ở 40 chỗ** (27 qua `sc_class` + 13 trên `<div>`), 0 dòng CSS bị đụng.
  - **Nợ (c)** — ép hiện trạng thái rỗng Công nợ bằng `?q=zzzkhongcogi`: sau F4 **khớp chuẩn component,
    không phải lỗi**; chỉ cần BA biết khi retest.
  - Thêm **3 guard mới** + mutation từng cái (3/3 đỏ, hoàn tác xanh): cấm marker ở `sc_class`, cấm marker
    trên thẻ không bấm được, cấm luật quét theo thẻ cho đầu bảng.
  - Dọn 3 việc nhỏ: sửa 537→540 trong doc F4 · bỏ số dòng đã lệch ở 12 comment "dời từ" · xoá 2 `@media`
    rỗng + 5 comment mồ côi (chứng minh **0 nguyên tử CSS thay đổi**).
- Commit: **chưa commit** (không được yêu cầu).
- Deploy: chưa — `-u wujia_portal_layout,wujia_portal_base,wujia_portal_sale,wujia_portal_return,
  wujia_portal_delivery,wujia_portal_support,wujia_portal_exam,wujia_portal_notification,
  wujia_portal_purchase_history,wujia_portal_knowledge` (layout `19.0.51.0.7`, `?v=` `_components.css`
  **1297** · `style.css` **1300**).
- Số đo: suite **543/543** (540 + 3 guard mới), 0 failed 0 error · B4 **286/286** · `css_owner
  --layout-domain` 20 nhóm cả 20 trong danh sách giữ · `--overrides` 9 rule cả 9 có `F4(c)` ·
  `check_layers` 1 vi phạm đã biết (order_window, F7) · hover: **0 chỗ không bấm được còn marker**,
  110 chỗ mất hover **100% là `<div>`**, 0 chỗ bấm được bị mất, 0 chỗ thừa · đầu bảng PC **16/17 = 14px** ·
  `wj_measure` vs F0: 8 ô lệch, **cả 8 là hệ quả của sửa 14px**, chứng minh bằng A/B tiêm lại luật cũ
  (Hỗ trợ @992 hàng 89→72px × 20 hàng = −340px; Yêu cầu thông tin −51px = 3 hàng × 17px) · bump
  version/`?v=` 0 sót · 0 selector đụng Khảo sát ngoài ca đã duyệt.
- Lệch plan / quyết định mới:
  - **Bắt 3 con số sai trong nhật ký F4**: suite 537 → **540**; nợ (a) "8 màn" → **14/17 bảng**;
    nợ (b) "×33" → **40 chỗ trong XML** (`wujia-mhome-kpi` phần lớn là `<a>` bấm được).
  - Chủ dự án chốt (a) = **14px theo chuẩn thiết kế**, (b) = **gỡ hết**.
  - 2 guard cũ phải sửa theo: `test_screen_surfaces_carry_the_marker` 4→3 (ô KPI Công nợ là `<div>`);
    `test_d3_card_header.test_store_name_became_subtitle...` bỏ chuỗi marker khỏi xpath.
- Nợ để lại:
  - **Bổ sung `/portal/franchise-information` (và rà toàn bộ `@http.route`) vào danh sách route đo** —
    màn này KHÔNG có trong mốc F0 nên 4 chỗ hover sai lọt qua cả F4 lẫn vòng soi tay của FR-B.
  - Mỗi màn cần **1 route ép ra trạng thái rỗng** trong danh sách đo (bài học từ nợ (c)).
  - Bảng kết quả Thi giữ 13px (cố ý) — BA xác nhận khi retest nếu muốn đồng bộ 14.
- Phiên kế: **F5** — khung thuần (menu, test, redirect). Cần biết trước: (1) rà danh sách route đo
  trước khi đo gì; (2) phiên nào đổi đường dẫn/nội dung guard đọc CSS-XML thì **cùng phiên** chạy
  mutation; (3) zsh dùng `${=R}` tách route; (4) sửa file bằng script Python phải mở `newline=''`.

---

## F5a — Khung `portal_layout` thuần: menu về module + redirect + vá điểm mù mốc đo (18/09/2026)

- Phạm vi: mục 0 (mốc đo) + mục 1 (menu) + mục 3 (redirect) của phiên F5. **Mục 2 (dời 94 test
  cross-module / 215 assert của layout về module) tách sang F5b** — chốt với chủ dự án đầu phiên.
- Làm được:
  - **Vá điểm mù mốc đo trước khi sửa dòng code nào**: kiểm kê **97 `@http.route`/13 module** bằng máy
    (`docs/f5-route-inventory.md`), mốc F0 chỉ đo 30 route → mốc F5a đo **46 (anh.owner) + 28 (em.hcm)**,
    thêm `/portal/franchise-information` + **11 route ép trạng thái rỗng** (đọc controller tìm tham số
    chắc ra rỗng, không đoán `?q=`). Mốc mới lộ ngay **4 lỗi HIERARCHY cũ chỉ thấy ở trạng thái rỗng**
    + 1 ở `/portal/exam/register` (tồn tại từ trước F5a, ghi nợ, không sửa trong phiên này).
  - **Công cụ mới `scripts/qa/nav_dump.py`**: đổ ra danh sách CÓ THỨ TỰ của mọi link điều hướng
    (sidebar PC · bottom-nav · sheet "Thêm" · header mobile · navbar PC) theo route × khổ × tài khoản —
    thứ `wj_measure` không đo được. Đây là bằng chứng chính của mục 1.
  - **Menu về đúng module sở hữu route**: xoá `pc_sidenav.xml` (`layout_sidenav_figma` priority 99
    `position="replace"` — 10 link cứng); khung còn `<ul>` + 2 tiêu đề nhóm có `id` làm neo + mục
    Tài khoản (route của chính khung). 9 module khai mục sidebar, 4 tab + 7 dòng sheet, 2 mục header
    mobile, 2 mục PC (navbar dropdown + shell Tài khoản) — tổng **24 mục điều hướng đổi chủ**.
  - **Redirect legacy** 3 route v14 về đúng module đích (301 giữ nguyên); `redirects.py` của khung xoá.
  - **Guard mới + mutation**: `check_layers.py` thêm **R6 "khung không biết route Wujia"**;
    `test_f5_frame_routes` (arch trong DB), `test_f5_menu_ownership` (danh sách vàng 11 mục + quyền sở
    hữu qua `ir.model.data` + active theo route + nút "Thêm"), 9 test module, 3 test 301 → **+28 test**.
- Commit: **chưa commit** (không được yêu cầu). Deploy: chưa.
- Số đo: `nav_dump` **0 lệch** về href/nhãn/icon/active/thứ tự (chỉ thêm thuộc tính `id` cho 2 tiêu đề
  nhóm làm neo) · `wj_measure` **0 ô lệch, 0 ô mất record** · ảnh **136/148 giống hệt**, 12 ảnh còn lại
  là đồng hồ đếm ngược / lượt xem / pha hoạt hình biểu đồ · suite **571/571** (543 + 28), 0 failed 0 error ·
  B4 **286/286** · `check_layers` R6 **0**, vi phạm cũ vẫn đúng 1 (order_window, F7) · mutation **5/5 đỏ,
  hoàn tác xanh** · `ir.ui.view` mồ côi sau `-u`: **0** · bump version **13 module**, 0 sót (không sửa CSS
  ⇒ không đụng `?v=`). Chi tiết: `docs/f5a-acceptance-matrix.md`.
- Lệch plan / quyết định mới:
  - **Đính chính plan §1.A3**: `pc_sidenav_inspection` của anh Thái có priority **101** > 99 nên mục
    "Khảo sát" VẪN hiện — sidebar PC thật đang có **11 mục**, không phải 10. Câu hỏi "cho hiện mục Khảo
    sát?" hoá ra vô nghĩa (nó đang hiện sẵn) ⇒ nghiệm thu chặt hơn: diff = 0 kể cả mục đó.
  - **`<li>` phải nằm trong ARCH, không sinh lúc render**: bản đầu dùng component sinh cả `<li>` bằng
    `t-att-id` ⇒ neo `//li[@id='nav_item_exam']` của anh Thái không tìm thấy gì, mọi trang 500. Khuôn
    cuối: module viết thẳng `<li id=... t-attf-class=...>`, thân mục gọi component của khung.
  - **Nút "Thêm" phải dùng CỜ, không dùng danh sách tiền tố**: tab Trang chủ khớp tuyệt đối `/portal`,
    nếu góp `/portal` vào danh sách tiền tố thì mọi route con đều "khớp" ⇒ "Thêm" không bao giờ sáng.
  - **Xoá view khỏi data file là chưa đủ**: Odoo dọn record mồ côi ở CUỐI lượt nạp nên 6 view chết vẫn
    bị validate giữa chừng và làm **gãy `-u`**. Phải xoá bằng `migrations/<version>/pre-*.py` (5 module).
  - Sửa nhỏ kèm đo lại: `pc_preview.xml` trỏ form về route không tồn tại `/portal/pc-preview`
    (route thật `/portal/_pc-preview`).
  - Không đụng 1 dòng code anh Thái; 2 inherit của anh (sidebar Khảo sát, dòng sheet Khảo sát) còn
    nguyên vị trí, chứng minh bằng `nav_dump`.
- Nợ để lại:
  - **F5b**: dời test cross-module của `wujia_portal_layout` về module sở hữu màn; guard nhiều module
    về `wujia_portal_base`; tổng số assert không được giảm.
  - **4 lỗi HIERARCHY ở trạng thái rỗng + 1 ở `/portal/exam/register`** (có từ trước F5a) — vá ở phiên
    dọn màn tương ứng hoặc gộp vào cụm EmptyState.
  - Bẫy đã cắn, ghi lại cho phiên sau: (1) **không `git checkout <file>`** để hoàn tác mutation khi cây
    còn thay đổi chưa commit — mất sạch sửa trong file đó; (2) khôi phục `.py` bằng `mv/cp` giữ `mtime`
    ⇒ Python dùng lại `__pycache__` của bản đã phá, phải `rm -rf __pycache__` trước khi chạy lại.
- Phiên kế: **F5b** — dời test cross-module (prompt ở `docs/next-session-clusters-F.md` §3).

---

## F5b — Test của khung về đúng chủ: `portal_layout` hết biết màn nghiệp vụ (18/09/2026)

- Phạm vi: mục 2 của phiên F5 (tách ra từ F5a). **Không tính năng mới, không đổi 1 pixel.**
- Làm được:
  - **Kiểm kê bằng máy trước khi dời** — công cụ mới `scripts/qa/test_ownership.py` (AST): mỗi hàm test
    → file · class · số assert · module bị đọc · đọc DB hay đọc đĩa. Kết quả: khung có **329 test /
    711 assert**, trong đó **236 test / 517 assert** là cross-module (94 đọc thẳng trong thân hàm +
    142 thừa kế hằng cấp class như `CALL_SITES`). Bảng đầy đủ: `docs/f5b-test-inventory.md`.
  - **Phân loại từng TEST (không phải từng class)** thành a/b/c + nhóm bàn giao, rồi dời thật:
    **a** 40 test ở lại khung nhưng đổi sang **fixture dựng trong chính tests của khung** ·
    **b** 24 test về module sở hữu màn (Công nợ, Đăng ký thi, Home) ·
    **c** 155 test quét-nhiều-module về `wujia_portal_base` (L3a), **giữ nguyên một hàm, không cắt thành 12** ·
    **BG** 17 test của màn Khảo sát gom vào `portal_base/tests/test_handover_inspection.py` để nhóm Khảo
    sát dời về — không ghi một dòng nào vào code anh Thái (chủ dự án chốt: *"cái nào của Khảo sát thì bên
    Khảo sát tự sửa"*).
  - **Helper dùng chung `portal_base/tests/css_probe.py`** thay vì chép ba bản cho debt/exam.
  - **Khung nay cài được một mình**: `wujia_portal_layout` thêm `depends` thiếu `http_routing`.
- Commit: F5a + F5b (tách 2 commit), push `main`. Deploy UAT: **không** (chưa được yêu cầu).
- Số đo (chi tiết `docs/f5b-acceptance-matrix.md`):
  - **Phép đo quyết định — DB `wujia_f5b` tạo mới, CHỈ cài `wujia_portal_layout`: 0 failed, 0 error /
    129 test.** Trước phiên này con số đó là *không chạy nổi*.
  - Suite 15 module portal trên `wujia_f0` kèm `-u`: **572/572**, 0 failed 0 error (F5a 571 + 1).
  - Assert **không giảm**: toàn hệ 1548 → **1549** (khung 711 → 261; 15 file mới giữ 451).
    Khung: **cross-module 236 → 0**.
  - B4 **286/286** · `check_layers` R1–R5 đúng 1 vi phạm cũ (`order_window`, chờ F7), **R6 = 0**.
  - `wj_measure --diff` **0 lệch, 0 ô mất record**; `nav_dump --diff` chỉ còn dư âm F5a (thuộc tính `id`
    của 2 `<li>` tiêu đề menu), href/nhãn/thứ tự/active/badge khớp tuyệt đối.
  - Mutation **5/5** đỏ khi phá, xanh khi hoàn tác. Bump version 4 module, 0 sót.
- Lệch plan / quyết định mới:
  - **Số cross thật là 236, không phải 94**: plan đếm hẹp (chỉ thân hàm). Một test nằm trong class có
    `CALL_SITES` liệt kê 12 module cũng là cross. Đếm lại bằng máy mới ra đúng.
  - **Công cụ đếm phải bỏ docstring**: sau khi dời, khung vẫn báo 115 test cross — vì câu *"đã dời sang
    `wujia_portal_base`"* trong mô tả bị tính là phụ thuộc. Đếm cả docstring là tự lừa mình.
  - **Phép đo quyết định bắt được 2 lỗi thật** mà suite 572 test trên `wujia_f0` không bao giờ thấy:
    (1) khung inherit `http_routing.404` mà không khai `http_routing` — trên DB đủ module nó có sẵn nhờ
    module khác; (2) `test_c10_lang` giả định `vi_VN` bật sẵn ⇒ nay tự `_activate_lang` trong `setUp`.
  - **Test khung không được import `portal_base`**: bản phân trang cũ mượn `build_pager` — thay bằng
    fixture dict viết trong chính tests của khung, và mutation M5 (phá `aria-label` của template) chứng
    minh fixture thật sự render template chứ không assert vào không khí.
  - Guard màn Khảo sát **không mutation** (phải sửa CSS của anh Thái mới phá được — luật cụm F cấm);
    thay bằng kiểm dương 14/14 đường dẫn tĩnh trỏ tới file có thật.
- Nợ để lại:
  - `portal_base/tests/test_handover_inspection.py` — **anh Thái dời trọn file về
    `wujia_portal_inspection/tests/`**, nội dung assert giữ nguyên.
  - 4 lỗi HIERARCHY ở trạng thái rỗng + 1 ở `/portal/exam/register` (từ trước F5a) — vẫn còn.
  - Dư âm F5a trong mốc đo: 2 thuộc tính `id` trên tiêu đề menu ⇒ nên chụp lại baseline ở phiên FR-A3.
- Phiên kế: **FR-A3** — review cổng khối A/B, kết luận có mở lại Issue List hay không.

## ★FR-A3 — Review cổng cụm F (F0→F5b): mở lại Issue List (18/09/2026 · Mac)

- Mục tiêu: lần ĐẦU đo đi suốt **mốc F0 → HEAD `33240c0`** (FR-B mới đo tới `52c7650`; F5a/F5b đo bằng
  mốc F5 riêng) rồi kết luận có mở lại Issue List hay không. Không làm tính năng.
- Chốt đầu phiên của chủ dự án: commit + push, **KHÔNG deploy UAT** · sửa lỗi HIERARCHY trạng thái rỗng
  nếu < 30 dòng · độ phủ đo **đầy đủ** (bộ F0 26+15 route × 5 khổ + bộ F5 46+28 route × 2 khổ + ảnh).
- **Kết luận: cổng ĐẠT — mở lại Issue List**, thứ tự E4b → E4c → E5 → E6 → E7 → E8.
- Làm được:
  - **25 phép đo Pass** (`docs/f-review-A3.md` §2). Suite **574/574** · phép đo quyết định (DB trắng chỉ
    cài khung) **129/129** · B4 **286/286** · `wj_measure` mốc F5 → HEAD **0 lệch** · ảnh 148 cặp **0
    khác biệt chưa duyệt** · `nav_dump` chỉ còn dư âm `id` (184+112, **100%**) và **đã chụp lại mốc**.
  - **Mutation xuyên khối 10/10** — trả nợ mutation cho F1 (3 guard an toàn, chưa phá lại từ 17/09),
    FR-B (2), F5a (2), F5b (1) + 2 guard mới của phiên.
  - **Bắt được 2 lỗi TẦNG thật, có từ trước cụm F, chưa công cụ nào thấy**: `portal_base` (L3a) gọi
    `_is_within_order_window`/`_user_now_hours` của `portal_order_window` (L3b) ⇒ Home **500** khi cài
    riêng; `portal_layout` (khung) gọi `_get_accessible_franchise_ids` của `wujia_franchise` (nghiệp vụ)
    ⇒ ACL ảnh **500**. Vá bằng **guard `hasattr`/`getattr`** (không thêm depend — thêm là vi phạm R2/R5
    thật), + 2 test giả lập module tắt bằng descriptor ném `AttributeError`.
  - **`check_layers` có luật R7 mới**: quét AST tìm lời gọi method của module không depend mà không có
    guard. Đây là vá cho chỗ mù của chính công cụ (R1–R5 chỉ đọc manifest). Chạy 2,5s.
  - **5/6 "lỗi" HIERARCHY trạng thái rỗng là thước đo báo nhầm**: khối rỗng căn giữa (icon + tiêu đề) và
    tiêu đề bản ghi ở trang chi tiết không phải "nhãn phụ". Chứng minh bằng ảnh, ghi vào bảng đã duyệt,
    **không sửa pixel**. Chỉ 1 lỗi thật: `wj-exam-pc-sectitle--sm` 18 → **16px** (áp chốt 04/09 "khối con
    trong card = 16px" — 3 anh em của nó đã 16px từ F4, sót đúng chỗ này).
  - Mốc mới `docs/fra3-baseline/` (4 measure + 2 nav + 4 route + check_layers) — sạch, hết dư âm F5a.
- Lệch số so với nhật ký (đếm lại bằng máy — bài học #2 của FR-B):

  | Nhật ký | Máy |
  |---|---|
  | `check_layers` 1 vi phạm | **2** (thêm R3 chéo kênh `wujia_mobile_portal_info_request`) |
  | css_owner nhóm 1 màn ở layout: 20 | **26** (F5a dời markup menu ⇒ đổi quy kết, KHÔNG có CSS mới) |
  | css_owner rule đổi dáng: 9 | **8** (FR-B đã xoá 1) |
  | EmptyState "~124 chỗ viết tay" | **92 viết tay / 124 đã dùng component** |

- Nợ để lại:
  - **`wujia_portal_base` không tự test được một mình** (41 failed / 81 error trên DB chỉ có base): 6 file
    test quét cả cổng, 2 trong số đó có **từ trước cụm F** ⇒ đúng thiết kế, không phải F5b gây ra. Cần
    gắn nhãn `portal_suite` hoặc tự bỏ qua khi module chủ chưa cài ⇒ **F6**, > 30 dòng.
  - **148 dòng comment nhắc mã phiên** trong 14 module portal (chủ dự án đã nhắc 2 lần về việc hạn chế
    comment). Đề xuất luật: *comment nói VÌ SAO, không nói PHIÊN NÀO*.
  - Cụm **EmptyState**: 92 chỗ viết tay, 6 họ class, **3 cỡ tiêu đề** (28/20/18) — đã soạn 3 câu hỏi
    chốt cho BA trong `docs/f-review-A3.md` §7.
  - Báo anh Thái 8 mục (§8): test `__init__` import file đã xoá · file bàn giao màn Khảo sát · R3 chéo
    kênh · `auto_install` · **R7: `_wj_ensure_contract` 2 chỗ** · view `res.config.settings` cũ gây
    `ParseError` khi deploy · `wujia_metabase_connector` chưa phân tầng · `origin/thai` 2 commit chưa merge.
- Bài học:
  - **Chỗ mù của công cụ là chỗ lỗi trốn.** 2 lỗi 500 sống qua 7 phiên vì `check_layers` chỉ đọc manifest.
  - **Cài module một mình** là phép đo rẻ nhất mà mạnh nhất — 2 lỗi tầng + 1 khoản nợ đều từ 1 lệnh.
  - **Máy báo lỗi ≠ có lỗi**: tin 5 ô HIERARCHY mà sửa là phá một thiết kế Figma đã duyệt.
  - **Tên module trong chuỗi thông báo lỗi cũng bị tính là phụ thuộc chéo** — `test_ownership` bắt ngay;
    đưa tên module vào docstring, đừng đưa vào code.
- Phiên kế: **E4b** — phủ hết call site FilterBar (`UI-FILTER-001`, E4a đã làm nền ở `12750a2`).

## Nhịp dọc mobile — nén khoảng cách + gom về một token · 18/09/2026 · Mac
- Kết quả: ◐ dở — **phần chuẩn hoá xong**, **chỉ tiêu −30…35% KHÔNG đạt (−8%)**, dừng theo chốt của
  chủ dự án (hết giờ) để làm tiếp ở phiên sau.
- Ngoài lộ trình cụm F: việc BA/chủ dự án giao trực tiếp từ ảnh chụp Home mobile ("khoảng trống giữa
  các thành phần quá lớn"). Không đụng Issue List.
- Đã làm:
  - Nhịp dọc mobile nay khai ở **đúng một chỗ** (khối `:root` trong `@media (max-width:991.98px)` của
    `_variables.css`): gap 14→**8**, mép trên 16→**10**, tiêu đề nhóm 16/8→**6/4** qua token mới
    `--wujia-m-sechead-mt/mb`.
  - Kéo **8 trang lạc chuẩn** về một rule chung: Home (gap 18) · Công nợ (12) · Báo cáo (12) ·
    Đặt hàng/Giỏ/Lịch sử (dàn con bằng `margin-bottom` 10/14/16 — gỡ 5 margin).
  - **Gỡ 3 rule bù trừ âm** cho PageHeader (−6 mpage, −4 công nợ, −4 báo cáo): gap chung nay đúng 8px
    của CMP-PG-001 nên chúng hết lý do tồn tại. Đo lại: **7/7 route ra đúng 8px**.
  - Guard mới `wujia_portal_base/tests/test_mobile_rhythm.py` (5 test) + sửa 1 guard D4d đã lỗi thời.
- Commit: `<điền sau khi commit>`
- Deploy: chưa (theo chốt: commit + push `main`, KHÔNG deploy UAT)
- Số đo: Home @390 **2613→2405 (−8,0%)** · @360 −7,9% · khoảng trắng trước tiêu đề nhóm **34→14px**
  · khối thấy trọn màn đầu 3→**4**, dòng 1→**2** (Thông báo 4→**5**) · **0 ô mất record** ·
  PC 1440/1024/992 **0 ô lệch** · 0 tràn ngang · 0 lỗi JS · suite **579/579** (574+5 mới) ·
  mutation **5/5 đỏ** · `check_layers` 2 vi phạm R7 **có sẵn** (của anh Thái, FR-A3 đã ghi).
- Lệch plan / quyết định mới:
  - **Chỉ tiêu −30…35% là bất khả thi bằng khoảng trắng** — chứng minh bằng thực nghiệm tiêm CSS:
    ép cả đệm thẻ, gap mục, `min-height` dòng xuống 48 (phá chuẩn D5) cũng chỉ ra **−12,9%**.
    Gốc: 8 dòng danh sách trên Home cao tổng **698px**, từng dòng 66/67/86/94/113 ⇒ **cao vì 2–3 dòng
    CHỮ, không vì đệm**. Trang dài do nội dung.
  - Rule chung **chỉ cấp nhịp, KHÔNG cấp padding**: trang dựng trong `.content-wrapper` đã được wrapper
    cấp pad-top (gom vào là cộng dồn), Home còn mất lề ngang vì `.wujia-home-wrapper` cố ý bỏ pad ngang.
  - Lệch Figma RESP-MOB-SHELL-003 — chủ dự án chốt "BA kêu mà, Figma tương đối thôi", chỉ cần 1 dòng FYI.
- Nợ để lại:
  - **Chưa gửi BA dòng FYI** về lệch Figma (gap 14→8, top 16→10, tiêu đề nhóm 16/8→6/4).
  - **1 error trên DB trắng chỉ cài khung** (`test_fra3_layer_guard`, 130 test) — đã chạy đối chứng
    `git stash`: **có sẵn từ FR-A3**, không phải phiên này. Cần xử ở F6 cùng nợ `portal_base`.
  - Hai cần gạt để thật sự tới −30%, **chưa làm, chờ chốt** (chi tiết + số ước tính ở
    `docs/mobile-rhythm-acceptance.md` §4):
    **G1** dòng danh sách 2–3 dòng → 1 dòng (−250…350px Home, ăn theo mọi màn danh sách, lệch Figma nhiều);
    **G2** khung cố định đang chiếm **235px = 26% màn hình** (header 104 + dải cửa hàng 48 + thanh dưới 83)
    → hạ header 104→72 và/hoặc ẩn header khi cuộn, lấy lại 30–50px MỖI MÀN cho mọi trang.
    **G3** cỡ chữ/line-height (rẻ nhưng chạm accessibility).
- **VIỆC CHỐT CHO PHIÊN SAU (chủ dự án giao cuối phiên 18/09, kèm ảnh header mobile):**
  **G2 — hạ chiều cao thanh điều hướng trên cùng của mobile.** Nguyên văn: *"cái navigation này phải
  hẹp cái height lại"*. Hiện `--wujia-mheader-height: 104px` (`_variables.css`), cộng dải cửa hàng 48
  + thanh dưới 83 = **235px = 26% màn hình 900px** không dùng để hiển thị nội dung. Việc cần làm:
  hạ header 104→~72 (logo 116×44 và 3 nút tròn 38 phải co theo, kiểm vùng chạm ≥44), cân nhắc ẩn
  header khi cuộn xuống. Lấy lại 30–50px MỖI MÀN cho **mọi trang**, không đụng nội dung.
  Lệch Figma "Mobile Shell FINAL (header 104 / strip 48 / footer 83)" ⇒ ghi FYI cho BA cùng dòng
  lệch nhịp dọc của phiên này. Mốc đo trước/sau: `wj_measure` + đếm "khối/dòng thấy trọn màn đầu"
  (script đã dùng ở phiên này, chép lại từ `docs/mobile-rhythm-acceptance.md` §2 phép đo 5–6).
- Phiên kế: **G2** (theo yêu cầu trên). Sau G2 mới quay lại **E4b** của Issue List; G1 (rút dòng danh
  sách về 1 dòng) chỉ làm khi BA đồng ý vì đổi cấu trúc dòng.

## G2 — Hạ chiều cao header mobile 104 → 72 · 18/09/2026 · Mac
- Kết quả: ✅ đạt. Việc chủ dự án giao trực tiếp cuối phiên trước (*"cái navigation này phải hẹp cái
  height lại"*), ngoài lộ trình cụm F. Phạm vi chốt: CHỈ header; dải cửa hàng 48 và thanh dưới 83 để sau.
- Đã làm:
  - `--wujia-mheader-height` **104 → 72**, khai trong khối `@media (max-width:991.98px)` của
    `_variables.css` (PC không đọc tới ⇒ khỏi phải chứng minh bất biến).
  - Gỡ neo tuyệt đối `.wujia-mheader-actions { align-self: flex-start; margin-top: 39px }` — con số 39
    chỉ đúng với header 104, giữ lại là cụm nút tràn khỏi header.
  - Trả nợ cũ tiện thể: vùng chạm 3 nút header **38 → 44** bằng `::before` 44×44, hộp nhìn thấy vẫn 38.
  - Guard mới `wujia_portal_layout/tests/test_g2_mobile_header.py` (7 test) — đặt ở KHUNG, không ở
    `portal_base`: header là component của chính khung và sau F5b khung phải tự chạy một mình.
- Commit: `7873175`
- Deploy: **ĐÃ DEPLOY UAT 18/09/2026** — chủ dự án deploy; `wujia_portal_layout` trên UAT ra đúng
  **19.0.51.0.12** và view mang `?v=1294`/`1299` ⇒ restart tự upgrade, không cần `-u`. Đo lại chỉ-đọc
  trên chính máy chủ: header **72** cả 10 ô, dải 48, mốc nội dung **120**, chạm **44**, bấm thật 3/3,
  0 tràn ngang, 0 lỗi JS. Bẫy khi đo: 3 nút báo "BỊ CHE" là do popup chọn cửa hàng của tài khoản
  admin (`#wujiaStoreOverlay`), không liên quan G2.
- Số đo: header 72 cả 10 ô · mốc đầu nội dung **152 → 120** · `wj_measure` mobile **−32,0px × 16 ô**,
  PC **0 ô lệch**, 0 ô mất record (Báo cáo 14 → 16 record) · dòng thấy trọn màn đầu Kiến thức @390
  3 → 4 · bấm thật 4/4 (bấm cao hơn hộp 38 đúng 2px vẫn mở dropdown ⇒ pseudo ăn thật) · 0 tràn ngang ·
  0 lỗi JS · HIERARCHY 3 → 3 · suite **586/586** · DB trắng chỉ cài khung **0 failed / 1 error** (`test_fra3_layer_guard`, **nợ có sẵn thuộc F6**, không phải do phiên nào trong cụm gây ra)
  · mutation **5/5 đỏ** · `check_layers` 2 R7 có sẵn.
- Bẫy gặp:
  - **`::after` của nút header đã bị dành để tắt caret Bootstrap** (`.dropdown-toggle::after{display:none}`).
    Viết vùng chạm vào `::after` là mất vùng chạm ở đúng 2/3 nút, im lặng. Đã chuyển sang `::before` và
    có guard riêng khoá bẫy này.
  - **Bộ đo của chính mình cũng phải soi**: probe đầu đọc mỗi `::after` nên báo "chạm 38" trong khi code
    đã đúng — suýt đi sửa code lành.
- Đính chính số của phiên trước (đã sửa thẳng vào `mobile-rhythm-acceptance.md` §4): **chỉ thanh dưới
  83 mới thật sự `position: fixed`**; header + dải cửa hàng nằm TRONG luồng, chiếm 152px ở đầu trang
  rồi trôi đi khi cuộn. Không có "235px khoá cứng mỗi màn". Đổi lại, hạ header LÀ làm ngắn trang thật
  32px, và không phải vá mốc đầu nội dung (`--wujia-mcontent-top` giữ 10, y=120 = 72+48+10 tự ra).
- Nợ để lại:
  - **Chưa gửi BA dòng FYI** — gộp 2 khoản: header 104→72 và nhịp dọc của phiên trước (gap 14→8,
    mép trên 16→10, tiêu đề nhóm 16/8→6/4), đều lệch Figma *Mobile Shell FINAL* / RESP-MOB-SHELL-003.
  - **G1** (dòng danh sách 2–3 dòng → 1 dòng) và **G3** (cỡ chữ/line-height) chờ BA.
  - Muốn lấy thêm chỗ ở MỌI vị trí cuộn thì phải đụng **thanh dưới 83** — thứ duy nhất thật sự cố định.
- Phiên kế: **E4b** — phủ hết call site FilterBar (`UI-FILTER-001`, E4a đã làm nền `12750a2`), quay lại
  hàng đợi Issue List đã mở lại sau FR-A3.

## E4b1 — FilterBar `CMP-FB-001`: phủ hết call site PC · 19/09/2026 · Mac
- Kết quả: ✅ đạt **16/16** tiêu chí. Lượt đầu quay lại hàng đợi **Issue List** sau cổng ★FR-A3.
  `UI-FILTER-001` (STT 139) **CHƯA đóng** — đóng ở E4c; không chạy `qa_sync.py`, không đổi sheet.
  Chủ dự án chốt 2 việc đầu phiên: (1) **cắt đôi E4b** → E4b1 PC / E4b2 mobile; (2) 5 màn "nhóm 2"
  (giao hàng · thông báo · thi · báo cáo · đặt hàng) **migrate hẳn vào component**, không chỉ căn lề.
- Đã làm:
  - **9 call site PC** về `wujia_portal_layout.wj_filter_bar`: support · knowledge · return ·
    info_request (4 màn Bootstrap `row g-2`) + delivery · notification · exam · report · order.
  - Component thêm đúng **một** knob: `fb_dates={'kind':'text'}` — màn Thi còn ô ngày dạng chữ,
    E4c mới wire; ép `type=date` sớm là tự sửa lỗi BA nêu bằng cách giấu nó.
  - Biến thể `--dense` (flex-basis hẹp hơn) cho 2 thanh **5–6 control** (notification · exam) —
    không có nó thì notification 88 → 142 ở 1440, tức là lượt chuẩn hoá làm xấu đi màn đang đạt.
  - Dọn CSS bản địa 4 module (`portal_notification`/`portal_report`/`portal_exam`/`portal_order`);
    2 họ class mà **Khảo sát của anh Thái còn dùng** thì **thu hẹp vào `.wj-inspection-pc`**, không
    xoá (bẫy E3c), kèm test chặn.
  - **Dựng lại + commit công cụ kiểm kê**: `scripts/qa/wj_filterbar_inventory.py` (bản E4a để ở
    `scratchpad/e4/`, thư mục đã mất). Thêm **chế độ render** đọc DOM thật — sau migrate thì quét
    `lxml` không còn đọc được điều kiện nằm trong component, bản tĩnh một mình là **mù**.
  - **Công nợ PC không sửa byte nào**: đo ra đã đúng chuẩn (42px, nhãn `Xem`/`Tìm kiếm` hợp
    FB-02/FB-09 item 9). Ghi rõ trong matrix thay vì sửa cho có.
  - 21 test mới (16 `portal_base` quét chéo module + 5 `portal_layout` hợp đồng component) — đúng
    luật sở hữu F5b.
- Commit: `131d948`
- Deploy: **chưa** — không tự deploy UAT. Lệnh `-u` gộp ghi ở `docs/e4b1-acceptance-matrix.md` §5.
- Số đo: **FB-10 0/48 ô lệch bộ điều kiện** (12 route × 4 khổ, chế độ render) · control PC
  **26.7–28.1 → 42** ở 4 màn nhóm 1, **50 → 42** ở báo cáo, baseline `2 → 1` ở return + exam ·
  card 88 ở cả 9 màn (delivery **142 → 88**, exam **144 → 88**) · `wj_formcontrol --scope body`
  **101 control / vi phạm 88 → 75** · `wj_measure` 13 route × 5 khổ **0 tràn ngang · 0 lỗi JS ·
  0 redirect** · suite **0 failed / 0 error / 601 test** · DB trắng **0 failed / 1 error**
  (`test_fra3_layer_guard`, nợ F6) · mutation **11/11 đỏ đúng guard** · `check_layers` 3 R1–R5 +
  2 R7 **có sẵn**, không thêm.
- Bẫy gặp:
  - **`log_level=warn` nuốt dòng tổng kết test.** `odoo.tests.result` chỉ ghi ERROR khi CÓ lỗi; suite
    xanh thì dòng "0 failed…" là INFO nên biến mất ⇒ mất 3 lần chạy lại vì tưởng test không chạy.
    Luôn thêm `--log-handler "odoo.tests.result:INFO"`.
  - **Harness mutation đọc stdout là đọc nhầm chỗ**: Odoo ghi `FAIL:` vào logfile, mà `wujia_core`
    còn dời logfile sang `<thư mục>/<năm>/<tháng>/<ngày>.log`. Phải đọc theo glob + chặn cứng
    "không thấy dòng tổng kết ⇒ run hỏng, KHÔNG phải 0 đỏ".
  - **Tách tên test cắt trước `test_`** bắt trúng tên logger (`tests.test_scan_e4_filter_bar`) nên
    11/11 mũi báo "SAI" oan. Phải cắt **sau** nhãn `FAIL:`/`ERROR:`.
  - **Cắt XML theo chỉ số anchor** làm hỏng `portal_order_catalog.xml` (chuỗi kết thúc lặp lại) —
    phải `git checkout` rồi cắt lại theo dòng tường minh.
- Nợ / phải nói với BA:
  - **Kiến thức PC mất 1 record trong khung** (30→29 @1440) và cao thêm 42px; Báo cáo 80 → 88. Lý do:
    thanh lọc cũ của Kiến thức chỉ cao 39px, nay về chuẩn control 42 / card 88 của chính BA. Muốn giữ
    record thì phải đổi **chuẩn**, không phải đổi riêng màn.
  - **Nút "Xóa lọc" của Thông báo** chuyển từ reload cả trang sang link `data-wj-nav` (AJAX) — cùng
    URL đích, cố ý thống nhất theo component.
  - 3 màn (exam · notification · return) **đổi thứ tự hiển thị** ô lọc sang chuẩn search → ngày →
    select; bộ điều kiện y nguyên. Ghi ra để retest không tưởng là mất/thêm ô.
- Phiên kế: **E4b2** — toàn bộ thanh lọc mobile. Prompt sẵn: `docs/prompt-e4b2.md` (đã ghi rõ G2 hạ
  header mobile 104→72 nên mốc cao trang mobile phải chụp lại, kèm bảng mốc sau E4b1).

## E4b2 — FilterBar `CMP-FB-001`: phủ hết call site **mobile** · 19/09/2026 · Mac
- Kết quả: ✅ xong — **13/13 tiêu chí**. `UI-FILTER-001` (STT 139) **CHƯA đóng** (đóng ở E4c);
  không chạy `qa_sync.py`, không đổi sheet, không tự deploy UAT.
- Đã làm:
  - **6 thanh lọc mobile vào component**: Lịch sử · Thông báo · Hỗ trợ · Kiến thức · Đổi trả ·
    **Báo cáo** (Báo cáo vào hẳn component theo chốt "làm chuẩn chỉ hẳn" của chủ dự án).
  - **Biến thể BA 04-DateRangeOnly** thêm vào component: màn **chỉ có ngày** thì nút tìm nằm **cùng
    hàng** với 2 ô ngày. Không có nó thì thẻ Báo cáo phình 72 → 116 (thêm hẳn một hàng nút).
  - **Đặt hàng mobile** giữ dáng hàng trần (bọc card là đổi thiết kế màn) nhưng kéo hình học về
    chuẩn: ô tìm + nút **44/r12 → 38/r10**, vùng chạm giữ 44 (ô tìm bọc `<label>`, nút `::before`).
  - **Công nợ mobile 0 byte** — component riêng đã duyệt Figma v31 (FB-09 item 9), đo lại để chứng
    minh không hồi quy.
  - **Màn Thi mobile cố ý để nguyên**: chủ dự án chốt *"làm chuẩn, phiên này không ổn thì phiên sau,
    miễn giải quyết tới nơi"* ⇒ E4c **migrate + wire ngày một thể**, không đẻ knob tạm trong
    component. Có test ghi nợ.
  - Dọn CSS: xoá họ `.wj-rep-mfilter*` (52 dòng) · **thu hẹp** khối 44px của D6c về `.wujia-mexam`
    (màn Thi còn dùng — xoá là đẻ vi phạm vùng chạm ở chính màn ta không đụng) · giữ `.wj-mform` 48
    (chuẩn form BH-009, khác chuẩn ô lọc).
  - 20 test mới (13 `portal_base` quét chéo + 7 `portal_layout` hợp đồng component — đúng F5b).
- Commit: _(điền khi push)_
- Deploy: **chưa** — lệnh `-u` gộp 9 module ghi ở `docs/e4b2-acceptance-matrix.md` §9.
- Số đo: **FB-10 render-diff 13 route × 6 khổ = 78 ô, 0 lệch** · ô lọc mobile **38 nhìn thấy /
  44 vùng chạm** ở cả 3 loại control, thẻ **r14 / p12 / gap 8** ở 6/6 màn · **0 tràn ngang**
  @360/390/430 · `wj_formcontrol --scope body` **82 control · vi phạm 14 → 4** (4 ô còn lại là
  select PC 42 của info-request, **có y hệt ở run đối chứng**) · `wj_measure --diff` 13 route × 5 khổ
  **0 tràn ngang · 0 lỗi JS · 0 mất record**, đúng **1 ô lệch** (Báo cáo mobile **+14**) · **PC không
  đổi 1 pixel** · suite **0 failed / 0 error / 621 test** · DB trắng **0 failed / 1 error / 149**
  (`test_fra3_layer_guard`, nợ F6) · mutation **20/20 đỏ đúng guard** · `check_layers` 3 R1–R5 +
  2 R7 **có sẵn**.
- Bẫy gặp:
  - **Harness mutation bị dừng giữa chừng để lại file đã phá trong cây mã** (`wj-sup-mchips2`), suite
    lần sau đỏ. Đã vá: `atexit` + `SIGTERM`/`SIGINT` phục hồi. **Không bắt `SIGHUP`** — `nohup` đang
    vô hiệu nó, bắt lại là tự chết khi shell thoát (dính đúng một lần).
  - **Mũi phá `str.replace(old, new, 1)` ăn vào call site PC** (PC và mobile cùng file) ⇒ 3 mũi đỏ
    nhầm test của lượt trước. Thêm cờ `[m]` → thay ở lần xuất hiện **cuối**.
  - **Mũi phá phải giữ XML hợp lệ**: đổi `<label>` thành `<div>` làm lệch thẻ đóng ⇒ `-u` fail, không
    có dòng tổng kết, harness báo "run hỏng" (đúng như thiết kế).
  - **`closest('a, b, c')` trả tổ tiên gần nhất khớp BẤT KỲ selector nào — và khớp cả chính nó** ⇒
    hai công cụ đo báo vùng chạm 38 thay vì 44. Vá cả `wj_filterbar_inventory.py` lẫn
    `wj_formcontrol.py`; nếu tin máy thì đã đi "sửa" đúng chỗ vừa làm đúng.
  - **zsh không tách từ khi expand biến** ⇒ `--routes $R` gửi một chuỗi khổng lồ, script vẫn chạy
    "xong" với 1 route giả. Dùng mảng `R=(…)` + `"${R[@]}"`, luôn đếm route trong JSON trước khi tin.
  - **`-u` cả `wujia_core`/`wujia_franchise` làm suite chết ngay khi nạp test** (`wujia_franchise/
    tests/__init__.py` import file đã xoá — nợ phía anh Thái). Suite của lượt chạy trên 9 module đụng.
- Nợ / phải nói với BA:
  - **Báo cáo mobile cao thêm 14px**: thẻ lọc thấp đi 2 (72 → 70) nhưng thẻ chuẩn có
    `margin-bottom: 16px` còn thanh cũ cố ý để 0 ⇒ −2 + 16 = +14. Giá của việc dùng **chung một vỏ**.
  - **Nợ nhịp G2**: `.wj-filter-card` cộng 16px lên trên `gap` 8px của khung trang ⇒ *lọc → danh
    sách* thành 24px ở **cả 7 màn**. Nợ có từ **E4a**, gỡ là đổi nhịp 7 màn cùng lúc ⇒ để **cụm nhịp
    E5**, đã ghi vào `docs/prompt-e4c.md`.
  - **Đổi trả đổi thứ tự** ô lọc sang chuẩn tìm → ngày → select (bộ điều kiện y nguyên);
    **Báo cáo** đổi nhãn `Tìm` thành nút kính lúp có `aria-label="Tìm kiếm"`; **Đặt hàng** ô tìm nhỏ
    lại còn 38 nhưng vùng bấm vẫn 44.
- Phiên kế: **E4c** — wiring ngày + màn Thi mobile (migrate **và** wire một thể) + guard + **đóng
  issue**. Prompt sẵn: `docs/prompt-e4c.md`.
