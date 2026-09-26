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
- Commit: `c6e2946`
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

## E4c — FilterBar `CMP-FB-001`: hành vi lọc + ĐÓNG `UI-FILTER-001` (19/09/2026 · Mac)

- Mục tiêu: lượt cuối cụm E4. E4a/E4b1/E4b2 lo **dáng**; E4c lo **hành vi lọc** rồi đưa issue về
  `Ready for Retest` (Dev không đặt `Done`). Chốt đầu phiên của chủ dự án: làm xong viết luôn
  `docs/prompt-e5.md`, commit + push `main`, **không tự deploy UAT**.
- **Đo trước khi đọc mã** (guard mới `scripts/qa/wj_filterbar.py`) và bảng trong prompt hoá ra **sai**:
  Thông báo ghi ✅ nhưng thật ra tính `date_error` rồi **không view nào in ra**, và vẫn trả **toàn bộ**
  danh sách (10 bản ghi) khi ngày ngược; Đổi trả báo ở **banner đầu trang**, gộp chung với lỗi sai định
  dạng. **5/6 màn im lặng**.
- Làm được:
  - **Một nguồn duy nhất** `ERR_DATE_RANGE` + `date_range_error()` ở `wujia_portal_base` (L3a, không
    thêm depend); 6 màn cùng gọi. Trước đó 2 câu chữ khác nhau cho cùng một lỗi.
  - **Một khuôn hiển thị**: `<p class="wj-filter-error" role="alert">` qua slot `fb_error`, id nằm
    trong `wjl_slots`, màn có fragment in cả 2 mảnh. CSS dời về `wujia_portal_layout` (`?v=1303`).
  - **Màn Thi mobile**: khối dựng tay (2 ô ngày **không có `name`**) → component, **migrate + wire một
    thể** đúng chốt 19/09. Đo ra lọc thật: 10 → 0 bản ghi theo khoảng.
  - **Báo cáo** bỏ tự kẹp im lặng; ngày ngược ⇒ KPI 0 + chart rỗng **cùng bộ khoá** với nhánh thường
    (thiếu khoá là JS biểu đồ vẽ hỏng im lặng).
  - Gỡ **2 knob mồ côi** của component: `kind='text'` và **`clamp`** (xem bẫy dưới).
  - Guard 4 mục + **12 mũi mutation**; 6 file test mới (5 module + quét chéo `portal_base`).
- Số đo: FB-10 render 78 ô ⇒ **3 ô lệch, đều là màn Thi mobile cố ý** · ngày ngược **6/6 báo, 0 im
  lặng** · về trang 1 **5/5** · sang trang giữ lọc **5/5 (6/6 link)** · ngày lọc thật **5 màn có số
  đổi** · `wj_measure` 65 ô **0 lệch** · suite **648/0** · `check_layers` 3 R1–R5 + 2 R7 **có sẵn**.
- Bẫy gặp:
  - **`clamp` chặn IM LẶNG cú dời khoảng ngày về trước.** Guard bắt màn Báo cáo "gửi đi không có
    ngày"; truy ra `min`/`max` do `clamp` sinh ra làm trình duyệt **từ chối submit** khi người dùng
    chọn khoảng sớm hơn khoảng đang lọc — không request, không thông điệp. Có ở **mọi** màn ngay khi
    đã lọc một lần. Đã gỡ `clamp` khỏi component + 6 call site; 2 test cũ khẳng định `clamp` đổi
    thành test khẳng định **không màn nào kẹp lại**.
  - **DB đo có 0 phiếu thi, 0 chuyến giao** ⇒ mục "ngày hợp lệ lọc đúng" không chứng minh được. Phải
    gieo (`scripts/seed_e4c_dates_demo.py`) rồi mới đo — nếu không lại là một bảng "Pass rỗng".
  - **`cls.session` trong `HttpCase` đè phiên HTTP** ⇒ `authenticate()` nổ `'... has no attribute
    sid'`. Đặt tên `cls.exam_session`.
  - **`--routes`/`--widths` phải khớp hệt lúc chụp mốc**, nếu không `--diff` in ra 31 "lệch" toàn là
    ô không đo (`sau=None`) — suýt tưởng hồi quy.
  - Mũi phá phải khớp **đúng thụt lề** của file đích; sai một dấu cách là harness báo "phép phá không
    ăn" (đúng như thiết kế, nhưng tốn một vòng chạy).
- Nợ mang sang: **nhịp G2** (`.wj-filter-card` +16px chồng `gap` 8 ⇒ *lọc → danh sách* 24px ở 7 màn)
  — đã ghi thành việc bắt buộc của **E5** trong `docs/prompt-e5.md`.
- Phiên kế: **E5** — ListCard `CMP-LC-001` (`UI-LISTCARD-001`, STT 136, dòng tuyệt đối 129).
  Prompt sẵn: `docs/prompt-e5.md`.
- Chốt phiên: commit **`faa76f5`** đã push `main`; ledger `UI-FILTER-001` + `qa_sync --apply` ⇒ sheet
  dòng tuyệt đối **132** (STT 139) về **`Ready for Retest`**, Owner `BA/Tester`, cột Build ghi rõ
  **CHƯA lên UAT** (chủ dự án tự deploy). Lệnh `-u` gộp 12 module nằm ở `docs/e4c-acceptance-matrix.md` §8.

## E5a — ListCard `CMP-LC-001`: component + 2 route mẫu (19/09/2026 · Mac)

- Chốt đầu phiên của chủ dự án: **chẻ E5 thành E5a / E5b / E5c** (như E4 chẻ a/b1/b2/c), và
  **LC-22 ProductCard token-only "fix luôn"** — xếp vào E5c, chụp mốc `wj_measure` riêng cho
  `/portal/order` để lùi được độc lập. E5a = inventory + component + 2 route mẫu + guard.
- **Đo trước khi đụng mã**, và hiện trạng tệ hơn bảng trong prompt: **22 call site** thật, **14 họ
  class item** khác nhau, mỗi module tự dựng ruột. D5 đã chuẩn hoá **dáng NGOÀI** (`.wj-data-item`),
  cái chưa ai làm là **anatomy BÊN TRONG** — đúng phạm vi E5.
- Làm được:
  - **Component** `wujia_portal_layout/views/wj_list_card.xml` — 2 template (`wj_list_card` +
    `wj_list_card_row`), dùng lại khuôn slot của `wj_data_list.xml`, **không JS mới**. Thẻ item vẫn ở
    call site vì QWeb **không có** directive đổi tên thẻ động (`ir_qweb.py:1705`) ⇒ `<a>`/href từng
    route giữ nguyên.
  - **Badge 12px = modifier DÙNG CHUNG** `.wj-status-badge--compact` (chỉ khai `font-size`), **không**
    CSS theo route; guard E2 nới đúng một khe hẹp cho modifier này, kèm chú thích LC-25.
  - **2 route mẫu**: history (`wujia-mhist-row`, 6 rule) và delivery (`wujia-mdelivery-row`, 9 rule)
    về `.wj-lc`; bỏ nhãn thừa "Chuyến xe" + divider nội bộ (LC-14), thêm nhãn "Ngày đặt"/"Tổng tiền"
    (LC-13). **Giá trị mất/thêm = 0/0** ở cả hai.
  - **2 công cụ mới**: `wj_listcard_inventory.py` (kiểm kê trường, `--diff` **tách nhãn khỏi giá trị**
    nên đổi nhãn theo BA không bị đếm nhầm là "thêm trường") và `wj_listcard.py` (guard anatomy
    LC-01/03/04/07/10).
  - **18 test mới**: 12 hợp đồng component ở `portal_layout`, 6 quét chéo ở `portal_base` theo sổ
    đăng ký `MIGRATED`/`GIU_NGUYEN` — thêm route ở E5b chỉ cần thêm một dòng vào sổ.
- Số đo: guard **0/10 ô** có vi phạm trên 2 route × 5 khổ · **đỏ đúng 7/7** route chưa migrate ·
  `wj_nesting` **0** khung lồng khung · `wj_datalist` **0** vi phạm · Home chữ ký DOM **trước = sau**
  (`fd881c9f4245`) · suite **433 tests, 0 failed, 0 error** · `check_layers` 3 R1–R5 + 2 R7 **có sẵn**.
- Bẫy gặp:
  - **Đo nhịp sai mốc**: *lọc → danh sách* ra 52/55/70 vì count-meta/section-header xen giữa. Đổi sang
    *lọc → phần tử anh em kế tiếp nhìn thấy được* mới lộ đúng **24px ở 7 route** — nợ G2 vẫn nguyên,
    trả ở E5c.
  - **3 công cụ QA mặc định `--base 127.0.0.1:8019`** (`wj_nesting`, `wj_datalist`, `wj_measure`) —
    đúng cổng bị cấm đụng, và lần chạy đầu đã lấy số từ **DB khác** (delivery item=0 trong khi thật là
    20). Đổi mặc định cả 3 về **8090**. Ai đọc số cũ của các cụm trước nên soi lại cột `base` trong JSON.
  - **Guard sạch ngay lần đầu** ⇒ phải chứng minh nó cắn: 11/11 ca `judge()` tổng hợp + mũi CSS thật
    (badge 12→13px ⇒ **20 vi phạm**, hoàn nguyên ⇒ **0**).
  - **Đổi ruột làm card cao lên 80 → 104px** ⇒ khai `compact-row` (64–76) thành **khai sai dáng**,
    guard D5 đỏ đúng. Chuyển call site sang `detail-card` và sửa bảng trong `test_scan_d5_data_list.py`.
  - **Skeleton hợp lệ viết tay `wj-lc__row`** (thanh xám, không nhãn/giá trị) ⇒ luật "cấm hàng phụ viết
    tay" phải hạ xuống "cấm **nhãn/giá trị** viết tay".
  - Test đọc CSS bằng `selector + ' {'` trượt vì rule canh cột → regex `\s*\{`.
- Nợ mang sang: **nhịp G2** 24→16 ở 7 route (E5c) · **padding item `12px 14px`** vs LC-07 ghi 12, đi
  chung món gutter LC-08 (E5c, **không** sửa lẻ) · **mẫu mỏng** `/portal/debt` 1 và
  `/portal/exam/register` 1 ⇒ phải gieo trước khi kết luận (E5b) · **LC-20 defer vĩnh viễn** (code anh
  Thái) · **LC-27** lệch dữ liệu — chỉ ghi nhận, không tự sửa mapping.
- Phiên kế: **E5b** — phủ 9 call site còn lại theo thứ tự rủi ro tăng dần: thông báo (LC-16) → hỗ trợ
  (LC-18) → đổi trả (LC-15) → kiến thức ×2 (LC-17) → thông tin nhượng quyền → thi ×3 (LC-19) → công nợ
  ×2 (LC-21, retest bằng role được phép). Chi tiết: `docs/e5a-acceptance-matrix.md` + kế hoạch cụm E5.
- Chốt phiên: **issue CHƯA đóng** — `UI-LISTCARD-001` chỉ ghi ledger + `Ready for Retest` ở **cuối
  E5c**, khi đủ 22 call site + regression 8 khổ. **Không tự deploy UAT.**

## E5b1 — ListCard `CMP-LC-001`: 6 call site rủi ro thấp (19/09/2026 · Mac)

- Chốt đầu phiên của chủ dự án: **chẻ E5b thành E5b1 / E5b2** (tiền lệ E4b1/E4b2) · **Kiến thức
  migrate cả PC lẫn mobile** ("cải tiến hết", PC riêng mobile riêng) · **CardHeader lồng trong item
  Thi sẽ thay bằng đầu ListCard** (ghi sẵn cho E5b2) · **giữ icon trang trí, đưa vào slot `lc_prefix`**
  chứ không tự xoá thứ BA đang thấy — kèm một câu hỏi cho BA ở cuối phiên.
- Sửa lại con số của nhật ký E5a: còn **11 call site** chứ không phải 9 (đếm theo call site, không
  theo route); Kiến thức ở PC là **card list**, không phải bảng ⇒ không vướng luật "bảng PC 0 byte DOM".
- Làm được:
  - **6 call site** về `.wj-lc`: Thông báo (LC-16, giữ dấu chưa đọc) · Hỗ trợ (LC-18) · Bù hàng
    (LC-15, **"Ngày yêu cầu" đủ năm**, bỏ divider + chevron) · Kiến thức **mobile + PC** (LC-17) ·
    Thành viên cửa hàng (LC-18).
  - **Khung học được 3 điều mới** (`_components.css` `?v=1306 → 1311`): tên card `flex: 1 1 0` + clamp
    2 dòng · thân card thành **lưới 2 cột** `minmax(0,1fr) auto` để "trường ngắn cùng hàng" mà không
    đẻ slot mới (dùng lại `lcr_class`) · `tabular-nums` cho giá trị.
  - **Sổ `MIGRATED` có khái niệm "họ dùng chung"**: `wujia-mdash-row` (Home 50 chỗ) và
    `wujia-content-card-row` (Home) **không được** xoá khỏi CSS ⇒ luật thu hẹp thành *"không còn nằm
    trong cây con của item đã migrate"*.
  - Test mới/đổi chủ: `test_e5b_list_card_read_state.py` ở **chính module Thông báo** (dấu chưa đọc là
    hành vi riêng) · D6b/BH-007/BH-008 của Bù hàng neo lại vào anatomy ListCard + `test_nhan_ngay_
    yeu_cau_du_nam` · D5e còn 5 call site Home, D5f bỏ sổ họ riêng · E2b đo "chip không bị kéo cao"
    ở khung thay vì ở màn.
- Số đo: inventory DIFF 13 route × 2 khổ = **3 dòng, cả 3 là món LC-15 của Bù hàng**, 5 route kia
  **0/0** · guard `wj_listcard` **0 vi phạm** (7 route × 5 khổ, +1440 cho Kiến thức) · **10/10 mũi
  mutation đỏ đúng guard của nó** · `wj_returncard` **0 vi phạm**, 1 bố cục metadata (trước khi có
  `tabular-nums` là **5**) · `wj_nesting` **0** · `wj_measure` 0 tràn/0 lỗi JS/0 redirect · Home chữ
  ký DOM **trước = sau** ở cả @390 lẫn @1440 · suite **567 tests, 0 failed, 0 error** ·
  `check_layers` 3 R1–R5 + 2 R7 **có sẵn**.
- Bẫy gặp:
  - **Card phình 100 → 150px** không phải do nội dung mà do `.wj-lc__name` **rớt xuống dòng dưới ô
    icon** (lead `flex-wrap`). Sửa ở khung một chỗ, 3 màn cùng thấp lại.
  - **Gỡ CSS theo họ làm chết markup khác**: bài Nổi bật + trang chi tiết Kiến thức dùng chung
    `.wujia-mknow-row-title` / `.wujia-mknow-date` với danh sách. Bắt được bằng một lượt quét *"class
    còn trong view mà không còn rule CSS"* — **nên làm mặc định sau mỗi lượt gỡ CSS**.
  - **`wj_returncard.py` Pass rỗng**: 51/51 phiếu trong DB đo có `resolution_type` rỗng ⇒ nhánh "Tiến
    độ bù" không bao giờ render. Gieo `seed_d6_return_demo.py` + đo bằng `anh.owner` mới có 5 cặp badge.
  - **Cột phải của lưới lệch 1–7px giữa các card** vì chữ số không cùng bề rộng — guard bắt đúng
    (5 bố cục metadata), `tabular-nums` mới về 1.
  - Hai lớp hook chết (`wujia-mnoti-list`, `wujia-mknow-list`): gap nay là việc của DataList ⇒ bỏ
    `dl_class` thay vì để tên lớp không có rule.
- Nợ mang sang: **E5b2** Thi ×3 + Công nợ ×2 (gieo trước, thay CardHeader lồng, giữ JS hook
  `data-exam-*`) · **nhịp G2** 24→16 ở 7 route (E5c) · **padding item `12px 14px`** vs LC-07 (E5c, đi
  chung gutter LC-08) · **LC-20 defer vĩnh viễn** · **LC-27** lệch dữ liệu · **mẫu một chiều**: cả 10
  thông báo của `em.hcm` đều chưa đọc ⇒ chưa đối chiếu được card đã đọc bằng trình duyệt.
- Hỏi BA (ghi trong `docs/e5b1-acceptance-matrix.md`): (1) ô icon phân loại 32×32 trong card — giữ hay
  bỏ theo đúng chữ LC-06/LC-07? (2) dải cao `detail-card` 96–120 — bản ghi Bù hàng có tiến độ bù +
  tên 2 dòng đo **122–156px**, siết trường hay công nhận dải rộng hơn?
- Phiên kế: **E5b2** — Thi ×3 (LC-19) + Công nợ ×2 (LC-21). Chi tiết:
  `docs/e5b1-acceptance-matrix.md` §"Còn treo".
- Chốt phiên: **issue CHƯA đóng** — `UI-LISTCARD-001` ghi ledger + `Ready for Retest` ở **cuối E5c**.
  **Không tự deploy UAT.**

## DOC-CTRL — Kiểm kê controller cho BA (19/09/2026 · Mac)

- Phiên **tài liệu**, không phải phiên F. **0 dòng code nghiệp vụ**: `git status` chỉ có `docs/` +
  `scripts/qa/`, **0 file dưới `custom/`**.
- Yêu cầu gốc (chủ dự án chuyển từ BA): *"cần check code và server xem đã có những controller nào,
  ở phân hệ nào, chức năng gì — để BA còn lên task tiếp"*, ra **`.tex` → PDF**. Chốt thêm:
  phạm vi `wujia_*`, **có** đối chiếu UAT (chỉ-đọc), PDF **độc lập** (không nhét vào master 300
  trang), và **ghi mỗi controller ứng với mục `CT-0xx` nào** + mục CT nào chưa có code.
- Làm:
  - `scripts/qa/controller_inventory.py` (**mới**, không tiền tố `wj_` theo luật F0) — duyệt **AST**,
    không grep. Mỗi hàm có `@http.route` xuất: module · file · dòng · class · bases · method · paths ·
    type · auth · methods · csrf · website/sitemap · docstring dòng đầu · model `env[...]` dùng trong
    thân. Ra `docs/controller-inventory/routes.json`.
  - Đọc UAT **chỉ-đọc** qua XML-RPC (`ir.module.module`) → cột "Trên UAT".
  - Đọc tab `3. Controller` bằng `sheet_io.read_values` → `docs/controller-inventory/ba_ct.json`.
  - Đọc tay 21 file controller để viết cột **chức năng nghiệp vụ** (máy sinh metadata, không sinh
    được nghiệp vụ).
  - `docs/controller-inventory.tex` → `controller-inventory.pdf` (**20 trang**, `lualatex` ×2,
    **không** qua `build-doc.sh`).
- Số đo chốt: **103 route · 106 path · 21 class · 23 file** (21 có route + 2 helper) · **16 module**
  có controller. CT: **71 mục thật** (CT-001…CT-071) = **56 ĐÃ CÓ · 6 MỘT PHẦN · 9 CHƯA CÓ**.
- Bẫy gặp:
  - **Đếm class sai 19 vs 20**: `WujiaPortal(CustomerPortal)` và `WujiaAuthController(AuthSignupHome)`
    có base **không chứa chữ "Controller"**. Sửa: nhận diện controller bằng **"có route"**, không bằng
    tên base ⇒ **21 class**. (Số route chưa bao giờ sai — chỉ class.)
  - **DB trên UAT là `wujia_tea_19`**, không phải `wujia_tea` — xác minh bằng `/xmlrpc/2/db` `list()`
    sau khi authenticate báo `database does not exist`. Traceback cũng lộ UAT chạy **Windows**
    (`D:\wujia-tea\odoo19`).
  - **Plan đếm bằng mắt sai**: plan ghi 17 file / 15 module / 20 class / 73 CT; máy đếm ra
    **23 / 16 / 21 / 71**. Hai dòng `CT-024.`/`CT-025.` cuối tab là **chữ thừa dưới bảng**, không
    phải mục.
  - Macro `\part` **trùng lệnh sectioning của LaTeX** ⇒ 100 lỗi `Misplaced \cr`. Đổi thành `\pt`.
  - Font **Lato không có trên máy này** ⇒ preamble ADR-027 chép sang phải đổi `\setmainfont`
    sang **Noto Sans**.
- Việc có ích cho BA (chương 6 của PDF): 8 module đang **lệch repo↔UAT** = E5a + E5b1 chưa deploy
  (chỉ giao diện, không mất chức năng) · **7 điểm cần BA xác nhận** (nguồn dữ liệu công nợ chưa nối
  `account.move` · ticket lọc theo **người tạo** chứ không theo cửa hàng · thành viên: Nhân viên có
  được xem không · cửa hàng lưu bằng **cookie** không phải session · đổi trả **1 sản phẩm/yêu cầu** ·
  QR thanh toán · 2 dòng thừa cuối tab) · **CT-061…CT-067** (ca làm, chấm công, nghỉ phép, chi phí)
  **chưa có dòng code nào** · **F6–F13 sẽ dời controller sang module khác nhưng URL không đổi** ⇒ BA
  **đừng lên task viết lại** các controller đó.
- Nợ mang sang: **11 nhóm route đã có code mà tab CT chưa mô tả** (quên/đặt lại mật khẩu, đổi ngôn
  ngữ, PDF đơn hàng, `.ics` giao hàng, 6 nhánh `.../results`, đồng bộ giỏ, 2 ảnh, 9 redirect 301, 12
  route Khảo sát, 2 route Metabase) — chờ BA bổ sung spec.
- Phiên kế: **E5b2** — Thi ×3 (LC-19) + Công nợ ×2 (LC-21), không đổi (phiên này không lấn lộ trình F).
- Chốt phiên: **không deploy**, **không đụng Issue List**, **không ghi sheet**.

## E5b2 — ListCard `CMP-LC-001`: 5 call site cuối, khép cụm E5b (19/09/2026 · Mac)

- Chốt đầu phiên của chủ dự án: **wizard "Chọn khóa thi" có migrate**, nút "Chọn" vào slot
  `lc_actions` · **tiền tách nhãn** ra `lcr_label` (`Còn lại` / `Đã trả` / `Được trừ`), số là giá trị
  đậm · chốt lượt **commit + push `main`, KHÔNG deploy UAT, issue vẫn mở** (đóng ở E5c).
- Làm được:
  - **5 call site cuối** về `.wj-lc`: `/portal/exam` · `/portal/exam/register` bước 1 ·
    `/portal/exam/registration/<id>` · `/portal/debt` · `/portal/debt/payment-history`.
    ⇒ **22/22 call site** của `UI-LISTCARD-001` đã về component, khép **E5b**.
  - Gỡ **100 dòng CSS** anatomy theo màn (Thi 70 · Công nợ 30). Giữ có chủ đích
    `wujia-mexam-card-top`/`-card-line` (khối tóm tắt phiếu, **không phải** danh sách); thu hẹp
    `portal_debt.css` còn **2 rule màu** bám đúng `.wj-lc__value--strong`.
  - Khung chỉ thêm **1 rule** `.wj-lc__link` (`?v=1311 → 1312`) — không màn nào khai `.wj-lc*` riêng.
  - **Gieo dữ liệu trước khi đo** (`scripts/seed_e5b2_demo.py`, LOCAL-ONLY, idempotent): 2 khoá thi
    Còn lịch/Đã đóng · phiếu đã công bố có Đạt + Không đạt + ghi chú · tuần mặc định có quá hạn/giấy
    báo có/đã trả · 3 thông báo **đã đọc** (trả nợ "mẫu một chiều" của E5b1).
  - Test: 2 file **mới** đúng chủ (`wujia_portal_exam/tests/test_list_card_e5b2.py` 6 test ·
    `wujia_portal_debt/tests/test_list_card_e5b2.py` 5 test); sổ `MIGRATED` 7 → **9**; **đảo chiều**
    2 test layout D5g/D5h (bố cục trong item nay là của ListCard ⇒ **cấm** màn khai lại).
- Số đo: inventory DIFF 14 route × 2 khổ = **13 dòng, tất cả là món tách nhãn đã chốt**, 0 lệch số
  record · `wj_listcard` **12 route × 5 khổ, 0 vi phạm** · `wj_nesting` 0 · `wj_datalist` 0 ·
  `wj_measure` 0 tràn/0 lỗi JS/0 redirect · Home + 7 route chưa migrate + **bảng PC của cả 5 màn vừa
  sửa** giữ **nguyên chữ ký DOM** · wizard 4 bước chạy thật PASS · **14/14 mũi mutation** · suite
  **653 tests, 0 failed, 0 error** · `check_layers` 3 R1–R5 + 2 R7 **có sẵn**.
- Ba bài học ghi lại:
  1. **Guard markup không thay được chạy thật**: JS wizard đọc `.wj-card-header__title` của card khoá
     thi — sau migrate card không còn header nên bước 2 hiện **tiêu đề rỗng**. Phép đo trình duyệt
     bắt được; test D3d của màn cũng đỏ đúng chỗ.
  2. **Sổ đăng ký đếm "có ít nhất một" là guard yếu**: mũi M1 bỏ `wj-lc` ở một trong ba call site của
     Thi mà sổ vẫn xanh ⇒ siết thành **đếm >= số call site**.
  3. **Bẫy tên con BEM lại xuất hiện**: `assertNotIn('wujia-mexam-card', view)` khớp
     `wujia-mexam-card-top`; so theo **token** (`(?![-\w])`) mới đúng.
- Còn treo → `docs/e5b2-acceptance-matrix.md` §"Còn treo sang E5c" + **2 câu hỏi BA** (ô icon
  `.wj-lc__tile`; **dải cao hai variant không còn phủ hết thực tế**: nhân sự có ghi chú **146px**,
  hoá đơn 2 hàng phụ **80px** — rơi vào khe giữa 76 và 96).
- Chốt phiên: **issue CHƯA đóng** — `UI-LISTCARD-001` ghi ledger + `Ready for Retest` ở **cuối E5c**.
  **Không tự deploy UAT.** Prompt phiên kế: `docs/prompt-e5c.md`.

## E5c — ListCard `CMP-LC-001`: nhịp + bề ngang, regression 8 khổ, **đóng issue** (19/09/2026 · Mac)
- Kết quả: ✅ xong — `UI-LISTCARD-001` (STT 136, dòng 129) → **Ready for Retest**, khép cụm **E5**.
- Chốt đầu phiên của chủ dự án: **Dev tự quyết, ít hỏi BA lại, làm nốt cho chuẩn chỉnh mọi màn** ·
  2 câu hỏi BA treo giải theo đề xuất của chủ dự án · codex-review phạm vi **toàn cụm E5**.
- Đã làm:
  - **Nhịp *thanh lọc → nội dung* 24 → 16** ở **8 route** (7 route theo prompt + `/portal/reports/orders`),
    sửa **một chỗ** ở khung và khai bằng **token** (`margin-bottom: var(--wujia-mshell-content-gap)`)
    nên 8 + 8 = 16 không còn là hai con số nằm hai nơi.
  - **Đệm item `12px 14px` → `12px`** (LC-07) và **gutter trang 16 → 12** (LC-08, BA Q2) bằng token
    `--wujia-mshell-content-pad-x`, không vá theo màn.
  - **Vá lệch 5px giữa hai họ màn**: `/portal/purchase-history`, `/portal/order` render trong
    `.content-wrapper` của Vuexy (16,8px) còn màn BlankShell ăn token ⇒ thêm **1 rule ở khung** cho
    wrapper lấy chính token đó (không `!important` để Home còn tự bỏ lề được). Sau đó **mọi** màn
    mobile — kể cả `/portal/inspection` của anh Thái — đo đúng **12/12**, 0 tràn ngang.
  - **Vùng chạm nút “Chọn”** (màn đăng ký thi) 37×21 → **45×45** bằng cặp đệm + lề âm nên **card
    không cao thêm một pixel**. Đã chứng minh lỗi **có từ E5b2**, không do phiên này.
  - **Vá mốc đóng băng rỗng** `/portal/order`: route không có vùng danh sách nay lấy chữ ký **cả
    trang** (loại canvas/ApexCharts/`.resize-triggers`/đồng hồ) + báo `MỐC RỖNG`; khớp route đóng
    băng đổi từ tiền tố sang **khớp đúng**.
  - **Guard mạnh thêm**: `wj_listcard.py` đọc **variant** và kiểm dải cao theo variant; ở ≥992 đếm
    DOM thật thay vì báo sai “CHƯA MIGRATE” (**33 báo sai** biến mất).
- Số đo: `wj_listcard` **12 route × 8 khổ = 96 ô, 0 vi phạm** · inventory **16 route × 2 khổ, 194
  record, 0 vấn đề** (kể cả chữ ký đóng băng) · `wj_nesting` 0 · `wj_datalist` gap 8 đúng chuẩn ·
  `wj_measure` **0 HIERARCHY / 0 tràn / 0 lỗi JS / 0 redirect** · suite **686 tests, 0 failed,
  0 error** · mutation **10/10** (+2 mũi cấp công cụ) · `check_layers` **3 R1–R5 + 2 R7 có sẵn**.
- Commit: xem cuối phiên (1 commit code+test, 1 commit docs).
- Deploy: **chưa** — anh Huy deploy UAT.
- Lệch plan / quyết định mới:
  - Dải cao variant **không** lấy số đề xuất E5b2 (64–84 / 96–150) mà lấy **số đo thật 96 ô**:
    `compact-row` **64–112** · `detail-card` **96–156**. Hai dải nay **chồng nhau** ⇒ chiều cao
    không còn phân biệt variant, phân biệt bằng class. FYI cho BA.
  - **GIỮ** ô icon `.wj-lc__tile` 32×32 (ngoại lệ có chủ đích với LC-06/LC-07): nó là ô **tín hiệu
    trạng thái**, bỏ thì Thông báo mất màu theo loại.
  - `/portal/franchise-information` đo gutter **27** = 12 (trang) + 14 (đệm trong SurfaceCard) + 1
    (viền) — phạm vi `UI-SURFACECARD-001`, ghi nhận, không sửa ở E5c.
- Nợ để lại: `LC-20` Khảo sát defer vĩnh viễn (code anh Thái) · `LC-27` chỉ ghi nhận · `LC-23` Home
  preview giữ grouped rows · `/portal/debt` còn 1 dấu hiệu **có từ trước**: card cuối chạm mép thanh
  cố định (còn 125px đuôi cuộn nên chưa che bản ghi) — để cụm sticky/EmptyState xử.
- Phiên kế: theo `docs/next-session-clusters-F.md` §2 — **E6 · E7 · E8** + đề xuất cụm EmptyState;
  việc cần biết trước: cụm E5 đã khép, ListCard là nguồn chuẩn cho mọi danh sách mobile.
- Soi mã đối kháng (Codex, toàn cụm E5 `cf6d2b0^..HEAD`) cuối phiên: **4 finding, 4 đều THẬT** —
  (1) lệnh deploy thiếu 8 mô đun có view nằm trong DB ⇒ sửa ledger + ô Build/Deploy thành **10 mô
  đun**; (2) chấm "chưa đọc" màn Thông báo là span inline nên **đo 0px, chưa từng hiện** kể từ E5b1
  ⇒ vá + test + bump `wujia_portal_notification` 19.0.2.18.0; (3) nhánh LC-02 của guard chỉ có
  `pass` ⇒ thay bằng dấu hiệu thật `scrollHeight > clientHeight`; (4) inventory không kiểm
  `final_url` ⇒ thêm cờ `CHUYỂN HƯỚNG`. Cả 4 đều đã chứng minh bằng phép phá có kiểm soát.
  Suite sau khi vá: **687 tests, 0 đỏ**; `wj_listcard` vẫn **0 vi phạm**.

## E6a — Button `CMP-BTN-001`: atom + thước đo + 3 route mẫu (20/09/2026 · Mac)
- Kết quả: ✅ xong lượt E6a — `UI-BUTTON-001` (STT 132, dòng 125) **vẫn mở**, đóng ở E6c.
- Chốt đầu phiên của chủ dự án: chia **3 lượt** E6a → E6b → E6c · **màn auth migrate luôn cho đồng
  bộ** (lệch scope BA vốn chỉ liệt 13 route portal, làm ở E6b, ghi IMPACT) · cuối phiên **commit +
  push `main`, KHÔNG deploy UAT, issue vẫn mở**.
- Đã làm:
  - **Atom `wj-btn` / `wj-iconbtn`** ở khung: 5 variant + 3 bậc size, số lấy nguyên văn spec BA
    (PC 32/40/46 · mobile 36/44/48 · radius 8/12 · typo 13/18/600 · 14/20/700 · 15/22/700), khai
    bằng token `--wj-btn-*` nên PC/mobile chỉ là một khối `@media`. Vùng chạm 44 của bậc `sm` làm
    bằng **pseudo-element** nên visual vẫn 36 (khuôn đã dùng ở E4a cho ô lọc).
  - **Template `wj_button` + `wj_icon_button`** (2 nhánh vì QWeb 19 không đặt được tên thẻ động):
    có `btn_href` ⇒ `<a>`, không ⇒ `<button>`; `wj_icon_button` gắn `aria-label` **và** `title`.
  - **`wujia_button_loading.js`**: bắt `submit` ở pha capture, khoá form, gắn `is-loading` cho nút
    vừa bấm và `is-disabled` cho nút anh em, dọn lại khi `pageshow` (bfcache).
  - **21 call site / 5 file / 3 module** về atom (Hỗ trợ · Bù hàng · Thông báo) — phủ đủ **3 họ cũ**
    (`wj-pc-btn`, Bootstrap `btn*`, class lẻ `wujia-mreturn-btn-*`) đúng mục đích "3 route mẫu".
  - **Thước đo mới `scripts/qa/wj_button.py`**: mỗi route × khổ đo computed size/radius/typo, hộp
    chạm **kể cả pseudo**, variant, đếm Primary theo vùng hành động, **tab-walk thật** + focus ring,
    `disabled` không được nhận focus, và `is-loading` không được đổi bề rộng.
- Số đo: guard **9 route × 5 khổ = 45 ô, 0 vi phạm · 0 lỗi JS**; zoom 200% (khổ CSS 720/512) **10 ô,
  0 vi phạm**; **144 atom** đo được đúng 6 con số của BA, hộp chạm nhỏ nhất **72×48**; tab-walk 144
  nút **0 thiếu ring / 0 disabled còn focus**; 24 nút loading giữ **nguyên** bề rộng · `wj_measure`
  **0 tràn / 0 lỗi JS / 0 redirect / 0 HIERARCHY** · `wj_listcard` 0 · `wj_nesting` 0 · `wj_datalist`
  gap 8 · `b4_regression` **286/286** · suite **708 tests, 0 đỏ** (mốc E5c 687, +21 test mới) ·
  mutation **7/7** · `check_layers` **3 R1–R5 + 2 R7 có sẵn**.
- Commit: xem cuối phiên. Deploy: **chưa** (E6c gộp một lần).
- Lệch plan / quyết định mới:
  - **Nút của FilterBar là boundary**, không phải họ cũ: FB-08 cho Filter giữ 42/38/32 và **ưu tiên
    hơn** size mặc định của CMP-BTN-001 ⇒ thước đo loại cả `wj-filter*`/`wj-pc-filterbar*` (trước khi
    sửa là 18 báo nhầm).
  - **Hover viền theo WJ-PORTAL-UI-001 (`#28A9DF`)**, không theo `#BFE8F7` của BA — C6 đã chốt
    interaction state dùng chung. `--ghost` cố ý không nằm trong danh sách bề mặt của
    `_interaction.css` để không khai hai nơi cùng độ đặc hiệu.
  - **Test quét call site đặt ở `wujia_portal_base`** (khuôn mọi `test_scan_*` có sẵn, một sổ
    `MIGRATED` dùng chung) thay vì 3 file rời từng module như plan ghi — để E6b khỏi nhân bản logic
    đếm/so token 13 lần.
  - Hai màn danh sách trước dùng hai variant khác nhau cho **cùng vai trò** nút xem hàng
    (`--outline` vs `--secondary`) ⇒ thống nhất `--secondary`.
- Bẫy trong phiên:
  - Thước đo đọc variant chỉ theo `wj-btn--` nên **120 icon button ra `null`** ⇒ luật "≤1 Primary"
    hụt đúng nhóm đông nhất; đã dò cả `wj-iconbtn--` và thêm mã `VARIANT` cho atom không variant.
  - Regex `([^{}]+)\{([^}]*)\}` **nuốt cả rule con** nên rule trong `@media` không bao giờ được thấy
    (test vùng chạm xanh giả) ⇒ phải cấm luôn `{` trong thân.
  - Helper `_block()` của E5 tìm theo `selector + "{"`, **không thấy selector nằm trong danh sách**
    (`.wj-btn, .wj-iconbtn { … }`) ⇒ viết lại theo token đã tách dấu phẩy.
  - Cờ "Pass rỗng" ban đầu kêu cả khi màn **vốn không có nút hành động** ở khổ hẹp ⇒ siết lại: chỉ
    kêu khi có action mà 0 atom; đã chứng minh cờ vẫn bắt được bằng cách thêm `/portal/delivery`
    (chưa migrate) vào sổ `MIGRATED`.
  - **16 ô `b4_regression` đỏ là id cố định đã cũ**, không phải hồi quy: 4 route chi tiết redirect
    về danh sách vì `anh.owner` không còn thấy bản ghi (cả route của module E6a **không** đụng tới);
    đo lại bằng id có thật của `em.hcm` ⇒ **286/286**.
- Nợ để lại: gạch 12 của BA (retest 13 route, nhãn dài, submit lặp trên máy chủ) · **112 call site**
  còn lại (E6b 10 route + màn auth · E6c màn Thi + nút dựng bằng JS) · nút icon của header shell
  (`wujia-header-icon-btn`, 40×40, mọi route) để E6b làm một lần · `.wj-pc-btn` giữ cho Khảo sát =
  **LIMIT** (có test canh chiều ngược lại).
- Phiên kế: **E6b** — 10 route portal còn lại + màn auth (login/đổi mật khẩu/quên mật khẩu); việc
  cần biết trước: ma trận nghiệm thu `docs/e6a-acceptance-matrix.md`, sổ `MIGRATED` ở
  `custom/wujia_portal_base/tests/test_scan_e6_button.py`, và màn danh sách mobile **vốn 0 nút hành
  động** nên đừng đọc con số "mobile 40 action" của BA theo nghĩa đen.

## DOC-CTRL-2 — Đặc tả chi tiết controller cho BA (20/09/2026 · Mac)
- Kết quả: ✅ xong — `docs/controller-spec-detail.pdf` **110 trang / 10 chương**, mô tả **104/104
  đường dẫn** của **16 mô-đun**, gom thành **67 phiếu màn**. Phiên tài liệu: **0 file dưới
  `custom/`**, **0 lệnh ghi lên UAT**.
- Gốc yêu cầu: BA phản hồi bản kiểm kê 20 trang (DOC-CTRL 19/09) là "còn chung chung" — cần biết
  *màn sản phẩm đang lọc điều kiện gì, nút Đặt hàng đang check gì, danh mục portal lấy theo field
  nào*. Chủ dự án chốt: **cả 16 module có controller** (gồm Khảo sát của anh Thái + Metabase, chỉ
  ĐỌC) · **có** số thật trên UAT theo từng điều kiện lọc · tài liệu **MỚI** chia chương theo phân
  hệ · có mục **"ai xem được gì"** mỗi màn · **viết hết rồi giao một lần** · **không dán code Python
  vào file BA**.
- Đã làm:
  - **Khuôn "phiếu màn" 7 mục khoá từ chương 3**, không màn nào được thiếu: vào màn bằng đâu · ai
    xem được gì · màn hiện gì (bảng: khối · bảng dữ liệu · điều kiện lọc · sắp xếp · **thực tế
    UAT**) · người dùng lọc/nhập được gì · bấm nút thì kiểm gì (bảng **đúng thứ tự mã chạy**) · ghi
    gì vào hệ thống · điểm cần BA xác nhận (khung vàng).
  - **10 chương**: 1 cách đọc + bản đồ chương · 2 bản đồ 104 đường dẫn (máy sinh) · 3 Đặt hàng ·
    4 Khung portal + Trang chủ + quy ước dùng chung · 5 Lịch sử mua · Giao hàng · Báo cáo ·
    6 Công nợ · Đổi trả · 7 Hỗ trợ · Yêu cầu thông tin · Kiến thức · Thông báo · 8 Đăng ký thi ·
    9 Khảo sát (Thái) + Metabase · **10 Tổng hợp**.
  - **Chương 10** là thứ BA cần nhất: đối chiếu CT-001…CT-071 cập nhật (**56 ĐÃ CÓ · 6 MỘT PHẦN ·
    9 CHƯA CÓ**, nói rõ "một phần" thiếu luật nào) · 12 nhóm route có mã mà tab CT chưa mô tả ·
    **bảng 157 điểm cần BA chốt** gom từ mục 7 của mọi màn, phân 7 nhóm (PV/VT/NC/SL/DL/TB/CH) ·
    mục "BA đừng lên task viết lại".
  - **Bộ công cụ `scripts/qa/`** (đọc AST, không grep): `controller_spec.py` trích domain/ORM
    call/template/redirect/chuỗi kiểm · `uat_domain_probe.py` đếm thật qua XML-RPC **chặn cứng mọi
    method ghi** · `controller_spec_tex.py` sinh chương 2 · **`controller_spec_check.py` mới** kiểm
    chứng trước khi giao.
- Số đo: **147 phép đếm** trên UAT `wujia_tea_19` (chụp 20/09 01:18) · kiểm chứng
  `controller_spec_check.py`: phủ đường dẫn **104/104**, khuôn phiếu màn **67/67 đủ 7 khối**,
  **245 chỗ** dùng số UAT · build `lualatex` ×2: **110 trang, 0 hộp tràn, 0 ký tự thiếu**.
- Ba đính chính so với bản 19/09 (đã ghi ngay đầu chương 10):
  - **"Công nợ chưa nối `account.move`" KHÔNG còn đúng** — màn đang đọc hoá đơn và phiếu thu thật;
    điều cần chốt bây giờ là **cách tính kỳ và quy đổi tiền**, không phải nối dữ liệu.
  - **"Chưa dùng chung một hàm tải tệp" đúng một nửa** — thực tế **ba mức**: Đổi trả đọc nội dung
    thật của tệp · Hỗ trợ + Yêu cầu thông tin dùng chung một hàm nhưng chỉ tin lời khai trình duyệt ·
    Khắc phục khảo sát **không kiểm gì**.
  - **104 đường dẫn, không phải 103** — 2 đường dẫn có hai hàm (`/portal/exam/register`,
    `/portal/support/new`).
- Phát hiện đáng giá nhất (đều có số UAT kèm theo):
  - **Bốn cách hiểu "cửa hàng đang xem"** cùng tồn tại trong portal (bắt buộc chọn · cộng tất cả khi
    chưa chọn · luôn gộp · không phân biệt) và **ba cách chặn vai trò** khác nhau ⇒ gom thành **2
    quyết định** cho BA thay vì 25 câu hỏi lẻ.
  - **Ba phân hệ hiện không dùng được trên UAT vì thiếu dữ liệu**: Đổi trả **0 đơn** lọt cửa sổ 10
    ngày · Đăng ký thi **0 kỳ** đăng ký được (2 kỳ mở đều đã qua ngày thi) · Hỗ trợ **0 phiếu** do
    tài khoản cửa hàng thật tạo.
  - Công nợ: Home và màn Công nợ là **hai phép tính khác nhau** (ô tổng lưu sẵn, tiền công ty, mọi
    thời điểm ↔ tiền gốc chứng từ, một tuần) — giống nhau trên UAT chỉ vì **chưa cấu hình tỉ giá**.
  - Đổi trả: phiếu nháp là **ngõ cụt** (lưu được, không đường dẫn nào gửi được — 3 phiếu kẹt trên
    UAT) · **video tải lên không bao giờ hiện lại**.
  - `/portal/info-request/franchise/<id>/values` với loại "Khác" trả về **bất kỳ trường nào** của hồ
    sơ cửa hàng và **không kiểm vai trò** ⇒ Nhân viên đọc được số mà màn Công nợ đã chặn họ.
  - Chương 9 (mã anh Thái): **gửi khắc phục và lưu bài khảo sát không kiểm người gửi**; bảng
    Metabase **không khai nhóm quyền** nên ai đăng nhập cũng xem được.
- Lệch plan / quyết định mới:
  - Plan ước 110–140 trang, ra **110** — vì viết bằng lời nghiệp vụ, không dán mã.
  - Thêm chương kiểm chứng `controller_spec_check.py` (plan chưa có) để phép kiểm "phủ route" và
    "đủ 7 mục" chạy được bằng máy thay vì đếm tay.
  - Chương 2 (bản đồ route) **máy sinh lại mỗi lần thêm nhãn** — đã chạy lại 4 lần trong phiên.
- Bẫy trong phiên:
  - `probes.json` **trùng khoá** (`tb_toanhe`, `tb_daxem`, `kt_congbo`… đã có từ lượt Trang chủ) ⇒
    script dừng trước khi ghi, không để lại trạng thái dở; phải bỏ khoá trùng rồi chạy lại.
  - Chữ **`đ` đặt trong công thức toán** của LaTeX ⇒ lỗi build; phải viết "ký hiệu đồng Việt Nam".
  - Mục lục có **số trang 3 chữ số** ⇒ 9 hộp tràn; nới `\@pnumwidth`.
  - `execute_kw` của Odoo 19 nhận **`args = [domain]`**, truyền lồng thêm một lớp là
    `Domain() invalid item`.
- Nợ để lại: bản `controller-inventory.pdf` 20 trang **giữ nguyên** làm mục lục tổng · 4 con số UAT
  đo riêng (47 đơn · 60 ngày cửa sổ · 65 lượt xem · 86 điểm khảo sát) không nằm trong bảng đếm nên
  script chỉ cảnh báo, kiểm bằng mắt · **Q144/Q145/Q148/Q149/Q156** (mã anh Thái) dev phải trao đổi
  trực tiếp, chưa nói.
- Phiên kế: theo bảng §2 `docs/next-session-clusters-F.md` — cụm F tiếp tục. Việc cần biết trước:
  42 điểm nhóm **CH** trong chương 10 chính là danh sách chuẩn hoá cụm F đã có bằng chứng số, dùng
  thẳng được làm đầu vào; và **BA không lên task cho nhóm CH**.

## E6b1 — Button `CMP-BTN-001`: nghiệp vụ còn lại + Công nợ + luật ranh giới thanh lọc (20/09/2026 · Mac)
- Kết quả: ✅ xong lượt E6b1 — `UI-BUTTON-001` (STT 132, dòng 125) **vẫn mở**, đóng ở E6c.
- Chốt đầu phiên của chủ dự án: chia E6b thành **E6b1** (nghiệp vụ + Công nợ) → **E6b2** (Đặt hàng/giỏ
  + màn auth, submit 50→46) · nhóm "nửa boundary" **xử lý nhiều nhất có thể** · atom Primary đổi sang
  **#0F7CA8** thay vì #28A9DF của BA (giữ chuẩn a11y, sửa một chỗ) · cuối phiên **commit + push `main`,
  KHÔNG deploy UAT**, issue vẫn mở.
- Đã làm:
  - **32 call site / 11 file / 7 module** về atom: Giao hàng 6 · Thư viện 3 · Yêu cầu thông tin 5 ·
    Lịch sử mua 2 · Nền portal 5 (store picker, danh sách/hồ sơ cửa hàng) · **Công nợ 10**.
  - **Luật ranh giới thanh lọc** — trả lời câu "làm sao đồng bộ": cùng file `portal_debt.xml`, cùng
    class `wj-pc-btn--primary` vừa là nút lọc (giữ 42 theo FB-08) vừa là nút hành động (về 40 theo
    CMP-BTN-001) ⇒ đồng bộ theo **ngữ cảnh** ở 4 tầng: token hoá 42/38/32 · CSS khai theo ngữ cảnh
    (`.wj-debt-pc-filter .wj-pc-btn`) · thước đo nhận diện theo **tổ tiên DOM** thay vì tiền tố class ·
    **test bắt chéo hai chiều** (không nút lọc nào được mang atom · từng khối CSS nút lọc phải đọc token).
  - **Vá 8 lỗi a11y thật**: 4 nút sao chép công nợ, 2 nút đóng modal, 2 nút xem chi tiết nay có
    `aria-label` tiếng Việt; 2 nút icon navbar (chuông, giỏ) cũng được đặt tên dù giữ boundary.
  - **Sửa bẫy "Pass rỗng" của chính thước đo** (phần nặng nhất phiên): lần đo đầu xanh nhưng **6/9
    route trong sổ ra 0 nút** — sổ ghi sai route (`/portal/franchise-information` render template
    khác), nút chỉ dựng ở khối rỗng, bảng yêu cầu **0 bản ghi**, màn lịch sử thanh toán vốn không có
    nút. Sửa cả sổ lẫn luật: route trong sổ mà không dựng nổi nút nào ⇒ **vi phạm**; so route bằng
    chuỗi đầy đủ; so URL sau khi giải mã `%`; **màn chi tiết dò lúc chạy** từ trang danh sách.
  - **`scratchpad/e6b1/overlay_probe.py`**: 5 call site nằm trong lớp phủ (store picker, modal thanh
    toán) không route nào thấy vì mặc định ẩn ⇒ probe mở lớp phủ rồi đo bằng đúng PROBE của thước đo.
- Số đo: thước đo **18 route × 5 khổ, 0 vi phạm · 0 lỗi JS**, **278 ô atom** đúng 6 con số BA (PC 32/40,
  mobile 36/44/48, radius 8/12, chạm mobile nhỏ nhất 44); zoom 200% (720/512) **0 vi phạm**; lớp phủ
  **0 vi phạm** · suite **714 tests, 0 đỏ** (mốc E6a 708, +6 test mới) · mutation **8/8 mũi đỏ đúng
  guard** · `wj_filterbar` **ĐẠT** · `wj_measure` 0 tràn/0 lỗi JS/0 redirect/0 HIERARCHY · `wj_listcard`
  0 · `wj_nesting` 0 · `b4_regression` **286/286** · `check_layers` 3 R1–R5 + 2 R7 **có sẵn, không thêm**.
- Lệch plan / quyết định mới:
  - **LIMIT** nút icon navbar (chuông + giỏ) **là boundary** — plan định migrate, đo ra 96 vi phạm:
    `_pc_account.css` cố ý cho hai nút 40×40 bo 20 nền kính để thắng padding `.nav-link` của Vuexy.
    Cùng loại BottomNavigation mà BA đã liệt boundary ⇒ giữ nguyên, ghim bằng test.
  - **LIMIT** `/my/franchises` dùng khung `portal.portal_layout` của Odoo, CSS design system không nạp
    ở đó nên atom ra **nút trần** ⇒ trả lại Bootstrap; bản Vuexy `/portal/franchises` mới là atom.
  - **IMPACT** atom Primary `#28A9DF` → `#0F7CA8` (BA ghi màu trượt WCAG AA 2.68; #0F7CA8 = 4.7 và đã
    là CTA portal từ Sprint 38) — **ảnh hưởng ngược 21 call site của E6a**, đã chụp lại đối chiếu:
    chỉ màn có nút Primary đổi, 2 màn danh sách giống hệt từng byte.
  - Số call site **32** chứ không phải 34 của plan (trừ 2 nút navbar); Công nợ **10/13** chứ không 11.
  - `btn-outline-danger` → `wj-btn--danger` đặc (BA không có bậc outline-danger).
  - Sửa 2 sổ của cụm khác cho khớp: F4 bỏ dòng `wj-debt-pc-pdf wj-state-surface` (nút đã về
    `--secondary`, variant nằm sẵn trong danh sách bề mặt) · E4 đổi ghim `38px` cứng sang ghim **token**.
- Nợ để lại: **E6b2** Đặt hàng/giỏ (25 action) + màn auth (submit 50→46) · **E6c** màn Thi + gạch 12
  của BA + **một lần deploy UAT** rồi đóng issue · sổ thước đo còn 2 route phụ thuộc dữ liệu mẫu.
- Phiên kế: **E6b2** — việc cần biết trước: `/portal/order` có 25 action và **JS dựng nút giỏ**, phải
  grep `querySelector` trước khi đổi class; màn auth nằm ngoài vỏ portal nên kiểm CSS có nạp không
  (bài học `/my/franchises` phiên này).

## E6b2 — Button `CMP-BTN-001`: màn Đặt hàng/giỏ + toàn bộ màn auth (21/09/2026 · Mac)
- Kết quả: ✅ xong lượt E6b2 — `UI-BUTTON-001` (STT 132, dòng 125) **vẫn mở**, đóng ở E6c.
  Nghiệm thu đầy đủ: `docs/e6b2-acceptance-matrix.md`.
- Chốt đầu phiên của chủ dự án: **auth migrate hết, kể cả khối legacy tiếng Anh** · nút thêm-vào-giỏ
  theo hàng **là boundary** cùng thể với stepper · cuối phiên **commit + push `main`, KHÔNG deploy UAT**,
  issue vẫn mở (E6c gộp một lần deploy).
- Đã làm:
  - **19 call site / 6 file / 2 module** về atom: giỏ mobile 3 · panel giỏ PC 3 · chi tiết sản phẩm 2 ·
    `login_page.xml` 6 (đăng nhập · 2FA · quên MK · đặt lại MK · 2 nút khối đăng ký) · `forgot_pass.xml` 2 ·
    đổi mật khẩu 3. Plan ghi 20 — đếm nhầm cặp Hủy/Lưu PC.
  - **Xoá hẳn họ `wj-cta-btn`** (31 dòng `_components.css`): sau E6b1 chỉ còn đúng một người dùng.
  - **Luật móc JS** (kế thừa E6b1): grep ra đúng **2** tên JS bám (`btn-add-cart-detail`,
    `wujia-mcart-submit`) ⇒ giữ tên, **gỡ sạch khai dáng**; 4 tên còn lại không ai bắt ⇒ chỉ giữ bố cục.
    Test ghim cả hai vế: móc còn đủ hai phía **và** móc không được khai `height/radius/background/font-*`.
  - **Thước đo đo được màn chưa đăng nhập**: thêm danh sách `ANON` chạy trong context trình duyệt sạch
    sau vòng chính (+ cờ `--no-anon`), và **in mã HTTP** khi trang không trả 200.
  - **Vá a11y**: 2 nút xóa dòng giỏ (mobile + PC) nay có `aria-label`/`title` tiếng Việt.
- Số đo: thước đo **29 route × 5 khổ, 0 vi phạm · 0 lỗi JS**, **338 ô atom** (PC 32×219 / 40×57 / 46×12;
  mobile 36×8 / 44×30 / 48×12; radius 8×227 / 12×111; chạm mobile nhỏ nhất **44**); zoom 200% (720/512)
  **0 vi phạm**; trạng thái giỏ rỗng đo riêng bằng `anh.owner` **4 action / 4 atom / 0 vi phạm** · suite
  **722 tests, 0 đỏ** (mốc E6b1 714, +8 test mới) · mutation **11/11 mũi đỏ đúng guard** · `wj_filterbar`
  **ĐẠT** · `wj_measure` 0 tràn/0 lỗi JS/0 HIERARCHY · `wj_listcard` 0 · `wj_nesting` 0 · `b4_regression`
  **286/286** · `check_layers` 3 R1–R5 + 2 R7 **có sẵn, không thêm**.
- Lệch plan / quyết định mới:
  - **IMPACT 1** submit màn auth PC **50 → 46** (bậc `lg` của BA), mobile giữ **48**. Nhịp dọc Figma S39
    giữ nguyên: `.wj-auth-submit` chỉ còn `margin-top` 21 / 20.5px.
  - **IMPACT 2** nút *Lưu mật khẩu* mobile **46 → 48** (46 là số PC dùng nhầm cho mobile).
  - **Cơ chế đã giữ nút auth ở 50px**: `_auth.css` nạp **SAU** `_components.css` nên mọi khai dáng sót lại
    đều thắng atom. Màn auth **có** nạp design system (`login_layout` → `asset_frontend`) ⇒ không phải
    bẫy `/my/franchises` của E6b1, không cần đụng asset bundle.
  - **LIMIT** ba template auth `signup`, `login_totp`, `forgot_pass_back` **không controller nào render** —
    vẫn migrate cho đồng bộ nhưng **không có bằng chứng đo bằng trình duyệt**; ghim bằng test: ngày nào
    có controller render, test đỏ để bắt đi đo thật.
  - **Variant `ghost` tự khai trạng thái nhấn**, không mượn marker `wj-state-surface` của F4 (danh sách bề
    mặt `_interaction.css` hover thêm viền + bóng, sai dáng nút icon trong hàng). F4 đếm marker ở 2 file giỏ
    **3 → 2**, đúng tiền lệ E6b1 với nút PDF công nợ.
  - **`/portal/forgot-pass` có `rate_limit` 10 lần/giờ theo IP** (`auth.py:89`) — đo lặp là **HTTP 429**, và
    thước đo cũ báo nhầm thành "không có nút hành động nào". Bộ đếm trong RAM, khởi động lại server là sạch.
  - **Bẫy "Pass rỗng" phiên bản trạng thái**: nút *Gửi đơn*/*Xóa dòng* chỉ có khi giỏ **có hàng**, CTA
    *Chọn sản phẩm* chỉ có khi giỏ **rỗng** ⇒ phải đo bằng **hai tài khoản**.
- **Phát hiện ngoài phạm vi (chưa sửa)**: `/portal/login` **tràn ngang 74px** ở khổ 390 (`scrollWidth` 464),
  do `.wj-auth__decor--1` (mép phải 479px) + cụm đổi ngôn ngữ. Ảnh **trước/sau giống hệt** ⇒ lỗi có sẵn,
  không do E6b2; cụm auth đang **KHÓA THIẾT KẾ S39** nên cần duyệt trước khi động.
- Nợ để lại: **E6c** màn Thi (30 nút XML + nút dựng bằng JS) + gạch **12** của BA + **một lần deploy UAT**
  rồi đóng issue, kèm quyết định về tràn ngang màn đăng nhập · 3 template auth chết · cụm **EmptyState**.
- Phiên kế: **E6c** — việc cần biết trước: màn Thi có nút **dựng bằng JS** (không grep XML là đủ);
  deploy UAT phải gộp `-u` của cả E6a + E6b1 + E6b2; trước khi đo lại màn auth trên máy chủ nhớ
  `rate_limit` 10 lần/giờ.

## E6c — Button `CMP-BTN-001`: màn Thi + gạch 12 + khép `UI-BUTTON-001` (23/09/2026 · Mac)
- Kết quả: ✅ xong lượt cuối cụm E6 — code + doc **đã push `main`**, **chờ chủ dự án deploy UAT** rồi mới
  `qa_sync` đưa `UI-BUTTON-001` (STT 132, dòng 125) sang Ready for Retest. Nghiệm thu: `docs/e6c-acceptance-matrix.md`.
- Chốt đầu phiên của chủ dự án: ô ngày/khung giờ/FAB/nút lùi wizard màn Thi **là boundary nhưng đọc token
  `--wj-btn-*`** (để sau này đổi token một chỗ là theo) · **vá tràn ngang màn đăng nhập** (IMPACT) ·
  **commit + push `main`, anh tự deploy**.
- Đã làm:
  - **30 call site màn Thi** về atom: 21 `.wj-btn` + 7 `.wj-iconbtn` trong `portal_exam.xml`, 2 `.wj-iconbtn`
    dựng bằng JS (sửa/xóa dòng người thi). Xoá hẳn họ `wujia-mexam-btn*`, `wj-exam-pc-navbtn`,
    `wj-exam-pc-iconbtn`, `wujia-mexam-cal-navbtn`, `wujia-mexam-person-del`.
  - **Boundary đọc token**: 5 khối CSS (ô ngày PC/mobile, ô khung giờ PC/mobile, FAB) bỏ số px cứng; trạng
    thái *đang chọn* dùng `--wujia-cta` như primary của atom.
  - Gửi đăng ký (PC + wizard mobile) dùng `setBusy()` = `.is-loading` của atom thay kiểu đổi chữ.
  - **Màn đăng nhập hết tràn ngang** 464 → 390: gốc là **tên ngôn ngữ** (thêm ở `WJ-LANG-001`) nhét vào pill 72px
    của Figma, bóp cờ còn 3px và đẩy chữ ra ngoài mép; ở điện thoại nay ẩn mắt tên ngôn ngữ (trình đọc màn hình
    vẫn đọc), cờ đủ 20px, bỏ caret Bootstrap trùng; `overflow-x` trên `.wj-auth` giữ làm lưới an toàn.
  - **Guard mới** `test_class_di_kem_atom_khong_gianh_dang` (sổ chung portal_base): class đứng cùng phần tử với
    atom cũng không được khai dáng — mũi M8 lần đầu lọt qua guard cũ.
  - Gạch 12: `scratchpad/e6c/bullet12.py` — 13 route × nhãn dài VI/EN/ZH × 3 khổ, submit lặp (form + fetch,
    không gửi thật), Enter/Space.
- Số đo: `wj_button` **32 route × 5 khổ, 0 vi phạm · 0 lỗi JS**, **358 ô atom** (PC 32×225 / 40×69 / 46×12;
  mobile 36×8 / 44×30 / 48×14; radius 8×233 / 12×125); zoom 200% **0 vi phạm**; từng trạng thái màn Thi
  (`exam_states.py`) **0 vi phạm** · suite **729 tests, 0 đỏ** (mốc E6b2 722, +7) · mutation **10/10** ·
  `wj_measure` trước/sau (stash) **0 dòng khác** · `wj_filterbar` **ĐẠT** · `wj_listcard` 0 · `wj_nesting` 0 ·
  `b4_regression` **286/286** · `check_layers` 2 R7 có sẵn, không thêm · gạch 12: submit lặp **1 request**
  giữ bề rộng (form 136,6px · fetch 174px), bàn phím **28/28**.
- Lệch plan / quyết định mới:
  - **2 LIMIT nhãn dài**: nút *Xem* trong dòng bảng PC (Giao hàng, Công nợ) làm bảng cuộn ngang **bên trong**
    khung bảng — hành vi DataTable, trang không cuộn; nhãn EN 44 ký tự ở nút full-width khổ 360 dư 6px — BA chốt
    "một dòng, không giảm font" nên đặt quy ước nhãn ≤ 40 ký tự Latin.
  - **IMPACT**: FAB `#28A9DF` → `#0F7CA8`; ô ngày mobile 38 → 36; ô ngày PC bo 6 → 8; ô khung giờ mobile ~51 → 48;
    nút đóng modal về ghost 32px (đồng bộ Công nợ/chọn cửa hàng); nút đổi tháng PC 32×28 → 32×32.
  - **LIMIT** nút lùi wizard mobile chạm 28×30 — thuộc BackPageHeader (`UI-BACKPAGEHEADER-001`), không đổi dáng ở E6.
- **Bài học môi trường đo**: `wj_filterbar` báo CHƯA ĐẠT, chạy lại trên HEAD (stash E6c) **y hệt** ⇒ không do E6c.
  Gốc: `wj_ajax_list.js` lọc bằng `fetch` + `pushState`, server đang `--dev=xml` nên một lượt lọc mất 3,1 giây,
  quá thời gian chờ của thước đo. **Đo giao diện luôn dùng server không `--dev=xml`** (cần nạp view thì `-u` rồi
  khởi động lại).
- **Retest UAT 24/09** (anh deploy; 12/12 module khớp `latest_version` qua XML-RPC chỉ-đọc). Chạy qua
  `scratchpad/e6c/uat_guard.py` (chặn mọi POST ngoài login + 4 route chỉ-đọc; **0 POST phải chặn**):
  `wj_button` **30 màn × 5 khổ + zoom 200%, 175 lượt atom, 0 vi phạm nút · 0 lỗi JS** (PC 32/40/46, mobile
  36/44/48, radius 8/12) · trạng thái màn Thi **0** · login 360/390/1440 hết cuộn ngang (3 route) · submit lặp
  1 request giữ bề rộng (136,5 / 174) · bàn phím **18/18** · nhãn dài: 5 ghi nhận đều thuộc 2 LIMIT cũ.
  Vi phạm tổng là môi trường: UAT chưa có `wujia.info.update.request` nào + em.hcm/anh.owner không có công nợ
  (màn chi tiết YC thông tin, `/portal/debt*` chỉ đo được local — ghi LIMIT); `/portal/forgot-pass` trả 429 vì
  chính các lượt đo chạm `rate_limit` 10/giờ. `wj_button` dò màn động hụt thì giữ placeholder ⇒ trên UAT phải
  truyền `--routes` bỏ placeholder đó. `qa_sync` UI-BUTTON-001 → **Ready for Retest**.
- Nợ để lại: nút lùi wizard 28×30 (BackPageHeader); cụm **EmptyState**; 3 template auth chết (E6b2).
- Phiên kế: sau khi UAT xác nhận E6 ⇒ **E7a** PageContainer `CMP-PC-001` (`UI-PAGECONTAINER-001`, STT 129).

## E7a — PageContainer `CMP-PC-001`: khung + gutter (24/09/2026 · Mac)
- Kết quả: ✅ xong lượt đầu cụm E7 — code + doc **commit local, chưa push**; `UI-PAGECONTAINER-001` (STT 129,
  dòng 122) **giữ Ready for Dev** tới E7b. Nghiệm thu: `docs/e7a-acceptance-matrix.md`.
- Chốt đầu phiên của chủ dự án: **E7a trước, phân cụm 140–145 sau E8** (143/145 đo lại trên khung mới) ·
  **sửa tối thiểu vỏ Khảo sát** (code anh Thái, chỉ vỏ, không logic) · **lề mobile: danh sách 12, còn lại 16**.
- Đã làm:
  - `app_layout` có **một** `<main class="wj-page-container">` bọc `t-out="0"`; Global Shell (header mobile,
    sidebar, bottom-nav) nằm ngoài. 4 token `--wj-page-gutter*` / `--wj-page-pad-bottom`.
  - `.content-wrapper` về 0 ở **mọi khổ** (mốc cũ 24px chỉ ở ≥1200 ⇒ 992–1199 rơi về Vuexy 30,8).
    Bỏ lề `.wujia-mpage`, `.wj-debt`, `.wujia-mhome`, `.wujia-home-wrapper`, đáy 96 của `.app-content`.
  - Biến thể `wj-page-container--list` (12) bật bằng `t-set pc_gutter='list'` ở **12 màn danh sách**.
  - **Gốc "tiêu đề lệch 16px" của BA**: rule không phạm vi `.wj-page-header {padding 16px !important}` trong
    `portal_inspection.css` (`ad7ffc3`, 07/08) đè PageHeader của **mọi** màn. Gỡ + guard.
  - Khảo sát: vỏ danh sách/chi tiết/khắc phục bỏ lề ngang + nền (`py-*` giữ nhịp dọc), bỏ max-width + `min-height:100vh`.
  - Thước đo mới `scripts/qa/wj_pagecontainer.py` (7 kiểm PC-1…PC-7, `--diff`, `--collapsed`).
  - Guard: `wujia_portal_layout/tests/test_e7_page_container.py` (11) + sổ chung
    `wujia_portal_base/tests/test_scan_e7_page_container.py` (6, gồm cấm class `p-*`/`px-*` trên vỏ route).
- Số đo: `wj_pagecontainer` 31 route × 6 khổ **707 → 0 vi phạm · 0 lỗi JS**; sidebar thu gọn **0**; zoom 200%
  **0** · suite **746 tests, 0 đỏ** (mốc E6c 729) · mutation **13/13** · `wj_measure` so E6c: 0 tràn/0 lỗi JS/
  0 redirect/0 HIERARCHY, **0 ô mất record**, chiều cao chỉ đổi trên trục đã duyệt · `wj_button` 0 ·
  `wj_listcard` 0 · `wj_filterbar` ĐẠT · `wj_nesting` 0 · `b4_regression` **286/286** (bản thay ID) ·
  `check_layers` 2 R7 có sẵn, không thêm.
- Lệch plan / quyết định mới:
  - **LIMIT** đệm đỉnh mobile 10 (token nhịp dọc 18/09), không phải 16 của spec — đổi một token nếu BA muốn.
  - **LIMIT** chưa có `bottomInset` cho sticky action (giỏ giữ đáy 150 riêng) ⇒ E7b.
  - Plan ghi "Khảo sát không đụng" ⇒ chủ dự án duyệt sửa tối thiểu; bàn giao anh Thái ở matrix.
  - `pc_account_layout` là partial trong `app_layout` ⇒ không cần vỏ riêng.
- **Bài học đo**: `b4_regression.py` dùng ID cứng — DB local đã mất `return/12`, `notification/41`, anh.owner
  hết giao hàng ⇒ báo 270/286 giả. Chạy lại bằng ID dò từ màn danh sách (`scratchpad/e7a/b4_local.py`).
  Thước đo gutter phải bỏ qua lề Bootstrap `.row`/`col-*` và cột phải của lưới, không thì báo nhầm.
- Nợ để lại: Khảo sát chi tiết/khắc phục chưa đo sống (DB local 0 phiếu) · sidebar overlay 992–1199 (E8) ·
  PC chi tiết Khảo sát có thể hiện hai tiêu đề (báo anh Thái).
- Phiên kế: **E7b** — width variant `fluid/standard 1440/narrow 960` + `bottomInset` + đo UAT chỉ-đọc ⇒ đóng
  `UI-PAGECONTAINER-001` (Ready for Retest). Cần deploy E7a+E7b cùng lượt.

## E7b — PageContainer `CMP-PC-001`: width variant + bottomInset (24–25/09/2026 · Mac)
- Kết quả: ✅ khép cụm E7 — `UI-PAGECONTAINER-001` (STT 129, dòng 122) **Ready for Retest** 25/09 sau đo UAT. Nghiệm thu: `docs/e7b-acceptance-matrix.md`.
- Đã làm:
  - `app_layout` thêm 2 công tắc cùng kiểu `pc_gutter`: `pc_width` (`standard` 1440 / `narrow` 960, fluid = không đặt) và
    `pc_bottom='sticky'`. Max-width đặt **trên chính `<main>`** (bề rộng trong + 2 gutter, căn giữa) ⇒ PageHeader cùng
    bề rộng nội dung, không thêm lớp DOM.
  - Cờ theo mapping BA ở **29 template**: narrow 4 (giỏ, tạo bù hàng, tạo hỗ trợ, tạo YC thông tin), standard 25
    (Bù hàng danh sách, Tài khoản, hồ sơ cửa hàng, mọi màn chi tiết, Khảo sát chi tiết/khắc phục…), còn lại fluid.
  - Đáy: gỡ đáy **chồng** của Đặt hàng (`.wujia-morder` 150) và giỏ (`.wujia-mcart` nav+116); container `--sticky`
    = nav + `--wj-sticky-action-h` (68 floatbar; giỏ khai 200 qua `:has(.wujia-mcart-summary)`) + gap 16.
  - Gỡ `.wj-pc-cart-standalone {max-width:760}` — bề rộng trang thuộc container.
  - Thước đo `wj_pagecontainer.py`: trục x đo từ **mép container** (narrow căn giữa), thêm **PC-8 WIDTH**, in biến thể.
  - Guard +10: `test_e7_page_container.py` (4) + sổ `test_scan_e7_page_container.py` (6: sổ width theo mapping, cấm
    narrow cho danh sách, cấm max-width ≥600 trong CSS route trừ 2 component, cấm route tự chừa đáy, sticky bật đúng màn).
- Số đo: `wj_pagecontainer` 31 route × **7 khổ (thêm 1920)** 0 vi phạm · 0 lỗi JS; sidebar thu gọn 0; zoom 200% 0 ·
  `--diff` **0 ô mật độ giảm** · narrow 960 @1024/1440/1920, standard 1440 chỉ @1920 · suite **756, 0 đỏ** (E7a 746) ·
  mutation **10/10** · `wj_measure` 0 ô mất record · `wj_button` 0 · `wj_listcard` 0 · `wj_filterbar` ĐẠT · `wj_nesting` 0 ·
  `b4` **286/286** · `check_layers` không thêm · `test_ownership` cross 0.
- IMPACT: giỏ PC 760 → 960 căn giữa; 3 form tạo mới thu về 960 căn giữa ở ≥1024; Đặt hàng mobile ngắn 79px.
- LIMIT: Khảo sát chi tiết chưa đo sống (0 phiếu local); chiều cao thanh sticky là token khai báo; `:has()` cần Safari 15.4+.
- Bài học: `b4_local.py` mặc định cổng 8055 — phải `--base http://127.0.0.1:8090`. Test chạy không `-u` chết ở
  `wujia_franchise/tests` (import file đã xoá) — luôn kèm `-u`. Log test bị `wujia_core` chuyển sang `<logdir>/<năm>/<tháng>/`.
- **UAT 25/09** (sau deploy, chỉ-đọc, 0 POST): 217 ô 0 vi phạm · thu gọn 0 · zoom 0 · **Khảo sát chi tiết/khắc phục đo sống
  0** (đóng LIMIT). Commit `419f9c9` (+`8ef3081`) đã push. Ledger + `qa_sync --apply` ⇒ `UI-PAGECONTAINER-001` **Ready for Retest**.
- Báo Thái: Khảo sát chi tiết PC có **2 tiêu đề** (`wj_page_header` + `.wj-pc-page-header` tự dựng, từ `2828171`) — thuộc PageHeader.
- Bài học: route `wujia_portal_inspection` trên UAT chuyển `/vi/…` ⇒ đo bằng `/vi/portal/inspection…`.
- Phiên kế: **E8** SidebarNavigation (`UI-SIDEBAR-001`).

## E8a — SidebarNavigation `CMP-SN-001`: đo hiện trạng, 0 code (25/09/2026 · Mac)
- Kết quả: ✅ xong lượt đo. `UI-SIDEBAR-001` (STT 131) **giữ Ready for Dev** tới E8b. Kiểm kê: `docs/e8a-sidebar-inventory.md`.
- Đã làm: đo local (`wujia_e4b1`, 8090) + UAT chỉ-đọc (`uat_guard`), `em.hcm`, 9 khổ, 32 route. **UAT khớp local tuyệt đối.**
  - **Width 264 chỉ cần CSS**: đổi token ⇒ `.main-menu` 264, content +36px (1140→1176), JS Vuexy không ghi đè
    (`$.app.menu.init/change` đã no-op ở `my_js.js`).
  - **Drawer 992–1199 kẹt mở**: gốc là `_wujiaForceMenuExpanded()` (`my_js.js:284`) ép `menu-open` ở ≥992 mỗi lần
    load/resize; hamburger nằm dưới drawer 260px nên không bấm được; toggle/Escape/bấm ngoài đều không đóng; 0 backdrop,
    2 `.sidenav-overlay` trùng.
  - **Q3**: sidebar PC **không có** mục Bù hàng (plan cũ ghi có `nav_item_return` là sai) ⇒ `/portal/return*`,
    `/portal/reports/orders`, `/portal/info-request*` không sáng mục nào; 29/32 route còn lại sáng đúng mục cha.
  - Item: cao 44 ✓, icon 20 ✓, focus ✓; lệch: đệm `10px 15px`, gap 26, bo 8/active 4, chữ 16/400, màu active `#28A9DF`,
    không rail, 0 `aria-current`. Brand 132px, logo 184×86. Hamburger 0 accessible name.
  - Chuông PC đạt (badge = unread thật, popup + "Xem tất cả", Escape); avatar dropdown 4/7 mục BA; tên gọi lệch PC↔mobile ở 3 route.
- Commit: chưa commit (chỉ doc).
- Deploy: không.
- Số đo: `sidebar_probe` 9 khổ × 2 môi trường 0 lệch · 0 lỗi JS · UAT 1 POST chặn (`/notification/recent`, do cú bấm chuông của thước đo).
- Lệch plan / quyết định mới: plan ghi 12 `sidenav_inherit`, thật **10** (F5a); Bù hàng/Báo cáo là **tạo mới** mục PC,
  không phải đổi nhãn. Dời Khảo sát xuống cuối nhóm bằng `position="move"` (Odoo 19 hỗ trợ), không sửa file anh Thái.
- Quyết định mới: chủ dự án chốt "chuẩn hoá bám BA hết" ⇒ 5 điểm tưởng là fork đều chốt theo câu BA (§4 kiểm kê):
  avatar đủ 7 mục + gỡ dropdown ngôn ngữ riêng (khối cửa hàng giữ cho STT 140) · quyền = điều kiện controller · info-request
  sáng "Hồ sơ cửa hàng" trong avatar · bỏ hover trượt · <992 `display:none`.
- Nợ để lại: báo BA `/portal/info-request` không có lối vào nào trong UI (ngoài E8, cần issue riêng).
- Phiên kế: **E8b** code theo §2–§3 kiểm kê. Test khoá sidebar phải sửa cùng lượt: `test_f5_nav_item.py` ×9,
  `test_f5_menu_ownership.py`, `test_f5_frame_routes.py`; chụp lại mốc `nav_dump`.

## E8b — SidebarNavigation `CMP-SN-001`: sidebar PC + drawer 992–1199 (25/09/2026 · Mac)
- Kết quả: ✅ xong lượt code. `UI-SIDEBAR-001` (STT 131) **giữ Ready for Dev** tới E8c. Nghiệm thu: `docs/e8b-acceptance-matrix.md`.
- Cụm E8 chia **3 phiên** (chủ dự án chốt 25/09): E8a đo · **E8b sidebar PC + drawer** · E8c avatar/mobile/UAT/ledger.
- Đã làm:
  - Khung `layout_sidenav` chỉ còn 4 neo (`nav_header_main` / `_finance` / `_ops` / `nav_end`) — 3 nhóm BA "Chức năng chính ·
    Tài chính & xử lý · Hỗ trợ vận hành". Gỡ nhóm Tiện ích + Tài khoản (về avatar), spacer, `mb-5`, logo 200×100, overlay trùng.
  - 10 module sở hữu route tự khai mục (`before` neo nhóm kế): Giao hàng lên trước Lịch sử · "Công nợ & thanh toán" ·
    **mới** "Đổi trả / Bù hàng" (return) + "Báo cáo" (report) · Thông báo rời sidebar (chuông). Quyền = điều kiện controller:
    Công nợ theo `_debt_access`, Báo cáo theo vai trò cao nhất owner/manager — `_nav_mgr_fids` tính 1 lần/trang ở `base`.
  - **Sửa tối thiểu file anh Thái** (`wujia_portal_inspection/views/sidenav_inherit.xml`, chủ dự án duyệt, tiền lệ E7a): neo
    `nav_end` + `wj_nav_item`; ghi bàn giao trong matrix.
  - `wj_nav_item` có `aria-current`. `_sidebar.css` mới giữ mọi dáng sidebar (264, brand 88, mục 44/10/12/15-22-500, bo 10 mọi
    state, active 700 `#EAF7FD`/`#168FC2` + rail 3, hover không trượt, nhóm rỗng tự ẩn, drawer, ẩn <992).
  - Drawer 992–1199: `my_js.js` chỉ ép mở ≥1200; `wujia_sidebar.js` mới (hamburger `<button>` đủ aria, nút Đóng, Escape,
    backdrop, focus vào/ra). Migration `pre-10` xoá view con của `layout_sidenav` (neo cũ mất ⇒ view cũ hỏng validate).
- Commit: local `feat(E8b)`, chưa push. Deploy: **không**.
- Số đo: `wj_sidebar` (mới, `scripts/qa/`) **0 vi phạm** × 4 vai trò, 9 khổ, 21/21 route sáng đúng + `aria-current`, 7 route
  ngoài sidebar sáng 0 · suite **779, 0 đỏ** (E7b 756) · mutation **14/14** · DB trắng chỉ cài khung 0 failed / 1 error (nợ F6
  có sẵn) · `wj_pagecontainer` 0 · `wj_button` 0 · `wj_listcard` 0 · `wj_filterbar` ĐẠT · `wj_nesting` 0 · `b4` 286/286 ·
  `check_layers` không thêm · `test_ownership` cross 0 (asserts 425 → 491) · `nav_dump` 9 route đổi mục sáng, đều chủ đích;
  mốc mới `docs/e8b-baseline/nav_em.json`.
- Lệch thước đo (không phải hồi quy): `wj_measure --diff` 26 ô "mất record" ở 360/390 = đúng 14 `li` sidebar cũ bị đếm
  khi còn nằm ngoài màn; `wj_button` thêm boundary `wj-menu-toggle`/`wj-sidebar` (hamburger nay là `<button>`).
- Bài học: đột biến ở module X mà guard ở `portal_base` ⇒ `-u X,wujia_portal_base`, không thì **0 test chạy** (Pass rỗng) ·
  test phải kèm `--db-filter='^wujia_e4b1$'` (config lọc `wujia_tea_19` ⇒ HttpCase rơi về trang login) · `style.css:96`
  đặt `.main-menu` z-index 1040 !important — drawer phải 1041 mới trên backdrop · focus vào drawer phải đợi hết transition.
- LIMIT: sheet "Thêm" mobile có Báo cáo không điều kiện vai trò (E8c) · ẩn nhóm rỗng cần Safari ≥ 15.4 (`:has`).
- Phiên kế: **E8c** — avatar dropdown 7 mục + gỡ dropdown ngôn ngữ topbar + `aria-expanded` chuông + avatar/sheet mobile
  + tên gọi PC↔mobile + deploy E8b+E8c + đo UAT chỉ-đọc (`wj_sidebar --base` UAT) + ledger/`qa_sync` ⇒ Ready for Retest.

## E8c — `UI-SIDEBAR-001` avatar dropdown · sheet "Thêm" mobile · chuông (25/09/2026 · Mac)
- Kết quả: ✅ **xong cụm E8**. Push `main` (`078dfeb`), chủ dự án deploy UAT (lượt 2 — lượt 1 `-u` khi máy chủ chưa có
  mã, 13/13 module vẫn bản E7b), đo UAT chỉ-đọc `em.hcm` 0 vi phạm, ledger + `qa_sync` ⇒ **`UI-SIDEBAR-001` Ready for Retest**
  (đã đọc lại CSV đúng dòng STT 131).
  Nghiệm thu: `docs/e8c-acceptance-matrix.md` (12/12 ý "Kết quả mong muốn").
- Chủ dự án chốt: ngôn ngữ **giữ trên header PC + mobile** (CMP-GH-001) **và** có nhóm trong avatar (huỷ chốt E8a gỡ
  dropdown topbar) · "Thông tin cửa hàng" → **"Hồ sơ cửa hàng"** ở menu + tiêu đề trang.
- Đã làm:
  - `wj_acct_menu_items` (mới, khung): thân menu avatar **dùng chung PC + mobile** — Thông tin tài khoản · Đổi mật khẩu ·
    Ngôn ngữ · neo `data-wj-anchor="acct_store_end"` · Đăng xuất. Nút avatar đủ aria.
  - `base`: một inherit chèn nhóm cửa hàng (mã/tên/chip vai trò · Đổi cửa hàng khi >1 · Hồ sơ cửa hàng sáng cả ở
    info-request); xoá `mheader_inherit.xml`. `_nav_mgr_fids` dời lên `app_layout` (1 lần/trang).
  - Sheet "Thêm": bỏ Hồ sơ cửa hàng + Tài khoản/Cài đặt; neo mới `msheet_end`; Công nợ + Báo cáo theo quyền như sidebar.
  - Chuông: `aria-controls`/`aria-expanded` + JS đồng bộ, Escape trả focus. Migration `19.0.58.0.0/pre-10`.
- Commit: `078dfeb feat(E8c)` đã push cùng E8a/E8b. Deploy UAT 25/09 09:06 (13 module đúng bản, `?v=1323`).
- Số đo: `wj_sidebar` +SN-10…14 **0 vi phạm × 4 vai trò** (avatar PC = mobile, sheet theo quyền, chuông, Đổi cửa hàng mở
  modal, bàn phím) · suite **801, 0 đỏ** (E8b 779, +22) · mutation **13/13** · DB trắng chỉ khung 225 tests, 0 failed, 1 error
  (nợ F6 có sẵn) · `wj_pagecontainer` 0 · `wj_button` 0 · `wj_listcard` 0 · `wj_filterbar` ĐẠT · `wj_nesting` 0 · `b4` 286/286 ·
  `check_layers` không thêm · `test_ownership` cross 0 · `nav_dump`: sidebar + bottom-nav 0 lệch, chỉ avatar/sheet đổi (chủ
  đích); mốc mới `docs/e8c-baseline/nav_em.json` · `wj_measure --diff` 0 mất record.
- Bài học: mutation làm module SAU không nạp được thì module TRƯỚC đã commit arch đột biến vào DB ⇒ mutation kế hỏng dây
  chuyền; `-u` lại bằng mã sạch. Harness nay `-u` mọi module trong `--test-tags`. · Menu mobile: `.dropdown .dropdown-menu`
  Vuexy (0,2,0) đè `min-width` ⇒ selector `.dropdown .wujia-mheader-menu`. · `<i>` trong `dropdown-item` có margin-right 7px
  Vuexy ⇒ chữ lệch với mục icon SVG.
- LIMIT: ngôn ngữ ở 2 chỗ (cố ý) · breadcrumb `/portal/franchise/<id>/profile` + thẻ Home "Thông tin cửa hàng" giữ tên ·
  báo BA: `/portal/info-request` không có lối vào UI.
- Bàn giao anh Thái: neo sheet mới `msheet_end`; dòng Khảo sát (`position="inside"`) không cần sửa, vẫn cuối.
- UAT: `wj_sidebar` SN-1…14 0 vi phạm · `wj_pagecontainer` 0 (Khảo sát đo qua `/vi/`) · `wj_button` 0 mới (6 dòng y hệt E6c) ·
  0 POST bị chặn · 0 lỗi JS. Staff/nhiều cửa hàng không đo trên UAT (mật khẩu khác seed, không reset).
- Phiên kế: theo `docs/next-session-clusters-F.md` (cụm E đã hết E4b→E8) — đề xuất cụm EmptyState hoặc F6 theo bảng §2.

## END-SPRINT 61/62 — chốt sổ cụm E + cổng F (25/09/2026 · Mac)
- Kết quả: ✅ xong. Phiên tài liệu, **0 file dưới `custom/`**, không deploy, không đụng sheet.
- Đã làm: chapter `docs/chapters/75-sprint61-cluster-e-components.tex` (Sprint 61 — cụm E: E1 · E9a · E9b · E2 · E3 ·
  E4 · E5 · E6 · E7 · E8 + phiên xen kẽ nhịp dọc / G2 / DOC-CTRL) và `76-sprint62-cluster-f-standardize.tex` (Sprint 62 —
  cổng F0 → ★FR-A3); `\include` sau ADR-027; PDF master **301 → 312 trang**, 0 lỗi LaTeX (trong PDF đánh số 74/75).
  Compact summary: dòng Cập nhật + §4 dòng 61/62 + §5 State mới, bỏ cảnh báo "§5 trễ". Skill `/wujia-start`: bỏ Step 2a
  (Issue List đã mở lại từ FR-A3), cụm F ghi "cổng đã qua, nhánh sau cổng xen kẽ Issue List".
- Commit: xem git log — `docs(multi): chapter cụm E + cụm F`
- Deploy: không.
- Số đo: `build-doc.sh` 312 trang · 0 `! ` trong log · 0 chữ Việt trong `\texttt` của 2 chapter mới (485 "Missing character"
  trong log là của chapter cũ, mono DejaVu thiếu dấu tiếng Việt — có từ trước).
- Còn treo: 7 issue mới STT 140–146 chưa phân cụm · EmptyState · nợ F6 (portal_base tự test + 1 error DB trắng).
- Phiên kế: **F6** — controller Đặt hàng mỏng (prompt `docs/next-session-clusters-F.md` §3 "Prompt F6"). Việc cần biết
  trước: gộp luôn nợ `portal_base` tự test một mình (nhãn `portal_suite` hoặc tự bỏ qua khi module chủ chưa cài).

## F6 — Controller Đặt hàng mỏng + nợ `portal_base` tự test · 25/09/2026 · Mac
- Kết quả: ✅ xong. Nghiệm thu: `docs/f6-acceptance-matrix.md` (11/11 ý).
- Issue List đầu phiên: 7 issue STT 140–146 `Ready for Dev`, chưa phân cụm, reconcile 0 code — chủ dự án chọn làm F6.
- Chủ dự án chốt: một savepoint cho cả khối gửi đơn (vá đơn mồ côi) · đúng 3 phần của prompt, báo số thật ·
  gộp nợ `portal_base`, làm sau phần sale.
- Đã làm:
  - Luật số lượng min/bước/max **một nguồn** `product._portal_qty_error` (`wujia_sale`) — thêm giỏ, sửa số lượng, dòng
    giỏ và constraint dòng đơn portal cùng gọi; mã lỗi + câu chữ giữ nguyên.
  - Giỏ về model `wujia.portal.cart(.line)`: thêm/tăng-giảm nguyên SQL cũ; **Gửi đơn** = `action_submit_order()` (khoá
    NOWAIT, khung giờ, dòng lỗi, huỷ báo giá cũ bằng write, tạo đơn, xoá giỏ trong **một savepoint**) → controller chỉ map
    mã lỗi sang redirect. Controller **1047 → 862 dòng (−185)**.
  - **Vá lỗi ẩn đơn mồ côi**: HEAD để lại đơn nháp khi tạo đơn lỗi sau khi đã insert (chứng minh bằng test đỏ trên HEAD).
  - Lưới test đặc tả 21 test (trước đó 0 test gọi cart/submit) + `scripts/qa/cart_race.py` đua 2 phiên thật.
  - Nợ `portal_base`: `tests/common.py` (`need`/`need_suite`/`find_view`) — test quét nhiều module tự skip khi module chủ
    chưa cài; `patch.object(…, create=True)` ở 2 file `test_fra3_layer_guard`.
- Commit: `feat(F6)` — xem git log (đã push `main`).
- Deploy: chưa. Lệnh khi được yêu cầu: `-u wujia_sale,wujia_portal_sale` (base/layout chỉ đổi test — không cần `-u`).
- Số đo: suite portal 15 module **822, 0 đỏ** (E8c 801, +21) · run đối chứng: test mới trên code HEAD chỉ đỏ test đơn mồ côi
  · `cart_race` HEAD = F6 (JSON y hệt, NOWAIT 5/5) · mutation **10/10** · HTML 4 route + fragment giống từng byte ·
  DB chỉ `portal_base` **39 failed + 82 error → 0/0** (274) · DB chỉ khung **225, 0 failed, 0 error** · `check_layers` không
  thêm · `test_ownership` cross 0.
- Lệch plan / quyết định mới: không dời `_cart_state` (chốt 2) nên −185 chứ không phải ~−240 · submit chưa có giỏ dựng giỏ
  ảo `new()` để giữ thứ tự `branch_locked` trước `CART_EMPTY` · constraint min = 0 vẫn chặn vượt max như HEAD.
- Bài học: server cũ phiên E4b2 còn nghe `127.0.0.1:8092` ⇒ HttpCase gửi nhầm server, 12 test đỏ giả (public/login).
  Kiểm port bằng `lsof` trước khi chạy; chưa tắt process đó (pid 23706, không phải của phiên này).
- Nợ để lại: 1 error có sẵn `test_wujia_supply_demand_report` (anh Thái `c64de50`) · mã `ORDER_TIME_CLOSED` lúc tạo đơn vẫn
  bắt theo chuỗi "khung giờ" (F7 thay) · bàn giao anh Thái 4 mục (xem matrix).
- Phiên kế: **F7** — pilot tách `order_window` khỏi `portal_sale` (luôn nhớ: `action_submit_order` gọi
  `_is_within_order_window(area_id=…)` và bắt ValidationError "khung giờ" — chỗ nối F7 phải thay) · hoặc phân cụm 7 issue
  STT 140–146 nếu chủ dự án ưu tiên Issue List.

## F7 — Pilot tách `order_window` → `wujia_order_window` · 25/09/2026 · Mac
- Kết quả: ✅ xong. Nghiệm thu: `docs/f7-acceptance-matrix.md` (10/10 ý + mutation 5/5).
- Chủ dự án chốt: module cũ = **vỏ rỗng** (depend mỗi `wujia_order_window`) → deploy, đo 0 xmlid → Uninstall trên Apps →
  FR-P xoá thư mục · **vá luôn nợ F6** (bắt lỗi khung giờ theo lớp).
- Đã làm:
  - Module nghiệp vụ mới `wujia_order_window` (L2, depend `wujia_sale`) nhận nguyên model khung giờ, cấu hình fallback,
    chặn đơn portal ngoài giờ, view/menu/ACL, bản dịch. `pre_init_hook` đổi chủ **toàn bộ** bản ghi của module cũ,
    cả `ir_model_constraint`/`ir_model_relation` (khuôn Khảo sát bỏ sót).
  - Lớp lỗi `OrderWindowClosed`; giỏ hàng bắt theo lớp → một lỗi khác có chữ "khung giờ" không còn bị báo nhầm
    "ngoài khung giờ".
  - 10 test cho khung giờ (trước đó 0 test tạo khung giờ) + 1 test portal_sale.
  - Công cụ `scripts/qa/split_snapshot.py` (chụp + diff có `--rename`) cho F8–F13.
  - Chapter 74 §Quy trình tách viết lại theo thực tế.
- Commit: `6b2938d` (đã push `main`).
- Deploy: UAT 25/09 (`-i wujia_order_window -u wujia_portal_order_window,wujia_portal_sale`). Đo chỉ-đọc qua RPC:
  3 version đúng · 36 xmlid + 6 ràng buộc thuộc module mới, vỏ 0 · 2 khung giờ, 3 tham số, 2 menu, 2 ACL, nhãn `vi_VN`
  giống trước deploy · form Settings + list/form khung giờ mở được · không module nào depend vỏ. **Chờ chủ dự án
  Uninstall vỏ trên Apps** rồi đo lần cuối.
- Số đo: 42 dòng đổi chủ (36 xmlid + 6 ràng buộc), **1 lệch có giải trình** (view Settings đổi `name` app/block), gỡ vỏ
  **0 lệch**, 0 ERROR · suite 15 module portal + `wujia_order_window` **833, 0 đỏ** (F6 822) · DB trắng chỉ module mới
  **10/10** · HTML 5 route HEAD ↔ F7 **giống từng byte**, bundle CSS/JS cùng md5 · mutation **5/5** · `check_layers`
  3 → 2 (R4 order_window hết; còn 2 R3 `wujia_mobile_portal_*` của anh Thái) · `test_ownership` cross 0.
- Lệch plan / quyết định mới: plan dự đoán "không đổi chủ constraint thì gỡ vỏ DROP CHECK" — đo mutation: **không DROP**,
  hậu quả thật là 2 dòng trùng + 6 dòng mồ côi. Hook chuyển TẤT CẢ thay vì danh sách tay (module cũ rút hết).
  Hook Khảo sát không còn được nối ở manifest (`ec6d380`).
- Nợ để lại: xoá thư mục vỏ ở FR-P (sau khi UAT gỡ) · bàn giao anh Thái 2 mục (hook Khảo sát không nối; 46 dòng
  ràng buộc Khảo sát vẫn ghi `wujia_franchise`) · 1 error có sẵn `test_wujia_supply_demand_report` (không chạy trong suite portal).
- Phiên kế: **★FR-P** — review pilot (prompt §3 "phiên review ★"): xác nhận vỏ đã Uninstall trên UAT (đo lại 36 xmlid +
  6 ràng buộc module mới), rà diff, xoá thư mục vỏ. Hoặc phân cụm 7 issue STT 140–146 nếu chủ dự án ưu tiên Issue List.

## ★FR-P — Review pilot F7 · 25–26/09/2026 · Mac
- Kết quả: ✅ xong — **ĐẠT, nhân quy trình sang F8 được** (điều kiện: chốt nợ `ref()` xmlid mobile Thái trước F8/F12).
  Review: `docs/f-review-FR-P.md`. Chủ dự án nhấn mạnh soi tuân thủ tầng nghiệp vụ–portal–mobile: **0 vi phạm** (bảng §3).
- Đã làm:
  - UAT: đo trước chỉ-đọc (vỏ 0 xmlid/0 cons/0 dependents) → chủ dự án duyệt → **gỡ vỏ qua RPC** `button_immediate_uninstall`
    (lời gọi ghi duy nhất, 6.4 s) → đo sau: 0 lệch với mốc F7 ngoài `state` vỏ.
  - Repo: xoá `custom/wujia_portal_order_window`; `check_layers` `DEPRECATED = set()` (34 module, 2 vi phạm R3 Thái);
    **`deploy.yml` còn `-i/-u` vỏ (F7 bỏ sót) → đổi**; bảng "tên cũ còn đâu" trong review.
  - **Dời `migrate_ownership` về L1** `wujia_core/tools/module_split.py` (chốt) + chặn module đích không tồn tại + helper
    **`imd_names`** suy xmlid theo model (model/field/selection/inherit/constraint/access/rule/view/action/srv/cron/tpl/seq).
  - Sửa test `test_split_ownership`: dòng module giả (DB trắng không có dòng vỏ → F7 chỉ Pass vì vỏ còn trên đĩa) + test
    helper phủ 36/36 xmlid F7. Comment L2 nhắc controller → bỏ.
  - `split_snapshot.py` +7 nhóm (inherit · sel · cron · tpl · srv · attach · rule theo module).
  - Thử tách MỘT PHẦN `info_request` trên `wujia_frp_trial`: helper 72/75 (3 dư = QWeb portal phải ở lại), 80 dòng đổi chủ,
    0 lệch thật, `number_next` giữ.
  - Chapter 74 §Quy trình tách 4 chỗ + số đo FR-P; build PDF.
- Commit: `9d2a606` — `review(FR-P): review pilot F7 đạt — gỡ vỏ order_window, hook đổi chủ về wujia_core` (đã push `main`; gồm cả mục F7 deploy sửa local từ phiên trước).
- Deploy: **UAT 26/09** (chủ dự án). Đo chỉ-đọc: `wujia_core 19.0.1.0.1`, 36 xmlid + 6 ràng buộc, vỏ `uninstalled`, khung giờ/tham số/Settings nguyên.
- Số đo: UAT 36 xmlid + 6 cons + 2 khung + 3 tham số + 2 menu + 2 ACL y hệt · `check_layers` 2 (Thái) · R6 0 · R7 2 (Thái) ·
  `-u` DB copy 0 ERROR · suite **834, 0 đỏ** (F7 833 + 1) · snapshot vs `f7r2/u.json` 0 lệch · DB trắng **11/11** (trước sửa
  1 error) · trial 80 đổi chủ / 0 lệch · mutation M3 trên helper đã dời **đỏ đúng**.
- Lệch plan / quyết định mới: `-u wujia_core --test-enable` kéo nạp test `wujia_franchise` (import file đã xoá) → 2 lượt
  chết 255; chỉ `-u wujia_order_window`. `ir_cron` Odoo 19 không có `name`/`model_id` (kế thừa `ir.actions.server`) — sửa cả
  helper lẫn snapshot. Hai Bash song song dùng chung cwd → đường dẫn tuyệt đối.
- Nợ để lại: (1) bàn giao Thái (chốt 26/09: phần mobile ngoài phạm vi, **không chặn F8**) — `wujia_mobile_portal_info_request`/
  `_exam` `ref()` xmlid `wujia_portal_<x>.*`, sau F8/F12 Thái đổi tiền tố; Dev báo trước khi deploy; (2) dư âm tên portal trong L2 (ICP `wujia_portal.*`, field
  `portal_order_time_*`, app/menu "Wujia Portal", xmlid view) — cần migration nếu đổi; (3) hook Khảo sát không nối + 46 cons
  `wujia_franchise` (bàn giao Thái); (4) `test_wujia_supply_demand_report` error có sẵn.
- Issue List (reconcile 7 issue STT 140–146): `grep custom/` + ledger = 0; `git log -S` chỉ bắt commit docs ⇒ **chưa có code**,
  chưa phân cụm. Toàn UI: 140 badge topbar PC · 141 store switcher mobile · 142 Home PC redesign (lớn) · 143+144 mật độ
  header/spacing `/portal/order` mobile · 145 bottom-nav 83px · 146 routing `/` → login (Suggestion).
- Phiên kế: đề xuất **Issue List cụm nhỏ trước** (143 + 144 + 145 cùng một chủ đề "mật độ mobile", 1 phiên; 140 + 141 phiên
  hai; 142 cần BA duyệt mockup; 146 hỏi BA) rồi **F8 `info_request`** — việc cần biết trước: dùng `imd_names` + liệt kê `extra` (menu), giữ 3 QWeb ở portal; báo Thái mục (1) trước deploy.
