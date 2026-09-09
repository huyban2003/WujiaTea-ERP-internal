from datetime import date, timedelta
from odoo.tests import tagged, TransactionCase
from odoo.exceptions import UserError, ValidationError
from odoo.addons.wujia_franchise_contract.hooks import post_init_hook


@tagged('post_install', '-at_install', 'wujia_contract')
class TestFranchiseContract(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Franchise = cls.env['wujia.franchise.management']
        cls.Contract = cls.env['wujia.franchise.contract']
        cls.Partner = cls.env['res.partner']

        cls.partner = cls.Partner.create({'name': 'Test Store Partner'})
        cls.store = cls.Franchise.create({
            'code': 'TCONTRACT01',
            'name': 'Test Contract Store',
            'partner_id': cls.partner.id,
            'franchise_start_date': date(2026, 1, 1),
            'franchise_end_date': date(2026, 12, 31),
        })

    def test_01_invalid_dates(self):
        """End date < Start date raises ValidationError."""
        with self.assertRaises(ValidationError):
            self.Contract.create({
                'name': 'HD-INVALID',
                'franchise_id': self.store.id,
                'start_date': date(2026, 12, 31),
                'end_date': date(2026, 1, 1),
            })

    def test_02a_overlap_new_encloses_existing(self):
        """Case [ ( ) ]: New contract completely encloses existing contract."""
        self.Contract.create({
            'name': 'HD-EXISTING',
            'franchise_id': self.store.id,
            'start_date': date(2026, 3, 1),
            'end_date': date(2026, 6, 30),
        })
        with self.assertRaises(ValidationError):
            self.Contract.create({
                'name': 'HD-ENCLOSING',
                'franchise_id': self.store.id,
                'start_date': date(2026, 1, 1),
                'end_date': date(2026, 12, 31),
            })

    def test_02b_overlap_new_starts_inside(self):
        """Case [ ( ] ): New contract starts inside existing contract."""
        self.Contract.create({
            'name': 'HD-EXISTING',
            'franchise_id': self.store.id,
            'start_date': date(2026, 1, 1),
            'end_date': date(2026, 6, 30),
        })
        with self.assertRaises(ValidationError):
            self.Contract.create({
                'name': 'HD-STARTS-INSIDE',
                'franchise_id': self.store.id,
                'start_date': date(2026, 5, 1),
                'end_date': date(2026, 12, 31),
            })

    def test_02c_overlap_new_inside_existing(self):
        """Case ( [ ] ): New contract is completely inside existing contract."""
        self.Contract.create({
            'name': 'HD-EXISTING',
            'franchise_id': self.store.id,
            'start_date': date(2026, 1, 1),
            'end_date': date(2026, 12, 31),
        })
        with self.assertRaises(ValidationError):
            self.Contract.create({
                'name': 'HD-INSIDE',
                'franchise_id': self.store.id,
                'start_date': date(2026, 3, 1),
                'end_date': date(2026, 6, 30),
            })

    def test_02d_overlap_new_ends_inside(self):
        """Case ( [ ) ]: New contract ends inside existing contract."""
        self.Contract.create({
            'name': 'HD-EXISTING',
            'franchise_id': self.store.id,
            'start_date': date(2026, 5, 1),
            'end_date': date(2026, 12, 31),
        })
        with self.assertRaises(ValidationError):
            self.Contract.create({
                'name': 'HD-ENDS-INSIDE',
                'franchise_id': self.store.id,
                'start_date': date(2026, 1, 1),
                'end_date': date(2026, 6, 30),
            })

    def test_03_non_overlapping_and_cancelled(self):
        """Non-overlapping or cancelled contracts can coexist."""
        c1 = self.Contract.create({
            'name': 'HD-01',
            'franchise_id': self.store.id,
            'start_date': date(2026, 1, 1),
            'end_date': date(2026, 6, 30),
        })

        # Next contract right after c1
        c2 = self.Contract.create({
            'name': 'HD-02',
            'franchise_id': self.store.id,
            'start_date': date(2026, 7, 1),
            'end_date': date(2026, 12, 31),
        })
        self.assertTrue(c2.id)

        # Cancel c1, allows another overlapping contract for c1's period
        c1.write({'active': False})
        c3 = self.Contract.create({
            'name': 'HD-03-REPLACEMENT',
            'franchise_id': self.store.id,
            'start_date': date(2026, 1, 1),
            'end_date': date(2026, 6, 30),
        })
        self.assertTrue(c3.id)

    def test_04_store_current_contract_compute(self):
        """Store computes current_contract_id and dates correctly (excluding draft contracts)."""
        today = date.today()

        # Draft contract in future must NOT be chosen as current_contract_id
        c_draft = self.Contract.create({
            'name': 'HD-FUTURE-DRAFT',
            'franchise_id': self.store.id,
            'start_date': today + timedelta(days=10),
            'end_date': today + timedelta(days=365),
        })
        self.assertEqual(c_draft.state, 'draft')
        self.assertFalse(self.store.current_contract_id)
        self.assertFalse(self.store.franchise_start_date)

        # Effective contract IS chosen as current_contract_id
        c = self.Contract.create({
            'name': 'HD-CURRENT',
            'franchise_id': self.store.id,
            'start_date': today - timedelta(days=10),
            'end_date': today + timedelta(days=20),
        })
        self.assertEqual(c.state, 'effective')
        self.assertEqual(self.store.current_contract_id, c)
        self.assertEqual(self.store.franchise_start_date, c.start_date)
        self.assertEqual(self.store.franchise_end_date, c.end_date)
        self.assertFalse(self.store.is_expired)


    def test_05_migration_legacy_contracts(self):
        """Migration helper creates contract for store without contracts."""
        self.env['ir.config_parameter'].sudo().set_param('wujia_franchise_contract.legacy_migrated', False)
        store2 = self.Franchise.create({
            'code': 'TCONTRACT02',
            'name': 'Legacy Store',
            'partner_id': self.partner.id,
            'franchise_start_date': date(2025, 1, 1),
            'franchise_end_date': date(2025, 12, 31),
        })

        self.Franchise._migrate_legacy_franchise_contracts()
        self.assertTrue(store2.contract_ids)
        self.assertEqual(store2.contract_count, 1)

        # Idempotent check: calling migration again when flag is True does not duplicate
        self.Franchise._migrate_legacy_franchise_contracts()
        self.assertEqual(store2.contract_count, 1)

    def test_06_unlink_restriction(self):
        """Deleting an effective or expired contract raises UserError."""
        c = self.Contract.create({
            'name': 'HD-ACTIVE-DEL',
            'franchise_id': self.store.id,
            'start_date': date(2020, 1, 1),
            'end_date': date(2030, 12, 31),
        })
        self.assertEqual(c.state, 'effective')
        with self.assertRaises(UserError):
            c.unlink()

        # Draft or cancelled contracts can be unlinked
        c_draft = self.Contract.create({
            'name': 'HD-DRAFT-DEL',
            'franchise_id': self.store.id,
            'start_date': date(2040, 1, 1),
            'end_date': date(2040, 12, 31),
        })
        self.assertEqual(c_draft.state, 'draft')
        c_draft.unlink()
        self.assertFalse(c_draft.exists())

    def test_07_post_init_hook(self):
        """post_init_hook executes migration cleanly."""
        self.env['ir.config_parameter'].sudo().set_param('wujia_franchise_contract.legacy_migrated', False)
        store3 = self.Franchise.create({
            'code': 'TCONTRACT03',
            'name': 'Hook Legacy Store',
            'partner_id': self.partner.id,
            'franchise_start_date': date(2025, 6, 1),
            'franchise_end_date': date(2026, 5, 31),
        })
        post_init_hook(self.env)
        self.assertEqual(store3.contract_count, 1)

    def test_08_edit_restriction(self):
        """Editing an effective contract detail raises UserError, but status change / cancellation is allowed."""
        c = self.Contract.create({
            'name': 'HD-ACTIVE-EDIT',
            'franchise_id': self.store.id,
            'start_date': date(2020, 1, 1),
            'end_date': date(2030, 12, 31),
        })
        self.assertEqual(c.state, 'effective')

        # Detail field edits are blocked
        with self.assertRaises(UserError):
            c.write({'note': 'Attempt to edit active contract'})

        # Cancellation / status change IS allowed
        c.action_cancel()
        self.assertEqual(c.state, 'cancelled')

        # Draft contracts can be edited freely
        c_draft = self.Contract.create({
            'name': 'HD-DRAFT-EDIT',
            'franchise_id': self.store.id,
            'start_date': date(2040, 1, 1),
            'end_date': date(2040, 12, 31),
        })
        self.assertEqual(c_draft.state, 'draft')
        c_draft.write({'note': 'Draft note updated'})
        self.assertEqual(c_draft.note, 'Draft note updated')



