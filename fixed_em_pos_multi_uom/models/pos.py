from odoo import models

class PosOrderLine(models.Model):
    _inherit = "pos.order.line"
    
    def _export_for_ui(self, orderline):
        vals = super(PosOrderLine, self)._export_for_ui(orderline)
        vals['wvproduct_id'] = [orderline.product_uom.id, orderline.product_uom.name]
        return vals