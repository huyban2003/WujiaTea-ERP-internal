"""Seed dữ liệu demo cho Portal Phase 1.0 (Sprint 4) vào DB local.

Mục đích: tạo records dev để test giao diện 8 module portal_*. KHÔNG load
qua Odoo demo data XML (theo feedback rule), chỉ chạy thủ công local.

Cách chạy:
    cd /home/huyban/odoo-dev/WujiaTea/odoo19
    /home/huyban/miniconda3/envs/odoo/bin/python odoo-bin shell \\
        -c /home/huyban/odoo-dev/WujiaTea/config/odoo.conf \\
        -d wujia_tea_19 --no-http \\
        < /home/huyban/odoo-dev/WujiaTea/scripts/seed_portal_demo.py

Idempotent: search-or-create theo `name`/`code`. Chạy nhiều lần không nhân đôi.
"""
from datetime import datetime, timedelta

print("=== SEEDING WUJIA PORTAL PHASE 1.0 DEMO DATA ===")


def upsert(model_name, domain, vals, label):
    Model = env[model_name]
    rec = Model.search(domain, limit=1)
    if rec:
        rec.write(vals)
        print(f"  [UPDATE] {label}: {rec.display_name or rec.id}")
    else:
        rec = Model.create(vals)
        print(f"  [CREATE] {label}: {rec.display_name or rec.id}")
    return rec


def has_model(name):
    return name in env

now = datetime.now()
today = now.date()

# ============================================================
# 1) Franchises (lookup từ wujia_portal_base.sample_data)
# ============================================================
print("\n[1] Franchise lookup")
franchises = env['wujia.franchise.management'].search([], limit=3)
if not franchises:
    print("  WARNING: Không có franchise nào. Chạy `wujia_portal_base/data/sample_data.xml` trước.")
else:
    print(f"  Found {len(franchises)} franchise: {franchises.mapped('name')}")

admin = env.ref('base.user_admin')

# ============================================================
# 2) Notifications (10 record + read tracking 5)
# ============================================================
if has_model('wujia.notification') and franchises:
    print("\n[2] Notifications (10 records)")
    types = {t.code: t for t in env['wujia.notification.type'].search([])}
    for i in range(10):
        code = ['URG', 'GEN', 'PROMO', 'SYS', 'OTH'][i % 5]
        n = upsert(
            'wujia.notification',
            [('name', '=', f'Thông báo demo #{i+1}')],
            {
                'name': f'Thông báo demo #{i+1}',
                'type_id': types.get(code, env['wujia.notification.type'].browse()).id or False,
                'dispatch_number': f'CV-{2026}-{i+1:03d}',
                'date': now - timedelta(days=i),
                'content': f'<p>Đây là nội dung mẫu cho thông báo #{i+1}. Mục đích: test giao diện list + detail page.</p><p>Vui lòng xem kỹ và phản hồi nếu có thắc mắc.</p>',
                'franchise_ids': [(6, 0, franchises.ids[:2 if i % 2 else 0])] if i % 3 else [(6, 0, [])],
                'published': True,
                'priority': 'urgent' if i == 0 else 'normal',
            },
            f'noti #{i+1}',
        )

# ============================================================
# 3) Return error types đã seed qua data/return_error_type_data.xml
# ============================================================

# ============================================================
# 4) Return requests (5 record, mix 5 state)
# ============================================================
if has_model('wujia.return.request') and franchises:
    print("\n[4] Return requests (5 records)")
    error_types = env['wujia.return.error.type'].search([], limit=5)
    states = ['draft', 'sent', 'approved', 'rejected', 'done']
    for i, st in enumerate(states):
        rr = upsert(
            'wujia.return.request',
            [('name', '=', f'WJ-RR/26/DEMO{i+1:05d}')],
            {
                'name': f'WJ-RR/26/DEMO{i+1:05d}',
                'franchise_id': franchises[i % len(franchises)].id,
                'request_date': now - timedelta(days=i*2),
                'state': st,
                'error_id': error_types[i % len(error_types)].id if error_types else False,
                'note': f'Yêu cầu đổi trả mẫu #{i+1} — {st}',
                'expected_delivery_date': today + timedelta(days=3),
                'refuse_reason': 'Không đủ chứng cứ ảnh' if st == 'rejected' else False,
            },
            f'return #{i+1}',
        )

# ============================================================
# 5) Knowledge categories (3) + articles (8)
# ============================================================
if has_model('wujia.knowledge.category'):
    print("\n[5] Knowledge categories + articles")
    cats = {}
    for code, name in [('OPS', 'Vận hành'), ('PROD', 'Sản phẩm'), ('MKT', 'Marketing')]:
        cats[code] = upsert(
            'wujia.knowledge.category',
            [('code', '=', code)],
            {'code': code, 'name': name, 'sequence': 10},
            f'cat {code}',
        )
    sample_articles = [
        ('OPS', 'Quy trình mở cửa hàng buổi sáng', 'Checklist 12 bước cho ca sáng.'),
        ('OPS', 'Vệ sinh máy pha trà cuối ngày', 'Hướng dẫn vệ sinh đúng cách.'),
        ('OPS', 'Quản lý tồn nguyên liệu hằng ngày', 'Cập nhật tồn theo ca.'),
        ('PROD', 'Công thức Hồng Trà Sữa nguyên bản', 'Tỷ lệ pha chuẩn.'),
        ('PROD', 'Pha trà Earl Grey size L', 'Định lượng và phụ liệu.'),
        ('PROD', 'Cách kiểm tra hạn sử dụng nguyên liệu', 'Dấu hiệu nhận biết NL hết hạn.'),
        ('MKT', 'Kịch bản đón khách Wujia Premium', 'Lời chào, gợi ý món.'),
        ('MKT', 'Hướng dẫn chạy combo sinh nhật', 'Lưu ý khi áp dụng combo.'),
    ]
    for cat_code, name, summary in sample_articles:
        slug = name.lower().replace(' ', '-')
        for ch in ['ạ','á','à','ả','ã','ô','ơ','ư','ê','đ','ó','ú','í','é','ẹ','ợ','ự','ự','ầ','ấ','ậ','ằ','ắ','ặ','ẽ','ẻ','ề','ế','ệ','ể','ễ','ỉ','ị','ỏ','ọ','ổ','ố','ồ','ộ','ỗ','ờ','ớ','ợ','ở','ỡ','ụ','ủ','ứ','ừ','ử','ữ','ự','ỳ','ý','ỵ','ỷ','ỹ']:
            slug = slug.replace(ch, '')
        slug = ''.join(c if c.isalnum() or c == '-' else '' for c in slug)[:80]
        upsert(
            'wujia.knowledge.article',
            [('slug', '=', slug)],
            {
                'name': name,
                'slug': slug,
                'category_id': cats[cat_code].id,
                'summary': summary,
                'content': f'<p>{summary}</p><p>Chi tiết hướng dẫn cho bài viết &lt;{name}&gt; sẽ được biên tập đầy đủ ở giai đoạn nội dung.</p>',
                'published': True,
                'publish_date': now - timedelta(days=sample_articles.index((cat_code, name, summary))),
            },
            f'article {name[:30]}',
        )

# ============================================================
# 6) Exam schedule (3) + registration (3) + result (1)
# ============================================================
if has_model('wujia.exam.schedule') and franchises:
    print("\n[6] Exam schedule + registration + result")
    schedules = []
    for i, (offset_days, name, state) in enumerate([
        (7, 'Thi pha chế Hồng Trà Sữa Q3 2026', 'open'),
        (14, 'Thi vận hành cửa hàng', 'open'),
        (-7, 'Thi nhận biết nguyên liệu', 'done'),
    ]):
        s = upsert(
            'wujia.exam.schedule',
            [('name', '=', name)],
            {
                'name': name,
                'exam_date': now + timedelta(days=offset_days),
                'location': 'Trụ sở HQ — Tầng 3' if i % 2 else 'Online — Google Meet',
                'description': f'Kỳ thi {name} — bắt buộc cho nhân viên.',
                'state': state,
                'max_participants': 30,
                'franchise_ids': [(6, 0, franchises.ids)] if i % 2 else [(6, 0, [])],
            },
            f'exam {name[:30]}',
        )
        schedules.append(s)
    # 3 đăng ký
    for i, sched in enumerate(schedules):
        upsert(
            'wujia.exam.registration',
            [('user_id', '=', admin.id), ('schedule_id', '=', sched.id)],
            {
                'user_id': admin.id,
                'schedule_id': sched.id,
                'franchise_id': franchises[i % len(franchises)].id,
                'state': 'registered' if sched.state != 'done' else 'checked_in',
                'register_date': now - timedelta(days=1),
            },
            f'reg admin × {sched.name[:25]}',
        )
    # 1 kết quả cho schedule done
    done_sched = next((s for s in schedules if s.state == 'done'), None)
    if done_sched:
        reg = env['wujia.exam.registration'].search([
            ('schedule_id', '=', done_sched.id), ('user_id', '=', admin.id),
        ], limit=1)
        if reg:
            upsert(
                'wujia.exam.result',
                [('registration_id', '=', reg.id)],
                {
                    'registration_id': reg.id,
                    'score': 8.5,
                    'passed': True,
                    'note': 'Hoàn thành xuất sắc.',
                },
                f'result reg {reg.name}',
            )

# ============================================================
# 7) Support tickets (3, mix state)
# ============================================================
if has_model('wujia.support.ticket') and franchises:
    print("\n[7] Support tickets (3 records)")
    for i, (st, cat, prio, subj) in enumerate([
        ('new', 'order', 'high', 'Không đặt được đơn hàng giao ngày 12/05'),
        ('in_progress', 'product', 'normal', 'Sản phẩm Hồng Trà Sữa lon bị méo bao bì'),
        ('resolved', 'pos', 'low', 'Máy POS in hóa đơn lệch nội dung'),
    ]):
        upsert(
            'wujia.support.ticket',
            [('subject', '=', subj)],
            {
                'subject': subj,
                'description': f'Mô tả chi tiết cho ticket #{i+1}: {subj}. Nhập lại đầy đủ thông tin để HQ xử lý.',
                'franchise_id': franchises[i % len(franchises)].id,
                'category': cat, 'priority': prio, 'state': st,
            },
            f'ticket {subj[:25]}',
        )

# ============================================================
# 8) Sale orders portal demo (10 record cho dashboard + history)
# ============================================================
if franchises:
    print("\n[8] Sale orders demo (10 records)")
    SO = env['sale.order']
    products = env['product.product'].search([], limit=5)
    if not products:
        print("  WARNING: không có product — bỏ qua tạo SO. Cần seed product trước.")
    else:
        # Tìm portal user đã có membership active để pass _check_portal_franchise_membership
        Member = env['wujia.franchise.member']
        for i in range(10):
            franch = franchises[i % len(franchises)]
            membership = Member.search([
                ('franchise_id', '=', franch.id),
                ('is_currently_valid', '=', True),
            ], limit=1)
            if not membership:
                print(f"  WARNING: franchise {franch.name} chưa có member — bỏ qua SO #{i+1}.")
                continue
            existing_name = f'WJ-PORTAL-SO-{i+1:03d}'
            existing = SO.search([('client_order_ref', '=', existing_name)], limit=1)
            if existing:
                continue
            so = SO.create({
                'partner_id': franch.partner_id.id if franch.partner_id else env['res.partner'].search([('is_company','=',True)], limit=1).id,
                'is_portal_order': True,
                'franchise_id': franch.id,
                'franchise_partner_id': franch.partner_id.id if franch.partner_id else False,
                'portal_requester_user_id': membership.user_id.id,
                'portal_member_id': membership.id,
                'client_order_ref': existing_name,
                'date_order': now - timedelta(days=i),
                'order_line': [(0, 0, {
                    'product_id': products[i % len(products)].id,
                    'product_uom_qty': 5 + i,
                }) for _ in range(min(3, len(products)))],
            })
            if i % 3 == 0:
                so.action_confirm()
            print(f"  [CREATE] SO {existing_name}: {so.name} (member: {membership.user_id.name})")

env.cr.commit()
print("\n=== DONE — đã commit transaction ===")
print("Tổng quan: kiểm tra tại http://localhost:8019/portal sau khi login.")
