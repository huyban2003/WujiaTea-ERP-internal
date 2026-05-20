from odoo import _, api, models
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model_create_multi
    def create(self, vals_list):
        # Defense-in-depth: even if controller misses the check,
        # block portal SO creation outside the configured order window.
        # Khung giờ theo area của franchise; nếu area chưa cấu hình thì
        # fallback global config.
        Settings = self.env['res.config.settings'].sudo()
        Franchise = self.env['wujia.franchise.management'].sudo()
        for vals in vals_list:
            if not vals.get('is_portal_order'):
                continue
            area_id = False
            franchise_id = vals.get('franchise_id')
            if franchise_id:
                franchise = Franchise.browse(franchise_id)
                area_id = franchise.area_id.id if franchise.area_id else False
            allowed, window = Settings._is_within_order_window(area_id=area_id)
            if not allowed:
                raise ValidationError(_(
                    "Hiện chưa nằm trong khung giờ nhận đơn. "
                    "Vui lòng đặt hàng trong khung giờ %(f).2f – %(t).2f.",
                    f=window['from'], t=window['to'],
                ))
        return super().create(vals_list)
