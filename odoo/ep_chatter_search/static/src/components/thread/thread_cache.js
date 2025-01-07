/** @odoo-module **/

import { registerPatch } from '@mail/model/model_core';

registerPatch({
    name: 'ThreadCache',
    recordMethods: {
    },
    fields: {
        orderedFetchedMessages:  {
            compute() {
                return this.fetchedMessages.sort((m1, m2) => m1.date < m2.date ? -1 : 1);
            },
        },
        /**
         * Ordered list of messages linked to this cache.
         */
        orderedMessages: {
            compute() {
                return this.messages.sort((m1, m2) => m1.date < m2.date ? -1 : 1);
            },
        },
    },
});
