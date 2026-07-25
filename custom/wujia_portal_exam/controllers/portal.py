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

# --------------------------------------------------------------------------- #
# PC demo data (Sprint 39 — Figma WJ_Exam_PC v1.2, 7 frame 1920×1080).
# UI-only như mobile: portal chưa wire đăng ký thật (backend Sprint M đã xong).
# Key đặt TRÙNG TÊN FIELD THẬT để sprint wire sau chỉ đổi nguồn dữ liệu, không
# phải sửa template:
#   registration : name, course_id, session_id, state, participant_count
#   session      : exam_date, time_slot_id, location, registration_deadline
#   line         : employee_name, phone, birth_year, job_position, result,
#                  result_note
# --------------------------------------------------------------------------- #
PC_REG_STATES = {
    'submitted': ('Chờ xác nhận', 'wj-pc-badge--transit'),
    'confirmed': ('Đã đăng ký', 'wj-pc-badge--sent'),
    'rejected': ('Từ chối', 'wj-pc-badge--cancel'),
    'cancelled': ('Đã hủy', 'wj-pc-badge--pending'),
}

# Trạng thái công bố kết quả — LUÔN là badge riêng với trạng thái đăng ký
# (spec frame 06: "hai thông tin riêng biệt").
PC_PUBLISH_STATES = {
    'published': ('Đã công bố', 'wj-pc-badge--done'),
    'unpublished': ('Chưa công bố', 'wj-pc-badge--pending'),
    'none': ('Chưa có', 'wj-pc-badge--pending'),
    'na': ('Không áp dụng', 'wj-pc-badge--pending'),
}

PC_REGS = [
    {'id': 21, 'name': 'EXR00021', 'course_name': 'Đăng ký thi lại',
     'exam_datetime': '02/07/2026 · 08:20', 'location': 'Trung tâm Ngô Gia',
     'participant_count': 3, 'state': 'confirmed',
     'result_label': '2 Đạt · 1 Không đạt', 'result_kind': 'mixed'},
    {'id': 22, 'name': 'EXR00022', 'course_name': 'Thi pha chế định kỳ',
     'exam_datetime': '11/07/2026 · 13:00', 'location': 'Trung tâm Ngô Gia',
     'participant_count': 2, 'state': 'submitted',
     'result_label': 'Chưa công bố', 'result_kind': 'muted'},
    {'id': 23, 'name': 'EXR00023', 'course_name': 'Đào tạo quản lý',
     'exam_datetime': '22/07/2026 · 08:20', 'location': 'Văn phòng Quận 5',
     'participant_count': 1, 'state': 'confirmed',
     'result_label': 'Chưa công bố', 'result_kind': 'muted'},
    {'id': 18, 'name': 'EXR00018', 'course_name': 'Thi pha chế định kỳ',
     'exam_datetime': '28/06/2026 · 16:00', 'location': 'Trung tâm Ngô Gia',
     'participant_count': 2, 'state': 'rejected',
     'result_label': 'Không áp dụng', 'result_kind': 'muted'},
    {'id': 15, 'name': 'EXR00015', 'course_name': 'Đăng ký thi lại',
     'exam_datetime': '15/06/2026 · 08:20', 'location': 'Trung tâm Ngô Gia',
     'participant_count': 1, 'state': 'cancelled',
     'result_label': 'Không áp dụng', 'result_kind': 'muted'},
    {'id': 12, 'name': 'EXR00012', 'course_name': 'Thi pha chế định kỳ',
     'exam_datetime': '06/06/2026 · 13:00', 'location': 'Văn phòng Quận 5',
     'participant_count': 4, 'state': 'confirmed',
     'result_label': '4 Đạt', 'result_kind': 'pass'},
]

PC_PAGER = {'from': 1, 'to': 6, 'total': 18, 'size': 10, 'page': 1, 'pages': 2}

# Calendar tháng 7/2026 của bản PC — 4 state theo legend Figma:
#   available (còn chỗ) · blocked (không thể đăng ký) · none (không có lịch)
PC_AVAILABLE_DAYS = {6, 8, 9, 11, 12, 14, 16, 19, 20, 21, 23, 24, 25, 28, 29, 31}
PC_BLOCKED_DAYS = {5, 10, 15, 26}
PC_SELECTED_DAY = 2

PC_SLOTS = [
    {'time_slot': '08:20–10:00', 'reason': 'Còn 3 chỗ', 'kind': 'open',
     'selected': True},
    {'time_slot': '13:00–14:40', 'reason': 'Hết chỗ', 'kind': 'full',
     'selected': False},
    {'time_slot': '16:00–17:40', 'reason': 'Đã đóng', 'kind': 'closed',
     'selected': False},
]

PC_LINES = [
    {'employee_name': 'Nguyễn Văn An', 'phone': '0901 234 567',
     'birth_year': '1998', 'job_position': 'Pha chế', 'has_photo': True},
    {'employee_name': 'Trần Thị Bình', 'phone': '0902 345 678',
     'birth_year': '1995', 'job_position': 'Quản lý ca', 'has_photo': False},
]

PC_SUMMARY = {
    'course_name': 'Đăng ký thi lại',
    'exam_date': '02/07/2026',
    'exam_datetime': '02/07/2026 · 08:20–10:00',
    'location': 'Trung tâm đào tạo Ngô Gia',
    'registration_deadline': '30/06/2026 · 08:20',
    'franchise_name': '[H000] Cửa hàng Nguyễn Trãi',
    'quota_label': 'Phiếu: 2 / 4',
    'seat_label': 'Ca còn: 3 chỗ',
    'note': 'Sắp xếp nhân sự tham gia đúng giờ',
    'note_full': 'Sắp xếp nhân sự tham gia đúng giờ theo lịch đã chọn.',
}

PC_DETAIL = {
    'id': 21,
    'name': 'EXR00021',
    'state': 'confirmed',
    'publish_state': 'published',
    'card_sub': 'Thông tin phiếu đã được Ngô Gia xác nhận.',
    'show_results': True,
    'course_name': 'Đăng ký thi lại',
    'exam_datetime': '02/07/2026 · 08:20–10:00',
    'location': 'Trung tâm đào tạo Ngô Gia',
    'franchise_name': '[H000] Nguyễn Trãi',
    'requester': 'Nguyễn Admin · Owner',
    'request_date': '26/06/2026 · 09:45',
    'participant_label': '03 người',
    'banner_title': 'Kết quả được công bố lúc 10:30 ngày 03/07/2026.',
    'banner_text': 'Nếu Ngô Gia cập nhật kết quả, trang này sẽ hiển thị giá trị mới nhất.',
    'banner_kind': 'info',
    'lines': [
        {'employee_name': 'Nguyễn Văn An', 'phone': '0901 234 567',
         'birth_year': '1998', 'job_position': 'Pha chế', 'result': 'passed',
         'result_note': ''},
        {'employee_name': 'Trần Thị Bình', 'phone': '0902 345 678',
         'birth_year': '1995', 'job_position': 'Quản lý ca', 'result': 'passed',
         'result_note': ''},
        {'employee_name': 'Lê Minh Châu', 'phone': '0903 456 789',
         'birth_year': '1999', 'job_position': 'Pha chế', 'result': 'failed',
         'result_note': 'Thiếu phần thao tác vệ sinh'},
    ],
}

# Frame 06 — 4 biến thể của màn chi tiết. Phiếu rejected/cancelled KHÔNG hiển
# thị bảng kết quả (spec board 06).
PC_DETAIL_VARIANTS = {
    'submitted': {
        'card_sub': 'Phiếu đang chờ Ngô Gia xác nhận.',
        'publish_state': 'none', 'show_results': False, 'banner_kind': 'warning',
        'banner_title': 'Yêu cầu đã được gửi đến Ngô Gia.',
        'banner_text': 'Portal chưa hiển thị kết quả cho đến khi phiếu được xác'
                       ' nhận và công bố.',
    },
    'confirmed': {
        'card_sub': 'Thông tin phiếu đã được Ngô Gia xác nhận.',
        'publish_state': 'unpublished', 'show_results': True,
        'banner_kind': 'info',
        'banner_title': 'Ngô Gia đã xác nhận danh sách đăng ký.',
        'banner_text': 'Kết quả sẽ xuất hiện trên chính danh sách người tham gia'
                       ' sau khi công bố.',
    },
    'rejected': {
        'card_sub': 'Phiếu đã bị từ chối.',
        'publish_state': 'na', 'show_results': False, 'banner_kind': 'danger',
        'banner_title': 'Lý do: Thông tin người đăng ký chưa đầy đủ.',
        'banner_text': 'Cửa hàng chỉ có thể xem lý do; MVP không sửa hoặc gửi'
                       ' lại từ phiếu này.',
    },
    'cancelled': {
        'card_sub': 'Phiếu đã bị hủy.',
        'publish_state': 'na', 'show_results': False, 'banner_kind': 'muted',
        'banner_title': 'Lý do: Session thi đã được Ngô Gia hủy.',
        'banner_text': 'Phiếu không tham gia công bố kết quả và không có nút hủy'
                       ' trên portal.',
    },
}


def _pc_detail_for(reg_id):
    """Ghép PC_DETAIL với biến thể state (frame 06) — UI-only demo.

    reg_id khớp PC_REGS → lấy đúng state/khóa thi của dòng đó, để bấm
    "Xem chi tiết" từ danh sách ra đúng biến thể trong spec.
    """
    row = next((r for r in PC_REGS if r['id'] == reg_id), None)
    detail = dict(PC_DETAIL)
    if not row:
        return detail
    variant = PC_DETAIL_VARIANTS.get(row['state'], {})
    detail.update({
        'id': row['id'],
        'name': row['name'],
        'state': row['state'],
        'course_name': row['course_name'],
        'participant_label': '%02d người' % row['participant_count'],
    })
    detail.update(variant)
    # Phiếu đã công bố (demo mặc định) giữ nguyên banner/publish của PC_DETAIL.
    if row['id'] == PC_DETAIL['id']:
        detail.update({
            'publish_state': PC_DETAIL['publish_state'],
            'show_results': True,
            'banner_kind': PC_DETAIL['banner_kind'],
            'banner_title': PC_DETAIL['banner_title'],
            'banner_text': PC_DETAIL['banner_text'],
            'card_sub': PC_DETAIL['card_sub'],
        })
    return detail


def _build_pc_calendar(year=2026, month=7):
    """Calendar PC — thêm state 'blocked' + 'selected' so với bản mobile."""
    cal = _calendar.Calendar(firstweekday=0)
    weeks = []
    for week in cal.monthdatescalendar(year, month):
        row = []
        for d in week:
            if d.month != month:
                state = 'out'
            elif d.day in PC_AVAILABLE_DAYS:
                state = 'available'
            elif d.day in PC_BLOCKED_DAYS:
                state = 'blocked'
            else:
                state = 'none'
            row.append({
                'day': d.day,
                'state': state,
                'selected': d.month == month and d.day == PC_SELECTED_DAY,
            })
        weeks.append(row)
    return {'label': 'Tháng %d %d' % (month, year), 'weeks': weeks,
            'weekdays': ['T2', 'T3', 'T4', 'T5', 'T6', 'T7', 'CN']}


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
            # PC (Figma 01_List) — demo UI-only, parity với nhánh mobile.
            'pc_regs': PC_REGS, 'pc_reg_states': PC_REG_STATES,
            'pc_pager': PC_PAGER,
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
            # PC (Figma 02_Create + 03/04 modal) — demo UI-only.
            'pc_calendar': _build_pc_calendar(),
            'pc_slots': PC_SLOTS,
            'pc_lines': PC_LINES,
            'pc_summary': PC_SUMMARY,
        })

    @http.route(['/portal/exam/registration/<int:reg_id>'], type='http',
                auth='user', sitemap=False)
    def portal_exam_registration_detail(self, reg_id, **kw):
        """Kết quả đăng ký (s6, UI-only demo — render bất kể id)."""
        return request.render(
            'wujia_portal_exam.portal_exam_registration_detail',
            {'result': DEMO_RESULT,
             # PC (Figma 05_Detail + 06 state matrix) — demo UI-only.
             'pc_detail': _pc_detail_for(reg_id),
             'pc_reg_states': PC_REG_STATES,
             'pc_publish_states': PC_PUBLISH_STATES})

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
