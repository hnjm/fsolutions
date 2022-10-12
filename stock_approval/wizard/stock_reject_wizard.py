# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.addons import decimal_precision as dp
import math

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, AccessError
from odoo.addons import decimal_precision as dp
import base64
import xlsxwriter
import io


class stockRejectWizard(models.TransientModel):
    _name = 'stock.reject.wizard'

    comment = fields.Char("Rejection Comment", required=True)

    def action_reject(self):
        """Switch active request to rejected and store the comment."""
        self.ensure_one()
        requests = self.env['stock.picking'].browse(
            self.env.context.get('active_ids')
        )
        requests.write({
            'rejection_comment': self.comment})
        return True

