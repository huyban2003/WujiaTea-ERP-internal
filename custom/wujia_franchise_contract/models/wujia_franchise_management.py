import logging
from datetime import timedelta
from odoo import _, api, fields, models

_logger = logging.getLogger(__name__)


class WujiaFranchiseManagement(models.Model):
    _inherit = 'wujia.franchise.management'

    contract_ids = fields.One2many(
        'wujia.franchise.contract',
        'franchise_id',
        string='Franchise Contracts',
    )
    contract_count = fields.Integer(
        string='Contract Count',
        compute='_compute_contract_count',
    )
    current_contract_id = fields.Many2one(
        'wujia.franchise.contract',
        string='Current Contract',
        compute='_compute_current_contract',
        store=True,
    )
    franchise_start_date = fields.Date(
        string='Franchise Start Date',
        compute='_compute_contract_dates',
        store=True,
        readonly=True,
        required=False,
        tracking=True,
    )
    franchise_end_date = fields.Date(
        string='Franchise End Date',
        compute='_compute_contract_dates',
        store=True,
        readonly=True,
        required=False,
        tracking=True,
    )

    @api.depends('contract_ids', 'contract_ids.active')
    def _compute_contract_count(self):
        for rec in self:
            rec.contract_count = len(rec.contract_ids.filtered(lambda c: c.active))

    @api.depends('contract_ids', 'contract_ids.start_date', 'contract_ids.end_date', 'contract_ids.state', 'contract_ids.active')
    def _compute_current_contract(self):
        today = fields.Date.context_today(self)
        for rec in self:
            # Only consider confirmed active/expired contracts (exclude draft and cancelled)
            valid = rec.contract_ids.filtered(lambda c: c.active and c.state in ('effective', 'expired'))
            effective = valid.filtered(lambda c: c.start_date and c.end_date and c.start_date <= today <= c.end_date)
            if effective:
                rec.current_contract_id = effective[0]
            elif valid:
                rec.current_contract_id = valid.sorted(key=lambda c: (c.start_date or fields.Date.today(), c.id), reverse=True)[0]
            else:
                rec.current_contract_id = False

    @api.depends('current_contract_id', 'current_contract_id.start_date', 'current_contract_id.end_date')
    def _compute_contract_dates(self):
        for rec in self:
            if rec.current_contract_id:
                rec.franchise_start_date = rec.current_contract_id.start_date
                rec.franchise_end_date = rec.current_contract_id.end_date
            else:
                rec.franchise_start_date = False
                rec.franchise_end_date = False


    def action_view_contracts(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Contracts of %s', self.display_name),
            'res_model': 'wujia.franchise.contract',
            'view_mode': 'list,form',
            'domain': [('franchise_id', '=', self.id)],
            'context': {'default_franchise_id': self.id},
        }

    @api.model
    def _migrate_legacy_franchise_contracts(self):
        """One-time migration helper: Create contract records for legacy stores upon module installation."""
        Param = self.env['ir.config_parameter'].sudo()
        if Param.get_param('wujia_franchise_contract.legacy_migrated'):
            _logger.info("Legacy franchise contract migration has already been executed. Skipping.")
            return

        Contract = self.env['wujia.franchise.contract']
        today = fields.Date.context_today(self)
        # Pure ORM search: fetch all stores including inactive ones
        stores = self.with_context(active_test=False).search([])
        for store in stores:
            # ORM check: create at most 1 contract if store has legacy dates and no contracts
            if not store.contract_ids and (store.franchise_start_date or store.franchise_end_date):
                start = store.franchise_start_date or today
                end = store.franchise_end_date or (start + timedelta(days=365))
                if end < start:
                    end = start + timedelta(days=365)
                state = 'expired' if end < today else 'effective'
                Contract.create({
                    'name': f'HD-{store.code or store.id}',
                    'franchise_id': store.id,
                    'start_date': start,
                    'end_date': end,
                    'state': state,
                })

        # Set system parameter flag so this migration never runs again
        Param.set_param('wujia_franchise_contract.legacy_migrated', 'True')

    @api.model
    def _cron_update_contract_states(self):
        """Daily cron job: Update state of effective contracts that reached their end date to 'expired'."""
        today = fields.Date.context_today(self)
        Contract = self.env['wujia.franchise.contract']
        expired_contracts = Contract.search([
            ('state', '=', 'effective'),
            ('end_date', '<', today),
        ])
        if expired_contracts:
            expired_contracts.write({'state': 'expired'})
            _logger.info("Cron updated %s contracts to 'expired' status.", len(expired_contracts))



