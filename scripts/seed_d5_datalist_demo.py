"""Seed dữ liệu cho cụm D5 (DataList CMP-DL-001) — đủ mốc BA acceptance #7.

BA đòi thử danh sách ở 0/1/2/10/11/50+ record, mà DB dev chỉ có 4 ticket / 4 phiếu
bù hàng / 1 chuyến giao / 0 hoá đơn / 0 phiếu khảo sát cho HN-01 (xem
docs/d5-datalist-inventory.md §5). Không có dữ liệu thì không có bảng đo trước–sau.

Idempotent: mọi bản ghi mang dấu SEED-D5 và được search-or-create.
LOCAL-ONLY — chạy trên DB copy, KHÔNG chạy trên wujia_tea_19 hay production.

    cd /home/huyban/odoo-dev/WujiaTea
    python3 odoo19/odoo-bin shell -c config/odoo.conf -d <db-copy> --no-http \
        --logfile=<thư-mục>/x.log < scripts/seed_d5_datalist_demo.py
"""
from datetime import date, datetime, timedelta

MARK = 'SEED-D5'
N_TICKET = 55      # > 50 để chạm mốc "50+" của acceptance #7
N_RETURN = 24        # > PAGE_SIZE 20 ⇒ pager thật sự hiện, guard page_count>1 được thử
N_INVOICE = 14
N_INSPECTION = 14
N_BATCH = 14

print("=== SEED D5 DATALIST ===")

franchise = env['wujia.franchise.management'].search([('code', '=', 'HN-01')], limit=1)
if not franchise:
    franchise = env['wujia.franchise.management'].search([], order='code', limit=1)
if not franchise:
    raise SystemExit("Không có franchise nào.")
print(f"Franchise: [{franchise.code}] {franchise.name} (id={franchise.id})")

now = datetime.now()
today = date.today()
admin = env.ref('base.user_admin')

# Portal Hỗ trợ lọc theo created_by_id = user đang đăng nhập, nên ticket phải thuộc
# chính chủ cửa hàng, không phải admin.
member = env['wujia.franchise.member'].search(
    [('franchise_id', '=', franchise.id), ('user_id', '!=', False)], limit=1)
owner_user = member.user_id or admin
print(f"Chủ cửa hàng: {owner_user.login} (id={owner_user.id})")


def upsert(model, domain, vals, label):
    rec = env[model].search(domain, limit=1)
    if rec:
        return rec
    rec = env[model].create(vals)
    print(f"  [CREATE] {label}: {rec.display_name or rec.id}")
    return rec


# ---------------------------------------------------------------- tickets
cats = env['wujia.support.category'].search([], order='sequence')
states = ['new', 'in_progress', 'waiting', 'resolved', 'closed']
prios = ['low', 'normal', 'high', 'urgent']
have = env['wujia.support.ticket'].search_count([('franchise_id', '=', franchise.id)])
print(f"\n[1] Support tickets — hiện {have}, cần {N_TICKET}")
Ticket = env['wujia.support.ticket']
valid_states = [s for s in states if s in dict(Ticket._fields['state'].selection)]
valid_prios = [p for p in prios if p in dict(Ticket._fields['priority'].selection)]
for i in range(max(0, N_TICKET - have)):
    title = f'[{MARK}] Yêu cầu hỗ trợ mẫu số {i + 1:03d}'
    upsert('wujia.support.ticket', [('title', '=', title)], {
        'title': title,
        'franchise_id': franchise.id,
        'category_id': cats[i % len(cats)].id,
        'created_by_id': owner_user.id,
        'priority': valid_prios[i % len(valid_prios)],
        'state': valid_states[i % len(valid_states)],
        'description': f'<p>Nội dung mẫu cho phiếu hỗ trợ số {i + 1}.</p>',
    }, f'ticket {i + 1}')
stale = env['wujia.support.ticket'].search(
    [('title', 'like', f'[{MARK}]'), ('created_by_id', '!=', owner_user.id)])
if stale:
    stale.write({'created_by_id': owner_user.id})
    print(f"  [FIX] gán lại {len(stale)} ticket về {owner_user.login}")
print(f"  → {env['wujia.support.ticket'].search_count([('created_by_id', '=', owner_user.id)])} ticket của chủ cửa hàng")

# ---------------------------------------------------------------- returns
issue_types = env['wujia.return.issue.type'].search([], limit=5)
products = env['product.product'].search([('sale_ok', '=', True)], limit=5)
uom = env.ref('uom.product_uom_unit', raise_if_not_found=False)
have = env['wujia.return.request'].search_count([('franchise_id', '=', franchise.id)])
print(f"\n[2] Return requests — hiện {have}, cần {N_RETURN}")
if not (issue_types and products and uom):
    print("  ! bỏ qua: thiếu loại lỗi / sản phẩm / đơn vị tính")
else:
    rr_states = ['draft', 'submitted', 'reviewing', 'approved', 'processing', 'done', 'rejected']
    # Đánh số theo mã cố định 001..N (không theo phần còn thiếu) — chạy lại lần hai
    # với N lớn hơn thì phần thêm mới không đụng mã đã có.
    for i in range(N_RETURN):
        code = f'WJ-RR/{MARK}/{i + 1:03d}'
        upsert('wujia.return.request', [('name', '=', code)], {
            'name': code,
            'franchise_id': franchise.id,
            'request_date': now - timedelta(days=i),
            'state': rr_states[i % len(rr_states)],
            'product_id': products[i % len(products)].id,
            'request_qty': 1.0 + i,
            'request_uom_id': uom.id,
            'opening_datetime': now - timedelta(days=i, hours=2),
            'issue_type_id': issue_types[i % len(issue_types)].id,
            'note': f'Phiếu bù hàng mẫu {i + 1}',
        }, f'return {i + 1}')
print(f"  → {env['wujia.return.request'].search_count([('franchise_id', '=', franchise.id)])} phiếu")

# ---------------------------------------------------------------- invoices
print(f"\n[3] Hoá đơn có franchise_id (cho /portal/debt)")
partner = franchise.partner_id or admin.partner_id
income = env['account.account'].search([('account_type', '=', 'income')], limit=1)
journal = env['account.journal'].search(
    [('type', '=', 'sale'), ('company_id', '=', env.company.id)], limit=1)
have = env['account.move'].search_count(
    [('franchise_id', '=', franchise.id), ('move_type', '=', 'out_invoice')])
print(f"  hiện {have}, cần {N_INVOICE}")
if not (income and journal and partner):
    print("  ! bỏ qua: thiếu partner / income account / sale journal")
else:
    for i in range(max(0, N_INVOICE - have)):
        ref = f'{MARK}-INV-{i + 1:03d}'
        if env['account.move'].search_count([('ref', '=', ref)]):
            continue
        inv_date = today - timedelta(days=7 * i)
        move = env['account.move'].create({
            'move_type': 'out_invoice',
            'partner_id': partner.id,
            'invoice_date': inv_date,
            'journal_id': journal.id,
            'franchise_id': franchise.id,
            'ref': ref,
            'invoice_payment_term_id': False,
            'invoice_line_ids': [(0, 0, {
                'name': f'Nguyên liệu đợt {i + 1}',
                'quantity': 1,
                'price_unit': 1500000.0 + i * 250000,
                'account_id': income.id,
                'tax_ids': [(6, 0, [])],
            })],
        })
        move.action_post()
        # Xen kẽ quá hạn / chưa tới hạn để thử đủ trạng thái công nợ.
        move.invoice_date_due = inv_date + timedelta(days=3 if i % 2 else 30)
        print(f"  [CREATE] invoice {ref}")
print(f"  → {env['account.move'].search_count([('franchise_id', '=', franchise.id)])} hoá đơn")

# ---------------------------------------------------------------- inspections
print(f"\n[4] Phiếu khảo sát (cho /portal/inspection)")
have = env['wujia.franchise.inspection'].search_count([('franchise_id', '=', franchise.id)])
print(f"  hiện {have}, cần {N_INSPECTION}")
template = env['wujia.franchise.inspection.template'].search([], limit=1)
for i in range(max(0, N_INSPECTION - have)):
    name = f'KS/{MARK}/{i + 1:03d}'
    # schedule_id là NOT NULL ở tầng DB — mỗi phiếu phải có lịch giám sát riêng.
    schedule = upsert('wujia.supervision.schedule', [('name', '=', f'LGS/{MARK}/{i + 1:03d}')], {
        'name': f'LGS/{MARK}/{i + 1:03d}',
        'store_id': franchise.id,
        'user_id': admin.id,
        'date': today - timedelta(days=10 * i),
    }, f'schedule {i + 1}')
    vals = {
        'name': name,
        'schedule_id': schedule.id,
        'franchise_id': franchise.id,
        'planned_date': today - timedelta(days=10 * i),
        'submit_date': today - timedelta(days=10 * i),
        'state': 'need_remediation' if i % 3 else 'done',
        'inspector_user_id': admin.id,
        'test_employee_name': f'Nhân viên mẫu {i + 1}',
    }
    if template:
        vals['template_id'] = template.id
    upsert('wujia.franchise.inspection', [('name', '=', name)], vals, f'inspection {i + 1}')
print(f"  → {env['wujia.franchise.inspection'].search_count([('franchise_id', '=', franchise.id)])} phiếu")

# ---------------------------------------------------------------- delivery
print(f"\n[5] Chuyến giao (cho /portal/delivery)")
Picking = env['stock.picking']
Batch = env['stock.picking.batch']
src = Picking.search([('franchise_id', '=', franchise.id), ('batch_id', '!=', False)], limit=1) \
    or Picking.search([('franchise_id', '=', franchise.id)], limit=1)
have = Batch.search_count([('picking_ids.franchise_id', '=', franchise.id)])
print(f"  hiện {have}, cần {N_BATCH}")
if not src:
    print("  ! bỏ qua: không có picking mẫu của cửa hàng này")
else:
    b_states = ['draft', 'assigned', 'delivering', 'done']
    for i in range(max(0, N_BATCH - have)):
        origin = f'{MARK}-DLV-{i + 1:03d}'
        if Picking.search_count([('origin', '=', origin)]):
            continue
        pick = src.copy({'origin': origin, 'franchise_id': franchise.id})
        batch = Batch.create({
            'picking_ids': [(6, 0, pick.ids)],
            'planned_departure': now - timedelta(days=i, hours=3),
        })
        status = b_states[i % len(b_states)]
        if 'delivery_batch_status' in batch._fields:
            batch.delivery_batch_status = status
        print(f"  [CREATE] batch {batch.name} ({status}) ← {origin}")
print(f"  → {Batch.search_count([('picking_ids.franchise_id', '=', franchise.id)])} chuyến")

env.cr.commit()
print("\n=== SEED D5 XONG ===")

# ---------------------------------------------------- [6] D5g — công nợ 2 trang
# Bảng PC lọc theo TUẦN, nên rải hoá đơn "đủ mốc" vào đúng tuần portal mở sẵn;
# thêm ở tuần khác thì bảng vẫn ra 1 dòng (docs/d5g-acceptance-matrix.md §1).
print(f"\n[6] Công nợ — hoá đơn trong tuần mặc định + thanh toán đã đối soát (D5g)")
N_WEEK_INVOICE = 11   # > page_size 10 ⇒ pager PC thật sự có 2 trang
N_PAYMENT = 11        # ⇒ /portal/debt/payment-history cũng 2 trang

Debt = env['wujia.portal.debt']
opt, _options = Debt._resolve_week(None, franchise_id=franchise.id)
monday = opt['monday']
print(f"  tuần mặc định: {opt['key']} ({monday} → {monday + timedelta(days=6)})")

have_week = env['account.move'].search_count([
    ('franchise_id', '=', franchise.id), ('move_type', '=', 'out_invoice'),
    ('state', '=', 'posted'),
    ('invoice_date', '>=', monday), ('invoice_date', '<=', monday + timedelta(days=6))])
print(f"  hiện {have_week} hoá đơn trong tuần, cần {N_WEEK_INVOICE}")
for i in range(max(0, N_WEEK_INVOICE - have_week)):
    ref = f'{MARK}G-INVW-{i + 1:03d}'
    if env['account.move'].search_count([('ref', '=', ref)]):
        continue
    inv_date = monday + timedelta(days=i % 7)
    move = env['account.move'].create({
        'move_type': 'out_invoice',
        'partner_id': partner.id,
        'invoice_date': inv_date,
        'journal_id': journal.id,
        'franchise_id': franchise.id,
        'ref': ref,
        'invoice_payment_term_id': False,
        'invoice_line_ids': [(0, 0, {
            'name': f'Nguyên liệu tuần {opt["key"]} đợt {i + 1}',
            'quantity': 1,
            'price_unit': 900000.0 + i * 150000,
            'account_id': income.id,
            'tax_ids': [(6, 0, [])],
        })],
    })
    move.action_post()
    move.invoice_date_due = inv_date + timedelta(days=3 if i % 2 else 30)
    print(f"  [CREATE] invoice tuần {ref} ({inv_date})")

# Thanh toán: KHÔNG ghi tay franchise_id (stored compute từ reconciled_invoice_ids,
# wujia_account/models/account_payment.py:19) — đối soát thật qua wizard register.
# Đối soát vào hoá đơn CŨ ngoài cửa sổ 6 tuần để không đổi tuần mặc định.
have_pay = env['account.payment'].search_count([('franchise_id', '=', franchise.id)])
print(f"  hiện {have_pay} thanh toán, cần {N_PAYMENT}")
old_invoices = env['account.move'].search([
    ('franchise_id', '=', franchise.id), ('move_type', '=', 'out_invoice'),
    ('state', '=', 'posted'), ('invoice_date', '<', monday),
    ('amount_residual', '>', 0),
], order='invoice_date')
bank_journal = env['account.journal'].search(
    [('type', '=', 'bank'), ('company_id', '=', env.company.id)], limit=1)
if not (old_invoices and bank_journal):
    print(f"  ! bỏ qua: old_invoices={len(old_invoices)} bank_journal={bank_journal.id if bank_journal else 0}")
else:
    made = 0
    for i in range(max(0, N_PAYMENT - have_pay)):
        memo = f'{MARK}G-PAY-{i + 1:03d}'
        if env['account.payment'].search_count([('memo', '=', memo)]):
            continue
        inv = old_invoices[i % len(old_invoices)]
        if inv.amount_residual <= 0:
            continue
        amount = min(500000.0, inv.amount_residual)
        wiz = env['account.payment.register'].with_context(
            active_model='account.move', active_ids=inv.ids).create({
                'amount': amount,
                # Tháng HIỆN TẠI: get_payments mặc định lọc theo tháng (wujia_portal_debt.py:323).
                'payment_date': today.replace(day=1) + timedelta(days=i % today.day),
                'journal_id': bank_journal.id,
                'communication': memo,
            })
        wiz.action_create_payments()
        pay = env['account.payment'].search([('memo', '=', memo)], limit=1)
        if pay:
            made += 1
            print(f"  [CREATE] payment {pay.name} ({pay.state}) ← {inv.name}"
                  f" franchise_id={pay.franchise_id.id or 0}")
env.cr.commit()
print(f"  → {env['account.move'].search_count([('franchise_id', '=', franchise.id), ('move_type', '=', 'out_invoice'), ('state', '=', 'posted'), ('invoice_date', '>=', monday), ('invoice_date', '<=', monday + timedelta(days=6))])} hoá đơn trong tuần"
      f" · {env['account.payment'].search_count([('franchise_id', '=', franchise.id)])} thanh toán có franchise_id")
print("\n=== SEED D5G XONG ===")

# ============================================================ [7] D5h — thi
# DB chỉ có 1 khóa thi và mọi kỳ thi của nó đều đã quá ngày ⇒ danh sách khoá thi
# ở /portal/exam/register có 1 item (harness bỏ qua) và mọi guard tự chứng minh
# rỗng. Đi qua cơ chế nghiệp vụ: 'closed' là KẾT QUẢ của _course_meta() đọc
# wujia.exam.session, KHÔNG phải cờ ghi tay (bài học D5g #5).
N_COURSE = 12
N_EXAM_REG = 13     # > PAGE_SIZE 10 ⇒ /portal/exam có 2 trang, guard pager thử được

Course = env['wujia.exam.course']
Session = env['wujia.exam.session']
slots = env['wujia.exam.time.slot'].search([], order='id')
before_course = Course.search_count([])
before_session = Session.search_count([])
before_reg = env['wujia.exam.registration'].search_count([])
print(f"\n[7] Khóa thi — hiện {before_course} khóa / {before_session} kỳ thi")
if not slots:
    print("  ! không có ca thi nào, bỏ qua")
else:
    for i in range(N_COURSE):
        cname = f'{MARK}H Khóa thi số {i + 1:02d}'
        course = Course.search([('name', '=', cname)], limit=1)
        if not course:
            course = Course.create({
                'name': cname,
                'registration_horizon_days': 60,
                'max_participants_per_registration': 4,
                # action_publish() đòi >=1 ca thi ⇒ gán ngay lúc tạo.
                'time_slot_ids': [(6, 0, slots.ids)],
            })
            course.action_publish()
            print(f"  [CREATE] course {course.code} {cname} ({course.state})")
        # 8 khóa có kỳ thi mở trong tương lai ⇒ 'Còn lịch'; 1 khóa mở nhưng hết
        # chỗ ⇒ 'Hết chỗ'; 3 khóa không có kỳ nào sắp tới ⇒ 'Đã đóng' (is-closed).
        if i >= N_COURSE - 3:
            continue
        sname_date = today + timedelta(days=10 + i)
        if Session.search_count([('course_id', '=', course.id),
                                 ('exam_date', '=', sname_date)]):
            continue
        sess = Session.create({
            'course_id': course.id,
            'exam_date': sname_date,
            'time_slot_id': slots[i % len(slots)].id,
            'location': f'Trung tâm đào tạo Wujia — phòng {i + 1}',
            'capacity': 1 if i == N_COURSE - 4 else 40,
            'registration_deadline': datetime.combine(
                sname_date - timedelta(days=1), datetime.min.time()),
        })
        sess.action_open()
        print(f"  [CREATE] session {sess.name} {sname_date} state={sess.state}"
              f" capacity={sess.capacity}")
env.cr.commit()

# Phiếu đăng ký cho franchise 1: create(state='submitted') đi qua
# _check_booking_allowed + _lock_and_check_capacity, không bơm thẳng DB.
print(f"\n[8] Phiếu đăng ký thi — hiện"
      f" {env['wujia.exam.registration'].search_count([('franchise_id', '=', franchise.id)])}"
      f" cho franchise {franchise.id}, cần {N_EXAM_REG}")
open_sessions = Session.search([
    ('state', '=', 'open'), ('exam_date', '>=', today),
    ('available_participant_count', '>', 4),
], order='exam_date')
Reg = env['wujia.exam.registration']
if not open_sessions:
    print("  ! không có kỳ thi mở còn chỗ, bỏ qua")
else:
    have_reg = Reg.search_count([('franchise_id', '=', franchise.id)])
    for i in range(max(0, N_EXAM_REG - have_reg)):
        note = f'{MARK}H-REG-{i + 1:03d}'
        if Reg.search_count([('note', '=', note)]):
            continue
        sess = open_sessions[i % len(open_sessions)]
        # Đúng đường của controller portal (portal.py:472): sudo() + gán
        # requester_user_id tay — portal user không đọc được ir.sequence.
        reg = Reg.sudo().create({
            'session_id': sess.id,
            'franchise_id': franchise.id,
            'requester_user_id': owner_user.id,
            'member_id': member.id if member else False,
            'note': note,
            'state': 'submitted',
            'line_ids': [(0, 0, {
                'employee_name': f'Nhân sự dự thi {i + 1:02d}-{j + 1}',
                'phone': '09%08d' % (10000000 + i * 10 + j),
                'birth_year': 1995 + (i + j) % 8,
                'job_position': ['Pha chế', 'Thu ngân', 'Quản lý ca'][(i + j) % 3],
            }) for j in range(1 + i % 3)],
        })
        if i % 3 == 0:
            reg.action_confirm()
        print(f"  [CREATE] reg {reg.name} state={reg.state}"
              f" lines={len(reg.line_ids)} session={sess.name}")
env.cr.commit()
print(f"  → khóa thi {Course.search_count([])} (trước {before_course})"
      f" · kỳ thi {Session.search_count([])} (trước {before_session})"
      f" · phiếu {Reg.search_count([])} (trước {before_reg})"
      f" · phiếu franchise {franchise.id}:"
      f" {Reg.search_count([('franchise_id', '=', franchise.id)])}")

# ================================================ [9] D5h — yêu cầu cập nhật TT
# /portal/info-request đang 0 bản ghi ⇒ chỉ đo được empty state. PAGE_SIZE=20 nên
# cần > 20 để pager (đã guard page_count>1 sẵn) thật sự hiện.
N_INFO_REQ = 24
Info = env['wujia.info.update.request']
before_info = Info.search_count([])
print(f"\n[9] Yêu cầu cập nhật thông tin — hiện {before_info}, cần {N_INFO_REQ}")
info_types = ['address', 'phone', 'email', 'owner_name', 'bank_info',
              'representative', 'other']
for i in range(max(0, N_INFO_REQ - before_info)):
    note = f'{MARK}H-INFO-{i + 1:03d}'
    if Info.search_count([('note', '=', note)]):
        continue
    rtype = info_types[i % len(info_types)]
    rec = Info.sudo().create({
        'created_by_user_id': owner_user.id,
        'franchise_id': franchise.id,
        'request_type': rtype,
        'field_target': 'other_field' if rtype == 'other' else False,
        'new_value': f'Giá trị mới đợt {i + 1:02d} — {rtype}',
        'note': note,
        'priority': 'urgent' if i % 4 == 0 else 'normal',
    })
    rec.action_submit()
    # Trải đủ 5 trạng thái để badge trong bảng không đơn điệu (acceptance #7).
    if i % 5 == 2:
        rec.action_start_review()
    elif i % 5 == 3:
        rec.action_approve()
    elif i % 5 == 4:
        rec.action_reject()
    print(f"  [CREATE] info-request {rec.name} {rtype} state={rec.state}")
env.cr.commit()
print(f"  → yêu cầu {Info.search_count([])} (trước {before_info})"
      f" · của franchise {franchise.id}:"
      f" {Info.search_count([('franchise_id', '=', franchise.id)])}")
print("\n=== SEED D5H XONG ===")
