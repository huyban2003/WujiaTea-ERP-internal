"""Wujia portal — Exam controller (Sprint 45: wire thật; Sprint 46: PC submit).

Phần XEM (list / chi tiết / kết quả / khóa / lịch / khung giờ) wire dữ liệu thật
cho cả mobile lẫn PC. Phần TẠO PHIẾU (submit) wire thật cho CẢ mobile lẫn PC
(Sprint 46 — PC dùng chung 3 endpoint calendar/slots/register). Mọi dữ liệu giới
hạn theo current store + membership; backend server-resolve franchise/member/
requester, không tin ID frontend.

Routes:
- GET  /portal/exam                          Action 1 — danh sách phiếu (list)
- GET  /portal/exam/register                 màn đăng ký (mobile + PC wire thật)
- POST /portal/exam/calendar        (json)   Action 4 — lịch tháng theo khóa
- POST /portal/exam/slots           (json)   Action 5 — khung giờ theo ngày
- POST /portal/exam/register        (json)   Action 7+8 — submit tạo phiếu
- GET  /portal/exam/registration/<int>       Action 2+9 — chi tiết + kết quả
- GET  /portal/exam/line/<int>/photo         Action 10 — ảnh thí sinh (ACL)
"""
import calendar as _calendar
import logging
from datetime import datetime, timedelta

import pytz
from werkzeug.exceptions import Forbidden, NotFound

from odoo import _, fields, http
from odoo.exceptions import UserError, ValidationError
from odoo.http import request

from odoo.addons.wujia_portal_base.controllers.portal import (
    get_active_franchise_id,
)
from odoo.addons.wujia_portal_base.controllers.utils import (
    build_pager,
    date_range_error,
    parse_page_size,
    status_badge,
    status_badge_for,
)
from odoo.addons.wujia_exam.models.wujia_exam_registration import ExamPortalError

_logger = logging.getLogger(__name__)

PAGE_SIZE = 10  # spec: list mặc định 10/trang
PAGE_SIZES = (10, 20, 50)  # whitelist ?limit — khớp <select> trong pager PC
DEFAULT_TZ = 'Asia/Ho_Chi_Minh'

_WEEKDAYS_VN = ['Thứ 2', 'Thứ 3', 'Thứ 4', 'Thứ 5', 'Thứ 6', 'Thứ 7', 'Chủ nhật']

# Nhãn hiển thị — key trùng state của registration (mobile).
M_REG_BADGE = {k: (v, status_badge_for(v)) for k, v in {
    'submitted': 'Chờ duyệt',
    'confirmed': 'Đã đăng ký',
    'rejected': 'Từ chối',
    'cancelled': 'Đã hủy',
}.items()}

# PC — dùng lại nhãn Figma WJ_Exam_PC (badge riêng cho trạng thái đăng ký).
PC_REG_STATES = {k: (v, status_badge_for(v)) for k, v in {
    'submitted': 'Chờ xác nhận',
    'confirmed': 'Đã đăng ký',
    'rejected': 'Từ chối',
    'cancelled': 'Đã hủy',
}.items()}

# Trạng thái công bố kết quả — LUÔN là badge riêng với trạng thái đăng ký.
PC_PUBLISH_STATES = {k: (v, status_badge_for(v)) for k, v in {
    'published': 'Đã công bố',
    'unpublished': 'Chưa công bố',
    'none': 'Chưa có',
    'na': 'Không áp dụng',
}.items()}

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
    passed, failed = reg._portal_result_counts()
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


def _max_hint(n):
    return (_("Mỗi phiếu được đăng ký tối đa %d người.", n) if n
            else _("Chọn khóa thi để xem giới hạn người mỗi phiếu."))


# Nhãn khung giờ theo wujia.exam.session._portal_slot_status().
SLOT_STATUS_LABELS = {'closed': 'Đã đóng', 'expired': 'Hết hạn', 'full': 'Hết chỗ'}


def _exam_calendar(course, year, month):
    """Ma trận tuần (T2→CN) trạng thái ngày cho 1 khóa thi (dữ liệu thật)."""
    states = course._portal_day_states(year, month)
    weeks = []
    for week in _calendar.Calendar(firstweekday=0).monthdatescalendar(year, month):
        row = []
        for d in week:
            in_month = d.month == month
            row.append({
                'day': d.day, 'in_month': in_month,
                'state': states[d] if in_month else 'out',
                'date': d.isoformat(),
                'date_label': '%s, %02d/%02d/%d' % (
                    _WEEKDAYS_VN[d.weekday()], d.day, month, year),
            })
        weeks.append(row)
    return {'label': 'Tháng %d %d' % (month, year), 'weeks': weeks,
            'year': year, 'month': month}


def _exam_slots(course, d):
    """Danh sách session (khung giờ) của khóa vào 1 ngày — dữ liệu thật."""
    now = fields.Datetime.now()
    slots = []
    for s in course._portal_sessions_on(d):
        status = s._portal_slot_status(now)
        slots.append({
            'session_id': s.id, 'time': _slot_time_label(s),
            'status': SLOT_STATUS_LABELS.get(
                status, 'Còn %d chỗ' % s.available_participant_count),
            'available': s._portal_is_selectable(now),
            'seats': s.available_participant_count,
            'max_per_reg': s._effective_max_per_registration(),
            'location': s.location or '—',
            # Additive (Sprint 46) — nhãn hạn đăng ký cho tóm tắt PC. Mobile
            # renderSlots không đọc key này ⇒ 0 regression.
            'deadline': (_to_local(s.registration_deadline)
                         .strftime('%d/%m/%Y · %H:%M')
                         if s.registration_deadline else '—'),
        })
    return slots


def _course_meta(course):
    """Meta ngắn cho card khóa thi (mobile) + cờ 'closed'/'full' (luật ở model)."""
    meta = course._portal_booking_meta()
    return {
        'meta': '%d kỳ thi • Trong %d ngày tới' % (
            meta['upcoming_count'], course.registration_horizon_days),
        'closed': meta['closed'],
        'full': meta['full'],
    }


def _published_courses():
    return request.env['wujia.exam.course'].sudo()._portal_published()


class WujiaPortalExam(http.Controller):

    # --------------------------------------------------------------- list
    @http.route(['/portal/exam'], type='http', auth='user', sitemap=False)
    def portal_exam_schedule(self, page=1, state='', result='', q='',
                             date_from='', date_to='', limit=None, **kw):
        fid = get_active_franchise_id()
        Reg = request.env['wujia.exam.registration'].sudo()
        # whitelist ?limit: giá trị ngoài ô chọn (?limit=100000) rơi về mặc định route.
        size = parse_page_size(limit, PAGE_SIZE, PAGE_SIZES)
        m_items, pc_regs, total = [], [], 0
        # Ngày ngược: không chạy query, giữ nguyên 2 ô đã nhập, báo TẠI thanh lọc
        # thay vì để domain vô nghiệm rồi hiện "chưa có đăng ký thi".
        filter_error = date_range_error(date_from, date_to)
        if fid and not filter_error:
            domain = Reg._portal_scope_domain(fid)
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
            total = Reg.search_count(domain)
        # Một nguồn duy nhất cho số trang: build_pager kẹp ?page=99 về trang cuối
        # nên lát cắt bên dưới không bao giờ rơi ra trang rỗng.
        pgn = build_pager(total, page, size, path='/portal/exam',
                          item_label='bản ghi', page_size_options=PAGE_SIZES,
                          size_param='limit')
        if total:
            regs = Reg.search(domain, limit=pgn['page_size'],
                              offset=pgn['offset'],
                              order='request_date desc, id desc')
            for reg in regs:
                m_items.append(_m_list_item(reg))
                pc_regs.append(_pc_list_item(reg))
        return request.render('wujia_portal_exam.portal_exam_schedule', {
            'm_exam_items': m_items,
            'pc_regs': pc_regs, 'pc_reg_states': PC_REG_STATES,
            'pgn': pgn,
            'f_state': state, 'f_result': result, 'f_q': q,
            'f_date_from': date_from, 'f_date_to': date_to,
            'filter_error': filter_error,
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
            cstatus = ('Còn lịch' if not meta['closed']
                       else 'Hết chỗ' if meta['full'] else 'Đã đóng')
            m_courses.append({
                'course_id': c.id, 'title': c.name, 'meta': meta['meta'],
                'status': cstatus,
                'badge': status_badge_for(cstatus),
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
        # PC "Đăng ký mới" — dữ liệu THẬT (Sprint 46, thay demo PC_*). Grid dùng
        # chung biến `calendar` real; khóa/khung giờ/người do JS nạp qua endpoint.
        max_per_reg = selected._effective_max_per_registration() if selected else 0
        store_name = request.env['wujia.franchise.management'].sudo().browse(
            fid).name or '—'
        pc_summary = {
            'course_name': selected.name if selected else 'Chưa có khóa thi',
            'franchise_name': store_name,
            'quota_label': '0 / %d' % max_per_reg, 'max_per_reg': max_per_reg,
            'max_hint': _max_hint(max_per_reg),
            # JS lấp khi chọn khung giờ.
            'exam_date': '—', 'exam_datetime': '—', 'location': '—',
            'registration_deadline': '—', 'seat_label': '—',
            'note': '', 'note_full': '',
        }
        return request.render('wujia_portal_exam.portal_exam_register', {
            'courses': m_courses,
            'selected_course': {
                'course_id': selected.id if selected else 0,
                'title': selected.name if selected else 'Chưa có khóa thi',
                'meta': sel_meta['meta'],
            },
            'calendar': calendar,
            'slots': [],   # nạp qua AJAX khi chọn ngày
            # PC "Đăng ký mới" — context thật (grid = `calendar`, người tự nhập).
            'pc_courses': [{'course_id': c.id, 'title': c.name,
                            'max_per_reg': c._effective_max_per_registration()}
                           for c in courses],
            'pc_lines': [], 'pc_summary': pc_summary,
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
        try:
            reg = request.env['wujia.exam.registration'].sudo().register_from_portal(
                int(session_id or 0), fid, request.env.user, participants, note)
        except ExamPortalError as e:
            return {'error': e.kind, 'message': _exc_msg(e)}
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
        reg = Reg.search([('id', '=', reg_id)] + Reg._portal_scope_domain(fid),
                         limit=1) if fid else Reg.browse()
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
        Line = request.env['wujia.exam.registration.line'].sudo()
        line = Line.search([('id', '=', line_id)] + Line._portal_scope_domain(fid),
                           limit=1)
        if not line or not line.image_1920:
            raise NotFound()
        return request.env['ir.binary']._get_image_stream_from(
            line, 'image_1920').get_response()


# --------------------------------------------------------------------------- #
# Mappers (record → dict template) — key trùng field thật.
# --------------------------------------------------------------------------- #
def _m_list_item(reg):
    label, kind = _result_summary(reg)
    if reg.session_id.results_published:
        status, badge, meta = 'Có kết quả', status_badge('success'), _m_result_meta(reg)
    else:
        status, badge = M_REG_BADGE.get(reg.state, (reg.state, status_badge('neutral')))
        meta = '%d nhân sự' % reg.participant_count
    return {
        'title': reg.course_id.name or reg.session_id.name,
        'date_label': _session_day_label(reg.session_id),
        'meta': meta, 'status': status, 'badge': badge,
        'link': '/portal/exam/registration/%d' % reg.id,
    }


def _m_result_meta(reg):
    passed, failed = reg._portal_result_counts()
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
    status, badge = M_REG_BADGE.get(reg.state, (reg.state, status_badge('neutral')))
    if published:
        status, badge = 'Có kết quả', status_badge('success')
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
        # WJ-EXAM-006 — chỉ nhắc "đăng ký thi lại" khi thật sự có người trượt.
        'has_failed': published and any(l.result == 'failed' for l in reg.line_ids),
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
# Helpers parse
# --------------------------------------------------------------------------- #
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
