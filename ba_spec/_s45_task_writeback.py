#!/usr/bin/env python3
"""Ghi kết quả Sprint 45 vào tab Tasks, row 7 (STT6 — controller Đăng ký thi).

Dev-only, chạy 1 lần. Chỉ đụng cột O/Q/R (Trạng thái AI / Kết quả AI / Ngày);
KHÔNG đụng cột A–N của BA. Status = Ready for Retest (KHÔNG Done — PC submit
defer sang S46, Done set ở session sau theo yêu cầu chủ dự án).
"""
import task_sync

ROW = 7  # STT6

STATUS = "Ready for Retest"

RESULT = (
    "[Sprint 45] Commit 4e4b2e5 (branch main, đã push origin). "
    "ĐÃ LÀM — wire Portal Đăng ký thi vào backend thật: "
    "phần XEM (danh sách phiếu / chi tiết / kết quả / khóa thi / lịch / khung giờ) "
    "đọc dữ liệu THẬT trên CẢ mobile lẫn PC, giới hạn theo cửa hàng đang chọn; "
    "phần TẠO PHIẾU (submit) wire THẬT trên MOBILE (chọn khóa→ngày→khung giờ→"
    "nhập nhân sự + ảnh→gửi phiếu thật, backend tự khóa sức chứa FOR-UPDATE). "
    "Gỡ hẳn 2 model legacy schedule/result + 3 route/template cũ + ACL/rule; "
    "migration 19.0.5.0.0 drop bảng legacy + dọn phiếu mồ côi. "
    "3 fix: vượt sức chứa báo lỗi thân thiện (không 500, không phiếu ma); "
    "ảnh hỏng chặn bằng validate (image_process); mọi query kèm franchise_id. "
    "VERIFY: -u wujia_portal_exam RC=0, 95 module, 0 ERROR/Traceback; smoke HTTP "
    "E2E login anh.owner (list/calendar/slots/submit→chi tiết 'Chờ kết quả'/vượt "
    "max/thiếu SĐT/vượt sức chứa/slot đầy/store khác→chặn/publish→Đạt-Không đạt/"
    "ảnh lưu+stream/từ chối→banner) đều đạt; 5 trang portal khác 200. "
    "GIỚI HẠN: PC submit defer sang Sprint 46 (PC vẫn XEM/duyệt dữ liệu thật) — "
    "task set Done SAU khi session PC-submit hoàn tất (prompt sẵn). "
    "DEPLOY UAT: -u wujia_portal_exam (có migration 19.0.5.0.0, KHÔNG -i) — chờ deploy tay."
)

if __name__ == "__main__":
    print(f"Ghi row {ROW}: status={STATUS!r}")
    print(f"result ({len(RESULT)} ký tự)...")
    n = task_sync.set_task(ROW, status=STATUS, result=RESULT)
    print(f"Đã ghi {n} ô vào row {ROW} (O/Q/R).")
