# -*- coding: utf-8 -*-
{
    'name': "Drdr_invoice_template",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Gourida Said",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','print_invoice_ksa'],

    # always loaded
    'data': [
        'reports/inherit_external_layout_tax_invoice.xml',
        'reports/inherit_tax_invoice_report_document.xml',
        'views/company.xml'
    ],
    'assets': {
        'web.report_assets_pdf': [ 
            "/drdr_invoice_template/static/src/css/report.css"
        ],

    },
    'installable': True,
    'application': True,
    'license': "AGPL-3",
    
}
