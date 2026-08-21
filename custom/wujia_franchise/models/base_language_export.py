# -*- coding: utf-8 -*-
import os
import base64
from odoo import models, tools
from odoo.addons.base.wizard.base_export_language import NEW_LANG_KEY


class BaseLanguageExport(models.TransientModel):
    _inherit = 'base.language.export'

    def act_getfile(self):
        self.ensure_one()
        mods = sorted(self.mapped('modules.name'))
        # Nếu xuất module wujia_franchise hoặc chỉ chọn 1 module là wujia_franchise
        if self.export_type == 'module' and ('wujia_franchise' in mods or (len(mods) == 1 and mods[0] == 'wujia_franchise')):
            lang = self.lang if self.lang != NEW_LANG_KEY else False
            module_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            i18n_dir = os.path.join(module_dir, 'i18n')

            if not lang or self.format == 'pot':
                # Xuất file template POT chuẩn gọn 100% từ i18n
                pot_file = os.path.join(i18n_dir, 'wujia_franchise.pot')
                if os.path.exists(pot_file):
                    with open(pot_file, 'rb') as f:
                        data = base64.encodebytes(f.read())
                    self.write({
                        'state': 'get',
                        'data': data,
                        'name': 'wujia_franchise.pot',
                    })
                    return {
                        'type': 'ir.actions.act_window',
                        'res_model': 'base.language.export',
                        'view_mode': 'form',
                        'res_id': self.id,
                        'views': [(False, 'form')],
                        'target': 'new',
                    }
            else:
                # Xuất file ngôn ngữ PO chuẩn gọn từ i18n
                po_file = os.path.join(i18n_dir, f"{lang}.po")
                if os.path.exists(po_file):
                    with open(po_file, 'rb') as f:
                        data = base64.encodebytes(f.read())
                    self.write({
                        'state': 'get',
                        'data': data,
                        'name': f"{tools.get_iso_codes(lang)}.po",
                    })
                    return {
                        'type': 'ir.actions.act_window',
                        'res_model': 'base.language.export',
                        'view_mode': 'form',
                        'res_id': self.id,
                        'views': [(False, 'form')],
                        'target': 'new',
                    }

        return super().act_getfile()
