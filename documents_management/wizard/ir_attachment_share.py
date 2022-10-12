from odoo import api, fields, models

class IrAttachmentsShare(models.TransientModel):
    _name = 'ir.attachment.share'
    _description = 'Share Attachments'

    name = fields.Char('Name')
    link = fields.Char('Link', readonly=True)

    @api.model
    def default_get(self, fields):
        res = super(IrAttachmentsShare, self).default_get(fields)        
            
        context = self._context or {}
        active_id = context.get('active_id')
        active_model = context.get('active_model')

        attachment_obj = self.env['ir.attachment'].search([('id', '=', active_id)])

        attachment_obj.sudo()._ensure_token()
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        attachment_url = "%s/web/get_attachments/token/" %(base_url)
        
        if attachment_obj.type == 'binary' and attachment_obj.access_token:
            link = attachment_url  + str(attachment_obj.access_token)
        
        if attachment_obj.type == 'url':
            link = attachment_obj.url

        res['name'] = attachment_obj.name
        res['link'] = link
        return res