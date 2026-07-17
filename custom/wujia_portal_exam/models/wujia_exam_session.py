from datetime import datetime, timedelta

import pytz

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

DEFAULT_TZ = 'Asia/Ho_Chi_Minh'


class WujiaExamSession(models.Model):
    """Kỳ thi — 1 lần tổ chức của 1 khóa thi tại 1 ca giờ, có sức chứa."""

    _name = 'wujia.exam.session'
    _description = 'Wujia Exam Session'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'exam_date desc, id desc'

    name = fields.Char(
        string='Mã kỳ thi', required=True, copy=False,
        readonly=True, default=lambda self: _('New'), tracking=True,
    )
    course_id = fields.Many2one(
        'wujia.exam.course', string='Khóa thi', required=True,
        domain="[('state', '=', 'published')]",
        ondelete='restrict', index=True, tracking=True,
    )
    exam_date = fields.Date(string='Ngày thi', required=True, index=True, tracking=True)
    time_slot_id = fields.Many2one(
        'wujia.exam.time.slot', string='Ca thi', required=True,
        ondelete='restrict', tracking=True,
    )
    start_datetime = fields.Datetime(
        string='Bắt đầu', compute='_compute_datetimes', store=True,
    )
    end_datetime = fields.Datetime(
        string='Kết thúc', compute='_compute_datetimes', store=True,
    )
    location = fields.Char(string='Địa điểm')
    capacity = fields.Integer(string='Sức chứa (người)', default=20, tracking=True)
    max_participants_per_registration = fields.Integer(
        string='Số nhân sự tối đa / phiếu', default=4,
    )
    registration_deadline = fields.Datetime(string='Hạn đăng ký', tracking=True)
    registration_ids = fields.One2many(
        'wujia.exam.registration', 'session_id', string='Phiếu đăng ký',
    )
    line_ids = fields.One2many(
        'wujia.exam.registration.line', 'session_id', string='Thí sinh',
        help='Toàn bộ thí sinh của kỳ thi — nhập kết quả trực tiếp tại đây.',
    )
    registration_count = fields.Integer(
        string='Số phiếu', compute='_compute_participant_counts',
    )
    reserved_participant_count = fields.Integer(
        string='Đã giữ chỗ', compute='_compute_participant_counts', store=True,
    )
    available_participant_count = fields.Integer(
        string='Còn trống', compute='_compute_participant_counts', store=True,
    )
    state = fields.Selection(
        [('draft', 'Nháp'), ('open', 'Mở đăng ký'), ('closed', 'Đóng đăng ký'),
         ('done', 'Đã thi xong'), ('cancelled', 'Đã hủy')],
        string='Trạng thái', default='draft', required=True, index=True,
        tracking=True,
    )
    results_published = fields.Boolean(
        string='Đã công bố kết quả', readonly=True, copy=False, tracking=True,
    )
    results_published_by_id = fields.Many2one(
        'res.users', string='Người công bố KQ', readonly=True, copy=False,
    )
    results_published_date = fields.Datetime(
        string='Ngày công bố KQ', readonly=True, copy=False,
    )
    cancellation_reason = fields.Text(string='Lý do hủy')
    note = fields.Text(string='Ghi chú')

    _check_capacity_positive = models.Constraint(
        'CHECK(capacity >= 1)', 'Sức chứa phải ≥ 1.',
    )

    # ------------------------------------------------------------ computes
    @api.depends('exam_date', 'time_slot_id.time_from', 'time_slot_id.time_to')
    def _compute_datetimes(self):
        tz = pytz.timezone(self.env.user.tz or DEFAULT_TZ)
        for rec in self:
            if not rec.exam_date or not rec.time_slot_id:
                rec.start_datetime = rec.end_datetime = False
                continue
            rec.start_datetime = rec._local_to_utc(tz, rec.time_slot_id.time_from)
            rec.end_datetime = rec._local_to_utc(tz, rec.time_slot_id.time_to)

    def _local_to_utc(self, tz, float_hour):
        hour = int(float_hour)
        minute = int(round((float_hour - hour) * 60))
        if hour >= 24:
            hour, minute = 23, 59
        naive = datetime(self.exam_date.year, self.exam_date.month,
                         self.exam_date.day, hour, minute)
        return tz.localize(naive).astimezone(pytz.utc).replace(tzinfo=None)

    @api.depends('capacity', 'registration_ids.state',
                 'registration_ids.participant_count')
    def _compute_participant_counts(self):
        reserved = {}
        counts = {}
        if self.ids:
            groups = self.env['wujia.exam.registration']._read_group(
                domain=[('session_id', 'in', self.ids),
                        ('state', 'in', ('submitted', 'confirmed'))],
                groupby=['session_id'],
                aggregates=['participant_count:sum', '__count'],
            )
            for sess, part_sum, cnt in groups:
                reserved[sess.id] = part_sum or 0
                counts[sess.id] = cnt
        for rec in self:
            rec.reserved_participant_count = reserved.get(rec.id, 0)
            rec.available_participant_count = (
                rec.capacity - rec.reserved_participant_count)
            rec.registration_count = counts.get(rec.id, 0)

    # ------------------------------------------------------------ defaults
    @api.onchange('course_id')
    def _onchange_course(self):
        if self.course_id:
            self.max_participants_per_registration = (
                self.course_id.max_participants_per_registration)
            slots = self.course_id.time_slot_ids
            if slots and self.time_slot_id not in slots:
                self.time_slot_id = slots[:1]
            return {'domain': {'time_slot_id': [('id', 'in', slots.ids)]}}

    @api.onchange('exam_date', 'time_slot_id', 'course_id')
    def _onchange_deadline(self):
        if self.exam_date and self.time_slot_id and not self.registration_deadline:
            lead = self.course_id.registration_lead_days or 0
            tz = pytz.timezone(self.env.user.tz or DEFAULT_TZ)
            start = self._local_to_utc(tz, self.time_slot_id.time_from)
            self.registration_deadline = start - timedelta(days=lead)

    # ------------------------------------------------------------ constraints
    @api.constrains('time_slot_id', 'course_id')
    def _check_slot_in_course(self):
        for rec in self:
            if rec.time_slot_id and rec.course_id and \
                    rec.time_slot_id not in rec.course_id.time_slot_ids:
                raise ValidationError(_(
                    "Ca thi phải thuộc danh sách ca của khóa thi '%s'.",
                    rec.course_id.name))

    @api.constrains('capacity', 'reserved_participant_count')
    def _check_capacity_ge_reserved(self):
        for rec in self:
            if rec.capacity < rec.reserved_participant_count:
                raise ValidationError(_(
                    "Sức chứa (%s) không được nhỏ hơn số đã giữ chỗ (%s).",
                    rec.capacity, rec.reserved_participant_count))

    @api.constrains('registration_deadline', 'start_datetime')
    def _check_deadline(self):
        for rec in self:
            if rec.registration_deadline and rec.start_datetime and \
                    rec.registration_deadline > rec.start_datetime:
                raise ValidationError(_(
                    "Hạn đăng ký không được sau giờ bắt đầu thi."))

    # ------------------------------------------------------------ sequence
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('name') or vals['name'] == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'wujia.exam.session') or _('New')
        return super().create(vals_list)

    # ------------------------------------------------------------ workflow
    def action_open(self):
        for rec in self:
            if rec.state != 'draft':
                raise ValidationError(_("Chỉ mở đăng ký cho kỳ thi ở trạng thái Nháp."))
            rec.state = 'open'
            rec.message_post(body=_("Kỳ thi đã mở đăng ký."))

    def action_close(self):
        for rec in self:
            if rec.state != 'open':
                raise ValidationError(_("Chỉ đóng kỳ thi đang mở đăng ký."))
            rec.state = 'closed'
            rec.message_post(body=_("Kỳ thi đã đóng đăng ký."))

    def action_mark_done(self):
        for rec in self:
            if rec.state not in ('open', 'closed'):
                raise ValidationError(_("Chỉ hoàn tất kỳ thi đang mở/đóng đăng ký."))
            rec.state = 'done'
            rec.message_post(body=_("Kỳ thi đã hoàn tất."))

    def action_cancel(self):
        for rec in self:
            if rec.state in ('done', 'cancelled'):
                raise ValidationError(_("Kỳ thi này không thể hủy."))
            if not rec.cancellation_reason:
                raise ValidationError(_("Nhập lý do hủy trước khi hủy kỳ thi."))
            rec.state = 'cancelled'
            rec.message_post(body=_("Kỳ thi bị hủy: %s", rec.cancellation_reason))

    def action_publish_results(self):
        for rec in self:
            if rec.state not in ('closed', 'done'):
                raise ValidationError(_(
                    "Chỉ công bố kết quả khi kỳ thi đã đóng đăng ký / hoàn tất."))
            pending_reg = rec.registration_ids.filtered(
                lambda r: r.state == 'submitted')
            if pending_reg:
                raise ValidationError(_(
                    "Còn %s phiếu đăng ký chưa duyệt — xử lý trước khi công bố.",
                    len(pending_reg)))
            confirmed_lines = rec.registration_ids.filtered(
                lambda r: r.state == 'confirmed').mapped('line_ids')
            if any(line.result == 'pending' for line in confirmed_lines):
                raise ValidationError(_(
                    "Còn thí sinh chưa nhập kết quả (Đạt/Không đạt)."))
            rec.write({
                'results_published': True,
                'results_published_by_id': self.env.uid,
                'results_published_date': fields.Datetime.now(),
            })
            rec.message_post(body=_("Đã công bố kết quả kỳ thi."))
