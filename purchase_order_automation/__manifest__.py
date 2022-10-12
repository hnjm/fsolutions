# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo,NTS
#    Copyright (C) 2021 dev:Mohamed Saber.
#    E-Mail:mohamedabosaber94@gmail.com
#    Mobile:+201153909418
#
##############################################################################
{
    'name' : 'Purchase Order Automation',
    'version' : '1.0',
    'author':'Mohamed Saber',
    'category': 'Purchase',
    'summary': """Enable auto Purchase workflow with Purchase order confirmation. Include operations like Auto Create Invoice, Auto Validate Invoice and Auto Transfer Recipt Order.""",
    'description': """

        You can directly create invoice and set done to delivery order by single click

    """,
    'license': 'LGPL-3',
    'support':'mohamedabosaber94@gmail.com',
    'depends' : ['purchase','stock','purchase_stock'],
    'data': [
        'views/purchase_config_view.xml',
    ],
    
    'installable': True,
    'application': True,
    'auto_install': False,

}
