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
    
    # 1. ORM QueryBuilder với _read_group
    groups = env['wujia.franchise.inspection']._read_group(
        domain=[('franchise_id', 'in', stores.ids), ('state', '!=', 'cancel')],
        groupby=['franchise_id'],
        aggregates=['id:max'],
    )
    print("_read_group result:", groups)
