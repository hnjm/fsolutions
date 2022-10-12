from datetime import datetime
import base64
import time
import io
import zipfile

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class IrAttachmentExport(models.TransientModel):
    _name = "ir.attachment.export"
    _description = 'Ir Attachment Export Zip'

    @api.model
    def _default_name(self):
        return "%s_%s" % (
            _("attachment_export"), datetime.now().strftime('%Y%m%d%H%M')  +'.zip')

    name = fields.Char('Filename', default=_default_name, required=True, readonly= True)
    zip_data = fields.Binary("Zip File")

    def action_export_zip(self):
        active_ids = self.env.context['active_ids']
        attachments = self.env[self.env.context['active_model']].browse(active_ids)        

        fp = io.BytesIO()
        zf = zipfile.ZipFile(fp, mode="w")
        for att in attachments:
            zf.writestr(att.name, base64.b64decode(att.datas))

        zf.close()
        self.write({'zip_data':base64.b64encode(fp.getvalue())})
        name = self.name
        action = {
            'name': name,
            'type': 'ir.actions.act_url',
            'url': "/web/content/?model="+self._name+"&id=" + str(self.id) + "&field=zip_data&download=true&filename="+ name,
            'target': 'self',
            }
        
        return action