"""Route portal Công nợ & thanh toán (Figma WJ_Debt_*_MVP_v31, node 5013:*).

Shape controller dựng sẵn theo `3. Controller` CT-050…CT-055 của BA; nguồn số liệu
đi qua `wujia.portal.debt` (xem docstring model — UI-only, chốt 2026-07-31).

Guard: chưa chọn cửa hàng → render empty state, KHÔNG 500. Cùng pattern
`wujia_portal_notification/controllers/portal.py`.
"""

from datetime import datetime

from odoo import http
from odoo.http import request

from odoo.addons.wujia_portal_base.controllers.portal import (
    get_active_franchise_id,
    get_max_role_in_franchises,
)

from ..models.wujia_portal_debt import INVOICE_BADGE, INVOICE_PREVIEW, STATE_BADGE

# BA §3/§8: chỉ Owner/Manager của cửa hàng hiện tại được xem công nợ. Staff bị chặn.
_DEBT_ROLES = ('owner', 'manager')


def _debt_access(franchise_id):
    """(allowed, denied_response). Có cửa hàng nhưng role không đủ → trả trang thông báo
    (không 500, không lộ data). Chưa chọn cửa hàng → để route render empty-state như cũ."""
    if franchise_id and get_max_role_in_franchises([franchise_id]) not in _DEBT_ROLES:
        return False, request.render('wujia_portal_debt.portal_debt_no_permission', {})
    return True, None


def _vnd(amount):
    """'12.650.000 đ' — idiom tiền tệ chung của portal (xem wujia_portal_sale/purchase_history)."""
    return '{:,.0f}'.format(amount or 0).replace(',', '.') + ' đ'


def _parse_date(value):
    """'YYYY-MM-DD' (input type=date) → date, hoặc None nếu rỗng/sai định dạng."""
    if not value:
        return None
    try:
        return datetime.strptime(value, '%Y-%m-%d').date()
    except (TypeError, ValueError):
        return None


class WujiaPortalDebt(http.Controller):

    @http.route(['/portal/debt'], type='http', auth='user', sitemap=False)
    def portal_debt(self, week=None, all=None, **kw):
        """Màn 02-05 — 4 biến thể (outstanding / partial / paid / empty) theo `state`."""
        franchise_id = get_active_franchise_id()
        allowed, denied = _debt_access(franchise_id)
        if not allowed:
            return denied
        summary = request.env['wujia.portal.debt'].get_summary(franchise_id, week=week)
        # Figma: mặc định 2 hoá đơn + note "Hiển thị 2/4 hóa đơn"; `?all=1` bung hết.
        show_all = str(all or '') in ('1', 'true', 'True')
        invoices = summary['invoices'] if show_all else summary['invoices'][:INVOICE_PREVIEW]
        return request.render('wujia_portal_debt.portal_debt_overview', {
            'summary': summary,
            'invoices': invoices,
            'show_all': show_all,
            'hidden_count': max(0, summary['invoice_count'] - len(invoices)),
            'no_store': not franchise_id,
            'STATE_BADGE': STATE_BADGE,
            'INVOICE_BADGE': INVOICE_BADGE,
            'vnd': _vnd,
        })

    @http.route(['/portal/debt/payment-history'], type='http', auth='user', sitemap=False)
    def portal_debt_payment_history(self, month=None, date_from=None, date_to=None, **kw):
        """Màn 06 — các khoản Ngô Gia đã xác nhận trong kỳ."""
        franchise_id = get_active_franchise_id()
        allowed, denied = _debt_access(franchise_id)
        if not allowed:
            return denied
        history = request.env['wujia.portal.debt'].get_payments(
            franchise_id, month=month,
            date_from=_parse_date(date_from), date_to=_parse_date(date_to))
        return request.render('wujia_portal_debt.portal_debt_payment_history', {
            'history': history,
            'no_store': not franchise_id,
            'vnd': _vnd,
        })

    @http.route(['/portal/debt/pay'], type='http', auth='user', sitemap=False)
    def portal_debt_pay(self, week=None, **kw):
        """Màn 07 — QR + thông tin chuyển khoản (STK thật; ảnh QR defer, chờ BA chốt)."""
        franchise_id = get_active_franchise_id()
        allowed, denied = _debt_access(franchise_id)
        if not allowed:
            return denied
        debt = request.env['wujia.portal.debt']
        summary = debt.get_summary(franchise_id, week=week)
        bank = debt.get_bank_info(
            franchise_id, summary['remaining'], summary['week_number'])
        return request.render('wujia_portal_debt.portal_debt_pay', {
            'summary': summary,
            'bank': bank,
            'no_store': not franchise_id,
            'vnd': _vnd,
        })
