"""Wujia portal — Return Request controller (single-product, BA spec K + Task STT3).

Routes:
- GET  /portal/return                              list (filter state/date/q)
- GET, POST /portal/return/new                     create draft or submit
- GET  /portal/return/<int>                        detail
- GET  /portal/return/<int>/attachment/<int>       download attachment
"""
import json
import logging
from datetime import datetime, timedelta

from werkzeug.exceptions import Forbidden, NotFound

from odoo import fields, http
from odoo.exceptions import ValidationError
from odoo.http import request
from odoo.tools.mimetypes import guess_mimetype

from odoo.addons.wujia_portal_base.controllers.portal import (
    get_active_franchise_ids_filter,
)
from odoo.addons.wujia_portal_base.controllers.utils import (
    attach_files_to_record,
    fmt_local_dt,
    local_day_range_utc,
    portal_tz,
)

_logger = logging.getLogger(__name__)

PAGE_SIZE = 20
MAX_PAGE_SIZE = 100

# Chỉ đơn đã xác nhận trong 10 ngày mới tạo được yêu cầu (BA STT3 #4).
ORDER_WINDOW_DAYS = 10

# Minh chứng (BA STT3 #7). Kiểm bằng MIME THẬT (sniff nội dung), không tin header.
IMAGE_MIME = ('image/jpeg', 'image/jpg', 'image/png')
VIDEO_MIME = ('video/mp4', 'video/quicktime')
MIN_IMAGES = 3
MAX_IMAGES = 5
MAX_IMAGE_MB = 5
MAX_VIDEOS = 1
MAX_VIDEO_MB = 10
MAX_TOTAL_MB = 30

# Trạng thái portal thấy (label + badge class).
STATE_LABELS = {
    'draft': ('Nháp', 'wujia-badge-muted'),
    'submitted': ('Đã gửi', 'wujia-badge-info'),
    'reviewing': ('Đang xử lý', 'wujia-badge-warning'),
    'approved': ('Đã duyệt', 'wujia-badge-success'),
    'processing': ('Đang xử lý', 'wujia-badge-warning'),
    'done': ('Hoàn tất', 'wujia-badge-success'),
    'rejected': ('Từ chối', 'wujia-badge-danger'),
    'cancelled': ('Đã huỷ', 'wujia-badge-muted'),
}

# Phương án xử lý HQ chốt khi duyệt.
RESOLUTION_LABELS = {
    'exchange': 'Đổi hàng',
    'return': 'Trả hàng',
    'compensation': 'Bù hàng',
    'refuse': 'Từ chối',
}

# Tình trạng bù hàng (label + badge class) — hiển thị tiến độ bù cho cửa hàng.
COMPENSATION_STATUS_LABELS = {
    'none': ('Chưa xử lý', 'wujia-badge-muted'),
    'allocated': ('Đã lên đơn bù', 'wujia-badge-info'),
    'partial': ('Đang bù một phần', 'wujia-badge-warning'),
    'done': ('Đã bù đủ', 'wujia-badge-success'),
}


# Bộ lọc trạng thái portal (UAT-BH-006) — nguồn DUY NHẤT cho dropdown PC + mobile.
# Nhãn ở đây phải trùng nhãn badge trên card, nên lọc theo NHÃN chứ không theo state
# thô: 'reviewing' và 'processing' cùng badge "Đang xử lý" ⇒ gộp; "Đang bù một phần"
# là pseudo-state (processing + compensation_status='partial'), không có trong schema.
# Giữ 'Nháp' vì portal cho lưu nháp nên danh sách có thật trạng thái này.
FILTER_OPTIONS = [
    ('draft', 'Nháp'),
    ('submitted', 'Đã gửi'),
    ('processing', 'Đang xử lý'),
    ('approved', 'Đã duyệt'),
    ('partial', 'Đang bù một phần'),
    ('done', 'Hoàn tất'),
    ('rejected', 'Từ chối'),
    ('cancelled', 'Đã huỷ'),
]


def state_filter_domain(key):
    """Domain của một lựa chọn lọc — [] nếu key rỗng hoặc không hợp lệ."""
    if key == 'partial':
        return [('state', '=', 'processing'),
                ('compensation_status', '=', 'partial')]
    if key == 'processing':
        return [('state', 'in', ('reviewing', 'processing')),
                '!', ('compensation_status', '=', 'partial')]
    if key in dict(FILTER_OPTIONS):
        return [('state', '=', key)]
    return []


def state_label(rr):
    """Nhãn trạng thái portal — 6 nhãn BA, suy từ state + tiến độ bù.

    'Đang bù một phần' KHÔNG phải state trong schema: nó là `processing` +
    `compensation_status='partial'` (BA: không đổi schema chỉ để khớp label).
    """
    if rr.state == 'processing' and rr.compensation_status == 'partial':
        return COMPENSATION_STATUS_LABELS['partial']
    return STATE_LABELS.get(rr.state, (rr.state, 'wujia-badge-muted'))


class WujiaPortalReturn(http.Controller):

    @http.route(['/portal/return'], type='http', auth='user', sitemap=False)
    def portal_return_list(self, page=1, state='', date_from='', date_to='', q='',
                           page_size=None, notice='', **kw):
        franchise_ids = get_active_franchise_ids_filter()
        if not franchise_ids:
            return request.render('wujia_portal_return.portal_return_list',
                                  self._list_ctx(no_franchise=True, notice='no_store'))

        domain = [('franchise_id', 'in', list(franchise_ids))]
        domain += state_filter_domain(state)
        q = (q or '').strip()
        if q:
            # Action 2: mã yêu cầu · mã đơn · chuyến · tên/mã sản phẩm.
            domain += ['|', '|', '|', '|',
                       ('name', 'ilike', q),
                       ('sale_order_id.name', 'ilike', q),
                       ('batch_id.name', 'ilike', q),
                       ('product_id.name', 'ilike', q),
                       ('product_id.default_code', 'ilike', q)]

        df, dt_ = self._parse_date(date_from), self._parse_date(date_to)
        if (date_from and not df) or (date_to and not dt_) or (df and dt_ and df > dt_):
            return request.render('wujia_portal_return.portal_return_list',
                                  self._list_ctx(notice='bad_filter', state=state, q=q,
                                                 date_from=date_from, date_to=date_to))
        # Khoảng ngày theo giờ địa phương (Odoo lưu naive UTC → lệch −7h nếu so thẳng).
        utc_from, utc_to = local_day_range_utc(df, dt_, portal_tz())
        if utc_from:
            domain.append(('request_date', '>=', utc_from))
        if utc_to:
            domain.append(('request_date', '<=', utc_to))

        page = self._parse_int(page, 1, minimum=1)
        size = self._parse_int(page_size, PAGE_SIZE, minimum=1, maximum=MAX_PAGE_SIZE)
        Model = request.env['wujia.return.request'].sudo()
        total = Model.search_count(domain)
        last_page = max(1, (total + size - 1) // size)
        page = min(page, last_page)
        returns = Model.search(domain, limit=size, offset=(page - 1) * size,
                               order='request_date desc')
        pager = {
            'page': {'num': page}, 'page_count': last_page,
            'page_previous': {'num': max(1, page - 1)},
            'page_next': {'num': min(last_page, page + 1)},
            'querystring': '&'.join(
                f'{k}={v}' for k, v in
                [('state', state), ('date_from', date_from), ('date_to', date_to),
                 ('q', q), ('page_size', size if size != PAGE_SIZE else '')]
                if v
            ),
        }
        return request.render('wujia_portal_return.portal_return_list', self._list_ctx(
            returns=returns, pager=pager, state=state, date_from=date_from,
            date_to=date_to, q=q, notice=notice, total=total,
        ))

    @http.route(['/portal/return/new'], type='http', auth='user',
                methods=['GET', 'POST'], sitemap=False, csrf=True)
    def portal_return_new(self, **post):
        franchise_ids = get_active_franchise_ids_filter()
        if not franchise_ids:
            return request.redirect('/portal/return?notice=no_store')

        if request.httprequest.method != 'POST':
            return self._render_form()

        images = request.httprequest.files.getlist('images')
        video = request.httprequest.files.getlist('video')
        try:
            vals, action = self._parse_payload(post, franchise_ids)
            self._validate_evidence(images, video, require_min=action == 'send')
        except ValidationError as e:
            return self._render_form(error=str(e), prefill=post)

        try:
            rr = request.env['wujia.return.request'].sudo().create(vals)
        except ValidationError as e:
            return self._render_form(error=str(e), prefill=post)
        except Exception:                          # noqa: BLE001 — không lộ traceback ra portal
            _logger.exception('Return request create failed')
            return self._render_form(
                error="Không thể gửi yêu cầu. Vui lòng kiểm tra lại thông tin và thử lại.",
                prefill=post)

        try:
            self._attach_evidence(rr, images, video)
        except ValidationError as e:
            rr.sudo().unlink()                     # không để phiếu/attachment mồ côi
            return self._render_form(error=str(e), prefill=post)

        if action == 'send':
            rr.sudo().write({'state': 'submitted'})
        return request.redirect(f'/portal/return/{rr.id}?message=created')

    @http.route(['/portal/return/<int:request_id>'], type='http',
                auth='user', sitemap=False)
    def portal_return_detail(self, request_id, **kw):
        franchise_ids = get_active_franchise_ids_filter()
        if not franchise_ids:
            return request.redirect('/portal/return?notice=no_store')
        rr = request.env['wujia.return.request'].sudo().search([
            ('id', '=', request_id),
            ('franchise_id', 'in', list(franchise_ids)),
        ], limit=1)
        if not rr:
            # Không phân biệt "không có" với "của cửa hàng khác" (chống dò ID).
            return request.redirect('/portal/return?notice=not_found')
        return request.render('wujia_portal_return.portal_return_detail', {
            'rr': rr, 'state_labels': STATE_LABELS,
            'wj_state_label': state_label,
            'resolution_labels': RESOLUTION_LABELS,
            'comp': self._build_compensation_ctx(rr),
            'wj_dt': fmt_local_dt,
            'message': kw.get('message'),
        })

    @http.route(['/portal/return/<int:request_id>/attachment/<int:att_id>'],
                type='http', auth='user', sitemap=False)
    def portal_return_attachment_download(self, request_id, att_id, **kw):
        """Stream attachment — ACL: chỉ user truy cập franchise của RR."""
        franchise_ids = get_active_franchise_ids_filter()
        if not franchise_ids:
            raise Forbidden()
        rr = request.env['wujia.return.request'].sudo().search([
            ('id', '=', request_id),
            ('franchise_id', 'in', list(franchise_ids)),
        ], limit=1)
        if not rr:
            raise NotFound()
        allowed = set(rr.image_attachment_ids.ids) | set(rr.video_attachment_ids.ids)
        if att_id not in allowed:
            raise Forbidden()
        att = request.env['ir.attachment'].sudo().browse(att_id).exists()
        if not att:
            raise NotFound()
        return request.env['ir.binary']._get_stream_from(att).get_response(
            as_attachment=False,
        )

    # ============================================================== helpers
    @staticmethod
    def _parse_int(value, default, minimum=None, maximum=None):
        try:
            value = int(value)
        except (TypeError, ValueError):
            return default
        if minimum is not None:
            value = max(minimum, value)
        if maximum is not None:
            value = min(maximum, value)
        return value

    @staticmethod
    def _parse_date(value):
        try:
            return datetime.strptime(value, '%Y-%m-%d').date() if value else None
        except (TypeError, ValueError):
            return None

    def _list_ctx(self, **kw):
        ctx = {
            'no_franchise': False, 'returns': [], 'pager': {}, 'total': 0,
            'state_labels': STATE_LABELS, 'wj_state_label': state_label,
            'comp_status_labels': COMPENSATION_STATUS_LABELS,
            'filter_options': FILTER_OPTIONS,
            'state': '', 'date_from': '', 'date_to': '', 'q': '', 'notice': '',
            'wj_dt': fmt_local_dt,
        }
        ctx.update(kw)
        return ctx

    def _eligible_order_domain(self, franchise_ids):
        """Đơn được phép làm căn cứ: đã xác nhận, trong 10 ngày (BA STT3 #4).

        `date_order` = ngày xác nhận với đơn đã confirm
        (`sale.order._prepare_confirmation_values`).
        """
        cutoff = fields.Datetime.now() - timedelta(days=ORDER_WINDOW_DAYS)
        return [
            ('franchise_id', 'in', list(franchise_ids)),
            ('state', 'in', ['sale', 'done']),
            ('date_order', '>=', cutoff),
        ]

    def _check_compensation_config(self, product):
        """Cấu hình bù của sản phẩm (BA STT3 #6). Trả None nếu hợp lệ."""
        msg = ("Sản phẩm chưa được cấu hình chính sách bù hàng. "
               "Vui lòng liên hệ Ngô Gia.")
        if not product.compensation_enabled or not product.compensation_claim_uom_id:
            return msg
        delivery_uom = product.compensation_delivery_uom_id
        if product.compensation_policy == 'accumulate':
            unit = product.compensation_unit_qty or 0.0
            # BA: tỷ lệ quy đổi chỉ hỗ trợ số nguyên > 0.
            if not delivery_uom or unit <= 0 or abs(unit - round(unit)) > 1e-6:
                return msg
        elif delivery_uom and delivery_uom != product.compensation_claim_uom_id:
            # exact: quy đổi qua engine UoM → phải cùng cây đơn vị.
            root = product.env['wujia.compensation.process.wizard']._uom_root
            if root(delivery_uom) != root(product.compensation_claim_uom_id):
                return msg
        return None

    @staticmethod
    def _file_size(f):
        f.stream.seek(0, 2)
        size = f.stream.tell()
        f.stream.seek(0)
        return size

    @staticmethod
    def _real_mime(f):
        """MIME đọc từ NỘI DUNG file.

        ⚠️ `guess_mimetype` của Odoo không có chữ ký video (và `python-magic`
        không được cài) ⇒ mp4/mov ra `application/octet-stream`. Tự đọc hộp
        `ftyp` của ISO-BMFF: byte 4–8 là 'ftyp', 8–12 là brand.
        """
        head = f.stream.read(4096)
        f.stream.seek(0)
        if head[4:8] == b'ftyp':
            brand = head[8:12]
            return 'video/quicktime' if brand == b'qt  ' else 'video/mp4'
        return guess_mimetype(head)

    def _validate_evidence(self, images, video, require_min=True):
        """Đếm/dung lượng/MIME thật của minh chứng (BA STT3 #7) — chạy TRƯỚC create."""
        images = [f for f in (images or []) if f and f.filename]
        video = [f for f in (video or []) if f and f.filename]
        if len(images) > MAX_IMAGES or (require_min and len(images) < MIN_IMAGES):
            raise ValidationError(
                f"Cần tải từ {MIN_IMAGES} đến {MAX_IMAGES} ảnh minh chứng.")
        if len(video) > MAX_VIDEOS:
            raise ValidationError(
                f"Chỉ được tải tối đa {MAX_VIDEOS} video minh chứng.")

        total = 0
        for f in images:
            self._check_one_file(f, IMAGE_MIME, MAX_IMAGE_MB)
            total += self._file_size(f)
        for f in video:
            self._check_one_file(f, VIDEO_MIME, MAX_VIDEO_MB)
            total += self._file_size(f)
        if total > MAX_TOTAL_MB * 1024 * 1024:
            raise ValidationError(
                f"Tổng dung lượng minh chứng không được vượt quá {MAX_TOTAL_MB} MB.")

    def _check_one_file(self, f, allowed_mime, max_mb):
        if self._file_size(f) > max_mb * 1024 * 1024:
            raise ValidationError(
                "Tệp không đúng định dạng hoặc vượt quá dung lượng cho phép.")
        # MIME THẬT (sniff nội dung) — header trình duyệt và đuôi file đều đổi được.
        real = self._real_mime(f)
        if real not in allowed_mime:
            raise ValidationError(
                "Tệp không đúng định dạng hoặc vượt quá dung lượng cho phép.")
        # Ghi đè header client bằng MIME thật: attachment lưu đúng loại, và
        # `attach_files_to_record` (kiểm theo header) không loại nhầm .mov mà
        # trình duyệt gửi kèm 'application/octet-stream'.
        f.headers['Content-Type'] = real

    def _attach_evidence(self, rr, images, video):
        """Tạo attachment sau khi đã validate — tái dùng helper chung của portal."""
        images = [f for f in (images or []) if f and f.filename]
        video = [f for f in (video or []) if f and f.filename]
        vals = {}
        if images:
            atts = attach_files_to_record(
                rr, images, allowed_mime=IMAGE_MIME,
                max_size_mb=MAX_IMAGE_MB, max_count=MAX_IMAGES)
            vals['image_attachment_ids'] = [(4, a.id) for a in atts]
        if video:
            atts = attach_files_to_record(
                rr, video, allowed_mime=VIDEO_MIME,
                max_size_mb=MAX_VIDEO_MB, max_count=MAX_VIDEOS)
            vals['video_attachment_ids'] = [(4, a.id) for a in atts]
        if vals:
            rr.sudo().write(vals)

    def _build_compensation_ctx(self, rr):
        """Context hiển thị tiến độ bù cho cửa hàng (read-only).

        Trả None khi HQ chưa chốt phương án → template ẩn card, không lộ số 0.
        Chỉ đọc field compute đã có trên record → không đổi schema.
        """
        if not rr.resolution_type:
            return None
        ctx = {
            'resolution_label': RESOLUTION_LABELS.get(
                rr.resolution_type, rr.resolution_type),
            'is_compensation': rr.resolution_type == 'compensation',
        }
        if not ctx['is_compensation']:
            return ctx
        approved = rr.approved_qty or 0.0
        compensated = rr.compensated_qty or 0.0
        remaining = rr.remaining_qty or 0.0
        allocations = rr.allocation_ids
        ctx.update({
            'approved_qty': approved,
            'approved_uom': rr.approved_uom_id.name or '',
            'product_label': rr.compensation_product_id.display_name or '—',
            'allocated_qty': rr.allocated_qty or 0.0,
            'compensated_qty': compensated,
            'remaining_qty': remaining,
            'progress_pct': min(100, round(compensated / approved * 100))
                            if approved > 0 else 0,
            'status': COMPENSATION_STATUS_LABELS.get(
                rr.compensation_status,
                (rr.compensation_status or '—', 'wujia-badge-muted')),
            'approval_note': rr.approval_note or '',
            # BA STT3 #12: SO bù bị huỷ thì quyền lợi đóng lại, cửa hàng phải tạo
            # yêu cầu mới — báo rõ thay vì để trang trông như đang chờ giao.
            'all_cancelled': bool(allocations)
                             and all(a.state == 'cancel' for a in allocations),
            'orders': [
                {
                    'name': so.name,
                    'state_label': dict(so._fields['state']._description_selection(
                        request.env)).get(so.state, so.state),
                    'delivery_label': self._so_delivery_label(so),
                }
                for so in rr.compensation_so_ids
            ],
        })
        return ctx

    def _so_delivery_label(self, so):
        """Nhãn tiến độ giao của 1 đơn bù (đếm phiếu giao done/tổng)."""
        if so.state == 'cancel':
            return 'Đơn bù đã bị hủy'
        if 'picking_ids' not in so._fields:
            return ''
        pickings = so.picking_ids
        total = len(pickings)
        if not total:
            return 'Chưa tạo phiếu giao'
        done = len(pickings.filtered(lambda p: p.state == 'done'))
        if done == 0:
            return 'Chưa giao'
        if done >= total:
            return 'Đã giao đủ'
        return 'Đã giao %d/%d phiếu' % (done, total)

    def _render_form(self, error=None, prefill=None):
        franchise_ids = get_active_franchise_ids_filter()
        franchises = request.env['wujia.franchise.management'].sudo().browse(
            franchise_ids)
        orders = request.env['sale.order'].sudo().search(
            self._eligible_order_domain(franchise_ids), order='date_order desc')
        issue_types = request.env['wujia.return.issue.type'].sudo().search(
            [('active', '=', True)])
        # Map order_id -> [{id, label}] cho cascade select sản phẩm.
        order_lines = {
            o.id: [{
                'id': line.id,
                'label': '%s (%s %s)' % (
                    line.product_id.display_name,
                    ('{:,.0f}'.format(line.product_uom_qty or 0)),
                    line.product_uom_id.name or ''),
            } for line in o.order_line if line.product_id]
            for o in orders
        }
        return request.render('wujia_portal_return.portal_return_form', {
            'franchises': franchises, 'orders': orders,
            'order_lines_json': json.dumps(order_lines),
            'issue_types': issue_types, 'state_labels': STATE_LABELS,
            'error': error, 'values': prefill or {},
            'window_days': ORDER_WINDOW_DAYS,
            'min_images': MIN_IMAGES, 'max_images': MAX_IMAGES,
            'max_total_mb': MAX_TOTAL_MB, 'max_video_mb': MAX_VIDEO_MB,
            'wj_dt': fmt_local_dt,
            'today': datetime.now(),
        })

    def _parse_payload(self, post, accessible_fids):
        try:
            franchise_id = int(post.get('franchise_id') or 0)
        except (TypeError, ValueError):
            raise ValidationError("Cửa hàng không hợp lệ.")
        if franchise_id not in set(accessible_fids):
            raise ValidationError("Cửa hàng không truy cập được.")

        # Đơn gốc + dòng sản phẩm (bắt buộc — SP phải thuộc đơn).
        try:
            sale_order_id = int(post.get('sale_order_id') or 0)
            sale_order_line_id = int(post.get('sale_order_line_id') or 0)
        except (TypeError, ValueError):
            raise ValidationError("Đơn hàng / sản phẩm không hợp lệ.")
        if not sale_order_id or not sale_order_line_id:
            raise ValidationError("Vui lòng chọn đơn hàng gốc và sản phẩm.")
        # Kiểm lại điều kiện đơn ở SERVER — form chỉ là gợi ý, client sửa được.
        order = request.env['sale.order'].sudo().search(
            self._eligible_order_domain([franchise_id])
            + [('id', '=', sale_order_id)], limit=1)
        if not order:
            raise ValidationError(
                f"Đơn hàng không hợp lệ hoặc đã quá thời hạn {ORDER_WINDOW_DAYS} ngày.")
        line = order.order_line.filtered(lambda l: l.id == sale_order_line_id)
        if not line or not line.product_id:
            raise ValidationError("Sản phẩm phải thuộc đơn hàng gốc của cửa hàng.")

        config_error = self._check_compensation_config(line.product_id)
        if config_error:
            raise ValidationError(config_error)

        issue_type = request.env['wujia.return.issue.type'].sudo().search(
            [('id', '=', self._parse_int(post.get('issue_type_id'), 0)),
             ('active', '=', True)], limit=1)
        if not issue_type:
            raise ValidationError("Vui lòng chọn loại lỗi.")

        try:
            request_qty = float(post.get('request_qty') or 0)
        except (TypeError, ValueError):
            request_qty = 0.0
        if request_qty <= 0:
            raise ValidationError("Số lượng yêu cầu phải lớn hơn 0.")

        opening = post.get('opening_datetime') or ''
        opening_dt = False
        for fmt in ('%Y-%m-%dT%H:%M', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M'):
            try:
                opening_dt = datetime.strptime(opening, fmt)
                break
            except ValueError:
                continue
        if not opening_dt:
            raise ValidationError("Vui lòng nhập thời gian mở hàng hợp lệ.")

        production_date = post.get('production_date') or False

        action = (post.get('action') or 'draft').strip()
        if action not in ('draft', 'send'):
            action = 'draft'

        vals = {
            'franchise_id': franchise_id,
            'sale_order_id': sale_order_id,
            'sale_order_line_id': sale_order_line_id,
            # ĐVT khai hao hụt = Claim UoM của sản phẩm (spec K dòng 1107);
            # sản phẩm chưa cấu hình thì lùi về ĐVT đơn gốc.
            'request_uom_id': (line.product_id.compensation_claim_uom_id.id
                               or line.product_uom_id.id),
            'request_qty': request_qty,
            'opening_datetime': opening_dt,
            'production_date': production_date,
            'issue_type_id': issue_type.id,
            'note': (post.get('note') or '').strip()[:5000],
            'state': 'draft',
        }
        return vals, action
