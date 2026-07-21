# -*- coding: utf-8 -*-
import logging
from odoo import models, fields, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def action_update_prices_from_supplier(self):
        """Busca explícitamente la mejor tarifa del proveedor para cada línea 
        y fuerza la actualización del precio unitario, ignorando bloqueos nativos.
        """
        for order in self:
            if order.state not in ('draft', 'sent', 'purchase'):
                raise UserError(_(
                    "Solo podés actualizar precios en órdenes en estado "
                    "Borrador, Enviada o Confirmada. "
                    "La orden '%s' está en estado '%s'."
                ) % (order.name, order.state))

            for line in order.order_line:
                if not line.product_id:
                    continue

                precio_viejo = line.price_unit
                
                # 1. Usamos el motor nativo de Odoo para buscar la tarifa exacta
                # que aplique a este proveedor, cantidad y fecha.
                seller = line.product_id._select_seller(
                    partner_id=order.partner_id,
                    quantity=line.product_qty or 1.0,
                    date=order.date_order and order.date_order.date() or fields.Date.context_today(self),
                    uom_id=line.product_uom_id
                )
                
                # 2. Si encontramos la tarifa, forzamos el precio
                if seller:
                    nuevo_precio = seller.price
                    
                    # Soporte multi-moneda: Si la tarifa está en USD y la PO en ARS, convierte.
                    if seller.currency_id and order.currency_id and seller.currency_id != order.currency_id:
                        nuevo_precio = seller.currency_id._convert(
                            nuevo_precio, order.currency_id, order.company_id, order.date_order or fields.Date.context_today(self)
                        )
                    
                    line.price_unit = nuevo_precio
                    
                    _logger.info(
                        "PO %s - Producto %s: Tarifa encontrada! Precio forzado de %s a %s", 
                        order.name, line.product_id.display_name, precio_viejo, line.price_unit
                    )
                else:
                    _logger.warning(
                        "PO %s - Producto %s: No se encontró tarifa de proveedor aplicable.", 
                        order.name, line.product_id.display_name
                    )