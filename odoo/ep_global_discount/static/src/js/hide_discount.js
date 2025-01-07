/** @odoo-module **/

import { registry } from "@web/core/registry";
import { SectionAndNoteFieldOne2Many } from "@account/components/section_and_note_fields_backend/section_and_note_fields_backend";
import { SectionAndNoteListRenderer } from "@account/components/section_and_note_fields_backend/section_and_note_fields_backend";


export class EPSectionAndNoteListRenderer extends SectionAndNoteListRenderer {
    getRowClass(record) {
        const existingClasses = super.getRowClass(record);
        return `${existingClasses} ${record.data.is_discount_line ? 'd-none' : ''}`;
    }
}

export class EPSectionAndNoteFieldOne2Many extends SectionAndNoteFieldOne2Many { }
EPSectionAndNoteFieldOne2Many.components = {
    ...SectionAndNoteFieldOne2Many.components,
    ListRenderer: EPSectionAndNoteListRenderer,
};

registry.category("fields").add("section_and_note_one2many", EPSectionAndNoteFieldOne2Many, { force: true });
