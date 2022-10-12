# -*- coding: utf-8 -*-
{
    'name': "Bank Fees/Commission",

    'summary': """This app can add bank Fees in payment""",

    'description': """
        This app can add bank Fees in payment
    """,

    'author': "Mohamed Saber",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Accounting',
    'version': '15.1',

    # any module necessary for this one to work correctly
    'depends': ['base','account'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/account_journal_views.xml',
        'views/account_payment.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}