# -*- coding: utf-8 -*-
import json
import base64
import csv
import os
from odoo import http, fields, _
# pyrefly: ignore [missing-import]
from odoo.http import request

# Glossary dùng chung toàn repo (repo_root/docs/), cùng nguồn với scripts/sync_translations.py.
# Thiếu file thì t() tự rơi về default — trang khảo sát vẫn chạy.
CSV_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'wujia_franchise_export.csv')

_SURVEY_LANG_COL = (('zh', 'CN'), ('cn', 'CN'), ('th', 'TH'), ('vi', 'VN'), ('vn', 'VN'))


def get_survey_translations(lang):
    low = (lang or '').lower()
    col = next((c for p, c in _SURVEY_LANG_COL if p in low), 'VN')
    trans_map = {}
    if os.path.exists(CSV_PATH):
        with open(CSV_PATH, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                opt = (row.get('option') or '').strip()
                k = (row.get('key') or '').strip()
                v = (row.get(col) or '').strip()
                if not v:
                    v = (row.get('VN') or '').strip()
                if opt and v:
                    trans_map[opt] = v
                if k and v:
                    trans_map[k] = v
    return trans_map


class WujiaFranchiseInspectionWebController(http.Controller):

    @http.route(['/franchise/inspection/do/<int:inspection_id>'], type='http', auth='user', website=True, sitemap=False)
    def do_inspection_survey(self, inspection_id, **kwargs):
        inspection = request.env['wujia.franchise.inspection'].sudo().browse(int(inspection_id))
            
        if not inspection.exists():
            return request.not_found()
            
        # Allow Admin, Manager, Supervisor, Assigned Inspector, and Internal Users
        user = request.env.user
        is_admin = user.has_group('base.group_system') or user.id in (1, 2)
        if not is_admin and inspection.inspector_user_id and inspection.inspector_user_id.id != user.id:
            if not user.has_group('base.group_user'):
                return request.not_found()

        lines_rec = inspection.line_ids

        # Kích hoạt prefetch tự động của Odoo ORM cho toàn bộ recordset liên kết (Tránh N+1)
        prev_lines = lines_rec.mapped('previous_line_id')
        prev_inspections = prev_lines.mapped('inspection_id')
        prev_inspections.mapped('inspector_user_id')
        lines_rec.mapped('template_line_id')

        # Build lines data grouped / ordered
        lines = []
        for line in lines_rec:
            prev_line = line.previous_line_id
            prev_info = None
            has_prev_note = False
            prev_note_text = ''
            
            if prev_line:
                p_note = (prev_line.note or '').strip()
                has_prev_note = bool(p_note and p_note not in ('No violation note', 'Chưa có ghi chú', '-'))
                prev_note_text = p_note if has_prev_note else ''
                prev_info = {
                    'inspection_name': prev_line.inspection_id.name if prev_line.inspection_id else '',
                    'planned_date': str(prev_line.inspection_id.planned_date) if (prev_line.inspection_id and prev_line.inspection_id.planned_date) else '',
                    'inspector': prev_line.inspection_id.inspector_user_id.name if (prev_line.inspection_id and prev_line.inspection_id.inspector_user_id) else '---',
                    'is_pass': prev_line.is_pass,
                    'note': prev_note_text,
                    'has_note': has_prev_note,
                    'deduction_score': prev_line.deduction_score_snapshot or 0.0,
                    'has_evidence': bool(prev_line.evidence_image),
                    'evidence_url': f'/web/image/wujia.franchise.inspection.line/{prev_line.id}/evidence_image' if prev_line.evidence_image else '',
                }

            crit_type = line.criterion_type_snapshot or (line.template_line_id.criterion_type if line.template_line_id else 'normal')
            deduction_score = line.deduction_score_snapshot or 0.0
            is_important = (crit_type == 'critical') or (deduction_score >= 5.0)

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
                'has_prev_note': has_prev_note,
                'prev_note': prev_note_text,
                'note': line.note or '',
                'has_evidence': bool(line.evidence_image),
                'evidence_image_url': f'/web/image/wujia.franchise.inspection.line/{line.id}/evidence_image' if line.evidence_image else '',
                'require_note': line.require_note_if_fail or line.require_note_if_fail_snapshot,
                'require_evidence': line.require_evidence_if_fail or line.require_evidence_if_fail_snapshot,
                'deduction_score': deduction_score,
            }
            lines.append(line_data)

        # Group lines by section and compute section total/earned scores
        current_section = None
        for l in lines:
            if l.get('display_type') == 'section':
                current_section = l
                l['section_id'] = l['id']
                l['section_total_score'] = 0.0
                l['section_earned_score'] = 0.0
                l['section_total_count'] = 0
                l['section_pass_count'] = 0
            elif current_section:
                l['section_id'] = current_section['id']
                score = float(l.get('deduction_score') or 0.0)
                current_section['section_total_score'] += score
                if l.get('is_pass'):
                    current_section['section_earned_score'] += score
                    current_section['section_pass_count'] += 1
                current_section['section_total_count'] += 1

        for l in lines:
            if l.get('display_type') == 'section':
                tot = l.get('section_total_score', 0.0)
                earned = l.get('section_earned_score', 0.0)
                l['section_total_score_str'] = str(int(tot)) if tot.is_integer() else f"{tot:.1f}"
                l['section_earned_score_str'] = str(int(earned)) if earned.is_integer() else f"{earned:.1f}"

        # Exam lines: Prefetch câu hỏi
        inspection.exam_line_ids.mapped('quest_id')
        exam_lines = [
            {
                'id': el.id,
                'sequence': el.sequence,
                'code': el.quest_code_snapshot or '',
                'question': el.quest_content_snapshot or '',
                'answer': el.answer or '',
                'is_correct': el.is_correct,
                'point': el.point or 0.0,
                'max_score': el.quest_id.score if (el.quest_id and el.quest_id.score) else 1.0,
            }
            for el in inspection.exam_line_ids
        ]

        is_inspection_closed = (inspection.state in ('done', 'cancel'))
        is_exam_submitted = bool(inspection.is_exam_submitted)

        user_lang = kwargs.get('lang') or request.params.get('lang') or request.env.user.lang or request.context.get('lang') or 'vi_VN'
        trans_map = get_survey_translations(user_lang)

        def _t(key, default=''):
            return trans_map.get(key, default or key)

        grades_data = [
            {
                'id': g.id,
                'name': g.name,
                'min_score': g.min_score,
                'max_score': g.max_score,
            }
            for g in request.env['wujia.franchise.inspection.grade'].sudo().search([], order='min_score desc')
        ]

        store_members = request.env['wujia.franchise.member'].sudo().search([
            ('franchise_id', '=', inspection.franchise_id.id),
            ('active', '=', True),
            ('is_working', '=', True),
        ], order='role, id')

        attendance_lines = [
            {
                'id': att.id,
                'member_id': att.member_id.id if att.member_id else False,
                'employee_name': att.employee_name or '',
                'role': att.role or 'staff',
                'phone': att.phone or '',
                'is_present': att.is_present,
                'note': att.note or '',
            }
            for att in inspection.attendance_line_ids
        ]

        passed_members = [
            {
                'id': m.id,
                'name': m.user_id.name if m.user_id else '',
                'role': m.role or 'staff',
                'phone': m.phone or '',
            }
            for m in inspection.passed_member_ids
        ]

        values = {
            'inspection': inspection,
            'grades_json': json.dumps(grades_data, ensure_ascii=False),
            'lines': lines,
            'exam_lines': exam_lines,
            'checklist_count': len([l for l in lines if l.get('display_type') == 'line']),
            'exam_count': len(exam_lines),
            'max_checklist_score': inspection.template_id.checklist_max_score if inspection.template_id else 95.0,
            'max_exam_score': inspection.template_id.exam_max_score if inspection.template_id else 5.0,
            'is_inspection_closed': is_inspection_closed,
            'is_exam_submitted': is_exam_submitted,
            'test_employee_name': inspection.test_employee_name or '',
            'tenure': inspection.tenure or '',
            'store_appearance_issues': inspection.store_appearance_issues or '',
            'previous_store_appearance_issues': inspection.previous_store_appearance_issues or '',
            'confirmed_user_name': inspection.confirmed_user_id.name if inspection.confirmed_user_id else request.env.user.name,
            'has_signature': bool(inspection.signature_image),
            'signature_image_url': f'/web/image/wujia.franchise.inspection/{inspection.id}/signature_image' if inspection.signature_image else '',
            'signature_date': str(inspection.signature_date) if inspection.signature_date else '',
            'confirmed_member_id': inspection.confirmed_member_id.id if inspection.confirmed_member_id else False,
            'store_members': store_members,
            'attendance_lines': attendance_lines,
            'passed_members': passed_members,
            'months_list': (
                [('01', '01月'), ('02', '02月'), ('03', '03月'), ('04', '04月'), ('05', '05月'), ('06', '06月'), ('07', '07月'), ('08', '08月'), ('09', '09月'), ('10', '10月'), ('11', '11月'), ('12', '12月')]
                if any(x in user_lang.lower() for x in ('zh', 'cn')) else (
                    [('01', 'ม.ค. (01)'), ('02', 'ก.พ. (02)'), ('03', 'มี.ค. (03)'), ('04', 'เม.ย. (04)'), ('05', 'พ.ค. (05)'), ('06', 'มิ.ย. (06)'), ('07', 'ก.ค. (07)'), ('08', 'ส.ค. (08)'), ('09', 'ก.ย. (09)'), ('10', 'ต.ค. (10)'), ('11', 'พ.ย. (11)'), ('12', 'ธ.ค. (12)')]
                    if 'th' in user_lang.lower() else
                    [('01', 'Tháng 01'), ('02', 'Tháng 02'), ('03', 'Tháng 03'), ('04', 'Tháng 04'), ('05', 'Tháng 05'), ('06', 'Tháng 06'), ('07', 'Tháng 07'), ('08', 'Tháng 08'), ('09', 'Tháng 09'), ('10', 'Tháng 10'), ('11', 'Tháng 11'), ('12', 'Tháng 12')]
                )
            ),
            'years_list': [str(y) for y in range(2023, 2031)],
            'report_lines': [
                {
                    'id': rl.id,
                    'date_month': str(rl.date_month) if rl.date_month else '',
                    'month_val': rl.date_month.strftime('%m') if rl.date_month else '01',
                    'year_val': rl.date_month.strftime('%Y') if rl.date_month else '2026',
                    'date_month_val': rl.date_month.strftime('%Y-%m') if rl.date_month else '',
                    'date_month_str': rl.date_month.strftime('%m/%Y') if rl.date_month else '',
                    'revenue': rl.revenue or 0.0,
                    'revenue_avg': rl.revenue_avg or 0.0,
                    'total_app_sale': rl.total_app_sale or 0,
                    'percent_app_sale': rl.percent_app_sale or 0.0,
                }
                for rl in inspection.report_line_ids.sorted(key=lambda r: (r.sequence, r.id))
            ],
            'present_count': inspection.present_count,
            'passed_count': len(passed_members),
            't': trans_map,
            'tj': json.dumps(trans_map, ensure_ascii=False),
            'trans_dict': trans_map,
            'trans': trans_map,
            'trans_json': json.dumps(trans_map, ensure_ascii=False),
        }
        return request.render('wujia_franchise.inspection_survey_do_page', values)

    @http.route(['/franchise/inspection/do/<int:inspection_id>/save'], type='json', auth='user', methods=['POST'])
    def save_inspection_survey(self, inspection_id, lines=None, exam_lines=None, test_employee_name=None, tenure=None, store_appearance_issues=None, confirmed_member_id=None, attendance_lines=None, signature_image=None, report_lines=None, finish=True, **kwargs):
        inspection = request.env['wujia.franchise.inspection'].sudo().browse(int(inspection_id))
        if not inspection.exists():
            return {'success': False, 'error': 'Inspection sheet does not exist'}

        if inspection.state in ('done', 'cancel'):
            return {'success': False, 'error': 'Inspection sheet is already completed or cancelled and cannot be edited!'}

        # 1. Tối ưu cập nhật checklist lines: So sánh qua ORM để chỉ ghi các dòng thực sự thay đổi
        if lines:
            line_map = {l.id: l for l in inspection.line_ids.filtered(lambda x: x.display_type == 'line')}
            for l_data in lines:
                l_id = int(l_data.get('id', 0))
                line = line_map.get(l_id)
                if not line:
                    continue
                new_is_pass = bool(l_data.get('is_pass'))
                new_note = (l_data.get('note', '') or '').strip()
                evidence_b64 = l_data.get('evidence_image')

                vals = {}
                if line.is_pass != new_is_pass:
                    vals['is_pass'] = new_is_pass
                if (line.note or '').strip() != new_note:
                    vals['note'] = new_note
                if evidence_b64 and 'base64,' in evidence_b64:
                    vals['evidence_image'] = evidence_b64.split('base64,')[1]
                elif (evidence_b64 in (False, 'REMOVE', 'CLEAR', '') or evidence_b64 is False) and line.evidence_image:
                    vals['evidence_image'] = False

                if vals:
                    line.write(vals)

        # 2. Tối ưu cập nhật exam lines
        insp_vals = {}
        if not inspection.is_exam_submitted:
            emp_name_clean = (test_employee_name or '').strip()
            if not emp_name_clean:
                return {'success': False, 'error': 'Vui lòng nhập Họ và tên Nhân viên được kiểm tra trước khi lưu!'}

            insp_vals['test_employee_name'] = emp_name_clean
            if tenure is not None:
                insp_vals['tenure'] = str(tenure).strip() if tenure else ''

            if exam_lines:
                exam_map = {el.id: el for el in inspection.exam_line_ids}
                for el_data in exam_lines:
                    el_id = int(el_data.get('id', 0))
                    exam_line = exam_map.get(el_id)
                    if not exam_line:
                        continue
                    ans = (el_data.get('answer', '') or '').strip()
                    if (exam_line.answer or '').strip() != ans:
                        exam_line.write({'answer': ans})
                        exam_line._evaluate_answer()

            insp_vals['is_exam_submitted'] = True

        if store_appearance_issues is not None:
            insp_vals['store_appearance_issues'] = store_appearance_issues

        sig_data = signature_image or kwargs.get('signature_image')
        if sig_data and 'base64,' in sig_data:
            insp_vals['signature_image'] = sig_data.split('base64,', 1)[1]
            insp_vals['signature_date'] = fields.Datetime.now()
        elif sig_data == 'CLEAR':
            insp_vals['signature_image'] = False
            insp_vals['signature_date'] = False

        if confirmed_member_id is not None:
            insp_vals['confirmed_member_id'] = int(confirmed_member_id) if confirmed_member_id else False

        # 3. Tối ưu cập nhật attendance lines
        if attendance_lines:
            att_map = {att.id: att for att in inspection.attendance_line_ids}
            for a_item in attendance_lines:
                att_id = int(a_item.get('id', 0))
                att = att_map.get(att_id)
                if not att:
                    continue
                is_present = bool(a_item.get('is_present', True))
                note = a_item.get('note', '') or False
                att_vals = {}
                if att.is_present != is_present:
                    att_vals['is_present'] = is_present
                if (att.note or False) != note:
                    att_vals['note'] = note
                if att_vals:
                    att.write(att_vals)

        if insp_vals:
            inspection.write(insp_vals)

        # 4. Tính toán lại điểm số & grade bằng các phương thức ORM
        inspection._compute_checklist_score()
        inspection._compute_exam_score()
        inspection._compute_total_score()
        inspection._compute_grade()

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

    @http.route(['/franchise/inspection/do/<int:inspection_id>/attendance/add'], type='json', auth='user', methods=['POST'])
    def add_attendance_line(self, inspection_id, employee_name, role='staff', phone='', note='', is_present=True, **kwargs):
        inspection = request.env['wujia.franchise.inspection'].sudo().browse(int(inspection_id))
        if not inspection.exists() or inspection.state in ('done', 'cancel'):
            return {'success': False, 'error': 'Phiếu khảo sát đã khóa hoặc không tồn tại!'}
        
        emp_name = (employee_name or '').strip()
        if not emp_name:
            return {'success': False, 'error': 'Vui lòng nhập Họ và tên nhân viên!'}
        
        new_line = request.env['wujia.franchise.inspection.attendance.line'].sudo().create({
            'inspection_id': inspection.id,
            'employee_name': emp_name,
            'role': role or 'staff',
            'phone': (phone or '').strip(),
            'note': (note or '').strip(),
            'is_present': bool(is_present),
        })
        
        return {
            'success': True,
            'line': {
                'id': new_line.id,
                'member_id': False,
                'employee_name': new_line.employee_name,
                'role': new_line.role,
                'phone': new_line.phone or '',
                'is_present': new_line.is_present,
                'note': new_line.note or '',
            },
            'present_count': inspection.present_count,
        }

    @http.route(['/franchise/inspection/do/<int:inspection_id>/attendance/save_member'], type='json', auth='user', methods=['POST'])
    def save_attendance_to_member(self, inspection_id, line_id, employee_name=None, role=None, phone=None, **kwargs):
        line = request.env['wujia.franchise.inspection.attendance.line'].sudo().browse(int(line_id))
        if not line.exists() or line.inspection_id.id != int(inspection_id):
            return {'success': False, 'error': 'Dòng điểm danh không tồn tại!'}
        
        if employee_name:
            line.employee_name = employee_name.strip()
        if role:
            line.role = role
        if phone is not None:
            line.phone = phone.strip()
            
        try:
            line.action_save_to_member()
            return {
                'success': True,
                'member_id': line.member_id.id if line.member_id else False,
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

    @http.route(['/franchise/inspection/do/<int:inspection_id>/attendance/deactivate_member'], type='json', auth='user', methods=['POST'])
    def deactivate_attendance_member(self, inspection_id, line_id, **kwargs):
        line = request.env['wujia.franchise.inspection.attendance.line'].sudo().browse(int(line_id))
        if not line.exists() or line.inspection_id.id != int(inspection_id):
            return {'success': False, 'error': 'Dòng điểm danh không tồn tại!'}
        
        try:
            inspection = line.inspection_id
            line.action_deactivate_member()
            return {'success': True, 'present_count': inspection.present_count}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    @http.route(['/franchise/inspection/do/<int:inspection_id>/attendance/delete_line'], type='json', auth='user', methods=['POST'])
    def delete_attendance_line(self, inspection_id, line_id, **kwargs):
        line = request.env['wujia.franchise.inspection.attendance.line'].sudo().browse(int(line_id))
        if not line.exists() or line.inspection_id.id != int(inspection_id):
            return {'success': False, 'error': 'Dòng điểm danh không tồn tại!'}
        
        inspection = line.inspection_id
        line.unlink()
        return {'success': True, 'present_count': inspection.present_count}
