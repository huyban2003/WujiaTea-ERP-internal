# -*- coding: utf-8 -*-

from odoo import models, fields, api

class WujiaFieldsValue(models.TransientModel):
    _name = 'wujia.fields.value'
    _description = 'Wujia View Fields Value Wizard'

    res_id = fields.Integer(string='Resource ID')
    model = fields.Char(string='Model Name')
    model_id = fields.Many2one('ir.model', string='Model', compute='_compute_model_id')
    field_ids = fields.Many2many('ir.model.fields', string='Filter Fields')
    field_value_line_ids = fields.Many2many('wujia.fields.value.line', compute='_compute_field_value_line_ids', string='Field Values')

    @api.depends('model')
    def _compute_model_id(self):
        for rec in self:
            if rec.model:
                rec.model_id = self.env['ir.model'].search([('model', '=', rec.model)], limit=1)
            else:
                rec.model_id = False

    @api.depends('res_id', 'model_id', 'field_ids')
    def _compute_field_value_line_ids(self):
        for rec in self:
            if rec.model_id and rec.res_id and rec.model_id.model in self.env:
                target_model = rec.model_id.model
                target_record = self.env[target_model].browse(rec.res_id).exists()
                if not target_record:
                    rec.field_value_line_ids = False
                    continue

                field_ids = rec.field_ids if rec.field_ids else rec.model_id.field_id
                lines = []
                idx = 1
                for field in field_ids:
                    if field.name == 'id':
                        continue
                    try:
                        val = getattr(target_record, field.name, None)
                    except Exception as e:
                        val_str = f"<Error reading field: {e}>"
                    else:
                        if isinstance(val, models.BaseModel):
                            if not val:
                                val_str = ""
                            elif len(val) == 1:
                                val_str = val.display_name or str(val.id)
                            else:
                                display_names = val.mapped('display_name')
                                val_str = ", ".join(str(d) for d in display_names if d)
                        elif val is not None:
                            val_str = str(val)
                        else:
                            val_str = ""

                    lines.append((0, 0, {
                        'sequence': idx,
                        'field_name': field.name,
                        'field_label': field.field_description or field.name,
                        'field_value': val_str,
                    }))
                    idx += 1
                rec.field_value_line_ids = lines
            else:
                rec.field_value_line_ids = False

class WujiaFieldsValueLine(models.TransientModel):
    _name = 'wujia.fields.value.line'
    _description = 'Wujia View Fields Value Line'

    sequence = fields.Integer(string='#', default=10)
    field_name = fields.Char(string='Field Technical Name')
    field_label = fields.Char(string='Field Label')
    field_value = fields.Text(string='Value')
