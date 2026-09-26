{
    'name': 'Wujia Exams',
    'version': '19.0.1.0.0',
    'category': 'Wujia',
    'summary': 'Đăng ký thi nhượng quyền — khóa thi, ca thi, kỳ thi, phiếu đa nhân sự, kết quả.',
    'description': """
Nghiệp vụ đào tạo / thi. Tách từ wujia_portal_exam (F12, ADR-027).

- Model wujia.exam.time.slot (ca giờ), wujia.exam.course (khóa, mã WJ-CRS/),
  wujia.exam.session (kỳ thi, mã WJ-EXS/, sức chứa, công bố kết quả),
  wujia.exam.registration (phiếu, mã WJ-EXR/) + wujia.exam.registration.line (thí sinh).
- _effective_max_per_registration / _portal_* / register_from_portal: luật dùng chung cho mọi kênh.
""",
    'author': 'WujiaTea',
    'license': 'LGPL-3',
    'depends': ['mail', 'wujia_franchise'],
    'data': [
        'security/wujia_exam_groups.xml',
        'security/ir.model.access.csv',
        'security/wujia_exam_rules.xml',
        'data/ir_sequence_data.xml',
        'views/backend_exam_time_slot_views.xml',
        'views/backend_exam_course_views.xml',
        'views/backend_exam_session_views.xml',
        'views/backend_exam_registration_views.xml',
        'views/backend_menu.xml',
    ],
    'pre_init_hook': 'pre_init_hook',
    'installable': True,
    'application': False,
    'auto_install': False,
}
