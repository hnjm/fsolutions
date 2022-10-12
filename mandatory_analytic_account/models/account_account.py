# -*- coding: utf-8 -*-

from odoo import models, fields, api

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_compare, float_is_zero

class AccountAccount(models.Model):
    _inherit = 'account.account'

    is_analytic_account = fields.Boolean()
    is_analytic_tag = fields.Boolean()


class AccountMove(models.Model):
    _inherit = 'account.move.line'

    is_analytic_account = fields.Boolean(related='account_id.is_analytic_account',store=True)
    is_analytic_tag = fields.Boolean(related='account_id.is_analytic_tag',store=True)




