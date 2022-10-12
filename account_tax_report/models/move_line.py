from odoo import fields, models, api, _
from odoo.http import request
import ast

from odoo.exceptions import AccessError, UserError, AccessDenied


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    """Function is updated to avoid conflict for new and old odoo V15 addons"""
    partner_vat = fields.Char(string='Partner Vat ID', related="partner_id.vat", store=True)
    amount_after_tax = fields.Monetary(compute='_compute_amount_tax_report', string="Total After Vat")
    tax_base_amount_per_type = fields.Monetary(compute='_compute_amount_tax_report', string="Total Amount", store=True)
    tax_amount = fields.Monetary(compute='_compute_amount_tax_report', string="Tax Amount", store=True)

    @api.depends('tax_base_amount', 'amount_currency')
    def _compute_amount_tax_report(self):
        for rec in self:
            tax_base_amount_per_type = 0.0
            if rec.move_id.move_type in ['out_invoice', 'in_refund']:
                tax_base_amount_per_type += rec.tax_base_amount
            elif rec.move_id.move_type in ['out_refund', 'in_invoice']:
                tax_base_amount_per_type += rec.tax_base_amount * -1
            rec.tax_base_amount_per_type = tax_base_amount_per_type
            rec.amount_after_tax = rec.tax_base_amount + abs(rec.amount_currency)
            rec.tax_amount = rec.amount_currency * -1
