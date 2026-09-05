#!/usr/bin/env python3
"""qa_done — set issue ĐÃ verify PASS sang "Done" trên "5. Issue List".

Khác qa_sync (chỉ "Ready for Retest"): dùng khi CHỦ DỰ ÁN duyệt cho Dev đóng Done
(override QA §6) với issue đã tự verify PASS bằng headless Chromium computed-style.

    python3 qa_done.py            # DRY-RUN — in diff
    python3 qa_done.py --apply    # ghi thật (status Done + note + History)

Mỗi issue kèm evidence đo thật (viewport + giá trị computed) trong EVIDENCE dưới đây.
"""
import argparse
import datetime

import sheet_io as sio

# Cột (0-based) trong "5. Issue List" — khớp qa_sync.py
C_ID, C_STATUS, C_DATE, C_NOTE, C_OWNER = 2, 8, 9, 10, 14

# issue_id -> câu evidence (đo bằng scripts/ba_spec/qa_visual_check.py trên UAT ?v=1156)
EVIDENCE = {
    "UI-02":            "PC language pill computed 118×40 border-box (đúng Figma). BA-Actual 118×46 khớp build cũ trước deploy.",
    "UI-04":            "Mobile header 3 action circle computed 38×38, tâm x≈248/302/356 (đúng Blank Shell). BA-Actual 44×44 khớp build cũ.",
    "UI-MOB-HOME-002":  "Home mobile mọi section-title computed 18px/line-height 24px/700 đồng nhất. BA-Actual lh 21.6 khớp build cũ.",
    "WJ-ORD-006":       "Banner khung giờ mobile trong giờ = xanh rgb(22,163,74) đồng bộ PC. BA-Actual mobile đỏ khớp build cũ.",
    "WJ-ORD-021":       "Card mobile qty=0 chỉ hiện icon giỏ (add visible, stepper ẩn) — state exclusive đúng v2.5. BA-Actual 'Thêm+stepper' khớp build cũ.",
}
DONE = "Done"
OWNER = "BA/Tester"


def _today():
    return datetime.datetime.now().strftime("%d/%m/%Y")


def run(apply=False, only=None):
    ids = [only] if only else list(EVIDENCE)
    values = sio.read_values("Issue List")
    cell_map, hist_rows, marked, notfound, skip = {}, [], [], [], []

    for vid in ids:
        row = sio.find_row(values, C_ID, vid)
        if not row:
            notfound.append(vid); continue
        cur = values[row - 1]
        old = cur[C_STATUS].strip() if len(cur) > C_STATUS else ""
        if old.lower() == "done":
            skip.append((vid, old)); continue
        note = f"VERIFIED PASS (headless Chromium): {EVIDENCE[vid]}"
        cell_map[(row, C_STATUS)] = DONE
        cell_map[(row, C_DATE)] = _today()
        cell_map[(row, C_NOTE)] = note
        cell_map[(row, C_OWNER)] = OWNER
        hist_rows.append([_today(), vid, old, DONE, OWNER,
                          "Dev (AI qa_done)", note, "UAT ?v=1156", ""])
        marked.append((vid, old))

    print(f"=== qa_done {'APPLY' if apply else 'DRY-RUN'} — {_today()} ===")
    for vid, old in marked:
        print(f"   • {vid:<18} {old or '(trống)'} -> {DONE}")
    for vid, old in skip:
        print(f"   ~ {vid:<18} đã Done (bỏ qua)")
    if notfound:
        print(f"   [!] không thấy trong sheet: {', '.join(notfound)}")

    if apply and cell_map:
        n = sio.batch_set("Issue List", cell_map)
        try:
            for h in hist_rows:
                sio.append_row("ISSUE HISTORY", h)
            hist_msg = f"{len(hist_rows)} dòng History"
        except Exception as ex:
            hist_msg = f"(History bỏ qua: {ex})"
        print(f"\n[APPLIED] ghi {n} ô + {hist_msg}.")
    elif not apply:
        print("\n[DRY-RUN] chưa ghi. Thêm --apply để ghi thật.")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--only", metavar="ISSUE_ID")
    run(**vars(ap.parse_args()))
