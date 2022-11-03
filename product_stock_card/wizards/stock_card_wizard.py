# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import Warning, ValidationError
from datetime import datetime
import pytz

FORMAT_DATE = "%Y-%m-%d %H:%M:%S"
ERREUR_FUSEAU = _("Set your timezone in preferences")

def convert_UTC_TZ(self, UTC_datetime):
    if not self.env.user.tz:
        raise Warning(ERREUR_FUSEAU)
    local_tz = pytz.timezone(self.env.user.tz)
    date = UTC_datetime
    date = pytz.utc.localize(date, is_dst=None).astimezone(local_tz)
    return date.strftime(FORMAT_DATE)


class StockCardWizard(models.TransientModel):
    _name = "wizard.stock.card.wizard"

    details = fields.Boolean(
        string="Detailed report",
        default=True)

    date_start = fields.Datetime(
        string="Start date",
        required=True)

    date_end = fields.Datetime(
        string="End date",
        required=True)

    location_id = fields.Many2one(
        string="Location",
        comodel_name="stock.location",
        required=True)

    filter_by = fields.Selection(
        string="Filter by",
        required=True,
        selection=[
            ('no_filter', 'No filter'),
            ('product', 'Product'),
            ('category', 'Category')],
        default='no_filter')

    products = fields.Many2many(
        string="Produits",
        comodel_name="product.product")

    category = fields.Many2one(
        string="Filter category",
        comodel_name="product.category",
        help="Select category to filter")

    is_zero = fields.Boolean(
        string='Include no moves in period',
        default=True,
        help="""Unselect if you just want to see product who have move"""
             """ in the period.""")

    def delete_values_in_stock_move(self):
        self.env.cr.execute(""" delete from stock_move_stock_card;
                   """)

    def update_values_in_stock_move(self,mvdate,product_id,location_id,initial_stock,product_in , product_out ,product_bal,val_bal, name):
        self._cr.execute(""" INSERT INTO stock_move_stock_card (date,product_id , location_id,initial_stock,product_in, product_out,product_bal,val_bal, name) 
                   VALUES """ + str((mvdate,product_id.id,location_id.id,initial_stock,product_in,product_out,product_bal,val_bal,name)) + """ RETURNING id as id; """ )
        data = self.env.cr.dictfetchall()
        id = 0
        if data:
            for rec in data:
                id = rec.get('id') or 0
        return id

    def open_product_stock_card(self):
        self.delete_values_in_stock_move()
        stock_move = self.env['stock.move.stock.card']
        quant_obj = self.env["stock.quant"].search([])
        products = self.env['product.product'].search([])
        start = self.date_start
        end = self.date_end
        location_id = self.location_id.id
        category_id = self.category.id if self.category else None
        filter_products =  self.products.mapped('id')
        is_zero = self.is_zero
        filter_by = self.filter_by
        quant_domain = [('location_id', 'child_of', location_id)]
        moves_domain = [
            ('date', '>=', start),
            ('date', '<=', end),
            ('state', '=', 'done'),
            '|',
            ('location_dest_id', 'child_of', location_id),
            ('location_id', 'child_of', location_id)]
        moves_now_domain = [
            ('date', '>=', end),
            ('date', '<=', fields.Datetime.now()),
            ('state', '=', 'done'),
            '|',
            ('location_dest_id', 'child_of', location_id),
            ('location_id', 'child_of', location_id)]

        if filter_by == 'product' and filter_products:
            quant_domain.append(('product_id', 'in', filter_products))
            moves_domain.append(('product_id', 'in', filter_products))
            moves_now_domain.append(('product_id', 'in', filter_products))

        elif filter_by == 'category' and category_id:
            quant_domain.append(('product_id.categ_id', 'child_of', category_id))
            moves_domain.append(('product_id.categ_id', 'child_of', category_id))
            moves_now_domain.append(('product_id.categ_id', 'child_of', category_id))

        quants = quant_obj.search(quant_domain)
        moves = self.env['stock.move'].search(moves_domain)
        moves_to_now = self.env['stock.move'].search(moves_now_domain)

        location = self.env['stock.location'].browse(location_id)
        location_ids = self.env['stock.location'].search([
            ('parent_path', '=like', location.parent_path + "%")])

        mv_in = moves.filtered(
            lambda x: x.location_dest_id.id in location_ids.ids)
        mv_out = moves.filtered(
            lambda x: x.location_id.id in location_ids.ids)
        mv_tonow_in = moves_to_now.filtered(
            lambda x: x.location_dest_id.id in location_ids.ids)
        mv_tonow_out = moves_to_now.filtered(
            lambda x: x.location_id.id in location_ids.ids)

        products |= quants.mapped('product_id')
        products |= mv_in.mapped("product_id")
        products |= mv_out.mapped("product_id")
        products_with_initial = []
        for product in products.sorted(lambda r: r.name):
            line = {}
            mv_in_pro = mv_in.filtered(
                lambda x: x.product_id.id == product.id)
            mv_out_pro = mv_out.filtered(
                lambda x: x.product_id.id == product.id)
            mv_tonow_in_pro = mv_tonow_in.filtered(
                lambda x: x.product_id.id == product.id)
            mv_tonow_out_pro = mv_tonow_out.filtered(
                lambda x: x.product_id.id == product.id)

            if not is_zero and not mv_in_pro and not mv_out_pro:
                continue

            product_uom = product.uom_id
            tot_in = 0
            for elt in mv_in_pro:
                if product_uom.id != elt.product_uom.id:
                    factor = product_uom.factor / elt.product_uom.factor
                else:
                    factor = 1.0
                tot_in += elt.product_uom_qty * factor

            tot_out = 0
            for elt in mv_out_pro:
                if product_uom.id != elt.product_uom.id:
                    factor = product_uom.factor / elt.product_uom.factor
                else:
                    factor = 1.0
                tot_out += elt.product_uom_qty * factor

            tot_tonow_in = 0
            for elt in mv_tonow_in_pro:
                if product_uom.id != elt.product_uom.id:
                    factor = product_uom.factor / elt.product_uom.factor
                else:
                    factor = 1.0
                tot_tonow_in += elt.product_uom_qty * factor

            tot_tonow_out = 0
            for elt in mv_tonow_out_pro:
                if product_uom.id != elt.product_uom.id:
                    factor = product_uom.factor / elt.product_uom.factor
                else:
                    factor = 1.0
                tot_tonow_out += elt.product_uom_qty * factor

            actual_qty = product.with_context(
                {'location': location_id}).qty_available
            actual_qty += tot_tonow_out - tot_tonow_in

            stock_init = actual_qty - tot_in + tot_out

            move_in_show = mv_in_pro - mv_tonow_in_pro
            move_out_show = mv_out_pro - mv_tonow_out_pro

            move_to_show = self.env['stock.move']
            move_to_show |= move_in_show
            move_to_show |= move_out_show
            move_to_show.sorted(lambda r: r.date)
            val_in = actual_qty - tot_in + tot_out
            val_fin = val_in

            for mv in move_to_show:
                if str(product.name) + str(stock_init) in products_with_initial:
                    stock_init = 0
                else:
                    products_with_initial.append(str(product.name) + str(stock_init))

                src = mv.location_id.id
                dst = mv.location_dest_id.id
                qty = mv.product_uom_qty

                val_in = qty if dst in location_ids.ids else 0
                val_out = qty if src in location_ids.ids else 0
                val_bal = val_in - val_out
                val_fin += val_bal

                mvdate = convert_UTC_TZ(self, mv.date) if mv.date else ""
                mvname = mv.picking_id.name or mv.name or "-"

                stock_move_created = self.update_values_in_stock_move(mvdate,product,location ,stock_init,val_in,val_out,val_fin,val_bal,mvname)
                our_move = stock_move.browse(stock_move_created)
                our_move.check_in_out()
                our_move._get_picking_id()

        return {
                'name': "Product Stock Card",
                'view_mode': 'tree,form',
                'res_model': 'stock.move.stock.card',
                'type': 'ir.actions.act_window',
                'target': 'current',
            }

    @api.onchange('filter_by')
    def department_ids_onchange(self):
        if self.filter_by == 'product':
            sub_domain = [('type', '=', 'product')]
            domain = {'domain': {'products': sub_domain}}
            return domain
        if self.filter_by == 'category':
            sub_domain = []
            domain = {'domain': {'category': sub_domain}}
            return domain
