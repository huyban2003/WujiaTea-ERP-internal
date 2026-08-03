# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class WujiaFranchiseInspectionGrade(models.Model):
    _name = 'wujia.franchise.inspection.grade'
    _description = 'Cấu hình xếp hạng giám sát'
    _order = 'min_score desc'

    name = fields.Char(
        string='Xếp hạng',
        required=True,
        help='Tên xếp hạng, ví dụ: A, B, C, D',
    )
    min_score = fields.Float(
        string='Điểm tối thiểu',
        required=True,
        help='Điểm tối thiểu để đạt hạng này (bao gồm)',
    )
    max_score = fields.Float(
        string='Điểm tối đa',
        required=True,
        default=100.0,
        help='Điểm tối đa của hạng này (bao gồm)',
    )
    description = fields.Text(
        string='Mô tả',
        help='Mô tả ngắn cho hạng xếp loại này',
    )
    sequence = fields.Integer(
        string='Thứ tự',
        default=10,
    )
    active = fields.Boolean(
        string='Active',
        default=True,
    )
    color = fields.Integer(
        string='Color',
        help='Màu hiển thị trên badge',
    )

    _sql_constraints = [
        ('name_unique', 'UNIQUE(name)', 'Tên xếp hạng phải là duy nhất!'),
        ('score_check', 'CHECK(min_score <= max_score)',
         'Điểm tối thiểu phải nhỏ hơn hoặc bằng điểm tối đa!'),
    ]

    def init(self):
        """Tự động khởi tạo các khoản điểm xếp hạng mặc định khi module được cài đặt/cập nhật."""
        super().init()
        self._init_default_grades()

    @api.model
    def _init_default_grades(self):
        """Tạo các xếp hạng mặc định (A, B, C, D) nếu chưa tồn tại trong database."""
        default_grades = [
            {'name': 'A', 'min_score': 96.0, 'max_score': 100.0, 'sequence': 1, 'color': 10, 'description': 'Xuất sắc'},
            {'name': 'B', 'min_score': 83.0, 'max_score': 95.99, 'sequence': 2, 'color': 2, 'description': 'Tốt'},
            {'name': 'C', 'min_score': 70.0, 'max_score': 82.99, 'sequence': 3, 'color': 3, 'description': 'Trung bình'},
            {'name': 'D', 'min_score': 0.0, 'max_score': 69.99, 'sequence': 4, 'color': 1, 'description': 'Yếu'},
        ]
        for grade_data in default_grades:
            existing = self.with_context(active_test=False).search([('name', '=', grade_data['name'])], limit=1)
            if not existing:
                self.create(grade_data)


    @api.constrains('name')
    def _check_name_unique(self):
        """Đảm bảo tên xếp hạng là duy nhất."""
        if self.env.context.get('install_mode') or self.env.context.get('import_file'):
            return
        for record in self:
            rec_id = record._origin.id if record._origin else (record.id if isinstance(record.id, int) else False)
            domain = [('name', '=', record.name)]
            if rec_id:
                domain.append(('id', '!=', rec_id))
            if self.search_count(domain) > 0:
                raise ValidationError(_('Tên xếp hạng "%s" đã tồn tại!', record.name))

    @api.constrains('min_score', 'max_score')
    def _check_score_overlap(self):
        """Kiểm tra các khoảng điểm không được chồng lấn nhau."""
        if self.env.context.get('install_mode') or self.env.context.get('import_file'):
            return
        for record in self:
            rec_id = record._origin.id if record._origin else (record.id if isinstance(record.id, int) else False)
            domain = [
                ('active', '=', True),
                ('min_score', '<=', record.max_score),
                ('max_score', '>=', record.min_score),
            ]
            if rec_id:
                domain.append(('id', '!=', rec_id))
            overlapping = self.search(domain, limit=1)
            if overlapping and overlapping.id != rec_id:
                raise ValidationError(
                    _('Khoảng điểm [%(min)s - %(max)s] của hạng "%(name)s" bị chồng lấn '
                      'với hạng "%(other)s" [%(other_min)s - %(other_max)s]!',
                      min=record.min_score,
                      max=record.max_score,
                      name=record.name,
                      other=overlapping.name,
                      other_min=overlapping.min_score,
                      other_max=overlapping.max_score,
                      )
                )
