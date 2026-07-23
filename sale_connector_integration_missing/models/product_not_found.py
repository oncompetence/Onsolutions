# -*- coding: utf-8 -*-
from odoo import fields, models

class ProductNotFound(models.Model):
    _name = "product.not.found"
    _description = "Faltantes de Mercado Libre"

    # Aquí defino los campos exactos que me indicaste que existen en Studio
    order_id = fields.Many2one("sale.order", string="Orden de Venta", ondelete="cascade")
    sku = fields.Char(string="SKU")
    quantity = fields.Float(string="Cantidad")
    price = fields.Float(string="Precio")


class TnProductNotFound(models.Model):
    _name = "tn.product.not.found"
    _description = "Faltantes de Tienda Nube"

    order_id = fields.Many2one("sale.order", string="Orden de Venta", ondelete="cascade")
    sku = fields.Char(string="SKU")
    quantity = fields.Float(string="Cantidad")
    price = fields.Float(string="Precio")