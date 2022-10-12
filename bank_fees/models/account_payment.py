from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_compare

from itertools import groupby


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    fees_percent_account_id = fields.Many2one('account.account', related='journal_id.fees_percent_account_id',
                                              string='Account')
    fees_fixed_account_id = fields.Many2one('account.account', related='journal_id.fees_fixed_account_id',
                                            string='Account')
    have_fees = fields.Boolean(related='journal_id.have_fees')
    tax_id = fields.Many2one('account.tax', related='journal_id.tax_id')
    tax_account_id = fields.Many2one('account.account', related='journal_id.tax_account_id',
                                            string='Account')
    fees_percent = fields.Float('Fees (%)')
    fees_amount = fields.Float('Fees Fixed Amount')
    fees_move_id = fields.Many2one('account.move', string='Fees Entry',readonly=1)
    writeoff_account_id = fields.Many2one('account.account', string="Difference Account", copy=False,
        domain="[('deprecated', '=', False), ('company_id', '=', company_id)]")
    writeoff_label = fields.Char(string='Journal Item Label', default='Write-Off')
    payment_difference = fields.Monetary()

    @api.constrains('fees_percent', 'fees_amount')
    def _check_fees(self):
        for payment in self:
            if payment.fees_percent < 0.0 or payment.fees_amount < 0.0:
                raise ValidationError(_("You can't add Negative value in Fees !"))
            if payment.fees_percent > 100:
                raise ValidationError(_("You can't add above 100 % value in Fees !"))



    @api.onchange('journal_id')
    def onchange_journal_fees(self):
        if self.have_fees:
            self.fees_percent = self.journal_id.fees_percent
            self.fees_amount = self.journal_id.fees_amount

    def create_fees_entry(self, percent, fixed):
        total = 0.0
        vals = []
        if percent > 0.0:
            total += percent
            vals.append((0, 0, {
                'name': 'Bank Percent Fees',
                'account_id': self.fees_percent_account_id.id,
                'debit': percent,
                'credit': 0.0,
                'journal_id': self.journal_id.id,
                'partner_id': self.partner_id.id,
                'currency_id': self.currency_id.id,
            }))
        if fixed > 0.0:
            total += fixed
            vals.append((0, 0, {
                'name': 'Bank Fixed Fees',
                'account_id': self.fees_fixed_account_id.id,
                'debit': fixed,
                'credit': 0.0,
                'journal_id': self.journal_id.id,
                'partner_id': self.partner_id.id,
                'currency_id': self.currency_id.id,
            }))
        if total > 0.0:
            tax = total * (self.tax_id.amount/100)
            vals.append((0, 0, {
                'name': self.tax_id.description,
                'account_id': self.tax_account_id.id,
                'debit': tax,
                'credit': 0.0,
                'journal_id': self.journal_id.id,
                'partner_id': self.partner_id.id,
                'currency_id': self.currency_id.id,
            }))
            vals.append((0, 0, {
                'name': 'Bank Fees',
                'account_id': self.journal_id.default_account_id.id,
                'debit': 0.0,
                'credit': total + tax,
                'journal_id': self.journal_id.id,
                'partner_id': self.partner_id.id,
                'currency_id': self.currency_id.id,
            }))
        if vals:
            move_vals = {
                'ref': _('Bank Fees %s') % self.name,
                'date': self.date,
                'journal_id': self.journal_id.id,
                'line_ids': vals,
            }
            fees_move_id = self.env['account.move'].create(move_vals)
            fees_move_id.post()
            self.fees_move_id = fees_move_id.id

    @api.model_create_multi
    def create(self, vals_list):
        for val in vals_list:
            if 'payment_difference' in val:
                val['write_off_line_vals'] = {
                    'name': val['writeoff_label'],
                    'amount': val['payment_difference'],
                    'account_id': self.env['account.account'].browse(val['writeoff_account_id']).id
                }
        payments = super().create(vals_list)
        return payments

    def action_post(self):
        res = super(AccountPayment, self).action_post()
        for payment in self.filtered(lambda p: p.have_fees and p.payment_type == "outbound"):
            fees = ((payment.fees_percent / 100) * payment.amount) if payment.fees_percent > 0.0 else 0.0
            commission = payment.fees_amount
            payment.create_fees_entry(fees, commission)
        return res


class AccountPaymentRegister(models.TransientModel):
    _inherit = "account.payment.register"

    fees_percent_account_id = fields.Many2one('account.account', related='journal_id.fees_percent_account_id',
                                              string='Account')
    fees_fixed_account_id = fields.Many2one('account.account', related='journal_id.fees_fixed_account_id',
                                            string='Account')
    have_fees = fields.Boolean(related='journal_id.have_fees')
    tax_id = fields.Many2one('account.tax', related='journal_id.tax_id')
    tax_account_id = fields.Many2one('account.account', related='journal_id.tax_account_id',
                                     string='Account')
    fees_percent = fields.Float('Fees (%)')
    fees_amount = fields.Float('Fees Fixed Amount')

    @api.constrains('fees_percent', 'fees_amount')
    def _check_fees(self):
        for payment in self:
            if payment.fees_percent < 0.0 or payment.fees_amount < 0.0:
                raise ValidationError(_("You can't add Negative value in Fees !"))
            if payment.fees_percent > 100:
                raise ValidationError(_("You can't add above 100 % value in Fees !"))

    @api.onchange('journal_id')
    def onchange_journal_fees(self):
        if self.have_fees:
            self.fees_percent = self.journal_id.fees_percent
            self.fees_amount = self.journal_id.fees_amount

    def create_fees_entry(self, percent, fixed,payment):
        total = 0.0
        vals = []
        if percent > 0.0:
            total += percent
            vals.append((0, 0, {
                'name': 'Bank Percent Fees',
                'account_id': self.fees_percent_account_id.id,
                'debit': percent,
                'credit': 0.0,
                'journal_id': self.journal_id.id,
                'partner_id': self.partner_id.id,
                'currency_id': self.currency_id.id,
            }))
        if fixed > 0.0:
            total += fixed
            vals.append((0, 0, {
                'name': 'Bank Fixed Fees',
                'account_id': self.fees_fixed_account_id.id,
                'debit': fixed,
                'credit': 0.0,
                'journal_id': self.journal_id.id,
                'partner_id': self.partner_id.id,
                'currency_id': self.currency_id.id,
            }))
        if total > 0.0:
            tax = total * (self.tax_id.amount/100)
            vals.append((0, 0, {
                'name': self.tax_id.description,
                'account_id': self.tax_account_id.id,
                'debit': tax,
                'credit': 0.0,
                'journal_id': self.journal_id.id,
                'partner_id': self.partner_id.id,
                'currency_id': self.currency_id.id,
            }))
            vals.append((0, 0, {
                'name': 'Bank Fees',
                'account_id': self.journal_id.default_account_id.id,
                'debit': 0.0,
                'credit': total + tax,
                'journal_id': self.journal_id.id,
                'partner_id': self.partner_id.id,
                'currency_id': self.currency_id.id,
            }))
        if vals:
            move_vals = {
                'ref': _('Bank Fees %s') % payment.name,
                'date': self.payment_date,
                'journal_id': self.journal_id.id,
                'line_ids': vals,
            }
            fees_move_id = self.env['account.move'].create(move_vals)
            fees_move_id.post()
            payment.fees_move_id = fees_move_id.id

    def _create_payments(self):
        payments = super(AccountPaymentRegister, self)._create_payments()
        for pay in payments:
            if self.have_fees and self.payment_type == "outbound" and len(payments) == 1:
                fees = ((self.fees_percent / 100) * self.amount) if self.fees_percent > 0.0 else 0.0
                commission = self.fees_amount
                self.create_fees_entry(fees, commission,pay)

        return payments