{
    'name': 'Wujia Portal — Info Update Request',
    'version': '19.0.2.0.0',
    'category': 'Wujia',
    'summary': 'Màn portal gửi yêu cầu cập nhật thông tin cửa hàng '
               '(nghiệp vụ ở wujia_info_request).',
    'author': 'WujiaTea',
    'license': 'LGPL-3',
    'depends': ['wujia_portal_base', 'wujia_info_request'],
    'data': [
        'views/portal_info_request_list.xml',
        'views/portal_info_request_form.xml',
        'views/portal_info_request_detail.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
