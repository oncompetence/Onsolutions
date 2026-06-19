# -*- coding: utf-8 -*-
{
    'name': 'Propagación de Campos en Asientos Contables',
    'version': '19.0.1.0.0',
    'summary': 'Agrega campos M2M en account.move y los propaga a las líneas.',
    'category': 'Accounting',
    'author': 'Tiago Rodriguez',
    'depends': ['account', 'account_invoice_extract'],
    'data': [
        'security/ir.model.access.csv',
        'views/account_move_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}