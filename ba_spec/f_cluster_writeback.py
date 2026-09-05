#!/usr/bin/env python3
"""Cập nhật lại Dev-handoff cho 3 issue cụm F đã ở "Ready for Retest" từ đợt trước.

qa_sync.py cố ý idempotent: issue đang Ready for Retest thì bỏ qua. Nhưng BA đã
retest và báo lại 3 issue này (đo 25/07), lần này Dev sửa tiếp nên cột ghi chú /
build phải được viết lại, nếu không BA vẫn đọc thông tin bàn giao của tháng 7.

KHÔNG đổi trạng thái (vẫn là Ready for Retest), KHÔNG đụng cột Need BA Confirm.

    python3 f_cluster_writeback.py           # DRY-RUN
    python3 f_cluster_writeback.py --apply
"""
import argparse

import qa_sync as qs
import sheet_io as sio

ISSUES = ["WJ-ORD-003", "WJ-ORD-002", "WJ-ORD-020"]


def main(apply_):
    ledger = qs._load_ledger()
    values = sio.read_values("Issue List")
    cell_map, hist = {}, []

    for vid in ISSUES:
        e = ledger.get(vid)
        if not e:
            print(f"[!] {vid} không có trong ledger"); continue
        row = sio.find_row(values, qs.C_ID, vid)
        if not row:
            print(f"[!] {vid} không thấy trong sheet"); continue
        cur = values[row - 1]
        status = cur[qs.C_STATUS].strip() if len(cur) > qs.C_STATUS else ""
        needc = cur[qs.C_NEEDCONFIRM].strip() if len(cur) > qs.C_NEEDCONFIRM else ""
        if needc.lower() == "yes":
            print(f"[skip] {vid} — Need BA Confirm = Yes"); continue

        cell_map[(row, qs.C_STATUS)] = qs.NEW_STATUS
        cell_map[(row, qs.C_BUILD)] = qs._build(e)
        cell_map[(row, qs.C_NOTE)] = qs._note(e)
        cell_map[(row, qs.C_ODOOFIT)] = e.get("odoo_fit", "Need Dev Confirm")
        cell_map[(row, qs.C_DATE)] = qs._today()
        cell_map[(row, qs.C_OWNER)] = qs.NEW_OWNER
        hist.append([qs._today(), vid, status, qs.NEW_STATUS, qs.NEW_OWNER,
                     "Dev (AI cụm F)", qs._note(e), qs._build(e), ""])
        print(f"-> {vid} (dòng {row}): {status} -> {qs.NEW_STATUS}, viết lại cột K/P/R")

    if not apply_:
        print(f"\n[DRY-RUN] sẽ ghi {len(cell_map)} ô + {len(hist)} dòng History. Thêm --apply.")
        return
    n = sio.batch_set("Issue List", cell_map)
    for h in hist:
        sio.append_row("ISSUE HISTORY", h)
    print(f"\n[APPLIED] ghi {n} ô + {len(hist)} dòng History.")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    main(ap.parse_args().apply)
