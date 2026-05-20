from odoo import _, api, models
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model_create_multi
    def create(self, vals_list):
        # Defense-in-depth: even if controller misses the check,
        # block portal SO creation outside the configured order window.
        Settings = self.env['res.config.settings'].sudo()
        portal_vals = [v for v in vals_list if v.get('is_portal_order')]
        if portal_vals:
            allowed, window = Settings._is_within_order_window()
            if not allowed:
                raise ValidationError(_(
                    "Hiện chưa nằm trong khung giờ nhận đơn. "
                    "Vui lòng đặt hàng trong khung giờ %(f).2f – %(t).2f.",
                    f=window['from'], t=window['to'],
                ))
        return super().create(vals_list)
