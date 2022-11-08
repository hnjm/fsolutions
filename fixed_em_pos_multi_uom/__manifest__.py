# -*- coding: utf-8 -*-

{
    'name': 'Fix Pos multi UOM with Barcode',
    'version': '1.0',
    'category': 'Point of Sale',
    'sequence': 1,
    'author': 'WhiteXGate',
    'summary': 'Allows you to sell one products in different unit of measure.',
    'description': "Allows you to sell one products in different unit of measure.",
    'depends': ['point_of_sale', 'em_pos_multi_uom'],
    'assets': {
        'point_of_sale.assets': [
            ('replace', 'em_pos_multi_uom/static/src/js/pos.js', 'fixed_em_pos_multi_uom/static/src/js/pos.js'),
            'fixed_em_pos_multi_uom/static/src/js/TicketScreen.js',
        ],
    },
    'installable': True,
    'website': '',
    'auto_install': False,
}
