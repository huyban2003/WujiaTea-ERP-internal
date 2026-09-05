#!/usr/bin/env python3
"""Sửa lại 3 ghi chú cột L về franchise_ids — bản đầu quy kết SAI cho BA.

Phát hiện 31/07 sau khi soi tab Tasks: task "Xây dựng controller Notification MVP cho Portal"
(Tasks row 6, giao 25/07, TRẠNG THÁI CÒN TRỐNG = chưa làm) có Out-of-scope ghi rõ "Không thêm
cơ chế target theo cửa hàng, khu vực, role hoặc user" -> BA NHẤT QUÁN, không mâu thuẫn.
franchise_ids mới là chỗ source lệch (thêm từ Sprint 32, trước khi có đặc tả này).
Đồng thời sửa 2 lỗi trích dẫn: POR-024 ở row 30 (không phải 31), và Feature Status đang TRỐNG
(chưa nghiệm thu) — bản đầu ghi "đã nghiệm thu".

    python3 spec_f_fix_targeting.py [--apply]
"""
import sys

import sheet_io

TAB = "1. Model/ Field"
C_NOTE = 11

NOTES = {
742: '❓CẦN LÀM RÕ — Dev hỏi, KHÔNG phải BA ghi sai. Đặc tả của BA đang nhất quán ở hướng không '
     'target: dòng này, dòng 816, dòng 872, và phần "Ràng buộc / Out-of-scope" của task "Xây dựng '
     'controller Notification MVP cho Portal" (tab Tasks, dòng 6, giao 25/07/2026) cũng ghi rõ '
     '"Không thêm cơ chế target theo cửa hàng, khu vực, role hoặc user". Vấn đề nằm ở SOURCE: model '
     'wujia.notification hiện CÓ field franchise_ids ("Cửa hàng nhận", Many2many), thêm từ Sprint 32 '
     '— tức có TRƯỚC khi BA ra đặc tả này — và ir.rule của portal đang lọc bằng field đó. Lưu ý: để '
     'trống franchise_ids nghĩa là gửi toàn hệ thống, nên hành vi mặc định hiện tại vẫn đúng "global" '
     'như dòng này mô tả. Chỗ duy nhất còn mập mờ: ô H12 (CT-011) và H42 (CT-041) của tab '
     '"3. Controller" ghi "đúng đối tượng (nhận)". Nhờ BA xác nhận giúp cách hiểu câu đó: (a) chỉ là '
     '"đúng user có membership hợp lệ tại cửa hàng hiện tại" — thì đặc tả không mâu thuẫn, Dev sẽ '
     'đóng băng franchise_ids (luôn để trống) hoặc gỡ hẳn; hay (b) thật sự là gửi theo cửa hàng — thì '
     'nhờ BA bổ sung franchise_ids vào đặc tả. Dev làm theo, không tự quyết.',

816: 'Xem ghi chú dòng 742. Source KHÔNG có target_store_ids / target_role / target_user_ids như '
     'dòng này cấm. Chỉ có franchise_ids ("Cửa hàng nhận") thêm từ Sprint 32, trước khi có đặc tả '
     'này — Dev đang chờ BA xác nhận để đóng băng (luôn để trống) hoặc gỡ hẳn.',

872: '❓CẦN LÀM RÕ — Dev hỏi. Câu này đúng với ý đồ MVP của BA, nhưng hiện KHÔNG khớp code: model '
     'wujia.notification đang có field franchise_ids ("Cửa hàng nhận", Many2many) từ Sprint 32 và '
     'ir.rule của portal lọc bằng field đó. Đây là chỗ SOURCE lệch đặc tả, không phải đặc tả sai — '
     'Dev ghi ra để BA nắm chứ không đề nghị BA sửa câu này. Xem ghi chú dòng 742: nhờ BA xác nhận để '
     'Dev đóng băng field (luôn để trống = gửi toàn hệ thống, đúng như dòng này mô tả) hay gỡ hẳn.',
}


def main():
    v = sheet_io.read_values(TAB)
    assert v[730][0].strip().startswith("F. Quản lý thông báo"), "Row 731 sai -> DỪNG"
    for r in NOTES:
        cur = v[r - 1][C_NOTE]
        assert cur.strip().startswith("❗XUNG ĐỘT") or cur.strip().startswith("Xem ghi chú"), \
            f"L{r} không phải ghi chú cũ của Dev ({cur[:40]!r}) -> DỪNG"
        print(f"L{r}\n   cũ : {cur[:120]}…\n   mới: {NOTES[r][:120]}…\n")
    if "--apply" not in sys.argv:
        print("(dry-run — chạy lại với --apply để ghi)")
        return
    n = sheet_io.batch_set(TAB, {(r, C_NOTE): t for r, t in NOTES.items()})
    print(f"✅ đã ghi đè {n} ô.")


if __name__ == "__main__":
    main()
