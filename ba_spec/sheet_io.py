#!/usr/bin/env python3
"""Helper đọc/ghi Google Sheet "Internal ERP Master Plan_Update" — dev-only.

- ĐỌC: qua CSV công khai (gviz) — sheet share "anyone view" nên không cần auth.
- GHI: POST tới Apps Script Web App (cổng "Wujia Sheet Bridge", chạy as editor) — tránh
  toàn bộ OAuth/Google-Cloud (Google đã chặn scope Sheets trên client mặc định).

Cấu hình cổng ghi ở `sheet_endpoint.json` (gitignored): {"webapp_url": "...", "secret": "..."}.
Row index 1-based, col index 0-based (giữ tương thích qa_sync/task_sync).
"""
import csv
import io
import json
import os
import string
import urllib.parse
import urllib.request

SPREADSHEET_ID = "1HRiRLAZ9FlErRTLvwMaGhsOlYNPJHdf5AEMPvdLkQNE"
HERE = os.path.dirname(os.path.abspath(__file__))
ENDPOINT_FILE = os.path.join(HERE, "sheet_endpoint.json")

# gid biết trước (đọc nhanh, chắc ăn); tab khác đọc theo tên.
# Lấy gid: tải `export?format=xlsx` rồi openpyxl `wb.sheetnames`, hoặc `htmlview | grep gid`.
# ⚠️ TÊN TAB: đừng lấy tên từ `export?format=xlsx` — Excel CẤM ký tự `/` trong tên sheet nên
# Google sanitize khi export: tab thật `1. Model/ Field` ra thành `1. Model Field`, gửi tên đó
# cho bridge sẽ lỗi "Không tìm thấy tab". Lấy tên thật bằng `_post({'action':'ping','sheet':...})`
# (bridge trả sheet.getName()) — nó có fallback substring nên "1. Model" là đủ để dò.
KNOWN_GID = {
    # Phải có CẢ tên thật có số thứ tự: thiếu key là rơi xuống gviz (tôn trọng filter
    # ẩn Done) -> find_row trả row của VIEW, bridge ghi theo row TUYỆT ĐỐI -> đè nhầm
    # issue khác. Đã xảy ra 04/09/2026 với "5. Issue List".
    "issue list": "335593633",
    "5. issue list": "335593633",
    "tasks": "1936593712",
    "1. model/ field": "2041118658",
    "1. model field": "2041118658",  # alias tên đã bị xlsx sanitize
    "3. controller": "643561224",
}

# ⚠️ GOTCHA row-offset: endpoint gviz/tq TÔN TRỌNG filter/hidden-row của sheet →
# nếu BA đang bật filter (vd ẩn "Done") thì gviz trả THIẾU dòng, find_row đánh số
# theo view lọc, còn bridge ghi theo ROW TUYỆT ĐỐI → ghi NHẦM dòng. export?format=csv
# BỎ QUA filter → row khớp tuyệt đối. Vì batch_set ghi theo row tuyệt đối nên với tab
# có gid ta ĐỌC bằng export để find_row luôn ra row thật.


def col_letter(idx0):
    """0 -> 'A', 25 -> 'Z', 26 -> 'AA'."""
    s = ""
    idx0 += 1
    while idx0:
        idx0, r = divmod(idx0 - 1, 26)
        s = string.ascii_uppercase[r] + s
    return s


# ----------------------------- ĐỌC (CSV public) -----------------------------
def read_values(title, timeout=25):
    """Trả list[list[str]] toàn tab. Hàng ngắn không pad.

    Tab có gid biết trước -> export?format=csv (BỎ QUA filter, row TUYỆT ĐỐI khớp
    bridge ghi). Tab chỉ biết tên -> gviz/tq?sheet= (chấp nhận, không dùng cho ghi
    theo row). Xem GOTCHA row-offset ở đầu file.
    """
    sid = SPREADSHEET_ID
    gid = KNOWN_GID.get(title.strip().lower())
    if gid:
        url = f"https://docs.google.com/spreadsheets/d/{sid}/export?format=csv&gid={gid}"
    else:
        q = urllib.parse.urlencode({"tqx": "out:csv", "sheet": title.strip()})
        url = f"https://docs.google.com/spreadsheets/d/{sid}/gviz/tq?{q}"
    req = urllib.request.Request(url, headers={"User-Agent": "wujia-sheet-io"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        text = resp.read().decode("utf-8", "replace")
    return list(csv.reader(io.StringIO(text)))


def find_row(values, col0, needle):
    """Trả row 1-based đầu tiên có values[r][col0] == needle (trim). 0 nếu không thấy."""
    needle = needle.strip()
    for i, row in enumerate(values):
        if len(row) > col0 and row[col0].strip() == needle:
            return i + 1
    return 0


# ----------------------------- GHI (Apps Script) ----------------------------
def _endpoint():
    if not os.path.exists(ENDPOINT_FILE):
        raise RuntimeError(
            f"Thiếu {ENDPOINT_FILE}. Deploy Apps Script bridge (docs/03) rồi lưu webapp_url."
        )
    with open(ENDPOINT_FILE) as fh:
        cfg = json.load(fh)
    if not cfg.get("webapp_url"):
        raise RuntimeError("sheet_endpoint.json chưa có webapp_url — dán URL sau khi deploy bridge.")
    return cfg["webapp_url"], cfg["secret"]


def _post(payload, timeout=45):
    url, secret = _endpoint()
    payload = dict(payload, secret=secret)
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:  # follow 302 -> googleusercontent
        out = json.loads(resp.read().decode("utf-8", "replace"))
    if out.get("error"):
        raise RuntimeError(f"Bridge error: {out['error']}")
    return out


def batch_set(title, cell_map):
    """cell_map = {(row1, col0): value}. Ghi qua bridge. Trả số ô đã ghi."""
    if not cell_map:
        return 0
    cells = [{"row": r, "col": c + 1, "value": v} for (r, c), v in cell_map.items()]
    _post({"action": "setCells", "sheet": title, "cells": cells})
    return len(cells)


def append_row(title, values_list):
    """Thêm 1 hàng vào cuối tab qua bridge."""
    _post({"action": "appendRow", "sheet": title, "values": list(values_list)})


def ping():
    return _post({"action": "ping", "sheet": "Tasks"})


if __name__ == "__main__":
    import sys
    if "--ping" in sys.argv:
        print("ping:", ping())
    else:
        v = read_values("Issue List")
        print(f"Issue List (CSV): {len(v)} hàng; header[:3] =", v[0][:3])
