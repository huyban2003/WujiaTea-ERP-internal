#!/usr/bin/env python3
"""task_sync — đọc hàng đợi tab "Tasks" + ghi ngược kết quả AI. Dev-only.

Nightly agent dùng:
    list_tasks()                         # lấy task "Sẵn sàng cho AI = Yes", chưa Done
    set_task(row, status=, question=, result=)   # ghi cột O/P/Q/R

CLI:
    python3 task_sync.py --list
    python3 task_sync.py --init-headers          # thêm nhãn cột H..R nếu tab còn thiếu
    python3 task_sync.py --row 2 --status "In Progress"
    python3 task_sync.py --row 2 --status Done-pushed --result "branch xyz, RC=0"
"""
import argparse
import datetime
import json
import os

import sheet_io as sio

TAB = "Tasks"
HERE = os.path.dirname(os.path.abspath(__file__))
# Sổ WIP: task dở dang xuyên đêm/xuyên session (nhánh + trạng thái + lý do). Gitignored.
WIP_STATE = os.path.join(HERE, "qa_nightly", "wip_state.json")
# Cột (0-based)
C_STT, C_GROUP, C_TITLE, C_DESC, C_LINK, C_PRIO, C_GNOTE = 0, 1, 2, 3, 4, 5, 6
C_TYPE, C_MODULE, C_ACCEPT, C_CONSTRAINT, C_DUE = 7, 8, 9, 10, 11
C_READY, C_ALLOWDEPLOY = 12, 13
C_AISTATUS, C_AIQUESTION, C_AIRESULT, C_AIDATE = 14, 15, 16, 17

HEADERS = {
    C_TYPE: "Loại task", C_MODULE: "Module/Phạm vi",
    C_ACCEPT: "Kết quả mong muốn (Acceptance)", C_CONSTRAINT: "Ràng buộc / Out-of-scope",
    C_DUE: "Ngày giao", C_READY: "Sẵn sàng cho AI?", C_ALLOWDEPLOY: "Cho phép tự deploy?",
    C_AISTATUS: "Trạng thái (AI)", C_AIQUESTION: "Câu hỏi Dev (AI)",
    C_AIRESULT: "Kết quả Dev (AI)", C_AIDATE: "Ngày AI xử lý",
}
DONE_AI = {"done-pushed", "need clarification"}


def _today():
    return datetime.datetime.now().strftime("%d/%m/%Y")


def _cell(row, i):
    return row[i].strip() if len(row) > i else ""


def list_tasks(ready_only=True):
    """Trả list dict task. ready_only -> chỉ M='Yes' và chưa Done-pushed/Need Clarification."""
    values = sio.read_values(TAB)
    out = []
    for i, row in enumerate(values[1:], start=2):  # bỏ header, row 1-based
        if not _cell(row, C_TITLE) and not _cell(row, C_DESC):
            continue
        t = {
            "row": i, "stt": _cell(row, C_STT), "group": _cell(row, C_GROUP),
            "title": _cell(row, C_TITLE), "desc": _cell(row, C_DESC),
            "link": _cell(row, C_LINK), "priority": _cell(row, C_PRIO),
            "type": _cell(row, C_TYPE), "module": _cell(row, C_MODULE),
            "acceptance": _cell(row, C_ACCEPT), "constraint": _cell(row, C_CONSTRAINT),
            "due": _cell(row, C_DUE), "ready": _cell(row, C_READY),
            "ai_status": _cell(row, C_AISTATUS),
        }
        if ready_only:
            if t["ready"].lower() != "yes":
                continue
            if t["ai_status"].lower() in DONE_AI:
                continue
        out.append(t)
    return out


def set_task(row, status=None, question=None, result=None, stamp_date=True):
    cm = {}
    if status is not None:
        cm[(row, C_AISTATUS)] = status
    if question is not None:
        cm[(row, C_AIQUESTION)] = question
    if result is not None:
        cm[(row, C_AIRESULT)] = result
    if stamp_date:
        cm[(row, C_AIDATE)] = _today()
    return sio.batch_set(TAB, cm)


def init_headers():
    values = sio.read_values(TAB)
    header = values[0] if values else []
    cm = {}
    for col, label in HEADERS.items():
        cur = header[col].strip() if len(header) > col else ""
        if not cur:
            cm[(1, col)] = label
    if cm:
        sio.batch_set(TAB, cm)
    return len(cm)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--all", action="store_true", help="với --list: cả task chưa Ready")
    ap.add_argument("--init-headers", action="store_true")
    ap.add_argument("--row", type=int)
    ap.add_argument("--status")
    ap.add_argument("--question")
    ap.add_argument("--result")
    a = ap.parse_args()

    if a.init_headers:
        n = init_headers()
        print(f"init-headers: thêm {n} nhãn cột H..R." if n else "Header H..R đã đủ.")
    elif a.list:
        for t in list_tasks(ready_only=not a.all):
            print(f"[row {t['row']}] STT {t['stt']} | {t['type'] or '?'} | "
                  f"{t['title']} | ready={t['ready']} | ai={t['ai_status'] or '-'}")
    elif a.row:
        n = set_task(a.row, status=a.status, question=a.question, result=a.result)
        print(f"Ghi {n} ô vào row {a.row}.")
    else:
        ap.print_help()
