# -*- coding: utf-8 -*-
"""Bộ token màu thương hiệu sinh từ MỘT màu chính.

Màu mặc định #28A9DF dùng nguyên bộ token BA đã chốt (_variables.css của
wujia_portal_layout) ⇒ cấu hình mặc định không lệch pixel nào. Màu khác thì
sinh theo HSL, riêng CTA làm đậm tới khi chữ trắng đạt AA 4.5:1 (WJ-ORD-012).
"""
import colorsys
import re

DEFAULT_PRIMARY = '#28A9DF'

# Thứ tự = thứ tự in ra CSS. Tên khớp biến `--wujia-<key>` trong _variables.css.
DEFAULT_PALETTE = {
    'primary': '#28A9DF',
    'primary-dark': '#168FC2',
    'primary-light': '#E0F7FF',
    'primary-soft': '#EAF7FD',
    'primary-border-soft': '#BFE8F7',
    'active-text': '#28A9DF',
    'cta': '#0F7CA8',
    'cta-dark': '#0C6688',
    'primary-rgb': '40 169 223',
}

AA_CONTRAST = 4.5
HEX_RE = re.compile(r'^#[0-9A-Fa-f]{6}$')


def normalize_hex(value):
    """'#28a9df' → '#28A9DF'; sai định dạng → None."""
    if not value or not HEX_RE.match(value.strip()):
        return None
    return value.strip().upper()


def _rgb(hex_color):
    h = hex_color.lstrip('#')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def _hex(rgb):
    return '#' + ''.join('%02X' % max(0, min(255, round(c))) for c in rgb)


def _luminance(rgb):
    def ch(c):
        c = c / 255.0
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (ch(c) for c in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast_with_white(hex_color):
    return 1.05 / (_luminance(_rgb(hex_color)) + 0.05)


def _from_hls(h, l, s):
    return _hex(c * 255 for c in colorsys.hls_to_rgb(h, max(0.0, min(1.0, l)), max(0.0, min(1.0, s))))


def _mix_white(hex_color, weight):
    """weight = tỉ lệ màu gốc (0 → trắng, 1 → màu gốc)."""
    return _hex(255 - weight * (255 - c) for c in _rgb(hex_color))


def derive_palette(primary):
    """Sinh bộ token từ màu chính bất kỳ (không dùng bảng mặc định)."""
    r, g, b = (c / 255.0 for c in _rgb(primary))
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    # Hệ số canh theo bộ BA của #28A9DF (dark l −10, light l 94 s 100, …).
    dark = _from_hls(h, l - 0.10, s + 0.07)
    cta_l = min(l, 0.50)
    cta = _from_hls(h, cta_l, s + 0.10)
    while contrast_with_white(cta) < AA_CONTRAST and cta_l > 0.05:
        cta_l -= 0.01
        cta = _from_hls(h, cta_l, s + 0.10)
    return {
        'primary': primary,
        'primary-dark': dark,
        'primary-light': _from_hls(h, 0.94, 1.0),
        'primary-soft': _mix_white(primary, 0.09),
        'primary-border-soft': _mix_white(primary, 0.28),
        'active-text': primary,
        'cta': cta,
        'cta-dark': _from_hls(h, cta_l - 0.07, s + 0.10),
        'primary-rgb': ' '.join(str(c) for c in _rgb(primary)),
    }


def brand_palette(primary):
    primary = normalize_hex(primary) or DEFAULT_PRIMARY
    if primary == DEFAULT_PRIMARY:
        return dict(DEFAULT_PALETTE)
    return derive_palette(primary)


def palette_css(primary):
    """Khối `:root{…}` ghi đè token; màu mặc định → '' (giữ nguyên _variables.css)."""
    primary = normalize_hex(primary) or DEFAULT_PRIMARY
    if primary == DEFAULT_PRIMARY:
        return ''
    body = ';'.join('--wujia-%s:%s' % kv for kv in brand_palette(primary).items())
    return ':root{%s}' % body
