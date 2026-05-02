import base64
import io
import logging

from odoo import _, api, fields, models

_logger = logging.getLogger(__name__)

try:
    import qrcode
except ImportError:
    qrcode = None
    _logger.info("qrcode python package not installed — wujia.fleet.management.qr_code sẽ trả về False.")


VEHICLE_STATUS = [
    ('available', 'Sẵn sàng'),
    ('in_yard', 'Vào bãi'),
    ('assigned', 'Đã sắp chuyến'),
    ('delivering', 'Đang giao'),
    ('maintenance', 'Bảo trì'),
    ('inactive', 'Ngưng dùng'),
]


class WujiaFleetManagement(models.Model):
    _name = 'wujia.fleet.management'
    _description = 'Wujia Fleet Vehicle — Xe'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'provider_id, name'

    name = fields.Char(
        string='Tên xe',
        required=True,
        tracking=True,
        help='Tên hiển thị, ví dụ "51C-12345 — Tải 3.5T".',
    )
    code = fields.Char(string='Mã xe', index=True)
    provider_id = fields.Many2one(
        'wujia.fleet.provider',
        string='Đội xe',
        required=True,
        ondelete='restrict',
        tracking=True,
        index=True,
        domain=[('active', '=', True)],
    )
    fleet_type_id = fields.Many2one(
        'wujia.fleet.type',
        string='Loại xe',
        required=True,
        ondelete='restrict',
        tracking=True,
        index=True,
    )
    vehicle_category = fields.Selection(
        related='fleet_type_id.vehicle_category',
        store=True,
        readonly=True,
    )
    payload_capacity_ton = fields.Float(
        related='fleet_type_id.payload_capacity_ton',
        store=True,
        readonly=True,
        digits=(10, 2),
    )
    max_payload_kg = fields.Float(
        related='fleet_type_id.max_payload_kg',
        store=True,
        readonly=True,
        digits='Stock Weight',
    )

    license_plate = fields.Char(string='Biển số', tracking=True, index=True)
    driver_name = fields.Char(string='Tài xế')
    driver_phone = fields.Char(string='SĐT tài xế')
    contact = fields.Char(
        string='Thông tin liên hệ',
        help='Thông tin liên hệ nhanh (số xe / tài xế).',
    )

    vehicle_status = fields.Selection(
        VEHICLE_STATUS,
        string='Trạng thái xe',
        required=True,
        default='available',
        tracking=True,
        index=True,
    )

    franchise_ids = fields.Many2many(
        'wujia.franchise.management',
        'wujia_fleet_franchise_rel',
        'fleet_id',
        'franchise_id',
        string='Cửa hàng thường giao',
        help='Danh sách cửa hàng thường được giao bởi xe này — gợi ý điều phối.',
    )

    qr_code = fields.Binary(
        string='QR Code',
        compute='_compute_qr_code',
        help='QR code chứa code xe — dùng cho check-in tại bãi.',
    )

    description = fields.Text(string='Mô tả')
    last_update_datetime = fields.Datetime(
        string='Cập nhật trạng thái lần cuối',
        readonly=True,
    )
    active = fields.Boolean(default=True)
    note = fields.Text(string='Ghi chú nội bộ')

    _code_uniq = models.Constraint(
        'UNIQUE (code)',
        'Mã xe phải duy nhất.',
    )

    @api.depends('code')
    def _compute_qr_code(self):
        for rec in self:
            if not qrcode or not rec.code:
                rec.qr_code = False
                continue
            try:
                img = qrcode.make(rec.code)
                buf = io.BytesIO()
                img.save(buf, format='PNG')
                rec.qr_code = base64.b64encode(buf.getvalue())
            except Exception as exc:
                _logger.warning("QR code generation failed for vehicle %s: %s", rec.code, exc)
                rec.qr_code = False

    def write(self, vals):
        if 'vehicle_status' in vals:
            vals.setdefault('last_update_datetime', fields.Datetime.now())
        return super().write(vals)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals.setdefault('last_update_datetime', fields.Datetime.now())
        return super().create(vals_list)

