# -*- coding: utf-8 -*-
"""Approval Template Models"""

from odoo import api, fields, models


class AuthorizationApprovalTemplate(models.Model):
    """Approval Template Model.

    This is used to define the approval mandate per model to be used later by
    objects of that model."""
    _name = 'hr.authorization.approval.template'

    name = fields.Char("Template Name", required=True, index=True)
    res_model_id = fields.Many2one('ir.model', "Model", required=True,
                                   ondelete='cascade',
                                   help="The model which this template is "
                                        "linked with.")
    res_model = fields.Char("Model Name", compute='_compute_res_model',
                            store=True)
    line_ids = fields.One2many(
        'hr.authorization.approval.template.line',
        'template_id',
        "Template Lines",
        required=True
    )
    active = fields.Boolean("Active", default=True)
    company_id = fields.Many2one('res.company', string='Company',
                                 default=lambda self: self.env.user.company_id)
    user_id = fields.Many2one('res.users', 'Responsible')

    @api.depends('res_model_id', 'res_model_id.name')
    def _compute_res_model(self):
        """Compute model name from res_model_id field."""
        for record in self:
            record.res_model = record.res_model_id and \
                record.res_model_id.model or None


class AuthorizationApprovalTemplateLine(models.Model):
    """Approval Template Line Model.

    This is used to define the approval workflow stages of the mandate."""
    _name = 'hr.authorization.approval.template.line'
    _order = 'sequence'


    name = fields.Char("Stage Name", required=True)
    sequence = fields.Integer("Sequence", required=True, default=1,
                              help="The order of the stages inside the "
                                   "template, same number means parallel "
                                   "approvals.")
    template_id = fields.Many2one('hr.authorization.approval.template',
                                  "Approval Template", required=True,
                                  index=True)
    department_id = fields.Many2one('hr.department', "Department",
                                    domain=[('parent_id', '!=', False)])
    parent_department_id = fields.Many2one('hr.department', "Parent Department",
                                           domain=[('parent_id', '=', False)])
    company_id = fields.Many2one('res.company', "Company",
                                 domain=[('parent_id', '!=', False)])
    parent_company_id = fields.Many2one('res.company', "Holding",
                                        domain=[('parent_id', '=', False)])
    user_ids = fields.Many2many('res.users',
                                'approval_template_res_users_rel',
                                'template_id',
                                'user_id',
                                "Users")
    domain = fields.Text("Filter Domain", default="[]")
    required = fields.Boolean("Required Stage", default=True)
    current_user = fields.Boolean("Current Direct Manager based", default=False)

    @api.onchange('department_id', 'parent_department_id', 'company_id',
                  'parent_company_id')
    def _onchange_department_id(self):
        if self.department_id:
            self.parent_department_id = self.department_id.parent_id
            self.company_id = self.department_id.company_id
            self.parent_company_id = self.company_id.parent_id
        elif self.parent_department_id:
            self.company_id = self.parent_department_id.company_id
            self.parent_company_id = self.company_id.parent_id
        elif self.company_id:
            self.parent_company_id = self.company_id.parent_id

