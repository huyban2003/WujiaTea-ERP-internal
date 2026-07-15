#!/usr/bin/env python3
"""Seed a demo dashboard for wj_ks_dashboard_ninja (Sprint 35 Step 1 verify).

Run:  cd WujiaTea/odoo19 && ../scripts/seed_dashboard_demo.py via odoo-bin shell:
      /home/huyban/miniconda3/envs/odoo/bin/python odoo-bin shell -c ../config/odoo.conf -d wujia_tea_19 --no-http < ../scripts/seed_dashboard_demo.py

Creates (idempotent): board "WJ Demo Dashboard" + 3 items (tile / bar chart / list view)
on res.partner, then calls ks_fetch_dashboard_data + item fetch to assert payload.
"""

BOARD_NAME = 'WJ Demo Dashboard'

Board = env['ks_dashboard_ninja.board']
Item = env['ks_dashboard_ninja.item']
IrModel = env['ir.model']
IrModelFields = env['ir.model.fields']

partner_model = IrModel.search([('model', '=', 'res.partner')], limit=1)
assert partner_model, 'res.partner ir.model missing'

board = Board.search([('name', '=', BOARD_NAME)], limit=1)
if not board:
    menu_root = env.ref('wj_ks_dashboard_ninja.board_menu_root')
    board = Board.create({
        'name': BOARD_NAME,
        'ks_dashboard_menu_name': BOARD_NAME,
        'ks_dashboard_top_menu_id': menu_root.id,
    })
    print(f'created board id={board.id}')
else:
    print(f'board exists id={board.id}')

def ensure_item(name, vals):
    it = Item.search([('name', '=', name), ('ks_dashboard_ninja_board_id', '=', board.id)], limit=1)
    if not it:
        it = Item.create(dict(vals, name=name, ks_dashboard_ninja_board_id=board.id))
        print(f'created item {name} id={it.id}')
    else:
        print(f'item exists {name} id={it.id}')
    return it

# 1. Tile — count partners
tile = ensure_item('WJ Tile Partners', {
    'ks_model_id': partner_model.id,
    'ks_dashboard_item_type': 'ks_tile',
    'ks_record_count_type': 'count',
})

# 2. Bar chart — partners grouped by country
country_field = IrModelFields.search([
    ('model', '=', 'res.partner'), ('name', '=', 'country_id')], limit=1)
bar = ensure_item('WJ Bar Partners by Country', {
    'ks_model_id': partner_model.id,
    'ks_dashboard_item_type': 'ks_bar_chart',
    'ks_chart_data_count_type': 'count',
    'ks_chart_relation_groupby': country_field.id,
})

# 3. List view — partner fields
fields_list = IrModelFields.search([
    ('model', '=', 'res.partner'), ('name', 'in', ['name', 'email', 'city'])])
lst = ensure_item('WJ List Partners', {
    'ks_model_id': partner_model.id,
    'ks_dashboard_item_type': 'ks_list_view',
    'ks_list_view_type': 'ungrouped',
    'ks_list_view_fields': [(6, 0, fields_list.ids)],
})

env.cr.commit()

# --- asserts ---
data = board.ks_fetch_dashboard_data(board.id)
assert isinstance(data, dict), 'ks_fetch_dashboard_data must return dict'
assert 'ks_item_data' in data, 'missing ks_item_data key'
item_ids = set(board.ks_dashboard_items_ids.ids)
assert {tile.id, bar.id, lst.id} <= item_ids, 'items not linked to board'

items_data = board.ks_fetch_item(list(item_ids), board.id, {})
assert str(tile.id) in {str(k) for k in items_data.keys()} or tile.id in items_data, 'tile data missing'

print('SEED+ASSERT OK: board', board.id, '| items', sorted(item_ids), '| payload keys', len(data))
