import { DropdownItem } from "@web/core/dropdown/dropdown_item";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { Component } from "@odoo/owl";

const cogMenuRegistry = registry.category("cogMenu");

export class ViewFieldsValueCogMenu extends Component {
    static template = "fields_value.ViewFieldsValueCogMenu";
    static components = { DropdownItem };

    setup() {
        this.actionService = useService("action");
    }

    async onSelected() {
        const root = this.env?.model?.root;
        const resId = root?.resId;
        const resModel = root?.resModel || this.env?.config?.resModel;

        if (!resId || !resModel) {
            return;
        }

        await this.actionService.doAction({
            type: "ir.actions.act_window",
            name: "View Fields Value",
            res_model: "fields.value",
            views: [[false, "form"]],
            target: "new",
            context: {
                default_res_id: resId,
                default_model: resModel,
                from_fields_value: true,
            },
        });
    }
}

export const viewFieldsValueItem = {
    Component: ViewFieldsValueCogMenu,
    groupNumber: 20,
    isDisplayed: (env) => {
        return env?.config?.viewType === "form" && Boolean(env?.model?.root?.resId);
    },
};

cogMenuRegistry.add("fields-value-menu", viewFieldsValueItem, { sequence: 50 });
