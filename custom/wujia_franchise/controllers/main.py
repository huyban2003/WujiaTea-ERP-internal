# -*- coding: utf-8 -*-
import json
import base64
from odoo import http, fields, _
from odoo.http import request


class WujiaFranchiseInspectionWebController(http.Controller):

    @http.route(['/franchise/inspection/do/<int:inspection_id>'], type='http', auth='user', website=True, sitemap=False)
    def do_inspection_survey(self, inspection_id, **kwargs):
        inspection = request.env['wujia.franchise.inspection'].sudo().browse(int(inspection_id))

        if inspection.state == 'done':
            return request.not_found()
            
        # check inspector_user_id = user.id
        if inspection.inspector_user_id.id != request.env.user.id:
            return request.not_found()
            
        if not inspection.exists():
            return request.not_found()

        # Build lines data grouped / ordered
        lines = []
        for line in inspection.line_ids:
            prev_line = line.previous_line_id
            prev_info = None
            if prev_line and prev_line.exists():
                prev_info = {
                    'inspection_name': prev_line.inspection_id.name if prev_line.inspection_id else '',
                    'planned_date': str(prev_line.inspection_id.planned_date) if (prev_line.inspection_id and prev_line.inspection_id.planned_date) else '',
                    'inspector': prev_line.inspection_id.inspector_user_id.name if (prev_line.inspection_id and prev_line.inspection_id.inspector_user_id) else '',
                    'is_pass': prev_line.is_pass,
                    'note': prev_line.note or 'Không có ghi chú vi phạm',
                    'deduction_score': prev_line.deduction_score_snapshot or 0.0,
                    'has_evidence': bool(prev_line.evidence_image),
                    'evidence_url': f'/web/image/wujia.franchise.inspection.line/{prev_line.id}/evidence_image' if prev_line.evidence_image else '',
                }

            crit_type = line.criterion_type_snapshot or (line.template_line_id.criterion_type if line.template_line_id else 'normal')
            is_important = (crit_type == 'critical') or (line.deduction_score_snapshot and line.deduction_score_snapshot >= 5.0)

            line_data = {
                'id': line.id,
                'sequence': line.sequence,
                'display_type': line.display_type,
                'content': line.content_snapshot or '',
                'criterion_type': crit_type,
                'is_important': is_important,
                'is_pass': line.is_pass,
                'previous_result': line.previous_result or '',
                'previous_info': prev_info,
                'note': line.note or '',
                'has_evidence': bool(line.evidence_image),
                'evidence_image_url': f'/web/image/wujia.franchise.inspection.line/{line.id}/evidence_image' if line.evidence_image else '',
                'require_note': line.require_note_if_fail or line.require_note_if_fail_snapshot,
                'require_evidence': line.require_evidence_if_fail or line.require_evidence_if_fail_snapshot,
                'deduction_score': line.deduction_score_snapshot or 0.0,
            }
            lines.append(line_data)

        # Exam lines
        exam_lines = []
        for el in inspection.exam_line_ids:
            exam_lines.append({
                'id': el.id,
                'sequence': el.sequence,
                'code': el.quest_code_snapshot or '',
                'question': el.quest_content_snapshot or '',
                'answer': el.answer or '',
                'is_correct': el.is_correct,
                'point': el.point or 0.0,
                'max_score': el.quest_id.score if (el.quest_id and el.quest_id.score) else 1.0,
            })

        is_inspection_closed = (inspection.state in ('done', 'cancel'))
        is_exam_submitted = bool(inspection.is_exam_submitted)

        values = {
            'inspection': inspection,
            'lines': lines,
            'exam_lines': exam_lines,
            'checklist_count': len([l for l in lines if l.get('display_type') == 'line']),
            'exam_count': len(exam_lines),
            'max_checklist_score': inspection.template_id.checklist_max_score if inspection.template_id else 95.0,
            'max_exam_score': inspection.template_id.exam_max_score if inspection.template_id else 5.0,
            'is_inspection_closed': is_inspection_closed,
            'is_exam_submitted': is_exam_submitted,
            'test_employee_name': inspection.test_employee_name or '',
            'tenure': inspection.tenure or 0.0,
        }
        return request.render('wujia_franchise.inspection_survey_do_page', values)

    @http.route(['/franchise/inspection/do/<int:inspection_id>/save'], type='json', auth='user', methods=['POST'])
    def save_inspection_survey(self, inspection_id, lines=None, exam_lines=None, test_employee_name=None, tenure=None, finish=True, **kwargs):
        inspection = request.env['wujia.franchise.inspection'].sudo().browse(int(inspection_id))
        if not inspection.exists():
            return {'success': False, 'error': 'Phiếu khảo sát không tồn tại'}

        if inspection.state in ('done', 'cancel'):
            return {'success': False, 'error': 'Phiếu khảo sát đã hoàn tất hoặc bị hủy, không thể chỉnh sửa!'}

        LineModel = request.env['wujia.franchise.inspection.line'].sudo()
        ExamLineModel = request.env['wujia.franchise.inspection.exam.line'].sudo()

        # Update checklist lines (Checklist tab is NOT locked by exam submission)
        if lines:
            for l_data in lines:
                l_id = l_data.get('id')
                line = LineModel.browse(int(l_id)) if l_id else None
                if line and line.exists() and line.inspection_id.id == inspection.id:
                    vals = {
                        'is_pass': bool(l_data.get('is_pass')),
                        'note': l_data.get('note', '') or '',
                    }
                    evidence_b64 = l_data.get('evidence_image')
                    if evidence_b64 and 'base64,' in evidence_b64:
                        vals['evidence_image'] = evidence_b64.split('base64,')[1]
                    elif evidence_b64 is False:
                        vals['evidence_image'] = False

                    line.write(vals)

        # Update exam lines & info only if exam is not already submitted
        insp_vals = {}
        if not inspection.is_exam_submitted:
            emp_name_clean = (test_employee_name or '').strip()
            if not emp_name_clean:
                return {'success': False, 'error': 'Vui lòng nhập Họ và tên Nhân viên được kiểm tra trước khi lưu!'}

            insp_vals['test_employee_name'] = emp_name_clean
            if tenure is not None:
                try:
                    insp_vals['tenure'] = float(tenure) if tenure else 0.0
                except (ValueError, TypeError):
                    insp_vals['tenure'] = 0.0

            if exam_lines:
                for el_data in exam_lines:
                    el_id = el_data.get('id')
                    exam_line = ExamLineModel.browse(int(el_id)) if el_id else None
                    if exam_line and exam_line.exists() and exam_line.inspection_id.id == inspection.id:
                        ans = el_data.get('answer', '') or ''
                        exam_line.write({'answer': ans})
                        exam_line._evaluate_answer()

            insp_vals['is_exam_submitted'] = True

        if insp_vals:
            inspection.write(insp_vals)

        # Recompute scores & grade
        inspection._compute_checklist_score()
        inspection._compute_exam_score()
        inspection._compute_total_score()
        inspection._compute_grade()

        # Update inspection state based on checklist pass/fail if completing
        failed_lines = inspection.line_ids.filtered(lambda l: l.display_type == 'line' and not l.is_pass)
        if failed_lines and inspection.state == 'draft':
            inspection.action_need_remediation()

        return {
            'success': True,
            'is_exam_submitted': True,
            'checklist_score': inspection.checklist_score,
            'exam_score': inspection.exam_score,
            'total_score': inspection.total_score,
            'grade': inspection.grade_id.name if inspection.grade_id else '',
            'state': inspection.state,
        }
