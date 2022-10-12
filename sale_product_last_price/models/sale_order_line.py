# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
from collections import defaultdict
from datetime import datetime, time
from dateutil import relativedelta
from itertools import groupby
from json import dumps
from psycopg2 import OperationalError

from odoo import SUPERUSER_ID, _, api, fields, models, registry
from odoo.addons.stock.models.stock_rule import ProcurementException
from odoo.exceptions import UserError, ValidationError
from odoo.osv import expression
from odoo.tools import add, float_compare, frozendict, split_every, format_date

_logger = logging.getLogger(__name__)


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    last_price = fields.Float(compute='_compute_last_price')

    @api.depends('product_id')
    def _compute_last_price(self):
        for rec in self:
            price = 0.0
            last_price = self.search([('order_partner_id', '=', rec.order_partner_id.id),
                                 ('product_id', '=', rec.product_id.id),('state', '=', 'sale')],limit=1)
            if last_price:
                price = last_price.price_unit
            rec.last_price = price
