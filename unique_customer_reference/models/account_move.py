# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.constrains('ref')
    def unique_customer_reference(self):
        for rec in self:
            moves = self.env['account.move'].sudo().search(
                [('id', '!=', rec.id), ('move_type', '=', rec.move_type), ('ref', '=', rec.ref)])
            if moves:
                raise ValidationError(_('The Customer Reference must be unique !'))
