from odoo import fields, models, api
from odoo.tools import float_compare

class ProductPricelist(models.Model):
    _inherit = "product.pricelist.item"

    show_replenishment_alert = fields.Boolean(
        compute='_compute_show_replenishment_alert'
    )

    def write(self, vals):
        """
        Interceptamos la escritura para auditar precios sin usar HTML.
        """
        # Solo monitoreamos campos de dinero
        tracked_fields = {
            'fixed_price': 'Precio Fijo',
            'percent_price': 'Porcentaje descuento',
            'standard_price': 'Costo',
        }

        for record in self:
            changes = []
            for field, label in tracked_fields.items():
                if field in vals:
                    old_val = record[field]
                    new_val = vals[field]
                    
                    if old_val != new_val:
                        # Usamos corchetes o flechas para resaltar el cambio individual
                        changes.append(f"[{label}: {old_val} -> {new_val}]")

            if changes:            
                separator = "  ||  "            
                header = "=== MODIFICACION DE PRECIO ==="
                details = separator.join(changes)
                footer = f"(Lista: {record.pricelist_id.name} / Producto: {record.product_tmpl_id.name})"
                
                # Armamos la línea larga con separadores claros
                msg_body = f"{header}{separator}{details}{separator}{footer}"
                
                # 1. Log en Lista
                record.pricelist_id.message_post(body=msg_body)

                # 2. Log en Template
                if record.product_tmpl_id:
                    record.product_tmpl_id.message_post(body=msg_body)
                
                # 3. Log en Variante
                if record.product_id:
                    record.product_id.message_post(body=msg_body)

        return super().write(vals)

    @api.model
    def create(self, vals):
        """
        Avisar creación.
        """
        record = super().create(vals)
        
        # Separador visual
        sep = "  ||  "
        
        # Construimos el string directamente
        msg_parts = [
            "+++ NUEVA REGLA DE PRECIO +++",
            f"Lista: {record.pricelist_id.name}",
            f"Precio: {record.fixed_price}",
            f"Desc: {record.percent_price}%"
        ]
        
        # Unimos con la doble barra
        msg_body = sep.join(msg_parts)
        
        if record.pricelist_id:
            record.pricelist_id.message_post(body=msg_body)
        
        if record.product_tmpl_id:
            record.product_tmpl_id.message_post(body=msg_body)
            
        return record
    
    @api.depends(
        'product_tmpl_id.replenishment_cost_type', 
        'product_tmpl_id.standard_price',    # Costo actual (Contable)
        'product_tmpl_id.replenishment_cost' # Costo objetivo (Reposición)
    )
    def _compute_show_replenishment_alert(self):
        for record in self:
            record.show_replenishment_alert = False
            
            # 1. Validaciones
            if not record.product_tmpl_id:
                continue
                
            # Verifica aquí el nombre técnico
            if record.product_tmpl_id.replenishment_cost_type not in ['supplier_price', 'last_supplier_price']:
                continue

            # 2. Obtenemos valores
            current_cost = record.product_tmpl_id.standard_price
            # Verifica que este sea el nombre real
            target_cost = record.product_tmpl_id.replenishment_cost 

            if float_compare(current_cost, target_cost, precision_digits=2) != 0:
                record.show_replenishment_alert = True

    def action_open_update_cost_wizard(self):
        """
        Abre el wizard forzando el contexto para que crea que está en el producto.
        """
        self.ensure_one()
        
        # LÓGICA DE TARGET:
        target_record = self.product_tmpl_id
        target_model = 'product.template'

        # Preparamos el contexto
        ctx = dict(self.env.context)
        ctx.update({
            'active_model': target_model,
            'active_id': target_record.id,
            'active_ids': [target_record.id],
            'default_product_id': target_record.id, 
        })

        return {
            'name': 'Actualizar Costo Contable',
            'type': 'ir.actions.act_window',
            'res_model': 'product.update_from_replenishment_cost.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': ctx,
        }
