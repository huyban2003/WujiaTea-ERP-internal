from odoo import models
from odoo.http import request


class IrHttp(models.AbstractModel):
    _inherit = 'ir.http'

    def get_frontend_session_info(self):
        # Shell portal tự dựng <head> nên phải tự gọi khối session info (WJ-ORD-002,
        # views/layouts.xml). Các route portal là route http thường, không khai báo
        # website=True, nên `request.website` chưa được gán. Khi app Website được cài
        # thêm vào hệ thống, bản mở rộng của nó đọc thẳng thuộc tính đó ⇒ AttributeError
        # làm MỌI trang portal trả lỗi 500. Gán sẵn website hiện hành để shell portal
        # chạy được bất kể app Website có mặt hay không.
        if 'website' in self.env:
            if not hasattr(request, 'website'):
                request.website = self.env['website'].get_current_website()
            if not hasattr(request, 'lang'):
                lang = self.env['res.lang']._get_data(code=self.env.user.lang)
                request.lang = lang or self.env['ir.http']._get_default_lang()
        return super().get_frontend_session_info()
