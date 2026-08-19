import odoo
import odoo.tools
from odoo.modules.registry import Registry

config = odoo.tools.config
config.parse_config(['-c', '/home/dev/WujiaTea-ERP-internal/config/odoo.conf'])
db = odoo.sql_db.db_connect('wujia_tea_19')
registry = Registry.new(db.dbname)
with db.cursor() as cr:
    env = odoo.api.Environment(cr, odoo.SUPERUSER_ID, {})
    
    # 1. Xóa toàn bộ phiếu khảo sát và chi tiết
    inspections = env['wujia.franchise.inspection'].search([])
    print(f"Xóa {len(inspections)} phiếu khảo sát...")
    inspections.unlink()

    # 2. Xóa các dòng tiêu chí mẫu
    t_lines = env['wujia.franchise.inspection.template.line'].search([])
    print(f"Xóa {len(t_lines)} dòng tiêu chí mẫu...")
    t_lines.unlink()

    # 3. Xóa mẫu khảo sát
    templates = env['wujia.franchise.inspection.template'].search([])
    print(f"Xóa {len(templates)} mẫu khảo sát...")
    templates.unlink()

    # 4. Xóa danh mục tiêu chí
    categories = env['wujia.franchise.inspection.category'].search([])
    print(f"Xóa {len(categories)} danh mục tiêu chí...")
    categories.unlink()

    # 5. Xóa khoản điểm xếp hạng
    grades = env['wujia.franchise.inspection.grade'].search([])
    print(f"Xóa {len(grades)} xếp hạng...")
    grades.unlink()

    cr.commit()
    print("Xóa sạch dữ liệu hoàn tất thành công!")
