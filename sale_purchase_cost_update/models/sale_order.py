# -*- coding: utf-8 -*-
from odoo import models, _
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_update_costs_and_prices(self):
        """Actualizo los costos contables desde el costo de reposición
        y luego refresco los precios de venta en todas las líneas del pedido.
        """
        for order in self:
            # Valido que el documento esté en un estado editable
            # antes de tocar cualquier dato
            if order.state not in ('draft', 'sent'):
                raise UserError(_(
                    "Solo podés actualizar costos en órdenes en estado "
                    "Presupuesto o Presupuesto Enviado. "
                    "La orden '%s' está en estado '%s'."
                ) % (order.name, order.state))

            # Acá extraigo las plantillas de producto únicas en memoria
            # con mapped() para no hacer queries dentro del bucle
            product_tmpls = order.order_line.mapped('product_id.product_tmpl_id')

            # Elevo privilegios con sudo() para evitar restricciones de acceso
            # sobre el campo standard_price y delego en el método de ADHOC
            # la sincronización del costo contable con el costo de reposición
            product_tmpls.sudo()._update_cost_from_replenishment_cost()

            # Con los costos ya actualizados, refresco los precios de venta
            # usando el método estándar de Odoo sobre la cabecera del pedido
            order.action_update_prices()
