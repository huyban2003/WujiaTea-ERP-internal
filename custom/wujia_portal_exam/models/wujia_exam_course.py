from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class WujiaExamCourse(models.Model):
    """Khóa thi / chương trình kiểm tra kiến thức (vd Pha chế, Quản lý ca)."""

    _name = 'wujia.exam.course'
    _description = 'Wujia Exam Course'
    _order = 'name, id'

    name = fields.Char(string='Tên khóa thi', required=True)
    code = fields.Char(
        string='Mã khóa', required=True, copy=False,
        readonly=True, default=lambda self: _('New'),
    )
    description = fields.Html(string='Mô tả')
    time_slot_ids = fields.Many2many(
        'wujia.exam.time.slot', 'wujia_exam_course_slot_rel',
        'course_id', 'slot_id', string='Ca thi áp dụng',
    )
    max_participants_per_registration = fields.Integer(
        string='Số nhân sự tối đa / phiếu', default=4,
    )
    registration_lead_days = fields.Integer(
        string='Hạn đăng ký trước (ngày)', default=0,
        help='Số ngày trước kỳ thi mà hệ thống đóng đăng ký.',
    )
    registration_horizon_days = fields.Integer(
        string='Mở đăng ký trong (ngày)', default=60,
        help='Chỉ cho phép đăng ký các kỳ thi trong khoảng ngày này kể từ hôm nay.',
    )
    session_ids = fields.One2many(
        'wujia.exam.session', 'course_id', string='Kỳ thi',
    )
    session_count = fields.Integer(
        string='Số kỳ thi', compute='_compute_session_count',
    )
    state = fields.Selection(
        [('draft', 'Nháp'), ('published', 'Đã phát hành')],
        string='Trạng thái', default='draft', required=True, index=True,
    )
    active = fields.Boolean(default=True)

    _uniq_code = models.Constraint(
        'unique(code)', 'Mã khóa thi phải duy nhất.',
    )

    @api.depends('session_ids')
    def _compute_session_count(self):
        data = {}
        if self.ids:
            groups = self.env['wujia.exam.session']._read_group(
                domain=[('course_id', 'in', self.ids)],
                groupby=['course_id'], aggregates=['__count'],
            )
            data = {c.id: n for c, n in groups}
        for rec in self:
            rec.session_count = data.get(rec.id, 0)

    @api.constrains('max_participants_per_registration',
                    'registration_lead_days', 'registration_horizon_days')
    def _check_config(self):
        for rec in self:
            if rec.max_participants_per_registration <= 0:
                raise ValidationError(_("Số nhân sự tối đa / phiếu phải > 0."))
            if rec.registration_lead_days < 0:
                raise ValidationError(_("Hạn đăng ký trước không được âm."))
            if rec.registration_horizon_days <= 0:
                raise ValidationError(_("Số ngày mở đăng ký phải > 0."))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('code') or vals['code'] == _('New'):
                vals['code'] = self.env['ir.sequence'].next_by_code(
                    'wujia.exam.course') or _('New')
        return super().create(vals_list)

    def action_publish(self):
        for rec in self:
            if not rec.time_slot_ids:
                raise ValidationError(_(
                    "Khóa thi '%s' cần ít nhất 1 ca thi trước khi phát hành.",
                    rec.name))
            if rec.max_participants_per_registration <= 0:
                raise ValidationError(_("Số nhân sự tối đa / phiếu phải > 0."))
            rec.state = 'published'

    def action_reset_to_draft(self):
        self.write({'state': 'draft'})
