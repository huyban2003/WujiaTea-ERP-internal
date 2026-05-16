"""Seed demo data for wujia_portal_knowledge (full BA spec).

Idempotent (upsert by name / slug / code). Creates 3 categories,
5 tags, ~15 articles mixing state and portal_badge to exercise the
full schema introduced in Sprint 5.

Run:
    cd /home/huyban/odoo-dev/WujiaTea/odoo19
    /home/huyban/miniconda3/envs/odoo/bin/python odoo-bin shell \\
        -c /home/huyban/odoo-dev/WujiaTea/config/odoo.conf \\
        -d wujia_tea_19 --no-http \\
        < /home/huyban/odoo-dev/WujiaTea/scripts/seed_knowledge_demo.py
"""
from datetime import datetime, timedelta

print("=== SEEDING WUJIA_PORTAL_KNOWLEDGE DEMO DATA ===")


def upsert(model_name, search_domain, vals, label):
    Model = env[model_name]
    rec = Model.search(search_domain, limit=1)
    if rec:
        rec.write(vals)
        print(f"  [UPDATE] {label}: {rec.display_name or rec.id}")
    else:
        rec = Model.create(vals)
        print(f"  [CREATE] {label}: {rec.display_name or rec.id}")
    return rec


print("\n[1] Categories")
cat_ops = upsert(
    'wujia.knowledge.category', [('code', '=', 'operation')],
    {'name': 'Vận hành cửa hàng', 'code': 'operation', 'sequence': 10,
     'description': 'SOP vận hành hàng ngày.'},
    'category: operation',
)
cat_prod = upsert(
    'wujia.knowledge.category', [('code', '=', 'product')],
    {'name': 'Sản phẩm & pha chế', 'code': 'product', 'sequence': 20,
     'description': 'Công thức và quy trình pha chế.'},
    'category: product',
)
cat_mkt = upsert(
    'wujia.knowledge.category', [('code', '=', 'marketing')],
    {'name': 'Marketing & khách hàng', 'code': 'marketing', 'sequence': 30,
     'description': 'Hướng dẫn chăm sóc khách và chương trình KM.'},
    'category: marketing',
)

print("\n[2] Tags")
tag_data = [
    ('Mới bắt đầu', 1),
    ('Bắt buộc đọc', 2),
    ('Cập nhật 2026', 3),
    ('POS', 4),
    ('Pha chế', 5),
]
tag_ids = []
for name, color in tag_data:
    t = upsert(
        'wujia.knowledge.tag', [('name', '=', name)],
        {'name': name, 'color': color}, f'tag: {name}',
    )
    tag_ids.append(t.id)

print("\n[3] Articles — mix state, badge, expired")
now = datetime.now()
past = now - timedelta(days=30)
future = now + timedelta(days=60)
expired_past = now - timedelta(days=1)

articles = [
    # (slug, name, cat, state, badge, expired, tag_indices)
    ('sop-mo-cua-hang', 'SOP mở cửa hàng buổi sáng', cat_ops, 'published',
     'mandatory', None, [0, 1]),
    ('sop-dong-cua', 'SOP đóng cửa hàng buổi tối', cat_ops, 'published',
     'mandatory', None, [1]),
    ('quy-trinh-kiem-kho', 'Quy trình kiểm kho tuần', cat_ops, 'published',
     'important', None, [2]),
    ('huong-dan-pos', 'Hướng dẫn sử dụng POS căn bản', cat_ops, 'published',
     'new', None, [3]),
    ('cong-thuc-tra-sua-truyen-thong', 'Công thức trà sữa truyền thống',
     cat_prod, 'published', 'normal', None, [4]),
    ('cong-thuc-mua-he-2026', 'Công thức món mới hè 2026', cat_prod,
     'published', 'new', future, [4, 2]),
    ('cong-thuc-cu-2025', 'Công thức cũ hè 2025 (đã ngưng)', cat_prod,
     'published', 'normal', expired_past, [4]),
    ('chu-de-marketing-tet', 'Bộ chủ đề marketing Tết 2026', cat_mkt,
     'published', 'important', None, []),
    ('script-cham-soc', 'Script chăm sóc khách hàng', cat_mkt, 'published',
     'normal', None, []),
    ('khoi-dau-pha-che-tai-nha', 'Sơ lược pha chế tại nhà',
     cat_prod, 'draft', 'normal', None, [0]),
    ('quy-trinh-bao-tri', 'Quy trình bảo trì máy pha cà phê', cat_ops,
     'draft', 'normal', None, []),
    ('km-tet-2024', 'KM Tết 2024 (lưu trữ)', cat_mkt, 'archived',
     'normal', None, []),
]

for slug, name, cat, state, badge, expired, t_idx in articles:
    vals = {
        'name': name, 'slug': slug, 'category_id': cat.id,
        'summary': f'Mô tả ngắn — {name}',
        'content': f'<p>Đây là nội dung mẫu của bài <strong>{name}</strong>.</p>'
                   f'<p>Nội dung bài viết sẽ được biên tập sau.</p>',
        'state': state, 'portal_badge': badge,
        'tag_ids': [(6, 0, [tag_ids[i] for i in t_idx])] if t_idx else False,
    }
    if expired:
        vals['expired_date'] = expired
    if state == 'published':
        vals['publish_date'] = past
    upsert(
        'wujia.knowledge.article', [('slug', '=', slug)],
        vals, f'article: {slug}',
    )

env.cr.commit()
print("\n=== DONE ===")
