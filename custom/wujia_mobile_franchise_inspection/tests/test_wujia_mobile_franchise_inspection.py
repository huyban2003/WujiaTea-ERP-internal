# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestWujiaMobileFranchiseInspection(TransactionCase):

    def setUp(self):
        super().setUp()
        self.partner = self.env['res.partner'].create({
            'name': 'Test Store Partner Mobile Inspection',
            'is_franchise': True,
        })
        self.store = self.env['wujia.franchise.management'].create({
            'code': 'INSMOBI01',
            'name': 'Inspection Mobile Test Store',
            'partner_id': self.partner.id,
        })

    def test_01_mobile_view_exists(self):
        """Verify mobile kanban view for franchise inspection exists."""
        view = self.env.ref('wujia_mobile_franchise_inspection.view_wujia_franchise_inspection_kanban_mobile', raise_if_not_found=False)
        self.assertTrue(view, "Mobile kanban view for wujia.franchise.inspection should exist.")
        self.assertEqual(view.model, 'wujia.franchise.inspection')
