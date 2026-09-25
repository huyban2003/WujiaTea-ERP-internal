"""Đổi chủ bản ghi khi tách ``wujia_portal_order_window`` → ``wujia_order_window`` (F7, ADR-027).

Module cũ bị rút hết nên chuyển TOÀN BỘ bản ghi của nó. Không đổi thì Odoo tạo bản sao dưới
tên mới rồi ``_process_end`` dọn bản cũ; còn ``ir_model_constraint`` để chủ cũ thì module mới
sinh dòng trùng tên và dòng cũ mồ côi sau khi gỡ vỏ (đo F7: 2 trùng + 6 mồ côi). Chạy ở
``pre_init_hook`` vì Odoo không chạy migration ở lần cài đầu.
"""
import logging

_logger = logging.getLogger(__name__)

OLD_MODULE = 'wujia_portal_order_window'
NEW_MODULE = 'wujia_order_window'


def migrate_ownership(cr, old, new, names=None, models=None):
    """Chuyển ``ir_model_data`` (``names``) + ràng buộc/quan hệ bảng (``models``) của ``old``.

    None ⇒ chuyển tất cả (module cũ bị rút hết, như F7).
    """
    if names is None:
        cr.execute("UPDATE ir_model_data SET module = %s WHERE module = %s", (new, old))
    else:
        cr.execute("UPDATE ir_model_data SET module = %s WHERE module = %s AND name IN %s",
                   (new, old, tuple(names)))
    moved = {'ir_model_data': cr.rowcount}
    for table in ('ir_model_constraint', 'ir_model_relation'):
        query = f"""
            UPDATE {table} t SET module = (SELECT id FROM ir_module_module WHERE name = %s)
             WHERE t.module = (SELECT id FROM ir_module_module WHERE name = %s)"""
        params = [new, old]
        if models is not None:
            query += " AND t.model IN (SELECT id FROM ir_model WHERE model IN %s)"
            params.append(tuple(models))
        cr.execute(query, params)
        moved[table] = cr.rowcount
    return moved


def pre_init_hook(env):
    moved = migrate_ownership(env.cr, OLD_MODULE, NEW_MODULE)
    _logger.info("%s: doi chu tu %s — %s", NEW_MODULE, OLD_MODULE, moved)
