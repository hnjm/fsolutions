/* Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
/* License URL : <https://store.webkul.com/license.html/> */
odoo.define('pos_invoice_print_without_download.model', function (require) {
    'use strict';

    var pos_model = require("point_of_sale.models");
    var SuperPosModel = pos_model.PosModel.prototype;


    pos_model.PosModel = pos_model.PosModel.extend({


        push_and_invoice_order: function (order) {
            var self = this;
            console.log('inside self.config-----------:',self.config.invoice_print)
            return new Promise((resolve, reject) => {
                if (!order.get_client()) {
                    reject({ code: 400, message: 'Missing Customer', data: {} });
                } else {
                    var order_id = self.db.add_order(order.export_as_JSON());
                    self.flush_mutex.exec(async () => {
                        try {
                            const server_ids = await self._flush_orders([self.db.get_order(order_id)], {
                                timeout: 30000,
                                to_invoice: true,
                            });
                            if (server_ids.length) {
                                const [orderWithInvoice] = await self.rpc({
                                    method: 'read',
                                    model: 'pos.order',
                                    args: [server_ids, ['account_move']],
                                    kwargs: { load: false },
                                });
                                if(self.config.invoice_print){
                                    console.log('orderWithInvoice.account_move----:',orderWithInvoice.account_move)
                                    order.invoice_id = orderWithInvoice.account_move

                                  
                                     // await self
                                //     .do_action('account.account_invoices', {
                                //         additional_context: {
                                //             active_ids: [orderWithInvoice.account_move],
                                //         },
                                //     })
                                //     .catch(() => {
                                //         reject({ code: 401, message: 'Backend Invoice', data: { order: order } });
                                //     });

                                }
                                else{

                                    order.invoice_id = orderWithInvoice.account_move
                                 

                                    await self
                                    .do_action('account.account_invoices', {
                                        additional_context: {
                                            active_ids: [orderWithInvoice.account_move],
                                        },
                                    })
                                    .catch(() => {
                                        reject({ code: 401, message: 'Backend Invoice', data: { order: order } });
                                    });
                                }
                               
                            } else {
                                reject({ code: 401, message: 'Backend Invoice', data: { order: order } });
                            }
                            resolve(server_ids);
                        } catch (error) {
                            reject(error);
                        }
                    });
                }
            });
        },
    })
});
