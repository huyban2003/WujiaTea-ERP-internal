/** @odoo-module **/

import { Component } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { standardActionServiceProps } from "@web/webclient/actions/action_service";

export class WujiaInspectionOverview extends Component {
    static template = "wujia_franchise_inspection.Overview";
    static props = {
        ...standardActionServiceProps,
    };

    setup() {
        this.overviewUrl = "/wujia_franchise_inspection/overview_embed?_t=" + Date.now();
    }
}

registry.category("actions").add("wujia_inspection_overview", WujiaInspectionOverview);
