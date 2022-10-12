# -*- coding: utf-8 -*-
{
    'name': 'Salla Sales & Invoices',
    'version': '15.0',
    'category': 'Sales',
    'author': 'Mohamed Saber',
    'summary': '',
    'description': """
    """,
    'depends': ['base','sale','account','print_invoice_ksa','analytic'
    ],
    'data': [
        'report/sale_layout.xml',
        'report/sale_order_report_view.xml',
        'report/tax_invoice_template.xml',
        'report/sale_report_action.xml',
        'views/account_config_view.xml',
        'views/sale_order_view.xml',
        'views/account_move_view.xml',
    ],
    'images': [
    ],
    'installable': True,
    'application': True,
    'license': "AGPL-3",
}
