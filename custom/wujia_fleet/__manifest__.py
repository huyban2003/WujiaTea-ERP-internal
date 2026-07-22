{
    'name': 'Wujia Fleet',
    'version': '19.0.1.0.1',
    'category': 'Wujia',
    'summary': 'Quản lý đội xe / nhà xe / loại xe / xe / bảng giá vận chuyển',
    'author': 'WujiaTea',
    'description': """
Master data đội xe (BA spec mục B):

- wujia.fleet.provider: nhà xe / đội xe (company / outsource).
- wujia.fleet.type: loại xe (xe tải, bán tải, đông lạnh...) + payload chuẩn.
- wujia.fleet.management: xe cụ thể (license_plate, driver, status), gắn provider + type.
- wujia.fleet.pricelist: bảng giá vận chuyển theo loại xe + nhà xe + scope (city/interprovince).
- wujia.fleet.pricelist.line: dòng giá theo khu vực (res.area), drop_fee per điểm.

Module này KHÔNG đụng stock.picking / stock.picking.batch — phần điều phối nằm ở
wujia_delivery để tránh circular dep với wujia_sale.
""",
    'license': 'LGPL-3',
    'depends': [
        'wujia_core',
        'wujia_franchise',
        'mail',
    ],
    'data': [
        'security/wujia_fleet_groups.xml',
        'security/ir.model.access.csv',
        'views/wujia_fleet_provider_views.xml',
        'views/wujia_fleet_type_views.xml',
        'views/wujia_fleet_management_views.xml',
        'views/wujia_fleet_pricelist_views.xml',
        'views/wujia_fleet_menu.xml',
        'data/ir_cron_data.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
