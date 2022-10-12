from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, AccessError
from odoo.exceptions import ValidationError
import base64
import xlsxwriter
import io
from datetime import datetime, time, timedelta
from dateutil.rrule import rrule, DAILY
from functools import partial
from itertools import chain
from pytz import timezone, utc
from datetime import datetime


def is_int(n):
    try:
        float_n = float(n)
        int_n = int(float_n)
    except ValueError:
        return False
    else:
        return float_n == int_n


def is_float(n):
    try:
        float_n = float(n)
    except ValueError:
        return False
    else:
        return True


class StagnantProductsReport(models.TransientModel):
    _name = 'stagnant.products.report.wizard'

    date_from = fields.Date('Date From')
    date_to = fields.Date('Date To')
    categ_ids = fields.Many2many('product.category')
    sale_qty = fields.Float()
    excel_sheet = fields.Binary()

    @api.constrains('date_from', 'date_to')
    def _validate_date(self):
        for rec in self:
            if rec.date_from and rec.date_to:
                if rec.date_to < rec.date_from:
                    raise ValidationError(_('"Date To" time cannot be earlier than "Date From" time.'))
            else:
                raise ValidationError(_('"Please insert Date from and Date to'))

    def get_products(self):
        domain = []
        if self.categ_ids:
            domain.append(('categ_id', 'in', self.categ_ids.ids))
        products = self.env['product.product'].search(domain)
        result = []
        for product in products:
            sale_moves = self.env['account.move.line'].search(
                [('date', '>=', self.date_from), ('date', '<=', self.date_to), ('move_id.state', '=', 'posted'),
                 ('move_id.payment_state', '!=', 'reversed'),
                 ('move_id.move_type', '=', 'out_invoice'), ('product_id', '=', product.id)], order='date desc')
            if sale_moves:
                if sum(sale_moves.mapped('quantity')) <= self.sale_qty:
                    result.append(product)
            else:
                result.append(product)

        return result

    def get_sale_move(self, product):
        sale_moves = self.env['account.move.line'].search(
            [('date', '>=', self.date_from), ('date', '<=', self.date_to), ('move_id.state', '=', 'posted'),
             ('move_id.payment_state', '!=', 'reversed'),
             ('move_id.move_type', '=', 'out_invoice'), ('product_id', '=', product.id)], order='date desc')
        sale_moves = sum(sale_moves.mapped('quantity'))
        return sale_moves

    def get_last_sale(self, product):
        sale_move = self.env['account.move.line'].search(
            [('date', '>=', self.date_from), ('date', '<=', self.date_to), ('move_id.state', '=', 'posted'),
             ('move_id.payment_state', '!=', 'reversed'),
             ('move_id.move_type', '=', 'out_invoice'), ('product_id', '=', product.id)], limit=1, order='date desc')
        return sale_move

    def get_purchase_move(self, product):
        purchase_moves = self.env['account.move.line'].search(
            [('date', '>=', self.date_from), ('date', '<=', self.date_to), ('move_id.state', '=', 'posted'),
             ('move_id.journal_id.type', '=', 'purchase'), ('product_id', '=', product.id)], order='date desc')
        purchase_moves = sum(purchase_moves.mapped('quantity'))
        return purchase_moves

    def get_last_purchase(self, product):
        purchase_move = self.env['account.move.line'].search(
            [('date', '>=', self.date_from), ('date', '<=', self.date_to), ('move_id.state', '=', 'posted'),
             ('move_id.journal_id.type', '=', 'purchase'), ('product_id', '=', product.id)], limit=1, order='date desc')
        return purchase_move

    def generate_report(self):
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output)

        custom_format = workbook.add_format({
            'bold': 0,
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'text_wrap': True,
            'font_size': 12,
            'fg_color': 'white',
        })

        first_header = workbook.add_format({
            'bold': 0,
            'border': 2,
            'align': 'center',
            'valign': 'vcenter',
            'text_wrap': True,
            'font_size': 15,
            'valign': 'vcenter',
            'fg_color': '#A3C7F3'
        })

        table_header_format = workbook.add_format({
            'bold': 1,
            'border': 2,
            'align': 'center',
            'text_wrap': True,
            'font_size': 12,
            'valign': 'vcenter',
            'fg_color': '#d8d6d6'
        })

        worksheet = workbook.add_worksheet('تقرير الاصناف الراكدة')
        worksheet.set_paper(9)
        worksheet.set_portrait()
        worksheet.set_column(0, 8, 35)
        worksheet.right_to_left()
        worksheet.write(0, 0, 'أسم السجل', first_header)
        worksheet.write(0, 1, "تقرير الاصناف الراكدة", custom_format)
        worksheet.write(1, 0, 'من', first_header)
        worksheet.write(1, 1, str(self.date_from), custom_format)
        worksheet.write(1, 2, 'الي', first_header)
        worksheet.write(1, 3, str(self.date_to), custom_format)

        worksheet.write(3, 0, 'اسم الصنف', table_header_format)
        worksheet.write(3, 1, 'فئة المنتج', table_header_format)
        worksheet.write(3, 2, 'تاريخ اخر فاتورة مبيعات', table_header_format)
        worksheet.write(3, 3, 'رقم السند المبيعات', table_header_format)
        worksheet.write(3, 4, 'تاريخ اخر فاتورة مشتريات', table_header_format)
        worksheet.write(3, 5, 'رقم السند المشتريات', table_header_format)
        worksheet.write(3, 6, 'كمية البيع', table_header_format)
        worksheet.write(3, 7, 'كمية الشراء', table_header_format)
        worksheet.write(3, 8, 'الرصيد الحالي', table_header_format)
        row = 4
        col = 0

        if self.get_products():
            total_qty = total_sale = total_purchase = 0.0
            for line in self.get_products():
                worksheet.write(row, col, str(line.name)+"["+str(line.barcode or "")+"]["+str(line.default_code or "")+"]", custom_format)
                worksheet.write(row, col + 1, line.categ_id.name, custom_format)
                last_sale = self.get_last_sale(line)
                worksheet.write(row, col + 2, str(last_sale.date) if last_sale else "", custom_format)
                worksheet.write(row, col + 3, last_sale.move_id.name if last_sale else "", custom_format)
                last_purchase = self.get_last_purchase(line)
                worksheet.write(row, col + 4, str(last_purchase.date) if last_purchase else "", custom_format)
                worksheet.write(row, col + 5, last_purchase.move_id.name if last_purchase else "", custom_format)
                total_sale += self.get_sale_move(line)
                worksheet.write(row, col + 6, self.get_sale_move(line), custom_format)
                total_purchase += self.get_purchase_move(line)
                worksheet.write(row, col + 7, self.get_purchase_move(line), custom_format)
                worksheet.write(row, col + 8, line.qty_available, custom_format)
                total_qty += line.qty_available
                row += 1
            worksheet.write(row, col + 5, "الاجمالي", custom_format)
            worksheet.write(row, col + 6, total_sale, custom_format)
            worksheet.write(row, col + 7, total_purchase, custom_format)
            worksheet.write(row, col + 8, total_qty, custom_format)
        else:
            raise ValidationError("Nothing to Print!")

        workbook.close()
        output.seek(0)
        self.write({'excel_sheet': base64.encodestring(output.getvalue())})

        return {
            'type': 'ir.actions.act_url',
            'name': 'Products',
            'url': '/web/content/stagnant.products.report.wizard/%s/excel_sheet/stagnant_products_report.xlsx?download=true' % (
                self.id),
            'target': 'self'
        }
