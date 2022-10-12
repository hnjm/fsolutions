# -*- coding: utf-8 -*-
{
    'name': 'KSA Invoice Templates',
    'version': '15.0',
    'category': 'Accounting',
    'author': 'Mohamed Saber',
    'summary': 'Generate Multi Invoice Template',
    'description': """
    -Configuration For Qr Code Type (Url,Text Information)
    -For Url It Will Open Invoice In Portal.
    -For Text Information , You Must Specify Invoice Field's To Show.
    -Add QR Code In Invoice Form View.
    -Add QR Code In Invoice Report.
    -Add QR code in POS Print.
    """,
    'depends': ['base',
        'account','l10n_sa_invoice'
    ],
    'data': [
        'security/security.xml',
        'report/tax_invoice_layout.xml',
        'report/tax_simplified_invoice_report_view.xml',
        'report/tax_invoice_report_view.xml',
        'report/tax_project_invoice_report_view.xml',
        'report/invoice_report_action.xml',
        'views/res_config_settings_views.xml',
        'views/account_invoice_view.xml',
        'views/res_currency.xml',
    ],
    'images': [
    ],
    'installable': True,
    'application': True,
    'license': "AGPL-3",
}
