# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class DailyPurchaseWizard(models.TransientModel):
    _name = "daily.purchase.wizard"

    from_date = fields.Date('From Date')
    to_date = fields.Date('To Date')

    @api.constrains('from_date', 'to_date')
    def _check_date(self):
        if self.from_date and self.to_date and self.from_date >= self.to_date:
            raise ValidationError('To date must be greater then from date')

    def check_report(self):
        data = {'form': self.read()[0]}
        order_ids = self.env['purchase.order'].search([('date_order', '>=', self.from_date), ('date_order', '<=', self.to_date), ('state', '=', 'purchase')])
        data['order_ids'] = order_ids.ids
        return self.env.ref('pways_daily_purchase_report.daily_purchare_report_id').report_action(self, data=data)