#!/usr/bin/env python3
"""Bung bảng dịch (khoá đã chuẩn hoá khoảng trắng) ra vi_en_map.json khoá theo CHUỖI GỐC.

Kiểm 3 điều kiện trước khi ghi, thiếu 1 là dừng:
  1. Mọi chuỗi gốc trích được đều có bản dịch  -> không sót
  2. Không khoá thừa trong bảng dịch           -> không rác
  3. Giá trị English DUY NHẤT                  -> .po không bị 2 nhãn chung 1 msgid
"""
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
from translations import T  # noqa: E402


def norm(s):
    return re.sub(r"\s+", " ", s).strip()


raw = subprocess.run(
    [sys.executable, str(HERE / "i18n_tool.py"), "extract"],
    capture_output=True, text=True, check=True,
).stdout
originals = list(json.loads(raw).keys())

TN = {norm(k): v for k, v in T.items()}
if len(TN) != len(T):
    print(f"!! bảng dịch có khoá trùng sau chuẩn hoá: {len(T)} -> {len(TN)}")
    sys.exit(2)

missing = sorted({o for o in originals if norm(o) not in TN})
if missing:
    print(f"!! {len(missing)} chuỗi chưa có bản dịch:")
    for s in missing[:60]:
        print(f"   {s!r}")
    sys.exit(2)

used = {norm(o) for o in originals}
extra = sorted(set(TN) - used)
if extra:
    print(f"!! {len(extra)} khoá thừa (không khớp chuỗi nào trong source):")
    for s in extra[:60]:
        print(f"   {s!r}")
    sys.exit(2)

dup = {}
for k, v in TN.items():
    dup.setdefault(v, []).append(k)
clash = {v: ks for v, ks in dup.items() if len(ks) > 1}
if clash:
    print(f"!! {len(clash)} bản dịch English bị trùng (msgid đụng nhau trong .po):")
    for v, ks in sorted(clash.items()):
        print(f"   {v!r}  <- {ks}")
    sys.exit(2)

out = {o: TN[norm(o)] for o in originals}
(HERE / "vi_en_map.json").write_text(
    json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"OK — {len(out)} chuỗi gốc, {len(set(out.values()))} bản dịch duy nhất -> vi_en_map.json")
