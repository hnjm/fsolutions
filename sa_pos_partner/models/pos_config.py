# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import base64

from odoo import fields, api, models


class PosConfig(models.Model):
    _inherit = 'pos.config'

    is_print_partner= fields.Boolean('Print Partner in Receipt')

class PaymentMethod(models.Model):
    _inherit = 'pos.payment.method'

    is_tax_invoice = fields.Boolean('Print Tax Invoice')
