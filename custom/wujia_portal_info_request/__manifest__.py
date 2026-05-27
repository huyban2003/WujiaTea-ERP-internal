{
    'name': 'Wujia Portal — Info Update Request',
    'version': '19.0.1.2.0',
    'category': 'Wujia',
    'summary': 'Cửa hàng nhượng quyền gửi yêu cầu cập nhật thông tin '
               '(địa chỉ, SĐT, người đại diện...) — HQ duyệt qua chatter.',
    'author': 'WujiaTea',
    'license': 'LGPL-3',
    'depends': ['wujia_portal_base', 'wujia_franchise', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'security/wujia_info_request_rules.xml',
        'data/ir_sequence_data.xml',
        'views/portal_info_request_list.xml',
        'views/portal_info_request_form.xml',
        'views/portal_info_request_detail.xml',
        'views/info_request_backend.xml',
        'views/sidenav_inherit.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
