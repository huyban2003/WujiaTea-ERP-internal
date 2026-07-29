# from odoo import fields, models


# class WujiaFranchiseInspectionCategory(models.Model):
#     _name = 'wujia.franchise.inspection.category'
#     _description = 'Danh mục / Nhóm tiêu chí khảo sát'
#     _order = 'sequence, id'

#     name = fields.Char(string='Tên danh mục', required=True)
#     code = fields.Char(
#         string='Mã danh mục',
#         readonly=True
#     )
#     sequence = fields.Integer(
#         string='Thứ tự',
#         default=10
#     )
#     active = fields.Boolean(
#         string='Kích hoạt',
#         default=True
#     )

#     def create(self, vals):
#         if not vals.get('code'):
#             vals['code'] = self.env['ir.sequence'].next_by_code(
#                 'wujia.franchise.inspection.category'
#             )

#         return super().create(vals)