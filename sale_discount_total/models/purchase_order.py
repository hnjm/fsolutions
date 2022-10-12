# -*- coding: utf-8 -*-
#############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2019-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Author: Faslu Rahman(odoo@cybrosys.com)
#
#    You can modify it under the terms of the GNU AFFERO
#    GENERAL PUBLIC LICENSE (AGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU AFFERO GENERAL PUBLIC LICENSE (AGPL v3) for more details.
#
#    You should have received a copy of the GNU AFFERO GENERAL PUBLIC LICENSE
#    (AGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################

from odoo import api, fields, models, _
import odoo.addons.decimal_precision as dp
from odoo.exceptions import AccessError, UserError, ValidationError


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    @api.depends('order_line.price_total', 'discount_type', 'discount_rate')
    def _amount_all(self):
        for order in self:
            amount_untaxed = amount_tax = amount_discount = 0.0
            for line in order.order_line:
                line._compute_amount()
                amount_untaxed += line.price_subtotal
                amount_tax += line.price_tax
                amount_discount += (line.product_qty * line.price_unit * line.discount) / 100
            currency = order.currency_id or order.partner_id.property_purchase_currency_id or self.env.company.currency_id
            order.update({
                'amount_untaxed': currency.round(amount_untaxed),
                'amount_tax': currency.round(amount_tax),
                'amount_discount': amount_discount,
                'amount_total': amount_untaxed + amount_tax,
                'amount_before_discount': amount_untaxed + amount_discount
            })

    discount_type = fields.Selection([('percent', 'Percentage'), ('amount', 'Amount')], string='Discount type',
                                     readonly=True,
                                     states={'draft': [('readonly', False)], 'sent': [('readonly', False)]})
    discount_rate = fields.Float('Discount Rate', digits=dp.get_precision('Account'))
    amount_discount = fields.Monetary(string='Discount', store=True, readonly=True, compute='_amount_all',
                                      digits=dp.get_precision('Account'), track_visibility='always')
    amount_before_discount = fields.Monetary(string='Total before discount', store=True, readonly=True,
                                             compute='_amount_all',
                                             digits=dp.get_precision('Account'), track_visibility='always')

    @api.onchange('discount_type', 'discount_rate', 'order_line')
    def supply_rate(self):
        for order in self:
            if order.discount_rate < 0.0:
                raise ValidationError(_("You can't add Negative value !"))
            if order.discount_rate > order.amount_untaxed:
                raise ValidationError(_("You can't add value above total!"))
            if order.discount_rate > 100:
                raise ValidationError(_("You can't add above 100 % value in Discount!"))
            if order.discount_type:
                if order.discount_type == 'percent':
                    for line in order.order_line:
                        line.discount = order.discount_rate
                else:
                    total = discount = 0.0
                    for line in order.order_line:
                        total += (line.product_qty * line.price_unit)
                    for line in order.order_line:
                        if order.discount_rate != 0:
                            if line != order.order_line[-1]:
                                line.discount = round((order.discount_rate / total) * 100)
                                discount += round((order.discount_rate / total) * 100)
                            else:
                                remind = ((order.discount_rate / total) * 100) * len(order.order_line)
                                line.discount = remind - discount
                        else:
                            line.discount = order.discount_rate
            else:
                order.discount_rate = 0.0

    def _prepare_invoice(self, ):
        invoice_vals = super(PurchaseOrder, self)._prepare_invoice()
        invoice_vals.update({
            'discount_type': self.discount_type,
            'discount_rate': self.discount_rate,
        })
        return invoice_vals

    def button_dummy(self):

        self.supply_rate()
        return True


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    discount = fields.Float(string='Discount (%)', digits=(16, 2), default=0.0)

    @api.constrains('discount')
    def _constrains_discount(self):
        for order in self:
            if order.discount < 0.0:
                raise ValidationError(_("You can't add Negative value in Discount!"))
            if order.discount > 100:
                raise ValidationError(_("You can't add above 100 % value in Discount!"))

    def _prepare_compute_all_values(self):
        # Hook method to returns the different argument values for the
        # compute_all method, due to the fact that discounts mechanism
        # is not implemented yet on the purchase orders.
        # This method should disappear as soon as this feature is
        # also introduced like in the sales module.
        self.ensure_one()
        return {
            'price_unit': self.price_unit * (1 - (self.discount or 0.0) / 100.0),
            'currency': self.order_id.currency_id,
            'quantity': self.product_qty,
            'product': self.product_id,
            'partner': self.order_id.partner_id,
        }
