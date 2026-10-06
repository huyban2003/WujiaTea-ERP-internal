{
    'name': 'Wujia Order Window',
    'version': '19.0.1.1.0',
    'category': 'Wujia',
    'summary': 'Ordering windows by area (BA Section B.5 + Model Field Section I)',
    'description': """
Time windows in which portal orders may be created, configured per area. Split from wujia_portal_order_window (F7, ADR-027).

- Model wujia.order.window: windows per res.area; an area may have several windows (morning + evening).
- res.config.settings: 3 fallback parameters wujia_portal.* when an area has no own configuration.
- _is_within_order_window(area_id): area first, then global fallback, handles crossing midnight in the user's tz.
- _next_order_window(area_id): the next window to open (time + date) for the "outside ordering hours" screen.
- sale.order.create blocks portal orders outside the window, raises OrderWindowClosed.
""",
    'author': 'WujiaTea',
    'license': 'LGPL-3',
    'depends': ['wujia_sale'],
    'data': [
        'security/ir.model.access.csv',
        'views/wujia_order_window_views.xml',
        'views/res_config_settings_views.xml',
    ],
    'pre_init_hook': 'pre_init_hook',
    'installable': True,
    'application': False,
    'auto_install': False,
}
