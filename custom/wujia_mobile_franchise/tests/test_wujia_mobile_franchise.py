# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestWujiaMobileFranchise(TransactionCase):

    def setUp(self):
        super().setUp()
        self.partner = self.env['res.partner'].create({
            'name': 'Test Store Partner Mobile Franchise',
            'is_franchise': True,
        })
        self.store = self.env['wujia.franchise.management'].create({
            'code': 'FRMOBI01',
            'name': 'Franchise Mobile Store',
            'partner_id': self.partner.id,
        })

    def test_01_mobile_view_exists(self):
        """Verify mobile kanban view for franchise management exists."""
        view = self.env.ref('wujia_mobile_franchise.view_wujia_franchise_management_kanban_mobile', raise_if_not_found=False)
        self.assertTrue(view, "Mobile kanban view for wujia.franchise.management should exist.")
        self.assertEqual(view.model, 'wujia.franchise.management')
