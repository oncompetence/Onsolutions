# -*- coding: utf-8 -*-
{
    "name": "Sale Integration Missing Products",
    "version": "19.0.1.0.0",
    "summary": "OnSolutions",
    "description": """
Este módulo migra la lógica de Odoo Studio a código nativo para la conciliación de 
productos faltantes provenientes de Tienda Nube y Mercado Libre.
Incluye optimización masiva de ORM (prevención de N+1) y vistas nativas.
    """,
    "category": "Sales",
    "author": "Gonzalo Fonseca",
    "depends": ["sale"],
    "data": [
        "security/ir.model.access.csv",
        "data/server_action.xml",
        "views/sale_order_views.xml",
    ],
    "installable": True,
    "license": "LGPL-3",
}