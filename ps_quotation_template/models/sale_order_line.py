# -*- coding: utf-8 -*-
#############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2020-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
#    Author: Cybrosys Techno Solutions(<https://www.cybrosys.com>)
#
#    You can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################
from odoo import fields, models,api
from odoo.exceptions import ValidationError, UserError

class SaleOrderLine(models.Model):
    _inherit = 'sale.order'

    is_print_image = fields.Boolean('Print Image?')

    # @api.depends('amount_untaxed')
    # def _compute_per_amount(self):
    #     for rec in self:
    #         rec.per_amount = rec.amount_untaxed * (20 /100)

    # @api.onchange('amount_untaxed')
    # def onchange_per_amount(self):
    #     self.per_amount = self.amount_untaxed * (20 /100)

    # related='partner_id.vat'

    # @api.constrains('per_amount')
    # def _constrain_per_amount(self):
    #     for rec in self:
    #         if rec.per_amount < 0.0:
    #             raise ValidationError("You Should add value in Per amount")

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    order_line_image = fields.Binary(string="Image",
                                     related="product_id.image_1920")
    barcode = fields.Char('Item Code', readonly=False)
