#!/usr/bin/env python3
"""W5a — soát bản dịch vi_VN cho các nhãn do sprint 44 sinh ra.

Tiêu chí ĐÚNG là "mọi msgid do sprint sinh ra phải có msgstr", KHÔNG phải "mọi field
model wujia% phải có vi_VN": query thô `model like 'wujia%'` trả 494 dòng rỗng, nhưng đó
là field core kế thừa (message_follower_ids, write_uid...) và nhãn vốn đã tiếng Anh từ
trước sprint (menu Franchise Management...). Cả hai đều ngoài phạm vi sprint này.

Soát 3 bảng jsonb:
  ir_model_fields.field_description
  ir_model_fields_selection.name      <- quan trọng nhất: W1 toàn sửa nhãn selection
  ir_ui_menu.name

Chạy: python3 verify_i18n.py
"""
import json
import sys
from pathlib import Path

import psycopg2

HERE = Path(__file__).parent
DSN = dict(host="127.0.0.1", port=5432, user="odoo19", password="1",
           dbname="wujia_tea_19")

# Tập chuỗi EN do sprint sinh ra = giá trị của vi_en_map.json + 4 nhãn tách ở W1.
W1_NEW = {
    "Rejected": "Từ chối",
    "Archived": "Lưu trữ",
    "Lock portal": "Khóa portal",
    "Assign vehicle": "Gán xe",
    "Rejection reason": "Lý do từ chối",
}
vi_en = json.loads((HERE / "vi_en_map.json").read_text(encoding="utf-8"))
SPRINT_EN = {en.replace("&amp;", "&") for en in vi_en.values()} | set(W1_NEW)

# Chỉ soát dòng do module Wujia SỞ HỮU. Chuỗi như "Draft"/"Cancelled"/"Configuration"
# cũng nằm trong tập EN của sprint nhưng thuộc model core (account/stock/sale) — bản dịch
# vi_VN của core là việc của Odoo, không phải của sprint này.
MODULES = (
    "wujia_core", "wujia_delivery", "wujia_fleet", "wujia_franchise", "wujia_sale",
    "wujia_portal_exam", "wujia_portal_notification", "wujia_portal_return",
    "wujia_portal_info_request", "wujia_portal_knowledge", "wujia_portal_support",
    "wujia_portal_order_window", "wujia_portal_debt", "wujia_portal_purchase_history",
    "wujia_portal_base",
)

TABLES = [
    ("ir_model_fields", "ir.model.fields", "field_description",
     "t.model || '.' || t.name"),
    ("ir_model_fields_selection", "ir.model.fields.selection", "name",
     "(select f.model || '.' || f.name from ir_model_fields f"
     "  where f.id = t.field_id) || ':' || t.value"),
    ("ir_ui_menu", "ir.ui.menu", "name", "d.module || '.' || d.name"),
]
OWNED = ("join ir_model_data d on d.model = %s and d.res_id = t.id "
         "and d.module = any(%s)")

conn = psycopg2.connect(**DSN)
cur = conn.cursor()

missing = []
for table, imd_model, col, ident in TABLES:
    cur.execute(
        f"select {ident}, t.{col}->>'en_US', t.{col}->>'vi_VN' "
        f"from {table} t {OWNED} where t.{col}->>'en_US' is not null",
        (imd_model, list(MODULES)),
    )
    for who, en, vi in cur.fetchall():
        if en not in SPRINT_EN:
            continue
        if not (vi or "").strip():
            missing.append((table, who, en))

print("=== W5a — nhãn sprint 44 thiếu bản dịch vi_VN ===")
for table, who, en in missing:
    print(f"MISSING {table:28s} {who:60s} {en!r}")
print(f"TỔNG thiếu = {len(missing)}  (kỳ vọng 0)")

# Kiểm riêng 5 nhãn tách mới của W1: phải ra đúng chữ Việt đã chốt.
print("\n=== W5a — 5 nhãn tách mới của W1 ===")
bad = 0
for en, want in W1_NEW.items():
    rows = []
    for table, imd_model, col, ident in TABLES:
        cur.execute(
            f"select {ident}, t.{col}->>'vi_VN' from {table} t {OWNED} "
            f"where t.{col}->>'en_US' = %s", (imd_model, list(MODULES), en)
        )
        rows += [(table, w, v) for w, v in cur.fetchall()]
    if not rows:
        print(f"(none)  {en!r} — không xuất hiện trong 3 bảng (nhãn nằm ở view/button)")
        continue
    for table, who, vi in rows:
        ok = vi == want
        bad += 0 if ok else 1
        print(f"{'OK  ' if ok else 'FAIL'} {table:28s} {who:60s} {en!r} -> {vi!r}")
print(f"FAIL = {bad}")

cur.close()
conn.close()
sys.exit(1 if (missing or bad) else 0)
