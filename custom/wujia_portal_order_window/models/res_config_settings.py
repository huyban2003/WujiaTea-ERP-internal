from datetime import datetime

import pytz

from odoo import api, fields, models


CONFIG_KEY_FROM = 'wujia_portal.portal_order_time_from'
CONFIG_KEY_TO = 'wujia_portal.portal_order_time_to'
CONFIG_KEY_ENABLED = 'wujia_portal.portal_order_time_limit_enabled'

DEFAULT_FROM = 10.0
DEFAULT_TO = 4.0
DEFAULT_ENABLED = True


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    # Global fallback (áp dụng khi khu vực chưa cấu hình `wujia.order.window`).
    portal_order_time_from = fields.Float(
        string='Portal Order Time From (fallback)',
        config_parameter=CONFIG_KEY_FROM,
        default=DEFAULT_FROM,
        help='Giờ bắt đầu mặc định (float 0.0–24.0) khi khu vực chưa có khung giờ riêng.',
    )
    portal_order_time_to = fields.Float(
        string='Portal Order Time To (fallback)',
        config_parameter=CONFIG_KEY_TO,
        default=DEFAULT_TO,
        help='Giờ kết thúc mặc định (float 0.0–24.0). Nếu To < From thì khung giờ chạy qua nửa đêm.',
    )
    portal_order_time_limit_enabled = fields.Boolean(
        string='Enable Portal Order Time Limit',
        config_parameter=CONFIG_KEY_ENABLED,
        default=DEFAULT_ENABLED,
        help='Bật/tắt giới hạn khung giờ đặt hàng cho portal. '
             'Nếu tắt thì cho phép đặt mọi lúc, bất kể `wujia.order.window`.',
    )

    # -------------------- helpers (class methods on env) --------------------
    @api.model
    def _get_portal_order_window(self):
        """Read 3 global config params (fallback). Default if missing."""
        ICP = self.env['ir.config_parameter'].sudo()

        def _to_float(key, default):
            raw = ICP.get_param(key)
            if raw in (False, None, ''):
                return default
            try:
                return float(raw)
            except (TypeError, ValueError):
                return default

        return {
            'from': _to_float(CONFIG_KEY_FROM, DEFAULT_FROM),
            'to': _to_float(CONFIG_KEY_TO, DEFAULT_TO),
            'enabled': ICP.get_param(CONFIG_KEY_ENABLED, 'True') in ('True', 'true', '1', True),
        }

    @api.model
    def _user_now_hours(self):
        """Current time in user's timezone, expressed as float hours."""
        tz = self.env.user.tz or 'UTC'
        try:
            tz_obj = pytz.timezone(tz)
        except pytz.UnknownTimeZoneError:
            tz_obj = pytz.UTC
        now = datetime.now(tz_obj)
        return now.hour + now.minute / 60.0 + now.second / 3600.0

    @api.model
    def _is_within_order_window(self, area_id=None):
        """Kiểm tra giờ hiện tại có nằm trong khung giờ đặt hàng không.

        Thứ tự ưu tiên:
            1. Nếu global enabled=False → always allowed.
            2. Nếu `area_id` truyền vào và khu vực có ít nhất 1 `wujia.order.window`
               active → cho phép khi BẤT KỲ window nào đang mở.
            3. Fallback: dùng global from/to trong `ir.config_parameter`.

        Return:
            (allowed: bool, window: dict) — window mang field 'from', 'to',
            'enabled', và 'source' ∈ {'global', 'area:<id>'} để controller
            biết đang lấy từ đâu mà render UI.
        """
        global_cfg = self._get_portal_order_window()
        if not global_cfg['enabled']:
            return True, dict(global_cfg, source='global')

        now = self._user_now_hours()

        # 2. Per-area windows
        if area_id:
            Window = self.env['wujia.order.window'].sudo()
            windows = Window.search([
                ('area_id', '=', area_id),
                ('active', '=', True),
            ])
            if windows:
                allowed = any(w.is_now_open(now) for w in windows)
                # Hiển thị window gần nhất (sequence nhỏ nhất) cho UI banner.
                first = windows[0]
                return allowed, {
                    'from': first.order_time_from,
                    'to': first.order_time_to,
                    'enabled': True,
                    'source': 'area:%s' % area_id,
                    'window_count': len(windows),
                    'window_name': first.name,
                }

        # 3. Fallback global
        f, t = global_cfg['from'], global_cfg['to']
        if f <= t:
            allowed = (now >= f) and (now <= t)
        else:
            allowed = (now >= f) or (now <= t)
        return allowed, dict(global_cfg, source='global')
