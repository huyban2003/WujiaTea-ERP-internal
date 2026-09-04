# -*- coding: utf-8 -*-
from odoo import fields, models


class ResUsers(models.Model):
    _inherit = 'res.users'

    inspection_signature = fields.Binary(
        string='Chữ ký giám sát / Chữ ký số',
        attachment=True,
        copy=False,
        help='Chữ ký mẫu dùng để ký xác nhận trên các phiếu khảo sát & giám sát.'
    )

    @property
    def SELF_READABLE_FIELDS(self):
        return super().SELF_READABLE_FIELDS + ['inspection_signature']

    @property
    def SELF_WRITEABLE_FIELDS(self):
        return super().SELF_WRITEABLE_FIELDS + ['inspection_signature']
