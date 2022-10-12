odoo.define('mai_pos_session_report_thermal.PosSessionPDFReportButton', function(require) {
    'use strict';

    const PosComponent = require('point_of_sale.PosComponent');
    const ProductScreen = require('point_of_sale.ProductScreen');
    const { useListener } = require('web.custom_hooks');
    const Registries = require('point_of_sale.Registries');

    class PosSessionPDFReportButton extends PosComponent {
        constructor() {
            super(...arguments);
            useListener('click', this.onClick);
        }
        async onClick() {
            var self = this;
            const order = this.env.pos.get_order();
            // if (order.get_orderlines().length > 0) {
            // var self = this;
            var pos_session_id = this.env.pos.pos_session.id;
            // let order = this.props.order;
            let download_invoice = await this.env.pos.do_action('mai_pos_session_report_thermal.action_report_session', {
                additional_context: {
                    active_ids: [pos_session_id]
                }
            })
            return download_invoice
            // } else {
            //     await this.showPopup('ErrorPopup', {
            //         title: this.env._t('Nothing to Print'),
            //         body: this.env._t('There are no order lines'),
            //     });
            // }
        }

    }
    PosSessionPDFReportButton.template = 'PosSessionPDFReportButton';

    ProductScreen.addControlButton({
        component: PosSessionPDFReportButton,
        condition: function() {
            return this.env.pos.config.do_session_report;
        },
    });

    Registries.Component.add(PosSessionPDFReportButton);

    return PosSessionPDFReportButton;
});



odoo.define('mai_pos_session_report_thermal.session_report', function (require) {
"use strict";

var gui = require('point_of_sale.gui');
var models = require('point_of_sale.models');
var screens = require('point_of_sale.screens');
var core = require('web.core');
var ActionManager = require('web.ActionManager');

var QWeb = core.qweb;

var SessionReportPrintButton = screens.ActionButtonWidget.extend({
    template: 'SessionReportPrintButton',
    button_click: function(){
        var self = this;
        var pos_session_id = self.pos.pos_session.id;

        var action = {
            'type': 'ir.actions.report',
            'report_type': 'qweb-pdf',
            'report_file': 'mai_pos_session_report_thermal.report_pos_session_pdf/'+pos_session_id.toString(),
            'report_name': 'mai_pos_session_report_thermal.report_pos_session_pdf/'+pos_session_id.toString(),
            'data': self.data,
            'context': {'active_id': [pos_session_id]},
        };
        return this.do_action(action);
    },
});

screens.define_action_button({
    'name': 'session_report_print',
    'widget': SessionReportPrintButton,
    'condition': function(){ 
        return this.pos.config.do_session_report;
    },
});
return {
    SessionReportPrintButton: SessionReportPrintButton,
};
});