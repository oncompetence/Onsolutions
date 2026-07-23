# -*- coding: utf-8 -*-
{
    "name": "Sale Order Line Search & Report Sort",
    "version": "19.0.2.1.0",
    "summary": "Buscador y orden visual (alfabético/categoría) en formulario y PDF para pedidos de venta.",
    "description": """ 
Este módulo extiende SaleOrderLineOne2Many sumándole:
- Input de búsqueda en vivo sobre las filas renderizadas.
- Selector de orden VISUAL (Manual / Alfabético / Categoría) integrado.
- Aplicación de este mismo orden visual al momento de imprimir el PDF del pedido.

En ningún caso se toca el campo `sequence` real ni se rompen las secciones nativas o los productos tipo Combo.
    """,
    "category": "Sales",
    "author": "Gonzalo Fonseca",
    "depends": ["sale"],
    "data": [
        "views/sale_order_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "sol_o2m_search/static/src/fields/sol_o2m_search/*.js",
            "sol_o2m_search/static/src/fields/sol_o2m_search/*.xml",
            "sol_o2m_search/static/src/fields/sol_o2m_search/*.scss",
        ],
    },
    "installable": True,
    "auto_install": False,
    "license": "LGPL-3",
}