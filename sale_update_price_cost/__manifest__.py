{
    'name': 'Alerta de Actualización de Tarifas en Ventas',
    'version': '18.0.1.0.0',
    'category': 'Sales',
    'summary': 'OnSolutions',
    'description': 'Muestra una alerta en el presupuesto si los precios están desactualizados respecto a la tarifa',
    'author': 'Gonzalo Fonseca',
    'license': 'LGPL-3',
    'depends': ['sale'],
    'data': [
        'views/sale_order_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}