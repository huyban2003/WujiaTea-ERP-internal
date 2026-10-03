{
    'name': 'Wujia Info Update Request',
    'version': '19.0.1.0.0',
    'category': 'Wujia',
    'summary': 'Yêu cầu cập nhật thông tin cửa hàng nhượng quyền (địa chỉ, SĐT, người đại diện...) — HQ duyệt qua chatter.',
    'description': """
Nghiệp vụ yêu cầu cập nhật thông tin cửa hàng. Tách từ wujia_portal_info_request (F8, ADR-027).

- Model wujia.info.update.request: mã INF-, trạng thái nháp → đã gửi → đang xem → duyệt/từ chối, đính kèm, chatter.
- Quyền: portal xem yêu cầu của cửa hàng mình, chỉ sửa yêu cầu mình tạo; nội bộ xem hết.
- create_from_portal / _portal_can_request / _portal_scope_domain: luật dùng chung cho mọi kênh.
""",
    'author': 'WujiaTea',
    'license': 'LGPL-3',
    'depends': ['wujia_franchise', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'security/wujia_info_request_rules.xml',
        'data/ir_sequence_data.xml',
        'views/info_request_backend.xml',
    ],
    'pre_init_hook': 'pre_init_hook',
    'installable': True,
    'application': False,
    'auto_install': False,
}
