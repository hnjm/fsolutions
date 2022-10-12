# -*- coding: utf-8 -*-
#############################################################################
#
#
#############################################################################

{
    'name': 'Account Tax Report',
    'version': '15.0.1.0.3',
    'category': 'Accounting',
    'summary': """Account Tax Report""",
    'author': 'Mohamed Saber',
    'depends': ['base', 'account'],
    'data': [
        'views/tax_report_view.xml',
    ],
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
