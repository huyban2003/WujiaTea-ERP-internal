# -*- coding: utf-8 -*-

from odoo import models, fields, api

class fields_value(models.TransientModel):
    _name = 'fields.value'

    res_id = fields.Integer()
    model = fields.Char()
    model_id = fields.Many2one('ir.model', compute='_compute_model_id')
    field_ids = fields.Many2many('ir.model.fields')
    field_value_line_ids = fields.Many2many('fields.value.line', compute='_compute_field_value_line_ids')

    @api.depends('model')
    def _compute_model_id(self):
        for rec in self:
            rec.model_id = self.env['ir.model'].search([('model', '=', rec.model)])

    @api.depends('res_id', 'model_id', 'field_ids')
    def _compute_field_value_line_ids(self):
        for rec in self:
            if rec.model_id:
                fields_list = rec.field_ids.mapped('name')
                domain = [('id', '=', rec.res_id)]
                values = self.env[rec.model_id.model].search_read(domain, fields_list)[0]
                line = self.env['fields.value.line']
                field_ids = rec.field_ids if bool(rec.field_ids) else rec.model_id.field_id
                for field in field_ids:
                    if field.name != 'id':
                        line += line.create({
                            'field_name': field.name,
                            'field_label': field.field_description,
                            'field_value': str(values[field.name]),
                    })
                rec.field_value_line_ids = [(6, 0, line.ids)]
            else:
                rec.field_value_line_ids = False

class FieldsValueLine(models.TransientModel):
    _name = 'fields.value.line'

    field_name = fields.Char()
    field_label = fields.Char()
    field_value = fields.Text()