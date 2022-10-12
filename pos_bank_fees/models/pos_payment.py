from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_compare

from itertools import groupby


class POSPayment(models.Model):
    _inherit = 'pos.payment'

    fees_percent_account_id = fields.Many2one('account.account', related='payment_method_id.fees_percent_account_id',
                                              string='Account')
    fees_fixed_account_id = fields.Many2one('account.account', related='payment_method_id.fees_fixed_account_id',
                                            string='Account')
    have_fees = fields.Boolean(related='payment_method_id.have_fees')
    tax_id = fields.Many2one('account.tax', related='payment_method_id.tax_id')
    tax_account_id = fields.Many2one('account.account', related='payment_method_id.tax_account_id',
                                     string='Account')
    fees_move_id = fields.Many2one('account.move', string='Fees Entry', readonly=1)

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
                'journal_id': self.payment_method_id.fees_journal_id.id,
                'currency_id': self.currency_id.id,
            }))
        if fixed > 0.0:
            total += fixed
            vals.append((0, 0, {
                'name': 'Bank Fixed Fees',
                'account_id': self.fees_fixed_account_id.id,
                'debit': fixed,
                'credit': 0.0,
                'journal_id': self.payment_method_id.fees_journal_id.id,
                'currency_id': self.currency_id.id,
            }))
        if total > 0.0:
            tax = total * (self.tax_id.amount / 100)
            vals.append((0, 0, {
                'name': self.tax_id.description,
                'account_id': self.tax_account_id.id,
                'debit': tax,
                'credit': 0.0,
                'journal_id': self.payment_method_id.fees_journal_id.id,
                'currency_id': self.payment_method_id.fees_journal_id.id,
            }))
            vals.append((0, 0, {
                'name': 'Bank Fees',
                'account_id': self.payment_method_id.fees_credit_account_id.id,
                'debit': 0.0,
                'credit': total + tax,
                'journal_id': self.payment_method_id.fees_journal_id.id,
                'currency_id': self.currency_id.id,
            }))
        if vals:
            move_vals = {
                'ref': _('Bank Fees %s') % self.session_id.name,
                'date': self.payment_date,
                'journal_id': self.payment_method_id.fees_journal_id.id,
                'line_ids': vals,
            }
            fees_move_id = self.env['account.move'].create(move_vals)
            fees_move_id.post()
            self.fees_move_id = fees_move_id.id

class PosSession(models.Model):
    _inherit = 'pos.session'


    def _validate_session(self, balancing_account=False, amount_to_balance=0, bank_payment_method_diffs=None):
        res = super(PosSession, self)._validate_session(balancing_account=False, amount_to_balance=0, bank_payment_method_diffs=None)
        payments= self.env['pos.payment'].search([('session_id', '=', self.id), ('have_fees', '=', True)])
        for payment in payments:
            fees = ((payment.payment_method_id.fees_percent / 100) * payment.amount) if payment.payment_method_id.fees_percent > 0.0 else 0.0
            commission = payment.payment_method_id.fees_amount
            payment.create_fees_entry(fees, commission)
        return res
