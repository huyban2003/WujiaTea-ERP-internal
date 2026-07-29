# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
# pyrefly: ignore [missing-import]
from odoo.exceptions import ValidationError


class WujiaFranchiseInspection(models.Model):
    _name = 'wujia.franchise.inspection'
    _description = 'Phiếu khảo sát đánh giá cửa hàng nhượng quyền'
    _order = 'id desc'

    name = fields.Char(string='Tên phiếu khảo sát', required=True)
    code = fields.Char(string='Mã danh mục')
    sequence = fields.Integer(string='Thứ tự', default=10)
    active = fields.Boolean(string='Kích hoạt', default=True)

    schedule_id = fields.Many2one(
        'wujia.supervision.schedule', 
        string='Lịch giám sát', 
        required=True)
