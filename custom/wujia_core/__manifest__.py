{
    'name': 'Wujia Core',
    'version': '19.0.1.0.0',
    'category': 'Wujia',
    'summary': 'Core master data dùng chung: khu vực, phường/xã, mixin, helpers',
    'description': """
Module nền tảng cho mọi custom Wujia. Hiện chứa:
- res.area: khu vực kinh doanh / vùng giao hàng
- res.ward: phường/xã, link tới res.country.state, có thể gắn vào res.area

Các module khác (wujia_franchise, wujia_franchise_management, wujia_sale)
chỉ depend lên wujia_core để dùng master data này, không cần biết franchise.
""",
    'author': 'WujiaTea',
    'license': 'LGPL-3',
    'depends': ['base', 'mail', 'contacts'],
    'data': [
        'security/ir.model.access.csv',
        'views/res_ward_views.xml',
        'views/res_area_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
