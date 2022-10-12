from odoo import models, fields, api, _
from odoo.osv import expression
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.float_utils import float_is_zero
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools.misc import formatLang, get_lang
from odoo.tests import tagged, Form


class Partner(models.Model):
    _inherit = "res.partner"

    def write(self, vals):
        if 'name' in vals or 'vat' in vals:
            has_adviser_group = self.env.user.has_group(
                'print_invoice_ksa.group_invoice_checker')
            if not has_adviser_group:
                for rec in self:
                    if rec.total_invoiced > 0.0:
                        raise ValidationError(_('You can not update Partner have invoices posted.'))
        return super(Partner, self).write(vals)
