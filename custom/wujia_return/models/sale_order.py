from odoo import _, fields, models


class SaleOrder(models.Model):
    """Huỷ SO bù → đóng quyền lợi (BA STT3 acceptance 12).

    Rule BA: allocation chuyển 'Đã huỷ', request cũ chuyển 'Hoàn tất', KHÔNG
    release/khôi phục quyền lợi — cần bù tiếp thì cửa hàng tạo yêu cầu mới.
    Khác hẳn `_release_shortfall` (kho giao thiếu, cố ý hoàn lại để bù kỳ sau).
    """

    _inherit = 'sale.order'

    def _action_cancel(self):
        res = super()._action_cancel()
        self._wujia_cancel_compensation()
        return res

    def _wujia_cancel_compensation(self):
        comp_orders = self.filtered('is_return_order')
        if not comp_orders:
            return
        allocations = self.env['wujia.compensation.allocation'].sudo().search([
            ('sale_order_id', 'in', comp_orders.ids),
            ('state', '!=', 'cancel'),
        ])
        if not allocations:
            return
        requests = allocations.request_id
        # KHÔNG đụng released_qty: quyền lợi đóng lại theo request chứ không quay
        # về hàng đợi phân bổ.
        allocations.write({
            'state': 'cancel',
            'release_reason': _("Đơn bù bị huỷ — quyền lợi đóng theo yêu cầu."),
        })
        to_close = requests.filtered(
            lambda r: r.state not in ('done', 'cancelled', 'rejected'))
        to_close.write({'state': 'done', 'resolved_date': fields.Datetime.now()})
        for req in to_close:
            req.message_post(body=_(
                "Đơn bù đã bị huỷ. Nếu vẫn cần bù hàng, vui lòng tạo yêu cầu mới."))
