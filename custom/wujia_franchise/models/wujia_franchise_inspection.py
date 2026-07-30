# -*- coding: utf-8 -*-
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
        ('draft', 'Đang chờ'),
        ('in_progress', 'Đang thực hiện'),
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
                rec.checklist_score = 95.0
            else:
                total_deduction = sum(
                    line.deduction_score_snapshot
                    for line in criteria_lines
                    if not line.is_pass
                )
                rec.checklist_score = max(0.0, 95.0 - total_deduction)

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
            for t_line in self.template_id.line_ids:
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
                        'is_pass': True,
                        'result': 'pass',
                        'previous_line_id': prev_l_id,
                        'previous_result': prev_res,
                        'previous_deduction_score': prev_ded,
                    }))
                    seq += 10

            self.line_ids = [(5, 0, 0)] + lines

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

    exam_score = fields.Float(
        string='Điểm kiểm tra',
        _description='là điểm được lấy từ cấu hỏi phần điền vào ô trống ' 
    )

    total_score = fields.Float(
        string='Tổng điểm',
        _description='điểm = điểm checklist + điểm kiểm tra'
    )

    grade = fields.Char(
        string='Xếp loại',
        _description='Xếp loại dựa trên điểm số'
    )
    
    next_due_date = fields.Date(
        string='Lần kiểm tra kế tiếp',   
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
    
    @api.depends('checklist_score', 'exam_score')
    def _compute_total_score(self):
        """
        Tự động chạy khi 'checklist_score' hoặc 'exam_score' thay đổi.
        Cộng 2 điểm thành phần để tạo thành total_score.
        """
        for rec in self:
            rec.total_score = (rec.checklist_score or 0.0) + (rec.exam_score or 0.0)

    @api.depends('total_score')
    def _compute_grade(self):
        """
        Tự động chạy khi 'total_score' thay đổi.
        Tính 'grade' dựa trên 'total_score'.
        """
        if self.total_score >= 96:
            self.grade = 'A'
        elif self.total_score >= 83:
            self.grade = 'B'
        elif self.total_score >= 70:
            self.grade = 'C'
        else:
            self.grade = 'D'

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
        string='Điểm trừ trước đó',
        compute='_compute_previous_line_info',
        store=True,
        readonly=True,
        default=0.0,
    )
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