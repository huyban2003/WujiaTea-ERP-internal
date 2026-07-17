"""Wujia portal — Exam controller.

Sprint M: backend đăng ký thi đã rework (course/session/registration đa-nhân-sự).
Portal GIỮ DEMO — wire đăng ký thật = sprint sau. Controller chỉ đảm bảo các route
render 200 (không tham chiếu field đã bỏ trên registration).

Routes:
- GET  /portal/exam                          schedule list (demo)
- GET  /portal/exam/register                 register wizard (demo, mobile)
- GET  /portal/exam/registration/<int>       registration result (demo)
- GET  /portal/exam/my                        my registrations (demo-safe empty)
- GET  /portal/exam/result                    results (demo-safe empty)
- GET  /portal/exam/schedule/<int>           schedule detail (dormant model)
- POST /portal/exam/register        (json)   deferred stub
- POST /portal/exam/cancel/<int>    (json)   deferred stub
"""
import calendar as _calendar
import logging

from odoo import fields, http
from odoo.http import request

from odoo.addons.wujia_portal_base.controllers.portal import (
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
    'submitted': ('Đã gửi', 'wujia-badge-info'),
    'confirmed': ('Đã duyệt', 'wujia-badge-success'),
    'rejected': ('Từ chối', 'wujia-badge-danger'),
    'cancelled': ('Đã hủy', 'wujia-badge-muted'),
}

# --------------------------------------------------------------------------- #
# UI-only demo data (Sprint 26 — mobile "Đăng ký thi" theo Figma #4755:2).
# Backend đa-nhân-sự / khung giờ / kết quả-theo-người đã có (Sprint M) nhưng
# portal chưa wire → giữ demo để render 100% khớp Figma.
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
        # Lịch thi cũ (dormant schedule) vẫn đọc được; đăng ký = demo.
        Schedule = request.env['wujia.exam.schedule'].sudo()
        upcoming = Schedule.search([
            ('exam_date', '>=', fields.Datetime.now()),
            ('state', 'in', ['open', 'closed']),
            '|', ('franchise_ids', '=', False),
                 ('franchise_ids', 'in',
                  list(franchise_ids) if franchise_ids else [-1]),
        ], order='exam_date asc', limit=50)
        return request.render('wujia_portal_exam.portal_exam_schedule', {
            'upcoming': upcoming, 'my_reg_schedule_ids': [],
            'schedule_labels': SCHEDULE_LABELS,
            'm_exam_items': DEMO_EXAM_ITEMS,
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
        # Demo-safe: portal chưa wire đăng ký thật (Sprint M backend-only).
        empty = request.env['wujia.exam.registration'].browse()
        return request.render('wujia_portal_exam.portal_exam_my', {
            'my_regs': empty, 'reg_labels': REG_LABELS,
            'schedule_labels': SCHEDULE_LABELS,
        })

    @http.route(['/portal/exam/result'], type='http', auth='user', sitemap=False)
    def portal_exam_result(self, **kw):
        # Demo-safe: kết quả giờ nhập trên registration.line (Sprint M) — portal
        # chưa wire → render rỗng.
        empty = request.env['wujia.exam.result'].browse()
        return request.render('wujia_portal_exam.portal_exam_result', {
            'results': empty,
        })

    @http.route(['/portal/exam/schedule/<int:schedule_id>'],
                type='http', auth='user', sitemap=False)
    def portal_exam_schedule_detail(self, schedule_id, **kw):
        Schedule = request.env['wujia.exam.schedule'].sudo()
        schedule = Schedule.browse(int(schedule_id)).exists()
        if not schedule:
            return request.redirect('/portal/exam')
        return request.render('wujia_portal_exam.portal_exam_schedule_detail', {
            'schedule': schedule, 'my_reg': False,
            'schedule_labels': SCHEDULE_LABELS,
        })

    # ============================================================ AJAX (stub)
    @http.route(['/portal/exam/register'], type='json', auth='user',
                methods=['POST'])
    def portal_exam_register(self, **kw):
        # Đăng ký qua portal deferred (Sprint M backend-only, wire sprint sau).
        return {'error': 'deferred',
                'message': 'Đăng ký thi qua portal sẽ sớm ra mắt.'}

    @http.route(['/portal/exam/cancel/<int:reg_id>'], type='json',
                auth='user', methods=['POST'])
    def portal_exam_cancel(self, reg_id, **kw):
        return {'error': 'deferred',
                'message': 'Chức năng sẽ sớm ra mắt.'}
