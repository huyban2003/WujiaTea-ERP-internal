from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError

try:
    from psycopg2 import errors as pg_errors
    LockNotAvailable = pg_errors.LockNotAvailable
except Exception:  # pragma: no cover
    LockNotAvailable = Exception

REG_STATE = [
    ('submitted', 'Đã gửi'),
    ('confirmed', 'Đã duyệt'),
    ('rejected', 'Từ chối'),
    ('cancelled', 'Đã hủy'),
]


class WujiaExamRegistration(models.Model):
    """Phiếu đăng ký thi của 1 cửa hàng cho 1 kỳ thi — nhiều nhân sự / phiếu.

    Sprint M: rework từ skeleton (user×schedule) sang phiếu-đa-nhân-sự gắn
    session. Giữ `_name` để portal (demo) không lỗi bind.
    """

    _name = 'wujia.exam.registration'
    _description = 'Wujia Exam Registration'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'request_date desc, id desc'

    name = fields.Char(
        string='Mã phiếu', required=True, copy=False,
        readonly=True, default=lambda self: _('New'), tracking=True,
    )
    session_id = fields.Many2one(
        'wujia.exam.session', string='Kỳ thi', required=True,
        ondelete='restrict', index=True, tracking=True,
    )
    course_id = fields.Many2one(
        'wujia.exam.course', string='Khóa thi',
        related='session_id.course_id', store=True, index=True,
    )
    franchise_id = fields.Many2one(
        'wujia.franchise.management', string='Cửa hàng', required=True,
        default=lambda self: self._default_franchise(),
        ondelete='restrict', index=True, tracking=True,
    )
    requester_user_id = fields.Many2one(
        'res.users', string='Người đăng ký',
        default=lambda self: self.env.user, readonly=True, index=True,
    )
    member_id = fields.Many2one(
        'wujia.franchise.member', string='Nhân sự phụ trách',
        domain="[('franchise_id', '=', franchise_id)]",
        ondelete='set null',
        help='Tùy chọn — thành viên cửa hàng đứng tên phiếu.',
    )
    request_date = fields.Datetime(
        string='Ngày đăng ký', default=fields.Datetime.now, readonly=True,
    )
    line_ids = fields.One2many(
        'wujia.exam.registration.line', 'registration_id',
        string='Danh sách dự thi',
    )
    participant_count = fields.Integer(
        string='Số nhân sự', compute='_compute_participant_count', store=True,
    )
    state = fields.Selection(
        REG_STATE, string='Trạng thái', default='submitted',
        required=True, index=True, tracking=True,
    )
    confirmed_by_id = fields.Many2one('res.users', string='Người duyệt', readonly=True)
    confirmed_date = fields.Datetime(string='Ngày duyệt', readonly=True)
    rejected_by_id = fields.Many2one('res.users', string='Người từ chối', readonly=True)
    rejected_date = fields.Datetime(string='Ngày từ chối', readonly=True)
    cancelled_by_id = fields.Many2one('res.users', string='Người hủy', readonly=True)
    cancelled_date = fields.Datetime(string='Ngày hủy', readonly=True)
    reject_reason = fields.Text(string='Lý do từ chối', tracking=True)
    cancellation_reason = fields.Text(string='Lý do hủy', tracking=True)
    note = fields.Text(string='Ghi chú')

    @api.model
    def _default_franchise(self):
        fids = self.env.user._get_accessible_franchise_ids()
        return fids[0] if fids else False

    @api.depends('line_ids')
    def _compute_participant_count(self):
        for rec in self:
            rec.participant_count = len(rec.line_ids)

    # ------------------------------------------------------------ constraints
    @api.constrains('line_ids', 'state', 'session_id')
    def _check_participant_bounds(self):
        for rec in self.filtered(lambda r: r.state in ('submitted', 'confirmed')):
            n = len(rec.line_ids)
            if n < 1:
                raise ValidationError(_(
                    "Phiếu '%s' cần ít nhất 1 nhân sự dự thi.", rec.name))
            max_p = rec.session_id.max_participants_per_registration or 0
            if max_p and n > max_p:
                raise ValidationError(_(
                    "Phiếu '%s': tối đa %s nhân sự / phiếu.", rec.name, max_p))

    # ------------------------------------------------------------ capacity lock
    def _lock_and_check_capacity(self):
        """Khóa row kỳ thi (NOWAIT) + đếm lại giữ-chỗ trong transaction.

        Chống 2 phiếu submit đồng thời vượt sức chứa (perf 1500 user: 1 lock +
        1 read_group, không loop per-record).
        """
        sessions = self.mapped('session_id')
        if not sessions:
            return
        try:
            self.env.cr.execute(
                "SELECT id FROM wujia_exam_session WHERE id IN %s FOR UPDATE NOWAIT",
                (tuple(sessions.ids),),
            )
        except LockNotAvailable:
            raise UserError(_(
                "Hệ thống đang xử lý đăng ký khác cho kỳ thi này, vui lòng thử lại."))
        # Recount reserved participants per session (submitted + confirmed).
        sessions.invalidate_recordset(
            ['reserved_participant_count', 'available_participant_count'])
        for sess in sessions:
            if sess.reserved_participant_count > sess.capacity:
                raise ValidationError(_(
                    "Kỳ thi '%s' đã hết chỗ (sức chứa %s, đã giữ %s).",
                    sess.name, sess.capacity, sess.reserved_participant_count))

    def _check_booking_allowed(self):
        for rec in self:
            sess = rec.session_id
            if sess.state != 'open':
                raise ValidationError(_(
                    "Kỳ thi '%s' không mở đăng ký.", sess.name))
            if sess.registration_deadline and \
                    fields.Datetime.now() > sess.registration_deadline:
                raise ValidationError(_(
                    "Kỳ thi '%s' đã quá hạn đăng ký.", sess.name))

    # ------------------------------------------------------------ sequence
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('name') or vals['name'] == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'wujia.exam.registration') or _('New')
        records = super().create(vals_list)
        booking = records.filtered(lambda r: r.state == 'submitted')
        booking._check_booking_allowed()
        booking._lock_and_check_capacity()
        return records

    def write(self, vals):
        res = super().write(vals)
        if {'line_ids', 'session_id', 'state'} & set(vals):
            self.filtered(
                lambda r: r.state in ('submitted', 'confirmed'))._lock_and_check_capacity()
        return res

    # ------------------------------------------------------------ workflow
    def action_confirm(self):
        for rec in self:
            if rec.state != 'submitted':
                raise ValidationError(_("Chỉ duyệt phiếu đang ở trạng thái Đã gửi."))
            rec.write({
                'state': 'confirmed',
                'confirmed_by_id': self.env.uid,
                'confirmed_date': fields.Datetime.now(),
            })
            rec.message_post(body=_("Phiếu đăng ký đã được duyệt."))

    def action_reject(self):
        for rec in self:
            if rec.state not in ('submitted', 'confirmed'):
                raise ValidationError(_("Phiếu này không thể từ chối."))
            if not rec.reject_reason:
                raise ValidationError(_("Nhập lý do từ chối trước khi từ chối."))
            rec.write({
                'state': 'rejected',
                'rejected_by_id': self.env.uid,
                'rejected_date': fields.Datetime.now(),
            })
            rec.message_post(body=_("Phiếu bị từ chối: %s", rec.reject_reason))

    def action_cancel(self):
        for rec in self:
            if rec.state in ('rejected', 'cancelled'):
                raise ValidationError(_("Phiếu này không thể hủy."))
            if rec.session_id.results_published:
                raise ValidationError(_(
                    "Không thể hủy phiếu sau khi kỳ thi đã công bố kết quả."))
            if not rec.cancellation_reason:
                raise ValidationError(_("Nhập lý do hủy trước khi hủy phiếu."))
            rec.write({
                'state': 'cancelled',
                'cancelled_by_id': self.env.uid,
                'cancelled_date': fields.Datetime.now(),
            })
            rec.message_post(body=_("Phiếu đăng ký đã bị hủy: %s",
                                    rec.cancellation_reason))
