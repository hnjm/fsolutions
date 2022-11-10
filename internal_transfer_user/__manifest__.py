# -*- coding: utf-8 -*-
{
    'name': 'Internal Transfer Users ',
    'summary': """""",
    'version': '15',
    'description': """""",
    'author': ' ',
    'company': '',
    'website': 'https://www.me.com',
    'category': 'Extra Tools',
    'depends': ['base', 'product','stock','account'],
    'license': 'AGPL-3',
    'data': [
        'security/ir.model.access.csv',
        # 'security/view_cost_price.xml',
        'views/internal_transfer.xml',
        'reports/internal_transfer_report.xml'
    ],
    'images': [],
    'demo': [],
    'installable': True,
    'auto_install': False,

}
