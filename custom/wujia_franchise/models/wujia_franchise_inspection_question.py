# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class WujiaFranchiseInspectionQuestion(models.Model):
    _name = 'wujia.franchise.inspection.question'
    _description = 'Thư viện câu hỏi kiểm tra khảo sát'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'
    _rec_name = 'question_text'

    code = fields.Char(string='Mã câu hỏi', tracking=True)
    question_text = fields.Text(
        string='Nội dung câu hỏi',
        required=True,
        tracking=True,
        help='Nội dung câu hỏi. Dùng ký tự ____ đại diện cho vị trí chỗ trống cần điền.'
    )
    score = fields.Float(string='Điểm số', default=1.0, tracking=True, help='Điểm số đạt được khi trả lời đúng câu hỏi này')
    
    # Mảng JSON lưu trữ mảng đáp án đúng tương ứng với các ô trống (Dùng default=False để tránh Odoo gọi list(self))
    correct_answers = fields.Json(
        string='Mảng đáp án đúng (JSON)',
        default=False,
        help='Mảng JSON chứa đáp án cho từng vị trí trống ____. Ví dụ: [["500", "500ml"], ["10", "10 phút"]]'
    )
    
    # Giao diện nhập liệu thân thiện cho người dùng
    correct_answers_text = fields.Text(
        string='Đáp án đúng (Mỗi vị trí trống 1 dòng)',
        compute='_compute_correct_answers_text',
        inverse='_inverse_correct_answers_text',
        store=False,
        help='Nhập đáp án đúng cho từng chỗ trống ____.\n'
             '- Chỗ trống 1: Nhập ở Dòng 1.\n'
             '- Chỗ trống 2: Nhập ở Dòng 2.\n'
             '- Nếu 1 chỗ trống có nhiều đáp án chấp nhận được, phân cách nhau bằng dấu phẩy (,).'
    )
    
    active = fields.Boolean(string='Kích hoạt', default=True, tracking=True)

    @api.depends('code', 'question_text')
    def _compute_display_name(self):
        """Hàm tính toán tên hiển thị ngắn gọn cho bản ghi"""
        for rec in self:
            if rec.code and rec.question_text:
                short_text = rec.question_text[:40] + ('...' if len(rec.question_text) > 40 else '')
                rec.display_name = f"[{rec.code}] {short_text}"
            elif rec.question_text:
                rec.display_name = rec.question_text[:50]
            elif rec.code:
                rec.display_name = rec.code
            else:
                rec.display_name = "Câu hỏi mới"

    @api.depends('correct_answers')
    def _compute_correct_answers_text(self):
        """
        Hàm tự động chuyển dữ liệu JSON từ correct_answers
        thành chuỗi văn bản nhiều dòng để hiển thị ra giao diện.
        """
        for rec in self:
            val = rec.correct_answers
            if isinstance(val, list):
                formatted_lines = []
                for item in val:
                    if isinstance(item, models.BaseModel):
                        continue
                    if isinstance(item, list):
                        clean_items = [
                            str(x) for x in item
                            if x is not None and not isinstance(x, models.BaseModel) and isinstance(x, (str, int, float))
                        ]
                        if clean_items:
                            formatted_lines.append(', '.join(clean_items))
                    elif isinstance(item, (str, int, float)) and item:
                        formatted_lines.append(str(item))
                rec.correct_answers_text = '\n'.join(formatted_lines)
            else:
                rec.correct_answers_text = False

    def _inverse_correct_answers_text(self):
        """
        Hàm xử lý khi người dùng nhập văn bản vào correct_answers_text trên giao diện:
        Phân tách từng dòng văn bản và lưu ngược lại vào trường correct_answers (JSON) trong CSDL.
        """
        for rec in self:
            if rec.correct_answers_text:
                result_list = []
                for line in rec.correct_answers_text.splitlines():
                    line_clean = line.strip()
                    if not line_clean:
                        continue
                    if ',' in line_clean:
                        parts = [p.strip() for p in line_clean.split(',') if p.strip()]
                        result_list.append(parts)
                    else:
                        result_list.append(line_clean)
                rec.correct_answers = result_list
            else:
                rec.correct_answers = False

    def action_save(self):
        """Lưu bản ghi câu hỏi"""
        self.ensure_one()
        return True
