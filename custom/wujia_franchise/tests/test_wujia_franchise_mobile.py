# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase


class TestWujiaFranchiseMobile(TransactionCase):
    """Automated unit tests for wujia_franchise mobile enhancements."""

    def test_01_store_master_action_view_mode(self):
        """Verify action_franchise_management prioritizes list view on desktop and supports kanban on mobile."""
        action = self.env.ref('wujia_franchise.action_franchise_management', raise_if_not_found=False)
        self.assertTrue(action, "Action action_franchise_management must exist.")
        self.assertIn('kanban', action.view_mode, "Action must include 'kanban' in view_mode.")
        self.assertTrue(action.view_mode.startswith('list'), "Action should prioritize 'list' view_mode for desktop.")
        self.assertFalse(action.view_id, "Action view_id must not be hardcoded to kanban.")

    def test_02_kanban_view_exists(self):
        """Verify mobile kanban view for Store Master loads properly."""
        store_kanban = self.env.ref('wujia_franchise.view_wujia_franchise_management_kanban_mobile', raise_if_not_found=False)
        self.assertTrue(store_kanban, "Mobile kanban view for Store Master must exist.")
        self.assertEqual(store_kanban.model, 'wujia.franchise.management')
