# -*- coding: utf-8 -*-
from odoo import api, fields, models


class SaleOrder(models.Model):
    """Extension of sale.order incorporating wujia.mobile.mixin for mobile rendering."""

    _name = 'sale.order'
    _inherit = ['sale.order', 'wujia.mobile.mixin']

    mobile_badge_class = fields.Char(
        string='Mobile Badge Class',
        compute='_compute_mobile_card_helpers',
        store=False,
    )
    mobile_card_title = fields.Char(
        string='Mobile Card Title',
        compute='_compute_mobile_card_helpers',
        store=False,
    )

    @api.depends('state', 'franchise_id', 'franchise_id.name', 'area_id', 'area_id.name', 'partner_id', 'partner_id.name')
    def _compute_mobile_card_helpers(self):
        """Batch compute mobile card display title and status badge class.

        Anti-N+1 compliant (Rule 14): Relies strictly on Odoo pre-fetched ORM cache
        without issuing database queries in loop.
        """
        for rec in self:
            rec.mobile_badge_class = rec.get_mobile_badge_class(rec.state)

            if rec.franchise_id:
                if rec.area_id:
                    rec.mobile_card_title = f"{rec.franchise_id.name} ({rec.area_id.name})"
                else:
                    rec.mobile_card_title = rec.franchise_id.name
            elif rec.partner_id:
                rec.mobile_card_title = rec.partner_id.name
            else:
                rec.mobile_card_title = rec.name or ""
