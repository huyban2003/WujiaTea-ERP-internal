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
    })
print('  Kiến thức: %d → %d bài mang dấu %s'
      % (have, max(have, TARGET_ARTICLES), MARK))

env.cr.commit()
print('=== XONG ===')
