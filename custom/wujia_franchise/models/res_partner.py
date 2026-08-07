from odoo import _, api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    franchise_ids = fields.One2many(
        'wujia.franchise.management',
        'partner_id',
        string='Franchise store',
    )
    is_franchise = fields.Boolean(
        string='Is a franchise store',
        compute='_compute_is_franchise',
        store=True,
        index=True,
        help='TRUE when the partner is used as the contact of at least one wujia.franchise.management.',
    )
    franchise_count = fields.Integer(
        string='Store count',
        compute='_compute_franchise_count',
    )

    @api.depends('franchise_ids')
    def _compute_is_franchise(self):
        for rec in self:
            rec.is_franchise = bool(rec.franchise_ids)

    @api.depends('franchise_ids')
    def _compute_franchise_count(self):
        for rec in self:
            rec.franchise_count = len(rec.franchise_ids)

    def action_view_franchises(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Cửa hàng nhượng quyền của %s', self.display_name),
            'res_model': 'wujia.franchise.management',
            'view_mode': 'list,form',
            'domain': [('partner_id', '=', self.id)],
            'context': {'default_partner_id': self.id},
        }
