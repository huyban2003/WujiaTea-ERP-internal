odoo.define('fields_value.form_controller', function (require) {
    "use strict";

    var FormController = require('web.FormController');
    var Sidebar = require('web.Sidebar');
    var core = require('web.core');
    var _t = core._t;
    var config = require("web.config");

    Sidebar.include({
        _addToolbarActions: function (toolbarActions) {
            if ('other' in toolbarActions && 'field_values_action' in toolbarActions) {
                toolbarActions.other.unshift(toolbarActions.field_values_action);
                toolbarActions.field_values_action = null;
            }
            this._super(toolbarActions);
        }
    });

    FormController.include({
        renderSidebar: function ($node) {
            if (this.hasSidebar && config.isDebug()) {
                this.toolbarActions['field_values_action'] = {
                    label: _t('View fields value'),
                    callback: this._onOpenFieldsValue.bind(this)
                };
            }
            this._super($node);
        },
        _onOpenFieldsValue: function () {
            var state = this.initialState;
            this.do_action({
                type: 'ir.actions.act_window',
                view_mode: 'form',
                res_model: 'fields.value',
                views: [[false, 'form']],
                context: {
                    default_res_id: state.res_id,
                    default_model: state.model,
                    from_fields_value: true
                },
                target: 'new'
            });
        }
    })
});
