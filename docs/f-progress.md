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

