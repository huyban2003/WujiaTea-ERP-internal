from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


ROLE_OWNER = 'owner'
ROLE_MANAGER = 'manager'
ROLE_STAFF = 'staff'

ROLE_RANK = {ROLE_STAFF: 1, ROLE_MANAGER: 2, ROLE_OWNER: 3}


class WujiaFranchiseMember(models.Model):
    _name = 'wujia.franchise.member'
    _description = 'Wujia Franchise Membership'
    _order = 'franchise_id, is_primary_owner desc, date_from desc, id desc'
    _rec_name = 'display_name'

    user_id = fields.Many2one(
        'res.users',
        string='User',
        required=True,
        ondelete='cascade',
        index=True,
    )
    franchise_id = fields.Many2one(
        'wujia.franchise.management',
        string='Cửa hàng nhượng quyền',
        required=True,
        ondelete='cascade',
        index=True,
    )
    role = fields.Selection(
        [
            (ROLE_OWNER, 'Chủ tiệm'),
            (ROLE_MANAGER, 'Quản lý'),
            (ROLE_STAFF, 'Nhân viên'),
        ],
        string='Role',
        required=True,
        default=ROLE_STAFF,
    )
    is_primary_owner = fields.Boolean(
        string='Chủ chính',
        default=False,
        help='Đánh dấu chủ chính của cửa hàng. Mỗi cửa hàng chỉ có 1 chủ chính.',
    )
    date_from = fields.Date(
        string='Hiệu lực từ',
        default=fields.Date.context_today,
    )
    date_to = fields.Date(string='Hiệu lực đến')
    active = fields.Boolean(default=True)

    display_name = fields.Char(compute='_compute_display_name', store=True)
    is_currently_valid = fields.Boolean(
        compute='_compute_is_currently_valid',
        store=True,
        index=True,
    )

    @api.depends('user_id.name', 'franchise_id.display_name', 'role')
    def _compute_display_name(self):
        role_label = dict(self._fields['role']._description_selection(self.env))
        for rec in self:
            rec.display_name = '%s @ %s (%s)' % (
                rec.user_id.name or '',
                rec.franchise_id.display_name or '',
                role_label.get(rec.role, ''),
            )

    @api.depends('active', 'date_from', 'date_to')
    def _compute_is_currently_valid(self):
        today = fields.Date.context_today(self)
        for rec in self:
            rec.is_currently_valid = bool(
                rec.active
                and (not rec.date_from or rec.date_from <= today)
                and (not rec.date_to or rec.date_to >= today)
            )

    @api.constrains('date_from', 'date_to')
    def _check_dates(self):
        for rec in self:
            if rec.date_from and rec.date_to and rec.date_to < rec.date_from:
                raise ValidationError(_("Ngày kết thúc phải >= ngày bắt đầu."))

    @api.constrains('is_primary_owner', 'role', 'franchise_id', 'active')
    def _check_primary_owner(self):
        for rec in self:
            if not rec.is_primary_owner:
                continue
            if rec.role != ROLE_OWNER:
                raise ValidationError(_("Chủ chính phải có role = Chủ tiệm."))
            duplicate = self.search([
                ('franchise_id', '=', rec.franchise_id.id),
                ('is_primary_owner', '=', True),
                ('active', '=', True),
                ('id', '!=', rec.id),
            ], limit=1)
            if duplicate:
                raise ValidationError(_(
                    "Cửa hàng '%s' đã có chủ chính. Hủy active membership cũ trước.",
                    rec.franchise_id.display_name,
                ))

    @api.constrains('user_id', 'franchise_id', 'active')
    def _check_unique_active(self):
        for rec in self:
            if not rec.active:
                continue
            duplicate = self.search([
                ('user_id', '=', rec.user_id.id),
                ('franchise_id', '=', rec.franchise_id.id),
                ('active', '=', True),
                ('id', '!=', rec.id),
            ], limit=1)
            if duplicate:
                raise ValidationError(_(
                    "User '%s' đã có membership active trong cửa hàng '%s'.",
                    rec.user_id.name, rec.franchise_id.display_name,
                ))

    @api.model
    def find_active_membership(self, user_id, franchise_id):
        return self.search([
            ('user_id', '=', user_id),
            ('franchise_id', '=', franchise_id),
            ('is_currently_valid', '=', True),
        ], limit=1)

    def has_role(self, role):
        self.ensure_one()
        return ROLE_RANK.get(self.role, 0) >= ROLE_RANK.get(role, 99)

    # ===========================================================
    # Cache invalidation + cron recompute
    # ===========================================================
    def _invalidate_user_cache(self):
        # Clear ormcache trên _get_accessible_franchise_ids.
        # registry.clear_cache() invalidate cross-worker (Odoo signal qua DB).
        if self:
            self.env.registry.clear_cache()

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        records._invalidate_user_cache()
        return records

    def write(self, vals):
        res = super().write(vals)
        self._invalidate_user_cache()
        return res

    def unlink(self):
        had_records = bool(self)
        res = super().unlink()
        if had_records:
            self.env.registry.clear_cache()
        return res

    @api.model
    def _cron_recompute_validity(self):
        # Re-trigger compute cho membership chuyển trạng thái valid/invalid theo ngày.
        from datetime import timedelta
        today = fields.Date.context_today(self)
        affected = self.search([
            '|',
            ('date_from', '=', today),
            ('date_to', '=', today - timedelta(days=1)),
        ])
        if affected:
            affected._compute_is_currently_valid()
            affected.flush_recordset()
            affected._invalidate_user_cache()
