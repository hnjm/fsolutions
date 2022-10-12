import json
import base64
import logging
import werkzeug

from odoo import http
from odoo.http import request

from odoo.tools import html_escape
from odoo.addons.web.controllers.main import _serialize_exception


class IrAttachemntsShareController(http.Controller):
    
    @http.route('/web/get_attachments/token/<string:token>', type='http', auth="none")
    def get_attachments(self, token , **kwargs):
        try:
            ir_attachment_env = request.env['ir.attachment']
            ir_attachment = ir_attachment_env.sudo().search([('access_token', '=', token)])
            if ir_attachment:
                for attachment in ir_attachment:                    
                    content = base64.b64decode(attachment.datas)
                    disposition = 'attachment; filename=%s' % werkzeug.urls.url_quote(attachment.name)                    
                    return request.make_response(
                        content,
                        [('Content-Length', len(content)),
                         ('Content-Type', attachment.mimetype),
                         ('Content-Disposition', disposition)])
            else:
                error = {
                    'code': 200,
                    'message': "Unable to locate the attachments",
                }
            return request.make_response(html_escape(json.dumps(error)))
            
        except Exception as e:
            se = _serialize_exception(e)
            error = {
                'code': 200,
                'message': "Error - Odoo Server Error",
            }
            return request.make_response(html_escape(json.dumps(error)))
