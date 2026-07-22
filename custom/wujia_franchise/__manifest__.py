{
    'name': 'Wujia Franchise',
    'version': '19.0.2.0.1',
    'category': 'Wujia',
    'summary': 'Quản lý cửa hàng nhượng quyền + membership user portal',
    'author': 'WujiaTea',
    'description': """
Module hợp nhất 2 phân hệ chính của nhượng quyền (BA spec mục A):

1. wujia.franchise.management — hồ sơ cửa hàng nhượng quyền:
   - Mã cửa hàng (unique), tên, partner liên kết, opening_date.
   - Hợp đồng: franchise_start/end_date, remaining_days, is_expired.
   - Khu vực (res.area), tỉnh/thành, địa chỉ, liên hệ.
   - Cờ điều khiển: portal_locked, invoiced, status (5 trạng thái).
   - main_owner_member_id (compute từ role='owner').

2. wujia.franchise.member — thành viên user portal × cửa hàng × role:
   - 1 user có thể thuộc nhiều cửa hàng (multi-membership).
   - 1 cửa hàng có nhiều user, mỗi user 1 role.
   - is_currently_valid (compute từ active + date range).
   - UI ĐỘC LẬP (form/list/search) — không nhúng vào res.users gốc.

Extension chuẩn:
   - res.partner.is_franchise (compute từ franchise_ids != False), franchise_ids.
   - res.users.member_ids + smart-button.

Hợp nhất 2 model trong cùng 1 module để tránh circular dep
(mgmt.member_ids ↔ member.franchise_id).
""",
    'license': 'LGPL-3',
    'depends': [
        'wujia_core',
        'contacts',
        'portal',
        'mail',
    ],
    'data': [
        'security/wujia_franchise_groups.xml',
        'security/ir.model.access.csv',
        'security/wujia_franchise_rules.xml',
        'views/wujia_franchise_management_views.xml',
        'views/wujia_franchise_member_views.xml',
        'views/res_partner_views.xml',
        'views/res_users_views.xml',
        'views/wujia_franchise_menu.xml',
        'data/ir_cron_data.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
