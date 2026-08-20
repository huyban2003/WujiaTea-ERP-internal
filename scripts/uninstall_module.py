#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gỡ sạch một module đã bị XOÁ CODE khỏi repo nhưng DB vẫn ghi là đang cài.

Tình huống: anh Thái xoá thư mục `custom/wujia_portal_remediation`, nhưng trong DB
bản ghi module vẫn `installed` / `to upgrade`. Để nguyên thì mỗi lần khởi động Odoo
lại đi tìm module không còn tồn tại, và view/menu/quyền của nó vẫn nằm lại trong DB.

Gỡ bằng tay trên giao diện thì cần code có mặt. Script này gỡ thẳng bằng ORM nên
KHÔNG cần trả code về.

Cách dùng (dừng service Odoo trước):

    # xem trước, không đổi gì
    python scripts/uninstall_module.py -c <odoo.conf> -d <db> -m wujia_portal_remediation

    # gỡ thật
    python scripts/uninstall_module.py -c <odoo.conf> -d <db> -m wujia_portal_remediation --apply

Chạy xong nhớ khởi động lại service Odoo.
"""

import argparse
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR, 'odoo19'))

import odoo  # noqa: E402  (phải chèn sys.path trước)
from odoo.api import Environment  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('-c', '--config', required=True, help='đường dẫn odoo.conf')
    ap.add_argument('-d', '--db', required=True, help='tên database')
    ap.add_argument('-m', '--module', required=True, help='tên module cần gỡ')
    ap.add_argument('--apply', action='store_true', help='gỡ thật (mặc định chỉ xem trước)')
    args = ap.parse_args()

    odoo.tools.config.parse_config(['-c', args.config, '-d', args.db])
    registry = odoo.modules.registry.Registry(args.db)

    with registry.cursor() as cr:
        env = Environment(cr, odoo.SUPERUSER_ID, {})
        mod = env['ir.module.module'].search([('name', '=', args.module)])
        if not mod:
            print(f"Không thấy module {args.module} trong DB — không phải làm gì.")
            return 0

        print(f"Module      : {mod.name}")
        print(f"Trạng thái  : {mod.state}")
        print(f"Bản đã cài  : {mod.installed_version}")

        code_path = odoo.modules.module.get_module_path(args.module, display_warning=False)
        print(f"Code trên đĩa: {code_path or 'KHÔNG CÒN (đã xoá khỏi repo)'}")

        # Đếm những gì sẽ bị xoá — để biết có đụng dữ liệu nghiệp vụ không.
        cr.execute("""
            SELECT model, count(*) FROM ir_model_data
             WHERE module = %s GROUP BY model ORDER BY 2 DESC
        """, (args.module,))
        rows = cr.fetchall()
        print("\nSẽ xoá các bản ghi sau:")
        for model, n in rows:
            print(f"  {model:<40} {n}")
        if not rows:
            print("  (không có gì)")

        models_own = [m for m, _ in rows if m == 'ir.model']
        if models_own:
            print("\n⚠️  Module này CÓ model riêng ⇒ gỡ sẽ xoá bảng dữ liệu. "
                  "Backup DB trước khi chạy --apply.")

        if not args.apply:
            print("\n(xem trước — thêm --apply để gỡ thật)")
            return 0

        # `to upgrade` là trạng thái treo do code bị xoá giữa chừng; đưa về
        # `installed` cho đúng luồng gỡ chuẩn của Odoo.
        if mod.state == 'to upgrade':
            mod.write({'state': 'installed'})
            cr.commit()
            print("\nĐã đưa trạng thái 'to upgrade' về 'installed'.")

        print("Đang gỡ...")
        mod.button_immediate_uninstall()

    # button_immediate_uninstall dựng lại registry ⇒ mở cursor mới để kiểm tra.
    registry = odoo.modules.registry.Registry(args.db)
    with registry.cursor() as cr:
        env = Environment(cr, odoo.SUPERUSER_ID, {})
        mod = env['ir.module.module'].search([('name', '=', args.module)])
        state = mod.state if mod else 'không còn bản ghi'
        cr.execute("SELECT count(*) FROM ir_model_data WHERE module = %s", (args.module,))
        left = cr.fetchone()[0]

    print(f"\nXong. Trạng thái: {state} · bản ghi còn sót: {left}")
    if state not in ('uninstalled', 'không còn bản ghi') or left:
        print("⚠️  Chưa sạch — đừng khởi động lại service, báo lại để xem tiếp.")
        return 1
    print("Sạch. Khởi động lại service Odoo là xong.")
    return 0


if __name__ == '__main__':
    sys.exit(main())
