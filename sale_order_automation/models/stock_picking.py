import json
import time
from ast import literal_eval
from collections import defaultdict
from datetime import date
from itertools import groupby
from operator import itemgetter

from odoo import SUPERUSER_ID, _, api, fields, models
from odoo.addons.stock.models.stock_move import PROCUREMENT_PRIORITIES
from odoo.exceptions import UserError
from odoo.osv import expression
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, format_datetime
from odoo.tools.float_utils import float_compare, float_is_zero, float_round
from odoo.tools.misc import format_date


class StockPicking(models.Model):
    _inherit = "stock.picking"

    date_done = fields.Datetime('Date of Transfer', copy=False, readonly=False,
                                help="Date at which the transfer has been processed or cancelled.")


    def _action_done(self):
        res = super(StockPicking, self)._action_done()
        for pick in self:
            pick.write({'date_done': pick.date_done})
            pick.move_lines.write({'date': pick.date_done})
            pick.move_line_ids.write({'date': pick.date_done})
            moves = self.env['account.move'].sudo().search([('stock_move_id.picking_id', '=', pick.id)])
            for mv in moves:
                mv.button_draft()
                mv.name = ''
                mv.date = pick.date_done.date()
                mv.action_post()
        return res