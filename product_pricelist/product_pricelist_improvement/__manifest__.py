{
    "name": "Mejora de Lista de Precios",
    "summary": "Oncompetence Solutions",
    "description": "Mejora de Lista de Precios",
    "version": "18.0",
    "author": "Micaela Ortiz",
    "license": "AGPL-3",
    "depends": [
        "base",
        "stock",
        "sale",
        "sale_management",
        "account",
        "product",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/product_price_history_views.xml",
        # "views/product_pricelist_views.xml",
        "views/pricelist_oncompetence_views.xml",
        "views/product_template_views.xml",
    ],
    'assets': {
        'web.assets_backend': [
            'product_pricelist_improvement/static/src/css/style.css',
        ],
    },
    "installable": True,
    "application": True,
    "auto_install": False,
}
