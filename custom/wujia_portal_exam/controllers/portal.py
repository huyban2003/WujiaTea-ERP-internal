from odoo import fields, http
from odoo.http import request


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
        franchise_ids = request.env.user._get_accessible_franchise_ids()
        Schedule = request.env['wujia.exam.schedule'].sudo()
        # Hiện tại chỉ list lịch thi sắp diễn ra (exam_date >= now) và mở
        upcoming = Schedule.search([
            ('exam_date', '>=', fields.Datetime.now()),
            ('state', 'in', ['open', 'closed']),
            '|', ('franchise_ids', '=', False),
                 ('franchise_ids', 'in', list(franchise_ids) if franchise_ids else [-1]),
        ], order='exam_date asc', limit=50)
        # Lấy id đăng ký user đã có cho upcoming → để hide button "Đăng ký"
        Reg = request.env['wujia.exam.registration'].sudo()
        my_reg_ids = Reg.search([
            ('user_id', '=', request.env.user.id),
            ('schedule_id', 'in', upcoming.ids),
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
