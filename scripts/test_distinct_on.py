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
    
    query = """
        SELECT DISTINCT ON (franchise_id) id
        FROM wujia_franchise_inspection
        WHERE franchise_id = ANY(%s) AND state != 'cancel'
        ORDER BY franchise_id, planned_date DESC, create_date DESC, id DESC
    """
    cr.execute(query, (stores.ids,))
    latest_ids = [r[0] for r in cr.fetchall()]
    print("DISTINCT ON inspection IDs:", latest_ids)
    
    latest_inspections = env['wujia.franchise.inspection'].browse(latest_ids)
    latest_by_franchise = {insp.franchise_id.id: insp for insp in latest_inspections}
    print("Mapped by store:", {k: v.name for k, v in latest_by_franchise.items()})
