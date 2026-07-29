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
        ('draft', 'Đang chờ'),
        ('in_progress', 'Đang thực hiện'),
        ('done', 'Hoàn thành'),
        ('cancel', 'Đã hủy')
    ], string='Trạng thái', default='draft')

    note = fields.Text(string='Ghi chú')

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