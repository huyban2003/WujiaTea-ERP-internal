from odoo import fields, models


class WujiaNotificationType(models.Model):
    """Master data — loại thông báo (Khẩn, Thông báo, Khuyến mãi, ...)."""

    _name = 'wujia.notification.type'
    _description = 'Wujia Notification Type'
    _order = 'sequence, code'

    name = fields.Char(required=True, translate=True)
    code = fields.Char(required=True)
    bg_color = fields.Char(string='Màu nền', default='#1f4180')
    text_color = fields.Char(string='Màu chữ', default='#ffffff')
    icon = fields.Char(string='Icon (FontAwesome)', default='fa-bell')
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)

    _sql_constraints = [
        ('uniq_code', 'unique(code)', 'Mã loại thông báo phải duy nhất.'),
    ]
