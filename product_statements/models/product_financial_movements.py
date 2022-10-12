# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import tools


class ProductFinancialMovementsReport(models.Model):
    _inherit = "product.financial.movements"

    product_id = fields.Many2one('product.product', readonly=True)
    categ_id = fields.Many2one('product.category', readonly=True)
    date = fields.Date(readonly=True)
    move_id = fields.Many2one('account.move', readonly=True)
    company_id = fields.Many2one('res.company', readonly=True)
    journal_id = fields.Many2one('account.journal', readonly=True)
    currency_id = fields.Many2one('res.currency', readonly=True)
    partner_id = fields.Many2one('res.partner', readonly=True)
    quantity = fields.Float(readonly=True)
    purchase_price = fields.Float(readonly=True)
    price_unit = fields.Float(readonly=True)
    price_subtotal = fields.Monetary(group_operator="sum", readonly=True)
    parent_state = fields.Selection([('draft', 'Draft'),
                                     ('posted', 'Posted'),
                                     ('cancel', 'Cancelled'),
                                     ], readonly=True)

    def _query(self, fields='', from_clause=''):
        select_ = """
                a.id as id,
                a.product_id,
                a.categ_id,
                a.date,
                a.move_id,
                a.company_id,
                a.journal_id,
                a.currency_id,
                a.partner_id,
                a.quantity,
                a.purchase_price,
                a.price_unit,
                a.price_subtotal,
                a.parent_state,
                %s
        """ % fields

        from_ = """
                account_move_line a
                %s
        """ % from_clause
        return "(SELECT %s FROM %s WHERE a.parent_state='posted' AND A.)" % (select_, from_)

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""CREATE or REPLACE VIEW %s as (%s)""" % (self._table, self._query()))
