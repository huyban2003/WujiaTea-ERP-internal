{
    'name': 'Wujia Knowledge Library',
    'version': '19.0.1.0.0',
    'category': 'Wujia',
    'summary': 'Thư viện kiến thức / SOP / đào tạo cho cửa hàng nhượng quyền — HQ soạn, publish, hẹn giờ, hết hạn.',
    'description': """
Nghiệp vụ thư viện kiến thức. Tách từ wujia_portal_knowledge (F9, ADR-027).

- Model wujia.knowledge.article (mã KNW-, slug, nháp → publish → lưu trữ, hẹn giờ, hết hạn, đính kèm, chatter),
  wujia.knowledge.category (cây danh mục), wujia.knowledge.tag.
- Cron hằng ngày hạ cờ hiển thị của bài đã hết hạn.
- _portal_visible_domain / _portal_search_domain / _portal_get_attachment: luật dùng chung cho mọi kênh.
""",
    'author': 'WujiaTea',
    'license': 'LGPL-3',
    'depends': ['wujia_franchise', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'data/ir_cron_data.xml',
        'views/wujia_knowledge_backend_views.xml',
    ],
    'pre_init_hook': 'pre_init_hook',
    'installable': True,
    'application': False,
    'auto_install': False,
}
