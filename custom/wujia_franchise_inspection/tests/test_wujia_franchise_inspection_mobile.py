# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase


class TestWujiaFranchiseInspectionMobile(TransactionCase):
    """Automated unit tests for wujia_franchise_inspection mobile enhancements."""

    def test_01_store_inspection_action_view_mode(self):
        """Verify action_wujia_franchise_inspection prioritizes list view on desktop and supports kanban on mobile."""
        action = self.env.ref('wujia_franchise_inspection.action_wujia_franchise_inspection', raise_if_not_found=False)
        self.assertTrue(action, "Action action_wujia_franchise_inspection must exist.")
        self.assertIn('kanban', action.view_mode, "Action must include 'kanban' in view_mode.")
        self.assertTrue(action.view_mode.startswith('list'), "Action should prioritize 'list' view_mode for desktop.")
        self.assertFalse(action.view_id, "Action view_id must not be hardcoded to kanban.")

    def test_02_kanban_view_exists(self):
        """Verify mobile kanban view for Store Inspection loads properly."""
        inspection_kanban = self.env.ref('wujia_franchise_inspection.view_wujia_franchise_inspection_kanban_mobile', raise_if_not_found=False)
        self.assertTrue(inspection_kanban, "Mobile kanban view for Store Inspection must exist.")
        self.assertEqual(inspection_kanban.model, 'wujia.franchise.inspection')
