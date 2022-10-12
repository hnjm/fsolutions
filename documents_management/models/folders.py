from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class DocumentFolder(models.Model):
    _name = 'documents.folder'
    _description = 'Directory'
    _parent_name = 'parent_folder_id'
    _order = 'name'
    _rec_name = 'complete_name'
    
    name = fields.Char(string='Name', required=True )
    complete_name = fields.Char('Complete Name', compute='_compute_complete_name', recursive=True, store=True) 
    sequence = fields.Integer('Sequence', default=10)   
    company_id = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.company)
    parent_folder_id = fields.Many2one('documents.folder',string='Parent Folder', ondelete="cascade", domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    children_folder_ids = fields.One2many('documents.folder','parent_folder_id', string="Sub Folders")
    attachment_ids = fields.One2many('ir.attachment', 'folder_id', string="Attachments")
    model_id = fields.Many2one('ir.model', string='Model' )
    attachment_count = fields.Integer(compute="_compute_attachment_count")    
    
    def name_get(self):
        if not self.env.context.get('hierarchical_naming', True):
            return [(record.id, record.name) for record in self]
        return super(DocumentFolder, self).name_get()

    @api.model
    def name_create(self, name):
        return self.create({'name': name}).name_get()[0]

    @api.depends('name', 'parent_folder_id.complete_name')
    def _compute_complete_name(self):
        for folder in self:
            if folder.parent_folder_id:
                folder.complete_name = '%s / %s' % (folder.parent_folder_id.complete_name, folder.name)
            else:
                folder.complete_name = folder.name
    
    @api.constrains('parent_folder_id')
    def _check_parent_folder_id(self):
        if not self._check_recursion():
            raise ValidationError(_('You cannot create recursive folder.'))

    @api.depends()
    def _compute_attachment_count(self):
        read_group_var = self.env['ir.attachment'].read_group(
            [('folder_id', 'in', self.ids)],
            fields=['folder_id'],
            groupby=['folder_id'])

        attachment_count_dict = dict((d['folder_id'][0], d['folder_id_count']) for d in read_group_var)
        for record in self:
            record.attachment_count = attachment_count_dict.get(record.id, 0)
       
    @api.constrains('model_id')
    def _check_model(self):
        self.ensure_one()
        model = self.env['documents.folder'].sudo().search([('model_id.model', '=', self.model_id.model)])
        if len(model) > 1:
            raise ValidationError(_('This models directory has already been established.!'))
            
    def action_see_attachments(self):
        domain = [('folder_id', '=', self.id)]
        return {
            'name': _('Documents'),
            'domain': domain,
            'res_model': 'ir.attachment',
            'type': 'ir.actions.act_window',
            'views': [(False, 'list'), (False, 'form')],
            'view_mode': 'tree,form',
            'context': "{'default_folder_id': %s}" % self.id
        }
        return res

    @api.model
    def create(self,vals):
        result = super(DocumentFolder, self).create(vals)        
        attachments = self.env['ir.attachment'].sudo().search([])
        model_id = vals.get('model_id' ,False)
        if model_id:
            for attachment in attachments:
                model = self.env['ir.model'].sudo().search([('id', '=', model_id)], limit=1)            
                if model and attachment.res_model == model.model:
                    attachment.sudo().write({
                        'folder_id': result.id
                    })
        return result
