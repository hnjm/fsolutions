from random import randint
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.osv import expression

class TagsCategories(models.Model):
    _name = "documents.tag.category"
    _description = "Category"
    _order = "sequence, name"

    folder_id = fields.Many2one('documents.folder', ondelete="cascade")
    name = fields.Char(required=True)
    tag_ids = fields.One2many('documents.tag', 'category_id')
    tooltip = fields.Char(help="hover text description", string="Tooltip")
    sequence = fields.Integer('Sequence', default=10)

    _sql_constraints = [
        ('name_unique', 'unique (folder_id, name)', "Category already exists in this folder"),
    ]
    
class Tags(models.Model):
    _name = "documents.tag"
    _description = "Tag"
    _order = "sequence, name"

    def _get_default_color(self):
        return randint(1, 11)

    name = fields.Char(required=True, translate=True)
    sequence = fields.Integer('Sequence', default=10)
    color = fields.Integer(string='Color Index', default=_get_default_color)
    folder_id = fields.Many2one('documents.folder', string='Directory')
    sequence = fields.Integer('Sequence', default=10)
    category_id = fields.Many2one('documents.tag.category', ondelete='cascade', required=True)        

    _sql_constraints = [
        ('tag_category_name_unique', 'unique (category_id, name)', "Tag already exists for this category"),
    ]
    
    def name_get(self):
        name_get_list = []
        for rec in self:
            name_get_list.append((rec.id, "%s > %s" % (rec.category_id.name, rec.name)))
        return name_get_list