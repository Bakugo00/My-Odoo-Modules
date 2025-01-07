/** @odoo-module **/
import { CalendarFilterPanel } from "@web/views/calendar/filter_panel/calendar_filter_panel";

import { patch } from "web.utils";
import { _t } from "@web/core/l10n/translation";
import { sprintf } from "@web/core/utils/strings";
import { SelectCreateDialog } from "@web/views/view_dialogs/select_create_dialog";



// Patch CalendarFilterPanel to add context
patch(CalendarFilterPanel.prototype, "ep_base.CalendarFilterPanel.inherit", {
    
    setup() {
        this._super(...arguments);
    },
     /**
     * @override
     */
    async loadSource(section, request) {
        const resModel = this.props.model.fields[section.fieldName].relation;
        const domain = [
            ["id", "not in", section.filters.filter((f) => f.type !== "all").map((f) => f.value)],
        ];
        const records = await this.orm.call(resModel, "name_search", [], {
            name: request,
            operator: "ilike",
            args: domain,
            limit: 8,
            context: {'show_portoflio_contacts': true},
        });

        const options = records.map((result) => ({
            value: result[0],
            label: result[1],
        }));

        if (records.length > 7) {
            options.push({
                label: _t("Search More..."),
                action: () => this.onSearchMore(section, resModel, domain, request),
            });
        }

        if (records.length === 0) {
            options.push({
                label: _t("No records"),
                classList: "o_m2o_no_result",
                unselectable: true,
            });
        }

        return options;
    },
    async onSearchMore(section, resModel, domain, request) {
        const dynamicFilters = [];
        if (request.length) {
            const nameGets = await this.orm.call(resModel, "name_search", [], {
                name: request,
                args: domain,
                operator: "ilike",
                context: {'show_portoflio_contacts': true},
            });
            dynamicFilters.push({
                description: sprintf(_t("Quick search: %s"), request),
                domain: [["id", "in", nameGets.map((nameGet) => nameGet[0])]],
            });
        }
        const title = sprintf(_t("Search: %s"), section.label);
        this.addDialog(SelectCreateDialog, {
            title,
            noCreate: true,
            multiSelect: false,
            resModel,
            context: {'show_portoflio_contacts': true},
            domain,
            onSelected: ([resId]) => this.props.model.createFilter(section.fieldName, resId),
            dynamicFilters,
        });
    }
},);

    
