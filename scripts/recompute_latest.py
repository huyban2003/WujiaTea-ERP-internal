import odoo
import odoo.tools
from odoo.modules.registry import Registry

config = odoo.tools.config
config.parse_config(['-c', '/home/dev/WujiaTea-ERP-internal/config/odoo.conf'])
db = odoo.sql_db.db_connect('wujia_tea_19')
registry = Registry.new(db.dbname)
with db.cursor() as cr:
    env = odoo.api.Environment(cr, odoo.SUPERUSER_ID, {})
    stores = env['wujia.franchise.management'].search([])
    stores._compute_latest_inspection_info()
    cr.commit()
    print("Recomputed successfully for stores:", stores.mapped('code'))
