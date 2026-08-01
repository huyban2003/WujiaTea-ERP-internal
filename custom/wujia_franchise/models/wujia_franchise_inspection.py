# -*- coding: utf-8 -*-
import random
from odoo import api, fields, models, _
# pyrefly: ignore [missing-import]
from odoo.exceptions import ValidationError


class WujiaFranchiseInspection(models.Model):
    _name = 'wujia.franchise.inspection'
    _description = 'Phiếu khảo sát đánh giá cửa hàng nhượng quyền'
    _order = 'id desc'

    name = fields.Char(string='Tên phiếu khảo sát', required=True)

    submit_date = fields.Date(
        string='Ngày nộp'
    )
    confirm_date = fields.Date(
        string='Ngày xác nhận'
    )

    state = fields.Selection([
        ('draft', 'Nháp'),
        ('in_progress', 'Đang thực hiện'),
        ('need_remediation', 'Cần khắc phục'),
        ('done', 'Hoàn thành'),
        ('cancel', 'Đã hủy')
    ], string='Trạng thái', default='draft')

    planned_date = fields.Date(
        string='Ngày dự kiến',
    )

    checklist_score = fields.Float(
        string='Điểm checklist',
        compute='_compute_checklist_score',
        store=True,
        readonly=True,
        default=95.0,
    )

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

    def _select_random_template_lines(self, template):
        """
        Chọn ngẫu nhiên tập hợp các tiêu chí từ template.line_ids sao cho:
        1. Giữ lại tất cả các tiêu chí 'critical' (Quan trọng/Điểm liệt).
        2. Bốc ngẫu nhiên các tiêu chí 'normal' để tổng điểm bằng checklist_max_score của Template.
        """
        all_lines = list(template.line_ids)
        target_score = template.checklist_max_score or 95.0

        # Nếu tổng điểm của toàn bộ câu trong template <= checklist_max_score thì trả về toàn bộ
        total_template_score = sum(l.deduction_score or 0.0 for l in all_lines)
        if total_template_score <= target_score:
            return all_lines

        critical_lines = [l for l in all_lines if l.criterion_type == 'critical']
        normal_lines = [l for l in all_lines if l.criterion_type != 'critical']

        critical_score = sum(l.deduction_score or 0.0 for l in critical_lines)
        if critical_score >= target_score:
            return critical_lines

        remaining_target = target_score - critical_score

        random.shuffle(normal_lines)

        selected_normal = []
        
        def backtrack(idx, current_sum, path):
            if abs(current_sum - remaining_target) < 0.001:
                return path
            if idx >= len(normal_lines) or current_sum > remaining_target + 0.001:
                return None
            
            res = backtrack(idx + 1, current_sum + (normal_lines[idx].deduction_score or 0.0), path + [normal_lines[idx]])
            if res is not None:
                return res
                
            res = backtrack(idx + 1, current_sum, path)
            if res is not None:
                return res
                
            return None

        found_path = backtrack(0, 0.0, [])
        if found_path is not None:
            selected_normal = found_path
        else:
            current_sum = 0.0
            for l in normal_lines:
                score = l.deduction_score or 0.0
                if current_sum + score <= remaining_target + 0.001:
                    selected_normal.append(l)
                    current_sum += score

        return critical_lines + selected_normal

    def action_randomize_criteria(self):
        """Bốc lại bộ câu hỏi ngẫu nhiên khi ở trạng thái Draft"""
        for rec in self:
            if rec.state != 'draft':
                raise ValidationError(_('Chỉ có thể bốc lại câu hỏi khi phiếu ở trạng thái Nháp!'))
            if not rec.template_id:
                raise ValidationError(_('Vui lòng chọn Mẫu khảo sát trước!'))
            rec.exam_line_ids = [(5, 0, 0)] + rec._generate_random_exam_lines()
            rec._onchange_template_id()

    @api.onchange('template_id', 'franchise_id')
    def _onchange_template_id(self):
        """
        Tự động sinh các dòng tiêu chí khảo sát phân nhóm theo Danh mục (Section Header)
        dựa trên Mẫu khảo sát được chọn. Tự động tra cứu kết quả đợt khảo sát trước (nếu có).
        """
        if self.template_id:
            lines = []
            seq = 10
            grouped_lines = {}
            target_lines = self._select_random_template_lines(self.template_id)
            for t_line in target_lines:
                cat = t_line.category_id
                cat_key = cat.id if cat else (t_line.category or 'general')
                if cat_key not in grouped_lines:
                    cat_name = cat.name if cat else (t_line.category or _("Tiêu chí chung"))
                    grouped_lines[cat_key] = {
                        'name': cat_name,
                        'lines': []
                    }
                grouped_lines[cat_key]['lines'].append(t_line)

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

            for cat_key, cat_info in grouped_lines.items():
                cat_name = cat_info['name']
                t_lines = cat_info['lines']
                total_cat_deduction = sum(l.deduction_score or 0.0 for l in t_lines)
                section_title = f"{cat_name} ({total_cat_deduction:.0f} điểm)"

                # 1. Thêm dòng tiêu đề Danh mục (Section Header)
                lines.append((0, 0, {
                    'sequence': seq,
                    'display_type': 'section',
                    'content_snapshot': section_title,
                }))
                seq += 10

                # 2. Thêm các tiêu chí chi tiết thuộc danh mục đó
                for t_line in t_lines:
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

                    lines.append((0, 0, {
                        'sequence': seq,
                        'display_type': 'line',
                        'template_line_id': t_line.id,
                        'category_id': t_line.category_id.id if t_line.category_id else False,
                        'content_snapshot': t_line.content,
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
                    seq += 10

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

    exam_score = fields.Float(
        string='Điểm kiểm tra',
        compute='_compute_exam_score',
        store=True,
        _description='là điểm được lấy từ câu hỏi phần điền vào ô trống',
    )

    total_score = fields.Float(
        string='Tổng điểm',
        compute='_compute_total_score',
        store=True,
        _description='điểm = điểm checklist + điểm kiểm tra'
    )

    grade_id = fields.Many2one(
        'wujia.franchise.inspection.grade',
        string='Xếp loại',
        compute='_compute_grade',
        store=True,
        readonly=True,
    )

    @api.onchange('checklist_score', 'exam_score')
    def _onchange_scores_update_total(self):
        """Khi điểm checklist hoặc điểm kiểm tra thay đổi, tự động tính lại tổng điểm và xếp loại lập tức."""
        for rec in self:
            rec.total_score = (rec.checklist_score or 0.0) + (rec.exam_score or 0.0)
            rec._compute_grade()
    
    next_due_date = fields.Date(
        string='Lần kiểm tra kế tiếp',   
    )

    next_schedule_id = fields.Many2one(
        'wujia.supervision.schedule',
        string='Lịch giám sát tiếp theo',
        ondelete='set null',
    )

    test_employee_name = fields.Char(
        string='Nhân viên được kiểm tra',
        _description='nhận viện tại cửa hàng không có trong user'
    )

    tenure = fields.Float(
        string='Thâm niên',
        _description='thời gian làm việc của nhân viên'
    )

    # RELATION 

    schedule_id = fields.Many2one(
        'wujia.supervision.schedule', 
        string='Lịch giám sát', 
        required=True)
    
    template_id = fields.Many2one(
        'wujia.franchise.inspection.template',
        string='Mẫu khảo sát',
        required=True,
        ondelete='restrict',
    )

    franchise_id = fields.Many2one(
        'wujia.franchise.management',
        string='Cửa hàng',
        required=True,
        ondelete='restrict',
    )

    inspector_user_id = fields.Many2one(
        'res.users',
        string='Người kiểm tra',
        required=True,
        ondelete='restrict',
        default=lambda self: self.env.user
    )

    previous_inspection_id = fields.Many2one(
        'wujia.franchise.inspection',
        string='Phiếu khảo sát trước',
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
        auto_join=True,
    )

    exam_line_ids = fields.One2many(
        'wujia.franchise.inspection.exam.line',
        'inspection_id',
        string='Điểm kiểm tra',
        copy=False,
        auto_join=True,
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

    def action_submit_exam(self):
        """
        Nộp bài kiểm tra nhân viên:
        - So sánh đáp án trả lời của nhân viên với đáp án đúng snapshot.
        - Cập nhật điểm từng dòng: Đúng -> 1.0 (hoặc score), Sai/Bỏ trống -> 0.0.
        - Khóa bài làm và tính tổng điểm phiếu khảo sát.
        """
        for rec in self:
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
        """Chuyển phiếu khảo sát sang trạng thái Cần khắc phục"""
        for rec in self:
            rec._validate_failed_lines()
            rec._validate_exam_lines()
            rec.write({'state': 'need_remediation'})
        return True

    def action_done(self):
        """Hoàn thành phiếu khảo sát, tự động lưu Ngày xác nhận và chuyển Lịch giám sát sang Hoàn thành"""
        today = fields.Date.context_today(self)
        for rec in self:
            rec._validate_failed_lines()
            rec._validate_exam_lines()
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

    def write(self, vals):
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
                            lines.append(', '.join(str(x) for x in item))
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
        for rec in self:
            if rec.franchise_id and rec.template_id:
                domain = [
                    ('franchise_id', '=', rec.franchise_id.id),
                    ('template_id', '=', rec.template_id.id),
                ]
                current_id = rec._origin.id if rec._origin else rec.id
                if current_id:
                    domain.append(('id', '!=', current_id))

                prev = self.search(domain, order='planned_date desc, id desc', limit=1)
                rec.previous_inspection_id = prev.id if prev else False
            else:
                rec.previous_inspection_id = False
    
    confirmed_user_id = fields.Many2one('res.users',
        string='Người xác nhận',
        required=True,
        ondelete='restrict',
        default=lambda self: self.env.user
    )
    confirmed_member_id = fields.Many2one('wujia.franchise.member',
        string='Quản lý của hàng xác nhận',
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
        selection=[('pass', 'Đạt'), ('fail', 'Không đạt')],
        string='Kết quả',
        default='pass',
        required=True,
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
    
    note = fields.Text(
        string='Ghi chú',
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
        selection=[('pass', 'Đạt'), ('fail', 'Không đạt')],
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
    content_class = fields.Char(
        string="CSS Class cho nội dung", 
        compute="_compute_content_class",
    )

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

    