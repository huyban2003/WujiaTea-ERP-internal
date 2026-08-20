{
    'name': 'Wujia — Accounting franchise link',
    'version': '19.0.1.1.0',
    'category': 'Wujia',
    'summary': 'Franchise scope for invoices/payments + portal debt aggregates',
    'description': """
Wujia — Accounting franchise link
=================================
Backend seam cho công nợ portal (BA task Tasks!STT9, Doc "Controller Công nợ & Thanh
toán Portal", tab 1. Model/ Field mục N, Controller CT-050..CT-055).

Thêm 3 field custom đã chốt với BA:

- ``account.move.franchise_id`` — phạm vi cửa hàng của hoá đơn / credit note.
- ``account.payment.franchise_id`` — phạm vi cửa hàng của khoản thanh toán (stored
  compute từ hoá đơn được đối soát).
- ``res.partner.bank.portal_payment_enabled`` — bật tài khoản nhận tiền lên portal.

Kèm 2 aggregate perf trên ``wujia.franchise.management`` (badge "n quá hạn" gọi trên
mọi trang portal — store + cron daily, KHÔNG query on-the-fly).

Không tạo model mới, không sequence mới, không đổi quy tắc hạch toán chuẩn.
""",
    'author': 'WujiaTea',
    'license': 'LGPL-3',
    'depends': ['account', 'wujia_franchise', 'wujia_sale'],
    'data': [
        'data/ir_cron.xml',
        'views/account_move_views.xml',
        'views/account_payment_views.xml',
        'views/res_partner_bank_views.xml',
    ],
    'post_init_hook': 'post_init_hook',
    'installable': True,
    'application': False,
    'auto_install': False,
}
