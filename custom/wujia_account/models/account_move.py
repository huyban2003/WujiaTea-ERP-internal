from odoo import api, fields, models

# Field đổi giá trị → cần tính lại badge công nợ (portal). Chỉ đúng những field ảnh
# hưởng "còn nợ / quá hạn": posting, số dư, hạn, cửa hàng. Không đụng các field khác.
_DEBT_TRIGGER_FIELDS = frozenset({
    'state', 'payment_state', 'amount_residual', 'invoice_date_due', 'franchise_id',
})


class AccountMove(models.Model):
    _inherit = 'account.move'

    franchise_id = fields.Many2one(
        'wujia.franchise.management',
        string='Franchise store',
        index=True,
        copy=False,
        tracking=True,
        help='Store scope of this invoice / credit note — used for portal debt filtering '
             '(BA Model/Field N). Set from the originating sale order; accountant picks it '
             'for invoices created directly in backend.',
    )

    # ------------------------------------------------------------------
    # Giữ badge công nợ portal tươi khi hoá đơn đổi (post / đối soát / đổi hạn).
    # Recompute idempotent + chỉ chạm franchise bị ảnh hưởng ⇒ double-fire vô hại.
    # ------------------------------------------------------------------
    def _debt_refresh(self, extra_franchises=None):
        franchises = self.franchise_id
        if extra_franchises:
            franchises |= extra_franchises
        if franchises:
            franchises._recompute_portal_debt_batch()

    @api.model_create_multi
    def create(self, vals_list):
        moves = super().create(vals_list)
        moves._debt_refresh()
        return moves

    def write(self, vals):
        before = self.franchise_id if 'franchise_id' in vals else None
        res = super().write(vals)
        if _DEBT_TRIGGER_FIELDS.intersection(vals):
            self._debt_refresh(extra_franchises=before)
        return res
