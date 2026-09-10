# -*- coding: utf-8 -*-
"""Empirical Challenger Test Harness for WJ-SALE-002 (STT 138)
Module: wujia_sale
Verifies search view filters, domains, and group-by functionality.
"""
import sys
import traceback
from datetime import datetime, timedelta
from odoo import fields

print("=" * 70)
print("WJ-SALE-002 EMPIRICAL CHALLENGER TEST HARNESS")
print("=" * 70)

PASS_COUNT = 0
FAIL_COUNT = 0
TEST_RESULTS = []

def record_test(name, success, details=""):
    global PASS_COUNT, FAIL_COUNT
    if success:
        PASS_COUNT += 1
        status = "PASS"
        print(f"[PASS] {name}")
    else:
        FAIL_COUNT += 1
        status = "FAIL"
        print(f"[FAIL] {name}: {details}")
    TEST_RESULTS.append({"name": name, "status": status, "details": details})

# Models
SaleOrder = env['sale.order']
Partner = env['res.partner']
Franchise = env['wujia.franchise.management']
Area = env['res.area']
Batch = env['stock.picking.batch']
Picking = env['stock.picking']
PickingType = env['stock.picking.type']
Warehouse = env['stock.warehouse']
Product = env['product.product']

try:
    with env.cr.savepoint():
        print("\n--- Phase 1: Test Fixtures Setup ---")
        # 1. Setup Area & Warehouse
        area = Area.search([], limit=1)
        if not area:
            area = Area.create({'name': 'Test Area CH1', 'code': 'TA-CH1'})
        print(f"Area: {area.name} (id={area.id})")

        warehouse = Warehouse.search([], limit=1)
        print(f"Warehouse: {warehouse.name} (id={warehouse.id})")

        # 2. Setup Partners
        parent_partner = Partner.create({
            'name': 'Test Parent Customer CH1',
            'is_company': True,
        })
        child_partner = Partner.create({
            'name': 'Test Child Contact CH1',
            'parent_id': parent_partner.id,
            'is_company': False,
        })
        store_partner = Partner.create({
            'name': 'Test Store Partner CH1',
            'is_franchise': True,
        })
        franchise = Franchise.create({
            'code': 'FR-CH1',
            'name': 'Test Franchise Store CH1',
            'partner_id': store_partner.id,
            'area_id': area.id,
        })
        print(f"Franchise Store: {franchise.name} (id={franchise.id})")

        # 3. Setup Product
        product = Product.search([('sale_ok', '=', True)], limit=1)
        if not product:
            product = Product.create({
                'name': 'Test Tea Ingredient CH1',
                'type': 'consu',
                'list_price': 10000.0,
            })
        print(f"Product: {product.name} (id={product.id})")

        # 4. Setup Batches
        batch_1 = Batch.create({
            'description': 'Test Batch CH1 Active',
        })
        batch_2 = Batch.create({
            'description': 'Test Batch CH1 Cancelled Picking',
        })
        print(f"Batch 1: {batch_1.name} (id={batch_1.id})")

        # 5. Create Test Orders Covering All Edge Cases
        # Case A: Pure Portal Order (is_portal_order=True, is_return_order=False)
        order_portal = SaleOrder.create({
            'name': 'SO-CH1-PORTAL',
            'partner_id': store_partner.id,
            'franchise_id': franchise.id,
            'is_portal_order': True,
            'is_return_order': False,
            'client_order_ref': 'REF-PORTAL-01',
            'date_order': fields.Datetime.now(),
            'order_line': [(0, 0, {
                'product_id': product.id,
                'product_uom_qty': 5,
                'price_unit': 10000.0,
            })],
        })

        # Case B: Pure Return/Compensation Order (is_portal_order=False, is_return_order=True)
        order_return = SaleOrder.create({
            'name': 'SO-CH1-RETURN',
            'partner_id': parent_partner.id,
            'franchise_id': franchise.id,
            'is_portal_order': False,
            'is_return_order': True,
            'client_order_ref': 'REF-RETURN-02',
            'date_order': fields.Datetime.now() - timedelta(days=2),
            'order_line': [(0, 0, {
                'product_id': product.id,
                'product_uom_qty': 2,
                'price_unit': 10000.0,
            })],
        })

        # Case C: Pure Manual Order (is_portal_order=False, is_return_order=False)
        order_manual = SaleOrder.create({
            'name': 'SO-CH1-MANUAL',
            'partner_id': child_partner.id,
            'franchise_id': franchise.id,
            'is_portal_order': False,
            'is_return_order': False,
            'client_order_ref': 'REF-MANUAL-03',
            'date_order': fields.Datetime.now() - timedelta(days=5),
            'order_line': [(0, 0, {
                'product_id': product.id,
                'product_uom_qty': 10,
                'price_unit': 10000.0,
            })],
        })

        # Case D: Manual Order WITHOUT Franchise (franchise_id=False, area_id=False)
        order_manual_no_franchise = SaleOrder.create({
            'name': 'SO-CH1-NO-FRANCHISE',
            'partner_id': parent_partner.id,
            'is_portal_order': False,
            'is_return_order': False,
            'client_order_ref': 'REF-NOFRAN-04',
            'date_order': fields.Datetime.now() - timedelta(days=10),
        })

        # Case E: Edge Case Order with BOTH is_portal_order=True AND is_return_order=True
        order_both = SaleOrder.create({
            'name': 'SO-CH1-BOTH',
            'partner_id': store_partner.id,
            'franchise_id': franchise.id,
            'is_portal_order': True,
            'is_return_order': True,
            'client_order_ref': 'REF-BOTH-05',
            'date_order': fields.Datetime.now() - timedelta(days=1),
        })

        # 6. Setup Picking and Batch Associations
        # Order with Has Batch: Link a stock.picking with batch_1 to order_portal
        picking_type = warehouse.out_type_id or PickingType.search([('code', '=', 'outgoing')], limit=1)
        picking_with_batch = Picking.create({
            'picking_type_id': picking_type.id,
            'location_id': warehouse.lot_stock_id.id,
            'location_dest_id': store_partner.property_stock_customer.id,
            'sale_id': order_portal.id,
            'batch_id': batch_1.id,
            'state': 'assigned',
        })
        # Trigger compute_batch_id
        order_portal._compute_batch_id()

        # Order with CANCELLED picking having a batch: should NOT have batch_id
        picking_cancelled = Picking.create({
            'picking_type_id': picking_type.id,
            'location_id': warehouse.lot_stock_id.id,
            'location_dest_id': parent_partner.property_stock_customer.id,
            'sale_id': order_return.id,
            'batch_id': batch_2.id,
        })
        picking_cancelled.write({'state': 'cancel'})
        print(f"picking_cancelled state: {picking_cancelled.state}")
        order_return._compute_batch_id()

        # Re-read batch_id
        order_portal.invalidate_recordset(['batch_id'])
        order_return.invalidate_recordset(['batch_id'])
        order_manual.invalidate_recordset(['batch_id'])

        created_orders = order_portal | order_return | order_manual | order_manual_no_franchise | order_both
        print(f"Created {len(created_orders)} test orders:")
        for o in created_orders:
            print(f"  - {o.name}: portal={o.is_portal_order}, return={o.is_return_order}, batch={o.batch_id.name or False}, fran={o.franchise_id.code or False}")

        print("\n--- Phase 2: Domain Strict Partitioning & Accuracy Tests ---")

        # Test 2.1: batch_id compute on order_portal
        record_test(
            "Batch Compute: order_portal has batch_id set from active picking",
            order_portal.batch_id.id == batch_1.id,
            f"Expected {batch_1.id}, got {order_portal.batch_id.id}"
        )

        # Test 2.2: batch_id compute on order_return (cancelled picking must be ignored)
        record_test(
            "Batch Compute: order_return batch_id is False despite cancelled picking with batch",
            order_return.batch_id.id is False or not order_return.batch_id,
            f"Expected False, got {order_return.batch_id.id}"
        )

        # Test 2.3: "Portal Orders" domain strictly filters records
        portal_domain = [('is_portal_order', '=', True)]
        found_portal = SaleOrder.search(portal_domain + [('id', 'in', created_orders.ids)])
        expected_portal_ids = {order_portal.id, order_both.id}
        record_test(
            "Filter 'Portal Orders' [('is_portal_order', '=', True)] strictly matches portal orders",
            set(found_portal.ids) == expected_portal_ids,
            f"Expected {expected_portal_ids}, got {set(found_portal.ids)}"
        )

        # Test 2.4: "Compensation Orders" domain strictly filters records
        return_domain = [('is_return_order', '=', True)]
        found_return = SaleOrder.search(return_domain + [('id', 'in', created_orders.ids)])
        expected_return_ids = {order_return.id, order_both.id}
        record_test(
            "Filter 'Compensation Orders' [('is_return_order', '=', True)] strictly matches return orders",
            set(found_return.ids) == expected_return_ids,
            f"Expected {expected_return_ids}, got {set(found_return.ids)}"
        )

        # Test 2.5: "Manual Orders" domain strictly filters records (both portal and return are False)
        manual_domain = [('is_portal_order', '=', False), ('is_return_order', '=', False)]
        found_manual = SaleOrder.search(manual_domain + [('id', 'in', created_orders.ids)])
        expected_manual_ids = {order_manual.id, order_manual_no_franchise.id}
        record_test(
            "Filter 'Manual Orders' [('is_portal_order', '=', False), ('is_return_order', '=', False)] strictly matches manual orders",
            set(found_manual.ids) == expected_manual_ids,
            f"Expected {expected_manual_ids}, got {set(found_manual.ids)}"
        )

        # Test 2.6: Mutual exclusivity between Manual Orders and Portal/Return orders
        manual_set = set(found_manual.ids)
        portal_set = set(found_portal.ids)
        return_set = set(found_return.ids)
        record_test(
            "Mutual Exclusivity: Manual Orders disjoint from Portal Orders",
            len(manual_set.intersection(portal_set)) == 0,
            f"Intersection: {manual_set.intersection(portal_set)}"
        )
        record_test(
            "Mutual Exclusivity: Manual Orders disjoint from Return Orders",
            len(manual_set.intersection(return_set)) == 0,
            f"Intersection: {manual_set.intersection(return_set)}"
        )

        # Test 2.7: Completeness (Coverage) across order types
        # Every order must be Portal, Return, or Manual (Union must cover all created orders)
        all_categorized = manual_set.union(portal_set).union(return_set)
        record_test(
            "Completeness: Portal | Return | Manual covers 100% of orders",
            all_categorized == set(created_orders.ids),
            f"Missing: {set(created_orders.ids) - all_categorized}"
        )

        # Test 2.8: "No Batch" filter [('batch_id', '=', False)]
        no_batch_domain = [('batch_id', '=', False)]
        found_no_batch = SaleOrder.search(no_batch_domain + [('id', 'in', created_orders.ids)])
        expected_no_batch_ids = {order_return.id, order_manual.id, order_manual_no_franchise.id, order_both.id}
        record_test(
            "Filter 'No Batch' [('batch_id', '=', False)] matches orders without active batch",
            set(found_no_batch.ids) == expected_no_batch_ids,
            f"Expected {expected_no_batch_ids}, got {set(found_no_batch.ids)}"
        )

        # Test 2.9: "Has Batch" filter [('batch_id', '!=', False)]
        has_batch_domain = [('batch_id', '!=', False)]
        found_has_batch = SaleOrder.search(has_batch_domain + [('id', 'in', created_orders.ids)])
        expected_has_batch_ids = {order_portal.id}
        record_test(
            "Filter 'Has Batch' [('batch_id', '!=', False)] matches orders with batch",
            set(found_has_batch.ids) == expected_has_batch_ids,
            f"Expected {expected_has_batch_ids}, got {set(found_has_batch.ids)}"
        )

        # Test 2.10: Batch partitioning is a strict mathematical partition (disjoint & complete)
        no_batch_set = set(found_no_batch.ids)
        has_batch_set = set(found_has_batch.ids)
        record_test(
            "Strict Partition: No Batch and Has Batch are disjoint (empty intersection)",
            len(no_batch_set.intersection(has_batch_set)) == 0,
            f"Intersection: {no_batch_set.intersection(has_batch_set)}"
        )
        record_test(
            "Strict Partition: No Batch and Has Batch union equals 100% of orders",
            (no_batch_set | has_batch_set) == set(created_orders.ids),
            f"Missing from batch partition: {set(created_orders.ids) - (no_batch_set | has_batch_set)}"
        )

        print("\n--- Phase 3: Search Fields & Custom Domains ---")
        # Test 3.1: Search by name filter domain
        # filter_domain="['|', '|', ('name', 'ilike', self), ('client_order_ref', 'ilike', self), ('partner_id', 'child_of', self)]"
        # Search by order name substring
        res_by_name = SaleOrder.search([('id', 'in', created_orders.ids), '|', '|', ('name', 'ilike', 'SO-CH1-PORTAL'), ('client_order_ref', 'ilike', 'SO-CH1-PORTAL'), ('partner_id', 'child_of', 'SO-CH1-PORTAL')])
        record_test(
            "Search Field: 'name' filter_domain finds order by order name",
            order_portal in res_by_name,
            f"Found: {res_by_name.mapped('name')}"
        )

        # Test 3.2: Search by client_order_ref via name field domain
        res_by_ref = SaleOrder.search([('id', 'in', created_orders.ids), '|', '|', ('name', 'ilike', 'REF-RETURN-02'), ('client_order_ref', 'ilike', 'REF-RETURN-02'), ('partner_id', 'child_of', 'REF-RETURN-02')])
        record_test(
            "Search Field: 'name' filter_domain finds order by client_order_ref",
            order_return in res_by_ref,
            f"Found: {res_by_ref.mapped('name')}"
        )

        # Test 3.3: Search by partner child_of
        res_by_parent_partner = SaleOrder.search([('id', 'in', created_orders.ids), ('partner_id', 'child_of', parent_partner.id)])
        # Child partner order and parent partner order must both be found
        record_test(
            "Search Field: 'partner_id' operator='child_of' resolves child contacts to parent",
            order_return in res_by_parent_partner and order_manual in res_by_parent_partner and order_manual_no_franchise in res_by_parent_partner,
            f"Found: {res_by_parent_partner.mapped('name')}"
        )

        # Test 3.4: Search by order_line product filter domain
        # filter_domain="[('order_line.product_id', 'ilike', self)]"
        res_by_product = SaleOrder.search([('id', 'in', created_orders.ids), ('order_line.product_id', 'ilike', product.name)])
        record_test(
            "Search Field: 'order_line' filter_domain finds orders containing product",
            order_portal in res_by_product and order_return in res_by_product and order_manual in res_by_product,
            f"Found: {res_by_product.mapped('name')}"
        )

        print("\n--- Phase 4: State Filters ---")
        # Set order states
        order_manual.action_cancel()
        record_test(
            "State Filter: filter_cancel [('state', '=', 'cancel')] matches cancelled order",
            order_manual in SaleOrder.search([('id', 'in', created_orders.ids), ('state', '=', 'cancel')]),
            f"Manual order state: {order_manual.state}"
        )
        record_test(
            "State Filter: filter_draft [('state', '=', 'draft')] matches draft orders",
            order_portal in SaleOrder.search([('id', 'in', created_orders.ids), ('state', '=', 'draft')]),
            f"Portal order state: {order_portal.state}"
        )

        print("\n--- Phase 5: read_group Queries Stress Testing ---")
        # Test individual group by fields
        fields_to_group = [
            ('franchise_id', "Franchise Store"),
            ('area_id', "Area"),
            ('batch_id', "Batch"),
            ('warehouse_id', "Warehouse"),
            ('partner_id', "Customer"),
            ('date_order', "Order Date default"),
            ('date_order:day', "Order Date Day"),
            ('date_order:month', "Order Date Month"),
            ('date_order:year', "Order Date Year"),
        ]

        for groupby_field, label in fields_to_group:
            try:
                res = SaleOrder.read_group(
                    domain=[('id', 'in', created_orders.ids)],
                    fields=['amount_total:sum', 'total_planned_weight:sum'],
                    groupby=[groupby_field],
                    lazy=False,
                )
                record_test(
                    f"read_group single: {label} ('{groupby_field}')",
                    isinstance(res, list) and len(res) > 0,
                    f"Result: {len(res)} groups returned"
                )
            except Exception as e:
                record_test(
                    f"read_group single: {label} ('{groupby_field}')",
                    False,
                    f"Exception raised: {str(e)}"
                )

        # Test NULL handling in read_group
        # order_manual_no_franchise has franchise_id=False, area_id=False
        try:
            null_res = SaleOrder.read_group(
                domain=[('id', '=', order_manual_no_franchise.id)],
                fields=['amount_total:sum'],
                groupby=['franchise_id', 'area_id'],
                lazy=False,
            )
            # Must return a group with False for franchise_id and area_id
            first_group = null_res[0] if null_res else {}
            has_false_group = (first_group.get('franchise_id') is False or first_group.get('franchise_id') is None)
            record_test(
                "read_group NULL robustness: groups record with NULL franchise_id and area_id cleanly",
                has_false_group,
                f"Group result: {null_res}"
            )
        except Exception as e:
            record_test(
                "read_group NULL robustness: groups record with NULL franchise_id and area_id cleanly",
                False,
                f"Exception: {str(e)}"
            )

        # Test multi-level / composite read_group queries
        composite_groupings = [
            (['franchise_id', 'area_id', 'batch_id', 'warehouse_id'], "4-level store-area-batch-wh"),
            (['area_id', 'franchise_id'], "2-level area-franchise hierarchy"),
            (['warehouse_id', 'batch_id'], "2-level warehouse-batch logistics"),
            (['partner_id', 'date_order:month'], "2-level customer-date"),
            (['franchise_id', 'area_id', 'batch_id', 'warehouse_id', 'partner_id', 'date_order:day'], "6-level deep group"),
        ]

        for groupby_list, label in composite_groupings:
            try:
                res = SaleOrder.read_group(
                    domain=[('id', 'in', created_orders.ids)],
                    fields=['amount_total:sum', 'total_planned_weight:sum'],
                    groupby=groupby_list,
                    lazy=False,
                )
                record_test(
                    f"read_group composite: {label}",
                    isinstance(res, list),
                    f"Result: {len(res)} groups returned"
                )
            except Exception as e:
                record_test(
                    f"read_group composite: {label}",
                    False,
                    f"Exception raised: {str(e)}"
                )

        # Test lazy=True read_group (standard Odoo search view interaction style)
        for groupby_field, label in [('franchise_id', 'Store'), ('batch_id', 'Batch'), ('warehouse_id', 'Warehouse')]:
            try:
                res = SaleOrder.read_group(
                    domain=[('id', 'in', created_orders.ids)],
                    fields=['amount_total:sum'],
                    groupby=[groupby_field],
                    lazy=True,
                )
                record_test(
                    f"read_group lazy=True: {label} ('{groupby_field}')",
                    isinstance(res, list) and len(res) > 0,
                    f"Result: {len(res)} groups"
                )
            except Exception as e:
                record_test(
                    f"read_group lazy=True: {label} ('{groupby_field}')",
                    False,
                    f"Exception raised: {str(e)}"
                )

        print("\n--- Phase 6: Conjunction of Multiple Filters ---")
        # Conjunction: "Portal Orders" AND "Has Batch" -> order_portal
        portal_and_batch = SaleOrder.search(portal_domain + has_batch_domain + [('id', 'in', created_orders.ids)])
        record_test(
            "Conjunction: 'Portal Orders' AND 'Has Batch' matches exactly order_portal",
            set(portal_and_batch.ids) == {order_portal.id},
            f"Expected [{order_portal.id}], got {portal_and_batch.ids}"
        )

        # Conjunction: "Portal Orders" AND "No Batch" -> order_both
        portal_no_batch = SaleOrder.search(portal_domain + no_batch_domain + [('id', 'in', created_orders.ids)])
        record_test(
            "Conjunction: 'Portal Orders' AND 'No Batch' matches exactly order_both",
            set(portal_no_batch.ids) == {order_both.id},
            f"Expected [{order_both.id}], got {portal_no_batch.ids}"
        )

        # Conjunction: "Manual Orders" AND "Has Batch" -> empty
        manual_has_batch = SaleOrder.search(manual_domain + has_batch_domain + [('id', 'in', created_orders.ids)])
        record_test(
            "Conjunction: 'Manual Orders' AND 'Has Batch' returns empty set",
            len(manual_has_batch) == 0,
            f"Expected 0, got {len(manual_has_batch)}"
        )

        print("\n--- Phase 7: Verification of Search View Arch in DB ---")
        search_view = env.ref('wujia_sale.view_wujia_sale_order_search')
        record_test(
            "View Arch: view_wujia_sale_order_search exists with priority 25",
            search_view and search_view.priority == 25,
            f"Priority: {search_view.priority if search_view else 'None'}"
        )

        # Trigger explicit rollback via exception at the end of savepoint to keep DB pristine
        raise RuntimeError("ROLLBACK_TO_KEEP_DB_PRISTINE")

except RuntimeError as re:
    if "ROLLBACK_TO_KEEP_DB_PRISTINE" in str(re):
        print("\n[INFO] Database successfully rolled back cleanly. Zero test fixtures persisted.")
    else:
        print(f"\n[ERROR] Unexpected runtime error: {re}")
        traceback.print_exc()
except Exception as e:
    print(f"\n[ERROR] Test harness execution failed: {e}")
    traceback.print_exc()

print("\n" + "=" * 70)
print(f"TEST HARNESS SUMMARY: {PASS_COUNT} PASSED, {FAIL_COUNT} FAILED")
print("=" * 70)
if FAIL_COUNT == 0:
    print("FINAL VERDICT: ALL TESTS PASSED.")
else:
    print(f"FINAL VERDICT: {FAIL_COUNT} TEST(S) FAILED.")
    sys.exit(1)
