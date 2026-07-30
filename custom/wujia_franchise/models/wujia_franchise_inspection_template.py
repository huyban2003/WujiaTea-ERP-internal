# -*- coding: utf-8 -*-
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
    criterion_code = fields.Char(string='Mã tiêu chí')
    category_id = fields.Many2one(
        'wujia.franchise.inspection.category',
        string='Danh mục tiêu chí',
    )
    category = fields.Char(string='Danh mục (Text cũ)', related='category_id.name', readonly=True, store=True)
    content = fields.Text(string='Nội dung tiêu chí', required=True)
    criterion_type = fields.Selection([
        ('normal', 'Bình thường'),
        ('critical', 'Quan trọng / Điểm liệt'),
    ], string='Loại tiêu chí', default='normal', required=True)
    deduction_score = fields.Float(string='Điểm trừ', default=1.0)
    require_note_if_fail = fields.Boolean(string='Yêu cầu ghi chú khi không đạt', default=False)
    require_evidence_if_fail = fields.Boolean(string='Yêu cầu bằng chứng khi không đạt', default=False)
    active = fields.Boolean(string='Kích hoạt', default=True)

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
