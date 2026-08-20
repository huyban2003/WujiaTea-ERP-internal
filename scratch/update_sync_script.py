path = "/home/dev/WujiaTea-ERP-internal/scripts/sync_franchise_translations.py"
with open(path, "r", encoding="utf-8") as f:
    code = f.read()

# Modify load_csv_mappings to return (trans_map, row_count)
old_load = """def load_csv_mappings():
    trans_map = {}
    if not os.path.exists(CSV_PATH):
        print(f"Lỗi: Không tìm thấy CSV tại {CSV_PATH}")
        return trans_map

    with open(CSV_PATH, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            key = (row.get('key') or '').strip()
            vn = (row.get('VN') or '').strip()
            cn = (row.get('CN') or '').strip()
            if key:
                trans_map[key] = {'VN': vn, 'CN': cn}
            if vn:
                trans_map[vn] = {'VN': vn, 'CN': cn}
    return trans_map"""

new_load = """def load_csv_mappings():
    trans_map = {}
    row_count = 0
    if not os.path.exists(CSV_PATH):
        print(f"Lỗi: Không tìm thấy CSV tại {CSV_PATH}")
        return trans_map, 0

    with open(CSV_PATH, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            key = (row.get('key') or '').strip()
            vn = (row.get('VN') or '').strip()
            cn = (row.get('CN') or '').strip()
            if not key and not vn:
                continue
            row_count += 1
            if key:
                trans_map[key] = {'VN': vn, 'CN': cn}
            if vn:
                trans_map[vn] = {'VN': vn, 'CN': cn}
    return trans_map, row_count"""

code = code.replace(old_load, new_load)
code = code.replace("trans_map = load_csv_mappings()\n    print(f\"Đã nạp {len(trans_map)} ánh xạ bản dịch từ CSV.\")", "trans_map, row_count = load_csv_mappings()\n    print(f\"Đã nạp {row_count} dòng bản dịch từ CSV.\")")

with open(path, "w", encoding="utf-8") as f:
    f.write(code)

print("Updated sync_franchise_translations.py successfully!")
