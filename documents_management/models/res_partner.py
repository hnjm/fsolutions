from odoo import api, models, fields, tools, _

class Partner(models.Model):
    _inherit = "res.partner"
    
    
    def _compute_ir_attachments_count(self):
        for rec in self:
            ir_attachments = self.env['ir.attachment'].sudo().search([
            '|',('partner_id', 'in', self.ids), 
            '&',('res_model','=', 'res.partner'),('res_id','=', self.id)
            ])
            rec.ir_attachments_count = len(ir_attachments)
    
    ir_attachments_count = fields.Integer(compute='_compute_ir_attachments_count', string='Documents Count')
    
    def action_view_ir_attachments(self):
        self.ensure_one()
        ir_attachments = self.env['ir.attachment'].sudo().search([
            '|',('partner_id', 'in', self.ids), 
            '&',('res_model','=', 'res.partner'),('res_id','=', self.id)
            ])
        return {
            'type': 'ir.actions.act_window',
            'name': _('Partner Documents'),
            'res_model': 'ir.attachment',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', ir_attachments.ids)],
        }