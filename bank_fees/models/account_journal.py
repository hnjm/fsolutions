# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    have_fees = fields.Boolean()
    fees_percent_account_id = fields.Many2one('account.account', string='Fees Percent Account')
    fees_fixed_account_id = fields.Many2one('account.account', string='Fees Fixed Account')
    tax_id = fields.Many2one('account.tax')
    tax_account_id = fields.Many2one('account.account', string='Tax Account')
    fees_percent = fields.Float('Fees (%)')
    fees_amount = fields.Float('Fees Fixed Amount')

