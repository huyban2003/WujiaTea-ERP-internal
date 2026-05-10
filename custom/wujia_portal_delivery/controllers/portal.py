from odoo import http
from odoo.http import request


PAGE_SIZE = 20

BATCH_STATUS_LABELS = {
    'draft': ('Nháp', 'state-draft'),
    'assigned': ('Đã gán xe', 'state-sent'),
    'loading': ('Đang chất hàng', 'state-in_progress'),
    'delivering': ('Đang giao', 'state-partial'),
    'done': ('Đã giao xong', 'state-done'),
    'cancelled': ('Hủy chuyến', 'state-cancel'),
}

PICKING_STATUS_LABELS = {
    'pending': ('Chờ xếp xe', 'state-draft'),
    'assigned_to_batch': ('Đã gán batch', 'state-sent'),
    'departed': ('Đang giao', 'state-in_progress'),
    'delivered': ('Đã giao', 'state-done'),
    'failed': ('Thất bại', 'state-cancel'),
}


class WujiaPortalDelivery(http.Controller):

    @http.route(['/portal/delivery'], type='http', auth='user', sitemap=False)
    def portal_delivery_list(self, page=1, status='', **kw):
        franchise_ids = request.env.user._get_accessible_franchise_ids()
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
        franchise_ids = request.env.user._get_accessible_franchise_ids()
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
