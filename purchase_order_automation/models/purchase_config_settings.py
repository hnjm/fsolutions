# -*- coding: utf-8 -*-

from odoo import models, fields

class ResCompany(models.Model):
    _inherit = 'res.company'

    is_purchase_deliver = fields.Boolean(string='Is Purchase Delivery Done')
    is_create_bill = fields.Boolean(string='Create Supplier Bill')
    is_validate_bill = fields.Boolean(string='Validate Supplier Bill')


class PurchaseConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'


    is_purchase_deliver = fields.Boolean(related='company_id.is_purchase_deliver', readonly=False)
    is_create_bill = fields.Boolean(related='company_id.is_create_bill', readonly=False)
    is_validate_bill = fields.Boolean(related='company_id.is_validate_bill', readonly=False)
