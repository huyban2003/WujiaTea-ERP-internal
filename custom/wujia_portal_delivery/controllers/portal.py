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

# Batch badge (label, css-modifier) theo delivery_batch_status.
# Mobile → .wujia-mdelivery-badge--*  |  PC desktop → .wj-pc-badge--dlv-*
MOBILE_BATCH_BADGE = {
    'draft': ('Sắp giao', 'soon'),
    'assigned': ('Sắp giao', 'soon'),
    'loading': ('Sắp giao', 'soon'),
    'delivering': ('Đang giao', 'going'),
    'done': ('Đã giao', 'done'),
    'cancelled': ('Đã hủy', 'muted'),
}
PC_BATCH_BADGE = MOBILE_BATCH_BADGE  # cùng label/nhóm; PC dùng class wj-pc-badge--dlv-<modifier>

# Chip lọc (Tất cả/Sắp giao/Đang giao/Đã giao) → nhóm delivery_batch_status.
BATCH_STATUS_GROUP = {
    'soon': ['draft', 'assigned', 'loading'],
    'going': ['delivering'],
    'done': ['done'],
}


def _page_numbers(current, last, edge=1, around=1):
    """Windowed page list cho numbered pager: [1, '…', 4, 5, 6, '…', 20]."""
    if last < 1:
        return []
    keep = set(range(1, edge + 1)) | set(range(last - edge + 1, last + 1))
    keep |= set(range(current - around, current + around + 1))
    pages = sorted(p for p in keep if 1 <= p <= last)
    result, prev = [], 0
    for p in pages:
        if prev and p - prev > 1:
            result.append('…')
        result.append(p)
        prev = p
    return result


def _chip_counts(Batch, base_domain):
    """Đếm chuyến theo nhóm cho chips card-head — 4 search_count (field có index)."""
    return {
        'all': Batch.search_count(base_domain),
        'going': Batch.search_count(base_domain + [('delivery_batch_status', 'in', BATCH_STATUS_GROUP['going'])]),
        'soon': Batch.search_count(base_domain + [('delivery_batch_status', 'in', BATCH_STATUS_GROUP['soon'])]),
        'done': Batch.search_count(base_domain + [('delivery_batch_status', 'in', BATCH_STATUS_GROUP['done'])]),
    }


def _hhmm(dt):
    return dt.strftime('%H:%M') if dt else '--'


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
    def portal_delivery_list(self, page=1, bs='', date_from='', date_to='', q='', **kw):
        franchise_ids = get_active_franchise_ids_filter()
        if not franchise_ids:
            return request.render('wujia_portal_delivery.portal_delivery_tracking', {
                'no_franchise': True, 'batches': [], 'view_state': 'empty',
                'm_pager': {}, 'chip_counts': {},
                'date_from': '', 'date_to': '', 'bs': '', 'q': '',
            })

        try:
            page = max(1, int(page))
        except (TypeError, ValueError):
            page = 1
        offset = (page - 1) * PAGE_SIZE
        q = (q or '').strip()

        # Batch-centric (1 thẻ = 1 chuyến xe) — nuôi cả desktop (Figma 4766) + mobile (4731).
        batches, m_pager, chip_counts, view_state = [], {}, {}, 'list'
        try:
            Batch = request.env['stock.picking.batch'].sudo()
            base_domain = [
                '|', ('picking_ids.franchise_id', 'in', list(franchise_ids)),
                     ('picking_ids.sale_id.franchise_id', 'in', list(franchise_ids)),
            ]
            d_from, d_to = _parse_date(date_from), _parse_date(date_to)
            if d_from:
                base_domain.append(('planned_departure', '>=', datetime.combine(d_from, dt_time.min)))
            if d_to:
                base_domain.append(('planned_departure', '<=', datetime.combine(d_to, dt_time.max)))
            # Chips card-head: đếm theo scope franchise+date (không status, không keyword).
            chip_counts = _chip_counts(Batch, base_domain)

            bdomain = list(base_domain)
            if bs in BATCH_STATUS_GROUP:
                bdomain.append(('delivery_batch_status', 'in', BATCH_STATUS_GROUP[bs]))
            if q:
                bdomain += ['|', ('name', 'ilike', q),
                                 ('picking_ids.sale_id.name', 'ilike', q)]
            total = Batch.search_count(bdomain)
            recs = Batch.search(bdomain, limit=PAGE_SIZE, offset=offset,
                                order='planned_departure desc, id desc')
            for b in recs:
                own = b.picking_ids.filtered(
                    lambda p: (p.franchise_id and p.franchise_id.id in franchise_ids)
                    or (p.sale_id and p.sale_id.franchise_id and p.sale_id.franchise_id.id in franchise_ids)
                )
                label, modifier = MOBILE_BATCH_BADGE.get(
                    b.delivery_batch_status, (b.delivery_batch_status or '—', 'muted'))
                v = b.vehicle_id
                vehicle_str = ('%s · %s' % (v.name, v.driver_name)) if v and v.driver_name else (v.name if v else '—')
                upd = b.actual_departure or b.write_date
                batches.append({
                    # Keys mobile (S24) — KHÔNG đổi:
                    'id': b.id, 'name': b.name or '—',
                    'label': label, 'modifier': modifier,
                    'departure': _short_departure(b.planned_departure),
                    'orders': _related_orders(own),
                    # Keys PC desktop:
                    'pc_label': label, 'pc_modifier': modifier,
                    'departure_full': _full_departure(b.planned_departure),
                    'vehicle': vehicle_str,
                    'plate': (v.license_plate if v and v.license_plate else '—'),
                    'updated': _hhmm(upd),
                })
            last_page = max(1, (total + PAGE_SIZE - 1) // PAGE_SIZE)
            m_pager = {
                'page': {'num': page}, 'page_count': last_page, 'page_total': total,
                'page_previous': {'num': max(1, page - 1)},
                'page_next': {'num': min(last_page, page + 1)},
                'page_nums': _page_numbers(page, last_page),
                'offset': offset, 'count': len(batches),
                'querystring': '&'.join(p for p in (
                    f'bs={bs}' if bs else '',
                    f'date_from={date_from}' if date_from else '',
                    f'date_to={date_to}' if date_to else '',
                    f'q={q}' if q else '',
                ) if p),
            }
            if not batches:
                view_state = 'empty'
        except Exception:
            _logger.exception('Wujia portal delivery — batch list failed')
            view_state = 'error'

        # QA preview: ?_preview=loading|error|empty|list (drive cả desktop + mobile).
        preview = kw.get('_preview')
        if preview in ('loading', 'error', 'empty', 'list'):
            view_state = preview

        return request.render('wujia_portal_delivery.portal_delivery_tracking', {
            'no_franchise': False,
            'batches': batches, 'view_state': view_state, 'm_pager': m_pager,
            'chip_counts': chip_counts,
            'date_from': date_from, 'date_to': date_to, 'bs': bs, 'q': q,
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

        # PC desktop (Figma 4766:1091): timeline 3 bước + SO chips + kho xuất + tên CH.
        status = batch.delivery_batch_status or ''
        tl_steps = (
            'done' if (batch.actual_departure or status in ('delivering', 'done')) else 'inactive',
            'active' if status == 'delivering' else ('done' if status == 'done' else 'inactive'),
            'done' if status == 'done' else 'inactive',
        )
        tl_times = (
            _hhmm(batch.actual_departure or (batch.planned_departure if status in ('delivering', 'done') else None)),
            _hhmm(batch.write_date if status in ('delivering', 'done') else None),
            _hhmm(batch.write_date if status == 'done' else None),
        )
        so_names = []
        for p in own_pickings:
            if p.sale_id and p.sale_id.name and p.sale_id.name not in so_names:
                so_names.append(p.sale_id.name)
        src_location = '—'
        if own_pickings and own_pickings[0].location_id:
            loc = own_pickings[0].location_id
            src_location = loc.complete_name or loc.name or '—'
        fr = (own_pickings[:1].mapped('franchise_id')
              or own_pickings[:1].mapped('sale_id.franchise_id'))[:1]
        store_label = (('[%s] ' % fr.code) if fr and fr.code else '') + (fr.name if fr else '') or '—'

        return request.render('wujia_portal_delivery.portal_delivery_detail', {
            'batch': batch, 'own_pickings': own_pickings,
            'products': products,
            # Mobile (S24):
            'm_badge': (label, modifier),
            'm_departure_full': _full_departure(batch.planned_departure),
            'm_updated': _full_departure(updated),
            'm_orders': _related_orders(own_pickings),
            # PC desktop:
            'pc_badge': (label, modifier),
            'pc_departure': _full_departure(batch.planned_departure),
            'pc_updated': _full_departure(updated),
            'pc_orders': _related_orders(own_pickings),
            'so_names': so_names,
            'tl_steps': tl_steps,
            'tl_times': tl_times,
            'src_location': src_location,
            'store_label': store_label,
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
