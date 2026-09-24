#!/usr/bin/env python3
"""Sinh chương "Bản đồ đường dẫn" + kiểm ĐỘ PHỦ của tài liệu đặc tả controller.

    python3 scripts/qa/controller_spec_tex.py                 # in độ phủ
    python3 scripts/qa/controller_spec_tex.py --write         # ghi ch02-ban-do-route.tex

Nguồn: docs/controller-spec/routes_deep.json (máy trích) + route-labels.json (người viết
nhãn tiếng Việt + chương mô tả). Đường dẫn chưa có nhãn bị in ra để không sót màn nào.
"""
import argparse
import collections
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
SPEC = ROOT / 'docs' / 'controller-spec'

# Thứ tự chương trong tài liệu; module nào chưa gán rơi vào "chưa xếp".
CHAPTERS = [
    ('3', 'Đặt hàng', ['wujia_portal_sale']),
    ('4', 'Khung portal + Trang chủ', ['wujia_portal_layout', 'wujia_portal_base',
                                       'wujia_portal_order_window']),
    ('5', 'Lịch sử mua · Giao hàng · Báo cáo', ['wujia_portal_purchase_history',
                                                'wujia_portal_delivery',
                                                'wujia_portal_report']),
    ('6', 'Công nợ · Đổi trả', ['wujia_portal_debt', 'wujia_portal_return']),
    ('7', 'Hỗ trợ · Yêu cầu thông tin · Kiến thức · Thông báo',
     ['wujia_portal_support', 'wujia_portal_info_request',
      'wujia_portal_knowledge', 'wujia_portal_notification']),
    ('8', 'Đăng ký thi', ['wujia_portal_exam']),
    ('9', 'Khảo sát cửa hàng · Metabase', ['wujia_franchise_inspection',
                                           'wujia_portal_inspection',
                                           'wujia_metabase_connector']),
]
MOD_CHAPTER = {m: (num, name) for num, name, mods in CHAPTERS for m in mods}

TYPE_LABEL = {'http': 'Trang', 'json': 'Gọi ngầm'}


def esc(text):
    """Thoát ký tự LaTeX cho văn bản thường (không dùng cho \\rt{})."""
    for a, b in (('\\', r'\textbackslash{}'), ('&', r'\&'), ('%', r'\%'),
                 ('$', r'\$'), ('#', r'\#'), ('_', r'\_'), ('{', r'\{'),
                 ('}', r'\}'), ('~', r'\textasciitilde{}'), ('^', r'\textasciicircum{}')):
        text = text.replace(a, b)
    return text


def load():
    deep = json.loads((SPEC / 'routes_deep.json').read_text(encoding='utf-8'))
    lab_path = SPEC / 'route-labels.json'
    labels = json.loads(lab_path.read_text(encoding='utf-8')) if lab_path.exists() else {}
    return deep, labels


def rows(deep, labels):
    """Một dòng = một ĐƯỜNG DẪN. Cùng đường dẫn khai 2 hàm (GET xem form, POST gửi
    form) là hợp lệ — gộp lại một dòng, không tính là trùng."""
    merged = {}
    for r in deep['routes']:
        for p in r['paths']:
            row = merged.setdefault(p, {
                'path': p, 'module': r['module'], 'type': r['type'],
                'handlers': [], 'methods': set(), 'label': labels.get(p, ''),
            })
            row['handlers'].append(f"{r['module']}.{r['method']}")
            for m in (r['methods'] or ['GET']):
                row['methods'].add(m)
    return list(merged.values())


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--write', action='store_true')
    args = ap.parse_args()

    deep, labels = load()
    data = rows(deep, labels)
    dup = [d['path'] for d in data if len(d['handlers']) > 2]
    missing = [d['path'] for d in data if not d['label']]

    twin = [d['path'] for d in data if len(d['handlers']) == 2]
    print(f"đường dẫn: {len(data)} · có nhãn: {len(data) - len(missing)} · "
          f"chưa có nhãn: {len(missing)} · 1 đường dẫn 2 hàm (GET+POST): {len(twin)} "
          f"{twin} · bất thường: {len(dup)}")
    if dup:
        print('TRÙNG:', dup)
    if missing:
        per = collections.Counter(d['module'] for d in data if not d['label'])
        for m, n in per.most_common():
            print(f'  chưa nhãn {n:3d}  {m}')

    if not args.write:
        return 0

    lines = [r'\chapter{Bản đồ đường dẫn}', '',
             f"Portal hiện có \\textbf{{{len(data)} đường dẫn}} trong "
             f"\\textbf{{{len({d['module'] for d in data})} mô-đun}}. Bảng này là mục lục tra "
             r'cứu: mỗi đường dẫn nằm ở chương nào trong tài liệu. Cột \emph{Kiểu} phân biệt '
             r'\emph{Trang} (người dùng nhìn thấy, gõ được trên thanh địa chỉ) với '
             r'\emph{Gọi ngầm} (trình duyệt gọi khi bấm nút, không phải màn riêng).', '']

    by_ch = collections.defaultdict(list)
    for d in data:
        num, name = MOD_CHAPTER.get(d['module'], ('--', 'Chưa xếp chương'))
        by_ch[(num, name)].append(d)

    for (num, name), items in sorted(by_ch.items()):
        lines += [f'\\section{{Chương {num} --- {esc(name)}}}', r'\footnotesize',
                  r'\begin{longtable}{L{7.0cm}L{1.8cm}L{6.0cm}}',
                  r'\rowcolor{hdrbg}\textbf{Đường dẫn} & \textbf{Kiểu} & \textbf{Làm gì}\\ \midrule',
                  r'\endfirsthead',
                  r'\rowcolor{hdrbg}\textbf{Đường dẫn} & \textbf{Kiểu} & \textbf{Làm gì}\\ \midrule',
                  r'\endhead']
        for d in sorted(items, key=lambda x: x['path']):
            lines.append(f"\\rt{{{d['path']}}} & {TYPE_LABEL.get(d['type'], d['type'])} & "
                         f"{esc(d['label']) or '---'}\\\\")
        lines += [r'\end{longtable}', r'\normalsize', '']

    out = SPEC / 'ch02-ban-do-route.tex'
    out.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(f'→ {out}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
