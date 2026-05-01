from odoo import _, api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    franchise_ids = fields.One2many(
        'wujia.franchise.management',
        'partner_id',
        string='Cửa hàng nhượng quyền',
    )
    is_franchise = fields.Boolean(
        string='Là cửa hàng nhượng quyền',
        compute='_compute_is_franchise',
        store=True,
        index=True,
        help='TRUE nếu partner đang được dùng làm contact của ít nhất 1 wujia.franchise.management.',
    )
    franchise_count = fields.Integer(
        string='Số cửa hàng',
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
