# -*- coding: utf-8 -*-
{
    'name': "POS Bank Fees/Commission",

    'summary': """This app can add bank Fees in POS""",

    'description': """
        This app can add bank Fees in POS
    """,

    'author': "Mohamed Saber",
    'category': 'Accounting',
    'version': '15.1',

    # any module necessary for this one to work correctly
    'depends': ['base','account','point_of_sale'],

    # always loaded
    'data': [
        'views/pos_payment_method_views.xml',
        'views/pos_payment.xml',
    ],
}