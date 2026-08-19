# -*- coding: utf-8 -*-
import base64
from odoo import http, fields, _
# pyrefly: ignore [missing-import]
from odoo.http import request

# pyrefly: ignore [missing-import]
from odoo.addons.wujia_portal_base.controllers.portal import get_active_franchise_ids_filter


def _parse_date(date_str):
    if not date_str:
        return ''
    date_str = str(date_str).strip()
    if '/' in date_str:
        parts = date_str.split('/')
        if len(parts) == 3:
            return f"{parts[2]}-{parts[1].zfill(2)}-{parts[0].zfill(2)}"
    return date_str


class WujiaPortalRemediationController(http.Controller):

    @http.route(['/portal/remediation'], type='http', auth='user', website=True)
    def portal_remediation_list(self, tab='pending', date_from=None, date_to=None, search=None, **kwargs):
        """
        Giao diện Khắc phục cửa hàng nhượng quyền.
        Chỉ lấy các phiếu khảo sát (wujia.franchise.inspection) đang trong trạng thái
        Cần khắc phục ('need_remediation') hoặc Hoàn thành ('done').
        Bỏ qua các phiếu Nháp ('draft'), Đang thực hiện ('in_progress'), Đã hủy ('cancel').
        """
        franchise_ids = get_active_franchise_ids_filter()

        # CHỈ lấy các phiếu khảo sát ở trạng thái 'need_remediation'
        inspection_domain = [('state', '=', 'need_remediation')]
        # fail-closed: không thuộc cửa hàng nào ⇒ domain rỗng ⇒ không thấy phiếu nào
        inspection_domain.append(('franchise_id', 'in', list(franchise_ids or ())))

        parsed_date_from = _parse_date(date_from)
        parsed_date_to = _parse_date(date_to)

        # Lọc theo khoảng ngày nếu có
        if parsed_date_from:
            inspection_domain.append(('planned_date', '>=', parsed_date_from))
        if parsed_date_to:
            inspection_domain.append(('planned_date', '<=', parsed_date_to))

        # Lọc theo từ khóa tìm kiếm nếu có
        if search:
            q = search.strip()
            inspection_domain.extend([
                '|', '|',
                ('name', 'ilike', q),
                ('franchise_id.name', 'ilike', q),
                ('franchise_id.code', 'ilike', q),
            ])

        inspections = request.env['wujia.franchise.inspection'].sudo().search(
            inspection_domain, order='planned_date desc, id desc'
        )

        # Batch pre-fetch relational fields để triệt tiêu N+1 queries khi lặp qua nhiều record
        inspections.mapped('franchise_id')
        inspections.mapped('grade_id')
        inspections.mapped('inspector_user_id')
        all_lines = inspections.mapped('line_ids')
        all_lines.mapped('template_line_id')
        all_lines.mapped('template_line_id.category_id')
        all_lines.mapped('category_id')

        pending_items = []
        completed_items = []

        for insp in inspections:
            # Lọc các dòng tiêu chí vi phạm (is_pass == False hoặc result == 'fail')
            failed_lines = insp.line_ids.filtered(
                lambda l: (
                    l.display_type == 'line'
                    and (not l.is_pass or l.result == 'fail')
                )
            )
            if not failed_lines:
                continue

            grade_name = insp.grade_id.name if insp.grade_id else 'N/A'
            grade_badge = 'bg-warning text-dark'
            if insp.grade_id:
                if 'A' in grade_name:
                    grade_badge = 'bg-success text-white'
                elif 'B' in grade_name:
                    grade_badge = 'bg-info text-white'
                elif 'C' in grade_name:
                    grade_badge = 'bg-warning text-dark'
                elif 'D' in grade_name or 'F' in grade_name:
                    grade_badge = 'bg-danger text-white'

            for line in failed_lines:
                # Mã tiêu chí
                code_str = ''
                if line.template_line_id and getattr(line.template_line_id, 'criterion_code', False):
                    code_str = line.template_line_id.criterion_code
                elif line.sequence:
                    code_str = f"TC-{line.sequence}"

                # Danh mục
                cat_str = ''
                if line.category_id and line.category_id.name:
                    cat_str = line.category_id.name
                elif line.template_line_id and line.template_line_id.category_id and line.template_line_id.category_id.name:
                    cat_str = line.template_line_id.category_id.name
                else:
                    cat_str = 'Tiêu chí vi phạm'

                # Nội dung
                content_str = line.content_snapshot or (line.template_line_id.content if (line.template_line_id and line.template_line_id.content) else '')

                # Điểm trừ
                deduction_score = line.deduction_score_snapshot or (line.template_line_id.deduction_score if (line.template_line_id and line.template_line_id.deduction_score) else 0.0)

                line_data = {
                    'id': line.id,
                    'line_id': line.id,
                    'code': code_str,
                    'category': cat_str,
                    'content': content_str,
                    'deduction': deduction_score,
                    'require_evidence': line.require_evidence_if_fail_snapshot or line.require_evidence_if_fail,
                    'note': line.note or '',
                    'remediation_note': line.remediation_note or '',
                    'has_remediation_image': bool(line.remediation_image),
                    'remediation_image_url': f"/web/image/wujia.franchise.inspection.line/{line.id}/remediation_image" if line.remediation_image else False,
                    # Thông tin từ phiếu khảo sát cha
                    'inspection_id': insp.id,
                    'inspection_code': insp.name,
                    'inspection_name': insp.name,
                    'franchise_name': insp.franchise_id.display_name if insp.franchise_id else 'Cửa hàng',
                    'planned_date': str(insp.planned_date) if insp.planned_date else '',
                    'due_date': str(insp.submit_date or insp.planned_date) if (insp.submit_date or insp.planned_date) else '',
                    'inspector': insp.inspector_user_id.name if insp.inspector_user_id else 'N/A',
                    'score': insp.total_score,
                    'grade': grade_name,
                    'grade_badge': grade_badge,
                }

                # Dòng được tính là Đã phản hồi nếu đã nhập ghi chú khắc phục HOẶC đã nộp ảnh minh chứng
                if line.remediation_image or line.remediation_note:
                    completed_items.append(line_data)
                else:
                    pending_items.append(line_data)

        values = {
            '_remediation_active': True,
            'active_tab': tab if tab in ('pending', 'completed') else 'pending',
            'date_from': date_from or '',
            'date_to': date_to or '',
            'search_q': search or '',
            'submitted_success': bool(kwargs.get('submitted')),
            'error_missing_data': kwargs.get('error') == 'missing_data',
            'error_missing_image': kwargs.get('error') == 'missing_image',
            'pending_items': pending_items,
            'completed_items': completed_items,
            'pending_count': len(pending_items),
            'completed_count': len(completed_items),
        }
        return request.render('wujia_portal_remediation.portal_remediation_main', values)

    @http.route(['/portal/remediation/submit_line'], type='http', auth='user', methods=['POST'], website=True)
    def portal_remediation_submit_line(self, line_id=None, note=None, remediation_note=None, remediation_image=None, redirect_tab=None, **kwargs):
        """
        Nộp/Cập nhật ảnh minh chứng & ghi chú khắc phục cho 1 dòng inspection_line.
        Yêu cầu người dùng phải có ít nhất Ghi chú HOẶC Ảnh minh chứng mới cho phép gửi.
        """
        if line_id:
            line = request.env['wujia.franchise.inspection.line'].sudo().browse(int(line_id))
            if line.exists():
                store_note = (remediation_note or note or '').strip()
                has_new_image = False
                file_content = None
                if remediation_image and hasattr(remediation_image, 'read'):
                    file_content = remediation_image.read()
                    if file_content:
                        has_new_image = True

                has_image = has_new_image or bool(line.remediation_image)
                has_note = bool(store_note) or bool(line.remediation_note)
                require_ev = line.require_evidence_if_fail_snapshot or line.require_evidence_if_fail

                tab_fallback = redirect_tab if redirect_tab in ('pending', 'completed') else ('completed' if (has_image or has_note) else 'pending')

                if require_ev and not has_image:
                    return request.redirect(f'/portal/remediation?tab={tab_fallback}&error=missing_image')

                if not has_image and not has_note:
                    return request.redirect(f'/portal/remediation?tab={tab_fallback}&error=missing_data')

                vals = {}
                if store_note:
                    vals['remediation_note'] = store_note
                if has_new_image and file_content:
                    vals['remediation_image'] = base64.b64encode(file_content)
                if vals:
                    line.write(vals)

        tab_to_redirect = redirect_tab if redirect_tab in ('pending', 'completed') else 'completed'
        return request.redirect(f'/portal/remediation?tab={tab_to_redirect}&submitted=1')