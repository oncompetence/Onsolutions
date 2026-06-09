{
    'name': 'Control de Stock Mínimo para MercadoLibre',
    'version': '19.0.1.0.0',
    'category': 'Inventory',
    'summary': 'Pausa publicaciones de MercadoLibre cuando el stock cae por debajo del mínimo configurado.',
    'depends': ['product', 'stock', 'meli_integration'],
    'data': [
        'views/product_product_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}