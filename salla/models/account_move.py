# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import base64

from odoo import api, fields, models, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError
from odoo.tools import float_compare, date_utils, email_split, email_re
from odoo.tools.misc import formatLang, format_date, get_lang


class AccountInvoice(models.Model):
    _inherit = "account.move"


    discount_amount = fields.Float('Discount',readonly=True, states={'draft': [('readonly', False)]})
    shipping_cost = fields.Float('Shipping Cost',readonly=True, states={'draft': [('readonly', False)]})
    payment_fees = fields.Float('Payment Fees',readonly=True, states={'draft': [('readonly', False)]})
    analytic_account_id = fields.Many2one('account.analytic.account', string="Analytic Account",readonly=True, states={'draft': [('readonly', False)]})

    def _get_computed_account(self, product_id):
        self.ensure_one()
        self = self.with_company(self.journal_id.company_id)
        if not product_id:
            return
        fiscal_position = self.fiscal_position_id
        accounts = product_id.product_tmpl_id.get_product_accounts(fiscal_pos=fiscal_position)
        if self.is_sale_document(include_receipts=True):
            # Out invoice.
            return accounts['income']
        elif self.is_purchase_document(include_receipts=True):
            # In invoice.
            return accounts['expense']

    @api.constrains('discount_amount')
    def supply_discount_amount(self):
        for move in self.filtered(lambda x:x.discount_amount != 0.0):
            product = self.company_id.discount_product_id
            if not product:
                raise ValidationError(_('please,You should select Discount product in accounting setting'))
            discount_val = move.invoice_line_ids.filtered(
                lambda line: line.product_id == product)
            account_id = self._get_computed_account(product)
            line_val = {'product_id': product.id,
                        'name': product.name,
                        'quantity': 1.0,
                        'product_uom_id': product.uom_id.id,
                        'currency_id': move.currency_id.id,
                        'analytic_account_id': move.analytic_account_id.id or False,
                        'account_id': account_id.id,
                        'price_unit': - move.discount_amount}
            if not discount_val:
                move.update({'invoice_line_ids': [(0, 0, line_val)]})
            else:
                discount_val.update(line_val)
            for line in move.line_ids:
                line._onchange_price_subtotal()
            move._onchange_recompute_dynamic_lines()
            move._compute_tax_totals_json()


    @api.constrains('shipping_cost')
    def supply_shipping_cost(self):
        for move in self.filtered(lambda x:x.shipping_cost != 0.0):
            product = self.company_id.shipping_product_id
            if not product:
                raise ValidationError(_('please,You should select Shipping product in accounting setting'))
            shipping_val = move.invoice_line_ids.filtered(
                lambda line: line.product_id == product)
            account_id = self._get_computed_account(product)
            line_val = {'product_id': product.id,
                        'name': product.name,
                        'quantity': 1.0,
                        'product_uom_id': product.uom_id.id,
                        'currency_id': move.currency_id.id,
                        'analytic_account_id': move.analytic_account_id.id or False,
                        'account_id': account_id.id,
                        'price_unit': move.shipping_cost}
            if not shipping_val:
                move.update({'invoice_line_ids': [(0, 0, line_val)]})
            else:
                shipping_val.update(line_val)
            for line in move.line_ids:
                line._onchange_price_subtotal()
            move._onchange_recompute_dynamic_lines()
            move._compute_tax_totals_json()


    @api.constrains('payment_fees')
    def supply_payment_fees(self):
        for move in self.filtered(lambda x:x.payment_fees != 0.0):
            product = self.company_id.payment_fees_product_id
            if not product:
                raise ValidationError(_('please,You should select Payment Fees product in accounting setting'))
            payment_val = move.invoice_line_ids.filtered(
                lambda line: line.product_id == product)
            account_id = self._get_computed_account(product)
            line_val = {'product_id': product.id,
                        'name': product.name,
                        'quantity': 1.0,
                        'product_uom_id': product.uom_id.id,
                        'currency_id': move.currency_id.id,
                        'analytic_account_id':move.analytic_account_id.id or False,
                        'account_id': account_id.id,
                        'price_unit': move.payment_fees}
            if not payment_val:
                move.update({'invoice_line_ids': [(0, 0, line_val)]})
            else:
                payment_val.update(line_val)
            for line in move.line_ids:
                line._onchange_price_subtotal()
            move._onchange_recompute_dynamic_lines()
            move._compute_tax_totals_json()


    @api.onchange('analytic_account_id')
    @api.constrains('analytic_account_id')
    def onchange_analytic_account_id(self):
        for move in self.filtered(lambda x:x.analytic_account_id):
            for line in move.invoice_line_ids:
                line.analytic_account_id = move.analytic_account_id.id




