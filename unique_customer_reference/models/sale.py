# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
from odoo.exceptions import UserError, ValidationError


class SaleOrder(models.Model):

    _inherit = 'sale.order'


    @api.constrains('client_order_ref')
    def unique_customer_reference(self):
        for rec in self:
            orders = self.env['sale.order'].sudo().search([('id','!=',rec.id),('client_order_ref','=',rec.client_order_ref)])
            if orders:
                raise ValidationError(_('The Customer Reference must be unique !'))




