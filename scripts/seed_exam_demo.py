"""Seed dữ liệu Đăng ký thi để tự smoke portal (LOCAL-ONLY, KHÔNG vào manifest).

Tạo: 1 time slot + 1 khóa thi (published) + 3 kỳ thi (open) trong horizon 60 ngày
→ đủ để test luồng mobile: chọn khóa → lịch → khung giờ → nhập nhân sự → gửi phiếu
thật; và PC đọc list/chi tiết/kết quả.

Cách chạy (Linux):
    cd /home/huyban/odoo-dev/WujiaTea/odoo19
    python odoo-bin shell -c ../config/odoo.conf -d wujia_tea_19 --no-http \\
        < ../scripts/seed_exam_demo.py

Idempotent: search-or-create theo code/tên; chạy lại không nhân bản.
"""
from datetime import timedelta

from odoo import fields

print("=== SEED EXAM DEMO (course + sessions) ===")

TimeSlot = env['wujia.exam.time.slot']
Course = env['wujia.exam.course']
Session = env['wujia.exam.session']

# --- Time slot -------------------------------------------------------------
slot = TimeSlot.search([('code', '=', 'S0820')], limit=1)
if not slot:
    slot = TimeSlot.create({
        'name': 'Ca sáng 08:20–10:00',
        'code': 'S0820',
        'time_from': 8.3333,   # 08:20
        'time_to': 10.0,       # 10:00
    })
    print(f"  + time slot {slot.name} (id={slot.id})")
else:
    print(f"  = time slot đã có (id={slot.id})")

slot2 = TimeSlot.search([('code', '=', 'S1300')], limit=1)
if not slot2:
    slot2 = TimeSlot.create({
        'name': 'Ca chiều 13:00–14:40',
        'code': 'S1300',
        'time_from': 13.0,
        'time_to': 14.6667,    # 14:40
    })
    print(f"  + time slot {slot2.name} (id={slot2.id})")

# --- Course (published) ----------------------------------------------------
course = Course.search([('name', '=', 'Khóa thi pha chế cơ bản')], limit=1)
if not course:
    course = Course.create({
        'name': 'Khóa thi pha chế cơ bản',
        'description': '<p>Đánh giá kỹ năng pha chế cơ bản cho nhân sự cửa hàng.</p>',
        'time_slot_ids': [(6, 0, [slot.id, slot2.id])],
        'max_participants_per_registration': 4,
        'registration_horizon_days': 60,
    })
    print(f"  + course {course.code} — {course.name} (id={course.id})")
else:
    print(f"  = course đã có {course.code} (id={course.id})")
if course.state != 'published':
    course.action_publish()
    print(f"    → published")

# --- Sessions (open) trong horizon -----------------------------------------
today = fields.Date.context_today(env.user)
plan = [
    (today + timedelta(days=3), slot, 20),
    (today + timedelta(days=7), slot2, 20),
    (today + timedelta(days=14), slot, 4),   # capacity nhỏ để test hết chỗ
]
for exam_date, sl, cap in plan:
    existing = Session.search([
        ('course_id', '=', course.id),
        ('exam_date', '=', exam_date),
        ('time_slot_id', '=', sl.id),
    ], limit=1)
    if existing:
        print(f"  = session {existing.name} {exam_date} đã có (state={existing.state})")
        sess = existing
    else:
        sess = Session.create({
            'course_id': course.id,
            'exam_date': exam_date,
            'time_slot_id': sl.id,
            'location': 'Trung tâm đào tạo Ngô Gia',
            'capacity': cap,
            'max_participants_per_registration': 4,
        })
        print(f"  + session {sess.name} {exam_date} cap={cap} (id={sess.id})")
    if sess.state == 'draft':
        sess.action_open()
        print(f"    → open registration")

env.cr.commit()
print("=== DONE. Đăng nhập portal → /portal/exam/register để test. ===")
