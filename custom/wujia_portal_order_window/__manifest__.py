{
    'name': 'Wujia Portal Order Window (vỏ chờ gỡ)',
    'version': '19.0.3.0.0',
    'category': 'Wujia',
    'summary': 'Vỏ rỗng — nghiệp vụ đã chuyển sang wujia_order_window (F7, ADR-027)',
    'description': """
Toàn bộ model/view/menu/quyền đã chuyển sang wujia_order_window (pre_init_hook đổi chủ bản ghi).
Module này không còn nội dung; giữ lại để DB đang cài nâng cấp được, sau đó Uninstall trên Apps.
""",
    'author': 'WujiaTea',
    'license': 'LGPL-3',
    'depends': ['wujia_order_window'],
    'data': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}
