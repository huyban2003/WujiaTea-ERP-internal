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

    portal_order_time_from = fields.Float(
        string='Portal Order Time From',
        config_parameter=CONFIG_KEY_FROM,
        default=DEFAULT_FROM,
        help='Giờ bắt đầu cho phép portal đặt hàng (float, 0.0–24.0).',
    )
    portal_order_time_to = fields.Float(
        string='Portal Order Time To',
        config_parameter=CONFIG_KEY_TO,
        default=DEFAULT_TO,
        help='Giờ kết thúc cho phép portal đặt hàng (float, 0.0–24.0). '
             'Nếu To < From thì khung giờ chạy qua nửa đêm.',
    )
    portal_order_time_limit_enabled = fields.Boolean(
        string='Enable Portal Order Time Limit',
        config_parameter=CONFIG_KEY_ENABLED,
        default=DEFAULT_ENABLED,
        help='Bật/tắt giới hạn khung giờ đặt hàng cho portal.',
    )

    # -------------------- helpers (class methods on env) --------------------
    @api.model
    def _get_portal_order_window(self):
        """Read 3 config params + cast. Default if missing."""
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
    def _is_within_order_window(self):
        """Return (allowed: bool, window: dict). Always allow if disabled."""
        window = self._get_portal_order_window()
        if not window['enabled']:
            return True, window
        now = self._user_now_hours()
        f, t = window['from'], window['to']
        if f <= t:
            allowed = (now >= f) and (now <= t)
        else:
            allowed = (now >= f) or (now <= t)
        return allowed, window
