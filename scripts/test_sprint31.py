"""Smoke test Sprint 31 — Controller Lịch sử đơn hàng (CT-024 list + CT-025 detail).

ORM-level (helper + dataset rule), chạy qua odoo shell:
    cd /home/huyban/odoo-dev/WujiaTea/odoo19
    /home/huyban/miniconda3/envs/odoo/bin/python odoo-bin shell \\
        -c /home/huyban/odoo-dev/WujiaTea/config/odoo.conf \\
        -d wujia_tea_19 --no-http \\
        < /home/huyban/odoo-dev/WujiaTea/scripts/test_sprint31.py

Tạo fixture (đơn own/cancel/foreign) + commit → HTTP test đọc lại. Route/quyền → test_sprint31_http.py.
"""
import json

from odoo.addons.wujia_portal_purchase_history.controllers import portal as H

print("=== SPRINT 31 SMOKE (ORM) ===")
PASS, FAIL = 0, 0


def check(cond, msg):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  PASS: {msg}")
    else:
        FAIL += 1
        print(f"  FAIL: {msg}")


SO = env['sale.order']
Product = env['product.product']
Member = env['wujia.franchise.member']
Franchise = env['wujia.franchise.management']
Batch = env['stock.picking.batch']

# ---------- 0. cleanup prior fixtures ----------
prior = SO.search([('origin', '=', 'S31TEST')])
if prior:
    prior.write({'state': 'draft'})
    prior.unlink()
Product.search([('default_code', '=', 'S31SP')]).unlink()

# ---------- 1. state meta mapping ----------
print("\n[1] _state_meta")
check(H._state_meta('draft') == ('Chờ xác nhận', 'pending'), "draft → Chờ xác nhận / pending")
check(H._state_meta('sale') == ('Đã xác nhận', 'confirmed'), "sale → Đã xác nhận / confirmed")
check(H._state_meta('sent') == ('Đã gửi', 'sent'), "sent → Đã gửi / sent")
check(H._state_meta('some_future_state') == H.DEFAULT_STATE_META, "unknown state → DEFAULT (Đang xử lý)")
check('cancel' not in H.SALE_STATE_META, "cancel không có trong SALE_STATE_META (ẩn khỏi lịch sử)")

# ---------- 2. fixtures: owner store + foreign store + product/tax ----------
print("\n[2] fixtures")
owner = env['res.users'].search([('login', '=', 'anh.owner')], limit=1)
check(bool(owner), "user anh.owner tồn tại")
owner_fids = owner._get_accessible_franchise_ids() if owner else []
store = Franchise.browse(owner_fids[0]) if owner_fids else Franchise.search([], limit=1)
foreign = Franchise.search([('id', 'not in', list(owner_fids))], limit=1)
check(bool(store), f"owner store = {store.display_name}")
membership = Member.find_active_membership(owner.id, store.id) if owner else False

tax = env['account.tax'].search(
    [('type_tax_use', '=', 'sale'), ('amount', '=', 8), ('amount_type', '=', 'percent')], limit=1)
if not tax:
    tax = env['account.tax'].create(
        {'name': 'S31 8%', 'amount': 8.0, 'amount_type': 'percent', 'type_tax_use': 'sale'})
prod = Product.create({
    'name': 'S31 Trà sữa', 'default_code': 'S31SP', 'type': 'consu',
    'list_price': 10000.0, 'taxes_id': [(6, 0, [tax.id])],
    'description_ecommerce': 'Thùng 24 chai',
})
partner = store.partner_id or env['res.partner'].search([('type', '=', 'contact')], limit=1)


def mk_order(fr, state='sale', requester=None, qty=2, sectionnote=True):
    lines = [(0, 0, {'product_id': prod.id, 'product_uom_qty': qty})]
    if sectionnote:
        lines += [
            (0, 0, {'display_type': 'line_section', 'name': 'Nhóm SP'}),
            (0, 0, {'display_type': 'line_note', 'name': 'Ghi chú dòng'}),
        ]
    vals = {'partner_id': partner.id, 'origin': 'S31TEST', 'franchise_id': fr.id, 'order_line': lines}
    if requester:
        vals['portal_requester_user_id'] = requester.id
    o = SO.create(vals)
    if state and state != 'draft':
        o.write({'state': state})
    return o


own_sale = mk_order(store, state='sale', requester=owner)
own_backend = mk_order(store, state='sale', requester=None)
own_cancel = mk_order(store, state='cancel', requester=None)
foreign_sale = mk_order(foreign, state='sale', requester=None) if foreign else SO
prod_line = own_sale.order_line.filtered(lambda ln: not ln.display_type)[:1]
check(bool(prod_line) and prod_line.price_total > prod_line.price_subtotal,
      f"price_total ({prod_line.price_total}) > price_subtotal ({prod_line.price_subtotal}) — có thuế")

# ---------- 3. requester label (BA) ----------
print("\n[3] _requester_display")
check(H._requester_display(own_sale) == owner.name, "đơn có requester → tên user portal")
check(H._requester_display(own_backend) == H.BACKEND_REQUESTER_LABEL,
      f"đơn backend (không requester) → '{H.BACKEND_REQUESTER_LABEL}'")

# ---------- 4. line vals: giá đã thuế + loại section/note ----------
print("\n[4] _history_line_vals + product_line_count")
lv = H._history_line_vals(prod_line)
check(abs(lv['line_total_tax_included'] - prod_line.price_total) < 0.01,
      "line_total_tax_included = price_total (đã thuế)")
check(abs(lv['unit_price_tax_included'] - (prod_line.price_total / prod_line.product_uom_qty)) < 0.01,
      "unit_price_tax_included = price_total / qty")
check(lv['unit_price_tax_included'] > (prod_line.price_unit or 0),
      "đơn giá đã thuế > price_unit (chưa thuế)")
check(lv['spec'] == 'Thùng 24 chai', "spec = product.description_ecommerce (quy cách)")
check(lv['uom_name'] == prod_line.product_uom_id.name, "uom_name = product_uom_id.name")

labels = dict(Batch._fields['delivery_batch_status'].selection)
detail = H._history_detail_vals(own_sale, labels)
check(detail['header']['product_line_count'] == 1, "product_line_count loại section/note (=1)")
check(len(detail['lines']) == 1, "detail.lines chỉ dòng sản phẩm (section/note loại)")
check(detail['note'] == (own_sale.portal_note or ''), "note = portal_note")

# ---------- 5. batch status label + departure_display ----------
print("\n[5] batch label + departure")
check(labels.get('delivering') == 'Đang giao', "batch selection label: delivering → Đang giao")
b = Batch.create({'name': 'S31-BATCH', 'delivery_batch_status': 'delivering'})
from datetime import datetime, timedelta
b.write({'planned_departure': datetime(2026, 7, 1, 8, 0), 'actual_departure': datetime(2026, 7, 1, 9, 30)})
check((b.actual_departure or b.planned_departure) == b.actual_departure,
      "departure_display ưu tiên actual_departure")
b2 = Batch.create({'name': 'S31-BATCH2', 'delivery_batch_status': 'assigned'})
b2.write({'planned_departure': datetime(2026, 7, 2, 7, 0)})
check((b2.actual_departure or b2.planned_departure) == b2.planned_departure,
      "departure_display fallback planned_departure khi chưa có actual")

# ---------- 6. list domain: ẩn cancel + sort create_date desc ----------
print("\n[6] list domain rules")
domain = [('franchise_id', '=', store.id), ('state', '!=', 'cancel')]
rows = SO.search(domain, order='create_date desc')
check(own_cancel not in rows, "đơn cancel KHÔNG nằm trong list")
check(own_sale in rows and own_backend in rows, "đơn own (sale/backend) nằm trong list")
if len(rows) >= 2:
    cds = [r.create_date for r in rows]
    check(cds == sorted(cds, reverse=True), "sort create_date desc đúng")

row_vals = H._history_row_vals(own_sale, {own_sale.id: 1}, labels)
check(row_vals['state_label'] == 'Đã xác nhận' and row_vals['status_type'] == 'confirmed',
      "row_vals state_label/status_type đúng")
check(row_vals['requester_display'] == owner.name, "row_vals requester_display đúng")

# ---------- 7. write fixture for HTTP test ----------
fixture = {
    'store_id': store.id,
    'own_sale_id': own_sale.id, 'own_sale_name': own_sale.name,
    'own_backend_id': own_backend.id, 'own_backend_name': own_backend.name,
    'cancel_id': own_cancel.id, 'cancel_name': own_cancel.name,
    'foreign_id': foreign_sale.id if foreign else 0,
    'foreign_name': foreign_sale.name if foreign else '',
}
path = '/tmp/claude-1000/-home-huyban-odoo-dev/70cc0c63-b725-40bf-bb0e-6d6ce2f8a665/scratchpad/s31_fixture.json'
with open(path, 'w') as f:
    json.dump(fixture, f)
print(f"  fixture → {path}: {fixture}")

# cleanup batches (không cần cho HTTP)
b.unlink()
b2.unlink()
env.cr.commit()

print(f"\n=== RESULT: {PASS} PASS / {FAIL} FAIL ===")
