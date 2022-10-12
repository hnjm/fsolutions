# See LICENSE file for full copyright and licensing details.

{
    'name': 'Product Statement Report',
    'version': '15.0.1.0.0',
    'category': 'Accounting',
    'license': 'AGPL-3',
    'author': 'Mohamed Saber',
    'summary': 'Product Statement Report',
    'depends': [
        'account', 'product','stock','account_invoice_margin'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/customer_statement_report_view.xml',
        'wizard/stagnant_products_report_view.xml',
    ],
    'installable': True,
    'auto_install': False,
}
