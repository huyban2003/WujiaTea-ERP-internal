import logging
from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class WujiaFranchiseContract(models.Model):
    _name = 'wujia.franchise.contract'
    _description = 'Franchise Contract'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'start_date desc, id desc'

    name = fields.Char(
        string='Contract Number',
        required=True,
        tracking=True,
        default=lambda self: self.env['ir.sequence'].next_by_code('wujia.franchise.contract') or '/',
        help='Franchise contract number (e.g. FC/2026/0001).',
    )
    franchise_id = fields.Many2one(
        'wujia.franchise.management',
        string='Franchise Store',
        required=True,
        ondelete='cascade',
        index=True,
        tracking=True,
    )
    start_date = fields.Date(
        string='Start Date',
        required=True,
        tracking=True,
        default=fields.Date.context_today,
    )
    end_date = fields.Date(
        string='End Date',
        required=True,
        tracking=True,
    )
    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('effective', 'Effective'),
            ('expired', 'Expired'),
            ('cancelled', 'Cancelled'),
        ],
        string='Status',
        default='draft',
        required=True,
        tracking=True,
    )
    note = fields.Text(string='Internal Note', tracking=True)
    attachment_ids = fields.Many2many(
        'ir.attachment',
        string='Contract Attachments',
        tracking=True,
        help='Scanned contract files or addendums.',
    )

    active = fields.Boolean(default=True)

    def action_confirm(self):
        """Confirm contract: check dates and calculate state based on start and end dates."""
        today = fields.Date.context_today(self)
        for rec in self:
            rec._check_dates()
            rec._check_no_overlap()
            if rec.end_date and rec.end_date < today:
                rec.state = 'expired'
            elif rec.start_date and rec.end_date and rec.start_date <= today <= rec.end_date:
                rec.state = 'effective'
            else:
                rec.state = 'effective'

    def action_cancel(self):
        """Cancel contract."""
        for rec in self:
            rec.state = 'cancelled'

    def action_draft(self):
        """Set contract back to draft."""
        for rec in self:
            rec.state = 'draft'

    @api.constrains('start_date', 'end_date')
    def _check_dates(self):
        for rec in self:
            if rec.start_date and rec.end_date and rec.end_date < rec.start_date:
                raise ValidationError(_("End date must be greater than or equal to start date."))

    @api.constrains('franchise_id', 'start_date', 'end_date', 'state', 'active')
    def _check_no_overlap(self):
        """Check contract date range overlap for the same store.
        Catches all 4 nested/overlapping cases:
        1. [ (  ) ] : New contract completely encloses existing contract (Start_new <= Start_old AND End_new >= End_old)
        2. [ (  ] ) : New contract starts inside existing contract (Start_old <= Start_new <= End_old)
        3. ( [  ] ) : New contract is completely inside existing contract (Start_old <= Start_new AND End_new <= End_old)
        4. ( [  ) ] : New contract ends inside existing contract (Start_old <= End_new <= End_old)
        """
        for rec in self:
            if not rec.franchise_id or not rec.start_date or not rec.end_date:
                continue
            if rec.state == 'cancelled' or not rec.active:
                continue
            # General mathematical condition for overlapping closed intervals [S1, E1] and [S2, E2]:
            # (Start_old <= End_new) AND (End_old >= Start_new)
            # Detailed breakdown into 4 nested cases:
            s_new, e_new = rec.start_date, rec.end_date
            domain = [
                ('id', '!=', rec.id),
                ('franchise_id', '=', rec.franchise_id.id),
                ('state', '!=', 'cancelled'),
                ('active', '=', True),
                '|', '|', '|',
                # Case 2 & 3: New start date falls within [Start_old, End_old]
                '&', ('start_date', '<=', s_new), ('end_date', '>=', s_new),
                # Case 3 & 4: New end date falls within [Start_old, End_old]
                '&', ('start_date', '<=', e_new), ('end_date', '>=', e_new),
                # Case 1: New contract completely encloses existing contract [ ( ) ]
                '&', ('start_date', '>=', s_new), ('end_date', '<=', e_new),
                # Case 3: Existing contract completely encloses new contract ( [ ] )
                '&', ('start_date', '<=', s_new), ('end_date', '>=', e_new),
            ]
            if self.search_count(domain) > 0:
                raise ValidationError(_(
                    "Contract date range (%s to %s) overlaps with an existing active contract of store '%s'."
                ) % (rec.start_date, rec.end_date, rec.franchise_id.display_name))

    def write(self, vals):
        restricted_fields = {'name', 'franchise_id', 'start_date', 'end_date', 'note', 'attachment_ids'}
        if any(f in vals for f in restricted_fields):
            for rec in self:
                if rec.state not in ('draft', 'cancelled'):
                    raise UserError(_(
                        "Contracts in '%s' status cannot be edited. Only status changes (such as cancellation) are allowed for effective/expired contracts."
                    ) % rec.state)
        return super().write(vals)

    def unlink(self):
        for rec in self:
            if rec.state in ('effective', 'expired'):
                raise UserError(_(
                    "Active or historical contracts (%s) cannot be deleted. Please cancel or archive them instead."
                ) % rec.name)
        return super().unlink()


