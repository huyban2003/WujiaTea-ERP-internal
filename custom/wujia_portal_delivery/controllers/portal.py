from datetime import datetime, timedelta

from werkzeug.exceptions import NotFound

from odoo import http
from odoo.http import request

from odoo.addons.wujia_portal_base.controllers.portal import (
    get_active_franchise_ids_filter,
)


def _ics_escape(text):
    if not text:
        return ''
    return (str(text)
            .replace('\\', '\\\\').replace(';', '\\;')
            .replace(',', '\\,').replace('\n', '\\n'))


def _ics_dt(dt):
    if not dt:
        return None
    if isinstance(dt, datetime):
        return dt.strftime('%Y%m%dT%H%M%SZ')
    return dt.strftime('%Y%m%d')


PAGE_SIZE = 20

BATCH_STATUS_LABELS = {
    'draft': ('Nháp', 'wujia-badge-muted'),
    'assigned': ('Đã gán xe', 'wujia-badge-info'),
    'loading': ('Đang chất hàng', 'wujia-badge-warning'),
    'delivering': ('Đang giao', 'wujia-badge-warning'),
    'done': ('Đã giao xong', 'wujia-badge-success'),
    'cancelled': ('Hủy chuyến', 'wujia-badge-danger'),
}

PICKING_STATUS_LABELS = {
    'pending': ('Chờ xếp xe', 'wujia-badge-muted'),
    'assigned_to_batch': ('Đã gán batch', 'wujia-badge-info'),
    'departed': ('Đang giao', 'wujia-badge-warning'),
    'delivered': ('Đã giao', 'wujia-badge-success'),
    'failed': ('Thất bại', 'wujia-badge-danger'),
}


class WujiaPortalDelivery(http.Controller):

    @http.route(['/portal/delivery'], type='http', auth='user', sitemap=False)
    def portal_delivery_list(self, page=1, status='', **kw):
        franchise_ids = get_active_franchise_ids_filter()
        if not franchise_ids:
            return request.render('wujia_portal_delivery.portal_delivery_tracking', {
                'no_franchise': True, 'pickings': [], 'pager': {},
                'picking_labels': PICKING_STATUS_LABELS, 'status': '',
            })

        # Filter pickings của các đơn thuộc franchise của user (qua sale_id.franchise_id)
        SP = request.env['stock.picking'].sudo()
        domain = [
            '|', ('franchise_id', 'in', list(franchise_ids)),
                 ('sale_id.franchise_id', 'in', list(franchise_ids)),
            ('picking_type_id.code', '=', 'outgoing'),
        ]
        if status and status in PICKING_STATUS_LABELS:
            domain.append(('delivery_status', '=', status))

        try:
            page = max(1, int(page))
        except (TypeError, ValueError):
            page = 1
        offset = (page - 1) * PAGE_SIZE
        total = SP.search_count(domain)
        pickings = SP.search(domain, limit=PAGE_SIZE, offset=offset, order='scheduled_date desc')
        last_page = max(1, (total + PAGE_SIZE - 1) // PAGE_SIZE)
        pager = {
            'page': {'num': page}, 'page_count': last_page,
            'page_previous': {'num': max(1, page - 1)},
            'page_next': {'num': min(last_page, page + 1)},
            'querystring': f'status={status}' if status else '',
        }

        return request.render('wujia_portal_delivery.portal_delivery_tracking', {
            'no_franchise': False, 'pickings': pickings, 'pager': pager,
            'picking_labels': PICKING_STATUS_LABELS, 'status': status,
        })

    @http.route(['/portal/delivery/<int:batch_id>'], type='http', auth='user', sitemap=False)
    def portal_delivery_detail(self, batch_id, **kw):
        franchise_ids = get_active_franchise_ids_filter()
        if not franchise_ids:
            return request.redirect('/portal/delivery')
        Batch = request.env['stock.picking.batch'].sudo()
        batch = Batch.search([
            ('id', '=', batch_id),
            ('picking_ids.franchise_id', 'in', list(franchise_ids)),
        ], limit=1)
        if not batch:
            return request.redirect('/portal/delivery')
        own_pickings = batch.picking_ids.filtered(
            lambda p: (p.franchise_id and p.franchise_id.id in franchise_ids)
                      or (p.sale_id and p.sale_id.franchise_id and p.sale_id.franchise_id.id in franchise_ids)
        )
        return request.render('wujia_portal_delivery.portal_delivery_detail', {
            'batch': batch, 'own_pickings': own_pickings,
            'batch_labels': BATCH_STATUS_LABELS,
            'picking_labels': PICKING_STATUS_LABELS,
        })

    @http.route(['/portal/delivery/<int:batch_id>.ics'], type='http',
                auth='user', sitemap=False)
    def portal_delivery_ics(self, batch_id, **kw):
        """Export lịch giao hàng dạng ICS — import vào Google/Outlook calendar."""
        franchise_ids = get_active_franchise_ids_filter()
        if not franchise_ids:
            raise NotFound()
        Batch = request.env['stock.picking.batch'].sudo()
        batch = Batch.search([
            ('id', '=', batch_id),
            ('picking_ids.franchise_id', 'in', list(franchise_ids)),
        ], limit=1)
        if not batch:
            raise NotFound()
        dt_start = batch.scheduled_date or datetime.now()
        dt_end = dt_start + timedelta(hours=2)
        own_pickings = batch.picking_ids.filtered(
            lambda p: p.franchise_id and p.franchise_id.id in franchise_ids
        )
        summary = f'Giao hàng {batch.name or batch.id}'
        description_parts = [f'Mã lô: {batch.name or batch.id}']
        for p in own_pickings:
            description_parts.append(f'- {p.name}: {p.origin or ""}')
        description = '\n'.join(description_parts)
        location = ', '.join(
            sorted({p.franchise_id.name for p in own_pickings if p.franchise_id})
        )
        ics = (
            'BEGIN:VCALENDAR\r\n'
            'VERSION:2.0\r\n'
            'PRODID:-//WujiaTea//Portal Delivery//VI\r\n'
            'CALSCALE:GREGORIAN\r\n'
            'METHOD:PUBLISH\r\n'
            'BEGIN:VEVENT\r\n'
            f'UID:wujia-delivery-{batch.id}@wujiatea\r\n'
            f'DTSTAMP:{_ics_dt(datetime.utcnow())}\r\n'
            f'DTSTART:{_ics_dt(dt_start)}\r\n'
            f'DTEND:{_ics_dt(dt_end)}\r\n'
            f'SUMMARY:{_ics_escape(summary)}\r\n'
            f'DESCRIPTION:{_ics_escape(description)}\r\n'
            f'LOCATION:{_ics_escape(location)}\r\n'
            'STATUS:CONFIRMED\r\n'
            'END:VEVENT\r\n'
            'END:VCALENDAR\r\n'
        )
        filename = f'delivery-{batch.id}.ics'
        return request.make_response(
            ics,
            headers=[
                ('Content-Type', 'text/calendar; charset=utf-8'),
                ('Content-Disposition', f'attachment; filename="{filename}"'),
                ('Cache-Control', 'private, no-cache'),
            ],
        )
