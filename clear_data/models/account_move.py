# -*- coding: utf-8 -*-

'''
Create Date:2017��9��1��

Author     :Administrator
'''
import datetime
import dateutil
import logging
import os
import time
import pdb
import logging
import odoo.tools

_logger = logging.getLogger(__name__)

from pytz import timezone

import odoo
from odoo import api, fields, models, tools, _
from odoo.exceptions import MissingError, UserError, ValidationError


class AccountMove(models.Model):
    _inherit = 'account.move'


    def force_delete_invoice(self):
        records = self.env['account.move'].browse(self._context.get('active_ids', []))
        for record in records:
            if record.state == 'cancel':
                record.button_draft()
                record.posted_before = False
                record.sudo().unlink()
            else:
                raise ValidationError(_("You can't force delete moves not in cancel !"))
