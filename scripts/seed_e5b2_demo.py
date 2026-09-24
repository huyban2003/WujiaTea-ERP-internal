"""Seed cho lượt E5b2 — đủ NHÁNH để đo anatomy ListCard của Thi + Công nợ (LOCAL-ONLY).

Vì sao cần: trước khi gieo, DB đo chỉ có 1 khoá thi (bước 1 wizard ra 1 card, không có
nhánh "đã đóng"), 45/45 dòng nhân sự đều `pending` (nhánh Đạt/Không đạt không bao giờ
render), và mọi hoá đơn của tuần hiện tại đều `unpaid` (3 nhãn tiền còn lại không hiện).
Đo trên dữ liệu đó ra bảng "Pass rỗng" — đúng bẫy đã dính 2 lần ở E5b1.

Tạo:
  · 2 khoá thi published nữa — một CÒN LỊCH, một ĐÃ ĐÓNG (không kỳ mở trong horizon);
  · 1 phiếu đăng ký đã công bố kết quả, có cả người Đạt lẫn Không đạt (+ ghi chú);
  · tuần HIỆN TẠI của cửa hàng đầu tiên: 1 hoá đơn quá hạn · 1 giấy báo có · 1 đã trả đủ;
  · vài thông báo ở trạng thái ĐÃ ĐỌC cho tài khoản đo (trước đó 10/10 đều chưa đọc).

Cách chạy (Mac):
    cd ~/odoo-dev/WujiaTea/odoo19
    python odoo-bin shell -c ../config/odoo.conf -d wujia_e4b1 --no-http \
        < ../scripts/seed_e5b2_demo.py

Idempotent: search-or-create theo tên/ref; chạy lại không nhân bản.
"""
from datetime import date, timedelta

from odoo import fields

print("=== SEED E5b2 (Thi + Công nợ + thông báo đã đọc) ===")

PORTAL_LOGIN = 'em.hcm'

Course = env['wujia.exam.course']
Session = env['wujia.exam.session']
TimeSlot = env['wujia.exam.time.slot']
today = fields.Date.context_today(env.user)

slots = TimeSlot.search([], limit=2)
if not slots:
    raise SystemExit("Chưa có time slot — chạy seed_exam_demo.py trước.")


def ensure_course(name, horizon, open_sessions, past_sessions=0):
    course = Course.search([('name', '=', name)], limit=1)
    if not course:
        course = Course.create({
            'name': name,
            'description': '<p>%s</p>' % name,
            'time_slot_ids': [(6, 0, slots.ids)],
            'max_participants_per_registration': 4,
            'registration_horizon_days': horizon,
        })
        print("  + course %s — %s" % (course.code, name))
    if course.state != 'published':
        course.action_publish() if hasattr(course, 'action_publish') else course.write({'state': 'published'})
    for i in range(open_sessions):
        d = today + timedelta(days=7 + i * 7)
        if not Session.search([('course_id', '=', course.id), ('exam_date', '=', d)], limit=1):
            Session.create({
                'course_id': course.id, 'exam_date': d,
                'time_slot_id': slots[0].id, 'capacity': 20,
                'location': 'Trung tâm đào tạo Wujia',
                'state': 'open',
            })
    for i in range(past_sessions):
        d = today - timedelta(days=30 + i * 7)
        if not Session.search([('course_id', '=', course.id), ('exam_date', '=', d)], limit=1):
            s = Session.create({
                'course_id': course.id, 'exam_date': d,
                'time_slot_id': slots[0].id, 'capacity': 20,
                'location': 'Trung tâm đào tạo Wujia',
            })
            s.write({'state': 'closed'}) if 'closed' in dict(
                s._fields['state'].selection) else None
    return course


c_open = ensure_course('Khóa thi phục vụ nâng cao', 60, open_sessions=2)
c_closed = ensure_course('Khóa thi quản lý ca', 30, open_sessions=0, past_sessions=1)
print("  = khoá còn lịch: %s · khoá đã đóng: %s" % (c_open.code, c_closed.code))

# --- Phiếu đăng ký ĐÃ CÔNG BỐ kết quả: cần cả Đạt lẫn Không đạt -------------
Reg = env['wujia.exam.registration']
reg = Reg.search([('state', '=', 'confirmed')], order='id', limit=1)
if not reg:
    print("  ! không có phiếu confirmed nào — bỏ qua phần kết quả")
else:
    sess = reg.session_id
    lines = reg.line_ids
    if len(lines) < 2:
        base = lines[:1]
        for idx in range(2 - len(lines)):
            env['wujia.exam.registration.line'].create({
                'registration_id': reg.id,
                'session_id': sess.id,
                'franchise_id': reg.franchise_id.id,
                'employee_name': 'Nguyễn Thị Kết Quả %d' % (idx + 1),
                'phone': '090000000%d' % (idx + 1),
                'job_position': 'Nhân viên pha chế',
            })
        lines = reg.line_ids
    lines[0].write({'result': 'passed', 'result_note': False})
    lines[1].write({'result': 'failed',
                    'result_note': 'Chưa đạt phần định lượng, đăng ký thi lại khi có lịch mở.'})
    if not sess.results_published:
        sess.write({'results_published': True,
                    'results_published_date': fields.Datetime.now()})
    print("  + phiếu %s: %d người (1 Đạt · 1 Không đạt), kỳ %s đã công bố"
          % (reg.name or reg.id, len(lines), sess.name or sess.id))

# --- Công nợ tuần HIỆN TẠI: overdue · credit · paid -------------------------
franchise = env['wujia.franchise.management'].search([], order='code', limit=1)
company = env.company
partner = franchise.partner_id or env.ref('base.user_admin').partner_id
income = env['account.account'].search([('account_type', '=', 'income')], limit=1)
sale_journal = env['account.journal'].search(
    [('type', '=', 'sale'), ('company_id', '=', company.id)], limit=1)
today_d = date.today()
monday = today_d - timedelta(days=today_d.weekday())


def make_move(move_type, inv_date, due, amount, tag):
    ref = 'SEED-E5B2-%s' % tag
    existing = env['account.move'].search([('ref', '=', ref)], limit=1)
    if existing:
        return existing
    move = env['account.move'].create({
        'move_type': move_type,
        'partner_id': partner.id,
        'invoice_date': inv_date,
        'journal_id': sale_journal.id,
        'franchise_id': franchise.id,
        'ref': ref,
        'invoice_payment_term_id': False,
        'invoice_line_ids': [(0, 0, {
            'name': 'Nguyên liệu tuần %s' % inv_date.isocalendar()[1],
            'quantity': 1, 'price_unit': amount,
            'account_id': income.id, 'tax_ids': [(6, 0, [])],
        })],
    })
    move.action_post()
    move.invoice_date_due = due
    return move


# Gieo vào ĐÚNG TUẦN PORTAL TỰ MỞ, không phải tuần hiện tại: `_default_week`
# (WJ-DEBT-010) mở tuần quá hạn CŨ NHẤT còn dư ⇒ gieo vào tuần hiện tại thì màn
# mặc định vẫn chỉ có 1 hoá đơn và bảng đo lại rỗng nhánh.
summary = env['wujia.portal.debt'].get_summary(franchise.id)
dmonday = date.fromisocalendar(int(summary['week_key'][:4]),
                               int(summary['week_key'][6:]), 1)
print("  = tuần portal mở sẵn: %s (%s)" % (summary['week_key'], dmonday))

mo = make_move('out_invoice', monday, monday - timedelta(days=1), 3_150_000, 'NOW-OVERDUE')
mc = make_move('out_refund', dmonday + timedelta(days=1), dmonday + timedelta(days=1),
               1_275_000, 'DEF-CREDIT')
mp = make_move('out_invoice', dmonday, dmonday + timedelta(days=6), 2_480_000, 'DEF-PAID')

# Hoá đơn "đã trả" phải được ĐỐI TRỪ thật, không chỉ đổi cờ — `_invoice_status`
# đọc amount_residual chứ không đọc payment_state một mình.
if mp.amount_residual > 0:
    # Memo gắn theo CHÍNH hoá đơn: dùng một memo cố định thì lượt chạy sau
    # tìm lại payment đã khớp vào hoá đơn cũ và hoá đơn mới không bao giờ tất toán.
    pay_ref = 'SEED-E5B2-PAY-%s' % mp.id
    payment = env['account.payment'].search([('memo', '=', pay_ref)], limit=1)
    if not payment:
        payment = env['account.payment'].create({
            'amount': mp.amount_total, 'date': dmonday + timedelta(days=2),
            'payment_type': 'inbound', 'partner_type': 'customer',
            'partner_id': partner.id, 'memo': pay_ref,
        })
        payment.action_post()
        payment.franchise_id = franchise
    lines = (mp.line_ids + payment.move_id.line_ids).filtered(
        lambda l: l.account_id.account_type == 'asset_receivable' and not l.reconciled)
    if lines:
        lines.reconcile()
print("  + quá hạn %s (tuần này) · báo có %s · đã trả %s (tuần mặc định, còn %s)"
      % (mo.name, mc.name, mp.name, mp.amount_residual))
franchise._recompute_portal_debt_batch()

# --- Thông báo đã đọc cho tài khoản đo --------------------------------------
user = env['res.users'].search([('login', '=', PORTAL_LOGIN)], limit=1)
if user:
    Read = env['wujia.notification.read']
    member = env['wujia.franchise.member'].search([('user_id', '=', user.id)], limit=1)
    notis = env['wujia.notification'].search([('state', '=', 'published')], limit=3)
    made = 0
    for noti in notis:
        if not Read.search([('notification_id', '=', noti.id),
                            ('user_id', '=', user.id)], limit=1):
            Read.create({
                'notification_id': noti.id, 'user_id': user.id,
                'franchise_id': member.franchise_id.id if member else False,
                'member_id': member.id if member else False,
                'last_open_date': fields.Datetime.now(),
            })
            made += 1
    print("  + %d thông báo chuyển sang ĐÃ ĐỌC cho %s" % (made, PORTAL_LOGIN))

env.cr.commit()
print("=== DONE (committed) ===")
