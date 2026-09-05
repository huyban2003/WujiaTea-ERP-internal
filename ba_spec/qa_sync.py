#!/usr/bin/env python3
"""qa_sync — set issue đã-làm-xong sang "Ready for Retest" đúng QA Operating Standard §6.

Nguồn: docs/qa-issue-ledger.yaml (issue mình đã fix+deploy) đối chiếu tab "5. Issue List".
Điền cột I(status)/P(build)/K(ghi chú)/R(Odoo Fit)/J(ngày)/O(owner) + thêm dòng "7. ISSUE HISTORY".

    python3 qa_sync.py                 # DRY-RUN (mặc định) — chỉ in diff
    python3 qa_sync.py --apply         # ghi thật
    python3 qa_sync.py --apply --only UI-01

An toàn: KHÔNG set Done; SKIP issue Need BA Confirm=Yes / Need Clarification; idempotent
(issue đã Ready for Retest/BA Retesting/Done -> bỏ qua).
"""
import argparse
import datetime
import os

import yaml

import sheet_io as sio

HERE = os.path.dirname(os.path.abspath(__file__))
LEDGER = os.path.normpath(os.path.join(HERE, "..", "..", "docs", "qa-issue-ledger.yaml"))

# Cột (0-based) trong "5. Issue List"
C_ID, C_STATUS, C_DATE, C_NOTE = 2, 8, 9, 10
C_NEEDCONFIRM, C_OWNER, C_BUILD, C_ODOOFIT = 13, 14, 15, 17

DONE_STATES = {"ready for retest", "ba retesting", "done"}
BLOCK_STATES = {"need clarification"}
NEW_STATUS = "Ready for Retest"
NEW_OWNER = "BA/Tester"


def _today():
    return datetime.datetime.now().strftime("%d/%m/%Y")


def _load_ledger():
    with open(LEDGER, encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}
    return {k: v for k, v in data.items() if isinstance(v, dict)}


def _note(e):
    return (f"FIX: {e.get('fix','')} | IMPACT: {e.get('impact','')} | "
            f"RETEST: {e.get('retest','')} | LIMIT: {e.get('limit','Không có')}")


def _build(e):
    # build_override: dùng khi code đã push nhưng CHƯA lên UAT — không được ghi
    # "UAT | ..." vì BA sẽ retest nhầm build cũ.
    if e.get("build_override"):
        return e["build_override"]
    return (f"UAT | {e.get('deployed_date','')} | commit: {e.get('commit','')} "
            f"(Sprint {e.get('sprint','')}) | URL: {e.get('url','')}")


def run(apply=False, only=None, force=False):
    ledger = _load_ledger()
    if only:
        ledger = {k: v for k, v in ledger.items() if k == only}
        if not ledger:
            print(f"[!] {only} không có trong ledger."); return
    values = sio.read_values("Issue List")

    marked, skip_idem, skip_block, notfound = [], [], [], []
    hist_rows = []
    cell_map = {}

    for vid, e in ledger.items():
        row = sio.find_row(values, C_ID, vid)
        if not row:
            notfound.append(vid); continue
        cur = values[row - 1]
        def g(i):
            return cur[i].strip() if len(cur) > i else ""
        status, needc = g(C_STATUS), g(C_NEEDCONFIRM)
        if status.lower() in DONE_STATES:
            skip_idem.append((vid, status)); continue
        if not force and (needc.lower() == "yes" or status.lower() in BLOCK_STATES):
            skip_block.append((vid, status, needc)); continue

        # -> handoff Ready for Retest
        marked.append((vid, status))
        cell_map[(row, C_STATUS)] = NEW_STATUS
        cell_map[(row, C_BUILD)] = _build(e)
        cell_map[(row, C_NOTE)] = _note(e)
        cell_map[(row, C_ODOOFIT)] = e.get("odoo_fit", "Need Dev Confirm")
        cell_map[(row, C_DATE)] = _today()
        cell_map[(row, C_OWNER)] = NEW_OWNER
        # dòng ISSUE HISTORY (QA §7): Ngày|ID|cũ|mới|Owner|Người|Lý do|Build|Evidence
        hist_rows.append([_today(), vid, status, NEW_STATUS, NEW_OWNER,
                          "Dev (AI qa_sync)", _note(e), _build(e), ""])

    _report(marked, skip_idem, skip_block, notfound, apply)

    if apply and cell_map:
        n = sio.batch_set("Issue List", cell_map)
        try:
            for h in hist_rows:
                sio.append_row("ISSUE HISTORY", h)
            hist_msg = f"{len(hist_rows)} dòng History"
        except Exception as ex:
            hist_msg = f"(History bỏ qua: {ex} — tạo tab '7. ISSUE HISTORY' rồi chạy lại)"
        print(f"\n[APPLIED] ghi {n} ô + {hist_msg}.")
    elif apply:
        print("\n[APPLIED] không có issue nào cần đổi (idempotent).")
    else:
        print("\n[DRY-RUN] chưa ghi gì. Thêm --apply để ghi thật.")


def _report(marked, idem, block, notfound, apply):
    print(f"=== qa_sync {'APPLY' if apply else 'DRY-RUN'} — {_today()} ===")
    print(f"\n-> Set Ready for Retest ({len(marked)}):")
    for vid, old in marked:
        print(f"   • {vid:<20} {old} -> {NEW_STATUS}")
    print(f"\n-> Skip idempotent, đã handoff/đóng ({len(idem)}):")
    for vid, st in idem:
        print(f"   • {vid:<20} {st}")
    print(f"\n-> Skip chờ BA (Need Confirm=Yes / Need Clarification) ({len(block)}):")
    for vid, st, nc in block:
        print(f"   • {vid:<20} status={st} needConfirm={nc}")
    if notfound:
        print(f"\n-> Không thấy trong sheet ({len(notfound)}): {', '.join(notfound)}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="ghi thật (mặc định dry-run)")
    ap.add_argument("--only", metavar="ISSUE_ID", help="chỉ xử lý 1 issue")
    ap.add_argument("--force", action="store_true", help="bỏ chặn Need Confirm=Yes/Need Clarification (KHÔNG đụng cột N)")
    a = ap.parse_args()
    run(apply=a.apply, only=a.only, force=a.force)
