{
    'name': 'Wujia Core',
    'version': '19.0.2.1.1',
    'category': 'Wujia',
    'summary': 'Core master data dùng chung: khu vực, phường/xã, mixin, helpers',
    'description': """
Module nền tảng cho mọi custom Wujia. Hiện chứa:
- res.area: khu vực kinh doanh / vùng giao hàng (Many2many ward_ids)
- res.ward: phường/xã, link tới res.country.state
- Thương hiệu (res.company + Settings): tên, màu chính, logo PC/mobile, favicon, nền đăng nhập; favicon + title tab backend theo thương hiệu

Các module khác (wujia_franchise, wujia_franchise_management, wujia_sale)
chỉ depend lên wujia_core để dùng master data này, không cần biết franchise.
""",
    'author': 'WujiaTea',
    'license': 'LGPL-3',
    'depends': ['base', 'web', 'mail', 'contacts'],
    'data': [
        'security/ir.model.access.csv',
        'views/res_ward_views.xml',
        'views/res_area_views.xml',
        'views/res_config_settings_views.xml',
        'views/webclient_templates.xml',
        'data/brand_defaults.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'wujia_core/static/src/js/brand_title.js',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
}
