from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


REQUEST_TYPE = [
    ('address', 'Address'),
    ('phone', 'Phone number'),
    ('email', 'Email'),
    ('owner_name', 'Store owner name'),
    ('bank_info', 'Bank details'),
    ('representative', 'Representative'),
    ('other', 'Other'),
]

REQUEST_TYPE_FIELD_MAP = {
    'address': 'address',
    'phone': 'phone',
    'email': 'email',
    'owner_name': 'name',
}

STATE = [
    ('draft', 'Draft'),
    ('submitted', 'Submitted'),
    ('reviewing', 'Being reviewed'),
    ('approved', 'Approved'),
    ('rejected', 'Rejected'),
]

PRIORITY = [
    ('normal', 'Normal'),
    ('urgent', 'Urgent'),
]


class WujiaInfoUpdateRequest(models.Model):
    """Yêu cầu cập nhật thông tin cửa hàng nhượng quyền — gửi từ portal,
    HQ duyệt qua chatter backend."""

    _name = 'wujia.info.update.request'
    _description = 'Wujia Info Update Request'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'request_date desc, id desc'

    name = fields.Char(
        string='Request code', readonly=True, copy=False, default='/',
    )
    franchise_id = fields.Many2one(
        'wujia.franchise.management', string='Store',
        required=True, index=True, ondelete='restrict', tracking=True,
    )
    request_type = fields.Selection(
        REQUEST_TYPE, string='Information type',
        required=True, tracking=True,
    )
    field_target = fields.Char(
        string='Target field (free text)',
        help='Technical field name — used when request_type=other.',
    )
    old_value = fields.Text(
        string='Old value',
        compute='_compute_old_value', store=False,
        help='Snapshot taken from the franchise when the form is opened.',
    )
    new_value = fields.Text(
        string='New value', required=True, tracking=True,
    )
    note = fields.Text(string='Notes')
    state = fields.Selection(
        STATE, string='Status',
        default='draft', required=True, index=True, tracking=True,
    )
    priority = fields.Selection(
        PRIORITY, string='Severity', default='normal', tracking=True,
    )
    attachment_ids = fields.Many2many(
        'ir.attachment', 'wujia_info_request_att_rel',
        'request_id', 'attachment_id', string='Supporting documents',
    )
    request_date = fields.Datetime(
        string='Creation date', default=fields.Datetime.now,
        index=True, readonly=True,
    )
    submitted_date = fields.Datetime(
        string='Submission date', readonly=True,
    )
    created_by_user_id = fields.Many2one(
        'res.users', string='Created by',
        default=lambda self: self.env.user, readonly=True, index=True,
    )
    reviewer_id = fields.Many2one(
        'res.users', string='HQ Reviewer',
        domain="[('share', '=', False)]", tracking=True,
    )
    reviewed_date = fields.Datetime(string='Approval date', readonly=True)
    refuse_reason = fields.Text(string='Rejection reason', tracking=True)

    _sql_constraints = [
        ('check_submitted_has_date',
         "CHECK (state = 'draft' OR submitted_date IS NOT NULL)",
         "submitted_date phải có khi state >= submitted."),
    ]

    @api.depends('franchise_id', 'request_type', 'field_target')
    def _compute_old_value(self):
        for rec in self:
            value = ''
            if rec.franchise_id and rec.request_type:
                field_name = REQUEST_TYPE_FIELD_MAP.get(rec.request_type)
                if not field_name and rec.request_type == 'other':
                    field_name = rec.field_target
                if field_name and field_name in rec.franchise_id._fields:
                    value = rec.franchise_id[field_name] or ''
            rec.old_value = str(value)

    @api.constrains('request_type', 'field_target')
    def _check_other_field_target(self):
        for rec in self:
            if rec.request_type == 'other' and not rec.field_target:
                raise ValidationError(_(
                    "Khi chọn 'Khác' phải nhập tên field cần đổi."
                ))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('name') or vals['name'] == '/':
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'wujia.info.update.request'
                ) or '/'
        return super().create(vals_list)

    def action_submit(self):
        for rec in self:
            if rec.state != 'draft':
                continue
            rec.write({
                'state': 'submitted',
                'submitted_date': fields.Datetime.now(),
            })
            rec.message_post(
                body=_("Yêu cầu cập nhật thông tin đã được gửi từ portal."),
                subtype_xmlid='mail.mt_comment',
            )

    def action_start_review(self):
        for rec in self:
            if rec.state == 'submitted':
                rec.write({'state': 'reviewing', 'reviewer_id': self.env.user.id})

    def action_approve(self):
        for rec in self:
            rec.write({
                'state': 'approved',
                'reviewer_id': self.env.user.id,
                'reviewed_date': fields.Datetime.now(),
            })

    def action_reject(self):
        for rec in self:
            rec.write({
                'state': 'rejected',
                'reviewer_id': self.env.user.id,
                'reviewed_date': fields.Datetime.now(),
            })

    def action_cancel(self):
        """User huỷ yêu cầu (chỉ khi state=draft hoặc submitted)."""
        for rec in self:
            if rec.state not in ('draft', 'submitted'):
                raise ValidationError(_(
                    "Chỉ có thể huỷ yêu cầu ở trạng thái Nháp/Đã gửi."
                ))
            rec.write({'state': 'rejected', 'refuse_reason': _('User huỷ')})
