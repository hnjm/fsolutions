from odoo import models, fields, api, exceptions, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_is_zero, float_compare


class StockPickingTypeInternalInherit(models.Model):
    _inherit = 'stock.picking.type'

    tow_steps_validation = fields.Boolean('2 Steps Validation')
    is_lost = fields.Boolean('Is Lost')


class StockLocationInternalInherit(models.Model):
    _inherit = 'stock.location'

    allowed_user = fields.Many2many('res.users', string='Allowed Users')
    is_lost = fields.Boolean('Is Lost')


class StockPickingInternalInherit(models.Model):
    _inherit = 'stock.picking'

    allowed_user = fields.Many2many('res.users', string='Allowed Users', related='location_dest_id.allowed_user')
    tow_steps_validation = fields.Boolean('2 Steps Validation', copy=True, store=True,
                                          related='picking_type_id.tow_steps_validation')
    op_id = fields.Char()
    # steps_validation = fields.Boolean('Validation')

    # picking_type_id = fields.Many2one(
    #     'stock.picking.type', 'Operation Type',
    #     required=True, readonly=True,
    #     states={'draft': [('readonly', False)]})
    operation_type_to = fields.Many2one(
        'stock.picking.type', 'To Operation Type',
        readonly=True,
        store=True, compute='compute_operation_type')
    # states = {'draft': [('readonly', False)]},

    location_id = fields.Many2one(
        'stock.location', "Source Location",
        default=lambda self: self.env['stock.picking.type'].browse(
            self._context.get('default_picking_type_id')).default_location_src_id,
        check_company=True, readonly=True, required=True,
        states={'draft': [('readonly', False)]})
    location_dest_id = fields.Many2one(
        'stock.location', "Destination Location",
        default=lambda self: self.env['stock.picking.type'].browse(
            self._context.get('default_picking_type_id')).default_location_dest_id,
        check_company=True, readonly=True, required=True,
        states={'draft': [('readonly', False)]})

    state = fields.Selection([

        ('draft', 'Draft'),
        ('waiting', 'Waiting Another Operation'),
        ('confirmed', 'Waiting'),
        ('assigned', 'Ready'),
        ('send', 'Sent'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
    ], string='Status', compute='_compute_state',
        copy=False, index=True, readonly=True, store=True, tracking=True,
        help=" * Draft: The transfer is not confirmed yet. Reservation doesn't apply.\n"
             " * Waiting another operation: This transfer is waiting for another operation before being ready.\n"
             " * Waiting: The transfer is waiting for the availability of some products.\n(a) The shipping policy is \"As soon as possible\": no product could be reserved.\n(b) The shipping policy is \"When all products are ready\": not all the products could be reserved.\n"
             " * Ready: The transfer is ready to be processed.\n(a) The shipping policy is \"As soon as possible\": at least one product has been reserved.\n(b) The shipping policy is \"When all products are ready\": all product have been reserved.\n"
             " * Done: The transfer has been processed.\n"
             " * Cancelled: The transfer has been cancelled.")

    @api.depends('location_dest_id')
    def compute_operation_type(self):
        for rec in self:
            if rec.location_dest_id:
                operation = self.env['stock.picking.type'].search(
                    [('default_location_src_id', '=', rec.location_dest_id.id),
                     ('default_location_dest_id', '=', rec.location_dest_id.id), ('is_lost', '=', False),
                     ('code', '=', 'internal'), ('active', '=', True)])
                rec.operation_type_to = operation.id
                print(operation, 'opp')

    def button_validate(self):
        # Clean-up the context key at validation to avoid forcing the creation of immediate
        # transfers.
        self._check_allowed_user()
        ret_op = self.env['stock.picking'].search([('id', '=', self.op_id)])
        if self.op_id:
            ret_op.state = 'done'
        else:
            if self.picking_type_id.code == 'internal':
                raise ValidationError('You can not validate order before sent you must send it first')

        # self.operations_on_moves()
        ctx = dict(self.env.context)
        ctx.pop('default_immediate_transfer', None)
        self = self.with_context(ctx)

        # Sanity checks.
        pickings_without_moves = self.browse()
        pickings_without_quantities = self.browse()
        pickings_without_lots = self.browse()
        products_without_lots = self.env['product.product']
        for picking in self:
            if not picking.move_lines and not picking.move_line_ids:
                pickings_without_moves |= picking

            picking.message_subscribe([self.env.user.partner_id.id])
            picking_type = picking.picking_type_id
            precision_digits = self.env['decimal.precision'].precision_get('Product Unit of Measure')
            no_quantities_done = all(
                float_is_zero(move_line.qty_done, precision_digits=precision_digits) for move_line in
                picking.move_line_ids.filtered(lambda m: m.state not in ('done', 'cancel')))
            no_reserved_quantities = all(
                float_is_zero(move_line.product_qty, precision_rounding=move_line.product_uom_id.rounding) for move_line
                in picking.move_line_ids)
            if no_reserved_quantities and no_quantities_done:
                pickings_without_quantities |= picking

            if picking_type.use_create_lots or picking_type.use_existing_lots:
                lines_to_check = picking.move_line_ids
                if not no_quantities_done:
                    lines_to_check = lines_to_check.filtered(
                        lambda line: float_compare(line.qty_done, 0, precision_rounding=line.product_uom_id.rounding))
                for line in lines_to_check:
                    product = line.product_id
                    if product and product.tracking != 'none':
                        if not line.lot_name and not line.lot_id:
                            pickings_without_lots |= picking
                            products_without_lots |= product

        if not self._should_show_transfers():
            if pickings_without_moves:
                raise UserError(_('Please add some items to move.'))
            if pickings_without_quantities:
                raise UserError(self._get_without_quantities_error_message())
            if pickings_without_lots:
                raise UserError(_('You need to supply a Lot/Serial number for products %s.') % ', '.join(
                    products_without_lots.mapped('display_name')))
        else:
            message = ""
            if pickings_without_moves:
                message += _('Transfers %s: Please add some items to move.') % ', '.join(
                    pickings_without_moves.mapped('name'))
            if pickings_without_quantities:
                message += _(
                    '\n\nTransfers %s: You cannot validate these transfers if no quantities are reserved nor done. To force these transfers, switch in edit more and encode the done quantities.') % ', '.join(
                    pickings_without_quantities.mapped('name'))
            if pickings_without_lots:
                message += _('\n\nTransfers %s: You need to supply a Lot/Serial number for products %s.') % (
                    ', '.join(pickings_without_lots.mapped('name')),
                    ', '.join(products_without_lots.mapped('display_name')))
            if message:
                raise UserError(message.lstrip())

        # Run the pre-validation wizards. Processing a pre-validation wizard should work on the
        # moves and/or the context and never call `_action_done`.
        if not self.env.context.get('button_validate_picking_ids'):
            self = self.with_context(button_validate_picking_ids=self.ids)
        res = self._pre_action_done_hook()
        if res is not True:
            return res

        # Call `_action_done`.
        if self.env.context.get('picking_ids_not_to_backorder'):
            pickings_not_to_backorder = self.browse(self.env.context['picking_ids_not_to_backorder'])
            pickings_to_backorder = self - pickings_not_to_backorder
        else:
            pickings_not_to_backorder = self.env['stock.picking']
            pickings_to_backorder = self
        pickings_not_to_backorder.with_context(cancel_backorder=True)._action_done()
        pickings_to_backorder.with_context(cancel_backorder=False)._action_done()

        if self.user_has_groups('stock.group_reception_report') \
                and self.user_has_groups('stock.group_auto_reception_report') \
                and self.filtered(lambda p: p.picking_type_id.code != 'outgoing'):
            lines = self.move_lines.filtered(lambda
                                                 m: m.product_id.type == 'product' and m.state != 'cancel' and m.quantity_done and not m.move_dest_ids)
            if lines:
                # don't show reception report if all already assigned/nothing to assign
                wh_location_ids = self.env['stock.location']._search(
                    [('id', 'child_of', self.picking_type_id.warehouse_id.view_location_id.id),
                     ('usage', '!=', 'supplier')])
                if self.env['stock.move'].search([
                    ('state', 'in', ['confirmed', 'partially_available', 'waiting', 'assigned']),
                    ('product_qty', '>', 0),
                    ('location_id', 'in', wh_location_ids),
                    ('move_orig_ids', '=', False),
                    ('picking_id', 'not in', self.ids),
                    ('product_id', 'in', lines.product_id.ids)], limit=1):
                    action = self.action_view_reception_report()
                    action['context'] = {'default_picking_ids': self.ids}
                    return action
        return True

    # def operations_on_moves(self):
    #     for rec in self:
    #         counter=1
    #         if rec.tow_steps_validation == True:
    #             print('fffffff')
    #             for line in rec.move_ids_without_package:
    #                 res =line.product_uom_qty - line.quantity_done
    #                 print(res,'resulllt')
    #                 if line.quantity_done > line.product_uom_qty:
    #                     raise ValidationError('Done Quantity can not be greater than Demand Quantity')
    #                 # if line.product_id.qty_available <= 0:
    #                 #     raise ValidationError(
    #                 #         'Product ({}) Has no quantity on hand available'.format(line.product_id.name))
    #                 if (line.product_uom_qty - line.quantity_done) > 0:
    #                     print('yeeees')
    #                     operation = self.env['stock.picking.type'].search([('is_lost', '=', True)], limit=1)
    #                     location_lost = self.env['stock.location'].search([('is_lost', '=', True)], limit=1)
    #                     print(operation,location_lost)
    #                     picking = self.env['stock.picking'].sudo().create({
    #                         # 'partner_id': rec.partner_id.id,
    #                         'picking_type_id': operation.id,
    #                         'operation_type_to': operation.id,
    #                         'location_id': rec.location_id.id,
    #                         'location_dest_id': location_lost.id,
    #                         'state': 'draft',
    #                         # 'op_id': rec.id,
    #                         # 'origin': rec.name+ 'Lost',
    #                         'name':rec.name + 'Lost' + str(counter)
    #
    #                     })
    #                     print('YE DOON')
    #                     counter += 1
    #
    #                     for l in picking:
    #                         l.write({
    #                             'move_ids_without_package': [(0, 0, {
    #                                 'product_id': line.product_id.id,
    #                                 'product_uom_qty': line.product_uom_qty - line.quantity_done,
    #                                 'name': str(line.product_id.name),
    #                                 # 'quantity_done': line.quantity_done,
    #                                 # 'reserved_availability': line.reserved_availability,
    #                                 'product_uom': line.product_uom.id,
    #                                 # 'product_packaging_id': line.product_packaging_id.id,
    #                                 'location_id': self.location_id.id,
    #                                 'location_dest_id': location_lost.id,
    #                                 # 'initial_demand_qty': line.initial_demand_qty - line.quantity_done,
    #
    #                             })]
    #                         })
    #                     for record in rec.move_line_ids_without_package:
    #                         for l in picking:
    #                             if line.product_id.id == record.product_id.id:
    #
    #                                 l.write({
    #                                     'move_line_ids_without_package': [(0, 0, {
    #                                         'product_id': line.product_id.id,
    #                                         'product_uom_qty': line.product_uom_qty - line.quantity_done,
    #                                         # 'name': str(line.product_id.name),
    #                                         'qty_done': line.product_uom_qty - line.quantity_done,
    #                                         # 'reserved_availability': line.reserved_availability,
    #                                         'product_uom_id': line.product_uom.id,
    #                                         # 'product_packaging_id': line.product_packaging_id.id,
    #                                         'location_id': self.location_id.id,
    #                                         'location_dest_id': location_lost.id,
    #                                         'lot_id': record.lot_id.id,
    #
    #                                     })]
    #                                 })
    #                         # print('finaaaaaaal')

    @api.constrains('allowed_user')
    def _check_allowed_user(self):
        for rec in self:
            m = self.env.user.id
            print(m, 'user id')
            list = []
            if rec.tow_steps_validation == True:
                if rec.allowed_user:
                    # print('yeess',rec.allowed_user.id)
                    for line in rec.allowed_user:
                        list.append(line.id)
                    print(list)
                    if m not in list:
                        raise ValidationError(
                            _('This user not allowed to complete the process to this destination location'))
                    else:
                        print('exist')
                else:
                    print('no')

    def action_send(self):
        if self.op_id:
            raise ValidationError('This operation in receipt and already sent now you can validate')
        else:

            if self.tow_steps_validation == True:
                picking = self.env['stock.picking'].sudo().create({
                    'partner_id': self.partner_id.id,
                    'picking_type_id': self.operation_type_to.id,
                    # 'operation_type_to': self.operation_type_to.id,
                    'location_id': self.location_id.id,
                    'location_dest_id': self.location_dest_id.id,
                    'op_id': self.id,
                    'origin': self.name,
                    # 'supervisor_name': self.supervisor_name,
                    # 'technician_name': self.technician_name,

                })
                for line in self.move_ids_without_package:
                    for l in picking:
                        l.write({
                            'move_ids_without_package': [(0, 0, {
                                'product_id': line.product_id.id,
                                'product_uom_qty': line.product_uom_qty,
                                'name': str(line.product_id.name),
                                'quantity_done': line.quantity_done,
                                'reserved_availability': line.reserved_availability,
                                'product_uom': line.product_uom.id,
                                'product_packaging_id': line.product_packaging_id.id,
                                'location_id': line.location_id.id,
                                'location_dest_id': line.location_dest_id.id,
                                # 'initial_demand_qty': line.product_uom_qty,
                                # 'lot_id': line.lot_id.id,

                            })]
                        })
                for line in self.move_line_ids_without_package:
                    for l in picking:
                        for record in l.move_line_ids_without_package:
                            if line.product_id.id == record.product_id.id:
                                record.lot_id = line.lot_id.id
                        # l.write({
                        #     'move_line_ids_without_package': [(0, 0, {
                        #         'product_id': line.product_id.id,
                        #         # 'product_uom_qty': line.product_uom_qty,
                        #         # 'name': str(line.product_id.name),
                        #         'qty_done': line.qty_done,
                        #         # 'reserved_availability': line.reserved_availability,
                        #         'product_uom_id': line.product_uom_id.id,
                        #         # 'product_packaging_id': line.product_packaging_id.id,
                        #         'location_id': line.location_id.id,
                        #         'location_dest_id': line.location_dest_id.id,
                        #         # 'initial_demand_qty': line.product_uom_qty,
                        #         'lot_id': line.lot_id.id,
                        #
                        #     })]
                        # })
                self.state = 'send'
                # picking.action_assign()
                picking.action_confirm()
                picking.state = 'assigned'

    def action_cancel(self):
        self.set_action_cancel()
        return super(StockPickingInternalInherit, self).action_cancel()

    def set_action_cancel(self):
        for rec in self:
            if self.picking_type_id.code == 'internal':
                if rec.op_id:
                    raise ValidationError(
                        'you can not cancel while receipt to cancel this order the sender must cancel it')
                else:
                    ret_op = self.env['stock.picking'].search([('op_id', '=', rec.id)])
                    if ret_op:
                        ret_op.state = 'cancel'

    def create_multi_products(self):

        return {
            'name': 'Select Multiple Products',
            'type': 'ir.actions.act_window',
            'res_model': 'wiz.products',
            'view_mode': 'form',
            'view_type': 'form',
            # 'res_id': self.id,
            'views': [(False, 'form')],
            'target': 'new',
            'context': {'default_pick': self.id},
            'key': self.id

        }


class StockMoveInternalInherit(models.Model):
    _inherit = 'stock.move'

    initial_demand_qty = fields.Float(string='Initial Demand')


class WizProductsMutiple(models.TransientModel):
    _name = "wiz.products"

    product_ids = fields.Many2many('product.product')
    pick = fields.Many2one('stock.picking')

    def confirm(self):
        list1 = []
        for line in self.product_ids:
            for l in self.pick:
                l.write({
                    'move_line_ids_without_package': [(0, 0, {
                        'product_id': line.id,
                        'company_id': self.pick.company_id.id,
                        'product_uom_id': line.uom_id.id,
                        'location_id': self.pick.location_id.id,
                        'location_dest_id': self.pick.location_dest_id.id,

                    })]
                })
        #     list1.append(
        #         {
        #             'product_id':line.id,
        #             'company_id': self.pick.company_id.id,
        #             'product_uom_id': line.uom_id.id,
        #             'location_id': self.pick.location_id.id,
        #             'location_dest_id': self.pick.location_dest_id.id,
        #
        #          })
        # print(list1)
        # self.pick.move_line_ids_without_package=list1
        # print(list1)
