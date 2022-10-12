# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class res_users(models.Model):
    _inherit = 'res.users'

    branch_id = fields.Many2one('res.branch', 'Current Branch')
    branch_ids = fields.Many2many('res.branch', id1='user_id', id2='branch_id', string='Allowed Branches')

    is_branch_user = fields.Boolean("Is branch user", compute="_compute_branch_user")

    def _compute_branch_user(self):
        for user in self:

            b_usr = user.has_group('pos_branch.group_branch_user')
            b_mngr = user.has_group('pos_branch.group_branch_user_manager')
            non_user_group = self.env.ref('pos_branch.group_no_branch_user')
            if not b_usr and not b_mngr:
                non_user_group.write({
                    'users': [(4, user.id)]
                })
            else:
                non_user_group.write({
                    'users': [(3, user.id)]
                })
            user.is_branch_user = False


class ResBranch(models.Model):
    _name = 'res.branch'
    _description = "Res Branch"

    name = fields.Char('Name', required=True)
    address = fields.Text('Address', size=252)
    telephone_no = fields.Char("Telephone No")
    company_id = fields.Many2one('res.company', 'Company', required=True)


class PosSession(models.Model):
    _inherit = 'pos.session'

    branch_id = fields.Many2one('res.branch', readonly=True)

    @api.model
    def create(self, vals):
        res = super(PosSession, self).create(vals)
        res.write({
            'branch_id': res.config_id.branch_id.id
        })
        return res

    def _create_picking_at_end_of_session(self):
        self.ensure_one()
        lines_grouped_by_dest_location = {}
        picking_type = self.config_id.picking_type_id

        if not picking_type or not picking_type.default_location_dest_id:
            session_destination_id = self.env['stock.warehouse']._get_partner_locations()[0].id
        else:
            session_destination_id = picking_type.default_location_dest_id.id

        for order in self.order_ids:
            if order.company_id.anglo_saxon_accounting and order.is_invoiced or order.to_ship:
                continue
            destination_id = order.partner_id.property_stock_customer.id or session_destination_id
            if destination_id in lines_grouped_by_dest_location:
                lines_grouped_by_dest_location[destination_id] |= order.lines
            else:
                lines_grouped_by_dest_location[destination_id] = order.lines

        for location_dest_id, lines in lines_grouped_by_dest_location.items():
            pickings = self.env['stock.picking']._create_picking_from_pos_order_lines(location_dest_id, lines,
                                                                                      picking_type)
            pickings.write(
                {'pos_session_id': self.id, 'origin': self.name, 'branch_id': self.order_ids.config_id.branch_id.id})


class PosConfig(models.Model):
    _inherit = 'pos.config'

    branch_id = fields.Many2one('res.branch', string='Branch')


class POSOrder(models.Model):
    _inherit = 'pos.order'

    branch_id = fields.Many2one('res.branch', 'Branch', readonly=True)

    @api.model
    def _process_order(self, order, draft, existing_order):
        res = super(POSOrder, self)._process_order(order, draft, existing_order)
        pos_order = self.browse(res)
        if pos_order:
            pos_order.write({
                'branch_id': pos_order.config_id.branch_id.id
            })
            pos_order.account_move.write({
                'branch_id': pos_order.config_id.branch_id.id
            })
            if not pos_order.session_id.branch_id:
                pos_order.session_id.write({
                    'branch_id': pos_order.config_id.branch_id.id
                })
        return res


class AccountMove(models.Model):
    _inherit = 'account.move'

    branch_id = fields.Many2one('res.branch', 'Branch', readonly=True)


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    branch_id = fields.Many2one('res.branch', 'Branch', readonly=True)


class PosPayment(models.Model):
    _inherit = 'pos.payment'

    branch_id = fields.Many2one('res.branch', related='pos_order_id.branch_id')


class AccountBankStatement(models.Model):
    _inherit = 'account.bank.statement'

    branch_id = fields.Many2one('res.branch', 'Pos Branch', related='pos_session_id.branch_id')


class AccountBankStatementLine(models.Model):
    _inherit = 'account.bank.statement.line'

    branch_id = fields.Many2one('res.branch', 'Pos Branch', related='statement_id.branch_id')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
