# -*- coding: utf-8 -*-
import math
from odoo import http, fields, _
# pyrefly: ignore [missing-import]
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
    def portal_inspection_list(self, tab='all', date_from=None, date_to=None, search=None, page=1, **kwargs):
        """
        Giao diện Xem phiếu Khảo sát đánh giá (Read-only) kèm Phân trang (Limit 5).
        """
        try:
            page = int(page)
            if page < 1:
                page = 1
        except (ValueError, TypeError):
            page = 1

        limit = 5
        franchise_ids = get_active_franchise_ids_filter()

        # Domain lọc phiếu khảo sát
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

        if parsed_date_from:
            inspection_domain.append(('planned_date', '>=', parsed_date_from))
        if parsed_date_to:
            inspection_domain.append(('planned_date', '<=', parsed_date_to))

        if search:
            q = search.strip()
            inspection_domain.extend([
                '|', '|',
                ('name', 'ilike', q),
                ('franchise_id.name', 'ilike', q),
                ('franchise_id.code', 'ilike', q),
            ])

        InspectionModel = request.env['wujia.franchise.inspection'].sudo()
        total_count = InspectionModel.search_count(inspection_domain)
        total_pages = math.ceil(total_count / limit) if total_count > 0 else 1
        if page > total_pages:
            page = total_pages

        offset = (page - 1) * limit
        inspections = InspectionModel.search(
            inspection_domain, order='planned_date desc, id desc', limit=limit, offset=offset
        )

        inspections.mapped('franchise_id')
        inspections.mapped('grade_id')
        inspections.mapped('inspector_user_id')
        inspections.mapped('template_id')

        inspection_items = []
        for insp in inspections:
            criteria_lines = insp.line_ids.filtered(lambda l: l.display_type == 'line')
            failed_lines = criteria_lines.filtered(lambda l: not l.is_pass or l.result == 'fail')
            unanswered_failed_lines = failed_lines.filtered(lambda l: not l.remediation_image and not l.remediation_note)
            has_unanswered = bool(unanswered_failed_lines)
            pass_lines = criteria_lines.filtered(lambda l: l.is_pass or l.result == 'pass')

            grade_name = insp.grade_id.name if insp.grade_id else 'N/A'

            state_label = 'Hoàn thành'
            badge_bg = '#dcfce7'
            badge_color = '#15803d'
            progress_color = '#22c55e'

            if insp.state == 'need_remediation':
                state_label = 'Chờ phản hồi'
                badge_bg = '#ffe4e6'
                badge_color = '#e11d48'
                progress_color = '#ef4444'
            elif insp.state == 'in_progress':
                state_label = 'Đang xử lý'
                badge_bg = '#dbeafe'
                badge_color = '#1d4ed8'
                progress_color = '#3b82f6'

            title_str = insp.name or "Khảo sát"
            if not title_str or title_str == "Khảo sát cửa hàng nhượng quyền" or title_str.startswith("Khảo sát cửa hàng nhượng quyền"):
                if insp.planned_date:
                    try:
                        d_str = fields.Date.from_string(insp.planned_date).strftime('%d/%m/%Y')
                        title_str = f"Lần {d_str}"
                    except Exception:
                        title_str = f"Lần {insp.planned_date}"
                else:
                    title_str = "Khảo sát cửa hàng"

            planned_date_formatted = ""
            if insp.planned_date:
                try:
                    planned_date_formatted = fields.Date.from_string(insp.planned_date).strftime('%d/%m/%Y')
                except Exception:
                    planned_date_formatted = str(insp.planned_date)

            item_data = {
                'id': insp.id,
                'name': insp.name or f"#AUD-{insp.id}",
                'code_badge': f"#{insp.name}" if insp.name else f"#AUD-{insp.id}",
                'title': title_str,
                'display_name': insp.name or title_str,
                'franchise_name': insp.franchise_id.display_name if insp.franchise_id else 'Cửa hàng',
                'planned_date': planned_date_formatted or 'N/A',
                'inspector_name': insp.inspector_user_id.name if insp.inspector_user_id else 'N/A',
                'state': insp.state,
                'state_label': state_label,
                'badge_bg': badge_bg,
                'badge_color': badge_color,
                'progress_color': progress_color,
                'total_score': int(insp.total_score or 0),
                'grade_name': grade_name,
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
            'page': page,
            'total_pages': total_pages,
            'total_count': total_count,
            'page_range': list(range(1, total_pages + 1)),
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
            state_label = 'Chờ phản hồi'
            state_badge_class = 'wj-badge-danger'
            state_pc_badge = 'wj-pc-badge--cancel'
        elif insp.state == 'in_progress':
            state_label = 'Đang xử lý'
            state_badge_class = 'wj-badge-info'
            state_pc_badge = 'wj-pc-badge--info'

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
