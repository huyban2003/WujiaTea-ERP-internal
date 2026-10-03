{
    'name': 'Wujia Returns',
    'version': '19.0.1.0.0',
    'category': 'Wujia',
    'summary': 'Đổi trả / bù hàng — yêu cầu 1 sản phẩm/phiếu, duyệt HQ, SO bù 0đ, theo dõi giao bù.',
    'description': """
Nghiệp vụ đổi trả / bù hàng. Tách từ wujia_portal_return (F13, ADR-027).

- wujia.return.request (mã RTN/), wujia.return.issue.type, wujia.compensation.allocation (mã CA/).
- Wizard xử lý bù hàng: gom yêu cầu đã duyệt thành SO 0đ theo cửa hàng (FIFO).
- Kế thừa sale.order (huỷ SO bù đóng quyền lợi), stock.picking (giao thực tế → số đã bù),
  product.product (cấu hình chính sách bù).
- _portal_* / create_from_portal: luật dùng chung cho mọi kênh.
""",
    'author': 'WujiaTea',
    'license': 'LGPL-3',
    'depends': ['mail', 'wujia_sale', 'wujia_franchise'],
    'data': [
        'security/wujia_return_groups.xml',
        'security/ir.model.access.csv',
        'security/wujia_return_rules.xml',
        'data/ir_sequence_data.xml',
        'data/return_issue_type_data.xml',
        'views/backend_return_request_views.xml',
        'wizards/compensation_process_wizard_views.xml',
        'views/backend_return_issue_type_views.xml',
        'views/backend_product_views.xml',
        'views/backend_menu.xml',
    ],
    'pre_init_hook': 'pre_init_hook',
    'installable': True,
    'application': False,
    'auto_install': False,
}
