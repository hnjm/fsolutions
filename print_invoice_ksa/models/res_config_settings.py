# -*- coding: utf-8 -*-

import logging
from typing import Sequence

from odoo import api, fields, models, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class ResCompany(models.Model):
    _inherit = 'res.company'

    arabic_name = fields.Char('Name', required=True)
    arabic_street = fields.Char('Street')
    arabic_street2 = fields.Char('Street2')
    arabic_city = fields.Char('City')
    arabic_state = fields.Char('State')
    arabic_country = fields.Char('Country')
    bank_accounts = fields.Char('Bank Accounts')
    # narration = fields.Text(string='Terms and Conditions')
