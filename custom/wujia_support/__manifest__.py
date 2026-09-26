{
    'name': 'Wujia Support Tickets',
    'version': '19.0.1.0.1',
    'category': 'Wujia',
    'summary': 'Yêu cầu hỗ trợ từ cửa hàng nhượng quyền — HQ tiếp nhận, phân công, trả lời, đóng.',
    'description': """
Nghiệp vụ yêu cầu hỗ trợ. Tách từ wujia_portal_support (F10, ADR-027).

- Model wujia.support.ticket (mã WJ-TK/, chatter, mốc ngày theo trạng thái, phân tích phản hồi
  cửa hàng/HQ), wujia.support.category (danh mục + người/đội nhận mặc định).
- _portal_scope_domain / create_from_portal / _portal_reply / _portal_get_attachment: luật dùng chung
  cho mọi kênh.
""",
    'author': 'WujiaTea',
    'license': 'LGPL-3',
    'depends': [
        'mail',
        'wujia_franchise',
        'sale',
        'stock_picking_batch',
        'sales_team',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/wujia_support_rules.xml',
        'data/ir_sequence_data.xml',
        'data/wujia_support_category_data.xml',
        'views/wujia_support_backend_views.xml',
    ],
    'pre_init_hook': 'pre_init_hook',
    'installable': True,
    'application': False,
    'auto_install': False,
}
