# -*- coding: utf-8 -*-
from odoo import api, fields, models


class WujiaFranchiseManagement(models.Model):
    _inherit = 'wujia.franchise.management'

    employee_assignment_ids = fields.One2many(
        'wujia.franchise.employee.assignment',
        'franchise_id',
        string='Employee Assignments',
    )
    employee_count = fields.Integer(
        string='Employee Count',
        compute='_compute_operation_counts',
    )
    work_schedule_count = fields.Integer(
        string='Schedule Count',
        compute='_compute_operation_counts',
    )
    operation_expense_count = fields.Integer(
        string='Expense Count',
        compute='_compute_operation_counts',
    )
    operation_revenue_count = fields.Integer(
        string='Revenue Count',
        compute='_compute_operation_counts',
    )

    def _compute_operation_counts(self):
        Assignment = self.env['wujia.franchise.employee.assignment']
        Schedule = self.env['wujia.franchise.work.schedule']
        Expense = self.env['wujia.franchise.expense']
        Revenue = self.env['wujia.franchise.revenue']

        for store in self:
            store.employee_count = Assignment.search_count([
                ('franchise_id', '=', store.id),
                ('state', '=', 'working'),
            ])
            store.work_schedule_count = Schedule.search_count([
                ('franchise_id', '=', store.id),
            ])
            store.operation_expense_count = Expense.search_count([
                ('franchise_id', '=', store.id),
            ])
            store.operation_revenue_count = Revenue.search_count([
                ('franchise_id', '=', store.id),
            ])

    def action_view_store_employees(self):
        self.ensure_one()
        action = self.env.ref('wujia_franchise_operations.action_wujia_franchise_employee_assignment').read()[0]
        action['domain'] = [('franchise_id', '=', self.id)]
        action['context'] = {'default_franchise_id': self.id}
        return action

    def action_view_store_schedules(self):
        self.ensure_one()
        action = self.env.ref('wujia_franchise_operations.action_wujia_franchise_work_schedule').read()[0]
        action['domain'] = [('franchise_id', '=', self.id)]
        action['context'] = {'default_franchise_id': self.id}
        return action

    def action_view_store_expenses(self):
        self.ensure_one()
        action = self.env.ref('wujia_franchise_operations.action_wujia_franchise_expense').read()[0]
        action['domain'] = [('franchise_id', '=', self.id)]
        action['context'] = {'default_franchise_id': self.id}
        return action

    def action_view_store_revenues(self):
        self.ensure_one()
        action = self.env.ref('wujia_franchise_operations.action_wujia_franchise_revenue').read()[0]
        action['domain'] = [('franchise_id', '=', self.id)]
        action['context'] = {'default_franchise_id': self.id}
        return action
