# -*- coding: utf-8 -*-
from datetime import date, timedelta
from odoo.fields import Date
from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase, tagged


@tagged('post_install', '-at_install', 'wujia_franchise_operations')
class TestFranchiseOperations(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Partner = cls.env['res.partner']
        cls.Franchise = cls.env['wujia.franchise.management']
        cls.Employee = cls.env['wujia.franchise.employee']
        cls.Assignment = cls.env['wujia.franchise.employee.assignment']
        cls.ShiftTemplate = cls.env['wujia.franchise.shift.template']
        cls.Schedule = cls.env['wujia.franchise.work.schedule']
        cls.ExpenseCategory = cls.env['wujia.franchise.expense.category']
        cls.Expense = cls.env['wujia.franchise.expense']
        cls.Revenue = cls.env['wujia.franchise.revenue']

        cls.partner1 = cls.Partner.create({'name': 'Store Partner 1', 'is_franchise': True})
        cls.partner2 = cls.Partner.create({'name': 'Store Partner 2', 'is_franchise': True})

        cls.store1 = cls.Franchise.create({
            'code': 'HCM-OPS-01',
            'name': 'Wujia Store 1',
            'partner_id': cls.partner1.id,
        })
        cls.store2 = cls.Franchise.create({
            'code': 'HCM-OPS-02',
            'name': 'Wujia Store 2',
            'partner_id': cls.partner2.id,
        })

        cls.employee = cls.Employee.create({
            'name': 'Nguyen Van A',
            'phone': '0901234567',
        })

        cls.shift_morning = cls.ShiftTemplate.create({
            'name': 'Test Morning Shift',
            'code': 'TEST_MORNING',
            'start_time': 6.5,
            'end_time': 14.5,
            'break_minutes': 30,
        })

        cls.expense_cat = cls.ExpenseCategory.create({
            'name': 'Electricity Bill',
            'code': 'TEST_ELEC',
            'expense_type': 'operating',
        })

    def test_01_primary_assignment_unique_constraint(self):
        """Test AC4: Max 1 active primary assignment per employee."""
        assign1 = self.Assignment.create({
            'employee_id': self.employee.id,
            'franchise_id': self.store1.id,
            'is_primary': True,
            'state': 'working',
        })
        self.assertTrue(assign1.is_primary)

        with self.assertRaises(ValidationError):
            self.Assignment.create({
                'employee_id': self.employee.id,
                'franchise_id': self.store2.id,
                'is_primary': True,
                'state': 'working',
            })

    def test_02_assignment_date_range_overlap(self):
        """Test AC3: Overlapping assignments at the same store trigger ValidationError."""
        self.Assignment.create({
            'employee_id': self.employee.id,
            'franchise_id': self.store1.id,
            'date_from': date(2026, 1, 1),
            'date_to': date(2026, 6, 30),
            'state': 'working',
        })

        with self.assertRaises(ValidationError):
            self.Assignment.create({
                'employee_id': self.employee.id,
                'franchise_id': self.store1.id,
                'date_from': date(2026, 5, 1),
                'date_to': date(2026, 8, 31),
                'state': 'working',
            })

    def test_03_shift_template_hours_computation(self):
        """Test shift planned hours computation (normal vs overnight)."""
        self.assertAlmostEqual(self.shift_morning.planned_hours, 7.5)

        overnight = self.ShiftTemplate.create({
            'name': 'Overnight Shift',
            'code': 'TEST_NIGHT',
            'start_time': 22.0,
            'end_time': 6.0,
            'break_minutes': 60,
        })
        self.assertAlmostEqual(overnight.planned_hours, 7.0)

    def test_04_work_schedule_overlap_and_confirm(self):
        """Test AC6 & AC7: Schedule overlap prevention and confirmation workflow."""
        assign = self.Assignment.create({
            'employee_id': self.employee.id,
            'franchise_id': self.store1.id,
            'state': 'working',
        })

        sched1 = self.Schedule.create({
            'franchise_id': self.store1.id,
            'assignment_id': assign.id,
            'work_date': date(2026, 9, 15),
            'shift_template_id': self.shift_morning.id,
        })
        sched1._onchange_calculate_planned_times()
        sched1.action_confirm()
        self.assertEqual(sched1.state, 'confirmed')

        sched2 = self.Schedule.new({
            'franchise_id': self.store1.id,
            'assignment_id': assign.id,
            'work_date': date(2026, 9, 15),
            'shift_template_id': self.shift_morning.id,
        })
        sched2._onchange_calculate_planned_times()

        with self.assertRaises(ValidationError):
            sched2_real = self.Schedule.create({
                'franchise_id': self.store1.id,
                'assignment_id': assign.id,
                'work_date': date(2026, 9, 15),
                'shift_template_id': self.shift_morning.id,
                'planned_start': sched1.planned_start,
                'planned_end': sched1.planned_end,
                'planned_hours': sched1.planned_hours,
            })
            sched2_real._check_overlapping_schedules()

    def test_05_expense_creation_and_confirm(self):
        """Test AC8: Expense creation, positive amount constraint, and confirmation."""
        expense = self.Expense.create({
            'franchise_id': self.store1.id,
            'category_id': self.expense_cat.id,
            'amount': 500000.0,
            'description': 'Electricity bill for September 2026',
        })
        self.assertEqual(expense.state, 'draft')
        expense.action_confirm()
        self.assertEqual(expense.state, 'confirmed')
        self.assertTrue(expense.confirmed_by_id)

        with self.assertRaises(ValidationError):
            self.Expense.create({
                'franchise_id': self.store1.id,
                'category_id': self.expense_cat.id,
                'amount': -100.0,
                'description': 'Negative amount expense',
            })

    def test_06_revenue_idempotency_and_zero_amount(self):
        """Test AC9 & AC10: Idempotent daily revenue constraint and zero amount revenue declaration."""
        rev1 = self.Revenue.create({
            'franchise_id': self.store1.id,
            'business_date': date(2026, 9, 11),
            'amount': 15000000.0,
        })
        rev1.action_confirm()
        self.assertEqual(rev1.state, 'confirmed')

        # Duplicate business date at same store triggers ValidationError
        with self.assertRaises(ValidationError):
            self.Revenue.create({
                'franchise_id': self.store1.id,
                'business_date': date(2026, 9, 11),
                'amount': 20000000.0,
            })

        # Zero revenue declaration for stormy/closed day is valid
        rev_zero = self.Revenue.create({
            'franchise_id': self.store2.id,
            'business_date': date(2026, 9, 11),
            'amount': 0.0,
            'note': 'Closed due to typhoon',
        })
        self.assertEqual(rev_zero.amount, 0.0)
        rev_zero.action_confirm()
        self.assertEqual(rev_zero.state, 'confirmed')

    def test_07_store_master_smart_button_counts(self):
        """Test Store Master smart buttons count computation."""
        assign = self.Assignment.create({
            'employee_id': self.employee.id,
            'franchise_id': self.store1.id,
            'state': 'working',
        })
        sched = self.Schedule.create({
            'franchise_id': self.store1.id,
            'assignment_id': assign.id,
            'work_date': date(2026, 9, 20),
            'shift_template_id': self.shift_morning.id,
            'planned_start': Date.context_today(self),
            'planned_end': Date.context_today(self),
            'planned_hours': 8.0,
        })
        exp = self.Expense.create({
            'franchise_id': self.store1.id,
            'category_id': self.expense_cat.id,
            'amount': 250000.0,
            'description': 'Store maintenance',
        })
        rev = self.Revenue.create({
            'franchise_id': self.store1.id,
            'business_date': date(2026, 9, 20),
            'amount': 12000000.0,
        })

        self.store1._compute_operation_counts()
        self.assertEqual(self.store1.employee_count, 1)
        self.assertEqual(self.store1.work_schedule_count, 1)
        self.assertEqual(self.store1.operation_expense_count, 1)
        self.assertEqual(self.store1.operation_revenue_count, 1)

    def test_08_assignment_auto_compute_state_by_date(self):
        """Test auto computation of assignment state based on start and end dates."""
        today = Date.context_today(self)

        # Future start date -> scheduled
        future_assign = self.Assignment.create({
            'employee_id': self.employee.id,
            'franchise_id': self.store1.id,
            'date_from': today + timedelta(days=5),
        })
        self.assertEqual(future_assign.state, 'scheduled')

        # Past start date with no end date -> working
        active_assign = self.Assignment.create({
            'employee_id': self.employee.id,
            'franchise_id': self.store2.id,
            'date_from': today - timedelta(days=5),
        })
        self.assertEqual(active_assign.state, 'working')

        # Past end date -> ended
        ended_assign = self.Assignment.create({
            'employee_id': self.employee.id,
            'franchise_id': self.store1.id,
            'date_from': today - timedelta(days=30),
            'date_to': today - timedelta(days=1),
        })
        self.assertEqual(ended_assign.state, 'ended')

    def test_09_action_get_work_schedules_defaults(self):
        """Test action_get_work_schedules returns smallest ID store and this week filter context."""
        action = self.Schedule.action_get_work_schedules()
        self.assertIn('context', action)
        self.assertEqual(action['context'].get('search_default_filter_this_week'), 1)
        smallest_store = self.env['wujia.franchise.management'].search([('active', '=', True)], order='id asc', limit=1)
        self.assertEqual(action['context'].get('search_default_franchise_id'), smallest_store.id)
