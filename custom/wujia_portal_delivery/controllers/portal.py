import logging
from datetime import datetime, timedelta, time as dt_time

from werkzeug.exceptions import NotFound

from odoo import http
from odoo.http import request

from odoo.addons.wujia_portal_base.controllers.portal import (
    get_active_franchise_ids_filter,
)

_logger = logging.getLogger(__name__)


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

# Mobile batch card — Figma 4731:2 (list batch-centric: 1 thẻ = 1 chuyến xe).
# (label, css-modifier) theo delivery_batch_status. Modifier khớp .wujia-mdelivery-badge--*.
MOBILE_BATCH_BADGE = {
    'draft': ('Sắp giao', 'soon'),
    'assigned': ('Sắp giao', 'soon'),
    'loading': ('Sắp giao', 'soon'),
    'delivering': ('Đang giao', 'going'),
    'done': ('Đã giao', 'done'),
    'cancelled': ('Đã hủy', 'muted'),
}

# Chip lọc mobile (Tất cả/Sắp giao/Đang giao/Đã giao) → nhóm delivery_batch_status.
BATCH_STATUS_GROUP = {
    'soon': ['draft', 'assigned', 'loading'],
    'going': ['delivering'],
    'done': ['done'],
}


def _parse_date(value):
    """'YYYY-MM-DD' (input type=date) → date, hoặc None."""
    if not value:
        return None
    try:
        return datetime.strptime(value, '%Y-%m-%d').date()
    except (TypeError, ValueError):
        return None


def _short_departure(dt):
    """'29/06 · 07:30' — Figma 4731 list card."""
    if not dt:
        return '—'
    return '%s · %s' % (dt.strftime('%d/%m'), dt.strftime('%H:%M'))


def _full_departure(dt):
    """'29/06/2026 · 07:30' — Figma 4731 detail."""
    if not dt:
        return '—'
    return dt.strftime('%d/%m/%Y · %H:%M')


def _related_orders(pickings):
    """Chuỗi 'SO…, SO… +N' — đơn liên quan trong chuyến (mobile)."""
    names = []
    for so in pickings.mapped('sale_id'):
        if so.name and so.name not in names:
            names.append(so.name)
    if not names:
        return '—'
    text = ', '.join(names[:2])
    if len(names) > 2:
        text += ' +%d' % (len(names) - 2)
    return text


class WujiaPortalDelivery(http.Controller):

    @http.route(['/portal/delivery'], type='http', auth='user', sitemap=False)
    def portal_delivery_list(self, page=1, status='', date_from='', date_to='', bs='', **kw):
        franchise_ids = get_active_franchise_ids_filter()
        if not franchise_ids:
            return request.render('wujia_portal_delivery.portal_delivery_tracking', {
                'no_franchise': True, 'pickings': [], 'pager': {},
                'picking_labels': PICKING_STATUS_LABELS, 'status': '',
                'batches': [], 'view_state': 'empty', 'm_pager': {},
                'date_from': '', 'date_to': '', 'bs': '',
            })

        try:
            page = max(1, int(page))
        except (TypeError, ValueError):
            page = 1

        # ----- Desktop (≥992px): danh sách phiếu xuất (picking) — giữ nguyên -----
        SP = request.env['stock.picking'].sudo()
        domain = [
            '|', ('franchise_id', 'in', list(franchise_ids)),
                 ('sale_id.franchise_id', 'in', list(franchise_ids)),
            ('picking_type_id.code', '=', 'outgoing'),
        ]
        if status and status in PICKING_STATUS_LABELS:
            domain.append(('delivery_status', '=', status))
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

        # ----- Mobile (<992px): thẻ theo CHUYẾN XE (batch) — Figma 4731:2 -----
        batches, m_pager, view_state = [], {}, 'list'
        try:
            Batch = request.env['stock.picking.batch'].sudo()
            bdomain = [
                '|', ('picking_ids.franchise_id', 'in', list(franchise_ids)),
                     ('picking_ids.sale_id.franchise_id', 'in', list(franchise_ids)),
            ]
            if bs in BATCH_STATUS_GROUP:
                bdomain.append(('delivery_batch_status', 'in', BATCH_STATUS_GROUP[bs]))
            d_from, d_to = _parse_date(date_from), _parse_date(date_to)
            if d_from:
                bdomain.append(('planned_departure', '>=', datetime.combine(d_from, dt_time.min)))
            if d_to:
                bdomain.append(('planned_departure', '<=', datetime.combine(d_to, dt_time.max)))
            m_total = Batch.search_count(bdomain)
            recs = Batch.search(bdomain, limit=PAGE_SIZE, offset=offset,
                                order='planned_departure desc, id desc')
            for b in recs:
                own = b.picking_ids.filtered(
                    lambda p: (p.franchise_id and p.franchise_id.id in franchise_ids)
                    or (p.sale_id and p.sale_id.franchise_id and p.sale_id.franchise_id.id in franchise_ids)
                )
                label, modifier = MOBILE_BATCH_BADGE.get(
                    b.delivery_batch_status, (b.delivery_batch_status or '—', 'muted'))
                batches.append({
                    'id': b.id, 'name': b.name or '—',
                    'label': label, 'modifier': modifier,
                    'departure': _short_departure(b.planned_departure),
                    'orders': _related_orders(own),
                })
            m_last = max(1, (m_total + PAGE_SIZE - 1) // PAGE_SIZE)
            m_pager = {
                'page': {'num': page}, 'page_count': m_last,
                'page_previous': {'num': max(1, page - 1)},
                'page_next': {'num': min(m_last, page + 1)},
                'querystring': '&'.join(p for p in (
                    f'bs={bs}' if bs else '',
                    f'date_from={date_from}' if date_from else '',
                    f'date_to={date_to}' if date_to else '',
                ) if p),
            }
            if not batches:
                view_state = 'empty'
        except Exception:
            _logger.exception('Wujia portal delivery — mobile batch list failed')
            view_state = 'error'

        # QA preview: ?_preview=loading|error|empty|list (chỉ ảnh hưởng block mobile).
        preview = kw.get('_preview')
        if preview in ('loading', 'error', 'empty', 'list'):
            view_state = preview

        return request.render('wujia_portal_delivery.portal_delivery_tracking', {
            'no_franchise': False, 'pickings': pickings, 'pager': pager,
            'picking_labels': PICKING_STATUS_LABELS, 'status': status,
            'batches': batches, 'view_state': view_state, 'm_pager': m_pager,
            'date_from': date_from, 'date_to': date_to, 'bs': bs,
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

        # Mobile (Figma 4731 detail): gom sản phẩm trong chuyến theo product → SL + ĐVT.
        products, seen = [], {}
        for mv in own_pickings.mapped('move_ids'):
            prod = mv.product_id
            if not prod:
                continue
            row = seen.get(prod.id)
            if row is None:
                row = {
                    'name': prod.display_name or prod.name or '—',
                    'qty': 0.0,
                    'uom': mv.product_uom.name if mv.product_uom else (prod.uom_id.name or ''),
                }
                seen[prod.id] = row
                products.append(row)
            row['qty'] += mv.product_uom_qty or 0.0

        label, modifier = MOBILE_BATCH_BADGE.get(
            batch.delivery_batch_status, (batch.delivery_batch_status or '—', 'muted'))
        updated = batch.actual_departure or batch.write_date

        return request.render('wujia_portal_delivery.portal_delivery_detail', {
            'batch': batch, 'own_pickings': own_pickings,
            'batch_labels': BATCH_STATUS_LABELS,
            'picking_labels': PICKING_STATUS_LABELS,
            'products': products,
            'm_badge': (label, modifier),
            'm_departure_full': _full_departure(batch.planned_departure),
            'm_updated': _full_departure(updated),
            'm_orders': _related_orders(own_pickings),
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
