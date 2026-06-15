"""Shared utilities cho portal controllers.

Reuse-first: mọi module portal_* khác import từ đây thay vì viết lại.
Tối ưu cho 1500 user — ormcache + atomic SQL + streaming attachment.
"""
import base64
import functools
import logging
import time
from datetime import date, datetime

from werkzeug.exceptions import Forbidden, TooManyRequests
from werkzeug.utils import secure_filename

from odoo import _
from odoo.exceptions import UserError, ValidationError
from odoo.http import request
from odoo.tools import ormcache

_logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Rate limit decorator
# ---------------------------------------------------------------------------
#
# Sliding window counter dùng ormcache. Key (ip, endpoint, bucket_seconds // window).
# Khi window expire, bucket key đổi → counter reset tự nhiên.
#
# KHÔNG dùng cache TTL chuẩn — ormcache không có TTL native, dùng bucketing
# theo unix time là hành vi đúng + có cleanup ngầm khi cache evict.
# ---------------------------------------------------------------------------

class _RateLimiter:
    """Lớp wrapper để ormcache có thể decorate method.

    ormcache yêu cầu method trên model — workaround: dùng dict in-memory với
    eviction theo timestamp. Quy mô 1500 user × few endpoints = OK.
    """
    _store = {}  # {(ip, endpoint, bucket): count}
    _last_gc = 0

    @classmethod
    def hit(cls, ip, endpoint, window_sec):
        now = int(time.time())
        bucket = now // window_sec
        key = (ip, endpoint, bucket)
        cls._store[key] = cls._store.get(key, 0) + 1
        # GC mỗi 5 phút — xóa bucket cũ
        if now - cls._last_gc > 300:
            cutoff = bucket - 2
            cls._store = {
                k: v for k, v in cls._store.items() if k[2] >= cutoff
            }
            cls._last_gc = now
        return cls._store[key]


def rate_limit(max_calls, window_sec, key_fn=None):
    """Decorator giới hạn số call / window.

    Args:
        max_calls: số call tối đa cho phép trong window
        window_sec: độ dài window (giây)
        key_fn: callable(request) -> str, default = remote_addr + endpoint

    Raises:
        TooManyRequests (HTTP 429) khi vượt limit.
    """
    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(self, *args, **kwargs):
            ip = (
                request.httprequest.headers.get('X-Forwarded-For', '').split(',')[0].strip()
                or request.httprequest.remote_addr
                or 'unknown'
            )
            endpoint = key_fn(request) if key_fn else fn.__qualname__
            count = _RateLimiter.hit(ip, endpoint, window_sec)
            if count > max_calls:
                _logger.warning(
                    'Rate limit hit: ip=%s endpoint=%s count=%d max=%d',
                    ip, endpoint, count, max_calls,
                )
                raise TooManyRequests(
                    description=_('Quá nhiều yêu cầu. Vui lòng thử lại sau.')
                )
            return fn(self, *args, **kwargs)
        return wrapper
    return decorator


# ---------------------------------------------------------------------------
# File upload helper — shared cho return / support / info_request
# ---------------------------------------------------------------------------

DEFAULT_IMAGE_MIME = ('image/png', 'image/jpeg', 'image/jpg', 'image/webp')
DEFAULT_DOC_MIME = (
    'image/png', 'image/jpeg', 'image/jpg', 'image/webp', 'application/pdf',
)


def attach_files_to_record(
    record, files, allowed_mime=DEFAULT_IMAGE_MIME,
    max_size_mb=5, max_count=10,
):
    """Tạo ir.attachment cho từng file, link tới record.

    Validate count, size, MIME backend (đừng trust client header thuần).
    Sanitize filename qua secure_filename — chống path traversal.

    Args:
        record: recordset đơn (ensure_one).
        files: list FileStorage từ request.httprequest.files.getlist(...).
        allowed_mime: tuple MIME được phép.
        max_size_mb: int, mỗi file tối đa.
        max_count: int, số file tối đa.

    Returns:
        ir.attachment recordset đã tạo.

    Raises:
        ValidationError nếu validation fail.
    """
    record.ensure_one()
    files = [f for f in (files or []) if f and f.filename]
    if not files:
        return request.env['ir.attachment'].browse()
    if len(files) > max_count:
        raise ValidationError(
            _('Tối đa %s file. Bạn gửi %s file.') % (max_count, len(files))
        )
    max_bytes = max_size_mb * 1024 * 1024
    Attachment = request.env['ir.attachment'].sudo()
    created = Attachment
    for f in files:
        data = f.read()
        if len(data) > max_bytes:
            raise ValidationError(
                _('File "%s" vượt quá %sMB.') % (f.filename, max_size_mb)
            )
        if f.mimetype not in allowed_mime:
            raise ValidationError(
                _('File "%s" có định dạng không hỗ trợ (%s).') % (
                    f.filename, f.mimetype,
                )
            )
        att = Attachment.create({
            'name': secure_filename(f.filename) or 'upload',
            'res_model': record._name,
            'res_id': record.id,
            'datas': base64.b64encode(data),
            'mimetype': f.mimetype,
        })
        created |= att
    return created


# ---------------------------------------------------------------------------
# Pagination helper
# ---------------------------------------------------------------------------

def paginate(model, domain, page=1, page_size=20, order='id desc',
             max_page=500):
    """Trả về (records, pager_dict). Tránh OFFSET deep — cap max_page.

    Performance: với page > max_page, raise hoặc return empty thay vì
    OFFSET 10000+ (PostgreSQL phải scan trước).

    Returns:
        (records, pager) where pager = {
            'page': int, 'page_count': int, 'page_total': int,
            'page_previous': int, 'page_next': int,
            'offset': int, 'limit': int,
        }
    """
    try:
        page = max(1, int(page))
    except (TypeError, ValueError):
        page = 1
    page = min(page, max_page)
    try:
        page_size = max(1, min(int(page_size), 100))
    except (TypeError, ValueError):
        page_size = 20

    Model = model if hasattr(model, 'search_count') else request.env[model]
    total = Model.search_count(domain)
    last_page = max(1, (total + page_size - 1) // page_size)
    page = min(page, last_page)
    offset = (page - 1) * page_size
    records = Model.search(domain, limit=page_size, offset=offset, order=order)

    return records, {
        'page': page,
        'page_count': last_page,
        'page_total': total,
        'page_previous': max(1, page - 1),
        'page_next': min(last_page, page + 1),
        'offset': offset,
        'limit': page_size,
    }


# ---------------------------------------------------------------------------
# Form re-render helper (PRG anti-pattern fallback)
# ---------------------------------------------------------------------------

def render_form_with_error(template, error, values, extra=None):
    """Re-render form khi validation fail, giữ values user đã nhập.

    Không dùng PRG vì cần giữ context error + values. PRG chỉ dùng cho
    success path (chống F5 double-submit).
    """
    ctx = dict(values or {})
    ctx['error'] = error
    ctx['values'] = values  # cho template dùng `values.get('field')`
    if extra:
        ctx.update(extra)
    return request.render(template, ctx)


# ---------------------------------------------------------------------------
# ACL check — accessible attachment for portal user
# ---------------------------------------------------------------------------

def check_attachment_access(att_id, allowed_models=None):
    """Validate user có quyền xem attachment qua franchise membership.

    Returns:
        ir.attachment sudo recordset (browsed) nếu OK.

    Raises:
        Forbidden nếu không có quyền.
    """
    Attachment = request.env['ir.attachment'].sudo()
    att = Attachment.browse(int(att_id)).exists()
    if not att:
        raise Forbidden()
    if allowed_models and att.res_model not in allowed_models:
        raise Forbidden()
    # Kiểm tra record gốc có thuộc franchise user có quyền không
    if not att.res_model or not att.res_id:
        raise Forbidden()
    Model = request.env.get(att.res_model)
    if Model is None:
        raise Forbidden()
    record = Model.sudo().browse(att.res_id).exists()
    if not record:
        raise Forbidden()
    accessible = set(request.env.user._get_accessible_franchise_ids())
    franchise_id = (
        getattr(record, 'franchise_id', False)
        and record.franchise_id.id
    )
    if franchise_id and franchise_id not in accessible:
        raise Forbidden()
    return att


# ---------------------------------------------------------------------------
# Role check shortcut
# ---------------------------------------------------------------------------

ROLE_RANK = {'staff': 1, 'manager': 2, 'owner': 3}


# ---------------------------------------------------------------------------
# Mobile dashboard sections — Sprint 16 (Figma mobile_dashboard 2474:2)
# ---------------------------------------------------------------------------
#
# Section "Đơn hàng gần đây" / "Giao hàng sắp tới" lặp trên 2-3 trang mobile
# (/portal/delivery, /portal/debt, /portal/support) → helper chung ở đây
# (cả 3 module đều depends wujia_portal_base). Field franchise_id (wujia_sale)
# và planned_departure (wujia_delivery) KHÔNG thuộc dependency của base →
# guard theo _fields, thiếu module thì trả rỗng thay vì crash.
#
# Label map MOBILE — UI-only, TÁCH map desktop (precedent MOBILE_STATE_BADGES
# Sprint 13). Nhãn theo Figma; nguồn state thật, chỉ nhãn là mobile-riêng.
# ---------------------------------------------------------------------------

MOBILE_ORDER_BADGES = {
    'draft':  ('Nháp', 'wujia-badge-muted'),
    'sent':   ('Đã gửi', 'wujia-badge-info'),
    'sale':   ('Đã xác nhận', 'wujia-badge-success'),
    'done':   ('Hoàn tất', 'wujia-badge-success'),
    'cancel': ('Đã hủy', 'wujia-badge-danger'),
}

# Figma 2474:187/197: "Đang giao"=info cyan / "Chuẩn bị giao"=muted.
MOBILE_BATCH_BADGES = {
    'draft':      ('Chuẩn bị giao', 'wujia-badge-muted'),
    'assigned':   ('Chuẩn bị giao', 'wujia-badge-muted'),
    'loading':    ('Chuẩn bị giao', 'wujia-badge-muted'),
    'delivering': ('Đang giao', 'wujia-badge-info'),
    'done':       ('Đã giao xong', 'wujia-badge-success'),
    'cancelled':  ('Hủy chuyến', 'wujia-badge-danger'),
}

# Sprint 17 — nhãn MOBILE cho "Yêu cầu đổi trả gần đây" (Figma 2474:206/213:
# "Chờ xử lý"=danger / "Đang xử lý"=warning). Chuyển từ wujia_portal_delivery
# về đây để Home (section gộp Sprint 16) + delivery dùng chung. UI-only, TÁCH
# STATE_LABELS desktop của wujia_portal_return; nguồn state thật wujia.return.request.
MOBILE_RETURN_BADGES = {
    'draft':    ('Nháp', 'wujia-badge-muted'),
    'sent':     ('Chờ xử lý', 'wujia-badge-danger'),
    'approved': ('Đang xử lý', 'wujia-badge-warning'),
    'rejected': ('Từ chối', 'wujia-badge-danger'),
    'done':     ('Hoàn thành', 'wujia-badge-success'),
}

# Sprint 17 — nhãn MOBILE cho ticket hỗ trợ (Figma Mobile_Ticket). UI-only,
# TÁCH STATE_LABELS desktop của wujia_portal_support (precedent S13). LƯU Ý nhãn
# 'waiting_customer'="Có phản hồi" (mobile/Figma) ≠ desktop "Chờ phản hồi" —
# drift chủ đích, đối chiếu BA. Nguồn state thật wujia.support.ticket.state.
MOBILE_TICKET_BADGES = {
    'new':              ('Mới', 'wujia-badge-info'),
    'in_progress':      ('Đang xử lý', 'wujia-badge-warning'),
    'waiting_customer': ('Có phản hồi', 'wujia-badge-info'),
    'resolved':         ('Đã giải quyết', 'wujia-badge-success'),
    'closed':           ('Đã đóng', 'wujia-badge-muted'),
    'cancelled':        ('Đã huỷ', 'wujia-badge-danger'),
}

VI_WEEKDAYS = {0: 'Thứ 2', 1: 'Thứ 3', 2: 'Thứ 4', 3: 'Thứ 5',
               4: 'Thứ 6', 5: 'Thứ 7', 6: 'CN'}


def format_batch_departure(dt):
    """'29/05/2026 (Thứ 5) · 08:00' — format ngày giờ batch theo Figma 2474:183."""
    if not dt:
        return '—'
    return '%s (%s) · %s' % (
        dt.strftime('%d/%m/%Y'), VI_WEEKDAYS[dt.weekday()], dt.strftime('%H:%M'),
    )


def get_recent_orders(franchise_ids, limit=3):
    """sale.order mới nhất của franchise — section "Đơn hàng gần đây"."""
    Order = request.env['sale.order'].sudo()
    if 'franchise_id' not in Order._fields or not franchise_ids:
        return Order.browse()
    return Order.search(
        [('franchise_id', 'in', list(franchise_ids))],
        order='date_order desc', limit=limit,
    )


def get_upcoming_batches(franchise_ids, limit=2):
    """Batch sắp giao có hàng của franchise — section "Giao hàng sắp tới".

    Returns: list dict {batch, when, order_count, total, badge} đã tính sẵn
    (Tổng đơn = số sale.order của franchise trong batch; Tổng tiền = sum
    amount_total các đơn đó — tính trên limit 2 batch, perf OK 1500 user).
    """
    Batch = request.env['stock.picking.batch'].sudo()
    if 'planned_departure' not in Batch._fields or not franchise_ids:
        return []
    franchise_ids = list(franchise_ids)
    start = datetime.combine(date.today(), datetime.min.time())
    batches = Batch.search([
        ('planned_departure', '>=', start),
        '|', ('picking_ids.franchise_id', 'in', franchise_ids),
             ('picking_ids.sale_id.franchise_id', 'in', franchise_ids),
    ], order='planned_departure asc', limit=limit)
    items = []
    for batch in batches:
        own = batch.picking_ids.filtered(
            lambda p: (p.franchise_id and p.franchise_id.id in franchise_ids)
            or (p.sale_id and p.sale_id.franchise_id
                and p.sale_id.franchise_id.id in franchise_ids)
        )
        orders = own.mapped('sale_id')
        items.append({
            'batch': batch,
            'when': format_batch_departure(batch.planned_departure),
            'order_count': len(orders),
            'total': sum(orders.mapped('amount_total')),
            'badge': MOBILE_BATCH_BADGES.get(
                batch.delivery_batch_status, ('Chuẩn bị giao', 'wujia-badge-muted'),
            ),
        })
    return items


def require_role(min_role, franchise_id=None):
    """Raise Forbidden nếu user không đạt role tối thiểu.

    Dùng trong controller POST cho action chỉ Owner/Manager được làm.
    """
    from odoo.addons.wujia_portal_base.controllers.portal import (
        get_max_role_in_franchises,
    )
    role = get_max_role_in_franchises(
        [franchise_id] if franchise_id else None
    )
    if not role:
        raise Forbidden(description=_('Không có quyền truy cập franchise.'))
    if ROLE_RANK.get(role, 0) < ROLE_RANK.get(min_role, 99):
        raise Forbidden(
            description=_('Yêu cầu role tối thiểu: %s') % min_role
        )
