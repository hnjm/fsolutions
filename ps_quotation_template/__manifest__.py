# -*- coding: utf-8 -*-
{
    'name': 'PS Quotation Template',
    'version': '15.0',
    'category': 'Sales',
    'author': 'Mohamed Saber',
    'summary': '',
    'description': """
    """,
    'depends': ['base',
        'sale','print_invoice_ksa',
    ],
    'data': [
        'report/sale_layout.xml',
        'report/sale_order_report_view.xml',
        'report/tax_invoice_template.xml',
        'report/sale_report_action.xml',
        'views/sale_order_line_view.xml',
        'views/account_move_view.xml',
    ],
    'images': [
    ],
    'installable': True,
    'application': True,
    'license': "AGPL-3",
}
