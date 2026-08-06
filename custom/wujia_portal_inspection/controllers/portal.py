# -*- coding: utf-8 -*-
from odoo import http, fields, _
from odoo.http import request

try:
    from odoo.addons.wujia_portal_base.controllers.portal import get_active_franchise_ids_filter
except ImportError:
    def get_active_franchise_ids_filter():
        return []


def _parse_date(date_str):
    if not date_str:
        return ''
    date_str = str(date_str).strip()
    if '/' in date_str:
        parts = date_str.split('/')
        if len(parts) == 3:
            return f"{parts[2]}-{parts[1].zfill(2)}-{parts[0].zfill(2)}"
    return date_str


class WujiaPortalInspectionController(http.Controller):

    @http.route(['/portal/inspection'], type='http', auth='user', website=True)
    def portal_inspection_list(self, tab='all', date_from=None, date_to=None, search=None, **kwargs):
        """
        Giao diện Xem phiếu Khảo sát đánh giá (Read-only).
        Chỉ lấy các phiếu khảo sát (wujia.franchise.inspection) ở trạng thái
        Cần khắc phục ('need_remediation') hoặc Hoàn thành ('done').
        Bỏ qua phiếu Nháp ('draft'), Đang thực hiện ('in_progress'), Đã hủy ('cancel').
        """
        franchise_ids = get_active_franchise_ids_filter()

        # Domain lọc phiếu khảo sát: Chỉ 'need_remediation' và 'done'
        if tab == 'need_remediation':
            inspection_domain = [('state', '=', 'need_remediation')]
        elif tab == 'done':
            inspection_domain = [('state', '=', 'done')]
        else:
            inspection_domain = [('state', 'in', ('need_remediation', 'done'))]

        if franchise_ids:
            inspection_domain.append(('franchise_id', 'in', list(franchise_ids)))

        parsed_date_from = _parse_date(date_from)
        parsed_date_to = _parse_date(date_to)

        # Lọc theo khoảng ngày nếu có
        if parsed_date_from:
            inspection_domain.append(('planned_date', '>=', parsed_date_from))
        if parsed_date_to:
            inspection_domain.append(('planned_date', '<=', parsed_date_to))

        # Lọc theo từ khóa tìm kiếm
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

        # Batch pre-fetch relational fields để triệt tiêu N+1 queries trên DB
        inspections.mapped('franchise_id')
        inspections.mapped('grade_id')
        inspections.mapped('inspector_user_id')
        inspections.mapped('template_id')
        all_lines = inspections.mapped('line_ids')
        all_lines.mapped('template_line_id')

        # Đếm tổng quan độc lập với tab active trực tiếp bằng SQL COUNT(*) để tối ưu hiệu năng
        base_count_domain = [('state', 'in', ('need_remediation', 'done'))]
        if franchise_ids:
            base_count_domain.append(('franchise_id', 'in', list(franchise_ids)))
        if parsed_date_from:
            base_count_domain.append(('planned_date', '>=', parsed_date_from))
        if parsed_date_to:
            base_count_domain.append(('planned_date', '<=', parsed_date_to))
        if search:
            q = search.strip()
            base_count_domain.extend([
                '|', '|',
                ('name', 'ilike', q),
                ('franchise_id.name', 'ilike', q),
                ('franchise_id.code', 'ilike', q),
            ])

        InspectionModel = request.env['wujia.franchise.inspection'].sudo()
        need_remediation_count = InspectionModel.search_count(base_count_domain + [('state', '=', 'need_remediation')])
        done_count = InspectionModel.search_count(base_count_domain + [('state', '=', 'done')])

        inspection_items = []
        for insp in inspections:
            criteria_lines = insp.line_ids.filtered(lambda l: l.display_type == 'line')
            failed_lines = criteria_lines.filtered(lambda l: not l.is_pass or l.result == 'fail')
            unanswered_failed_lines = failed_lines.filtered(lambda l: not l.remediation_image and not l.remediation_note)
            has_unanswered = bool(unanswered_failed_lines)
            pass_lines = criteria_lines.filtered(lambda l: l.is_pass or l.result == 'pass')

            grade_name = insp.grade_id.name if insp.grade_id else 'N/A'
            grade_badge_class = 'wj-badge-warning'
            if insp.grade_id:
                if 'A' in grade_name:
                    grade_badge_class = 'wj-badge-success'
                elif 'B' in grade_name:
                    grade_badge_class = 'wj-badge-info'
                elif 'C' in grade_name:
                    grade_badge_class = 'wj-badge-warning'
                elif 'D' in grade_name or 'F' in grade_name:
                    grade_badge_class = 'wj-badge-danger'

            state_label = 'Hoàn thành'
            state_badge_class = 'wj-badge-success'
            state_pc_badge = 'wj-pc-badge--done'
            if insp.state == 'need_remediation':
                state_label = 'Chờ khắc phục'
                state_badge_class = 'wj-badge-danger'
                state_pc_badge = 'wj-pc-badge--cancel'

            # Làm sạch tên mã hiển thị trên Badge, bỏ chữ "Lịch giám sát kế tiếp..." thừa
            clean_code = insp.template_id.name if (insp.template_id and insp.template_id.name) else (insp.name or '')
            if clean_code:
                clean_code = clean_code.replace('Khảo sát: Lịch giám sát kế tiếp - ', '')
                clean_code = clean_code.replace('Lịch giám sát kế tiếp - ', '')
                clean_code = clean_code.replace('Lịch giám sát kế tiếp', '')
                clean_code = clean_code.replace('Khảo sát: ', '')
                clean_code = clean_code.strip(' -:')
                franchise_str = insp.franchise_id.display_name if insp.franchise_id else ''
                if not clean_code or (franchise_str and clean_code in franchise_str):
                    clean_code = 'Phiếu khảo sát'
            else:
                clean_code = 'Phiếu khảo sát'

            item_data = {
                'id': insp.id,
                'code': clean_code,
                'name': insp.name,
                'franchise_name': insp.franchise_id.display_name if insp.franchise_id else 'Cửa hàng',
                'planned_date': str(insp.planned_date) if insp.planned_date else '',
                'submit_date': str(insp.submit_date) if insp.submit_date else '',
                'inspector_name': insp.inspector_user_id.name if insp.inspector_user_id else 'N/A',
                'test_employee_name': insp.test_employee_name or 'N/A',
                'state': insp.state,
                'state_label': state_label,
                'state_badge_class': state_badge_class,
                'state_pc_badge': state_pc_badge,
                'total_score': insp.total_score,
                'checklist_score': insp.checklist_score,
                'exam_score': insp.exam_score,
                'grade_name': grade_name,
                'grade_badge_class': grade_badge_class,
                'total_criteria': len(criteria_lines),
                'pass_count': len(pass_lines),
                'failed_count': len(failed_lines),
                'remediation_url': f"/portal/remediation?search={insp.name}" if (insp.state == 'need_remediation' and has_unanswered) else False,
                'detail_url': f"/portal/inspection/detail/{insp.id}",
            }
            inspection_items.append(item_data)

        values = {
            '_inspection_active': True,
            'active_tab': tab if tab in ('all', 'need_remediation', 'done') else 'all',
            'date_from': date_from or '',
            'date_to': date_to or '',
            'search_q': search or '',
            'inspection_items': inspection_items,
            'all_count': need_remediation_count + done_count,
            'need_remediation_count': need_remediation_count,
            'done_count': done_count,
        }
        return request.render('wujia_portal_inspection.portal_inspection_main', values)

    @http.route(['/portal/inspection/detail/<int:inspection_id>'], type='http', auth='user', website=True)
    def portal_inspection_detail(self, inspection_id=None, **kwargs):
        """
        Trang xem chi tiết phiếu khảo sát (Read-only).
        """
        if not inspection_id:
            return request.redirect('/portal/inspection')

        insp = request.env['wujia.franchise.inspection'].sudo().browse(int(inspection_id))
        if not insp.exists() or insp.state not in ('need_remediation', 'done'):
            return request.redirect('/portal/inspection')

        # Đảm bảo cửa hàng nằm trong danh sách được cấp quyền
        franchise_ids = get_active_franchise_ids_filter()
        if franchise_ids and insp.franchise_id.id not in franchise_ids:
            return request.redirect('/portal/inspection')

        criteria_lines = insp.line_ids.filtered(lambda l: l.display_type == 'line')
        failed_lines = criteria_lines.filtered(lambda l: not l.is_pass or l.result == 'fail')
        unanswered_failed_lines = failed_lines.filtered(lambda l: not l.remediation_image and not l.remediation_note)
        has_unanswered = bool(unanswered_failed_lines)
        pass_lines = criteria_lines.filtered(lambda l: l.is_pass or l.result == 'pass')

        grade_name = insp.grade_id.name if insp.grade_id else 'N/A'
        grade_badge_class = 'wj-badge-warning'
        if insp.grade_id:
            if 'A' in grade_name:
                grade_badge_class = 'wj-badge-success'
            elif 'B' in grade_name:
                grade_badge_class = 'wj-badge-info'
            elif 'C' in grade_name:
                grade_badge_class = 'wj-badge-warning'
            elif 'D' in grade_name or 'F' in grade_name:
                grade_badge_class = 'wj-badge-danger'

        state_label = 'Hoàn thành'
        state_badge_class = 'wj-badge-success'
        state_pc_badge = 'wj-pc-badge--done'
        if insp.state == 'need_remediation':
            state_label = 'Chờ khắc phục'
            state_badge_class = 'wj-badge-danger'
            state_pc_badge = 'wj-pc-badge--cancel'

        sections = []
        current_section = {'title': 'Tiêu chí chung', 'lines': []}
        
        for line in insp.line_ids:
            if line.display_type == 'section':
                if current_section['lines']:
                    sections.append(current_section)
                current_section = {'title': line.content_snapshot or 'Section', 'lines': []}
            elif line.display_type == 'line':
                code_str = ''
                if line.template_line_id and getattr(line.template_line_id, 'criterion_code', False):
                    code_str = line.template_line_id.criterion_code
                elif line.sequence:
                    code_str = f"TC-{line.sequence}"

                cat_str = ''
                if line.category_id and line.category_id.name:
                    cat_str = line.category_id.name
                elif line.template_line_id and line.template_line_id.category_id and line.template_line_id.category_id.name:
                    cat_str = line.template_line_id.category_id.name

                content_str = line.content_snapshot or (line.template_line_id.content if (line.template_line_id and line.template_line_id.content) else '')
                deduction_score = line.deduction_score_snapshot or (line.template_line_id.deduction_score if (line.template_line_id and line.template_line_id.deduction_score) else 0.0)

                current_section['lines'].append({
                    'id': line.id,
                    'code': code_str,
                    'category': cat_str,
                    'content': content_str,
                    'is_pass': line.is_pass or line.result == 'pass',
                    'deduction': deduction_score,
                    'note': line.note or '',
                    'remediation_note': line.remediation_note or '',
                    'evidence_image_url': f"/web/image/wujia.franchise.inspection.line/{line.id}/evidence_image" if line.evidence_image else False,
                    'remediation_image_url': f"/web/image/wujia.franchise.inspection.line/{line.id}/remediation_image" if line.remediation_image else False,
                })

        if current_section['lines']:
            sections.append(current_section)

        clean_code = insp.template_id.name if (insp.template_id and insp.template_id.name) else (insp.name or '')
        if clean_code:
            clean_code = clean_code.replace('Khảo sát: Lịch giám sát kế tiếp - ', '')
            clean_code = clean_code.replace('Lịch giám sát kế tiếp - ', '')
            clean_code = clean_code.replace('Lịch giám sát kế tiếp', '')
            clean_code = clean_code.replace('Khảo sát: ', '')
            clean_code = clean_code.strip(' -:')
            franchise_str = insp.franchise_id.display_name if insp.franchise_id else ''
            if not clean_code or (franchise_str and clean_code in franchise_str):
                clean_code = 'Phiếu khảo sát'
        else:
            clean_code = 'Phiếu khảo sát'

        values = {
            '_inspection_active': True,
            'insp': insp,
            'inspection_id': insp.id,
            'code': clean_code,
            'franchise_name': insp.franchise_id.display_name if insp.franchise_id else 'Cửa hàng',
            'planned_date': str(insp.planned_date) if insp.planned_date else '',
            'submit_date': str(insp.submit_date) if insp.submit_date else '',
            'inspector_name': insp.inspector_user_id.name if insp.inspector_user_id else 'N/A',
            'test_employee_name': insp.test_employee_name or 'N/A',
            'state': insp.state,
            'state_label': state_label,
            'state_badge_class': state_badge_class,
            'state_pc_badge': state_pc_badge,
            'total_score': insp.total_score,
            'checklist_score': insp.checklist_score,
            'exam_score': insp.exam_score,
            'grade_name': grade_name,
            'grade_badge_class': grade_badge_class,
            'total_criteria': len(criteria_lines),
            'pass_count': len(pass_lines),
            'failed_count': len(failed_lines),
            'sections': sections,
            'remediation_url': f"/portal/remediation?search={insp.name}" if (insp.state == 'need_remediation' and has_unanswered) else False,
            'has_unanswered_remediation': has_unanswered,
        }
        return request.render('wujia_portal_inspection.portal_inspection_detail', values)
