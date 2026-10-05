#!/usr/bin/env python3
"""Gom file filestore Odoo của các DB Wujia trên máy này thành 1 file .tar (khử trùng theo sha1).

Chạy trên máy CÒN filestore (máy Linux/Windows qua RDP…), chỉ ĐỌC — không sửa/xoá gì:

    python3 scripts/dev/filestore_pack.py                     # tự tìm thư mục filestore
    python3 scripts/dev/filestore_pack.py /duong/dan/filestore # chỉ định thêm chỗ tìm
    python3 scripts/dev/filestore_pack.py --db-glob '*'        # lấy mọi DB, không chỉ wujia*

Ra 1 file `wujia_filestore_pool_<ngày>.tar` ở thư mục home, dạng `xx/<sha1>`. Odoo đặt tên file theo
sha1 nội dung ⇒ file trùng tên là cùng nội dung, DB copy dùng chung được. Mang file .tar về máy Mac
rồi chạy `filestore_restore.py`.
"""
import argparse
import datetime
import fnmatch
import os
import pathlib
import re
import sys
import tarfile

FNAME = re.compile(r'^[0-9a-f]{2}$')
SHA1 = re.compile(r'^[0-9a-f]{40}$')
SKIP_DIRS = {'.git', 'node_modules', '__pycache__', 'sessions', 'addons', 'odoo', 'odoo19', 'odoo20'}


def default_roots():
    home = pathlib.Path.home()
    roots = [home / 'odoo-dev', home / '.local/share/Odoo', pathlib.Path('/var/lib/odoo'),
             pathlib.Path('/opt/odoo')]
    if os.environ.get('LOCALAPPDATA'):
        roots.append(pathlib.Path(os.environ['LOCALAPPDATA']) / 'OpenERP S.A.' / 'Odoo')
    return roots


def find_filestores(roots, max_depth=6):
    seen = set()
    for root in roots:
        root = pathlib.Path(root).expanduser()
        if not root.is_dir():
            continue
        if root.name == 'filestore':
            seen.add(root.resolve())
            continue
        base = len(root.parts)
        for dirpath, dirnames, _files in os.walk(root):
            path = pathlib.Path(dirpath)
            if 'filestore' in dirnames:
                seen.add((path / 'filestore').resolve())
                dirnames.remove('filestore')
            if len(path.parts) - base >= max_depth:
                dirnames[:] = []
            else:
                dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith('.')]
    return sorted(seen)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('roots', nargs='*', help='thư mục tìm filestore (mặc định: ~/odoo-dev, data dir Odoo)')
    ap.add_argument('--db-glob', default='wujia*', help="tên DB cần lấy (mặc định 'wujia*')")
    ap.add_argument('--out', help='file .tar đầu ra (mặc định ~/wujia_filestore_pool_<ngày>.tar)')
    args = ap.parse_args()

    stores = find_filestores(args.roots or default_roots())
    if not stores:
        sys.exit('Không tìm thấy thư mục filestore nào — truyền đường dẫn vào: filestore_pack.py <dir>')
    out = pathlib.Path(args.out or pathlib.Path.home() / (
        'wujia_filestore_pool_%s.tar' % datetime.date.today().strftime('%Y%m%d'))).expanduser()
    if out.exists():
        sys.exit('%s đã tồn tại — đổi tên/di chuyển file cũ hoặc dùng --out' % out)

    names, total = set(), 0
    with tarfile.open(out, 'w') as tar:
        for store in stores:
            for db in sorted(p for p in store.iterdir() if p.is_dir()):
                if not fnmatch.fnmatch(db.name, args.db_glob):
                    continue
                count = new = 0
                for sub in db.iterdir():
                    if not (sub.is_dir() and FNAME.match(sub.name)):
                        continue
                    for f in sub.iterdir():
                        if not (f.is_file() and SHA1.match(f.name)):
                            continue
                        count += 1
                        rel = '%s/%s' % (sub.name, f.name)
                        if rel in names:
                            continue
                        tar.add(str(f), arcname=rel, recursive=False)
                        names.add(rel)
                        new += 1
                        total += f.stat().st_size
                print('%-60s %7d file  (+%d mới)' % (db, count, new))
    print('\nXong: %s — %d file, %.1f MB' % (out, len(names), total / 1e6))
    print('Mang file này về Mac rồi chạy: python3 scripts/dev/filestore_restore.py <file.tar>')


if __name__ == '__main__':
    main()
