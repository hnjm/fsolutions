{
    'name': 'Print Payment Receipt',
    'version': '15.0',
    'category': 'account',
    'summary': 'Print Payment Receipt',
    'description': """
    this module use for Print Payment Receipt in PDF report"
    """,
    'author': "Mohamed Saber",
    'depends': ['account','print_invoice_ksa'],
    'license': 'AGPL-3',
    'data': [
        'report/receipt_layout.xml',
        'report/payment_cashing.xml',
        'report/payment_receipt.xml',
    ],

    'demo': [],
    "images": [
    ],
    'installable': True,
    'auto_install': False,
}
