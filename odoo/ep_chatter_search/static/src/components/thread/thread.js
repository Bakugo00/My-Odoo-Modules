/** @odoo-module **/

import { registerPatch } from '@mail/model/model_core';

registerPatch({
    name: 'Thread',
    recordMethods: {
    },
    fields: {
        orderedMessages: {
            compute() {
                return this.messages.sort((m1, m2) => m1.date < m2.date ? -1 : 1);
            },
        },
    },
});
