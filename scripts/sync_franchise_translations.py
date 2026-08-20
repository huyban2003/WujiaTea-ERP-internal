#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script đồng bộ hoàn hảo bản dịch Odoo 19:
1. Trích xuất chính xác cấu trúc POT từ Odoo (bao gồm đầy đủ comment #: model_terms:ir.ui.view,arch_db:...)
2. Điền bản dịch từ wujia_franchise_export.csv vào vi_VN.po và zh_CN.po
3. Tự động nạp trực tiếp vào Odoo DB qua lệnh 'odoo-bin i18n import'
"""

import os
import sys
import csv
import re
import subprocess

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(BASE_DIR, 'custom', 'wujia_franchise', 'data', 'wujia_franchise_export.csv')
I18N_DIR = os.path.join(BASE_DIR, 'custom', 'wujia_franchise', 'i18n')
VI_PO_PATH = os.path.join(I18N_DIR, 'vi_VN.po')
ZH_PO_PATH = os.path.join(I18N_DIR, 'zh_CN.po')
ODOO_BIN = os.path.join(BASE_DIR, 'odoo19', 'odoo-bin')
CONFIG_PATH = os.path.join(BASE_DIR, 'config', 'odoo.conf')
PYTHON = "/home/dev/miniconda3/envs/odoo19/bin/python3.10"
DB_NAME = "wujia_tea_19"

def export_pot():
    pot_path = "/tmp/wujia_franchise.pot"
    cmd = [
        PYTHON, ODOO_BIN, "i18n", "export",
        "-c", CONFIG_PATH,
        "-d", DB_NAME,
        "-l", "pot",
        "-o", pot_path,
        "wujia_franchise"
    ]
    print("1. Đang trích xuất cấu trúc giao diện và terms từ Odoo...")
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"Cảnh báo export POT: {res.stderr}")
    return pot_path

def load_csv_mappings():
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
    return trans_map

def generate_po_from_pot(pot_path, out_po_path, trans_map, lang_col):
    with open(pot_path, 'r', encoding='utf-8') as f:
        content = f.read()

    blocks = content.split('\n\n')
    out_blocks = []

    for block in blocks:
        if not block.strip():
            continue
        if block.startswith('# Translation of Odoo Server.'):
            out_blocks.append(block)
            continue

        # Trích xuất msgid
        raw_msgid = re.findall(r'msgid (?:".*?"\n?)+', block)
        if not raw_msgid:
            out_blocks.append(block)
            continue

        full_msgid = "".join(re.findall(r'"(.*?)"', raw_msgid[0])).replace('\\n', '\n').replace('\\"', '"')
        
        # Tìm bản dịch
        translated_val = ""
        if full_msgid in trans_map:
            translated_val = trans_map[full_msgid].get(lang_col, '')
        elif full_msgid.strip() in trans_map:
            translated_val = trans_map[full_msgid.strip()].get(lang_col, '')

        # Nếu không có trong CSV nhưng là tiếng Việt (cho vi_VN)
        if not translated_val and lang_col == 'VN':
            translated_val = full_msgid

        if translated_val:
            escaped_val = translated_val.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n"\n"')
            # Thay thế msgstr "" bằng giá trị dịch
            new_block = re.sub(r'msgstr (?:".*?"\n?)+', f'msgstr "{escaped_val}"\n', block)
            out_blocks.append(new_block.strip())
        else:
            out_blocks.append(block)

    with open(out_po_path, 'w', encoding='utf-8') as f:
        f.write('\n\n'.join(out_blocks) + '\n')
    print(f"2. Đã tạo file {os.path.basename(out_po_path)} hoàn chỉnh với đầy đủ metadata Odoo.")

def import_po_to_odoo(po_path, lang_code):
    cmd = [
        PYTHON, ODOO_BIN, "i18n", "import",
        "-c", CONFIG_PATH,
        "-d", DB_NAME,
        "-l", lang_code,
        "-w",
        po_path
    ]
    print(f"3. Đang nạp trực tiếp {os.path.basename(po_path)} ({lang_code}) vào database...")
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode == 0:
        print(f"   -> Nạp {lang_code} thành công!")
    else:
        print(f"   -> Cảnh báo import {lang_code}: {res.stderr}")

def main():
    pot_path = export_pot()
    if not os.path.exists(pot_path):
        print("Lỗi: Không thể xuất file POT.")
        sys.exit(1)

    trans_map = load_csv_mappings()
    print(f"Đã nạp {len(trans_map)} ánh xạ bản dịch từ CSV.")

    generate_po_from_pot(pot_path, VI_PO_PATH, trans_map, 'VN')
    generate_po_from_pot(pot_path, ZH_PO_PATH, trans_map, 'CN')

    import_po_to_odoo(VI_PO_PATH, "vi_VN")
    import_po_to_odoo(ZH_PO_PATH, "zh_CN")

    print("\n Hoàn tất đồng bộ toàn bộ giao diện và DB Odoo!")

if __name__ == '__main__':
    main()
