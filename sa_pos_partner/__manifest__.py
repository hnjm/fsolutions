# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Partner in Point of Sale',
    'author': 'Mohamed Saber',
    'category': 'Accounting/Localizations/Point of Sale',
    'description': """
K.S.A. POS Localization
=======================================================
    """,
    'depends': ['l10n_gcc_pos','pos_branch','print_invoice_ksa'],
    'data': [
        'views/pos_config_view.xml',
        'views/invoice_report.xml',
    ],
    'assets': {
        'web.assets_qweb': [
            'sa_pos_partner/static/src/xml/OrderReceipt.xml',
        ],
    },
}
