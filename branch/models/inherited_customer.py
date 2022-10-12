# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class ResPartnerIn(models.Model):
    _inherit = 'res.partner'

    
    @api.model
    def default_get(self, default_fields):
        res = super(ResPartnerIn, self).default_get(default_fields)
        res.update({
            'branch_ids': self.env.user.branch_id.ids or False
        })
        return res

    branch_ids = fields.Many2many('res.branch', string="Branches")