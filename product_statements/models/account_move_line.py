# -*- coding: utf-8 -*-
import qrcode
import base64
from io import BytesIO
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.http import request
from odoo.tools import html2plaintext
from odoo import api, fields, models
from datetime import datetime
from odoo import api, fields, models, _
import qrcode
import base64
import io
from odoo import http
from num2words import num2words
from odoo.tools.misc import formatLang, format_date, get_lang

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'
    
    categ_id = fields.Many2one(related='product_id.categ_id')
    