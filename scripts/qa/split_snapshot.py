#!/usr/bin/env python3
"""Chụp mọi thứ một lần tách phân hệ có thể làm hỏng — bằng chứng trước/sau cho F7–F13.

Tách `wujia_portal_<x>` → `wujia_<x>` chỉ được phép đổi CỘT MODULE của bản ghi, không được
đổi dữ liệu, quyền, menu, nhãn hay ràng buộc trong bảng thật. Script đọc thẳng Postgres
(qua `psql`, không cần Odoo) và ghi ra một JSON phẳng `khoá → giá trị`:

  module     state + version của các module liên quan
  imd        ir_model_data (model:name#res_id → module) của các module liên quan
  records    số dòng + md5 toàn bảng của từng model (kể cả archived)
  columns    cột thật của bảng (information_schema)
  pgcons     CHECK/FK/UNIQUE thật trong Postgres
  cons/rel   ir_model_constraint / ir_model_relation → module sở hữu (gỡ module = DROP)
  field      ir_model_fields: kiểu, store, relation, nhãn en_US + vi_VN
  acl/rule   ir_model_access, ir_rule của model
  menu       đường dẫn menu đầy đủ + action + group, của module liên quan hoặc trỏ tới model
  action     ir_act_window trỏ tới model
  view       ir_ui_view của model hoặc của module liên quan (md5 arch)
  icp        ir_config_parameter theo tiền tố
  group      số user của mọi group dùng trong acl/rule/menu
  seq        ir_sequence theo code (number_next)
  inherit    ir_model_inherit của model (Odoo 19 có xmlid riêng, F8+ phải chuyển)
  sel        giá trị selection của field thuộc model (xmlid riêng)
  cron/tpl/srv  ir_cron · mail_template · ir_act_server trỏ tới model
  attach     số ir_attachment theo res_model
  Route controller không nằm trong DB — kiểm bằng scripts/qa/controller_inventory.py.

    python3 scripts/qa/split_snapshot.py --db wujia_f7 \
        --modules wujia_portal_order_window,wujia_order_window \
        --models wujia.order.window --icp wujia_portal. -o before.json
    python3 scripts/qa/split_snapshot.py --diff before.json after.json \
        --rename wujia_portal_order_window=wujia_order_window

`--rename old=new` coi "module old" ở bản trước là "module new" — sau đó còn dòng lệch nào
là lệch THẬT. Nhóm `module` luôn in riêng (vỏ đổi version là chủ đích).
"""
import argparse
import json
import subprocess
import sys


def q(args, sql):
    cmd = ['psql', '-h', args.host, '-p', str(args.port), '-U', args.user, '-d', args.db,
           '-X', '-A', '-t', '-v', 'ON_ERROR_STOP=1', '-c', sql]
    out = subprocess.run(cmd, check=True, capture_output=True, text=True).stdout.strip()
    return json.loads(out) if out else []


def lst(values):
    return '(' + ','.join("'%s'" % v.replace("'", "''") for v in values) + ')' if values else "('')"


def snapshot(args):
    mods, models = args.modules, args.models
    tables = [m.replace('.', '_') for m in models]
    snap = {}

    def put(group, key, value):
        snap['%s|%s' % (group, key)] = value

    for r in q(args, f"""select json_agg(json_build_array(name, state, latest_version))
                         from ir_module_module where name in {lst(mods)}"""):
        put('module', r[0], '%s %s' % (r[1], r[2]))

    for r in q(args, f"""select json_agg(json_build_array(model, name, res_id, module))
                         from ir_model_data where module in {lst(mods)}"""):
        put('imd', '%s:%s#%s' % (r[0], r[1], r[2]), r[3])

    for t in tables:
        rows = q(args, f"""select json_build_array(count(*), md5(coalesce(string_agg(x::text, '|' order by x.id), '')))
                           from {t} x""")
        put('records', t, rows)
        for r in q(args, f"""select json_agg(json_build_array(column_name, data_type, is_nullable))
                             from information_schema.columns where table_name = '{t}'"""):
            put('columns', '%s.%s' % (t, r[0]), '%s null=%s' % (r[1], r[2]))
        for r in q(args, f"""select json_agg(json_build_array(conname, pg_get_constraintdef(oid)))
                             from pg_constraint where conrelid = '{t}'::regclass"""):
            put('pgcons', '%s.%s' % (t, r[0]), r[1])

    # gom theo tên: dòng trùng tên (mỗi module một dòng) phải hiện ra, không được gộp mất
    for r in q(args, f"""select json_agg(json_build_array(name, rows)) from (
                           select c.name, json_agg(m.name || ' ' || c.type || ' ' || coalesce(c.definition, '')
                                                   order by m.name) rows
                           from ir_model_constraint c join ir_module_module m on m.id = c.module
                           join ir_model im on im.id = c.model where im.model in {lst(models)}
                           group by c.name) x"""):
        put('cons', r[0], r[1])
    for r in q(args, f"""select json_agg(json_build_array(name, rows)) from (
                           select r.name, json_agg(m.name order by m.name) rows
                           from ir_model_relation r join ir_module_module m on m.id = r.module
                           join ir_model im on im.id = r.model where im.model in {lst(models)}
                           group by r.name) x"""):
        put('rel', r[0], r[1])

    for r in q(args, f"""select json_agg(json_build_array(f.model, f.name, f.ttype, f.store, f.relation,
                                f.required, f.index, f.field_description->>'en_US',
                                f.field_description->>'vi_VN', f.help->>'en_US'))
                         from ir_model_fields f
                         where f.model in {lst(models)}
                            or f.id in (select res_id from ir_model_data
                                         where model = 'ir.model.fields' and module in {lst(mods)})"""):
        put('field', '%s.%s' % (r[0], r[1]), r[2:])

    for r in q(args, f"""select json_agg(json_build_array(a.name, im.model, g.name->>'en_US', a.active,
                                a.perm_read, a.perm_write, a.perm_create, a.perm_unlink))
                         from ir_model_access a join ir_model im on im.id = a.model_id
                         left join res_groups g on g.id = a.group_id where im.model in {lst(models)}"""):
        put('acl', r[0], r[1:])
    for r in q(args, f"""select json_agg(json_build_array(r.name, im.model, r.domain_force, r.active, r.global))
                         from ir_rule r join ir_model im on im.id = r.model_id where im.model in {lst(models)}
                            or r.id in (select res_id from ir_model_data where model = 'ir.rule' and module in {lst(mods)})"""):
        put('rule', r[0] or '', r[1:])

    menu_sql = f"""
      with recursive p(id, path) as (
        select id, name->>'en_US' from ir_ui_menu where parent_id is null
        union all select c.id, p.path || ' / ' || (c.name->>'en_US') from ir_ui_menu c join p on c.parent_id = p.id)
      select json_agg(json_build_array(p.path, m.action, m.sequence, m.active,
             (select string_agg(g.name->>'en_US', ',' order by g.id) from ir_ui_menu_group_rel r
                join res_groups g on g.id = r.gid where r.menu_id = m.id)))
      from ir_ui_menu m join p on p.id = m.id
      where m.id in (select res_id from ir_model_data where model = 'ir.ui.menu' and module in {lst(mods)})
         or m.action in (select 'ir.actions.act_window,' || id from ir_act_window where res_model in {lst(models)})"""
    for r in q(args, menu_sql):
        put('menu', r[0], r[1:])

    for r in q(args, f"""select json_agg(json_build_array(id, name->>'en_US', res_model, view_mode, context, domain,
                                (select name from ir_ui_view v where v.id = a.search_view_id)))
                         from ir_act_window a where res_model in {lst(models)}"""):
        put('action', r[0], r[1:])

    for r in q(args, f"""select json_agg(json_build_array(v.id, v.name, v.model, v.mode, v.priority, v.active,
                                (select name from ir_ui_view i where i.id = v.inherit_id), md5(v.arch_db::text)))
                         from ir_ui_view v
                         where v.model in {lst(models)}
                            or v.id in (select res_id from ir_model_data where model = 'ir.ui.view' and module in {lst(mods)})"""):
        put('view', r[0], r[1:])

    for prefix in args.icp:
        for r in q(args, f"""select json_agg(json_build_array(key, value)) from ir_config_parameter
                             where key like '{prefix}%'"""):
            put('icp', r[0], r[1])

    group_sql = f"""
      select json_agg(json_build_array(g.name->>'en_US', (select count(*) from res_groups_users_rel u where u.gid = g.id)))
      from res_groups g where g.id in (
        select group_id from ir_model_access a join ir_model im on im.id = a.model_id where im.model in {lst(models)}
        union select r.group_id from rule_group_rel r join ir_rule ru on ru.id = r.rule_group_id
              join ir_model im on im.id = ru.model_id where im.model in {lst(models)}
        union select gid from ir_ui_menu_group_rel where menu_id in
              (select res_id from ir_model_data where model = 'ir.ui.menu' and module in {lst(mods)}))"""
    for r in q(args, group_sql):
        put('group', r[0], r[1])

    for r in q(args, f"""select json_agg(json_build_array(code, number_next, prefix, padding, active))
                         from ir_sequence where code in {lst(args.seq)}"""):
        put('seq', r[0], r[1:])

    # Odoo 19: inherit + selection có xmlid riêng — F7 không gặp (model không kế thừa mixin), F8+ có
    for r in q(args, f"""select json_agg(json_build_array(im.model, p.model, pf.name))
                         from ir_model_inherit i join ir_model im on im.id = i.model_id
                         join ir_model p on p.id = i.parent_id left join ir_model_fields pf on pf.id = i.parent_field_id
                         where im.model in {lst(models)}"""):
        put('inherit', '%s<%s' % (r[0], r[1]), r[2])
    for r in q(args, f"""select json_agg(json_build_array(f.model, f.name, s.value, s.name->>'en_US', s.name->>'vi_VN', s.sequence))
                         from ir_model_fields_selection s join ir_model_fields f on f.id = s.field_id
                         where f.model in {lst(models)}"""):
        put('sel', '%s.%s=%s' % (r[0], r[1], r[2]), r[3:])
    for group, table, flag in (('tpl', 'mail_template', 't.active'), ('srv', 'ir_act_server', 't.state')):
        for r in q(args, f"""select json_agg(json_build_array(t.id, t.name->>'en_US', {flag}))
                             from {table} t join ir_model im on im.id = t.model_id where im.model in {lst(models)}"""):
            put(group, r[0], r[1:])
    # ir_cron kế thừa ir.actions.server (Odoo 17+): tên + model nằm ở ir_act_server
    for r in q(args, f"""select json_agg(json_build_array(t.id, a.name->>'en_US', t.active, t.interval_number, t.interval_type))
                         from ir_cron t join ir_act_server a on a.id = t.ir_actions_server_id
                         join ir_model im on im.id = a.model_id where im.model in {lst(models)}"""):
        put('cron', r[0], r[1:])
    for r in q(args, f"""select json_agg(json_build_array(res_model, n)) from
                         (select res_model, count(*) n from ir_attachment where res_model in {lst(models)} group by 1) x"""):
        put('attach', r[0], r[1])
    return snap


def diff(before_path, after_path, renames):
    before = json.load(open(before_path, encoding='utf-8'))
    after = json.load(open(after_path, encoding='utf-8'))

    def norm(value):
        text = json.dumps(value, ensure_ascii=False)
        for old, new in renames:
            text = text.replace('"%s"' % old, '"%s"' % new).replace('"%s ' % old, '"%s ' % new)
        return text

    moved = sum(1 for k, v in before.items() if k.startswith(('imd|', 'cons|', 'rel|'))
                and any(o in str(v) and o not in str(after.get(k, '')) for o, _n in renames))
    real, info = [], []
    for key in sorted(set(before) | set(after)):
        b, a = before.get(key, '∅'), after.get(key, '∅')
        if key.startswith('module|'):
            if b != a:
                info.append((key, b, a))
            continue
        if norm(b) != norm(a):
            real.append((key, b, a))

    print('# split_snapshot diff — %d khoá trước, %d khoá sau' % (len(before), len(after)))
    print('đổi chủ theo --rename: %d dòng' % moved)
    for key, b, a in info:
        print('  (module) %s: %s → %s' % (key[7:], b, a))
    print('LỆCH THẬT: %d' % len(real))
    for key, b, a in real:
        print('  %s\n    trước: %s\n    sau:   %s' % (key, json.dumps(b, ensure_ascii=False), json.dumps(a, ensure_ascii=False)))
    return 1 if real else 0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--db')
    ap.add_argument('--host', default='127.0.0.1')
    ap.add_argument('--port', default=5432, type=int)
    ap.add_argument('--user', default='odoo19')
    ap.add_argument('--modules', default='', type=lambda s: [x for x in s.split(',') if x])
    ap.add_argument('--models', default='', type=lambda s: [x for x in s.split(',') if x])
    ap.add_argument('--icp', action='append', default=[])
    ap.add_argument('--seq', default='', type=lambda s: [x for x in s.split(',') if x])
    ap.add_argument('-o', '--out')
    ap.add_argument('--diff', nargs=2, metavar=('BEFORE', 'AFTER'))
    ap.add_argument('--rename', action='append', default=[], help='old=new')
    args = ap.parse_args()

    if args.diff:
        sys.exit(diff(*args.diff, [tuple(r.split('=', 1)) for r in args.rename]))
    if not (args.db and args.out):
        ap.error('cần --db và -o (hoặc --diff)')
    snap = snapshot(args)
    with open(args.out, 'w', encoding='utf-8') as fh:
        json.dump(snap, fh, ensure_ascii=False, indent=1, sort_keys=True)
    groups = {}
    for key in snap:
        groups[key.split('|', 1)[0]] = groups.get(key.split('|', 1)[0], 0) + 1
    print('%s: %d khoá — %s' % (args.out, len(snap), ', '.join('%s %d' % kv for kv in sorted(groups.items()))))


if __name__ == '__main__':
    main()
