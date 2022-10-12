from odoo import models, fields, api


class stock_update_wizard(models.TransientModel):
    _name = "stock.update.wizard"

    date = fields.Date(string="New Date", required=True)

    def update_date(self):
        self.ensure_one()
        context = dict(self._context or {})
        active_ids = context.get('active_ids', []) or []
        self.env.cr.execute(
            """UPDATE stock_picking SET date_done = %(date)s
            WHERE id in %(ids)s""",
            {'date': self.date,
             'ids': tuple(active_ids)},
        )
        self.env.cr.execute(
            """UPDATE stock_move SET date = %(date)s
            WHERE picking_id in %(ids)s""",
            {'date': self.date,
             'ids': tuple(active_ids)},
        )
        self.env.cr.execute(
            """UPDATE stock_move_line SET date = %(date)s
            WHERE picking_id in %(ids)s""",
            {'date': self.date,
             'ids': tuple(active_ids)},
        )
        moves = self.env['account.move'].sudo().search([('stock_move_id.picking_id', 'in', tuple(active_ids))])
        for mv in moves:
            mv.button_draft()
            mv.name = ''
            mv.date = self.date
            mv.action_post()
        return {'type': 'ir.actions.act_window_close'}
