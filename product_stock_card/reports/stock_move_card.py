# -*-coding: utf-8 -*-
from odoo import api, fields, models, _


class StockMoveStockCard(models.Model):
    _name = 'stock.move.stock.card'

    date = fields.Date(string="Transaction Date", required=False, )
    product_id = fields.Many2one(comodel_name="product.product", string="Product", required=False, )
    location_id = fields.Many2one(comodel_name="stock.location", string="Location", required=False, )
    name = fields.Char(string="Move Name", required=False, )
    initial_stock = fields.Float(string="Initial Stock",  required=False, )
    product_in = fields.Float(string="IN",  required=False, )
    product_out = fields.Float(string="OUT",  required=False, )
    val_bal = fields.Float(string="Balance",  required=False, )
    product_bal = fields.Float(string="Available Quantity",  required=False, )
    picking_id = fields.Many2one(comodel_name="stock.picking", string="Picking", required=False,compute='_get_picking_id',store=True )
    partner_id = fields.Many2one(comodel_name="res.partner", string="Partner", required=False,store=True )
    transaction_type = fields.Selection(string="Transaction Type", selection=[('in', 'IN'), ('out', 'OUT'), ], required=False,compute='check_in_out',store=True )

    @api.depends('product_in','product_out')
    def check_in_out(self):
        for rec in self:
            if rec.product_in:
                rec.transaction_type = 'in'
            elif rec.product_out:
                rec.transaction_type = 'out'
            else:
                rec.transaction_type = False

    @api.depends('name')
    def _get_picking_id(self):
        for rec in self:
            self.picking_id = self.env['stock.picking'].search([('name','=',rec.name)],limit=1) or False
            self.partner_id = self.picking_id.partner_id.id
