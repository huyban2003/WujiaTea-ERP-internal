from odoo import api, models

# Nhãn vai trò portal — một nguồn cho Home, trang Cửa hàng, dải cửa hàng mobile,
# khối Cửa hàng hiện tại PC và menu avatar. Portal giữ tiếng Việt.
ROLE_LABELS = {
    'owner': 'Chủ tiệm',
    'manager': 'Quản lý',
    'staff': 'Nhân viên',
}


class WujiaFranchiseMember(models.Model):
    _inherit = 'wujia.franchise.member'

    def _portal_role_label(self):
        self.ensure_one()
        return ROLE_LABELS.get(self.role, self.role or '')

    def _notify_franchise_realtime(self, action):
        bus = self.env['bus.bus'].sudo()
        for franchise_id in {m.franchise_id.id for m in self if m.franchise_id}:
            bus._sendone(
                f'wujia.franchise_{franchise_id}',
                'wujia_franchise_members_changed',
                {'franchise_id': franchise_id, 'action': action},
            )

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        records._notify_franchise_realtime('create')
        return records

    def write(self, vals):
        res = super().write(vals)
        self._notify_franchise_realtime('write')
        return res

    def unlink(self):
        affected_franchise_ids = list({
            m.franchise_id.id for m in self if m.franchise_id
        })
        res = super().unlink()
        bus = self.env['bus.bus'].sudo()
        for franchise_id in affected_franchise_ids:
            bus._sendone(
                f'wujia.franchise_{franchise_id}',
                'wujia_franchise_members_changed',
                {'franchise_id': franchise_id, 'action': 'unlink'},
            )
        return res
