# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import date, datetime
from odoo.exceptions import ValidationError
import math

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, AccessError
from odoo.exceptions import UserError
from odoo.addons import decimal_precision as dp
import base64
import xlsxwriter
import io
from werkzeug.urls import url_encode

class Location(models.Model):
    _inherit = "stock.location"

    responsible_id = fields.Many2one('res.users', 'Responsible')

class Picking(models.Model):
    _name = "stock.picking"
    _inherit = ['stock.picking', 'hr.authorization.approval']

    rejection_comment = fields.Text(tracking=True)
    location_responsible_id = fields.Many2one(related='location_dest_id.responsible_id')

    def action_confirm(self):
        for rec in self.filtered(lambda r: r.approval_template_id):
            if rec.approval_status != 'approved':
                raise UserError(_("You can't validate this Order without "
                                  "completing the Approval Mandate "
                                  "signatures."))
        return super().action_confirm()

    @api.model
    def create(self, vals):
        res = super(Picking, self).create(vals)
        template = self.env['hr.authorization.approval.template'].sudo().search(
            [('company_id', '=', res.company_id.id), ('res_model_id', '=', res._name)], limit=1)
        if template and res.picking_type_code == 'internal':
            res.action_approval_create(template)
        return res

    def action_approval_send_mail(self, action, line):
        """Override to add request details."""
        self.ensure_one()
        ctx = dict(self.env.context)
        if action != 'waiting':
            ctx.update(mail_subject=("%s , %s has been %s") %
                                    (self._description, self.name, line.status))
            ctx.update(line=self.user_id)
            ctx.update(mail_to=self.user_id.login)
        if action == 'waiting':
            ctx.update(mail_subject=("%s , %s is waiting for your "
                                     "approval") % (self._description, self.name))
        ctx.update(mail_cc=self.user_id.login)
        ctx.update(mail_signature="IT Management Team")
        return super(Picking, self.with_context(**ctx)) \
            .action_approval_send_mail(action, line)

    def action_approval_next_reject(self):
        """Override to go to next request after rejection."""
        super(Picking, self).action_approval_next_reject()
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'stock.reject.wizard',
            'views': [[False, 'form']],
            'target': 'new',

        }


    def get_approval_current_user_data(self, user_field='location_responsible_id'):
        """
        :param user_field: string representing a `Many2one` field pointing at
        `res.users` model to be used to get all the user specific approvals.
        If the owner partner of the request has no user or is a non-it employee,
        we compute the user representing a user in the same division and is
        stored in field `responsible_division_member_user_id` to be sent off to meth
        `get_approval_current_user_data`.
        NOTE: This field is only populated if it needs to be to prevent
        performance degradation.
        :return: call super method
        """
        self.ensure_one()
        if not user_field:
            user_field = 'create_uid'
        return super(Picking, self) \
            .get_approval_current_user_data(user_field)
