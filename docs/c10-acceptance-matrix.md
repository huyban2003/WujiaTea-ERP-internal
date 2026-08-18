# C10 — bảng đối chiếu acceptance (WJ-EXAM-007 · WJ-LANG-001)

**Ngày đo:** 2026-08-18 · **Môi trường:** DB copy cô lập `wujia_tea_c10`, port 8056
(KHÔNG đụng `wujia_tea_19`/8019) · **Harness:** Playwright + chromium (env `odoo`),
1920×1080 và 391×844 · **Kết quả:** **33/33 Pass (100%)**.

Build: `-u wujia_portal_exam,wujia_portal_layout,wujia_sale --stop-after-init` → RC=0, 0 ERROR.
Test: 20 test mới (`wujia_exam_c10`, `wujia_lang_c10`) + 82 test hồi quy 4 module khác — 0 failed / 0 error.

---

## WJ-EXAM-007 — giới hạn người / phiếu

Ngữ cảnh dữ liệu đo: khóa `C10 QA giới hạn 2` (max 2) · khóa `Khóa thi pha chế cơ bản` (max 4)
· một ca thi của khóa 4 được cấu hình riêng **max 3** (để kiểm thứ tự ưu tiên).

| Yêu cầu (cột "Kết quả mong muốn") | Đo được | Pass |
|---|---|---|
| Mọi vị trí hiển thị **cùng** giới hạn được cấu hình | Hướng dẫn `Mỗi phiếu được đăng ký tối đa 2 người.` + chip `0 / 2` (khóa max 2) | ✅ |
| Không còn số 4 hard-code | Hướng dẫn đọc từ `pc_summary['max_hint']`; đổi sang khóa max 4 → `…tối đa 4 người.` + chip `0 / 4` | ✅ |
| Giá trị theo cấu hình backend, không theo component | Chọn ca thi max 3 của khóa max 4 → hướng dẫn `…tối đa 3 người.` + chip `0 / 3` (ca thắng khóa) | ✅ |
| Khi đạt giới hạn, nút thêm người bị chặn rõ ràng | `saveParticipant()` chặn khi `realRows() >= maxPer`, thông báo `Tối đa N người mỗi phiếu.` dùng chung `maxPer` | ✅ |
| Server kiểm tra lại cùng rule khi gửi phiếu | `portal.py` `_max_per_reg(session)` + `wujia.exam.registration._check_participant_bounds` — test `test_server_rejects_over_limit` chặn 3 người / khóa max 2 | ✅ |
| Trang không lỗi | 0 JS pageerror, 0 tràn ngang | ✅ |

**Nguồn giá trị (trả lời ghi chú BA "chưa xác định 2 hay 4"):** nguồn duy nhất là
`wujia.exam.session.max_participants_per_registration`; ca để trống thì lấy
`wujia.exam.course.max_participants_per_registration`. Trên UAT khóa BA test
(`QA-MANUAL-HCM-20260803`) đang cấu hình **2** — nên "0 / 2" mới là số đúng, câu "tối đa 4
người" là chuỗi chép tay (default của field), nay đã gỡ.

## WJ-LANG-001 — bộ chọn ngôn ngữ

| Yêu cầu (GIVEN/WHEN/THEN của BA) | Đo được | Pass |
|---|---|---|
| Bộ chọn hiển thị Thai cùng English và Vietnam — PC | Navbar PC: 3 mục `en_US` / `th_TH` / `vi_VN` | ✅ |
| … mobile | Header mobile 391×844: đúng 3 mục | ✅ |
| … màn đăng nhập | `/portal/login`: 3 mục, pill đổi thành dropdown thật | ✅ |
| Chọn Thai → session/context đổi sang Thai | Đổi ở màn login → pill ra `ภาษาไทย` + cờ `flag-icon-th` ngay | ✅ |
| Giữ ngôn ngữ sau đăng nhập | Chọn Thai ở màn login rồi đăng nhập → `/portal/profile` vẫn cờ `th` | ✅ |
| Giữ khi chuyển trang | Sang `/portal/order` vẫn cờ `th` | ✅ |
| Cờ / tên ngôn ngữ hiện tại hiển thị đúng | Nút navbar: `Tiếng Việt` + `flag-icon-vn` khi đang vi | ✅ |
| Tên ngôn ngữ đúng | Nhãn bản địa `English (US)` · `Tiếng Việt` · `ภาษาไทย` | ✅ |
| English và Vietnam vẫn chuyển đổi bình thường | en↔vi đổi được, `res.users.lang` cập nhật (test `test_logged_in_switch_writes_user_lang`) | ✅ |
| Danh sách lấy từ cấu hình, **không hard-code 2 lựa chọn** | Bật thêm `zh_TW` trong Settings → bộ chọn tự có **4 mục**, nhãn `繁體中文 (台灣)`, cờ `flag-icon-tw`, **0 dòng code sửa** (đã tắt lại sau khi đo) | ✅ |
| Ngôn ngữ chưa bật không xuất hiện | `ja_JP` không có trong danh sách (test) | ✅ |
| `<html lang>` theo ngôn ngữ đang dùng | `th-TH` khi chọn Thai (trước đây ghim `en`/`vi`) | ✅ |

**Hồi quy:** `/portal/order`, `/portal/delivery`, `/portal/knowledge` × 2 viewport — 200,
0 lỗi JS, 0 tràn ngang (6/6).

---

## LIMIT (ghi rõ, không tự xử)

1. **Nội dung portal chưa dịch sang tiếng Thái.** Cụm này chỉ sửa *bộ chọn* + cơ chế đổi;
   chuỗi tiếng Việt trong QWeb portal vốn là source, BA import `.po` mới ra tiếng Thái.
2. **3 seam pin nhãn tiếng Việt ở controller** (trạng thái nhượng quyền · độ ưu tiên popup
   chuông · loại yêu cầu — tồn từ S44) vẫn ra tiếng Việt khi chọn Thai. Cố ý không gỡ
   (gỡ sẽ làm rò tiếng Anh ngược lại), chờ BA chốt từ vựng.
3. **Cờ suy từ hậu tố mã ngôn ngữ** (`vi_VN`→`vn`, `zh_TW`→`tw`). Bộ `flag-icon` trong repo
   có đủ cờ cho các ngôn ngữ dự kiến; ngôn ngữ không có mã quốc gia (vd `sr@latin`) sẽ
   không có cờ — chưa phát sinh, mở issue riêng nếu BA cần.
