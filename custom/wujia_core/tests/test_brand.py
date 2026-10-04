import base64
import io

from PIL import Image

from odoo.exceptions import ValidationError
from odoo.tests import HttpCase, TransactionCase, tagged

from ..tools.brand_palette import (
    DEFAULT_PALETTE, brand_palette, contrast_with_white, derive_palette, palette_css,
)


def _png(color, size=(200, 200)):
    buf = io.BytesIO()
    Image.new('RGB', size, color).save(buf, 'PNG')
    return base64.b64encode(buf.getvalue())


@tagged('post_install', '-at_install', 'wujia_brand')
class TestBrandPalette(TransactionCase):

    def test_default_color_keeps_ba_tokens(self):
        # Màu mặc định ⇒ đúng bộ token đã chốt + không sinh CSS ghi đè (0 pixel đổi).
        self.assertEqual(brand_palette('#28a9df'), DEFAULT_PALETTE)
        self.assertEqual(palette_css('#28A9DF'), '')
        self.assertEqual(palette_css(None), '')

    def test_derivation_calibrated_on_default(self):
        derived = derive_palette('#28A9DF')
        for key, expected in DEFAULT_PALETTE.items():
            if key == 'primary-rgb':
                continue
            for a, b in zip(bytes.fromhex(expected[1:]), bytes.fromhex(derived[key][1:])):
                self.assertLessEqual(abs(a - b), 8, key)

    def test_cta_always_passes_aa(self):
        for color in ('#E4572E', '#2E7D32', '#FFD400', '#00E5FF', '#FFFFFF', '#9C27B0'):
            self.assertGreaterEqual(contrast_with_white(brand_palette(color)['cta']), 4.5, color)

    def test_custom_color_css(self):
        css = palette_css('#e4572e')
        self.assertTrue(css.startswith(':root{--wujia-primary:#E4572E;'))
        self.assertIn('--wujia-primary-rgb:228 87 46', css)


@tagged('post_install', '-at_install', 'wujia_brand')
class TestBrandCompany(TransactionCase):

    def setUp(self):
        super().setUp()
        self.company = self.env.company

    def test_invalid_hex_rejected(self):
        with self.assertRaises(ValidationError):
            self.company.wj_primary_color = 'blue'

    def test_hex_normalized_and_cache_cleared(self):
        info = self.company._wj_brand_info()
        self.assertEqual(info['css'], '' if info['primary'] == '#28A9DF' else info['css'])
        self.company.write({'wj_primary_color': '#e4572e', 'wj_brand_name': 'Acme Tea'})
        self.assertEqual(self.company.wj_primary_color, '#E4572E')
        info = self.company._wj_brand_info()
        self.assertEqual(info['name'], 'Acme Tea')
        self.assertEqual(info['primary'], '#E4572E')
        self.assertIn('--wujia-primary:#E4572E', info['css'])

    def test_brand_name_falls_back_to_company(self):
        self.company.wj_brand_name = False
        self.assertEqual(self.company._wj_brand_info()['name'], self.company.name)

    def test_settings_write_company(self):
        settings = self.env['res.config.settings'].create({
            'wj_brand_name': 'Acme Tea', 'wj_primary_color': '#2E7D32',
        })
        settings.execute()
        self.assertEqual(self.company.wj_brand_name, 'Acme Tea')
        self.assertEqual(self.company.wj_primary_color, '#2E7D32')


@tagged('post_install', '-at_install', 'wujia_brand')
class TestBrandRoute(HttpCase):

    def setUp(self):
        super().setUp()
        self.company = self.env.company
        self.company.write({'logo': _png('red'), 'wj_logo_mobile': False, 'wj_favicon': _png('blue')})

    def test_public_images(self):
        cid = self.company.id
        self.assertEqual(self.url_open('/wj/brand/%s/logo' % cid).status_code, 200)
        # Không có logo mobile ⇒ dùng logo công ty.
        self.assertEqual(self.url_open('/wj/brand/%s/logo_mobile' % cid).status_code, 200)
        res = self.url_open('/wj/brand/%s/favicon?width=32&v=1' % cid)
        self.assertEqual(res.status_code, 200)
        self.assertIn('immutable', res.headers.get('Cache-Control', ''))
        self.assertEqual(Image.open(io.BytesIO(res.content)).size[0], 32)

    def test_rejects_unknown_kind_width_and_empty(self):
        cid = self.company.id
        self.assertEqual(self.url_open('/wj/brand/%s/secret' % cid).status_code, 404)
        self.assertEqual(self.url_open('/wj/brand/%s/logo?width=777' % cid).status_code, 404)
        # Nền đăng nhập không có dự phòng ⇒ trống là 404 (trang tự dùng ảnh mặc định).
        self.assertEqual(self.url_open('/wj/brand/%s/login_background' % cid).status_code, 404)
        self.assertEqual(self.url_open('/wj/brand/999999/logo').status_code, 404)
