# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
# 
#################################################################################
from odoo import fields, models, api
import logging
import base64
_logger = logging.getLogger(__name__)

class PosConfig(models.Model):
    _inherit = 'pos.config'
    
    invoice_print = fields.Boolean(string="Print Invoice Without Download", help="Enalble this options to Print Invoice Without Download .", default=True)
    
class PosOrder(models.Model):
    _inherit = "pos.order" 

    def action_invoice_pdf(self,invoice_id):

        report = self.env.ref('account.account_invoices')._render_qweb_pdf([invoice_id])
        base = base64.b64encode(report[0])
        return base