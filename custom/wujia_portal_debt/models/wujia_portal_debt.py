"""Nguồn dữ liệu DUY NHẤT của module Công nợ portal.

`AbstractModel` — không bảng, không migration. Toàn bộ controller + 2 template
inherit (badge sheet "Thêm", KPI Home) đều lấy số qua `get_summary()` /
`get_payments()`, nên khi BA chốt spec backend (`account.move` ↔ franchise) thì
chỉ đổi phần dựng dict trong file này, template không đụng một dòng.

⚠️ UI-ONLY (chốt 2026-07-31) — hiện trả dict thuần Python, **0 query**:
  * Tab `1. Model/ Field` mục "D. Quản lý công nợ nhượng quyền" mới là tiêu đề rỗng.
  * DB chưa có field nối `account.move`/`account.payment` ↔ franchise.
  * Figma tự ghi "QR minh họa", "Vietcombank (minh họa)".

⚠️ RÀNG BUỘC PERF cho lúc wire thật (§7 perf-first, 1500 portal user): badge
"n quá hạn" nằm trong sheet "Thêm" của shell ⇒ **mọi trang mobile** gọi
`get_summary()`. Lúc đó số quá hạn phải là field store + index / ormcache /
cron daily — TUYỆT ĐỐI không `search_count` on-the-fly mỗi request.
"""

from datetime import date, timedelta

from odoo import api, models

# Số tuần / kỳ đổ vào dropdown bộ lọc (kỳ hiện tại + 5 kỳ trước).
WEEK_CHOICES = 6
MONTH_CHOICES = 6

# Mặc định hiển thị 2 hoá đơn, phần còn lại bung bằng `?all=1` (Figma: "Hiển thị 2/4 hóa đơn").
INVOICE_PREVIEW = 2

# UI-only demo: tuần thứ n (0 = tuần hiện tại) rơi vào biến thể nào của Figma.
# Đủ 4 state để QA/BA click qua lại được cả 4 màn 02-05 mà không cần seed data.
DEMO_STATE_BY_OFFSET = ('outstanding', 'partial', 'paid', 'paid', 'empty', 'empty')

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


def _short_vnd(amount):
    """Tiền rút gọn cho tile KPI Home (ô hẹp, 4 tile/hàng): 12.650.000 → '12,7tr'."""
    amount = amount or 0
    if amount >= 1000000:
        return ('%.1f' % (amount / 1000000.0)).replace('.', ',').replace(',0', '') + 'tr'
    if amount >= 1000:
        return '%dk' % (amount // 1000)
    return '%d ₫' % amount


def _week_label(monday):
    """Nhãn Figma: '08/07 – 14/07/2026'."""
    sunday = monday + timedelta(days=6)
    return '%s – %s' % (monday.strftime('%d/%m'), sunday.strftime('%d/%m/%Y'))


class WujiaPortalDebt(models.AbstractModel):
    _name = 'wujia.portal.debt'
    _description = 'Wujia Portal — nguồn dữ liệu Công nợ & thanh toán'

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

    # ------------------------------------------------------------------
    # Summary — điểm nối duy nhất giữa UI và (sau này) backend kế toán
    # ------------------------------------------------------------------
    @api.model
    def get_summary(self, franchise_id, week=None, today=None):
        """Số liệu công nợ của 1 cửa hàng trong 1 tuần.

        :param franchise_id: id `wujia.franchise.management` (0/False = chưa chọn cửa hàng)
        :param week: khoá tuần 'YYYY-Www'; sai hoặc None → tuần hiện tại
        :return: dict — xem docstring module. Luôn đủ key kể cả state 'empty',
                 để template không phải `.get()` phòng thủ.
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
        base.update(self._demo_payload(DEMO_STATE_BY_OFFSET[opt['offset']], monday))
        return base

    @api.model
    def get_shell_badge(self):
        """Số liệu cho 2 điểm vào ở shell: badge sheet "Thêm" + tile KPI Home.

        Tự resolve cửa hàng đang chọn (template không có sẵn franchise_id).

        ⚠️ Gọi trên MỌI trang mobile — xem cảnh báo perf ở đầu file trước khi
        thay bằng query thật."""
        try:
            from odoo.addons.wujia_portal_base.controllers.portal import (
                get_active_franchise_id,
            )
            franchise_id = get_active_franchise_id()
        except Exception:  # noqa: BLE001 — render backend/cron: không có request
            franchise_id = False
        summary = self.get_summary(franchise_id)
        return {
            'overdue_count': summary['overdue_count'],
            'remaining': summary['remaining'],
            'remaining_label': _short_vnd(summary['remaining']),
        }

    # ------------------------------------------------------------------
    # Kỳ thanh toán (màn 06)
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
        """Lịch sử thanh toán đã xác nhận trong 1 kỳ (Figma màn 06).

        Ưu tiên `month` (dropdown). `date_from`/`date_to` vẫn nhận được để BA/FE
        gọi khoảng tuỳ ý sau này. Mặc định = tháng hiện tại."""
        opt, options = self._resolve_month(month, today=today)
        date_from = date_from or opt['date_from']
        date_to = date_to or opt['date_to']
        if date_from > date_to:
            date_from, date_to = date_to, date_from
        payments = self._demo_payments(franchise_id, date_to) if franchise_id else []
        payments = [p for p in payments if date_from <= p['date'] <= date_to]
        return {
            'month_key': opt['key'],
            'months': [{'key': m['key'], 'label': m['label']} for m in options],
            'date_from': date_from,
            'date_to': date_to,
            'range_label': '%s – %s' % (
                date_from.strftime('%d/%m'), date_to.strftime('%d/%m/%Y')),
            'payments': payments,
            'total': sum(p['amount'] for p in payments),
        }

    @api.model
    def get_bank_info(self, franchise_id, amount, week_number):
        """Thông tin chuyển khoản (Figma màn 07).

        UI-only: BA chưa chốt "QR tĩnh hay QR động" (tab `3. Controller`, CT-05x),
        nên hardcode đúng chuỗi Figma và giữ chữ "(minh họa)"."""
        return {
            'name': 'Vietcombank (minh họa)',
            'holder': 'CÔNG TY TNHH NGÔ GIA',
            'account': '0123 456 789',
            'memo': '%s K%s %s' % (
                self._franchise_code(franchise_id), week_number, int(amount)),
        }

    # ------------------------------------------------------------------
    # Nội bộ — phần sẽ bị thay khi wire backend thật
    # ------------------------------------------------------------------
    @api.model
    def _franchise_code(self, franchise_id):
        if not franchise_id:
            return 'H000'
        franchise = self.env['wujia.franchise.management'].browse(franchise_id)
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
        }

    @api.model
    def _demo_payload(self, state, monday):
        """Số liệu minh hoạ đúng bằng con số trên Figma, ngày suy từ đầu tuần đang xem."""
        if state == 'empty':
            return self._empty_payload()

        def day(offset):
            return monday + timedelta(days=offset)

        def ref(offset, seq):
            return 'INV/%s/%s/%s' % (monday.strftime('%Y'), day(offset).strftime('%d%m'), seq)

        if state == 'outstanding':
            invoices = [
                (ref(2, '018'), day(2), day(4), 'overdue', 3400000),
                (ref(3, '026'), day(3), day(10), 'unpaid', 5250000),
                (ref(4, '033'), day(4), day(11), 'unpaid', 2400000),
                (ref(5, '041'), day(5), day(12), 'unpaid', 1600000),
            ]
            payload = {
                'state': 'outstanding',
                'total': 14850000,
                'paid': 2200000,
                'has_overdue': True,
                'overdue_count': 1,
                'nearest_due': day(8),
                'confirmed_date': False,
            }
        elif state == 'partial':
            invoices = [
                (ref(3, '026'), day(3), day(10), 'partial', 5250000),
                (ref(4, '033'), day(4), day(11), 'partial', 2400000),
            ]
            payload = {
                'state': 'partial',
                'total': 12650000,
                'paid': 5000000,
                'has_overdue': False,
                'overdue_count': 0,
                'nearest_due': False,
                'confirmed_date': False,
            }
        else:  # paid
            invoices = [
                (ref(2, '018'), day(2), day(4), 'paid', 3400000),
                (ref(3, '026'), day(3), day(10), 'paid', 5250000),
                (ref(4, '033'), day(4), day(11), 'paid', 4000000),
            ]
            payload = {
                'state': 'paid',
                'total': 12650000,
                'paid': 12650000,
                'has_overdue': False,
                'overdue_count': 0,
                'nearest_due': False,
                'confirmed_date': day(7),
            }
        payload['invoices'] = [
            {'name': name, 'date': inv_date, 'due': due, 'status': status, 'amount': amount}
            for name, inv_date, due, status, amount in invoices
        ]
        payload['invoice_count'] = len(payload['invoices'])
        payload['remaining'] = payload['total'] - payload['paid']
        return payload

    @api.model
    def _demo_payments(self, franchise_id, date_to):
        """3 giao dịch đã xác nhận (Figma 06). Ngày lùi từ cuối kỳ để luôn nằm trong khoảng."""
        code = self._franchise_code(franchise_id)
        rows = [(17, '16:40', '03', 5000000), (19, '14:25', '01', 4150000),
                (22, '09:10', '02', 3500000)]
        payments = []
        for back, hhmm, seq, amount in rows:
            when = date_to - timedelta(days=back)
            payments.append({
                'ref': 'TT-%s-%s' % (when.strftime('%d%m%Y'), seq),
                'date': when,
                'time': hhmm,
                'method': 'Chuyển khoản',
                'trace': '%s-K%s-%s' % (code, when.isocalendar()[1], seq),
                'amount': amount,
                'state': 'confirmed',
            })
        return payments
