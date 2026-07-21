# -*- coding: utf-8 -*-
from odoo import models, fields, _

class ProductSupplierinfo(models.Model):
    _inherit = 'product.supplierinfo'

    def action_push_price_to_purchase_orders(self):
        """Propago los precios de las tarifas seleccionadas buscando explícitamente 
        el seller para forzar la actualización de la PO sin bloqueos de caché.
        """
        orders_touched = self.env['purchase.order']

        for supplierinfo in self:
            lines = self.env['purchase.order.line'].search([
                ('order_id.partner_id', '=', supplierinfo.partner_id.id),
                ('product_id.product_tmpl_id', '=', supplierinfo.product_tmpl_id.id),
                ('order_id.state', 'in', ['draft', 'sent', 'purchase']),
            ])

            for line in lines:
                # Buscamos la tarifa directamente
                seller = line.product_id._select_seller(
                    partner_id=line.order_id.partner_id,
                    quantity=line.product_qty or 1.0,
                    date=line.order_id.date_order and line.order_id.date_order.date() or fields.Date.context_today(self),
                    uom_id=line.product_uom_id
                )
                
                if seller:
                    nuevo_precio = seller.price
                    if seller.currency_id and line.order_id.currency_id and seller.currency_id != line.order_id.currency_id:
                        nuevo_precio = seller.currency_id._convert(
                            nuevo_precio, line.order_id.currency_id, line.order_id.company_id, line.order_id.date_order or fields.Date.context_today(self)
                        )
                    
                    # Forzamos la inyección del precio a la línea
                    line.price_unit = nuevo_precio

            orders_touched |= lines.mapped('order_id')

        for order in orders_touched:
            order.message_post(body=_(
                "Los precios de las líneas han sido actualizados masivamente "
                "desde la tarifa del proveedor %s."
            ) % order.partner_id.name)