# -*- coding: utf-8 -*-
from odoo import fields, models, Command

class SaleOrder(models.Model):
    _inherit = "sale.order"

    # Aquí vinculo los campos One2many hacia nuestros nuevos modelos
    not_found_ids = fields.One2many("product.not.found", "order_id", string="Faltantes ML")
    tn_not_found = fields.One2many("tn.product.not.found", "order_id", string="Faltantes TN")

    def action_resolve_not_found_products(self):
        """
        Este método es el orquestador principal. Reemplaza al bucle N+1 de Studio.
        Recolecta los SKUs, realiza una única búsqueda y procesa las líneas en memoria.
        """
        for order in self:
            ml_lines = order.not_found_ids
            tn_lines = order.tn_not_found

            if not ml_lines and not tn_lines:
                continue

            # Paso 1: Recolectar todos los SKUs únicos para hacer una sola consulta
            all_skus = set()
            for line in ml_lines:
                if line.sku:
                    all_skus.add(line.sku)
            for line in tn_lines:
                if line.sku:
                    # Tienda Nube lo busca en mayúsculas según tu código original
                    all_skus.add(line.sku.upper())

            if not all_skus:
                continue

            # Paso 2: Búsqueda optimizada (una sola query al ORM)
            products = self.env["product.product"].sudo().search([("default_code", "in", list(all_skus))])
            
            # Aquí mapeo los productos en un diccionario para acceso inmediato O(1)
            product_map = {p.default_code: p for p in products if p.default_code}
            
            # Guardo los IDs de los productos que ya están en la orden para evitar duplicados
            existing_product_ids = set(order.order_line.mapped("product_id.id"))
            
            # Listas para procesar masivamente al final del bucle
            lines_to_create = []
            tn_to_unlink = self.env["tn.product.not.found"].browse()
            ml_to_unlink = self.env["product.not.found"].browse()

            # Paso 3: Procesar Tienda Nube
            for p in tn_lines:
                sku_upper = p.sku.upper() if p.sku else False
                if sku_upper and sku_upper in product_map:
                    prod = product_map[sku_upper]
                    if prod.id not in existing_product_ids:
                        # Aquí uso Command.create para preparar la inserción masiva
                        lines_to_create.append(Command.create({
                            "product_id": prod.id,
                            "name": prod.name,
                            "product_uom_qty": p.quantity,
                            "price_unit": p.price,
                        }))
                        existing_product_ids.add(prod.id)
                    tn_to_unlink |= p

            # Paso 4: Procesar Mercado Libre
            for p in ml_lines:
                sku = p.sku
                if sku and sku in product_map:
                    prod = product_map[sku]
                    if prod.id not in existing_product_ids:
                        lines_to_create.append(Command.create({
                            "product_id": prod.id,
                            "name": prod.name,
                            "product_uom_qty": p.quantity,
                            "price_unit": p.price,
                        }))
                        existing_product_ids.add(prod.id)
                    ml_to_unlink |= p

            # Paso 5: Ejecución masiva. Escribo todo en la base de datos de un solo golpe.
            if lines_to_create:
                order.write({"order_line": lines_to_create})
            if tn_to_unlink:
                tn_to_unlink.unlink()
            if ml_to_unlink:
                ml_to_unlink.unlink()