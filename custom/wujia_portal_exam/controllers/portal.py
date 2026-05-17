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
    'open': ('Đang mở', 'state-active'),
    'closed': ('Đã đóng', 'state-sent'),
    'done': ('Đã thi xong', 'state-done'),
    'cancelled': ('Đã hủy', 'state-cancel'),
}

REG_LABELS = {
    'registered': ('Đã đăng ký', 'state-sent'),
    'checked_in': ('Đã có mặt', 'state-active'),
    'cancelled': ('Đã hủy', 'state-cancel'),
}


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
        return request.render('wujia_portal_exam.portal_exam_schedule', {
            'upcoming': upcoming, 'my_reg_schedule_ids': my_reg_ids,
            'schedule_labels': SCHEDULE_LABELS,
        })

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
