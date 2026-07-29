import sys
sys.path.append('/home/dev/WujiaTea-ERP-internal/odoo19')
import odoo
from odoo.api import Environment

def main():
    odoo.tools.config.parse_config(['-c', '/home/dev/WujiaTea-ERP-internal/config/odoo.conf', '-d', 'wujia_tea_19'])
    registry = odoo.modules.registry.Registry.new('wujia_tea_19')
    with registry.cursor() as cr:
        env = Environment(cr, odoo.SUPERUSER_ID, {})
        
        # Find template
        template = env['wujia.franchise.inspection.template'].search([], limit=1)
        franchise = env['wujia.franchise.management'].search([], limit=1)
        schedule = env['wujia.supervision.schedule'].search([], limit=1)
        
        print("Template:", template.name, "Lines count:", len(template.line_ids))
        for tl in template.line_ids:
            print("  Template Line ID:", tl.id, "Content:", tl.content)
            
        # Simulate onchange
        insp = env['wujia.franchise.inspection'].new({
            'franchise_id': franchise.id,
            'template_id': template.id,
            'schedule_id': schedule.id,
        })
        insp._onchange_template_id()
        
        lines_data = []
        for line in insp.line_ids:
            lines_data.append((0, 0, {
                'display_type': line.display_type,
                'sequence': line.sequence,
                'template_line_id': False, # Simulate web client sending False/Null
                'content_snapshot': line.content_snapshot,
                'deduction_score_snapshot': line.deduction_score_snapshot,
                'criterion_type_snapshot': line.criterion_type_snapshot,
                'is_pass': line.is_pass,
                'result': line.result,
                'previous_line_id': line.previous_line_id.id if line.previous_line_id else False,
                'previous_result': line.previous_result,
            }))
            
        # Create record
        member = env['wujia.franchise.member'].search([], limit=1)
        created_insp = env['wujia.franchise.inspection'].create({
            'name': 'Khảo sát test',
            'franchise_id': franchise.id,
            'template_id': template.id,
            'schedule_id': schedule.id,
            'confirmed_member_id': member.id if member else False,
            'planned_date': '2026-08-01',
            'line_ids': lines_data,
        })
        cr.commit()
        
        print("Created Inspection ID:", created_insp.id)
        for l in created_insp.line_ids:
            print(f"Line ID: {l.id}, display_type: {l.display_type}, template_line_id: {l.template_line_id.id if l.template_line_id else None}, content: {l.content_snapshot}, prev_result: {l.previous_result}")

if __name__ == '__main__':
    main()
