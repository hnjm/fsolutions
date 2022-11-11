from odoo import models,fields

class Company(models.Model):
    _inherit = 'res.company'


    logo_quotation = fields.Binary(string='Quotation Image')
    
    
        
    
