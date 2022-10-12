# -*- coding: utf-8 -*-

from odoo import models, fields

class ResCompany(models.Model):
    _inherit = 'res.company'

    discount_product_id = fields.Many2one('product.product',string='Discount Service')
    shipping_product_id = fields.Many2one('product.product',string='shipping Service')
    payment_fees_product_id = fields.Many2one('product.product',string='Payment Fees Service')


class PurchaseConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'


    discount_product_id = fields.Many2one('product.product',related='company_id.discount_product_id', readonly=False)
    shipping_product_id = fields.Many2one('product.product',related='company_id.shipping_product_id', readonly=False)
    payment_fees_product_id = fields.Many2one('product.product',related='company_id.payment_fees_product_id', readonly=False)
