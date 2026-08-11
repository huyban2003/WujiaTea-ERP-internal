from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError

class WujiaSupervisionSchedule(models.Model):
    _name = 'wujia.supervision.schedule'
    _description = 'Lịch giám sát cửa hàng'
    _order = 'date desc'

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Tiêu đề/Mã lịch giám sát (name) đã tồn tại! Không thể đặt trùng lặp.'),
    ]

    def write(self, vals):
        if 'name' in vals and not self.env.su:
            for rec in self:
                if rec.name and vals['name'] != rec.name:
                    raise ValidationError(_("Tiêu đề/Mã lịch giám sát (%s) không thể thay đổi sau khi đã tạo!") % rec.name)
        return super().write(vals)

    @api.model
    def _generate_schedule_name(self, store_id, seq_number=None):
        """
        Hàm sinh đệ quy mã Lịch giám sát dạng 'LGS-[mã cửa hàng]-[stt 4 chữ số]'.
        """
        if not store_id:
            return 'LGS-STORE-0001'
        store = store_id if isinstance(store_id, models.Model) else self.env['wujia.franchise.management'].browse(store_id)
        if not store.exists():
            return 'LGS-STORE-0001'

        store_code = (store.code or store.name or 'STORE').strip().replace(' ', '_')

        if seq_number is None:
            seq_number = self.search_count([('store_id', '=', store.id)]) + 1

        candidate_name = f"LGS-{store_code}-{seq_number:04d}"

        if self.search_count([('name', '=', candidate_name)]):
            return self._generate_schedule_name(store, seq_number=seq_number + 1)

        return candidate_name

    @api.onchange('store_id')
    def _onchange_store_id_set_name(self):
        if self.store_id:
            if not self.name or self.name.startswith('LGS-') or self.name.startswith('PSG-') or self.name.startswith('Lịch giám sát') or self.name == 'New':
                self.name = self._generate_schedule_name(self.store_id)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            store_id = vals.get('store_id')
            current_name = vals.get('name')
            if not current_name or current_name == 'New' or current_name.startswith('Lịch giám sát') or not current_name.startswith('LGS-'):
                if store_id:
                    vals['name'] = self._generate_schedule_name(store_id)
                elif not current_name:
                    count = self.search_count([]) + 1
                    vals['name'] = f"LGS-STORE-{count:04d}"
        return super(WujiaSupervisionSchedule, self).create(vals_list)

    name = fields.Char(string='Tiêu đề', required=True, copy=False)
    
    # Liên kết với Cửa hàng
    store_id = fields.Many2one('wujia.franchise.management', string='Cửa hàng', required=True)
    
    # Nhân viên thực hiện giám sát
    user_id = fields.Many2one(
        'res.users', 
        string='Nhân viên giám sát', 
        default=lambda self: self.env.user
    )
    
    # Thời gian giám sát
    date = fields.Date(string='Thời gian giám sát', required=True)
    
    # Trạng thái lịch
    state = fields.Selection([
        ('draft', 'Nháp'),
        ('in_progress', 'Đang thực hiện'),
        ('need_remediation', 'Cần khắc phục'),
        ('done', 'Hoàn thành'),
        ('cancel', 'Đã hủy')
    ], string='Trạng thái', default='draft')

    note = fields.Text(string='Ghi chú')

    inspection_id = fields.Many2one(
        'wujia.franchise.inspection',
        string='Phiếu khảo sát',
        compute='_compute_inspection_info',
    )
    inspection_count = fields.Integer(
        string='Số phiếu khảo sát',
        compute='_compute_inspection_info',
    )

    latest_inspection_id = fields.Many2one(
        'wujia.franchise.inspection',
        string='Phiếu khảo sát mới nhất',
        compute='_compute_latest_inspection_info',
    )
    latest_total_score = fields.Float(
        string='Điểm mới nhất',
        compute='_compute_latest_inspection_info',
    )
    latest_grade_id = fields.Many2one(
        'wujia.franchise.inspection.grade',
        string='Loại đánh giá mới nhất',
        compute='_compute_latest_inspection_info',
    )

    def _compute_inspection_info(self):
        if not self:
            return
        groups = self.env['wujia.franchise.inspection']._read_group(
            domain=[('schedule_id', 'in', self.ids)],
            groupby=['schedule_id'],
            aggregates=['id:max'],
        )
        latest_ids = [max_id for schedule, max_id in groups if max_id]
        inspections = self.env['wujia.franchise.inspection'].browse(latest_ids)
        insp_by_schedule = {insp.schedule_id.id: insp for insp in inspections}

        for record in self:
            insp = insp_by_schedule.get(record.id)
            record.inspection_id = insp
            record.inspection_count = 1 if insp else 0

    @api.depends('store_id')
    def _compute_latest_inspection_info(self):
        if not self:
            return
        store_ids = [s.id for s in self.mapped('store_id') if s]
        if store_ids:
            groups = self.env['wujia.franchise.inspection']._read_group(
                domain=[
                    ('franchise_id', 'in', store_ids),
                    ('state', '=', 'done'),
                ],
                groupby=['franchise_id'],
                aggregates=['id:max'],
            )
            latest_ids = [max_id for store, max_id in groups if max_id]
            inspections = self.env['wujia.franchise.inspection'].browse(latest_ids)
            latest_by_store = {insp.franchise_id.id: insp for insp in inspections}
        else:
            latest_by_store = {}

        for record in self:
            latest = latest_by_store.get(record.store_id.id) if record.store_id else False
            record.latest_inspection_id = latest
            record.latest_total_score = latest.total_score if latest else 0.0
            record.latest_grade_id = latest.grade_id if latest else False

    def action_view_inspections(self):
        self.ensure_one()
        inspection = self.env['wujia.franchise.inspection'].search([('schedule_id', '=', self.id)], limit=1)
        if inspection:
            return {
                'name': 'Phiếu khảo sát',
                'type': 'ir.actions.act_window',
                'res_model': 'wujia.franchise.inspection',
                'view_mode': 'form',
                'res_id': inspection.id,
                'target': 'current',
            }
        return {
            'name': 'Tạo phiếu khảo sát',
            'type': 'ir.actions.act_window',
            'res_model': 'wujia.franchise.inspection',
            'view_mode': 'form',
            'context': {
                'default_schedule_id': self.id,
                'default_name': self.name.replace('LGS-', 'PSG-', 1) if self.name else False,
                'default_planned_date': self.date,
                'default_franchise_id': self.store_id.id if self.store_id else False,
                'default_inspector_user_id': self.user_id.id if self.user_id else False,
            },
            'target': 'current',
        }


    # =========================================================================
    # HÀM ONCHANGE: TỰ ĐỘNG RESET VÀ LỌC LẠI DANH SÁCH CỬA HÀNG KHI ĐỔI USER
    # =========================================================================
    @api.onchange('user_id')
    def _onchange_user_id(self):
        """
        Sự kiện chạy khi người dùng thay đổi Nhân viên giám sát trên Form View:
        - Tự động xóa Cửa hàng đang chọn (nếu có).
        - Trả về bộ lọc (domain) để danh sách Cửa hàng chỉ hiện các cửa hàng của user_id mới.
        """
        self.store_id = None

        if self.user_id:
            domain = [('effective_supervision_user_id', '=', self.user_id.id)]
        else:
            domain = [('id', '=', False)]

        # Trả về cả value (để xoá giao diện) lẫn domain (để lọc danh sách)
        return {
            'value': {
                'store_id': False
            },
            'domain': {
                'store_id': domain
            }
        }