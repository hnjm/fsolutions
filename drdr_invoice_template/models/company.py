from odoo import models,fields

class Company(models.Model):
    _inherit = 'res.company'


    image = fields.Binary(string='Invoice Image')
    
    
        
    
