# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError

class DailyPurchaseReport(models.AbstractModel):
    _name = 'report.pways_daily_purchase_report.daily_template_id'

    @api.model
    def _get_report_values(self, docids, data=None):
        partner_dict = {}
        product_dict = {}
        docs = {}
        purchase_ids = data.get('order_ids')
        if not purchase_ids:
            raise UserError('Nothing to print. Purchase order must be confirmed !')
        order_ids = self.env['purchase.order'].browse(purchase_ids)
        lines = order_ids.mapped('order_line').filtered(lambda x: x.product_qty > 0)

        for line in lines:
            if line.order_id.partner_id not in partner_dict:
                partner_dict[line.order_id.partner_id] = line
            else:
                partner_dict[line.order_id.partner_id] |= line
        for key, values in partner_dict.items():
            prod_list = []
            for prod in values.mapped('product_id'):
                po_line = self.env['purchase.order.line'].search([('product_id', '=', prod.id), ('order_id.partner_id', '=', key.id), ('order_id.state', '=', 'purchase')])
                line_total = sum(po_line.mapped('price_unit')) * sum(po_line.mapped('product_qty'))
                line_avg = line_total / len(po_line)
                line_dict = {
                    'product_id': po_line[0].product_id,
                    'qty': sum(po_line.mapped('product_qty')),
                    'price': sum(po_line.mapped('price_unit')) / len(po_line),
                    'uom':po_line[0].product_id.uom_po_id.name,
                    'total': line_avg,
                }
                prod_list.append(line_dict)
            product_dict[key] = prod_list
        docs['records'] = product_dict
        return docs