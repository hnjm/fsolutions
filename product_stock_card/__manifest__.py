# -*-coding: utf-8 -*-
{
    'name': "Product Stock Card",

    'summary': "Report for Transactions in and out in the stock for products ",

    'description': """
        View all transactions of products for specific location in selected period
    """,

    'author': "Ahmed mokhlef",
    'Note': "Extract and update the source code of hyd_stock_card addon that its author (HyD Freelance)",
    'category': 'Stock',
    'version': '15.0.1',
    'license': 'AGPL-3',
    'depends': ['base','stock'],

    'data': [
        'security/ir.model.access.csv',
        'reports/stock_move_stock_card.xml',
        'wizards/stock_card_wizard_views.xml',
    ],
    'demo': [],
    'installable': True,
    'price': 20,
    'currency': 'EUR',
}
