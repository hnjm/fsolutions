odoo.define("print_report_preview.print_report_preview", async function(require) {
    "use strict";

    const {ActionContainer} = require("@web/webclient/actions/action_container");
    const {registry} = require("@web/core/registry");
    const {KeepLast} = require("@web/core/utils/concurrency");
    const {patch} = require("@web/core/utils/patch");
    const { session } = require('@web/session');
    const actionRegistry = registry.category("actions");

    var ReportPreviewDialog = require('print_report_preview.report_preview_dialog');
    
    let actionCache = {};
    var core = require("web.core");
    const _t = core._t;

    let wkhtmltopdfStateProm;
    const link = '<br><br><a href="http://wkhtmltopdf.org/" target="_blank">wkhtmltopdf.org</a>';

    function _getReportUrl(action, type) {
        let url = `/report/${type}/${action.report_name}`;
        const actionContext = action.context || {};
        if (action.data && JSON.stringify(action.data) !== "{}") {
            // build a query string with `action.data` (it's the place where reports
            // using a wizard to customize the output traditionally put their options)
            const options = encodeURIComponent(JSON.stringify(action.data));
            const context = encodeURIComponent(JSON.stringify(actionContext));
            url += `?options=${options}&context=${context}`;
        } else {
            if (actionContext.active_ids) {
                url += `/${actionContext.active_ids.join(",")}`;
            }
            if (type === "html") {
                const context = encodeURIComponent(JSON.stringify(env.services.user.context));
                url += `?context=${context}`;
            }
        }
        return url;
    }

    patch(ActionContainer.prototype, "print_report_preview.action_service", {

        setup() {
            this._super();
            const env = this.env;
            const keepLast = new KeepLast();
            env.bus.on("CLEAR-CACHES", null, () => {
                actionCache = {};
            });
            const _super = env.services.action.doAction;
            env.services.action.doAction = async function (actionRequest, options = {}) {
                const proms = _loadAction(actionRequest, options.additionalContext);
                let action = await keepLast.add(proms);
                
                if (action.type === "ir.actions.report" && action.report_type === "qweb-pdf") {
                    if(session.report_preview || session.report_automatic_printing){
                        if (!wkhtmltopdfStateProm) {
                            wkhtmltopdfStateProm = env.services.rpc("/report/check_wkhtmltopdf");
                        }
                        const state = await wkhtmltopdfStateProm;
                        const WKHTMLTOPDF_MESSAGES = {
                            broken:
                                env._t(
                                    "Your installation of Wkhtmltopdf seems to be broken. The report will be shown " +
                                        "in html."
                                ) + link,
                            install:
                                env._t(
                                    "Unable to find Wkhtmltopdf on this system. The report will be shown in " + "html."
                                ) + link,
                            upgrade:
                                env._t(
                                    "You should upgrade your version of Wkhtmltopdf to at least 0.12.0 in order to " +
                                        "get a correct display of headers and footers as well as support for " +
                                        "table-breaking between pages."
                                ) + link,
                            workers: env._t(
                                "You need to start Odoo with at least two workers to print a pdf version of " +
                                    "the reports."
                            ),
                        };
                        if (state in WKHTMLTOPDF_MESSAGES) {
                            env.services.notification.add(WKHTMLTOPDF_MESSAGES[state], {
                                sticky: true,
                                title: _t("Report"),
                            });
                        }
                        if (state === "upgrade" || state === "ok") {
                            const type = "pdf";
                            const reportUrl = _getReportUrl(action, type);
                            const title = action.name;
                            
                            if(session.report_preview){
                                new ReportPreviewDialog(this, reportUrl,  title)._onOpen();
                            }
                            if (session.report_automatic_printing) {                   
                                try {
                                    var pdf = window.open(reportUrl);
                                    pdf.print();    
                                }
                                catch(err) {
                                    this.doAction({
                                        type: "ir.actions.client",
                                        tag: "display_notification",
                                        params: {
                                            title: _t("Warning"),
                                            message: "Please allow pop upin your browser to preview report in another tab.",
                                            sticky: true,
                                        },
                                    });                                
                                }
                            }
                            return Promise.resolve();
                        }
                    }
                    if (!session.report_automatic_printing && !session.report_preview) {
                        _super(actionRequest, options);
                    }
                }else{
                    _super(actionRequest, options);
                }
            }

            async function _loadAction(actionRequest, context = {}) {
                if (typeof actionRequest === "string" && actionRegistry.contains(actionRequest)) {
                    // actionRequest is a key in the actionRegistry
                    return {
                        target: "current",
                        tag: actionRequest,
                        type: "ir.actions.client",
                    };
                }
        
                if (typeof actionRequest === "string" || typeof actionRequest === "number") {
                    // actionRequest is an id or an xmlid
                    const additional_context = {
                        active_id: context.active_id,
                        active_ids: context.active_ids,
                        active_model: context.active_model,
                    };
                    const key = `${JSON.stringify(actionRequest)},${JSON.stringify(additional_context)}`;
                    if (!actionCache[key]) {
                        actionCache[key] = env.services.rpc("/web/action/load", {
                            action_id: actionRequest,
                            additional_context,
                        });
                    }
                    const action = await actionCache[key];
                    if (!action) {
                        return {
                            type: "ir.actions.client",
                            tag: "invalid_action",
                            id: actionRequest,
                        };
                    }
                    return Object.assign({}, action);
                }
        
                // actionRequest is an object describing the action
                return actionRequest;
            }
        }

    });
});
