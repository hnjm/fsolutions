# -*- coding: utf-8 -*-
###################################################################################
#
#    PS,Development Team.
#    Copyright (C) 2022
#    Authors: Mohamed Saber,mohamedabosaber94@gmail.com,+201153909418
###################################################################################
{
    'name': "Stock Approval",

    'summary': """
        Stock Approval""",

    'description': """
        Stock Approval
    """,

    'author': 'Mohamed Saber',
    'category': 'Inventory',
    'version': '15.1',

    # any module necessary for this one to work correctly
    'depends': ['base','stock','hr_approval_structure'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'wizard/reject_reason_wizard.xml',
        'views/stock_picking.xml',
        'views/inherited_stock_location.xml',
    ],
}
