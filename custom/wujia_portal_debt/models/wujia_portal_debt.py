"""Nguồn dữ liệu DUY NHẤT của module Công nợ portal.

`AbstractModel` — không bảng, không migration. Toàn bộ controller + 2 template
inherit (badge sheet "Thêm", KPI Home) đều lấy số qua `get_summary()` /
`get_payments()` / `get_bank_info()` / `get_shell_badge()`, nên khi wire backend thật
chỉ đổi phần dựng dict trong file này, template KHÔNG đụng một dòng.

**Wire backend thật — Sprint 48 (BA task Tasks!STT9, Controller CT-050..CT-055):**
Đọc `account.move` (out_invoice/out_refund) + `account.payment` scope theo
`franchise_id` (3 field custom ở module `wujia_account`). Mọi query bằng `sudo()` +
domain franchise tường minh — portal user KHÔNG có ACL account, và KHÔNG tin store do
client truyền (controller resolve franchise từ session).

⚠️ PERF 1500 user: `get_shell_badge()` chạy trên MỌI trang mobile ⇒ đọc thẳng 2 field
store `portal_overdue_invoice_count` / `portal_debt_remaining` trên franchise (0 query;
cập nhật bằng cron daily + hook ở `wujia_account`). TUYỆT ĐỐI không search on-the-fly ở đây.

Kiểu dữ liệu template phụ thuộc (giữ nguyên): `date`/`due`/`nearest_due`/`confirmed_date`
là `datetime.date` (template gọi `.strftime`); `status` ∈ overdue/unpaid/partial/paid;
`state` ∈ outstanding/partial/paid/empty.
"""

from datetime import date, timedelta

from odoo import api, fields, models

# Số tuần / kỳ đổ vào dropdown bộ lọc (kỳ hiện tại + 5 kỳ trước).
WEEK_CHOICES = 6
MONTH_CHOICES = 6

# Mặc định hiển thị 2 hoá đơn, phần còn lại bung bằng `?all=1` (Figma: "Hiển thị 2/4 hóa đơn").
INVOICE_PREVIEW = 2

# Nhãn + tone badge cho state tổng (Figma 02/03/04).
STATE_BADGE = {
    'outstanding': ('Có quá hạn', 'danger'),
    'partial': ('Thanh toán một phần', 'info'),
    'paid': ('Đã thanh toán', 'success'),
}

# Nhãn + tone badge cho từng hoá đơn.
INVOICE_BADGE = {
    'overdue': ('Quá hạn', 'danger'),
    'unpaid': ('Chưa thanh toán', 'warn'),
    'partial': ('Một phần', 'info'),
    'paid': ('Đã thanh toán', 'success'),
}

# Chứng từ công nợ khách hàng của cửa hàng: hoá đơn + credit note đã ghi sổ.
_DEBT_MOVE_TYPES = ('out_invoice', 'out_refund')
# Payment đã xác nhận (Odoo 19): loại draft/canceled/rejected.
_CONFIRMED_PAYMENT_STATES = ('in_process', 'paid')
# payment_state coi như đã tất toán (không còn nợ).
_SETTLED_PAYMENT_STATES = ('paid', 'in_payment', 'reversed')


def _monday(day):
    """Thứ Hai của tuần chứa `day` (ISO: tuần Mon→Sun)."""
    return day - timedelta(days=day.weekday())


def _week_key(monday):
    """Khoá tuần dùng trên URL — ISO 'YYYY-Www', so sánh/parse được, không phụ thuộc locale."""
    iso = monday.isocalendar()
    return '%04d-W%02d' % (iso[0], iso[1])


def _start_of_month(day):
    return day.replace(day=1)


def _end_of_month(day):
    """Ngày cuối tháng chứa `day` (khỏi cần dateutil)."""
    first_next_month = (day.replace(day=28) + timedelta(days=4)).replace(day=1)
    return first_next_month - timedelta(days=1)


def _short_amount(amount, symbol=''):
    """Tiền rút gọn cho tile KPI Home (ô hẹp, 4 tile/hàng): 12.650.000 → '12,7tr'.

    Ký hiệu truyền từ ngoài (currency của công ty), không hardcode '₫' — cùng luật
    với cụm D: portal không được tự quyết đơn vị tiền."""
    amount = amount or 0
    if amount >= 1000000:
        return ('%.1f' % (amount / 1000000.0)).replace('.', ',').replace(',0', '') + 'tr'
    if amount >= 1000:
        return '%dk' % (amount // 1000)
    return ('%d %s' % (amount, symbol)).strip()


def _week_label(monday):
    """Nhãn Figma: '08/07 – 14/07/2026'."""
    sunday = monday + timedelta(days=6)
    return '%s – %s' % (monday.strftime('%d/%m'), sunday.strftime('%d/%m/%Y'))


class WujiaPortalDebt(models.AbstractModel):
    _name = 'wujia.portal.debt'
    _description = 'Wujia Portal — debt & payment data source'

    # ------------------------------------------------------------------
    # Tuần
    # ------------------------------------------------------------------
    @api.model
    def _week_options(self, today=None):
        """Danh sách tuần cho dropdown, mới nhất trước."""
        today = today or date.today()
        first = _monday(today)
        return [
            {
                'key': _week_key(first - timedelta(weeks=i)),
                'label': _week_label(first - timedelta(weeks=i)),
                'monday': first - timedelta(weeks=i),
                'offset': i,
            }
            for i in range(WEEK_CHOICES)
        ]

    @api.model
    def _resolve_week(self, week=None, today=None):
        """`?week=` → option tương ứng. Sai/thiếu/không thuộc danh sách → tuần hiện tại.

        Không bao giờ raise: bộ lọc là query param người dùng sửa được tay."""
        options = self._week_options(today=today)
        if week:
            for opt in options:
                if opt['key'] == week:
                    return opt, options
        return options[0], options

    @api.model
    def _currency_decimals(self, moves=None):
        """Số chữ số thập phân của currency công nợ — đi cặp với `_currency_symbol`."""
        if moves:
            currencies = moves.mapped('currency_id')
            if len(currencies) == 1:
                return currencies.decimal_places or 0
        return self.env.company.currency_id.decimal_places or 0

    @api.model
    def _currency_symbol(self, moves=None):
        """Ký hiệu tiền của dữ liệu công nợ.

        Hoá đơn cùng một currency → lấy currency đó; rỗng hoặc pha trộn nhiều
        currency → currency công ty (gộp số của nhiều currency vốn đã là chuyện
        khác, không giải ở cụm D)."""
        if moves:
            currencies = moves.mapped('currency_id')
            if len(currencies) == 1:
                return currencies.symbol or ''
        return self.env.company.currency_id.symbol or ''

    # ------------------------------------------------------------------
    # Summary — điểm nối duy nhất giữa UI và backend kế toán (CT-050/051/052)
    # ------------------------------------------------------------------
    @api.model
    def get_summary(self, franchise_id, week=None, today=None):
        """Số liệu công nợ của 1 cửa hàng trong 1 tuần (Mon→Sun theo `invoice_date`).

        :param franchise_id: id `wujia.franchise.management` (0/False = chưa chọn cửa hàng)
        :param week: khoá tuần 'YYYY-Www'; sai hoặc None → tuần hiện tại
        :return: dict — luôn đủ key kể cả state 'empty', để template không phải `.get()`.
        """
        opt, options = self._resolve_week(week, today=today)
        monday = opt['monday']
        base = {
            'franchise_id': franchise_id or False,
            'franchise_code': self._franchise_code(franchise_id),
            'week_key': opt['key'],
            'week_label': opt['label'],
            'week_number': monday.isocalendar()[1],
            'week_short': '%s – %s' % (
                monday.strftime('%d/%m'), (monday + timedelta(days=6)).strftime('%d/%m')),
            'weeks': [{'key': w['key'], 'label': w['label']} for w in options],
        }
        if not franchise_id:
            # Chưa chọn cửa hàng → empty state, KHÔNG 500 (guard controller).
            base.update(self._empty_payload())
            return base
        base.update(self._week_payload(franchise_id, monday, today=today))
        return base

    @api.model
    def get_shell_badge(self):
        """Số liệu cho 2 điểm vào ở shell: badge sheet "Thêm" + tile KPI Home.

        ⚠️ Gọi trên MỌI trang mobile ⇒ đọc thẳng 2 field STORE trên franchise (0 query).
        Nguồn cập nhật: cron daily + hook account.move/account.payment (module wujia_account)."""
        try:
            from odoo.addons.wujia_portal_base.controllers.portal import (
                get_active_franchise_id,
            )
            franchise_id = get_active_franchise_id()
        except Exception:  # noqa: BLE001 — render backend/cron: không có request
            franchise_id = False
        symbol = self.env.company.currency_id.symbol or ''
        if not franchise_id:
            return {'overdue_count': 0, 'remaining': 0,
                    'remaining_label': _short_amount(0, symbol),
                    'currency_symbol': symbol,
                    'currency_decimals': self.env.company.currency_id.decimal_places or 0}
        franchise = self.env['wujia.franchise.management'].sudo().browse(franchise_id).exists()
        remaining = franchise.portal_debt_remaining or 0
        return {
            'overdue_count': franchise.portal_overdue_invoice_count or 0,
            'remaining': remaining,
            'remaining_label': _short_amount(remaining, symbol),
            'currency_symbol': symbol,
            'currency_decimals': self.env.company.currency_id.decimal_places or 0,
        }

    # ------------------------------------------------------------------
    # Kỳ thanh toán (màn 06) — CT-054
    # ------------------------------------------------------------------
    @api.model
    def _month_options(self, today=None):
        """Danh sách kỳ cho dropdown "Thời gian thanh toán", mới nhất trước.

        Figma vẽ 1 dòng "01/07 – 31/07/2026" ⇒ kỳ = trọn tháng (1 control native,
        dùng chung component filter + JS auto-submit với bộ lọc tuần)."""
        first = (today or date.today()).replace(day=1)
        options = []
        for _i in range(MONTH_CHOICES):
            last = _end_of_month(first)
            options.append({
                'key': first.strftime('%Y-%m'),
                'label': '%s – %s' % (first.strftime('%d/%m'), last.strftime('%d/%m/%Y')),
                'date_from': first,
                'date_to': last,
            })
            first = _start_of_month(first - timedelta(days=1))
        return options

    @api.model
    def _resolve_month(self, month=None, today=None):
        """`?month=YYYY-MM` → option. Sai/thiếu → tháng hiện tại. Không bao giờ raise."""
        options = self._month_options(today=today)
        if month:
            for opt in options:
                if opt['key'] == month:
                    return opt, options
        return options[0], options

    @api.model
    def get_payments(self, franchise_id, month=None, date_from=None, date_to=None, today=None):
        """Lịch sử thanh toán đã xác nhận trong 1 kỳ (Figma màn 06, CT-054).

        Ưu tiên `month` (dropdown). `date_from`/`date_to` vẫn nhận được để BA/FE
        gọi khoảng tuỳ ý sau này. Mặc định = tháng hiện tại."""
        opt, options = self._resolve_month(month, today=today)
        date_from = date_from or opt['date_from']
        date_to = date_to or opt['date_to']
        if date_from > date_to:
            date_from, date_to = date_to, date_from
        payments = self._query_payments(franchise_id, date_from, date_to) if franchise_id else []
        return {
            'month_key': opt['key'],
            'months': [{'key': m['key'], 'label': m['label']} for m in options],
            'date_from': date_from,
            'date_to': date_to,
            'range_label': '%s – %s' % (
                date_from.strftime('%d/%m'), date_to.strftime('%d/%m/%Y')),
            'payments': payments,
            'total': sum(p['amount'] for p in payments),
            'currency_symbol': self._currency_symbol(),
            'currency_decimals': self._currency_decimals(),
        }

    @api.model
    def get_bank_info(self, franchise_id, amount, week_number):
        """Thông tin chuyển khoản (Figma màn 07, CT-055).

        Lấy tài khoản nhận tiền của company hiện hành có `portal_payment_enabled=True`,
        sequence nhỏ nhất. Backend tự tính nội dung CK từ mã cửa hàng + tuần + số tiền
        (KHÔNG tin giá trị portal gửi lên). Mở QR chỉ trả hướng dẫn — không tạo payment.

        ⚠️ Ảnh QR (tĩnh/động) BA CHƯA chốt (CT-055 cột ghi chú còn để ngỏ) ⇒ chỉ trả
        STK + nội dung, defer ảnh QR (Need BA Confirm)."""
        bank = self._portal_bank_account()
        if not bank:
            return {
                'name': 'Cửa hàng chưa được cấu hình tài khoản nhận thanh toán. '
                        'Vui lòng liên hệ bộ phận hỗ trợ.',
                'holder': '',
                'account': '',
                'memo': '',
            }
        return {
            'name': bank.bank_id.name or bank.bank_name or 'Ngân hàng',
            'holder': bank.acc_holder_name or bank.partner_id.name or '',
            'account': bank.acc_number or '',
            'memo': '%s K%s %s' % (
                self._franchise_code(franchise_id), week_number, int(amount or 0)),
        }

    # ------------------------------------------------------------------
    # Query backend thật (sudo + scope franchise)
    # ------------------------------------------------------------------
    @api.model
    def _franchise_code(self, franchise_id):
        if not franchise_id:
            return 'H000'
        franchise = self.env['wujia.franchise.management'].sudo().browse(franchise_id)
        return franchise.exists().code or 'H000'

    @api.model
    def _empty_payload(self):
        return {
            'state': 'empty',
            'total': 0,
            'paid': 0,
            'remaining': 0,
            'invoice_count': 0,
            'has_overdue': False,
            'overdue_count': 0,
            'nearest_due': False,
            'confirmed_date': False,
            'invoices': [],
            'currency_symbol': self._currency_symbol(),
            'currency_decimals': self._currency_decimals(),
        }

    @api.model
    def _invoice_status(self, move, today):
        """Trạng thái Portal của 1 chứng từ, suy từ payment_state + số dư + hạn (CT-051).
        Không tạo trạng thái kế toán mới."""
        if move.amount_residual <= 0 or move.payment_state in _SETTLED_PAYMENT_STATES:
            return 'paid'
        if (move.move_type == 'out_invoice' and move.invoice_date_due
                and move.invoice_date_due < today and move.amount_residual > 0):
            return 'overdue'
        if move.payment_state == 'partial':
            return 'partial'
        return 'unpaid'

    @api.model
    def _week_payload(self, franchise_id, monday, today=None):
        """Số liệu 1 tuần từ account.move thật. Credit note (out_refund) giảm công nợ:
        total/paid/remaining là số RÒNG (hoá đơn − credit note)."""
        today = today or date.today()
        sunday = monday + timedelta(days=6)
        moves = self.env['account.move'].sudo().search([
            ('franchise_id', '=', franchise_id),
            ('move_type', 'in', _DEBT_MOVE_TYPES),
            ('state', '=', 'posted'),
            ('invoice_date', '>=', monday),
            ('invoice_date', '<=', sunday),
        ], order='invoice_date, id')
        if not moves:
            return self._empty_payload()

        total = paid = remaining = 0.0
        overdue_count = 0
        due_dates = []
        invoices = []
        for move in moves:
            sign = -1.0 if move.move_type == 'out_refund' else 1.0
            total += sign * move.amount_total
            remaining += sign * move.amount_residual
            status = self._invoice_status(move, today)
            if status == 'overdue':
                overdue_count += 1
                if move.invoice_date_due:
                    due_dates.append(move.invoice_date_due)
            # Số dòng: còn dư → hiển thị số dư; đã tất toán → tổng. Credit note âm.
            line_amount = move.amount_residual if move.amount_residual > 0 else move.amount_total
            invoices.append({
                'name': move.name or move.ref or '—',
                'date': move.invoice_date,
                'due': move.invoice_date_due or move.invoice_date,
                'status': status,
                'amount': sign * line_amount,
            })
        paid = total - remaining

        if remaining <= 0:
            state = 'paid'
        elif overdue_count > 0:
            state = 'outstanding'
        else:
            state = 'partial'

        return {
            'state': state,
            'total': total,
            'paid': paid,
            'remaining': remaining,
            'invoice_count': len(invoices),
            'has_overdue': overdue_count > 0,
            'overdue_count': overdue_count,
            'nearest_due': min(due_dates) if due_dates else False,
            'confirmed_date': self._confirmed_date(moves) if state == 'paid' else False,
            'invoices': invoices,
            'currency_symbol': self._currency_symbol(moves),
            'currency_decimals': self._currency_decimals(moves),
        }

    @api.model
    def _confirmed_date(self, moves):
        """Ngày Ngô Gia xác nhận (state 'paid'): ngày payment đối soát mới nhất của các
        chứng từ trong tuần; fallback ngày hoá đơn mới nhất."""
        payments = moves.reconciled_payment_ids.filtered('date')
        if payments:
            return max(payments.mapped('date'))
        inv_dates = [m.invoice_date for m in moves if m.invoice_date]
        return max(inv_dates) if inv_dates else False

    @api.model
    def _payment_time(self, payment):
        """account.payment.date là Date (không giờ) → lấy giờ từ create_date theo tz user."""
        if not payment.create_date:
            return ''
        local_dt = fields.Datetime.context_timestamp(payment, payment.create_date)
        return local_dt.strftime('%H:%M')

    @api.model
    def _query_payments(self, franchise_id, date_from, date_to):
        """Payment đã xác nhận của cửa hàng trong kỳ (CT-054). Chi ngược (outbound) hiển
        thị số âm để không cộng nhầm vào "đã trả" (BA §6)."""
        payments = self.env['account.payment'].sudo().search([
            ('franchise_id', '=', franchise_id),
            ('state', 'in', _CONFIRMED_PAYMENT_STATES),
            ('date', '>=', date_from),
            ('date', '<=', date_to),
        ], order='date desc, id desc')
        result = []
        for payment in payments:
            sign = -1.0 if payment.payment_type == 'outbound' else 1.0
            result.append({
                'ref': payment.name or '—',
                'date': payment.date,
                'time': self._payment_time(payment),
                'method': payment.journal_id.name or 'Chuyển khoản',
                'trace': payment.memo or payment.name or '',
                'amount': sign * payment.amount,
                'state': 'confirmed',
            })
        return result

    @api.model
    def _portal_bank_account(self):
        """TK nhận tiền của company hiện hành, bật portal, sequence nhỏ nhất (CT-055)."""
        company = self.env.company
        return self.env['res.partner.bank'].sudo().search([
            ('id', 'in', company.bank_ids.ids),
            ('portal_payment_enabled', '=', True),
        ], order='sequence, id', limit=1)
