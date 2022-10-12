{
    'name': 'Update Inventory Date',
    'description': 'Update Effective Date in Inventory',
    'version': '1.0.0',
    'license': 'LGPL-3',
    'category': 'Inventory',
    'author': 'Mohamed Saber',
    'website': '',
    'depends': [
        'stock','stock_account'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/stock_picking_view.xml',
        'wizard/stock_update_wizard_view.xml',
    ],
    'application': True,
    'installable': True,
}
