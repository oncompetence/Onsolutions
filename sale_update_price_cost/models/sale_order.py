from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    is_outdated_price = fields.Boolean(
        string="Precio desactualizado",
        compute="_compute_is_outdated_price"
    )

    @api.depends('order_line.product_id', 'order_line.price_unit', 'pricelist_id', 'state')
    def _compute_is_outdated_price(self):
        # Acá itero sobre los registros (self) respetando las reglas de operaciones masivas del ORM
        for order in self:
            outdated = False
            # Solo me interesa evaluar presupuestos abiertos que tengan una tarifa asignada
            if order.state in ['draft', 'sent'] and order.pricelist_id:
                # Acá filtro las líneas válidas, ignorando secciones o notas
                lines = order.order_line.filtered(lambda l: not l.display_type and l.product_id)
                for line in lines:
                    # Acá consulto el precio que dicta la tarifa HOY para este producto
                    expected_price = order.pricelist_id._get_product_price(
                        product=line.product_id,
                        quantity=line.product_uom_qty or 1.0,
                        currency=order.currency_id,
                        date=order.date_order,
                    )
                    
                    # Acá utilizo el comparador de montos de la moneda nativa
                    # Esto previene falsos positivos por problemas de redondeo o decimales
                    if order.currency_id.compare_amounts(line.price_unit, expected_price) != 0:
                        outdated = True
                        break  # Rompo el bucle al encontrar la primera diferencia para no castigar el rendimiento
                        
            order.is_outdated_price = outdated

    def copy(self, default=None):
        # Acá delego la creación del clon exacto al método nativo del ORM.
        new_order = super(SaleOrder, self).copy(default=default)
        
        # Solo necesito confirmar que exista una tarifa asignada para operar.
        if new_order.pricelist_id:
            # Acá llamo al orquestador nativo para actualizar las líneas al costo/precio de hoy.
            new_order.action_update_prices()
            
        return new_order