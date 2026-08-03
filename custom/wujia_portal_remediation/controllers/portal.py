# -*- coding: utf-8 -*-
from odoo import http, fields, _
from odoo.http import request


class WujiaPortalRemediationController(http.Controller):

    @http.route(['/portal/remediation'], type='http', auth='user', website=True)
    def portal_remediation_list(self, tab='pending', date_from=None, date_to=None, search=None, **kwargs):
        """
        Giao diện Khắc phục đánh giá cửa hàng nhượng quyền.
        Bao gồm 2 Tab chính:
        1. Cần khắc phục (pending)
        2. Đã khắc phục (completed)
        Kèm Bộ lọc theo ngày & từ khóa tìm kiếm.
        """
        # Demo data cho Tab "Cần khắc phục"
        pending_items = [
            {
                'id': 101,
                'inspection_code': 'KS-2026-08-001',
                'inspection_name': 'Khảo sát cửa hàng Lấp Vò - Đợt 1',
                'franchise_name': 'H005 Lấp Vò',
                'planned_date': '2026-08-03',
                'due_date': '2026-08-10',
                'inspector': 'Mitchell Admin',
                'score': 78.5,
                'grade': 'Hạng C',
                'grade_badge': 'bg-warning text-dark',
                'remediation_status': 'need_action',
                'remediation_status_label': 'Chưa khắc phục',
                'failed_count': 3,
                'failed_items': [
                    {
                        'code': '1.02',
                        'category': 'Gìn giữ hình ảnh ngoại quan cửa hàng',
                        'content': 'Biển hiệu cửa hàng bị bám bẩn, đèn LED logo chưa bật đúng giờ',
                        'deduction': 3.0,
                        'require_evidence': True,
                    },
                    {
                        'code': '2.05',
                        'category': 'Yêu cầu giữ gìn các thiết bị',
                        'content': 'Máy dập nắp ly chưa được vệ sinh sạch sau ca tối',
                        'deduction': 4.0,
                        'require_evidence': True,
                    },
                    {
                        'code': '3.01',
                        'category': 'Yêu cầu tiêu chuẩn cơ bản',
                        'content': 'Nhân viên pha chế chưa đeo bảng tên theo quy định',
                        'deduction': 2.0,
                        'require_evidence': False,
                    }
                ]
            },
            {
                'id': 102,
                'inspection_code': 'KS-2026-07-018',
                'inspection_name': 'Khảo sát định kỳ cửa hàng Đống Đa',
                'franchise_name': 'HN-02 Đống Đa',
                'planned_date': '2026-07-28',
                'due_date': '2026-08-05',
                'inspector': 'Nguyễn Văn Kiểm',
                'score': 68.0,
                'grade': 'Hạng D',
                'grade_badge': 'bg-danger text-white',
                'remediation_status': 'in_review',
                'remediation_status_label': 'Đang chờ duyệt',
                'failed_count': 2,
                'failed_items': [
                    {
                        'code': '4.01',
                        'category': 'Những hạng mục vi phạm nghiêm trọng',
                        'content': 'Bảo quản nguyên liệu sai nhiệt độ tiêu chuẩn tủ đông',
                        'deduction': 6.0,
                        'require_evidence': True,
                    },
                    {
                        'code': '2.11',
                        'category': 'Yêu cầu giữ gìn các thiết bị',
                        'content': 'Tủ bánh ngọt bám hơi nước, thiếu tem hạn sử dụng',
                        'deduction': 3.0,
                        'require_evidence': True,
                    }
                ]
            }
        ]

        # Demo data cho Tab "Đã khắc phục"
        completed_items = [
            {
                'id': 201,
                'inspection_code': 'KS-2026-07-005',
                'inspection_name': 'Khảo sát cửa hàng Cầu Giấy',
                'franchise_name': 'HN-01 Cầu Giấy',
                'planned_date': '2026-07-15',
                'completed_date': '2026-07-20',
                'inspector': 'Mitchell Admin',
                'score_before': 81.0,
                'score_after': 95.0,
                'grade': 'Hạng A',
                'grade_badge': 'bg-success text-white',
                'reviewer': 'Trần Văn Duyệt',
                'fixed_count': 2,
                'fixed_items': [
                    {
                        'code': '1.05',
                        'category': 'Gìn giữ hình ảnh ngoại quan cửa hàng',
                        'content': 'Khu vực để xe khách hàng chưa sắp xếp gọn gàng',
                        'remediation_note': 'Đã bố trí lại vạch kẻ xe và phân công bảo vệ túc trực 100%',
                        'evidence_file': 'anh_khac_phuc_xe.jpg',
                    },
                    {
                        'code': '3.08',
                        'category': 'Yêu cầu tiêu chuẩn cơ bản',
                        'content': 'Sàn nhà khu pha chế có vết nước đọng',
                        'remediation_note': 'Đã trang bị thảm chống trượt và máy hút nước tự động',
                        'evidence_file': 'anh_khac_phuc_san.jpg',
                    }
                ]
            }
        ]

        # Áp dụng bộ lọc tìm kiếm theo từ khóa nếu có
        if search:
            q = search.strip().lower()
            pending_items = [
                i for i in pending_items
                if q in i['inspection_code'].lower() or q in i['inspection_name'].lower() or q in i['franchise_name'].lower()
            ]
            completed_items = [
                i for i in completed_items
                if q in i['inspection_code'].lower() or q in i['inspection_name'].lower() or q in i['franchise_name'].lower()
            ]

        values = {
            '_remediation_active': True,
            'active_tab': tab if tab in ('pending', 'completed') else 'pending',
            'date_from': date_from or '',
            'date_to': date_to or '',
            'search_q': search or '',
            'pending_items': pending_items,
            'completed_items': completed_items,
            'pending_count': len(pending_items),
            'completed_count': len(completed_items),
        }
        return request.render('wujia_portal_remediation.portal_remediation_main', values)
