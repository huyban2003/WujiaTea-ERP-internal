"""Smoke test Sprint 30 — Order controller (product fields + shared cart + submit rules).

Run via odoo shell (ORM-level, same style as test_sprint9.py):
    cd /home/huyban/odoo-dev/WujiaTea/odoo19
    /home/huyban/miniconda3/envs/odoo/bin/python odoo-bin shell \\
        -c /home/huyban/odoo-dev/WujiaTea/config/odoo.conf \\
        -d wujia_tea_19 --no-http \\
        < /home/huyban/odoo-dev/WujiaTea/scripts/test_sprint30.py

HTTP-level (routes, race 2 submit, giỏ chung 2 user) → test_sprint30_http.py.
"""
import psycopg2

print("=== SPRINT 30 SMOKE TEST ===")

PASS, FAIL = 0, 0


def check(cond, msg):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  PASS: {msg}")
    else:
        FAIL += 1
        print(f"  FAIL: {msg}")


from odoo.exceptions import ValidationError

Product = env['product.product']
Cart = env['wujia.portal.cart']
Line = env['wujia.portal.cart.line']
SO = env['sale.order']
Franchise = env['wujia.franchise.management']

# ---------- 1. Migration state ----------
print("\n[1] Migration template → variant")
env.cr.execute("""
    SELECT count(*) FROM information_schema.columns
    WHERE table_name = 'product_template'
      AND column_name IN ('is_public_website', 'min_qty', 'max_qty')
""")
check(env.cr.fetchone()[0] == 0, "old template columns dropped")
check('is_public_portal' in Product._fields, "product.product.is_public_portal exists")
publics = Product.search([('is_public_portal', '=', True)])
check(publics and all(p.min_qty > 0 for p in publics), f"all {len(publics)} public products have min_qty > 0")
env.cr.execute("""
    SELECT domain_force FROM ir_rule r
    JOIN ir_model_data d ON d.res_id = r.id AND d.model = 'ir.rule'
    WHERE d.module = 'wujia_sale' AND d.name = 'rule_product_product_portal_public'
""")
check("is_public_portal" in (env.cr.fetchone() or [''])[0], "portal product rule domain updated")
env.cr.execute("""
    SELECT count(*) FROM ir_model_data
    WHERE module = 'wujia_sale' AND name = 'rule_product_template_portal_public'
""")
check(env.cr.fetchone()[0] == 0, "old template rule removed")

# ---------- 2. Product constraints (BA min/step/max) ----------
print("\n[2] product.product constraints")
tmpl_vals = {'name': 'S30 Test SP', 'type': 'consu', 'list_price': 10000}
prod = Product.create(tmpl_vals)
try:
    prod.write({'is_public_portal': True})   # min_qty = 0
    check(False, "public with min_qty=0 must raise")
except ValidationError:
    check(True, "public with min_qty=0 raises (MIN_QTY rule)")
prod.write({'min_qty': 5, 'is_public_portal': True})
try:
    prod.write({'max_qty': 12})              # 12 % 5 != 0
    check(False, "max not divisible by min must raise")
except ValidationError:
    check(True, "max_qty must be divisible by min_qty")
prod.write({'max_qty': 20})
check(prod.max_qty == 20, "valid max_qty accepted (20 = 4 x 5)")

# ---------- 3. Cart model + unique constraints ----------
print("\n[3] wujia.portal.cart shared per store")
fr = Franchise.search([('partner_id', '!=', False)], limit=1)
Cart.search([('franchise_id', '=', fr.id)]).unlink()
cart = Cart.create({'franchise_id': fr.id})
try:
    with env.cr.savepoint():
        Cart.create({'franchise_id': fr.id})
    check(False, "second cart per store must raise")
except (ValidationError, psycopg2.IntegrityError, Exception):
    check(True, "unique(franchise_id): 1 store 1 cart")

# ---------- 4. Upsert SQL semantics (controller add path) ----------
print("\n[4] atomic upsert + cap max_qty")
UPSERT = """
    INSERT INTO wujia_portal_cart_line
           (cart_id, product_id, qty, create_uid, create_date, write_uid, write_date)
    VALUES (%(cart)s, %(product)s, LEAST(%(inc)s, %(cap)s),
            %(uid)s, now() AT TIME ZONE 'UTC', %(uid)s, now() AT TIME ZONE 'UTC')
    ON CONFLICT (cart_id, product_id) DO UPDATE
       SET qty = LEAST(wujia_portal_cart_line.qty + %(inc)s, %(cap)s),
           write_uid = %(uid)s, write_date = now() AT TIME ZONE 'UTC'
    RETURNING id, qty
"""
params = {'cart': cart.id, 'product': prod.id, 'inc': 5, 'cap': 20, 'uid': env.uid}
env.cr.execute(UPSERT, params)
_lid, q1 = env.cr.fetchone()
env.cr.execute(UPSERT, params)
_lid, q2 = env.cr.fetchone()
check(q1 == 5 and q2 == 10, f"add twice: 5 → 10 (got {q1} → {q2})")
for _ in range(4):
    env.cr.execute(UPSERT, params)
    _lid, qn = env.cr.fetchone()
check(qn == 20, f"cap at max_qty=20 (got {qn})")
Line.invalidate_model()
env.cr.execute("SELECT create_uid, write_uid FROM wujia_portal_cart_line WHERE id = %s", (_lid,))
cu, wu = env.cr.fetchone()
check(cu == env.uid and wu == env.uid, "audit columns set by raw upsert")

# ---------- 5. SOL portal constraint: min/step/max ----------
print("\n[5] sale.order.line portal constraint (step = min_qty)")
so_vals = {
    'is_portal_order': True,
    'franchise_id': fr.id,
    'franchise_partner_id': fr.partner_id.id,
    'partner_id': fr.partner_id.id,
    'portal_requester_user_id': env.uid,
}
# Đơn hợp lệ: qty = 10 (bội của 5, <= 20)
try:
    with env.cr.savepoint():
        so_ok = SO.create(dict(so_vals, order_line=[(0, 0, {
            'product_id': prod.id, 'product_uom_qty': 10,
        })]))
        check(so_ok.state == 'draft', "portal SO created at draft with valid qty")
        so_ok.write({'state': 'cancel'})
except ValidationError as e:
    # ORM window gate có thể chặn nếu chạy test ngoài khung giờ — chấp nhận cả 2 nhánh.
    check('khung giờ' in str(e), f"SO create blocked only by window gate ({e})")
try:
    with env.cr.savepoint():
        SO.create(dict(so_vals, order_line=[(0, 0, {
            'product_id': prod.id, 'product_uom_qty': 7,   # 7 % 5 != 0
        })]))
    check(False, "qty=7 (sai step 5) must raise")
except ValidationError:
    check(True, "qty violating step rejected at ORM (defense-in-depth)")

# ---------- 6. Category model ----------
print("\n[6] wujia.product.category")
cat = env['wujia.product.category'].create({'name': 'S30 Cat', 'sequence': 5})
prod.write({'public_categ_id': cat.id})
check(prod.public_categ_id == cat, "product linked to portal category")
groups = Product._read_group(
    [('is_public_portal', '=', True), ('public_categ_id', '!=', False)],
    ['public_categ_id'], [],
)
check(any(g[0].id == cat.id for g in groups), "read_group returns used category")

# ---------- cleanup ----------
Line.search([('cart_id', '=', cart.id)]).unlink()
cart.unlink()
prod.write({'is_public_portal': False})
prod.unlink()
cat.unlink()
env.cr.commit()

print(f"\n=== RESULT: {PASS} PASS / {FAIL} FAIL ===")
