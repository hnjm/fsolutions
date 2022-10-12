# -*- coding: utf-8 -*-
#################################################################################
# Author      : CFIS (<https://www.cfis.store/>)
# Copyright(c): 2017-Present CFIS.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://www.cfis.store/>
#################################################################################

{
    "name": "Document Management System",
    "summary": "This module provide simple and very useful functionality to manage documents with directory (folders), tags, export, numbering, versions  and security groups.",
    "version": "15.0.1",
    "description": """
        This module provide simple and very useful functionality to manage documents with directory (folders), tags, export, numbering, versions  and security groups.
        Directory Views        
        Documents Send Document by mail
        Documents Tags
        Documents numbering
        Documents versions
        Documents Folder Views  
        Documents Export to Zip
        User Group and Manager Group Security
        Folder View Based on Document modules
        Document versions
        Documet numbering
        Filter by tags
        Document Share
        Document Send by Email
        Export Multiple Documents to Zip
    """,    
    "author": "CFIS",
    "maintainer": "CFIS",
    "license" :  "Other proprietary",
    "website": "https://www.cfis.store",
    "images": ["images/documents_management.png"],
    "category": "Sales",
    "depends": [
        "base",
        "mail",
    ],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "data/mail_attachment_data.xml",
        "data/attachment_sequence_data.xml",
        "views/folders_views.xml",
        "views/ir_attachment_views.xml",
        "views/tags_views.xml",            
        "views/res_partner_views.xml",            
        "wizard/ir_attachment_export.xml",        
        "wizard/ir_attachment_share.xml",        
    ],
    "assets": {
        "web.assets_backend": [
            "/documents_management/static/src/css/style.css",
            "/documents_management/static/src/js/ir_attachment_document_viewer.js",
            "/documents_management/static/src/js/ir_attachment_preview.js",
            "/documents_management/static/src/js/ir_attachment_share.js",
        ],
        "web.assets_qweb": [
            "/documents_management/static/src/xml/*.xml",
        ],
    },    
    "installable": True,
    "application": True,
    "price"                 :  11,
    "currency"              :  "EUR",
    "pre_init_hook"         :  "pre_init_check",
}
