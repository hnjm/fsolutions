# -*- coding: utf-8 -*-

{
    "name": "Sale Product Last Price",
    "summary": "Order Line Last Price In Sale",
    "version": "15.0.1.0.0",
    "category": 'Sales',
    "description": """Order Line Last Price In Sale""",
    'author': 'Mohamed Saber',
    "depends": [
        'sale_management',
    ],
    "data": [
        'security/security.xml',
        'views/sale_order_line.xml',
    ],
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
