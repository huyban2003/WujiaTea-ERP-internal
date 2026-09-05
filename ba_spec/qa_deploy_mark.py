#!/usr/bin/env python3
"""Đánh dấu issue ĐÃ DEPLOY UAT trên tab `5. Issue List` (cột P Build/Deploy).

Vì sao cần: `qa_sync.py` cố ý **idempotent** — issue đã ở `Ready for Retest` thì lần chạy
sau bỏ qua, không ghi đè. Nhưng cột Build/Deploy lúc đó còn ghi "Chờ deploy UAT", và sau khi
chủ dự án cài lên UAT thì dòng đó **sai sự thật** ⇒ BA không biết đã retest được hay chưa.
Script này chỉ đổi đúng phần đầu cột P + cột "Ngày cập nhật", KHÔNG đụng trạng thái/owner.

    python3 qa_deploy_mark.py WJ-PORTAL-UI-002 UAT-BH-001 ...          # dry-run
    python3 qa_deploy_mark.py --apply --note "..." WJ-PORTAL-UI-002 ...
"""
import argparse
import datetime
import sys

import sheet_io as sio

TAB = "Issue List"
C_ID, C_STATUS, C_DATE, C_OWNER, C_BUILD = 2, 8, 9, 14, 15
OLD_PREFIX = "Chờ deploy UAT"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ids", nargs="+")
    ap.add_argument("--apply", action="store_true", help="ghi thật (mặc định dry-run)")
    ap.add_argument("--date", default=None, help="ngày deploy dd/mm/yyyy (mặc định hôm nay)")
    ap.add_argument("--note", default="", help="ghi thêm vào cuối cột P (số đo sau deploy)")
    a = ap.parse_args()

    day = a.date or datetime.date.today().strftime("%d/%m/%Y")
    head = f"ĐÃ DEPLOY UAT {day} — sẵn sàng retest"

    values = sio.read_values(TAB)
    cell_map, hist, skipped = {}, [], []
    for vid in a.ids:
        row = sio.find_row(values, C_ID, vid)
        if not row:
            skipped.append((vid, "không thấy trong sheet")); continue
        cur = values[row - 1]
        build = cur[C_BUILD] if len(cur) > C_BUILD else ""
        if head.split("—")[0].strip() in build:
            skipped.append((vid, "đã đánh dấu deploy rồi")); continue
        if build.startswith(OLD_PREFIX):
            new = head + build[len(OLD_PREFIX):]
        else:
            new = head + " | " + build
        if a.note:
            new += " | " + a.note
        cell_map[(row, C_BUILD)] = new
        cell_map[(row, C_DATE)] = day
        hist.append([day, vid, cur[C_STATUS], cur[C_STATUS],
                     cur[C_OWNER] if len(cur) > C_OWNER else "BA/Tester",
                     "Dev (AI qa_deploy_mark)",
                     f"Đã cài lên UAT ngày {day}, đo lại chỉ-đọc trên chính máy chủ. "
                     + (a.note or ""), new, ""])
        print(f"[{vid}] dòng {row}\n    → {new[:160]}")

    for vid, why in skipped:
        print(f"[bỏ qua] {vid}: {why}")
    if not cell_map:
        print("\nKhông có gì để ghi.")
        return 0
    if not a.apply:
        print(f"\n[DRY-RUN] sẽ ghi {len(cell_map)} ô + {len(hist)} dòng History. Thêm --apply.")
        return 0
    n = sio.batch_set(TAB, cell_map)
    try:
        for h in hist:
            sio.append_row("ISSUE HISTORY", h)
        hm = f"{len(hist)} dòng History"
    except Exception as ex:  # noqa: BLE001
        hm = f"(History bỏ qua: {ex})"
    print(f"\n[APPLIED] ghi {n} ô + {hm}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
