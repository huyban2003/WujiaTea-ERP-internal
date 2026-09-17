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
- Commit: chưa commit
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

