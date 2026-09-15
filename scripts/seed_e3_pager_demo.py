"""Seed cho cụm E3 (Pagination — UI-PAGINATION-001).

Vì sao cần: BA ghi rõ "các màn hiện chưa đủ seed cần test lại khi có nhiều hơn
một trang". Đo trên `wujia_tea_e3a` 15/09/2026: HCM-01 có 14 đơn (2 trang, đủ)
nhưng chỉ 7 yêu cầu hỗ trợ / page_size 20 ⇒ pager KHÔNG BAO GIỜ render ⇒ bảng đo
xanh mà chưa đo gì (đúng họ "Pass rỗng" của D6a).

Seed đủ để có >=5 trang: kiểm được trang đầu/giữa/cuối và dấu "…".
Idempotent: mọi bản ghi mang dấu SEED-E3 và được search-or-create.

LOCAL-ONLY — chạy trên DB copy, KHÔNG chạy trên wujia_tea_19 hay production.

    cd /home/huyban/odoo-dev/WujiaTea
    python3 odoo19/odoo-bin shell -c config/odoo.conf -d <db-copy> --no-http \
        < scripts/seed_e3_pager_demo.py
"""
from datetime import datetime, timedelta

MARK = 'SEED-E3'
TARGET_TICKETS = 45
TARGET_ARTICLES = 40

print('=== SEED E3 — PAGINATION ===')

franchise = env['wujia.franchise.management'].search([('code', '=', 'HCM-01')], limit=1)
if not franchise:
    franchise = env['wujia.franchise.management'].search([], order='code', limit=1)
if not franchise:
    raise SystemExit('Không có franchise nào.')
print('Franchise: [%s] %s (id=%s)' % (franchise.code, franchise.name, franchise.id))

# --------------------------------------------------------------- hỗ trợ
Ticket = env['wujia.support.ticket']
category = env['wujia.support.category'].search([], order='sequence', limit=1)
states = ['new', 'in_progress', 'resolved', 'closed']
# Danh sách portal lọc `created_by_id = người đang đăng nhập` + `portal_visible`
# (controllers/portal.py:46) ⇒ seed bằng admin là 0 dòng, pager không bao giờ
# render và bảng đo ra Pass rỗng. Phải seed ĐÚNG chủ cửa hàng.
owner = env['res.users'].search([('login', '=', 'em.hcm')], limit=1)
if not owner:
    raise SystemExit('Không thấy tài khoản chủ cửa hàng để gán created_by_id.')
have = Ticket.search_count([('franchise_id', '=', franchise.id),
                            ('title', 'like', MARK)])
now = datetime.now()
for i in range(have, TARGET_TICKETS):
    Ticket.create({
        'franchise_id': franchise.id,
        'category_id': category.id if category else False,
        'title': '%s Yêu cầu hỗ trợ mẫu số %02d' % (MARK, i + 1),
        'description': 'Bản ghi seed cho phép đo phân trang E3.',
        'state': states[i % len(states)],
        'created_by_id': owner.id,
        'portal_visible': True,
        'create_date': now - timedelta(days=i),
    })
print('  Hỗ trợ: %d → %d bản ghi mang dấu %s'
      % (have, max(have, TARGET_TICKETS), MARK))

# ------------------------------------------------------------ kiến thức
Article = env['wujia.knowledge.article']
cat = env['wujia.knowledge.category'].search([('active', '=', True)],
                                             order='sequence', limit=1)
have = Article.search_count([('name', 'like', MARK)])
for i in range(have, TARGET_ARTICLES):
    Article.create({
        'name': '%s Bài viết mẫu số %02d' % (MARK, i + 1),
        'category_id': cat.id if cat else False,
        'content': '<p>Bản ghi seed cho phép đo phân trang E3.</p>',
        'publish_date': (now - timedelta(days=i)).date(),
        'active': True,
        # Thiếu `published` là portal không thấy ⇒ lọc theo từ khoá ra 0 dòng,
        # pager không render và bảng đo thành "Pass rỗng".
        'state': 'published',
    })
print('  Kiến thức: %d → %d bài mang dấu %s'
      % (have, max(have, TARGET_ARTICLES), MARK))

env.cr.commit()
print('=== XONG ===')

# ------------------------------------------------- E3b: 5 màn còn lại
# Nhân bản bản ghi có sẵn thay vì dựng tay: mọi trường bắt buộc (UoM, loại lỗi,
# giờ mở hộp…) đã đúng, chỉ đổi mốc thời gian để thứ tự trang ổn định.
TARGET_E3B = 45


def _clone(model, domain, target, vals_fn, label):
    Model = env[model]
    src = Model.search(domain, limit=1)
    if not src:
        print('  %s: không có bản ghi mẫu → bỏ qua' % label)
        return
    have = Model.search_count(domain)
    for i in range(have, target):
        src.copy(vals_fn(i))
    print('  %s: %d → %d' % (label, have, Model.search_count(domain)))


# `state` là copy=False ⇒ bản sao rơi về `draft` và portal KHÔNG thấy (pager rỗng).
_clone('wujia.notification', [('id', '!=', 0)], TARGET_E3B,
       lambda i: {'name': '%s Thông báo mẫu số %02d' % (MARK, i + 1),
                  'published_date': now - timedelta(days=i),
                  'state': 'published'},
       'Thông báo')

_clone('wujia.return.request', [('franchise_id', '=', franchise.id)], TARGET_E3B,
       lambda i: {'request_date': now - timedelta(days=i)}, 'Đổi trả')

_clone('wujia.info.update.request', [('franchise_id', '=', franchise.id)], TARGET_E3B,
       lambda i: {'request_date': now - timedelta(days=i)}, 'Yêu cầu thông tin')

# Chuyến giao: mỗi chuyến cần picking riêng của chính cửa hàng (khuôn seed D5).
Picking, Batch = env['stock.picking'], env['stock.picking.batch']
src_pick = Picking.search([('franchise_id', '=', franchise.id)], limit=1)
bdom = [('picking_ids.franchise_id', '=', franchise.id)]
have = Batch.search_count(bdom)
if not src_pick:
    print('  Chuyến giao: không có picking mẫu → bỏ qua')
else:
    for i in range(have, TARGET_E3B):
        origin = '%s-DLV-%03d' % (MARK, i + 1)
        if Picking.search_count([('origin', '=', origin)]):
            continue
        pick = src_pick.copy({'origin': origin, 'franchise_id': franchise.id})
        Batch.create({'picking_ids': [(6, 0, pick.ids)],
                      'planned_departure': now - timedelta(days=i, hours=3)})
    print('  Chuyến giao: %d → %d' % (have, Batch.search_count(bdom)))

# Thành viên cửa hàng: mỗi thành viên một user portal (ràng buộc 1 user/cửa hàng).
Member = env['wujia.franchise.member']
mdom = [('franchise_id', '=', franchise.id), ('is_currently_valid', '=', True)]
have = Member.search_count(mdom)
group_portal = env.ref('base.group_portal')
for i in range(have, 25):
    login = 'seed.e3.%02d@wujiatea.test' % (i + 1)
    user = env['res.users'].search([('login', '=', login)], limit=1)
    if not user:
        user = env['res.users'].with_context(no_reset_password=True).create({
            'name': '%s Thành viên %02d' % (MARK, i + 1),
            'login': login, 'email': login,
            'group_ids': [(6, 0, [group_portal.id])],
        })
    Member.create({'franchise_id': franchise.id, 'user_id': user.id,
                   'role': 'staff'})
print('  Thành viên: %d → %d' % (have, Member.search_count(mdom)))

env.cr.commit()
print('=== XONG E3b ===')
