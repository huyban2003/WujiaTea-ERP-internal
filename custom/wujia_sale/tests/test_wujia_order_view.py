# -*- coding: utf-8 -*-
from lxml import etree

from odoo.tests.common import TransactionCase, tagged


@tagged('post_install', '-at_install', 'wujia_sale')
class TestWujiaOrderView(TransactionCase):
    """Automated Unit Tests for WJ-SALE-002 (STT 138)
    Wujia Sales Orders Inherited List & Search Views Verification.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Partner = cls.env['res.partner']
        cls.SaleOrder = cls.env['sale.order']

        cls.partner = cls.Partner.create({
            'name': 'Test Store Partner WJ-SALE-002',
            'is_franchise': True,
        })
        cls.franchise = cls.env['wujia.franchise.management'].create({
            'code': 'TEST-002',
            'name': 'Test Franchise Store WJ-SALE-002',
            'partner_id': cls.partner.id,
        })

    def test_01_action_and_menu(self):
        """Test 1: Action and menu item are properly configured."""
        action = self.env.ref('wujia_sale.action_wujia_sale_orders')
        self.assertEqual(action.res_model, 'sale.order', "Action model must be sale.order")

        # Menu Item verification
        menu = self.env.ref('wujia_sale.menu_wujia_sale_orders')
        self.assertEqual(menu.action.id, action.id, "Menu item must trigger action_wujia_sale_orders")
        self.assertEqual(
            menu.parent_id.id,
            self.env.ref('sale.sale_order_menu').id,
            "Menu item parent must be sale.sale_order_menu",
        )
        self.assertEqual(menu.sequence, 2, "Menu item sequence must be 2")

    def test_02_inherited_tree_view_structure_and_priority(self):
        """Test 2: Inherited tree view sale.order.list.inherit.wujia exists with priority=99,
        inherits sale.sale_order_tree, and adds Wujia fields."""
        tree_view = self.env.ref('wujia_sale.view_order_tree_wujia')
        self.assertEqual(tree_view.name, 'sale.order.list.inherit.wujia')
        self.assertEqual(tree_view.priority, 99, "Priority must be 99")
        self.assertEqual(tree_view.inherit_id.id, self.env.ref('sale.sale_order_tree').id)

        arch_xml = tree_view.arch_base or tree_view.arch
        root = etree.fromstring(arch_xml)

        fields = [f.get('name') for f in root.xpath('//field')]
        for fname in ['create_date', 'franchise_id', 'area_id', 'is_portal_order', 'is_return_order', 'total_planned_weight', 'batch_id']:
            self.assertIn(fname, fields, f"Field '{fname}' must be added in inherited tree view")

    def test_03_inherited_search_view_filters_and_group_by(self):
        """Test 3: Search view inherits sale.view_sales_order_filter and queries run successfully."""
        search_view = self.env.ref('wujia_sale.view_sales_order_filter_wujia')
        self.assertEqual(search_view.priority, 99)
        self.assertEqual(search_view.inherit_id.id, self.env.ref('sale.view_sales_order_filter').id)

        arch_xml = search_view.arch_base or search_view.arch
        root = etree.fromstring(arch_xml)

        filters = root.xpath('//filter')
        domains = [f.get('domain') for f in filters if f.get('domain')]
        contexts = [f.get('context') for f in filters if f.get('context')]
        context_str = " ".join(contexts)

        # 1. Check filters
        self.assertTrue(any('is_portal_order' in d and 'True' in d for d in domains))
        self.assertTrue(any('is_return_order' in d and 'True' in d for d in domains))
        self.assertTrue(any('batch_id' in d and 'False' in d for d in domains))

        # 2. Check group-by options
        self.assertIn("'franchise_id'", context_str)
        self.assertIn("'area_id'", context_str)
        self.assertIn("'batch_id'", context_str)

        # 3. Functional ORM verification
        so_portal = self.SaleOrder.create({
            'partner_id': self.partner.id,
            'franchise_id': self.franchise.id,
            'is_portal_order': True,
            'is_return_order': False,
        })
        so_return = self.SaleOrder.create({
            'partner_id': self.partner.id,
            'franchise_id': self.franchise.id,
            'is_portal_order': False,
            'is_return_order': True,
        })

        portal_orders = self.SaleOrder.search([('is_portal_order', '=', True)])
        self.assertIn(so_portal, portal_orders)
        self.assertNotIn(so_return, portal_orders)

    def test_04_combined_list_view_has_all_fields(self):
        """Test 4: Combined list view for sale.order has Wujia fields."""
        list_view = self.SaleOrder.get_view(view_type='list')
        arch_xml = list_view['arch']
        root = etree.fromstring(arch_xml)
        field_names = [f.get('name') for f in root.xpath('//field')]

        for fname in ['franchise_id', 'area_id', 'is_portal_order', 'is_return_order', 'total_planned_weight', 'batch_id']:
            self.assertIn(fname, field_names, f"Combined list view must contain '{fname}'")
