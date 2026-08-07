# -*- coding: utf-8 -*-
import os
import json
from odoo import api, fields, models, _
# pyrefly: ignore [missing-import]
from odoo.exceptions import ValidationError


class WujiaFranchiseInspectionCategory(models.Model):
    _name = 'wujia.franchise.inspection.category'
    _description = 'Danh mục / Nhóm tiêu chí khảo sát'
    _order = 'sequence, id'

    name = fields.Char(string='Tên danh mục', required=True)
    code = fields.Char(string='Mã danh mục')
    sequence = fields.Integer(string='Thứ tự', default=10)
    active = fields.Boolean(string='Kích hoạt', default=True)
    is_severe = fields.Boolean(string='Vi phạm nghiêm trọng', default=False)

    _sql_constraints = [
        ('name_unique', 'UNIQUE(name)', 'Tên danh mục phải là duy nhất!'),
    ]

    @api.model
    def _init_default_categories(self):
        """Khởi tạo các Danh mục tiêu chí mặc định nếu chưa tồn tại trong DB."""
        default_categories = [
            {'name': 'Gìn giữ hình ảnh ngoại quan cửa hàng / 店鋪外觀形象保持', 'sequence': 10},
            {'name': 'Yêu cầu giữ gìn các thiết bị / 各設備維護要求', 'sequence': 20},
            {'name': 'Yêu cầu tiêu chuẩn cơ bản / 基本規範要求', 'sequence': 30},
            {'name': 'Những hạng mục vi phạm nghiêm trọng (vi phạm 1 hạng mục bất kỳ sẽ bị trừ trực tiếp 6 điểm) / 任何一項嚴重違規,就直接扣六分', 'sequence': 40, 'is_severe': True},
        ]
        for cat_data in default_categories:
            existing = self.search([('name', '=', cat_data['name'])], limit=1)
            if not existing:
                self.create(cat_data)

    def init(self):
        super().init()
        self._init_default_categories()


class WujiaFranchiseInspectionTemplate(models.Model):
    _name = 'wujia.franchise.inspection.template'
    _description = 'Mẫu khảo sát đánh giá cửa hàng nhượng quyền'
    _order = 'effective_date desc, id desc'

    name = fields.Char(string='Tên mẫu khảo sát', required=True)
    code = fields.Char(string='Mã mẫu')
    version = fields.Char(string='Phiên bản', default='v1.0')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('archived', 'Archived'),
    ], string='Trạng thái', default='draft', required=True)
    effective_date = fields.Date(string='Ngày áp dụng', default=fields.Date.context_today)
    
    checklist_max_score = fields.Float(string='Điểm tối đa Checklist', default=95.0)
    exam_max_score = fields.Float(string='Điểm tối đa Bài thi', default=5.0)
    total_max_score = fields.Float(
        string='Tổng điểm tối đa',
        compute='_compute_total_max_score',
        store=True,
    )
    
    line_ids = fields.One2many(
        'wujia.franchise.inspection.template.line',
        'template_id',
        string='Chi tiết tiêu chí',
        copy=True,
    )

    @api.depends('checklist_max_score', 'exam_max_score')
    def _compute_total_max_score(self):
        for rec in self:
            rec.total_max_score = (rec.checklist_max_score or 0.0) + (rec.exam_max_score or 0.0)

    @api.ondelete(at_uninstall=False)
    def _unlink_except_draft(self):
        for rec in self:
            if rec.state != 'draft':
                raise ValidationError(_('Chỉ được phép xóa mẫu khảo sát khi ở trạng thái Draft!'))

    def write(self, vals):
        for rec in self:
            if rec.state in ('active', 'archived'):
                allowed_keys = {'state'}
                if not set(vals.keys()).issubset(allowed_keys):
                    raise ValidationError(_(
                        'Mẫu khảo sát "%s" đã ở trạng thái "%s" nên KHÔNG ĐƯỢC PHÉP chỉnh sửa nội dung!\n'
                        'Nếu bạn muốn thay đổi tiêu chí, vui lòng bấm nút "Tạo phiên bản mới".'
                    ) % (rec.name, rec.state))
        return super().write(vals)

    def action_activate(self):
        for rec in self:
            if rec.code:
                old_actives = self.search([
                    ('id', '!=', rec.id),
                    ('code', '=', rec.code),
                    ('state', '=', 'active'),
                ])
                old_actives.write({'state': 'archived'})
            rec.write({'state': 'active'})

    def action_archive(self):
        self.write({'state': 'archived'})

    def action_reset_draft(self):
        self.write({'state': 'draft'})

    def _increment_version(self, ver_str):
        if not ver_str:
            return 'v1.1'
        clean_ver = ver_str.lower().lstrip('v')
        try:
            parts = clean_ver.split('.')
            if len(parts) >= 2:
                parts[-1] = str(int(parts[-1]) + 1)
                return f"v{'.'.join(parts)}"
            elif len(parts) == 1:
                return f"v{int(parts[0]) + 1}.0"
        except Exception:
            pass
        return f"{ver_str}-v2"

    def action_create_new_version(self):
        self.ensure_one()
        new_version = self._increment_version(self.version)
        new_template = self.copy({
            'name': f"{self.name} ({new_version})",
            'version': new_version,
            'state': 'draft',
            'effective_date': fields.Date.context_today(self),
        })

        # Đảm bảo sao chép toàn bộ các dòng tiêu chí cũ sang phiên bản mới
        if not new_template.line_ids and self.line_ids:
            new_lines = []
            for line in self.line_ids:
                new_lines.append({
                    'template_id': new_template.id,
                    'sequence': line.sequence,
                    'criterion_code': line.criterion_code,
                    'category_id': line.category_id.id if line.category_id else False,
                    'display_type': line.display_type,
                    'content': line.content,
                    'criterion_type': line.criterion_type,
                    'deduction_score': line.deduction_score,
                    'require_note_if_fail': line.require_note_if_fail,
                    'require_evidence_if_fail': line.require_evidence_if_fail,
                    'active': line.active,
                })
            if new_lines:
                self.env['wujia.franchise.inspection.template.line'].create(new_lines)

        return {
            'name': _('Mẫu khảo sát (Phiên bản mới)'),
            'type': 'ir.actions.act_window',
            'res_model': 'wujia.franchise.inspection.template',
            'res_id': new_template.id,
            'view_mode': 'form',
            'target': 'current',
        }

    @api.model
    def _init_demo_template(self):
        """Khởi tạo dữ liệu mẫu khảo sát MM01 (Khảo sát cửa hàng nhượng quyền) nếu chưa tồn tại trong DB."""
        existing = self.search([('code', '=', 'MM01')], limit=1)
        if existing:
            return

        Category = self.env['wujia.franchise.inspection.category']

        template = self.create({
            'name': 'Khảo sát cửa hàng nhượng quyền',
            'code': 'MM01',
            'state': 'draft',
            'version': 'v1.0',
            'checklist_max_score': 95.0,
            'exam_max_score': 5.0,
            'total_max_score': 100.0,
            'effective_date': fields.Date.today(),
        })

        json_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'template_mm01_lines.json')
        if os.path.exists(json_path):
            with open(json_path, 'r', encoding='utf-8') as f:
                lines_data = json.load(f)

            category_cache = {}
            lines_to_create = []

            for item in lines_data:
                cat_name = item.get('category_name')
                cat_id = False
                if cat_name:
                    if cat_name not in category_cache:
                        cat_rec = Category.search([('name', '=', cat_name)], limit=1)
                        if not cat_rec:
                            cat_rec = Category.create({'name': cat_name, 'sequence': 10})
                        category_cache[cat_name] = cat_rec.id
                    cat_id = category_cache[cat_name]

                lines_to_create.append({
                    'template_id': template.id,
                    'sequence': item.get('sequence', 10),
                    'display_type': item.get('display_type') or 'line',
                    'criterion_code': item.get('criterion_code'),
                    'category_id': cat_id,
                    'content': item.get('content'),
                    'criterion_type': item.get('criterion_type') or 'normal',
                    'deduction_score': item.get('deduction_score', 1.0),
                    'require_note_if_fail': item.get('require_note_if_fail', False),
                    'require_evidence_if_fail': item.get('require_evidence_if_fail', False),
                })

            if lines_to_create:
                self.env['wujia.franchise.inspection.template.line'].create(lines_to_create)

        template.write({'state': 'active'})

    def init(self):
        super().init()
        self._init_demo_template()


class WujiaFranchiseInspectionTemplateLine(models.Model):
    _name = 'wujia.franchise.inspection.template.line'
    _description = 'Dòng tiêu chí mẫu khảo sát cửa hàng'
    _order = 'sequence, id'

    template_id = fields.Many2one(
        'wujia.franchise.inspection.template',
        string='Mẫu khảo sát',
        required=True,
        ondelete='cascade',
    )
    sequence = fields.Integer(string='Thứ tự', default=10)
    display_type = fields.Selection([
        ('line', 'Dòng tiêu chí'),
        ('section', 'Section (Đầu mục)'),
    ], string='Loại hiển thị', default='line', required=True)
    criterion_code = fields.Char(string='Mã tiêu chí')
    category_id = fields.Many2one(
        'wujia.franchise.inspection.category',
        string='Danh mục tiêu chí',
    )
    category = fields.Char(string='Danh mục (Text cũ)', related='category_id.name', readonly=True, store=True)
    content = fields.Text(string='Nội dung tiêu chí')
    criterion_type = fields.Selection([
        ('normal', 'Bình thường'),
        ('critical', 'Quan trọng / Điểm liệt'),
    ], string='Loại tiêu chí', default='normal', required=True)
    deduction_score = fields.Float(string='Điểm trừ', default=1.0)
    require_note_if_fail = fields.Boolean(string='Yêu cầu ghi chú khi không đạt', default=False)
    require_evidence_if_fail = fields.Boolean(string='Yêu cầu bằng chứng khi không đạt', default=False)
    active = fields.Boolean(string='Kích hoạt', default=True)
    is_severe = fields.Boolean(string='Vi phạm nghiêm trọng', default=False)

    @api.onchange('category_id', 'display_type')
    def _onchange_category_id_section(self):
        """Khi chọn loại là Section và chọn Danh mục, tự điền Nội dung = Tên danh mục."""
        if self.display_type == 'section' and self.category_id:
            self.content = self.category_id.name

    @api.depends('criterion_code', 'content', 'display_type', 'category_id')
    def _compute_display_name(self):
        for rec in self:
            code_raw = (rec.criterion_code or '').strip()
            sub_code = code_raw.split('.', 1)[1].strip() if '.' in code_raw else ''
            if rec.display_type == 'section':
                cat_name = rec.category_id.name if rec.category_id else rec.content
                if sub_code:
                    rec.display_name = f"[{sub_code}] {cat_name or _('Chưa chọn danh mục')}"
                else:
                    rec.display_name = cat_name or _('Chưa chọn danh mục')
            else:
                content = (rec.content or '').strip()
                if sub_code:
                    rec.display_name = f"[{sub_code}] {content}"
                else:
                    rec.display_name = content or _("Tiêu chí không tên")

    @api.ondelete(at_uninstall=False)
    def _unlink_except_draft_template(self):
        for line in self:
            if line.template_id.state in ('active', 'archived'):
                raise ValidationError(_('Không thể xóa tiêu chí của mẫu khảo sát đã ở trạng thái Active hoặc Archived!'))

    def write(self, vals):
        for line in self:
            if line.template_id.state in ('active', 'archived'):
                raise ValidationError(_('Không thể sửa tiêu chí của mẫu khảo sát đã ở trạng thái Active hoặc Archived!'))
        return super().write(vals)

    @api.model_create_multi
    def create(self, vals_list):
        lines = super().create(vals_list)
        for line in lines:
            if line.template_id.state in ('active', 'archived'):
                raise ValidationError(_('Không thể thêm tiêu chí mới vào mẫu khảo sát đã ở trạng thái Active hoặc Archived!'))
        return lines
