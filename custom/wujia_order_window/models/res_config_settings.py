from datetime import datetime, timedelta

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
        help='Default start hour (float 0.0–24.0) used when the area has no window of its own.',
    )
    portal_order_time_to = fields.Float(
        string='Portal Order Time To (fallback)',
        config_parameter=CONFIG_KEY_TO,
        default=DEFAULT_TO,
        help='Default end hour (float 0.0–24.0). If To < From the window runs past midnight.',
    )
    portal_order_time_limit_enabled = fields.Boolean(
        string='Enable Portal Order Time Limit',
        config_parameter=CONFIG_KEY_ENABLED,
        default=DEFAULT_ENABLED,
        help="Enable/disable the portal ordering time window. When off, ordering is allowed at any time regardless of `wujia.order.window`.",
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
            # False = chưa có ai lưu config → controller hiện ORDER_TIME_NOT_CONFIGURED (BA row 2).
            'configured': ICP.get_param(CONFIG_KEY_FROM) not in (False, None, ''),
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
            (allowed: bool, window: dict) — window LUÔN có các key:
            'from', 'to', 'enabled', 'configured', 'source' ∈ {'global',
            'area:<id>'}, 'windows' (list dict {name, from, to} — đủ khung giờ
            áp dụng); nhánh area có thêm 'window_count', 'window_name'.
        """
        global_cfg = self._get_portal_order_window()
        if not global_cfg['enabled']:
            return True, dict(global_cfg, source='global', windows=[])

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
                    'configured': True,
                    'source': 'area:%s' % area_id,
                    'window_count': len(windows),
                    'window_name': first.name,
                    # Đủ danh sách khung giờ cho banner (BA row 2 — area có thể nhiều khung).
                    'windows': [
                        {'name': w.name, 'from': w.order_time_from, 'to': w.order_time_to}
                        for w in windows
                    ],
                }

        # 3. Fallback global
        f, t = global_cfg['from'], global_cfg['to']
        if f <= t:
            allowed = (now >= f) and (now <= t)
        else:
            allowed = (now >= f) or (now <= t)
        return allowed, dict(
            global_cfg, source='global',
            windows=[{'name': '', 'from': f, 'to': t}],
        )

    @api.model
    def _user_now_dt(self):
        """Current datetime in user's timezone (naive, tz-local wall clock)."""
        tz = self.env.user.tz or 'UTC'
        try:
            tz_obj = pytz.timezone(tz)
        except pytz.UnknownTimeZoneError:
            tz_obj = pytz.UTC
        return datetime.now(tz_obj).replace(tzinfo=None)

    @api.model
    def _next_order_window(self, area_id=None):
        """Khung giờ đặt hàng SẮP TỚI (read-only, không đổi rule hiện có).

        Dùng cho màn "ngoài khung giờ" trên portal: cần nói rõ mở lại lúc nào
        và NGÀY nào. Lấy danh sách khung áp dụng từ `_is_within_order_window`
        (đã xử lý ưu tiên area → global fallback) rồi chọn lần mở gần nhất:
        `now < from` → mở hôm nay, ngược lại → mở ngày mai.

        Return:
            dict {'from': float, 'to': float, 'name': str, 'date': date,
            'is_today': bool} — hoặc None khi tắt giới hạn khung giờ / không
            có khung nào áp dụng.
        """
        _allowed, window = self._is_within_order_window(area_id=area_id)
        if not window.get('enabled'):
            return None
        windows = window.get('windows') or []
        if not windows:
            return None

        now = self._user_now_hours()
        today = self._user_now_dt().date()
        # (day_offset, from) nhỏ nhất = lần mở gần nhất kể từ bây giờ.
        best = min(
            windows,
            key=lambda w: (0 if now < (w['from'] or 0.0) else 1, w['from'] or 0.0),
        )
        day_offset = 0 if now < (best['from'] or 0.0) else 1
        return {
            'from': best['from'] or 0.0,
            'to': best['to'] or 0.0,
            'name': best.get('name') or '',
            'date': today + timedelta(days=day_offset),
            'is_today': day_offset == 0,
        }
