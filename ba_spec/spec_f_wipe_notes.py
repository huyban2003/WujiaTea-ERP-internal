#!/usr/bin/env python3
"""GỠ toàn bộ ghi chú Dev ở cột L phần F — trả sheet BA về đúng phạm vi "chỉ đổi field".

Lý do: bản ghi chú đầu quy kết BA mâu thuẫn về targeting, nhưng BA nhất quán (Tasks dòng 6,
Out-of-scope: "Không thêm cơ chế target theo cửa hàng, khu vực, role hoặc user"); chỗ lệch là
source. Kèm 2 lỗi trích dẫn (POR-024 ở dòng 30 chứ không phải 31; Feature Status đang TRỐNG,
không phải "đã nghiệm thu"). Chủ dự án yêu cầu gỡ hết, chỉ giữ phần đổi tên field.

    python3 spec_f_wipe_notes.py [--apply]
"""
import sys

import sheet_io

TAB = "1. Model/ Field"
F_FROM, F_TO = 731, 895
C_NOTE = 11


def main():
    v = sheet_io.read_values(TAB)
    assert v[F_FROM - 1][0].strip().startswith("F. Quản lý thông báo"), "Row 731 sai -> DỪNG"
    assert v[897 - 1][0].strip().startswith("G."), "Row 897 sai -> DỪNG"

    targets = {}
    for r in range(F_FROM, F_TO + 1):
        row = v[r - 1] if r - 1 < len(v) else []
        cur = row[C_NOTE] if C_NOTE < len(row) else ""
        if cur.strip():
            targets[(r, C_NOTE)] = ""
            print(f"xoá L{r}: {cur[:80]}…")
    print(f"\n{len(targets)} ô sẽ bị xoá trắng.")
    if "--apply" not in sys.argv:
        print("(dry-run — chạy lại với --apply để ghi)")
        return
    print(f"\n✅ đã xoá {sheet_io.batch_set(TAB, targets)} ô.")


if __name__ == "__main__":
    main()
