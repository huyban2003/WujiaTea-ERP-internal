import odoo
import odoo.tools
from odoo.modules.registry import Registry

config = odoo.tools.config
config.parse_config(['-c', '/home/dev/WujiaTea-ERP-internal/config/odoo.conf'])
db = odoo.sql_db.db_connect('wujia_tea_19')
registry = Registry.new(db.dbname)
with db.cursor() as cr:
    env = odoo.api.Environment(cr, odoo.SUPERUSER_ID, {})
    print("REAL_TABLE:", env['wujia.franchise.inspection.template']._table)
