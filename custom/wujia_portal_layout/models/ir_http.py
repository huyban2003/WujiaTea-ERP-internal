from urllib.parse import urlsplit

from odoo import models
from odoo.http import request


class IrHttp(models.AbstractModel):
    _inherit = 'ir.http'

    def _wj_portal_path(self, url):
        """Chỉ nhận đích điều hướng NỘI BỘ portal (CMP-BPH-001) — chặn open redirect."""
        if not url or not isinstance(url, str) or '\\' in url or url.startswith('//'):
            return False
        # '..' leo ra ngoài /portal sau khi trình duyệt chuẩn hoá (vd /portal/../web)
        if '..' in url.split('?')[0].split('/'):
            return False
        if url == '/portal' or url.startswith('/portal/') or url.startswith('/portal?'):
            return url
        return False

    def _wj_back_url(self, default):
        """URL nút Quay lại: return_url đã validate → Referer trùng list cha (giữ
        filter/page) → fallback list cha. Không query, không history.back()."""
        default = default or '/portal'
        explicit = self._wj_portal_path(request.params.get('return_url'))
        if explicit:
            return explicit
        ref = request.httprequest.referrer
        if ref:
            parts = urlsplit(ref)
            if parts.netloc == request.httprequest.host and parts.path == urlsplit(default).path:
                back = parts.path + (('?' + parts.query) if parts.query else '')
                return self._wj_portal_path(back) or default
        return default

    def _wj_portal_langs(self):
        """Ngôn ngữ cho bộ chọn của portal — nguồn duy nhất, gọi từ QWeb.

        Đọc ngôn ngữ ĐANG BẬT (Settings → Languages); bật thêm ngôn ngữ nào là
        portal có ngay mục đó, không sửa code (WJ-LANG-001). `_get_active_by` đã
        được Odoo ormcache ⇒ 0 query/trang.
        """
        current = self.env.lang
        langs = []
        for code, data in self.env['res.lang'].sudo()._get_active_by('code').items():
            # 'Vietnamese / Tiếng Việt' → tên bản địa; không có '/' thì giữ nguyên.
            label = data.name.split(' / ')[-1].strip() or data.name
            langs.append({
                'code': code,
                'url_code': data.url_code,
                'label': label,
                'flag': 'flag-icon-%s' % code.split('_')[-1].split('@')[0].lower(),
                'current': code == current,
            })
        return langs

    def _wj_html_lang(self):
        """Giá trị cho <html lang> — theo ngôn ngữ đang dùng, không ghim vi/en."""
        return (self.env.lang or 'en_US').replace('_', '-')

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
