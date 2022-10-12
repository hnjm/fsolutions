odoo.define('print_report_preview.user_menu_items', async function(require) {
    'use strict';

    let __exports = {};
    const { registry } = require("@web/core/registry");

    function printReportPreview(env)  {
        return {
            type: "item",
            id: "print_report_preview",
            description: env._t("Report Preview"),
            callback: async function () {
                const actionDescription = await env.services.orm.call("res.users", "action_get_print_report_preview");
                actionDescription.res_id = env.services.user.userId;
                env.services.action.doAction(actionDescription);
            },
            sequence: 5,
        };
    }

    registry.category("user_menuitems").add('print_report_preview', printReportPreview, { force: true })
    return __exports;
});