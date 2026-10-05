from odoo import fields, models, tools


class WujiaI18nCoverage(models.Model):
    _name = 'wujia.i18n.coverage'
    _description = 'Translation coverage'
    _auto = False
    _order = 'module, lang'

    module = fields.Char(readonly=True)
    lang = fields.Selection('_selection_lang', string='Language', readonly=True)
    total = fields.Integer(readonly=True)
    translated = fields.Integer(readonly=True)
    edited = fields.Integer(readonly=True)
    pending = fields.Integer(string='Waiting to apply', readonly=True)
    missing = fields.Integer(readonly=True)
    percent = fields.Float(string='Coverage %', readonly=True, digits=(5, 1), aggregator='avg')

    def _selection_lang(self):
        return self.env['res.lang'].get_installed()

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(f"""
            CREATE VIEW {self._table} AS (
                SELECT min(v.id) AS id, v.module, v.lang,
                       count(*) AS total,
                       count(*) FILTER (WHERE v.state != 'missing') AS translated,
                       count(*) FILTER (WHERE v.state = 'override') AS edited,
                       count(*) FILTER (WHERE v.pending) AS pending,
                       count(*) FILTER (WHERE v.state = 'missing') AS missing,
                       round(100.0 * count(*) FILTER (WHERE v.state != 'missing') / count(*), 1) AS percent
                  FROM wujia_i18n_value v
                 WHERE v.term_active
              GROUP BY v.module, v.lang
            )
        """)
