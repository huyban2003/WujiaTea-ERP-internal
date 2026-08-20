# -*- coding: utf-8 -*-
import os
import json
from odoo import api, fields, models, _
# pyrefly: ignore [missing-import]
from odoo.exceptions import ValidationError


class WujiaFranchiseInspectionCategory(models.Model):
    _name = 'wujia.franchise.inspection.category'
    _description = 'Inspection criterion category / group'
    _order = 'sequence, id'

    name = fields.Char(string='Category name', required=True)
    code = fields.Char(string='Category code')
    sequence = fields.Integer(string='Sequence', default=10)
    active = fields.Boolean(string='Active', default=True)
    is_severe = fields.Boolean(string='Critical violation', default=False)

    _sql_constraints = [
        ('name_unique', 'UNIQUE(name)', 'The category name must be unique!'),
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



class WujiaFranchiseInspectionTemplate(models.Model):
    _name = 'wujia.franchise.inspection.template'
    _description = 'Franchise store inspection template'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'effective_date desc, id desc'

    name = fields.Char(string='Template name', required=True, tracking=True)
    code = fields.Char(string='Template code', tracking=True)
    version = fields.Char(string='Version', default='v1.0', tracking=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('archived', 'Archived'),
    ], string='Status', default='draft', required=True, tracking=True)
    effective_date = fields.Date(string='Effective date', default=fields.Date.context_today, tracking=True)
    
    checklist_max_score = fields.Float(string='Maximum checklist score', default=95.0, tracking=True)
    exam_max_score = fields.Float(string='Maximum exam score', default=5.0, tracking=True)
    total_max_score = fields.Float(
        string='Maximum total score',
        compute='_compute_total_max_score',
        store=True,
        tracking=True,
    )
    
    line_ids = fields.One2many(
        'wujia.franchise.inspection.template.line',
        'template_id',
        string='Criterion details',
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
                raise ValidationError(_('An inspection template can only be deleted while in the Draft state!'))

    def write(self, vals):
        for rec in self:
            if rec.state in ('active', 'archived'):
                allowed_keys = {'state'}
                if not set(vals.keys()).issubset(allowed_keys):
                    raise ValidationError(_(
                        'Inspection template "%s" is in the "%s" state, so its content CANNOT be edited!\n'
                        'To change the criteria, please click "Create new version".'
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
            'name': _('Inspection template (new version)'),
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
            'name': 'Franchise store inspection',
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


class WujiaFranchiseInspectionTemplateLine(models.Model):
    _name = 'wujia.franchise.inspection.template.line'
    _description = 'Inspection template criterion line'
    _order = 'sequence, id'

    template_id = fields.Many2one(
        'wujia.franchise.inspection.template',
        string='Inspection template',
        required=True,
        ondelete='cascade',
    )
    sequence = fields.Integer(string='Sequence', default=10)
    display_type = fields.Selection([
        ('line', 'Criterion line'),
        ('section', 'Section (heading)'),
    ], string='Display type', default='line', required=True)
    criterion_code = fields.Char(string='Criterion code')
    category_id = fields.Many2one(
        'wujia.franchise.inspection.category',
        string='Criterion categories',
    )
    category = fields.Char(string='Category (legacy text)', related='category_id.name', readonly=True, store=True)
    content = fields.Text(string='Criterion content')
    criterion_type = fields.Selection([
        ('normal', 'Normal'),
        ('critical', 'Critical / disqualifying'),
    ], string='Criterion type', default='normal', required=True)
    deduction_score = fields.Float(string='Deduction', default=1.0)
    require_note_if_fail = fields.Boolean(string='Note required when failed', default=False)
    require_evidence_if_fail = fields.Boolean(string='Evidence required when failed', default=False)
    active = fields.Boolean(string='Active', default=True)
    is_severe = fields.Boolean(string='Critical violation', default=False)

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
                    rec.display_name = f"[{sub_code}] {cat_name or _('No category selected')}"
                else:
                    rec.display_name = cat_name or _('No category selected')
            else:
                content = (rec.content or '').strip()
                if sub_code:
                    rec.display_name = f"[{sub_code}] {content}"
                else:
                    rec.display_name = content or _('Unnamed criterion')

    @api.ondelete(at_uninstall=False)
    def _unlink_except_draft_template(self):
        for line in self:
            if line.template_id.state in ('active', 'archived'):
                raise ValidationError(_('Criteria of an Active or Archived inspection template cannot be deleted!'))

    def write(self, vals):
        for line in self:
            if line.template_id.state in ('active', 'archived'):
                raise ValidationError(_('Criteria of an Active or Archived inspection template cannot be edited!'))
        return super().write(vals)

    @api.model_create_multi
    def create(self, vals_list):
        lines = super().create(vals_list)
        for line in lines:
            if line.template_id.state in ('active', 'archived'):
                raise ValidationError(_('New criteria cannot be added to an Active or Archived inspection template!'))
        return lines
