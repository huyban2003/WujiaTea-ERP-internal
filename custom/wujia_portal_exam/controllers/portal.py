"""Wujia portal — Exam Schedule controller.

Routes:
- GET  /portal/exam                          schedule list
- GET  /portal/exam/my                       my registrations
- GET  /portal/exam/result                   results
- GET  /portal/exam/schedule/<int>           schedule detail
- POST /portal/exam/register        (json)   register (race-safe)
- POST /portal/exam/cancel/<int>    (json)   cancel registration

Race-safety: register dùng SELECT ... FOR UPDATE để lock schedule row
trước khi count → tránh oversell khi 100 user click cùng lúc.
"""
import calendar as _calendar
import logging

from odoo import fields, http
from odoo.http import request

from odoo.addons.wujia_portal_base.controllers.portal import (
    get_active_franchise_id,
    get_active_franchise_ids_filter,
)

_logger = logging.getLogger(__name__)

PAGE_SIZE = 20

SCHEDULE_LABELS = {
    'open': ('Đang mở', 'wujia-badge-info'),
    'closed': ('Đã đóng', 'wujia-badge-muted'),
    'done': ('Đã thi xong', 'wujia-badge-success'),
    'cancelled': ('Đã hủy', 'wujia-badge-danger'),
}

REG_LABELS = {
    'registered': ('Đã đăng ký', 'wujia-badge-info'),
    'checked_in': ('Đã có mặt', 'wujia-badge-success'),
    'cancelled': ('Đã hủy', 'wujia-badge-danger'),
}

# --------------------------------------------------------------------------- #
# UI-only demo data (Sprint 26 — mobile "Đăng ký thi" theo Figma #4755:2).
# Backend đa-nhân-sự / khung giờ / kết quả-theo-người là Phase 2 → hardcode để
# khớp Figma 100%. s0 fallback về đây khi user chưa có đăng ký thật.
# --------------------------------------------------------------------------- #
_WEEKDAYS_VN = ['Thứ 2', 'Thứ 3', 'Thứ 4', 'Thứ 5', 'Thứ 6', 'Thứ 7', 'Chủ nhật']

DEMO_EXAM_ITEMS = [
    {'title': 'Đăng ký thi lại', 'date_label': 'Thứ 5, 02/07/2026 • 08:20',
     'meta': '3 nhân sự', 'status': 'Đã đăng ký', 'badge': 'wujia-badge-info',
     'link': '/portal/exam/registration/1'},
    {'title': 'Thi pha chế định kỳ', 'date_label': 'Thứ 7, 11/07/2026 • 13:00',
     'meta': '2 nhân sự', 'status': 'Chờ duyệt', 'badge': 'wujia-badge-warning',
     'link': '/portal/exam/registration/2'},
    {'title': 'Đào tạo quản lý', 'date_label': 'Thứ 2, 15/06/2026 • 08:20',
     'meta': '1 đạt • 1 không đạt', 'status': 'Có kết quả',
     'badge': 'wujia-badge-success', 'link': '/portal/exam/registration/3'},
]

DEMO_COURSES = [
    {'title': 'Đăng ký thi lại', 'meta': '5 vòng thi • Trong 60 ngày tiếp theo',
     'status': 'Còn lịch', 'badge': 'wujia-badge-info', 'closed': False},
    {'title': 'Thi pha chế định kỳ', 'meta': '4 vòng thi • Mở lịch tháng 7',
     'status': 'Còn lịch', 'badge': 'wujia-badge-info', 'closed': False},
    {'title': 'Đào tạo quản lý cửa hàng', 'meta': '2 vòng thi • Chưa mở lịch mới',
     'status': 'Đã đóng', 'badge': 'wujia-badge-muted', 'closed': True},
]

DEMO_SELECTED_COURSE = {'title': 'Đăng ký thi lại',
                        'meta': '5 vòng thi • Trung tâm đào tạo Ngô Gia'}

DEMO_SLOTS = [
    {'time': '08:20', 'status': 'Còn chỗ', 'available': True},
    {'time': '13:00', 'status': 'Hết chỗ', 'available': False},
    {'time': '16:00', 'status': 'Còn chỗ', 'available': True},
]

DEMO_PEOPLE = [
    {'name': 'Nguyễn Văn A', 'role': 'Pha chế', 'phone': '0901***123'},
    {'name': 'Trần Thị B', 'role': 'Quản lý ca', 'phone': '0902***456'},
    {'name': 'Lê Văn C', 'role': 'Pha chế', 'phone': '0903***789'},
]

DEMO_RESULT = {
    'title': 'Đăng ký thi lại',
    'date_label': 'Thứ 5, 02/07/2026 • 08:20',
    'summary': '3 nhân sự • 2 đạt • 1 không đạt',
    'location': 'Trung tâm đào tạo Ngô Gia',
    'people': [
        {'name': 'Nguyễn Văn A', 'role': 'Pha chế', 'score': '84 điểm', 'passed': True},
        {'name': 'Trần Thị B', 'role': 'Quản lý ca', 'score': '91 điểm', 'passed': True},
        {'name': 'Lê Văn C', 'role': 'Pha chế', 'score': '58 điểm', 'passed': False},
    ],
}

# Ngày "còn chỗ" tháng 7/2026 (khớp Figma s2). Còn lại = không lịch (inert).
DEMO_AVAILABLE_DAYS = {1, 2, 3, 6, 8, 9, 11, 12, 14, 16, 19, 20, 21, 23, 24, 25,
                       28, 29, 31}


def _build_demo_calendar(year=2026, month=7, available=None):
    """Ma trận tuần (T2→CN) cho calendar chọn lịch thi — UI-only demo."""
    available = available if available is not None else DEMO_AVAILABLE_DAYS
    cal = _calendar.Calendar(firstweekday=0)  # 0 = Monday → cột T2 đầu tiên
    weeks = []
    for week in cal.monthdatescalendar(year, month):
        row = []
        for d in week:
            in_month = d.month == month
            if not in_month:
                state = 'out'
            elif d.day in available:
                state = 'available'
            else:
                state = 'none'
            row.append({
                'day': d.day,
                'in_month': in_month,
                'state': state,
                'date_label': '%s, %02d/%02d/%d' % (
                    _WEEKDAYS_VN[d.weekday()], d.day, month, year),
            })
        weeks.append(row)
    return {'label': 'Tháng %d %d' % (month, year), 'weeks': weeks}


class WujiaPortalExam(http.Controller):

    @http.route(['/portal/exam'], type='http', auth='user', sitemap=False)
    def portal_exam_schedule(self, **kw):
        franchise_ids = get_active_franchise_ids_filter()
        Schedule = request.env['wujia.exam.schedule'].sudo()
        upcoming = Schedule.search([
            ('exam_date', '>=', fields.Datetime.now()),
            ('state', 'in', ['open', 'closed']),
            '|', ('franchise_ids', '=', False),
                 ('franchise_ids', 'in',
                  list(franchise_ids) if franchise_ids else [-1]),
        ], order='exam_date asc', limit=50)
        Reg = request.env['wujia.exam.registration'].sudo()
        my_reg_ids = Reg.search([
            ('user_id', '=', request.env.user.id),
            ('schedule_id', 'in', upcoming.ids),
            ('state', '!=', 'cancelled'),
        ]).mapped('schedule_id').ids
        # Mobile (s0): list card theo đăng ký của cửa hàng — data thật nếu có,
        # fallback demo khớp Figma (UI-only, backend đa-nhân-sự = Phase 2).
        my_regs = Reg.search([
            ('user_id', '=', request.env.user.id),
            ('state', '!=', 'cancelled'),
        ], order='register_date desc', limit=20)
        m_exam_items = []
        for r in my_regs:
            lbl = REG_LABELS.get(r.state, (r.state, 'wujia-badge-muted'))
            m_exam_items.append({
                'title': r.schedule_id.name,
                'date_label': r.schedule_id.exam_date and
                    r.schedule_id.exam_date.strftime('%d/%m/%Y • %H:%M') or '',
                'meta': '1 nhân sự', 'status': lbl[0], 'badge': lbl[1],
                'link': '/portal/exam/registration/%d' % r.id,
            })
        if not m_exam_items:
            m_exam_items = DEMO_EXAM_ITEMS
        return request.render('wujia_portal_exam.portal_exam_schedule', {
            'upcoming': upcoming, 'my_reg_schedule_ids': my_reg_ids,
            'schedule_labels': SCHEDULE_LABELS,
            'm_exam_items': m_exam_items,
        })

    @http.route(['/portal/exam/register'], type='http', auth='user',
                sitemap=False)
    def portal_exam_register_flow(self, **kw):
        """Wizard s1→s5 (UI-only, 1 trang JS). Demo khớp Figma #4755:2."""
        return request.render('wujia_portal_exam.portal_exam_register', {
            'courses': DEMO_COURSES,
            'selected_course': DEMO_SELECTED_COURSE,
            'calendar': _build_demo_calendar(),
            'slots': DEMO_SLOTS,
            'people': DEMO_PEOPLE,
        })

    @http.route(['/portal/exam/registration/<int:reg_id>'], type='http',
                auth='user', sitemap=False)
    def portal_exam_registration_detail(self, reg_id, **kw):
        """Kết quả đăng ký (s6, UI-only demo — render bất kể id)."""
        return request.render(
            'wujia_portal_exam.portal_exam_registration_detail',
            {'result': DEMO_RESULT})

    @http.route(['/portal/exam/my'], type='http', auth='user', sitemap=False)
    def portal_exam_my(self, **kw):
        Reg = request.env['wujia.exam.registration'].sudo()
        my_regs = Reg.search([('user_id', '=', request.env.user.id)],
                             order='register_date desc', limit=100)
        return request.render('wujia_portal_exam.portal_exam_my', {
            'my_regs': my_regs, 'reg_labels': REG_LABELS,
            'schedule_labels': SCHEDULE_LABELS,
        })

    @http.route(['/portal/exam/result'], type='http', auth='user', sitemap=False)
    def portal_exam_result(self, **kw):
        Result = request.env['wujia.exam.result'].sudo()
        results = Result.search([('user_id', '=', request.env.user.id)],
                                order='create_date desc', limit=100)
        return request.render('wujia_portal_exam.portal_exam_result', {
            'results': results,
        })

    @http.route(['/portal/exam/schedule/<int:schedule_id>'],
                type='http', auth='user', sitemap=False)
    def portal_exam_schedule_detail(self, schedule_id, **kw):
        Schedule = request.env['wujia.exam.schedule'].sudo()
        schedule = Schedule.browse(int(schedule_id)).exists()
        if not schedule:
            return request.redirect('/portal/exam')
        Reg = request.env['wujia.exam.registration'].sudo()
        my_reg = Reg.search([
            ('user_id', '=', request.env.uid),
            ('schedule_id', '=', schedule.id),
            ('state', '!=', 'cancelled'),
        ], limit=1)
        return request.render('wujia_portal_exam.portal_exam_schedule_detail', {
            'schedule': schedule, 'my_reg': my_reg,
            'schedule_labels': SCHEDULE_LABELS,
        })

    # ============================================================ AJAX
    @http.route(['/portal/exam/register'], type='json', auth='user',
                methods=['POST'])
    def portal_exam_register(self, schedule_id, **kw):
        try:
            schedule_id = int(schedule_id)
        except (TypeError, ValueError):
            return {'error': 'invalid_input'}
        fid = get_active_franchise_id()
        if not fid:
            return {'error': 'no_active_franchise'}
        Schedule = request.env['wujia.exam.schedule'].sudo()
        schedule = Schedule.browse(schedule_id).exists()
        if not schedule or schedule.state != 'open':
            return {'error': 'schedule_closed'}

        Reg = request.env['wujia.exam.registration'].sudo()
        # Lock schedule row → count → insert. Race-safe.
        request.env.cr.execute(
            "SELECT id FROM wujia_exam_schedule WHERE id=%s FOR UPDATE",
            (schedule.id,),
        )
        if schedule.max_participants:
            current = Reg.search_count([
                ('schedule_id', '=', schedule.id),
                ('state', '!=', 'cancelled'),
            ])
            if current >= schedule.max_participants:
                return {'error': 'full', 'message': 'Lịch thi đã đầy.'}
        # Idempotent — uniq constraint sẽ raise nếu race vẫn lọt
        existing = Reg.search([
            ('user_id', '=', request.env.uid),
            ('schedule_id', '=', schedule.id),
        ], limit=1)
        if existing:
            if existing.state == 'cancelled':
                existing.write({'state': 'registered'})
                return {'success': True, 'reg_id': existing.id, 'restored': True}
            return {'error': 'duplicate', 'reg_id': existing.id}
        try:
            reg = Reg.create({
                'schedule_id': schedule.id,
                'user_id': request.env.uid,
                'franchise_id': fid,
            })
        except Exception:
            _logger.exception('Exam register failed schedule=%s', schedule.id)
            return {'error': 'internal_error'}
        return {'success': True, 'reg_id': reg.id}

    @http.route(['/portal/exam/cancel/<int:reg_id>'], type='json',
                auth='user', methods=['POST'])
    def portal_exam_cancel(self, reg_id, **kw):
        Reg = request.env['wujia.exam.registration'].sudo()
        reg = Reg.browse(int(reg_id)).exists()
        if not reg or reg.user_id.id != request.env.uid:
            return {'error': 'not_found'}
        if reg.state == 'cancelled':
            return {'success': True, 'already_cancelled': True}
        if reg.schedule_id.exam_date and reg.schedule_id.exam_date <= fields.Datetime.now():
            return {'error': 'already_started'}
        reg.write({'state': 'cancelled'})
        return {'success': True}
