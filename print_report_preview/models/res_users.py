from odoo import api, fields, models, tools, _

class ResUsers(models.Model):
    _inherit = "res.users"

    report_preview = fields.Boolean(string="Report Preview", default=True)
    report_automatic_printing = fields.Boolean(srting="Report Automatic printing")    

    def __init__(self, pool, cr):
        init_res = super(ResUsers, self).__init__(pool, cr)
        # duplicate list to avoid modifying the original reference
        type(self).SELF_WRITEABLE_FIELDS = list(self.SELF_WRITEABLE_FIELDS)
        type(self).SELF_WRITEABLE_FIELDS.extend(["report_preview", "report_automatic_printing"])
        # duplicate list to avoid modifying the original reference
        type(self).SELF_READABLE_FIELDS = list(self.SELF_READABLE_FIELDS)
        type(self).SELF_READABLE_FIELDS.extend(["report_preview", "report_automatic_printing"])
        return init_res

    def report_preview_reload(self):
        return {
            "type": "ir.actions.client",
            "tag": "reload_context"
        }
    
    @api.model
    def action_get_print_report_preview(self):
        if self.env.user:
            return self.env['ir.actions.act_window']._for_xml_id('print_report_preview.action_simple_print_report_preview')