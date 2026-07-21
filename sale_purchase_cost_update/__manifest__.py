# -*- coding: utf-8 -*-
{
    'name': 'Sale Purchase Cost Update',
    'version': '19.0.1.0.0',
    'summary': 'Oncompetence Solutions',
    'description': 'Este módulo actualiza el costo de los productos en las órdenes de venta y compra, utilizando el costo de reposición del producto.',
    'author': 'Gonzalo Fonseca',
    'license': 'AGPL-3',
    'category': 'Sales/Purchase',
    'depends': [
        'sale_management',
        'purchase',
        'product_replenishment_cost',
    ],
    'data': [
        'views/sale_order_views.xml',
        'views/purchase_order_views.xml',
        'views/product_supplierinfo_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
