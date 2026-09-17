# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase


class TestWujiaMobileSale(TransactionCase):
    """Automated unit tests for wujia_sale mobile enhancements."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.partner = cls.env['res.partner'].create({
            'name': 'Test Franchisee Partner',
        })

    def test_01_mobile_badge_class(self):
        """Verify status badge classes are correctly assigned to sales orders."""
        order = self.env['sale.order'].create({
            'partner_id': self.partner.id,
            'state': 'draft',
        })
        self.assertEqual(order.mobile_badge_class, 'wj_mobile_badge--warning')

        order.state = 'sale'
        self.assertEqual(order.mobile_badge_class, 'wj_mobile_badge--success')

        order.state = 'cancel'
        self.assertEqual(order.mobile_badge_class, 'wj_mobile_badge--danger')

    def test_02_mobile_card_title(self):
        """Verify mobile card title prioritizes franchise and area over partner."""
        order = self.env['sale.order'].create({
            'partner_id': self.partner.id,
        })
        # When no franchise_id is set, it defaults to partner_id name
        self.assertEqual(order.mobile_card_title, 'Test Franchisee Partner')

        # Create area and store if wujia.franchise.management model exists
        if 'wujia.franchise.management' in self.env:
            area = False
            if 'res.area' in self.env:
                area = self.env['res.area'].create({
                    'name': 'Area 1 - HCM Central',
                    'code': 'TEST-MB-AREA-01',
                })
            store = self.env['wujia.franchise.management'].create({
                'name': 'Wujia Store 01 - Nguyen Trai',
                'code': 'TEST-MB-STORE-01',
                'partner_id': self.partner.id,
                'area_id': area.id if area else False,
            })
            order.franchise_id = store.id
            order.area_id = area.id if area else False

            if area:
                self.assertEqual(order.mobile_card_title, 'Wujia Store 01 - Nguyen Trai (Area 1 - HCM Central)')
            else:
                self.assertEqual(order.mobile_card_title, 'Wujia Store 01 - Nguyen Trai')

    def test_03_action_wujia_sale_orders_view_mode(self):
        """Verify action_wujia_sale_orders defaults to list on desktop and kanban on mobile."""
        action = self.env.ref('wujia_sale.action_wujia_sale_orders', raise_if_not_found=False)
        if action:
            self.assertIn('kanban', action.view_mode, "Action must include 'kanban' in view_mode.")
            self.assertTrue(action.view_mode.startswith('list'), "Action should prioritize 'list' view_mode for desktop.")
            self.assertFalse(action.view_id, "Action view_id must not be hardcoded to kanban.")
