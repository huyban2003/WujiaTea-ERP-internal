import pandas as pd
from enum import Enum


class RemediationState(str, Enum):
    NEED_REMEDIATION = 'need_remediation'
    REMEDIATED = 'remediated'
    DONE = 'done'

# -*- coding: utf-8 -*-
import random
from odoo import api, fields, models, _
# pyrefly: ignore [missing-import]
from odoo.exceptions import ValidationError, UserError


class WujiaFranchiseInspection(models.Model):

    def _check_and_update_done_state(self):
        for rec in self:
            if rec.state == 'need_remediation':
                criteria_lines = rec.line_ids.filtered(lambda l: l.display_type == 'line' and not l.is_pass)
                # Phiếu chỉ hoàn thành nếu TẤT CẢ các dòng không đạt đều ở trạng thái DONE
                if not criteria_lines or all(l.remediation_state == RemediationState.DONE.value for l in criteria_lines):
                    rec.write({'state': 'done'})

    _name = 'wujia.franchise.inspection'
    _description = 'Phiếu khảo sát đánh giá cửa hàng nhượng quyền'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Mã/Tên phiếu khảo sát (name) đã tồn tại trong hệ thống! Không thể trùng lặp.'),
    ]

    name = fields.Char(string='Tên phiếu khảo sát', required=True, copy=False, tracking=True)

    submit_date = fields.Date(
        string='Ngày nộp',
        tracking=True,
    )
    confirm_date = fields.Date(
        string='fields:wujia.franchise.inspection:confirm_date',
        tracking=True,
    )

    state = fields.Selection([
        ('draft', 'selection:wujia.franchise.inspection:state:draft'),
        ('in_progress', 'selection:wujia.franchise.inspection:state:in_progress'),
        ('need_remediation', 'selection:wujia.franchise.inspection:state:need_remediation'),
        ('done', 'selection:wujia.franchise.inspection:state:done'),
        ('cancel', 'selection:wujia.franchise.inspection:state:cancel')
    ], string='Status', default='draft', tracking=True)

    planned_date = fields.Date(
        string='Ngày dự kiến',
        tracking=True,
    )

    checklist_score = fields.Float(
        string='fields:wujia.franchise.inspection:checklist_score',
        compute='_compute_checklist_score',
        store=True,
        readonly=True,
        default=95.0,
        tracking=True,
    )

    exam_score = fields.Float(
        string='fields:wujia.franchise.inspection:exam_score',
        compute='_compute_exam_score',
        store=True,
        aggregator='avg',
        tracking=True,
        help='là điểm được lấy từ câu hỏi phần điền vào ô trống',
    )

    total_score = fields.Float(
        string='fields:wujia.franchise.inspection:total_score',
        compute='_compute_total_score',
        store=True,
        aggregator='avg',
        tracking=True,
        help='điểm = điểm checklist + điểm kiểm tra',
    )

    grade_id = fields.Many2one(
        'wujia.franchise.inspection.grade',
        string='Xếp loại',
        compute='_compute_grade',
        store=True,
        readonly=True,
        tracking=True,
    )
    
    next_due_date = fields.Date(
        string='Lần kiểm tra kế tiếp',
        tracking=True,
    )

    next_schedule_id = fields.Many2one(
        'wujia.supervision.schedule',
        string='Lịch giám sát tiếp theo',
        ondelete='set null',
    )

    test_employee_name = fields.Char(
        string='Nhân viên được kiểm tra',
        help='nhận viện tại cửa hàng không có trong user',
    )

    tenure = fields.Float(
        string='Thâm niên',
        help='thời gian làm việc của nhân viên',
    )
    # video 
    video = fields.Binary(
        string='Video',
        attachment=True,
    )

    # RELATION 

    schedule_id = fields.Many2one(
        'wujia.supervision.schedule',
        string='Lịch giám sát',
        required=True,
        ondelete='cascade',
        tracking=True,
    )
    
    template_id = fields.Many2one(
        'wujia.franchise.inspection.template',
        string='Mẫu khảo sát',
        required=True,
        ondelete='restrict',
        tracking=True,
    )

    franchise_id = fields.Many2one(
        'wujia.franchise.management',
        string='Cửa hàng',
        required=True,
        ondelete='restrict',
        tracking=True,
    )

    inspector_user_id = fields.Many2one(
        'res.users',
        string='Người kiểm tra',
        required=True,
        ondelete='restrict',
        default=lambda self: self.env.user,
        tracking=True,
    )

    previous_inspection_id = fields.Many2one(
        'wujia.franchise.inspection',
        string='fields:wujia.franchise.inspection:previous_inspection_id',
        compute='_compute_previous_inspection_id',
        store=True,
        ondelete='set null',
        readonly=True
    )

    line_ids = fields.One2many(
        'wujia.franchise.inspection.line',
        'inspection_id',
        string='Chi tiết khảo sát',
        copy=False,
    )

    exam_line_ids = fields.One2many(
        'wujia.franchise.inspection.exam.line',
        'inspection_id',
        string='Điểm kiểm tra',
        copy=False,
    )

    report_line_ids = fields.One2many(
        'wujia.franchise.inspection.report.line',
        'inspection_id',
        string='Dòng báo cáo',
        copy=False,
    )

    is_exam_submitted = fields.Boolean(
        string='Đã nộp bài kiểm tra',
        default=False,
        copy=False,
    )

    exam_submit_date = fields.Datetime(
        string='Thời gian nộp bài kiểm tra',
        copy=False,
    )

    inspection_chart_data = fields.Text(
        string='Dữ liệu biểu đồ',
        compute='_compute_inspection_chart_data',
    )

    @api.depends('franchise_id', 'template_id', 'total_score', 'state')
    def _compute_inspection_chart_data(self):
        import json
        for rec in self:
            if not rec.franchise_id or not rec.template_id:
                rec.inspection_chart_data = json.dumps({
                    'title': _("label:wujia.franchise.inspection:chart_history_title"),
                    'single_label': _("label:wujia.franchise.inspection:chart_single_score"),
                    'avg_label': _("label:wujia.franchise.inspection:chart_avg_score"),
                    'no_data_title': _("label:wujia.franchise.inspection:chart_no_data_title"),
                    'no_data_desc': _("label:wujia.franchise.inspection:chart_no_data_desc"),
                })
                continue
            
            # Lấy 10 phiếu giám sát gần nhất của cửa hàng này theo đúng Mẫu khảo sát (template_id)
            inspections = self.env['wujia.franchise.inspection'].search([
                ('franchise_id', '=', rec.franchise_id.id),
                ('template_id', '=', rec.template_id.id),
                ('state', 'in', ['done', 'need_remediation']),
                ('planned_date', '!=', False)
            ], order='planned_date desc, id desc', limit=10)
            
            # Sắp xếp theo thứ tự thời gian tăng dần từ cũ -> mới để vẽ biểu đồ
            inspections = inspections.sorted(key=lambda r: (r.planned_date, r.id))
            
            labels = []
            scores = []
            avg_scores = []
            
            if inspections:
                total_sum = sum(ins.total_score for ins in inspections)
                overall_avg = total_sum / len(inspections)
                
                for ins in inspections:
                    date_str = ins.planned_date.strftime('%d/%m/%Y') if ins.planned_date else ''
                    labels.append(date_str)
                    scores.append(ins.total_score)
                    avg_scores.append(round(overall_avg, 2))
            
            rec.inspection_chart_data = json.dumps({
                'labels': labels,
                'scores': scores,
                'avg_scores': avg_scores,
                'title': _("label:wujia.franchise.inspection:chart_history_title"),
                'single_label': _("label:wujia.franchise.inspection:chart_single_score"),
                'avg_label': _("label:wujia.franchise.inspection:chart_avg_score"),
                'no_data_title': _("label:wujia.franchise.inspection:chart_no_data_title"),
                'no_data_desc': _("label:wujia.franchise.inspection:chart_no_data_desc"),
            })

    @api.constrains('planned_date', 'franchise_id', 'state')
    def _check_inspection_constraints(self):
        today = fields.Date.context_today(self)
        for rec in self:
            if rec.state == 'cancel':
                continue
            if rec.planned_date and rec.planned_date > today:
                raise ValidationError(_(
                    "Không thể tạo hoặc lưu phiếu khảo sát cho ngày trong tương lai (%s)!\n"
                    "Ngày khảo sát chưa đến (Hôm nay: %s). Bạn có thể tạo Lịch giám sát trước."
                ) % (rec.planned_date.strftime('%d/%m/%Y'), today.strftime('%d/%m/%Y')))
            
            if rec.franchise_id and rec.planned_date:
                duplicate = self.search([
                    ('franchise_id', '=', rec.franchise_id.id),
                    ('planned_date', '=', rec.planned_date),
                    ('state', '!=', 'cancel'),
                    ('id', '!=', rec.id)
                ], limit=1)
                if duplicate:
                    raise ValidationError(_(
                        "Trong 1 ngày (%s), mỗi cửa hàng '%s' chỉ được phép có tối đa 1 phiếu khảo sát!\n"
                        "Đã có phiếu khảo sát (%s) trong ngày này."
                    ) % (rec.planned_date.strftime('%d/%m/%Y'), rec.franchise_id.name, duplicate.name))


    @api.model
    def _generate_inspection_name(self, franchise_id, schedule_id=None, seq_number=None):
        """
        Hàm sinh mã phiếu khảo sát dạng 'PGS-[mã cửa hàng]-[stt 4 chữ số]'.
        Nếu tạo từ Lịch giám sát (schedule_id), tên phiếu sẽ khớp 100% với mã lịch giám sát (thay LGS thành PGS).
        """
        if schedule_id:
            schedule = schedule_id if isinstance(schedule_id, models.Model) else self.env['wujia.supervision.schedule'].browse(schedule_id)
            if schedule.exists() and schedule.name:
                if schedule.name.startswith('LGS-'):
                    return schedule.name.replace('LGS-', 'PGS-', 1)
                return f"PGS-{schedule.name}"
        if not franchise_id:
            return 'PGS-STORE-0001'
        store = franchise_id if isinstance(franchise_id, models.Model) else self.env['wujia.franchise.management'].browse(franchise_id)
        if not store.exists():
            return 'PGS-STORE-0001'

        store_code = (store.code or store.name or 'STORE').strip().replace(' ', '_')

        if seq_number is None:
            seq_number = self.search_count([('franchise_id', '=', store.id)]) + 1

        candidate_name = f"PGS-{store_code}-{seq_number:04d}"

        # Kiểm tra trùng lặp: Nếu đã tồn tại candidate_name trong DB -> Gọi ĐỆ QUY tăng seq_number + 1
        if self.search_count([('name', '=', candidate_name)]):
            return self._generate_inspection_name(store, schedule_id=schedule_id, seq_number=seq_number + 1)

        return candidate_name

    @api.onchange('schedule_id', 'franchise_id')
    def _onchange_schedule_or_franchise_set_name(self):
        if self.schedule_id:
            self.name = self._generate_inspection_name(self.franchise_id, schedule_id=self.schedule_id)
        elif self.franchise_id:
            if not self.name or self.name.startswith('PGS-') or self.name.startswith('Khảo sát') or self.name == 'New':
                self.name = self._generate_inspection_name(self.franchise_id)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            franchise_id = vals.get('franchise_id')
            schedule_id = vals.get('schedule_id')
            current_name = vals.get('name')
            if not current_name or current_name == 'New' or current_name.startswith('Khảo sát') or not current_name.startswith('PGS-'):
                if schedule_id:
                    vals['name'] = self._generate_inspection_name(franchise_id, schedule_id=schedule_id)
                elif franchise_id:
                    vals['name'] = self._generate_inspection_name(franchise_id)
                elif not current_name:
                    count = self.search_count([]) + 1
                    vals['name'] = f"PGS-STORE-{count:04d}"
        return super(WujiaFranchiseInspection, self).create(vals_list)

   
    @api.depends('line_ids.is_pass', 'line_ids.result', 'line_ids.deduction_score_snapshot', 'line_ids.display_type')
    def _compute_checklist_score(self):
        """
        Mặc định điểm checklist là 95 điểm.
        Cứ mỗi tiêu chí Không đạt (is_pass == False hoặc result == 'fail'),
        sẽ bị trừ số điểm tương ứng (deduction_score_snapshot).
        Bỏ qua các dòng Section Header (display_type == 'section').
        """
        for rec in self:
            criteria_lines = rec.line_ids.filtered(lambda l: l.display_type == 'line')
            if not criteria_lines:
                if rec.template_id:
                    rec.checklist_score = rec.template_id.checklist_max_score
                else:
                    rec.checklist_score = 95.0
            else:
                total_deduction = sum(
                    line.deduction_score_snapshot
                    for line in criteria_lines
                    if not line.is_pass
                )
                rec.checklist_score = rec.template_id.checklist_max_score - total_deduction

    @api.onchange('template_id', 'franchise_id')
    def _onchange_template_id(self):
        """
        Tự động sao chép các dòng tiêu chí (bao gồm dòng Section) từ Mẫu khảo sát được chọn
        sang phiếu khảo sát theo đúng thứ tự đã cấu hình trong Template.
        Tự động tra cứu kết quả đợt khảo sát trước (nếu có).
        """
        if self.template_id:
            lines = []

            # Tra cứu phiếu khảo sát trước (cùng cửa hàng và cùng mẫu)
            prev_insp = self.previous_inspection_id
            if not prev_insp and self.franchise_id and self.template_id:
                domain = [
                    ('franchise_id', '=', self.franchise_id.id),
                    ('template_id', '=', self.template_id.id),
                ]
                current_id = self._origin.id if self._origin else (self.id if isinstance(self.id, int) else False)
                if current_id:
                    domain.append(('id', '!=', current_id))
                prev_insp = self.env['wujia.franchise.inspection'].search(domain, order='planned_date desc, id desc', limit=1)
                if prev_insp:
                    self.previous_inspection_id = prev_insp.id

            for t_line in self.template_id.line_ids:
                code_raw = (t_line.criterion_code or '').strip()
                sub_code = code_raw.split('.', 1)[1].strip() if '.' in code_raw else ''

                if t_line.display_type == 'section':
                    cat_name = t_line.category_id.name if t_line.category_id else (t_line.content or _("Section"))
                    if sub_code:
                        section_content = f"[{sub_code}] {cat_name}"
                    else:
                        section_content = cat_name

                    lines.append((0, 0, {
                        'sequence': t_line.sequence,
                        'display_type': 'section',
                        'template_line_id': t_line.id,
                        'category_id': t_line.category_id.id if t_line.category_id else False,
                        'content_snapshot': section_content,
                    }))
                else:
                    prev_l_id = False
                    prev_res = False
                    prev_ded = 0.0

                    if prev_insp:
                        target_tid = t_line.id
                        match_l = [
                            l for l in prev_insp.line_ids
                            if l.display_type == 'line' and l.template_line_id and l.template_line_id.id == target_tid
                        ]
                        if match_l:
                            prev_l_id = match_l[0].id
                            prev_res = 'pass' if match_l[0].is_pass else 'fail'
                            prev_ded = match_l[0].deduction_score_snapshot

                    cnt = (t_line.content or '').strip()
                    if code_raw and cnt.startswith(code_raw):
                        cnt = cnt[len(code_raw):].lstrip('. :-')
                    elif '.' in cnt[:10] and cnt[:10].split('.', 1)[0].replace('.', '').isdigit():
                        cnt = cnt.split('.', 1)[1].strip()

                    if sub_code:
                        content_str = f"[{sub_code}] {cnt}" if cnt else f"[{sub_code}]"
                    else:
                        content_str = cnt

                    lines.append((0, 0, {
                        'sequence': t_line.sequence,
                        'display_type': 'line',
                        'template_line_id': t_line.id,
                        'category_id': t_line.category_id.id if t_line.category_id else False,
                        'content_snapshot': content_str,
                        'deduction_score_snapshot': t_line.deduction_score or 0.0,
                        'criterion_type_snapshot': t_line.criterion_type or 'normal',
                        'require_note_if_fail_snapshot': t_line.require_note_if_fail,
                        'require_evidence_if_fail_snapshot': t_line.require_evidence_if_fail,
                        'is_pass': True,
                        'result': 'pass',
                        'previous_line_id': prev_l_id,
                        'previous_result': prev_res,
                        'previous_deduction_score': prev_ded,
                    }))

            self.line_ids = [(5, 0, 0)] + lines

            if not self.exam_line_ids:
                exam_lines = self._generate_random_exam_lines()
                if exam_lines:
                    self.exam_line_ids = exam_lines

    @api.onchange('previous_inspection_id')
    def _onchange_previous_inspection_id(self):
        """
        Khi Phiếu khảo sát trước (previous_inspection_id) được cập nhật,
        tự động tra cứu và cập nhật lại Kết quả đợt trước cho các dòng tiêu chí hiện tại.
        """
        if self.previous_inspection_id and self.line_ids:
            for line in self.line_ids:
                if line.display_type == 'section':
                    line.previous_line_id = False
                    line.previous_result = False
                    line.previous_deduction_score = 0.0
                    continue
                if line.template_line_id:
                    target_tid = line.template_line_id.id
                    match_l = [
                        l for l in self.previous_inspection_id.line_ids
                        if l.display_type == 'line' and l.template_line_id and l.template_line_id.id == target_tid
                    ]
                    if match_l:
                        line.previous_line_id = match_l[0].id
                        line.previous_result = 'pass' if match_l[0].is_pass else 'fail'
                        line.previous_deduction_score = match_l[0].deduction_score_snapshot
                    else:
                        line.previous_line_id = False
                        line.previous_result = False
                        line.previous_deduction_score = 0.0

    @api.depends('exam_line_ids.point', 'exam_line_ids.is_correct')
    def _compute_exam_score(self):
        """Tự động tính tổng điểm bài kiểm tra từ điểm của từng câu hỏi."""
        for rec in self:
            rec.exam_score = sum(line.point for line in rec.exam_line_ids)
            if rec.template_id:
                rec.exam_score = min(rec.template_id.exam_max_score, rec.exam_score)

    

    @api.onchange('checklist_score', 'exam_score')
    def _onchange_scores_update_total(self):
        """Khi điểm checklist hoặc điểm kiểm tra thay đổi, tự động tính lại tổng điểm và xếp loại lập tức."""
        for rec in self:
            rec.total_score = (rec.checklist_score or 0.0) + (rec.exam_score or 0.0)
            rec._compute_grade()
    
  

    def action_submit_exam(self):
        """
        Nộp bài kiểm tra nhân viên:
        - Yêu cầu phiếu khảo sát phải ở trạng thái 'Đang thực hiện' (in_progress).
        - So sánh đáp án trả lời của nhân viên với đáp án đúng snapshot.
        - Cập nhật điểm từng dòng: Đúng -> 1.0 (hoặc score), Sai/Bỏ trống -> 0.0.
        - Khóa bài làm và tính tổng điểm phiếu khảo sát.
        """
        for rec in self:
            if rec.state != 'in_progress':
                raise UserError(_("Phiếu khảo sát phải ở trạng thái 'Đang thực hiện' mới được phép nộp bài kiểm tra!"))

            for line in rec.exam_line_ids:
                line._evaluate_answer()
                score_val = (line.quest_id.score or 1.0) if line.is_correct else 0.0
                line.write({
                    'is_correct': line.is_correct,
                    'point': score_val,
                    'is_locked': True,
                })
            
            rec.write({
                'is_exam_submitted': True,
                'exam_submit_date': fields.Datetime.now(),
            })
            
            rec._compute_exam_score()
            rec._compute_checklist_score()
            rec._compute_total_score()
            rec._compute_grade()
            
        return True

    def action_start(self):
        """Chuyển phiếu khảo sát sang trạng thái Đang thực hiện và đồng bộ Lịch giám sát"""
        for rec in self:
            rec.write({'state': 'in_progress'})
        return True

    def _validate_failed_lines(self):
        """
        Kiểm tra tính hợp lệ của các dòng tiêu chí không đạt (Fail):
        1. require_note_if_fail: nếu True thì phải có note.
        2. require_evidence_if_fail: nếu True thì phải có evidence_image (hình ảnh bằng chứng khi khảo sát).
        """
        for rec in self:
            for line in rec.line_ids:
                if line.display_type == 'line' and not line.is_pass:
                    criterion_name = line.content_snapshot or (line.template_line_id.content if line.template_line_id else _('Tiêu chí'))
                    
                    req_note = line.require_note_if_fail or line.require_note_if_fail_snapshot
                    req_evidence = line.require_evidence_if_fail or line.require_evidence_if_fail_snapshot

                    if req_note and not line.note:
                        raise ValidationError(_(
                            'Tiêu chí "%s" được đánh giá KHÔNG ĐẠT và yêu cầu phải có GHI CHÚ vi phạm!\nVui lòng nhập ghi chú trước khi tiếp tục.'
                        ) % criterion_name)
                    
                    if req_evidence and not line.evidence_image:
                        raise ValidationError(_(
                            'Tiêu chí "%s" được đánh giá KHÔNG ĐẠT và yêu cầu phải có HÌNH ẢNH BẰNG CHỨNG!\nVui lòng tải ảnh bằng chứng lên trước khi tiếp tục.'
                        ) % criterion_name)

    def _validate_exam_lines(self):
        """
        Kiểm tra tính hợp lệ của bài kiểm tra kiến thức (exam_line_ids):
        Yêu cầu bài kiểm tra phải được bấm "Nộp bài kiểm tra" (is_exam_submitted = True) trước khi hoàn thành.
        """
        for rec in self:
            if rec.exam_line_ids and not rec.is_exam_submitted:
                raise ValidationError(_(
                    'Bài kiểm tra nhân viên chưa được nộp!\n'
                    'Vui lòng chuyển sang tab "Bài kiểm tra nhân viên" và bấm nút "Nộp bài kiểm tra" trước khi thực hiện Hoàn thành.'
                ))

    def action_need_remediation(self):
        """Chuyển phiếu khảo sát sang trạng thái Cần khắc phục & cập nhật trạng thái khắc phục cho tất cả tiêu chí"""
        for rec in self:
            rec._validate_failed_lines()
            rec._validate_exam_lines()
            for line in rec.line_ids.filtered(lambda l: l.display_type == 'line'):
                if not line.is_pass or line.result == 'fail':
                    line.write({'remediation_state': RemediationState.NEED_REMEDIATION.value})
                else:
                    line.write({'remediation_state': RemediationState.DONE.value})
            rec.write({'state': 'need_remediation'})
        return True

    def action_done(self):
        """Hoàn thành phiếu khảo sát, tự động lưu Ngày xác nhận và chuyển Lịch giám sát sang Hoàn thành"""
        today = fields.Date.context_today(self)
        for rec in self:
            rec._validate_failed_lines()
            rec._validate_exam_lines()
            failed_lines = rec.line_ids.filtered(lambda l: l.display_type == 'line' and not l.is_pass)
            uncompleted_lines = failed_lines.filtered(lambda l: l.remediation_state != RemediationState.DONE.value)
            if uncompleted_lines:
                raise UserError(_("Không thể hoàn thành phiếu khảo sát! Vẫn còn %s tiêu chí vi phạm chưa được xử lý Hoàn thành (Done).") % len(uncompleted_lines))
            rec.write({
                'state': 'done',
                'confirm_date': rec.confirm_date or today,
            })
        return True

    def action_cancel(self):
        """Hủy phiếu khảo sát và tự động chuyển Lịch giám sát sang Đã hủy"""
        for rec in self:
            rec.write({'state': 'cancel'})
        return True

    def action_draft(self):
        """Đặt lại phiếu khảo sát về trạng thái Nháp và đồng bộ Lịch giám sát"""
        for rec in self:
            rec.write({'state': 'draft'})
        return True

    def action_create_next_schedule(self):
        """
        Tạo hoặc mở Lịch giám sát tiếp theo dựa trên ngày chọn trong 'Lần kiểm tra kế tiếp' (next_due_date).
        """
        self.ensure_one()
        if not self.next_due_date:
            raise ValidationError(_('Vui lòng chọn ngày trong "Lần kiểm tra kế tiếp" trước khi tạo lịch!'))

        if not self.next_schedule_id:
            store_name = self.franchise_id.name or ''
            new_schedule = self.env['wujia.supervision.schedule'].create({
                'name': f"Lịch giám sát kế tiếp - {store_name}",
                'store_id': self.franchise_id.id,
                'user_id': self.inspector_user_id.id or self.env.user.id,
                'date': self.next_due_date,
                'state': 'draft',
                'note': f"Lịch được tạo tự động từ Phiếu khảo sát: {self.name}",
            })
            self.next_schedule_id = new_schedule.id

        return {
            'name': _('Lịch giám sát tiếp theo'),
            'type': 'ir.actions.act_window',
            'res_model': 'wujia.supervision.schedule',
            'res_id': self.next_schedule_id.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_open_inspection_detail(self):
        """Mở trang Website chuyên dụng để thực hiện khảo sát Checklist độc lập"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'url': f'/franchise/inspection/do/{self.id}',
            'target': 'self',
        }

    def write(self, vals):
        if 'name' in vals and not self.env.su:
            for rec in self:
                if rec.name and vals['name'] != rec.name:
                    raise ValidationError(_("Không thể thay đổi Mã/Tên phiếu khảo sát (%s) sau khi đã tạo!") % rec.name)

        if vals.get('state') == 'need_remediation':
            for rec in self:
                for line in rec.line_ids.filtered(lambda l: l.display_type == 'line'):
                    if not line.is_pass or line.result == 'fail':
                        if line.remediation_state != RemediationState.REMEDIATED.value and line.remediation_state != RemediationState.DONE.value:
                            line.remediation_state = RemediationState.NEED_REMEDIATION.value
                    else:
                        line.remediation_state = RemediationState.DONE.value

        if vals.get('state') == 'done':
            for rec in self:
                failed_lines = rec.line_ids.filtered(lambda l: l.display_type == 'line' and not l.is_pass)
                uncompleted_lines = failed_lines.filtered(lambda l: l.remediation_state != RemediationState.DONE.value)
                if uncompleted_lines:
                    raise UserError(_("Không thể chuyển phiếu khảo sát sang Hoàn thành! Vẫn còn %s tiêu chí vi phạm chưa ở trạng thái Hoàn thành (Done).") % len(uncompleted_lines))

        if vals.get('state') == 'done' and 'confirm_date' not in vals:
            vals['confirm_date'] = fields.Date.context_today(self)
        res = super().write(vals)
        if 'state' in vals:
            for rec in self:
                if rec.schedule_id:
                    schedule_state_keys = dict(rec.schedule_id._fields['state'].selection)
                    if vals['state'] in schedule_state_keys and rec.schedule_id.state != vals['state']:
                        rec.schedule_id.state = vals['state']
        return res

    def _generate_random_exam_lines(self):
        """Tự động lấy ngẫu nhiên danh sách câu hỏi từ wujia.franchise.inspection.question sao cho tổng điểm bằng exam_max_score"""
        questions = self.env['wujia.franchise.inspection.question'].search([('active', '=', True)])
        if not questions:
            return []
        
        target_exam_score = self.template_id.exam_max_score if (self.template_id and self.template_id.exam_max_score) else 5.0
        
        all_q = list(questions)
        total_available_score = sum(q.score or 1.0 for q in all_q)
        
        if total_available_score <= target_exam_score:
            selected_questions = all_q
        else:
            random.shuffle(all_q)
            selected_questions = []
            
            def backtrack(idx, current_sum, path):
                if abs(current_sum - target_exam_score) < 0.001:
                    return path
                if idx >= len(all_q) or current_sum > target_exam_score + 0.001:
                    return None
                
                res = backtrack(idx + 1, current_sum + (all_q[idx].score or 1.0), path + [all_q[idx]])
                if res is not None:
                    return res
                
                res = backtrack(idx + 1, current_sum, path)
                if res is not None:
                    return res
                
                return None
            
            found = backtrack(0, 0.0, [])
            if found is not None:
                selected_questions = found
            else:
                current_sum = 0.0
                for q in all_q:
                    score = q.score or 1.0
                    if current_sum + score <= target_exam_score + 0.001:
                        selected_questions.append(q)
                        current_sum += score

        exam_lines = []
        seq = 10
        for q in selected_questions:
            correct_snap = q.correct_answers_text
            if not correct_snap and q.correct_answers:
                if isinstance(q.correct_answers, list):
                    lines = []
                    for item in q.correct_answers:
                        if isinstance(item, list):
                            lines.append('; '.join(str(x) for x in item))
                        elif item:
                            lines.append(str(item))
                    correct_snap = '\n'.join(lines)

            exam_lines.append((0, 0, {
                'sequence': seq,
                'quest_id': q.id,
                'quest_code_snapshot': q.code or f"QUEST-{q.id}",
                'quest_content_snapshot': q.question_text or '',
                'correct_answer_snapshot': correct_snap or '',
                'answer': '',
                'is_correct': False,
                'point': q.score or 1.0,
            }))
            seq += 10
        return exam_lines

    @api.depends('franchise_id', 'template_id')
    def _compute_previous_inspection_id(self):
        """
        Tự động lấy phiếu khảo sát gần nhất có cùng Cửa hàng (franchise_id)
        và cùng Mẫu khảo sát (template_id).
        """
        valid_recs = self.filtered(lambda r: r.franchise_id and r.template_id)
        if not valid_recs:
            for rec in self:
                rec.previous_inspection_id = False
            return

        franchise_ids = list(set(valid_recs.mapped('franchise_id').ids))
        template_ids = list(set(valid_recs.mapped('template_id').ids))
        current_ids = [r._origin.id if r._origin else r.id for r in valid_recs if (r._origin.id or isinstance(r.id, int))]

        domain = [
            ('franchise_id', 'in', franchise_ids),
            ('template_id', 'in', template_ids),
            ('state', '!=', 'cancel'),
        ]
        if current_ids:
            domain.append(('id', 'not in', current_ids))

        groups = self.env['wujia.franchise.inspection']._read_group(
            domain=domain,
            groupby=['franchise_id', 'template_id'],
            aggregates=['id:max'],
        )
        prev_map = {
            (f.id, t.id): max_id
            for f, t, max_id in groups if f and t and max_id
        }

        for rec in self:
            if rec.franchise_id and rec.template_id:
                rec.previous_inspection_id = prev_map.get((rec.franchise_id.id, rec.template_id.id), False)
            else:
                rec.previous_inspection_id = False
    
    confirmed_user_id = fields.Many2one('res.users',
        string='field:wujia.franchise.inspection:confirmed_user_id',
        required=True,
        ondelete='restrict',
        default=lambda self: self.env.user
    )
    confirmed_member_id = fields.Many2one('wujia.franchise.member',
        string='field:wujia.franchise.inspection:confirmed_member_id',
        required=True,
        ondelete='restrict',
    )

    @api.onchange('schedule_id')
    def _onchange_schedule_id(self):
        if self.schedule_id:
            self.planned_date = self.schedule_id.date
            if self.schedule_id.store_id:
                self.franchise_id = self.schedule_id.store_id
            if self.schedule_id.user_id:
                self.inspector_user_id = self.schedule_id.user_id

    @api.onchange('line_ids', 'exam_line_ids')
    def _onchange_lines_update_scores(self):
        """
        Cập nhật REAL-TIME lập tức khi người dùng bật/tắt Đánh giá Đạt hoặc trả lời bài kiểm tra
        ngay trên giao diện form mà chưa cần bấm nút Lưu (Save).
        """
        for rec in self:
            rec._compute_checklist_score()
            rec._compute_exam_score()
            rec.total_score = (rec.checklist_score or 0.0) + (rec.exam_score or 0.0)
            rec._compute_grade()
    
    @api.depends(
        'checklist_score',
        'exam_score',
        'line_ids.is_pass',
        'line_ids.deduction_score_snapshot',
        'line_ids.display_type',
        'exam_line_ids.is_correct',
        'exam_line_ids.point',
        'is_exam_submitted'
    )
    def _compute_total_score(self):
        """
        Tự động chạy khi 'checklist_score', 'exam_score' hoặc các dòng tiêu chí thay đổi.
        Cộng 2 điểm thành phần (checklist_score + exam_score) để tạo thành total_score.
        """
        for rec in self:
            rec.total_score = (rec.checklist_score or 0.0) + (rec.exam_score or 0.0)

    @api.depends(
        'total_score',
        'checklist_score',
        'exam_score',
        'line_ids.is_pass',
        'line_ids.deduction_score_snapshot',
        'exam_line_ids.is_correct'
    )
    def _compute_grade(self):
        """
        Tự động chạy khi 'total_score' thay đổi.
        Tính 'grade_id' dựa trên 'total_score' bằng cách tra cứu model cấu hình.
        """
        GradeModel = self.env['wujia.franchise.inspection.grade'].sudo()
        all_grades = GradeModel.search([], order='min_score desc')
        for rec in self:
            score = rec.total_score or 0.0
            matched_grade = GradeModel
            for grade in all_grades:
                if grade.min_score <= score <= grade.max_score:
                    matched_grade = grade
                    break
            rec.grade_id = matched_grade

    @api.model_create_multi
    def create(self, vals_list):
        """Tự động tạo 5 câu hỏi ngẫu nhiên cho bài kiểm tra nếu chưa có khi tạo phiếu khảo sát mới."""
        for vals in vals_list:
            if 'exam_line_ids' not in vals or not vals['exam_line_ids']:
                exam_lines = self._generate_random_exam_lines()
                if exam_lines:
                    vals['exam_line_ids'] = exam_lines
        return super().create(vals_list)

class WujiaFranchiseInspectionLine(models.Model):

    def action_toggle_remediation_state(self):
        for line in self:
            if line.remediation_state == RemediationState.DONE.value:
                line.write({'remediation_state': RemediationState.NEED_REMEDIATION.value})
            else:
                line.write({'remediation_state': RemediationState.DONE.value})
        return True

    _name = 'wujia.franchise.inspection.line'
    _description = 'Từng dòng tiêu chí trong phiếu khảo sát đánh giá cửa hàng nhượng quyền'
    _order = 'sequence, id'

    sequence = fields.Integer(string='Thứ tự', default=10)
    display_type = fields.Selection([
        ('section', 'Section'),
        ('line', 'Line'),
    ], default='line', help="Trường kỹ thuật phân nhóm danh mục section header")

    content_snapshot = fields.Text(
        string='Nội dung kiểm tra checklist',
    )

    deduction_score_snapshot = fields.Float(
        string='Điểm trừ',
        default=0.0,
    )

    criterion_type_snapshot = fields.Char(
        string='Loại tiêu chí',
        default='normal',
    )

    is_pass = fields.Boolean(
        string='Đánh giá Đạt (Pass)',
        default=True,
    )

    result = fields.Selection(
        selection=[
            ('pass', 'selection:wujia.franchise.inspection.line:result:pass'),
            ('fail', 'selection:wujia.franchise.inspection.line:result:fail')
        ],
        string='Kết quả',
        default='pass',
        required=True,
    )

    note = fields.Text(
        string='Ghi chú vi phạm (Admin)',
    )

    remediation_state = fields.Selection([
        (RemediationState.NEED_REMEDIATION.value, 'selection:wujia.franchise.inspection.line:remediation_state:need_remediation'),
        (RemediationState.REMEDIATED.value, 'selection:wujia.franchise.inspection.line:remediation_state:remediated'),
        (RemediationState.DONE.value, 'selection:wujia.franchise.inspection.line:remediation_state:done'),
    ], string='Trạng thái khắc phục', tracking=True)

    remediation_note = fields.Text(
        string='Ghi chú khắc phục (Cửa hàng)',
        help='Ghi chú phản hồi/khắc phục do cửa hàng nhập từ Portal.'
    )

    evidence_image = fields.Binary(
        string='Hình ảnh bằng chứng (Khi khảo sát)',
        attachment=True,
        help='Hình ảnh bằng chứng chụp vi phạm khi thực hiện khảo sát.'
    )

    remediation_image = fields.Binary(
        string='Hình ảnh sau khắc phục',
        attachment=True,
        help='Hình ảnh chụp lại kết quả sau khi cửa hàng đã thực hiện khắc phục vi phạm.'
    )

    require_note_if_fail = fields.Boolean(
        string='Yêu cầu ghi chú khi không đạt',
        related='template_line_id.require_note_if_fail',
        readonly=True,
        store=True,
    )

    require_evidence_if_fail = fields.Boolean(
        string='Yêu cầu bằng chứng khi không đạt',
        related='template_line_id.require_evidence_if_fail',
        readonly=True,
        store=True,
    )

    require_note_if_fail_snapshot = fields.Boolean(
        string='Snapshot yêu cầu ghi chú',
        default=False,
    )

    require_evidence_if_fail_snapshot = fields.Boolean(
        string='Snapshot yêu cầu bằng chứng',
        default=False,
    )
    
    # RELATION 
    inspection_id = fields.Many2one(
        'wujia.franchise.inspection',
        string='Phiếu khảo sát',
        required=True,
        ondelete='cascade',
    )

    template_line_id = fields.Many2one(
        'wujia.franchise.inspection.template.line',
        string='Tiêu chí',
        required=False,
        ondelete='restrict',
    )

    template_id = fields.Many2one(
        'wujia.franchise.inspection.template',
        related='inspection_id.template_id',
        string='Mẫu khảo sát',
        store=True,
        readonly=True,
    )

    franchise_id = fields.Many2one(
        'wujia.franchise.management',
        related='inspection_id.franchise_id',
        string='Cửa hàng',
        store=True,
        readonly=True,
    )

    planned_date = fields.Date(
        related='inspection_id.planned_date',
        string='Ngày kiểm tra',
        store=True,
        readonly=True,
    )

    pass_count = fields.Integer(
        string='Số lần Đạt',
        compute='_compute_pass_fail_count',
        store=True,
    )

    fail_count = fields.Integer(
        string='Số lần Vi phạm (Không đạt)',
        compute='_compute_pass_fail_count',
        store=True,
    )

    line_count = fields.Integer(
        string='Số lượt kiểm tra',
        default=1,
    )

    category_id = fields.Many2one(
        'wujia.franchise.inspection.category',
        string='Danh mục tiêu chí',
        ondelete='restrict',
    )

    previous_line_id = fields.Many2one(
        'wujia.franchise.inspection.line',
        string='Line trước',
        compute='_compute_previous_line_info',
        store=True,
        readonly=True,
    )

    previous_result = fields.Selection(
        selection=[
            ('pass', 'selection:wujia.franchise.inspection.line:previous_result:pass'),
            ('fail', 'selection:wujia.franchise.inspection.line:previous_result:fail')
        ],
        string='Kết quả trước đó',
        compute='_compute_previous_line_info',
        store=True,
        readonly=True,
    )

    previous_deduction_score = fields.Float(
        string='Điểm trừ đợt trước',
        compute='_compute_previous_line_info',
        store=True,
        readonly=True,
    )

    previous_inspection_id = fields.Many2one(
        'wujia.franchise.inspection',
        related='inspection_id.previous_inspection_id',
        string='Phiếu khảo sát đợt trước',
        readonly=True,
    )
    
    content_class = fields.Char(
        string="CSS Class cho nội dung", 
        compute="_compute_content_class",
    )
    
    @api.onchange('is_pass')
    def _onchange_is_pass(self):
        if self.is_pass:
            self.result = 'pass'
        else:
            self.result = 'fail'

    @api.onchange('result')
    def _onchange_result(self):
        if self.result == 'pass':
            self.is_pass = True
        else:
            self.is_pass = False
    
 
    @api.onchange('is_pass', 'result')
    def _onchange_is_pass_remediation_state(self):
        if self.is_pass or self.result == 'pass':
            self.remediation_state = RemediationState.DONE.value
        else:
            if not self.remediation_state or self.remediation_state == RemediationState.DONE.value:
                self.remediation_state = RemediationState.NEED_REMEDIATION.value
    
   

    @api.depends('is_pass', 'result', 'display_type')
    def _compute_pass_fail_count(self):
        for rec in self:
            if rec.display_type == 'line':
                rec.pass_count = 1 if (rec.is_pass or rec.result == 'pass') else 0
                rec.fail_count = 0 if (rec.is_pass or rec.result == 'pass') else 1
                rec.line_count = 1
            else:
                rec.pass_count = 0
                rec.fail_count = 0
                rec.line_count = 0

   

    def action_view_previous_inspection(self):
        """Mở popup Form View xem duy nhất 1 dòng tiêu chí đợt trước (Readonly)"""
        self.ensure_one()
        if not self.previous_line_id:
            raise ValidationError(_('Không có dữ liệu tiêu chí này ở đợt khảo sát trước!'))
        return {
            'name': _('Tiêu chí đợt trước: %s') % (self.content_snapshot or ''),
            'type': 'ir.actions.act_window',
            'res_model': 'wujia.franchise.inspection.line',
            'res_id': self.previous_line_id.id,
            'view_mode': 'form',
            'target': 'new',
            'context': {'create': False, 'edit': False},
        }

    # 2. Phương thức tính toán class
    @api.depends('display_type')
    def _compute_content_class(self):
        for line in self:
            # Kiểm tra nếu là dòng Section
            if line.display_type == 'section':
                line.content_class = 'text-center fw-bold d-block w-100 py-1'
            else:
                line.content_class = ''

    @api.depends('inspection_id.previous_inspection_id', 'template_line_id')
    def _compute_previous_line_info(self):
        """
        Tự động liên kết dòng tiêu chí đợt trước (previous_line_id) có cùng Mẫu tiêu chí (template_line_id),
        đồng thời lưu trữ luôn Kết quả đợt trước (previous_result) và Điểm trừ đợt trước (previous_deduction_score).
        """
        for rec in self:
            if rec.display_type == 'section':
                rec.previous_line_id = False
                rec.previous_result = False
                rec.previous_deduction_score = 0.0
                continue

            prev_insp = rec.inspection_id.previous_inspection_id if rec.inspection_id else False
            if prev_insp and rec.template_line_id:
                target_tid = rec.template_line_id.id
                match_lines = [
                    l for l in prev_insp.line_ids
                    if l.display_type == 'line' and l.template_line_id and l.template_line_id.id == target_tid
                ]
                if match_lines:
                    prev_l = match_lines[0]
                    rec.previous_line_id = prev_l.id
                    rec.previous_result = 'pass' if prev_l.is_pass else 'fail'
                    rec.previous_deduction_score = prev_l.deduction_score_snapshot
                else:
                    rec.previous_line_id = False
                    rec.previous_result = False
                    rec.previous_deduction_score = 0.0
            else:
                rec.previous_line_id = False
                rec.previous_result = False
                rec.previous_deduction_score = 0.0

    @api.onchange('template_line_id')
    def _onchange_template_line_id(self):
        """
        Khi chọn Mẫu tiêu chí (template_line_id), tự động nạp nội dung, điểm trừ,
        loại tiêu chí và danh mục vào các trường snapshot tương ứng.
        """
        if self.template_line_id:
            self.category_id = self.template_line_id.category_id
            self.content_snapshot = self.template_line_id.content
            self.deduction_score_snapshot = self.template_line_id.deduction_score
            self.criterion_type_snapshot = self.template_line_id.criterion_type
            self.require_note_if_fail_snapshot = self.template_line_id.require_note_if_fail
            self.require_evidence_if_fail_snapshot = self.template_line_id.require_evidence_if_fail

    @api.model_create_multi
    def create(self, vals_list):
        """
        Bảo đảm dữ liệu content_snapshot, deduction_score_snapshot, criterion_type_snapshot
        và template_line_id luôn được lưu chính xác và vĩnh viễn vào CSDL khi bấm Lưu (Save).
        """
        for vals in vals_list:
            if vals.get('display_type') == 'section':
                continue

            # Đồng bộ result chuẩn xác theo is_pass
            if 'is_pass' in vals:
                vals['result'] = 'pass' if vals['is_pass'] else 'fail'

            # 1. Tự động phục hồi template_line_id nếu web client truyền null/False
            if not vals.get('template_line_id') and vals.get('content_snapshot'):
                insp = False
                if vals.get('inspection_id'):
                    insp = self.env['wujia.franchise.inspection'].browse(vals['inspection_id'])
                
                if insp and insp.exists() and insp.template_id:
                    t_line = insp.template_id.line_ids.filtered(
                        lambda l: l.content == vals['content_snapshot']
                    )
                    if t_line:
                        vals['template_line_id'] = t_line[0].id

                if not vals.get('template_line_id'):
                    t_line = self.env['wujia.franchise.inspection.template.line'].search([
                        ('content', '=', vals['content_snapshot'])
                    ], limit=1)
                    if t_line:
                        vals['template_line_id'] = t_line.id

            # 2. Điền thông tin snapshot từ template_line_id
            if vals.get('template_line_id'):
                t_line = self.env['wujia.franchise.inspection.template.line'].browse(vals['template_line_id'])
                if t_line.exists():
                    if not vals.get('category_id') and t_line.category_id:
                        vals['category_id'] = t_line.category_id.id
                    if not vals.get('content_snapshot'):
                        vals['content_snapshot'] = t_line.content
                    if 'deduction_score_snapshot' not in vals:
                        vals['deduction_score_snapshot'] = t_line.deduction_score
                    if not vals.get('criterion_type_snapshot'):
                        vals['criterion_type_snapshot'] = t_line.criterion_type
                    if 'require_note_if_fail_snapshot' not in vals:
                        vals['require_note_if_fail_snapshot'] = t_line.require_note_if_fail
                    if 'require_evidence_if_fail_snapshot' not in vals:
                        vals['require_evidence_if_fail_snapshot'] = t_line.require_evidence_if_fail

            # 3. Tự động phục hồi dòng đợt trước (previous_line_id)
            if vals.get('inspection_id') and vals.get('template_line_id') and not vals.get('previous_result'):
                insp = self.env['wujia.franchise.inspection'].browse(vals['inspection_id'])
                if insp.exists() and insp.previous_inspection_id:
                    target_tid = vals['template_line_id']
                    match_l = [
                        l for l in insp.previous_inspection_id.line_ids
                        if l.display_type == 'line' and l.template_line_id and l.template_line_id.id == target_tid
                    ]
                    if match_l:
                        vals['previous_line_id'] = match_l[0].id
                        vals['previous_result'] = 'pass' if match_l[0].is_pass else 'fail'
                        vals['previous_deduction_score'] = match_l[0].deduction_score_snapshot

        return super().create(vals_list)

    def write(self, vals):
        if vals.get('state') == 'need_remediation':
            for rec in self:
                for line in rec.line_ids.filtered(lambda l: l.display_type == 'line'):
                    if not line.is_pass or line.result == 'fail':
                        if line.remediation_state != RemediationState.REMEDIATED.value and line.remediation_state != RemediationState.DONE.value:
                            line.remediation_state = RemediationState.NEED_REMEDIATION.value
                    else:
                        line.remediation_state = RemediationState.DONE.value

        if vals.get('state') == 'done':
            for rec in self:
                failed_lines = rec.line_ids.filtered(lambda l: l.display_type == 'line' and not l.is_pass)
                uncompleted_lines = failed_lines.filtered(lambda l: l.remediation_state != RemediationState.DONE.value)
                if uncompleted_lines:
                    raise UserError(_("Không thể chuyển phiếu khảo sát sang Hoàn thành! Vẫn còn %s tiêu chí vi phạm chưa ở trạng thái Hoàn thành (Done).") % len(uncompleted_lines))

        if 'is_pass' in vals:
            vals['result'] = 'pass' if vals['is_pass'] else 'fail'

        if not vals.get('template_line_id') and vals.get('content_snapshot'):
            t_line = self.env['wujia.franchise.inspection.template.line'].search([
                ('content', '=', vals['content_snapshot'])
            ], limit=1)
            if t_line:
                vals['template_line_id'] = t_line.id

        if 'template_line_id' in vals and vals['template_line_id']:
            t_line = self.env['wujia.franchise.inspection.template.line'].browse(vals['template_line_id'])
            if t_line.exists():
                if 'category_id' not in vals and t_line.category_id:
                    vals['category_id'] = t_line.category_id.id
                if 'content_snapshot' not in vals:
                    vals['content_snapshot'] = t_line.content
                if 'deduction_score_snapshot' not in vals:
                    vals['deduction_score_snapshot'] = t_line.deduction_score
                if 'criterion_type_snapshot' not in vals:
                    vals['criterion_type_snapshot'] = t_line.criterion_type
        return super().write(vals)

    @api.depends('template_line_id', 'content_snapshot', 'display_type')
    def _compute_display_name(self):
        """
        Tự động tính toán tên hiển thị ngắn gọn cho bản ghi.
        Lấy từ template_line_id và content_snapshot.
        """
        for rec in self:
            if rec.display_type == 'section':
                rec.display_name = rec.content_snapshot or _("Danh mục tiêu chí")
            elif rec.template_line_id:
                code = rec.template_line_id.criterion_code or ''
                rec.display_name = f"[{code}] {rec.content_snapshot or ''}" if code else (rec.content_snapshot or '')
            else:
                rec.display_name = rec.content_snapshot or _("Tiêu chí không xác định")

class WujiaFranchiseInspectionReportLine(models.Model):
    _name = 'wujia.franchise.inspection.report.line'
    _description = 'Từng dòng báo cáo tài chính trong 3 tháng'
    _order = 'sequence, id'

    sequence = fields.Integer(string='Thứ tự', default=10)

    date_month = fields.Date(
        string='Tháng (YYYY-MM)',
        required=True,
    )
    
    days_of_month = fields.Integer(
        string='Số ngày trong tháng',
        compute='_compute_days_of_month',
        store=True,
    )

    revenue = fields.Float(
        string='Doanh thu',
        required=True,
    )

    revenue_avg = fields.Float(
        string='Doanh thu / ngày',
        compute='_compute_revenue_avg',
        store=True,
        readonly=False,
    )

    total_app_sale = fields.Integer(
        string='Tổng giao dịch qua app',
        required=True,
    )

    percent_app_sale = fields.Float(
        string='% giao dịch qua app',
        required=True,
    )

    # RELATION
    inspection_id = fields.Many2one(
        'wujia.franchise.inspection',
        string='Phiếu khảo sát',
        required=True,
        ondelete='cascade',
    )

    @api.depends('date_month')
    def _compute_days_of_month(self):
        for rec in self:
            if rec.date_month:
                try:
                    period = pd.Period(rec.date_month)
                    rec.days_of_month = period.days_in_month
                except Exception:
                    rec.days_of_month = 30
            else:
                rec.days_of_month = 0

    @api.depends('revenue', 'days_of_month')
    def _compute_revenue_avg(self):
        for rec in self:
            if rec.days_of_month and rec.days_of_month > 0:
                rec.revenue_avg = round(rec.revenue / rec.days_of_month, 2)
            else:
                rec.revenue_avg = 0.0


    
class WujiaFranchiseInspectionExamLine(models.Model):
    _name = 'wujia.franchise.inspection.exam.line'
    _description = 'Điểm kiểm tra phiếu khảo sát đánh giá cửa hàng nhượng quyền'
    _order = 'sequence, id'

    sequence = fields.Integer(
        string='Thứ tự',
        default=10,
    )

    quest_code_snapshot = fields.Char(
        string='Mã câu hỏi',
        required=True,
    )

    quest_content_snapshot = fields.Text(
        string='Nội dung câu hỏi',
        required=True,
    )

    correct_answer_snapshot = fields.Text(
        string='Đáp án đúng',
    )
    answer = fields.Text(
        string='Đáp án trả lời',
    )

    is_correct = fields.Boolean(
        string='Đúng',
        default=False,
    )
    point = fields.Float(
        string='Điểm',
        default=1.0,
    )

    is_locked = fields.Boolean(
        string='Khóa',
        default=False,
    )

    # RELATION
    inspection_id = fields.Many2one(
        'wujia.franchise.inspection',
        string='Phiếu khảo sát',
        required=True,
        ondelete='cascade',
    )
    quest_id = fields.Many2one(
        'wujia.franchise.inspection.question',
        string='Câu hỏi',
        required=True,
        ondelete='cascade',
    )

    # DISPLAY
    _point_return = fields.Float(
        string='Điểm',
        compute='_compute_point',
    )

    @api.depends('is_correct', 'quest_id')
    def _compute_point(self):
        for rec in self:
            if rec.is_correct:
                if rec.quest_id and rec.quest_id.score:
                    rec._point_return = rec.quest_id.score
                else:
                    rec._point_return = 1.0
            else:
                rec._point_return = 0.0

    @api.onchange('answer')
    def _onchange_answer(self):
        """Tự động kiểm tra đáp án trả lời với đáp án đúng trong thư viện câu hỏi"""
        self._evaluate_answer()

    def _evaluate_answer(self):
        """So sánh đáp án trả lời của nhân viên với đáp án đúng snapshot"""
        import re
        for rec in self:
            max_score = rec.quest_id.score if (rec.quest_id and rec.quest_id.score) else 1.0
            if not rec.answer:
                rec.is_correct = False
                rec.point = 0.0
                continue
            
            ans_raw = str(rec.answer).strip()
            if not ans_raw:
                rec.is_correct = False
                rec.point = 0.0
                continue

            if '\n' in ans_raw:
                user_lines = [l.strip().lower() for l in ans_raw.splitlines() if l.strip()]
            else:
                user_lines = [l.strip().lower() for l in re.split(r'[\n,;]+', ans_raw) if l.strip()]

            is_right = False

            # 1. Ưu tiên kiểm tra dữ liệu JSON correct_answers từ quest_id
            if rec.quest_id and rec.quest_id.correct_answers:
                val = rec.quest_id.correct_answers
                if isinstance(val, list) and val:
                    if len(val) > 1:
                        if len(user_lines) >= len(val):
                            all_matched = True
                            for idx, target in enumerate(val):
                                target_list = [str(x).strip().lower() for x in (target if isinstance(target, list) else [target])]
                                if idx < len(user_lines):
                                    if user_lines[idx] not in target_list:
                                        all_matched = False
                                        break
                                else:
                                    all_matched = False
                                    break
                            is_right = all_matched
                    else:
                        target_list = [str(x).strip().lower() for x in (val[0] if isinstance(val[0], list) else val)]
                        is_right = (ans_raw.strip().lower() in target_list) or any(u in target_list for u in user_lines)

            # 2. Fallback so sánh với correct_answer_snapshot
            if not is_right and rec.correct_answer_snapshot:
                snap_raw = str(rec.correct_answer_snapshot).strip()
                if '\n' in snap_raw:
                    snap_lines = [l.strip().lower() for l in snap_raw.splitlines() if l.strip()]
                else:
                    snap_lines = [l.strip().lower() for l in re.split(r'[\n,;]+', snap_raw) if l.strip()]

                if len(snap_lines) > 1:
                    is_right = (user_lines == snap_lines)
                else:
                    is_right = (ans_raw.strip().lower() == snap_lines[0]) or any(u == snap_lines[0] for u in user_lines)

            rec.is_correct = is_right
            rec.point = max_score if is_right else 0.0

    