# -*- coding: utf-8 -*-

from odoo import models, api

class IrModelFields(models.Model):
    _inherit = 'ir.model.fields'

    def name_get(self):
        if self.env.context.get('from_fields_value'):
            return [(field_id.id, field_id.field_description) for field_id in self]
        return super(IrModelFields, self).name_get()