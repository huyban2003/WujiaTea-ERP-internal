#!/usr/bin/env python3
"""issue_queue — nhìn tab "5. Issue List" theo TRẠNG THÁI để biết mỗi ngày cần làm gì.

Hai công dụng:
  1. Daily status view (`--status`, mặc định): gom issue theo Trạng thái + Ngày cập
     nhật → ai đang giữ việc (Dev / BA / Done). Trả lời "hôm nay cần làm gì".
  2. Dev work queue (`--dev`): liệt kê issue Dev CÓ THỂ nhận ngay =
     Trạng thái ∈ {Ready for Dev, Retest Failed} + Owner=Dev + Need BA Confirm≠Yes.
     Đây là NGUỒN VIỆC bổ sung cho agent (hybrid: tab Tasks trước, hết thì lấy đây).

Chỉ ĐỌC (CSV công khai) — không ghi gì, không cần cổng bridge.

    python3 issue_queue.py            # cả status view + dev queue
    python3 issue_queue.py --status   # chỉ bảng trạng thái
    python3 issue_queue.py --dev      # chỉ hàng đợi Dev (cho agent nhặt việc)
    python3 issue_queue.py --json     # xuất JSON (agent parse) — kèm --dev hoặc --status
"""
import argparse
import json

import sheet_io as sio

TAB = "Issue List"
# Cột (0-based) — khớp qa_sync.py / cấu trúc "5. Issue List"
C_STT, C_PHANHE, C_ID, C_KHUVUC, C_VANDE = 0, 1, 2, 3, 4
C_STATUS, C_DATE, C_NOTE = 8, 9, 10
C_LOAI, C_SEVERITY, C_NEEDCONFIRM, C_OWNER = 11, 12, 13, 14
C_BUILD, C_FEATURE, C_ODOOFIT = 15, 16, 17

# Nhóm trạng thái theo "ai đang giữ việc"
DEV_STATES = {"ready for dev", "dev in progress", "retest failed"}
BA_STATES = {"ready for retest", "ba retesting", "need clarification", "new"}
DONE_STATES = {"done"}

# Trạng thái mà Dev CÓ THỂ bắt tay code ngay (agent nhặt việc)
ACTIONABLE_DEV = {"ready for dev", "retest failed"}


def _g(row, i):
    return row[i].strip() if len(row) > i else ""


def _load():
    values = sio.read_values(TAB)
    rows = []
    for r in values[1:]:  # bỏ header
        if not _g(r, C_ID):
            continue
        rows.append({
            "stt": _g(r, C_STT), "phanhe": _g(r, C_PHANHE), "id": _g(r, C_ID),
            "khuvuc": _g(r, C_KHUVUC), "vande": _g(r, C_VANDE),
            "status": _g(r, C_STATUS), "date": _g(r, C_DATE),
            "severity": _g(r, C_SEVERITY), "loai": _g(r, C_LOAI),
            "need_confirm": _g(r, C_NEEDCONFIRM), "owner": _g(r, C_OWNER),
            "odoo_fit": _g(r, C_ODOOFIT), "feature": _g(r, C_FEATURE),
        })
    return rows


def dev_queue(rows):
    """Issue Dev có thể nhận ngay — nguồn việc hybrid cho agent."""
    out = []
    for it in rows:
        if it["status"].lower() not in ACTIONABLE_DEV:
            continue
        if it["need_confirm"].lower() == "yes":   # còn chờ BA chốt spec → không nhặt
            continue
        # KHÔNG lọc theo Current Owner: BA điền cột này không nhất quán (25/08 cả 11
        # issue Ready for Dev đều để "BA/Tester" ⇒ hàng đợi báo 0 việc). Trạng thái
        # mới là nguồn sự thật; Owner lệch chỉ in cảnh báo.
        out.append(it)
    return out


def print_status(rows):
    dev, ba, done, other = [], [], [], []
    for it in rows:
        s = it["status"].lower()
        (dev if s in DEV_STATES else ba if s in BA_STATES
         else done if s in DONE_STATES else other).append(it)

    def block(title, items):
        print(f"\n== {title} ({len(items)}) ==")
        for it in sorted(items, key=lambda x: (x["status"], x["id"])):
            flag = " ⚠BAconfirm" if it["need_confirm"].lower() == "yes" else ""
            print(f"  {it['id']:<22} {it['status']:<18} "
                  f"[{it['severity'] or '-'}] cập nhật {it['date'] or '-'}{flag}")

    print(f"=== Issue List — tổng {len(rows)} issue ===")
    block("🔧 DEV đang giữ việc (làm/verify/handoff)", dev)
    block("👀 BA/Tester đang giữ việc (retest/clarify)", ba)
    block("✅ Done", done)
    if other:
        block("❓ Trạng thái khác", other)


def print_dev_queue(items):
    print(f"\n=== Hàng đợi Dev có thể nhận ngay ({len(items)}) ===")
    if not items:
        print("  (trống — không có Ready for Dev / Retest Failed nào, Need BA Confirm=No)")
        return
    for it in items:
        owner = it["owner"] or "-"
        flag = "" if owner.lower() in ("dev", "-") else f"  ⚠ Owner={owner} (sheet lệch)"
        print(f"\n[{it['id']}] STT {it['stt']} | {it['status']} | "
              f"Severity {it['severity'] or '-'} | fit={it['odoo_fit'] or '-'}{flag}")
        print(f"    {it['vande'][:150]}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--status", action="store_true", help="chỉ bảng trạng thái")
    ap.add_argument("--dev", action="store_true", help="chỉ hàng đợi Dev (nguồn việc agent)")
    ap.add_argument("--json", action="store_true", help="xuất JSON thay vì text")
    a = ap.parse_args()

    rows = _load()
    show_status = a.status or not a.dev
    show_dev = a.dev or not a.status

    if a.json:
        payload = {}
        if show_status:
            payload["all"] = rows
        if show_dev:
            payload["dev_queue"] = dev_queue(rows)
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        if show_status:
            print_status(rows)
        if show_dev:
            print_dev_queue(dev_queue(rows))
