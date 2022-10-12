# -*- coding: utf-8 -*-
{
    'name': "mandatory analytic account",

    'summary': """This app can add mandatory analytic account and tags in account""",

    'description': """
        This app can add mandatory analytic account and tags in account
    """,

    'author': "Mohamed Saber",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Accounting',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','account'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/account_account_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}