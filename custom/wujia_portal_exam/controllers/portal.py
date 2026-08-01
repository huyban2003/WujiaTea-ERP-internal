"""Wujia portal — Exam controller (Sprint 45: wire thật vào backend Sprint M).

Phần XEM (list / chi tiết / kết quả / khóa / lịch / khung giờ) wire dữ liệu thật
cho cả mobile lẫn PC. Phần TẠO PHIẾU (submit) wire thật trên MOBILE; PC create
deferred (PC vẫn xem/duyệt real, dùng demo pc_calendar/pc_slots/pc_summary cho
màn đăng ký). Mọi dữ liệu giới hạn theo current store + membership; backend
server-resolve franchise/member/requester, không tin ID frontend.

Routes:
- GET  /portal/exam                          Action 1 — danh sách phiếu (list)
- GET  /portal/exam/register                 màn đăng ký (mobile wire / PC demo)
- POST /portal/exam/calendar        (json)   Action 4 — lịch tháng theo khóa
- POST /portal/exam/slots           (json)   Action 5 — khung giờ theo ngày
- POST /portal/exam/register        (json)   Action 7+8 — submit tạo phiếu
- GET  /portal/exam/registration/<int>       Action 2+9 — chi tiết + kết quả
- GET  /portal/exam/line/<int>/photo         Action 10 — ảnh thí sinh (ACL)
"""
import base64
import binascii
import calendar as _calendar
import logging
from datetime import date, datetime, timedelta

import pytz
from werkzeug.exceptions import Forbidden, NotFound

from odoo import _, fields, http
from odoo.exceptions import UserError, ValidationError
from odoo.http import request
from odoo.tools.image import image_process

from odoo.addons.wujia_portal_base.controllers.portal import (
    get_active_franchise_id,
)

_logger = logging.getLogger(__name__)

PAGE_SIZE = 10  # spec: list mặc định 10/trang
DEFAULT_TZ = 'Asia/Ho_Chi_Minh'
MAX_PHOTO_BYTES = 5 * 1024 * 1024
PHOTO_MIMES = ('image/jpeg', 'image/jpg', 'image/png')

_WEEKDAYS_VN = ['Thứ 2', 'Thứ 3', 'Thứ 4', 'Thứ 5', 'Thứ 6', 'Thứ 7', 'Chủ nhật']

# Nhãn hiển thị — key trùng state của registration (mobile).
M_REG_BADGE = {
    'submitted': ('Chờ duyệt', 'wujia-badge-warning'),
    'confirmed': ('Đã đăng ký', 'wujia-badge-info'),
    'rejected': ('Từ chối', 'wujia-badge-danger'),
    'cancelled': ('Đã hủy', 'wujia-badge-muted'),
}

# PC — dùng lại nhãn Figma WJ_Exam_PC (badge riêng cho trạng thái đăng ký).
PC_REG_STATES = {
    'submitted': ('Chờ xác nhận', 'wj-pc-badge--transit'),
    'confirmed': ('Đã đăng ký', 'wj-pc-badge--sent'),
    'rejected': ('Từ chối', 'wj-pc-badge--cancel'),
    'cancelled': ('Đã hủy', 'wj-pc-badge--pending'),
}

# Trạng thái công bố kết quả — LUÔN là badge riêng với trạng thái đăng ký.
PC_PUBLISH_STATES = {
    'published': ('Đã công bố', 'wj-pc-badge--done'),
    'unpublished': ('Chưa công bố', 'wj-pc-badge--pending'),
    'none': ('Chưa có', 'wj-pc-badge--pending'),
    'na': ('Không áp dụng', 'wj-pc-badge--pending'),
}

# --------------------------------------------------------------------------- #
# PC "Đăng ký mới" — demo UI-only (PC submit deferred, Sprint sau). Bản đọc PC
# (list/detail) dùng dữ liệu THẬT; chỉ màn tạo phiếu PC còn demo.
# --------------------------------------------------------------------------- #
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
    'course_name': 'Đăng ký thi lại', 'exam_date': '02/07/2026',
    'exam_datetime': '02/07/2026 · 08:20–10:00',
    'location': 'Trung tâm đào tạo Ngô Gia',
    'registration_deadline': '30/06/2026 · 08:20',
    'franchise_name': '[H000] Cửa hàng Nguyễn Trãi',
    'quota_label': 'Phiếu: 2 / 4', 'seat_label': 'Ca còn: 3 chỗ',
    'note': 'Sắp xếp nhân sự tham gia đúng giờ',
    'note_full': 'Sắp xếp nhân sự tham gia đúng giờ theo lịch đã chọn.',
}
PC_AVAILABLE_DAYS = {6, 8, 9, 11, 12, 14, 16, 19, 20, 21, 23, 24, 25, 28, 29, 31}
PC_BLOCKED_DAYS = {5, 10, 15, 26}
PC_SELECTED_DAY = 2


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
def _user_tz():
    return pytz.timezone(request.env.user.tz or DEFAULT_TZ)


def _to_local(dt):
    """Datetime UTC naive (Odoo) → aware local."""
    if not dt:
        return None
    return pytz.utc.localize(dt).astimezone(_user_tz())


def _float_hhmm(value):
    v = float(value or 0.0)
    h = int(v)
    m = int(round((v - h) * 60))
    if m == 60:
        h, m = h + 1, 0
    return '%02d:%02d' % (h, m)


def _slot_time_label(session):
    slot = session.time_slot_id
    if not slot:
        return '—'
    return '%s–%s' % (_float_hhmm(slot.time_from), _float_hhmm(slot.time_to))


def _session_dt_label(session, sep='·'):
    """'dd/mm/YYYY · HH:MM' theo giờ địa phương."""
    local = _to_local(session.start_datetime)
    if not local:
        return '—'
    return local.strftime('%%d/%%m/%%Y %s %%H:%%M' % sep)


def _session_day_label(session):
    """'Thứ 5, 02/07/2026 • 08:20' cho card mobile."""
    local = _to_local(session.start_datetime)
    if not local:
        return '—'
    return '%s, %s' % (_WEEKDAYS_VN[local.weekday()],
                       local.strftime('%d/%m/%Y • %H:%M'))


def _result_summary(reg):
    """(label, kind) tổng hợp Đạt/Không đạt — chỉ khi đã công bố."""
    if not reg.session_id.results_published:
        return ('Chưa công bố', 'muted')
    passed = sum(1 for l in reg.line_ids if l.result == 'passed')
    failed = sum(1 for l in reg.line_ids if l.result == 'failed')
    parts = []
    if passed:
        parts.append('%d Đạt' % passed)
    if failed:
        parts.append('%d Không đạt' % failed)
    label = ' · '.join(parts) or 'Đã công bố'
    if passed and not failed:
        kind = 'pass'
    elif failed and not passed:
        kind = 'fail'
    else:
        kind = 'mixed'
    return (label, kind)


def _selectable(session, now):
    return (session.state == 'open'
            and (not session.registration_deadline
                 or now <= session.registration_deadline)
            and session.available_participant_count > 0)


def _day_state(day_sessions, d, today, horizon, now):
    """Trạng thái 1 ngày trên lịch: available / full / none."""
    if d < today or d > horizon:
        return 'none'
    if not day_sessions:
        return 'none'
    if any(_selectable(s, now) for s in day_sessions):
        return 'available'
    # Còn session open/chưa quá hạn nhưng hết chỗ → 'full'; else 'none'.
    if any(s.state == 'open'
           and (not s.registration_deadline or now <= s.registration_deadline)
           for s in day_sessions):
        return 'full'
    return 'none'


def _exam_calendar(course, year, month):
    """Ma trận tuần (T2→CN) trạng thái ngày cho 1 khóa thi (dữ liệu thật)."""
    Session = request.env['wujia.exam.session'].sudo()
    today = fields.Date.context_today(request.env.user)
    horizon = today + timedelta(days=course.registration_horizon_days)
    first = date(year, month, 1)
    last = date(year, month, _calendar.monthrange(year, month)[1])
    sessions = Session.search([
        ('course_id', '=', course.id),
        ('exam_date', '>=', first), ('exam_date', '<=', last),
        ('state', '!=', 'cancelled'),
    ])
    by_day = {}
    for s in sessions:
        by_day.setdefault(s.exam_date, []).append(s)
    now = fields.Datetime.now()
    weeks = []
    for week in _calendar.Calendar(firstweekday=0).monthdatescalendar(year, month):
        row = []
        for d in week:
            in_month = d.month == month
            state = 'out' if not in_month else _day_state(
                by_day.get(d, []), d, today, horizon, now)
            row.append({
                'day': d.day, 'in_month': in_month, 'state': state,
                'date': d.isoformat(),
                'date_label': '%s, %02d/%02d/%d' % (
                    _WEEKDAYS_VN[d.weekday()], d.day, month, year),
            })
        weeks.append(row)
    return {'label': 'Tháng %d %d' % (month, year), 'weeks': weeks,
            'year': year, 'month': month}


def _exam_slots(course, d):
    """Danh sách session (khung giờ) của khóa vào 1 ngày — dữ liệu thật."""
    Session = request.env['wujia.exam.session'].sudo()
    now = fields.Datetime.now()
    sessions = Session.search([
        ('course_id', '=', course.id), ('exam_date', '=', d),
        ('state', '!=', 'cancelled'),
    ], order='start_datetime, id')
    slots = []
    for s in sessions:
        ok = _selectable(s, now)
        if s.state != 'open':
            status = 'Đã đóng'
        elif s.registration_deadline and now > s.registration_deadline:
            status = 'Hết hạn'
        elif s.available_participant_count <= 0:
            status = 'Hết chỗ'
        else:
            status = 'Còn %d chỗ' % s.available_participant_count
        slots.append({
            'session_id': s.id, 'time': _slot_time_label(s), 'status': status,
            'available': ok, 'seats': s.available_participant_count,
            'max_per_reg': s.max_participants_per_registration,
            'location': s.location or '—',
        })
    return slots


def _course_meta(course):
    """Meta ngắn cho card khóa thi (mobile) + cờ 'closed' (không còn lịch)."""
    Session = request.env['wujia.exam.session'].sudo()
    today = fields.Date.context_today(request.env.user)
    horizon = today + timedelta(days=course.registration_horizon_days)
    now = fields.Datetime.now()
    upcoming = Session.search([
        ('course_id', '=', course.id),
        ('exam_date', '>=', today), ('exam_date', '<=', horizon),
        ('state', '=', 'open'),
    ])
    has_open = any(_selectable(s, now) for s in upcoming)
    return {
        'meta': '%d kỳ thi • Trong %d ngày tới' % (
            len(upcoming), course.registration_horizon_days),
        'closed': not has_open,
    }


def _published_courses():
    return request.env['wujia.exam.course'].sudo().search(
        [('state', '=', 'published'), ('active', '=', True)], order='name, id')


def _build_pc_calendar(year=2026, month=7):
    """Calendar PC 'Đăng ký mới' — demo UI-only (PC submit deferred)."""
    weeks = []
    for week in _calendar.Calendar(firstweekday=0).monthdatescalendar(year, month):
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
            row.append({'day': d.day, 'state': state,
                        'selected': d.month == month and d.day == PC_SELECTED_DAY})
        weeks.append(row)
    return {'label': 'Tháng %d %d' % (month, year), 'weeks': weeks,
            'weekdays': ['T2', 'T3', 'T4', 'T5', 'T6', 'T7', 'CN']}


class WujiaPortalExam(http.Controller):

    # --------------------------------------------------------------- list
    @http.route(['/portal/exam'], type='http', auth='user', sitemap=False)
    def portal_exam_schedule(self, page=1, state='', result='', q='',
                             date_from='', date_to='', **kw):
        fid = get_active_franchise_id()
        Reg = request.env['wujia.exam.registration'].sudo()
        m_items, pc_regs, pager = [], [], _empty_pager()
        if fid:
            domain = [('franchise_id', '=', fid)]
            if state in M_REG_BADGE:
                domain.append(('state', '=', state))
            q = (q or '').strip()
            if q:
                domain += ['|', ('name', 'ilike', q),
                           ('course_id.name', 'ilike', q)]
            if result == 'published':
                domain.append(('session_id.results_published', '=', True))
            elif result == 'unpublished':
                domain.append(('session_id.results_published', '=', False))
            df, dt = _parse_date(date_from), _parse_date(date_to)
            if df:
                domain.append(('request_date', '>=', fields.Datetime.to_string(
                    _local_day_start(df))))
            if dt:
                domain.append(('request_date', '<=', fields.Datetime.to_string(
                    _local_day_start(dt) + timedelta(days=1))))
            try:
                page = max(1, int(page))
            except (TypeError, ValueError):
                page = 1
            total = Reg.search_count(domain)
            offset = (page - 1) * PAGE_SIZE
            regs = Reg.search(domain, limit=PAGE_SIZE, offset=offset,
                              order='request_date desc, id desc')
            for reg in regs:
                m_items.append(_m_list_item(reg))
                pc_regs.append(_pc_list_item(reg))
            pages = max(1, (total + PAGE_SIZE - 1) // PAGE_SIZE)
            pager = {'from': offset + 1 if total else 0,
                     'to': min(offset + PAGE_SIZE, total), 'total': total,
                     'size': PAGE_SIZE, 'page': page, 'pages': pages}
        return request.render('wujia_portal_exam.portal_exam_schedule', {
            'm_exam_items': m_items,
            'pc_regs': pc_regs, 'pc_reg_states': PC_REG_STATES,
            'pc_pager': pager,
            'f_state': state, 'f_result': result, 'f_q': q,
        })

    # --------------------------------------------------------------- register
    @http.route(['/portal/exam/register'], type='http', auth='user',
                sitemap=False)
    def portal_exam_register_flow(self, course_id=None, year=None, month=None,
                                  **kw):
        fid = get_active_franchise_id()
        if not fid:
            return request.redirect('/portal/exam')
        courses = _published_courses()
        m_courses = []
        for c in courses:
            meta = _course_meta(c)
            m_courses.append({
                'course_id': c.id, 'title': c.name, 'meta': meta['meta'],
                'status': 'Còn lịch' if not meta['closed'] else 'Đã đóng',
                'badge': 'wujia-badge-info' if not meta['closed']
                else 'wujia-badge-muted',
                'closed': meta['closed'],
            })
        selected = courses.browse(int(course_id)) if course_id else courses[:1]
        if selected and selected not in courses:
            selected = courses[:1]
        today = fields.Date.context_today(request.env.user)
        y = int(year) if year else today.year
        mo = int(month) if month else today.month
        calendar = (_exam_calendar(selected, y, mo) if selected
                    else {'label': '', 'weeks': [], 'year': y, 'month': mo})
        sel_meta = _course_meta(selected) if selected else {'meta': ''}
        return request.render('wujia_portal_exam.portal_exam_register', {
            'courses': m_courses,
            'selected_course': {
                'course_id': selected.id if selected else 0,
                'title': selected.name if selected else 'Chưa có khóa thi',
                'meta': sel_meta['meta'],
            },
            'calendar': calendar,
            'slots': [],   # nạp qua AJAX khi chọn ngày
            # PC "Đăng ký mới" — demo (PC submit deferred).
            'pc_calendar': _build_pc_calendar(), 'pc_slots': PC_SLOTS,
            'pc_lines': PC_LINES, 'pc_summary': PC_SUMMARY,
        })

    # --------------------------------------------------------------- calendar
    @http.route(['/portal/exam/calendar'], type='json', auth='user',
                methods=['POST'])
    def portal_exam_calendar(self, course_id=None, year=None, month=None, **kw):
        if not get_active_franchise_id():
            return {'error': 'no_store',
                    'message': 'Vui lòng chọn cửa hàng trước khi thao tác.'}
        course = _published_courses().browse(int(course_id or 0)).exists()
        course = course.filtered(lambda c: c.state == 'published')
        if not course:
            return {'error': 'not_found', 'message': 'Khóa thi không hợp lệ.'}
        today = fields.Date.context_today(request.env.user)
        return {'calendar': _exam_calendar(
            course, int(year or today.year), int(month or today.month))}

    # --------------------------------------------------------------- slots
    @http.route(['/portal/exam/slots'], type='json', auth='user',
                methods=['POST'])
    def portal_exam_slots(self, course_id=None, exam_date=None, **kw):
        if not get_active_franchise_id():
            return {'error': 'no_store',
                    'message': 'Vui lòng chọn cửa hàng trước khi thao tác.'}
        course = _published_courses().browse(int(course_id or 0)).exists()
        course = course.filtered(lambda c: c.state == 'published')
        d = _parse_date(exam_date)
        if not course or not d:
            return {'error': 'not_found', 'message': 'Lịch thi không hợp lệ.'}
        return {'slots': _exam_slots(course, d)}

    # --------------------------------------------------------------- submit
    @http.route(['/portal/exam/register'], type='json', auth='user',
                methods=['POST'])
    def portal_exam_register(self, session_id=None, participants=None,
                             note=None, **kw):
        fid = get_active_franchise_id()
        if not fid:
            return {'error': 'no_store',
                    'message': 'Vui lòng chọn cửa hàng trước khi thao tác.'}
        Session = request.env['wujia.exam.session'].sudo()
        session = Session.browse(int(session_id or 0)).exists()
        if not session or session.course_id.state != 'published':
            return {'error': 'not_found',
                    'message': 'Khung giờ đã thay đổi hoặc không còn. Vui lòng'
                               ' chọn lại lịch thi.'}
        parts = participants or []
        max_p = session.max_participants_per_registration or 4
        if not parts:
            return {'error': 'validation',
                    'message': 'Cần ít nhất 1 người dự thi.'}
        if len(parts) > max_p:
            return {'error': 'validation',
                    'message': 'Tối đa %d người mỗi phiếu.' % max_p}
        try:
            line_cmds = [(0, 0, _build_line_vals(p)) for p in parts]
        except ValidationError as e:
            return {'error': 'validation', 'message': _exc_msg(e)}
        member = request.env['wujia.franchise.member'].sudo()
        try:
            member = member.find_active_membership(request.env.user.id, fid)
        except Exception:  # pragma: no cover — helper vắng thì bỏ qua
            member = member.browse()
        # Savepoint + flush trong try: constraint sức chứa của session là
        # @api.constrains → chỉ raise lúc flush; nếu để tới flush cuối request thì
        # sẽ thành 500 và (nguy hiểm hơn) commit phiếu vượt chỗ. Ép flush ở đây
        # để bắt lỗi thành message thân thiện, savepoint đảm bảo rollback sạch.
        try:
            with request.env.cr.savepoint():
                reg = request.env['wujia.exam.registration'].sudo().create({
                    'session_id': session.id,
                    'franchise_id': fid,
                    'requester_user_id': request.env.user.id,
                    'member_id': member.id if member else False,
                    'note': (note or '').strip() or False,
                    'line_ids': line_cmds,
                })
                request.env.flush_all()
        except (ValidationError, UserError) as e:
            return {'error': 'business', 'message': _exc_msg(e)}
        return {'success': True,
                'redirect': '/portal/exam/registration/%d' % reg.id}

    # --------------------------------------------------------------- detail
    @http.route(['/portal/exam/registration/<int:reg_id>'], type='http',
                auth='user', sitemap=False)
    def portal_exam_registration_detail(self, reg_id, **kw):
        fid = get_active_franchise_id()
        Reg = request.env['wujia.exam.registration'].sudo()
        reg = Reg.search([('id', '=', reg_id),
                          ('franchise_id', '=', fid)], limit=1) if fid \
            else Reg.browse()
        if not reg:
            return request.redirect('/portal/exam')
        return request.render(
            'wujia_portal_exam.portal_exam_registration_detail', {
                'reg_view': _m_detail(reg),
                'pc_detail': _pc_detail(reg),
                'pc_reg_states': PC_REG_STATES,
                'pc_publish_states': PC_PUBLISH_STATES,
            })

    # --------------------------------------------------------------- photo
    @http.route(['/portal/exam/line/<int:line_id>/photo'], type='http',
                auth='user', sitemap=False)
    def portal_exam_line_photo(self, line_id, **kw):
        """Stream ảnh thí sinh — ACL: line phải thuộc phiếu current store."""
        fid = get_active_franchise_id()
        if not fid:
            raise Forbidden()
        line = request.env['wujia.exam.registration.line'].sudo().search([
            ('id', '=', line_id), ('franchise_id', '=', fid),
        ], limit=1)
        if not line or not line.image_1920:
            raise NotFound()
        return request.env['ir.binary']._get_image_stream_from(
            line, 'image_1920').get_response()


# --------------------------------------------------------------------------- #
# Mappers (record → dict template) — key trùng field thật.
# --------------------------------------------------------------------------- #
def _empty_pager():
    return {'from': 0, 'to': 0, 'total': 0, 'size': PAGE_SIZE,
            'page': 1, 'pages': 1}


def _m_list_item(reg):
    label, kind = _result_summary(reg)
    if reg.session_id.results_published:
        status, badge, meta = 'Có kết quả', 'wujia-badge-success', _m_result_meta(reg)
    else:
        status, badge = M_REG_BADGE.get(reg.state, (reg.state, 'wujia-badge-muted'))
        meta = '%d nhân sự' % reg.participant_count
    return {
        'title': reg.course_id.name or reg.session_id.name,
        'date_label': _session_day_label(reg.session_id),
        'meta': meta, 'status': status, 'badge': badge,
        'link': '/portal/exam/registration/%d' % reg.id,
    }


def _m_result_meta(reg):
    passed = sum(1 for l in reg.line_ids if l.result == 'passed')
    failed = sum(1 for l in reg.line_ids if l.result == 'failed')
    parts = []
    if passed:
        parts.append('%d đạt' % passed)
    if failed:
        parts.append('%d không đạt' % failed)
    return ' • '.join(parts) or ('%d nhân sự' % reg.participant_count)


def _pc_list_item(reg):
    label, kind = _result_summary(reg)
    return {
        'id': reg.id, 'name': reg.name,
        'course_name': reg.course_id.name or reg.session_id.name,
        'exam_datetime': _session_dt_label(reg.session_id),
        'location': reg.session_id.location or '—',
        'participant_count': reg.participant_count, 'state': reg.state,
        'result_label': label, 'result_kind': kind,
    }


def _reg_lines(reg, published):
    lines = []
    for l in reg.line_ids:
        lines.append({
            'employee_name': l.employee_name, 'phone': l.phone or '',
            'birth_year': l.birth_year or '', 'job_position': l.job_position or '',
            'result': l.result if published else 'pending',
            'result_note': l.result_note if published else '',
            'has_photo': bool(l.image_1920), 'line_id': l.id,
        })
    return lines


def _m_detail(reg):
    """Chi tiết cho mobile — state-aware (thay demo DEMO_RESULT có 'điểm')."""
    published = reg.session_id.results_published
    status, badge = M_REG_BADGE.get(reg.state, (reg.state, 'wujia-badge-muted'))
    if published:
        status, badge = 'Có kết quả', 'wujia-badge-success'
    reason = ''
    if reg.state == 'rejected':
        reason = reg.reject_reason or ''
    elif reg.state == 'cancelled':
        reason = reg.cancellation_reason or ''
    return {
        'id': reg.id, 'name': reg.name,
        'title': reg.course_id.name or reg.session_id.name,
        'date_label': _session_day_label(reg.session_id),
        'location': reg.session_id.location or 'Trung tâm đào tạo Ngô Gia',
        'summary': '%d nhân sự%s' % (
            reg.participant_count,
            (' • ' + _result_summary(reg)[0]) if published else ''),
        'status': status, 'badge': badge,
        'state': reg.state, 'is_published': published, 'reason': reason,
        'people': _reg_lines(reg, published),
    }


def _pc_detail(reg):
    """Chi tiết cho PC — dữ liệu thật vào layout Figma 05/06."""
    published = reg.session_id.results_published
    show_results = reg.state == 'confirmed'
    if reg.state == 'submitted':
        publish_state, banner_kind = 'none', 'warning'
        card_sub = 'Phiếu đang chờ Ngô Gia xác nhận.'
        banner_title = 'Yêu cầu đã được gửi đến Ngô Gia.'
        banner_text = ('Portal chưa hiển thị kết quả cho đến khi phiếu được xác'
                       ' nhận và công bố.')
    elif reg.state == 'confirmed':
        publish_state = 'published' if published else 'unpublished'
        banner_kind = 'info'
        card_sub = 'Thông tin phiếu đã được Ngô Gia xác nhận.'
        if published:
            banner_title = 'Kết quả đã được công bố.'
            banner_text = 'Trang hiển thị giá trị kết quả mới nhất theo từng người.'
        else:
            banner_title = 'Ngô Gia đã xác nhận danh sách đăng ký.'
            banner_text = ('Kết quả sẽ xuất hiện trên chính danh sách người tham'
                           ' gia sau khi công bố.')
    elif reg.state == 'rejected':
        publish_state, banner_kind = 'na', 'danger'
        card_sub = 'Phiếu đã bị từ chối.'
        banner_title = 'Lý do: %s' % (reg.reject_reason or 'Không có.')
        banner_text = ('Cửa hàng chỉ có thể xem lý do; MVP không sửa hoặc gửi lại'
                       ' từ phiếu này.')
    else:  # cancelled
        publish_state, banner_kind = 'na', 'muted'
        card_sub = 'Phiếu đã bị hủy.'
        banner_title = 'Lý do: %s' % (reg.cancellation_reason or 'Không có.')
        banner_text = ('Phiếu không tham gia công bố kết quả và không có nút hủy'
                       ' trên portal.')
    return {
        'id': reg.id, 'name': reg.name, 'state': reg.state,
        'publish_state': publish_state, 'show_results': show_results,
        'card_sub': card_sub,
        'course_name': reg.course_id.name or reg.session_id.name,
        'exam_datetime': _session_dt_label(reg.session_id),
        'location': reg.session_id.location or '—',
        'franchise_name': reg.franchise_id.name or '—',
        'requester': reg.requester_user_id.name or '—',
        'request_date': (_to_local(reg.request_date).strftime('%d/%m/%Y · %H:%M')
                         if reg.request_date else '—'),
        'participant_label': '%02d người' % reg.participant_count,
        'banner_kind': banner_kind, 'banner_title': banner_title,
        'banner_text': banner_text,
        'lines': _reg_lines(reg, published),
    }


# --------------------------------------------------------------------------- #
# Submit helpers
# --------------------------------------------------------------------------- #
def _build_line_vals(p):
    name = (p.get('employee_name') or '').strip()
    phone = (p.get('phone') or '').strip()
    if not name or not phone:
        raise ValidationError(_(
            "Mỗi người dự thi cần có họ tên và số điện thoại."))
    vals = {
        'employee_name': name, 'phone': phone,
        'job_position': (p.get('job_position') or '').strip() or False,
    }
    by = (p.get('birth_year') or '').strip() if isinstance(
        p.get('birth_year'), str) else p.get('birth_year')
    if by:
        try:
            vals['birth_year'] = int(by)
        except (TypeError, ValueError):
            raise ValidationError(_("Năm sinh '%s' không hợp lệ.", by))
    photo = p.get('photo')
    if photo:
        vals['image_1920'] = _clean_photo(photo)
    return vals


def _clean_photo(raw):
    """data-URL/base64 ảnh → base64 str hợp lệ (guard MIME + dung lượng)."""
    data = raw
    if raw.startswith('data:'):
        try:
            head, data = raw.split(',', 1)
        except ValueError:
            raise ValidationError(_(
                "Ảnh nhân viên không đúng định dạng hoặc vượt dung lượng cho phép."))
        mime = head[5:].split(';', 1)[0].lower()
        if mime and mime not in PHOTO_MIMES:
            raise ValidationError(_(
                "Ảnh nhân viên không đúng định dạng hoặc vượt dung lượng cho phép."))
    try:
        decoded = base64.b64decode(data, validate=True)
    except (binascii.Error, ValueError):
        raise ValidationError(_(
            "Ảnh nhân viên không đúng định dạng hoặc vượt dung lượng cho phép."))
    if len(decoded) > MAX_PHOTO_BYTES:
        raise ValidationError(_(
            "Ảnh nhân viên vượt dung lượng cho phép (tối đa 5 MB)."))
    # Chạy đúng pipeline mà fields.Image dùng lúc write (resize ≤1920). Ảnh
    # hỏng/cắt cụt sẽ ném ở đây → trả message thân thiện thay vì 500 khi flush.
    try:
        image_process(decoded, size=(1920, 1920))
    except Exception:
        raise ValidationError(_(
            "Ảnh nhân viên không hợp lệ hoặc bị hỏng. Vui lòng chọn ảnh khác."))
    return data


def _exc_msg(e):
    return (getattr(e, 'args', None) and e.args[0]) or str(e)


def _parse_date(value):
    if not value:
        return None
    value = value.strip()
    for fmt in ('%Y-%m-%d', '%d/%m/%Y'):
        try:
            return datetime.strptime(value, fmt).date()
        except (ValueError, TypeError):
            continue
    return None


def _local_day_start(d):
    """Đầu ngày local (00:00) → datetime UTC naive để so với request_date."""
    local = _user_tz().localize(datetime(d.year, d.month, d.day))
    return local.astimezone(pytz.utc).replace(tzinfo=None)
