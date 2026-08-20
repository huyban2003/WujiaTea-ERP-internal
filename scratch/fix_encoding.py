import os

script_path = "/home/dev/WujiaTea-ERP-internal/scripts/sync_franchise_translations.py"
with open(script_path, "r", encoding="utf-8") as f:
    code = f.read()
code = code.replace("open(CSV_PATH, 'r', encoding='utf-8')", "open(CSV_PATH, 'r', encoding='utf-8-sig')")
with open(script_path, "w", encoding="utf-8") as f:
    f.write(code)

csv_path = "/home/dev/WujiaTea-ERP-internal/custom/wujia_franchise/data/wujia_franchise_export.csv"
with open(csv_path, "r", encoding="utf-8-sig") as f:
    csv_content = f.read()
with open(csv_path, "w", encoding="utf-8") as f:
    f.write(csv_content)

print("Fixed encoding in CSV and script!")
