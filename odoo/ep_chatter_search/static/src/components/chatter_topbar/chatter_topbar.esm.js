/** @odoo-module **/
import { ChatterTopbar } from "@mail/components/chatter_topbar/chatter_topbar";
import { deviceContext } from "@web_responsive/components/ui_context.esm";
import { patch } from "web.utils";

// Patch chatter topbar to add ui device context
patch(ChatterTopbar.prototype, "ep_chatter_search.ChatterTopbar.inherit", {
    setup() {
        this._super();
        this.ui = deviceContext;
    },

    async onClickSearch() {
        if (this.env && this.env.bus) {
            // Trigger the 'chatterTopbarButtonClicked' event
            await this.env.bus.trigger('chatterTopbarButtonClicked');
        }
    },

});