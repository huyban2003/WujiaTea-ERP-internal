from odoo import models, fields, api

class WujiaSupervisionSchedule(models.Model):
    _name = 'wujia.supervision.schedule'
    _description = 'Lịch giám sát cửa hàng'
    _order = 'date desc'

    name = fields.Char(string='Tiêu đề', required=True)
    
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
                    ('state', '!=', 'cancel'),
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
                'default_name': f"Khảo sát: {self.name}",
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