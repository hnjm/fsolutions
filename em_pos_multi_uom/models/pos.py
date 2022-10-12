# -*- coding: utf-8 -*-

import logging
from datetime import timedelta
from functools import partial
import psycopg2
from odoo import api, fields, models, tools, _
from odoo.tools import float_is_zero
from odoo.exceptions import UserError
from odoo.http import request
import odoo.addons.decimal_precision as dp
from itertools import groupby
from itertools import groupby
import logging
import re

from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError
from odoo.osv import expression

_logger = logging.getLogger(__name__)


class PosConfig(models.Model):
    _inherit = 'pos.config' 

    allow_multi_uom = fields.Boolean('Product multi uom', default=True)

class ProductMultiUom(models.Model):
    _name = 'product.multi.uom'
    _order = "sequence desc"

    multi_uom_id = fields.Many2one('uom.uom','Unit of measure')
    price = fields.Float("Sale Price",default=0)
    sequence = fields.Integer("Sequence",default=1)
    barcode = fields.Char("Barcode")
    product_tmp_id = fields.Many2one("product.template",string="Product")
    product_id = fields.Many2one("product.product",string="Product")

    # @api.depends('product_tmp_id')
    # def _compute_product_tmp_id(self):
    #     for record in self:
    #         if record.product_tmp_id:
    #             record.product_id = record.product_tmp_id.product_tmp_id.ids[0]

    # @api.multi
    @api.onchange('multi_uom_id')
    def unit_id_change(self):
        domain = {'multi_uom_id': [('category_id', '=', self.product_tmp_id.uom_id.category_id.id)]}        
        return {'domain': domain}

    @api.model
    def create(self, vals):
        if 'barcode' in vals:
            barcodes = self.env['product.product'].sudo().search([('barcode','=',vals['barcode'])])
            barcodes2 = self.search([('barcode','=',vals['barcode'])])
            if barcodes or barcodes2:
                raise UserError(_('A barcode can only be assigned to one product !'))
        return super(ProductMultiUom, self).create(vals)

    # @api.multi
    def write(self, vals):
        if 'barcode' in vals:
            barcodes = self.env['product.product'].sudo().search([('barcode','=',vals['barcode'])])
            barcodes2 = self.search([('barcode','=',vals['barcode'])])
            if barcodes or barcodes2:
                raise UserError(_('A barcode can only be assigned to one product !'))
        return super(ProductMultiUom, self).write(vals)


class ProductTemplate(models.Model):
    _inherit = 'product.template'
    
    has_multi_uom = fields.Boolean('Has multi UOM')
    multi_uom_ids = fields.One2many('product.multi.uom','product_tmp_id')

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        res = super(ProductTemplate, self)._name_search(name, args=args, operator=operator, limit=limit,
                                                        name_get_uid=name_get_uid)
        if operator in ('ilike', 'like', '=', '=like', '=ilike'):
            recs = self.env['product.multi.uom'].search([('barcode', operator, name)])
            domain = expression.AND([
                args or [],
                ['|', '|', '|', ('name', operator, name), ('barcode', operator, name), ('default_code', operator, name),
                 ('id', 'in', recs.mapped('product_tmp_id').ids)]
            ])
            return self._search(domain, limit=limit, access_rights_uid=name_get_uid)
        return res

    @api.model
    def create(self, vals):
        if 'barcode' in vals:
            barcodes = self.env['product.multi.uom'].search([('barcode','=',vals['barcode'])])
            if barcodes:
                raise UserError(_('A barcode can only be assigned to one product !'))
        return super(ProductTemplate, self).create(vals)

    # @api.multi
    def write(self, vals):
        if 'barcode' in vals:
            barcodes = self.env['product.multi.uom'].search([('barcode','=',vals['barcode'])])
            if barcodes:
                raise UserError(_('A barcode can only be assigned to one product !'))
        return super(ProductTemplate, self).write(vals)

class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        res = super(ProductProduct, self)._name_search(name, args=args, operator=operator, limit=limit,
                                                       name_get_uid=name_get_uid)
        if operator in ('ilike', 'like', '=', '=like', '=ilike'):
            recs = self.env['product.multi.uom'].search([('barcode', operator, name)])
            domain = expression.AND([
                args or [],
                ['|', '|', '|', ('name', operator, name), ('barcode', operator, name), ('default_code', operator, name),
                 ('product_tmpl_id', 'in', recs.mapped('product_tmp_id').ids)]
            ])
            return self._search(domain, limit=limit, access_rights_uid=name_get_uid)
        return res


class PosOrder(models.Model):
    _inherit = "pos.order"



    def _prepare_invoice_line(self, order_line):
        return {
            'product_id': order_line.product_id.id,
            'quantity': order_line.qty if self.amount_total >= 0 else -order_line.qty,
            'discount': order_line.discount,
            'price_unit': order_line.price_unit,
            'name': order_line.full_product_name or order_line.product_id.display_name,
            'tax_ids': [(6, 0, order_line.tax_ids_after_fiscal_position.ids)],
            'product_uom_id': order_line.product_uom.id,
        }



class PosOrderLine(models.Model):
    _inherit = "pos.order.line"

    product_uom_id = fields.Many2one('uom.uom', string='Product UoM',store=True)
    product_uom = fields.Many2one('uom.uom','Unit of measure')

    @api.onchange('product_uom')
    @api.constrains('product_uom')
    def onchange_product_uom(self):
        for rec in self:
            if rec.product_uom:
                rec.product_uom_id = rec.product_uom.id


    def _compute_total_cost(self, stock_moves):
        """
        Compute the total cost of the order lines.
        :param stock_moves: recordset of `stock.move`, used for fifo/avco lines
        """
        for line in self.filtered(lambda l: not l.is_total_cost_computed):
            product = line.product_id
            if line._is_product_storable_fifo_avco() and stock_moves:
                product_cost = product._compute_average_price(0, line.qty, stock_moves.filtered(lambda ml: ml.product_id == product))
            else:
                product_cost = product.standard_price
            if product.uom_id != line.product_uom:
                currency = line.currency_id
                ratio = product.uom_id.ratio
                product_cost = currency.round(product.standard_price / ratio)
            line.total_cost = line.qty * product.cost_currency_id._convert(
                from_amount=product_cost,
                to_currency=line.currency_id,
                company=line.company_id or self.env.company,
                date=line.order_id.date_order or fields.Date.today(),
                round=False,
            )
            line.is_total_cost_computed = True


class StockPicking(models.Model):
    _inherit='stock.picking'

    def _prepare_stock_move_vals(self, first_line, order_lines):
        res = super(StockPicking, self)._prepare_stock_move_vals(first_line, order_lines)
        res['product_uom'] = first_line.product_uom.id or first_line.product_id.uom_id.id,
        return res

    @api.model
    def _create_picking_from_pos_order_lines(self, location_dest_id, lines, picking_type, partner=False):
        """We'll create some picking based on order_lines"""

        pickings = self.env['stock.picking']
        stockable_lines = lines.filtered(lambda l: l.product_id.type in ['product', 'consu'] and not float_is_zero(l.qty, precision_rounding=l.product_uom.rounding))
        if not stockable_lines:
            return pickings
        positive_lines = stockable_lines.filtered(lambda l: l.qty > 0)
        negative_lines = stockable_lines - positive_lines

        if positive_lines:
            location_id = picking_type.default_location_src_id.id
            positive_picking = self.env['stock.picking'].create(
                self._prepare_picking_vals(partner, picking_type, location_id, location_dest_id)
            )

            positive_picking._create_move_from_pos_order_lines(positive_lines)
            try:
                with self.env.cr.savepoint():
                    positive_picking._action_done()
            except (UserError, ValidationError):
                pass

            pickings |= positive_picking
        if negative_lines:
            if picking_type.return_picking_type_id:
                return_picking_type = picking_type.return_picking_type_id
                return_location_id = return_picking_type.default_location_dest_id.id
            else:
                return_picking_type = picking_type
                return_location_id = picking_type.default_location_src_id.id

            negative_picking = self.env['stock.picking'].create(
                self._prepare_picking_vals(partner, return_picking_type, location_dest_id, return_location_id)
            )
            negative_picking._create_move_from_pos_order_lines(negative_lines)
            try:
                with self.env.cr.savepoint():
                    negative_picking._action_done()
            except (UserError, ValidationError):
                pass
            pickings |= negative_picking
        return pickings




class StockMove(models.Model):
    _inherit='stock.move'


    def _create_out_svl(self, forced_quantity=None):
        """Create a `stock.valuation.layer` from `self`.

        :param forced_quantity: under some circunstances, the quantity to value is different than
            the initial demand of the move (Default value = None)
        """
        svl_vals_list = []
        for move in self:
            move = move.with_company(move.company_id)
            valued_move_lines = move._get_out_move_lines()
            valued_quantity = 0
            for valued_move_line in valued_move_lines:
                valued_quantity += valued_move_line.product_uom_id._compute_quantity(valued_move_line.qty_done, move.product_id.uom_id)
            if float_is_zero(forced_quantity or valued_quantity, precision_rounding=move.product_id.uom_id.rounding):
                continue
            svl_vals = move.product_id._prepare_out_svl_vals(forced_quantity or valued_quantity, move.company_id)
            svl_vals.update(move._prepare_common_svl_vals())

            if forced_quantity:
                svl_vals['description'] = 'Correction of %s (modification of past move)' % move.picking_id.name or move.name
            svl_vals['description'] += svl_vals.pop('rounding_adjustment', '')
            if move.product_id.uom_id != move.product_uom:
                currency = move.company_id.currency_id
                ratio = move.product_id.uom_id.ratio
                unit_cost = currency.round(move.product_id.standard_price / ratio)
                svl_vals['unit_cost'] = unit_cost
            svl_vals_list.append(svl_vals)
        return self.env['stock.valuation.layer'].sudo().create(svl_vals_list)

    def _generate_analytic_lines_data(self, unit_amount, amount):
        self.ensure_one()
        account_id = self._get_analytic_account()
        return {
            'name': self.name,
            'amount': amount,
            'account_id': account_id.id,
            'unit_amount': unit_amount,
            'product_id': self.product_id.id,
            'product_uom_id': self.product_uom.id,
            'company_id': self.company_id.id,
            'ref': self._description,
            'category': 'other',
        }

    def _generate_valuation_lines_data(self, partner_id, qty, debit_value, credit_value, debit_account_id, credit_account_id, description):
        # This method returns a dictionary to provide an easy extension hook to modify the valuation lines (see purchase for an example)
        self.ensure_one()
        debit_line_vals = {
            'name': description,
            'product_id': self.product_id.id,
            'quantity': qty,
            'product_uom_id': self.product_uom.id,
            'ref': description,
            'partner_id': partner_id,
            'debit': debit_value if debit_value > 0 else 0,
            'credit': -debit_value if debit_value < 0 else 0,
            'account_id': debit_account_id,
        }

        credit_line_vals = {
            'name': description,
            'product_id': self.product_id.id,
            'quantity': qty,
            'product_uom_id': self.product_uom.id,
            'ref': description,
            'partner_id': partner_id,
            'credit': credit_value if credit_value > 0 else 0,
            'debit': -credit_value if credit_value < 0 else 0,
            'account_id': credit_account_id,
        }

        rslt = {'credit_line_vals': credit_line_vals, 'debit_line_vals': debit_line_vals}
        if credit_value != debit_value:
            # for supplier returns of product in average costing method, in anglo saxon mode
            diff_amount = debit_value - credit_value
            price_diff_account = self.product_id.property_account_creditor_price_difference

            if not price_diff_account:
                price_diff_account = self.product_id.categ_id.property_account_creditor_price_difference_categ
            if not price_diff_account:
                raise UserError(_('Configuration error. Please configure the price difference account on the product or its category to process this operation.'))

            rslt['price_diff_line_vals'] = {
                'name': self.name,
                'product_id': self.product_id.id,
                'quantity': qty,
                'product_uom_id': self.product_uom.id,
                'ref': description,
                'partner_id': partner_id,
                'credit': diff_amount > 0 and diff_amount or 0,
                'debit': diff_amount < 0 and -diff_amount or 0,
                'account_id': price_diff_account.id,
            }
        return rslt


class StockValuationLayer(models.Model):
    _inherit = 'stock.valuation.layer'

    uom_id = fields.Many2one(related='stock_move_id.product_uom', readonly=True, required=True)


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    def _stock_account_get_anglo_saxon_price_unit(self):
        self.ensure_one()
        if not self.product_id:
            return self.price_unit
        price_unit = super(AccountMoveLine, self)._stock_account_get_anglo_saxon_price_unit()
        order = self.move_id.pos_order_ids
        if order and self.product_id.uom_id != self.product_uom_id:
            currency = self.currency_id
            ratio = self.product_id.uom_id.ratio
            price_unit = currency.round(self.product_id.standard_price/ratio)
        return price_unit