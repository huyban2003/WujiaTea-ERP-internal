#!/usr/bin/env python3
"""Trả file filestore cho các DB local từ 1 file pool .tar (do `filestore_pack.py` tạo).

    python3 scripts/dev/filestore_restore.py ~/wujia_filestore_pool_20261004.tar --dry-run   # xem trước
    python3 scripts/dev/filestore_restore.py ~/wujia_filestore_pool_20261004.tar             # mọi DB wujia*
    python3 scripts/dev/filestore_restore.py pool.tar --db wujia_tea_19 --db wujia_b2

Với mỗi DB: đọc `ir_attachment.store_fname`, file nào thiếu trên đĩa mà pool có thì chép vào
`<data_dir>/filestore/<db>/`. KHÔNG ghi đè file đã có, KHÔNG xoá file nào.
Bundle CSS/JS (`/web/assets/…`) thiếu file ⇒ xoá dòng attachment đó để Odoo tự build lại
(bỏ bằng --keep-assets). Cần psycopg2 (env odoo19 có sẵn).
"""
import argparse
import configparser
import pathlib
import sys
import tarfile

ROOT = pathlib.Path(__file__).resolve().parents[2]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('pool', help='file .tar từ filestore_pack.py')
    ap.add_argument('--db', action='append', help='DB cần trả (lặp được); mặc định mọi DB wujia%%')
    ap.add_argument('--conf', default=str(ROOT / 'config' / 'odoo.conf'), help='file cấu hình Odoo')
    ap.add_argument('--keep-assets', action='store_true', help='không xoá attachment bundle thiếu file')
    ap.add_argument('--dry-run', action='store_true', help='chỉ đếm, không chép/không xoá')
    args = ap.parse_args()

    import psycopg2

    cfg = configparser.ConfigParser()
    cfg.read(args.conf)
    opt = cfg['options']
    data_dir = pathlib.Path(opt.get('data_dir')).expanduser()
    conn_args = dict(host=opt.get('db_host', '127.0.0.1'), port=opt.get('db_port', '5432'),
                     user=opt.get('db_user'), password=opt.get('db_password'))

    dbs = args.db
    if not dbs:
        with psycopg2.connect(dbname='postgres', **conn_args) as cn, cn.cursor() as cr:
            cr.execute("SELECT datname FROM pg_database WHERE datname LIKE 'wujia%%' "
                       "AND NOT datistemplate ORDER BY datname")
            dbs = [r[0] for r in cr.fetchall()]

    tar = tarfile.open(args.pool)
    members = {m.name: m for m in tar.getmembers() if m.isfile()}
    print('pool: %d file — data_dir: %s%s\n' % (len(members), data_dir, '  [DRY-RUN]' if args.dry_run else ''))
    print('%-22s %8s %8s %8s %10s %8s' % ('DB', 'cần', 'đã có', 'đã chép', 'thiếu-asset', 'thiếu'))

    for db in dbs:
        dest = data_dir / 'filestore' / db
        try:
            cn = psycopg2.connect(dbname=db, **conn_args)
        except psycopg2.Error as e:
            print('%-22s bỏ qua: %s' % (db, str(e).strip().splitlines()[0]))
            continue
        with cn, cn.cursor() as cr:
            try:
                cr.execute("SELECT id, store_fname, coalesce(url, '') FROM ir_attachment "
                           "WHERE store_fname IS NOT NULL")
            except psycopg2.Error:
                print('%-22s bỏ qua: không phải DB Odoo' % db)
                continue
            rows = cr.fetchall()
            have = copied = 0
            asset_ids, missing = [], set()
            for att_id, fname, url in rows:
                target = dest / fname
                if target.exists():
                    have += 1
                elif fname in members:
                    if not args.dry_run:
                        target.parent.mkdir(parents=True, exist_ok=True)
                        with tar.extractfile(members[fname]) as src, open(target, 'xb') as out:
                            out.write(src.read())
                    copied += 1
                elif url.startswith('/web/assets/'):
                    asset_ids.append(att_id)
                else:
                    missing.add(fname)
            if asset_ids and not args.keep_assets and not args.dry_run:
                cr.execute('DELETE FROM ir_attachment WHERE id = ANY(%s)', [asset_ids])
        cn.close()
        print('%-22s %8d %8d %8d %10d %8d' % (db, len(rows), have, copied, len(asset_ids), len(missing)))

    print('\nthiếu-asset: bundle CSS/JS — %s.' % (
        'giữ nguyên (--keep-assets)' if args.keep_assets or args.dry_run else 'đã xoá dòng, Odoo tự build lại'))
    print('thiếu: file pool không có (thường là file upload thử ở local) — không lấy lại được.')
    print('Nhớ khởi động lại server Odoo đang chạy các DB này.')


if __name__ == '__main__':
    sys.exit(main())
