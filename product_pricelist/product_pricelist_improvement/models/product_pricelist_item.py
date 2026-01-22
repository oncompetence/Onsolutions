from odoo import fields, models, api


class ProductPricelist(models.Model):
    _inherit = "product.pricelist.item"

    standard_price = fields.Float(
        string="Costo unitario",
        # related="product_id.standard_price",
        compute="_compute_standard_price",
        store=True,
        readonly=True,
    )
    # variant_display_name = fields.Char(
    #     related="product_id.display_name",
    #     string="Variante (Nombre Completo)",
    #     store=False,
    #     readonly=True,
    # )

    @api.depends(
        "applied_on",
        "product_id.standard_price",
        "product_tmpl_id.standard_price",
    )
    def _compute_standard_price(self):
        for item in self:
            price = 0.0      
            if item.applied_on == '0_product_variant' and item.product_id:
                price = item.product_id.standard_price            
            elif item.applied_on == '1_product' and item.product_tmpl_id:
                price = item.product_tmpl_id.standard_price
            item.standard_price = price

    def write(self, vals):
        """Registrar cambios de fixed_price"""
        self._process_price_changes(vals)
        return super().write(vals)

    def _process_price_changes(self, vals):
        """Detecta cambios y crea historial"""
        if "fixed_price" not in vals:
            return

        changed_items = self.filtered(
            lambda r: not fields.Float.is_zero(
                vals["fixed_price"] - getattr(r, "fixed_price"), precision_digits=2
            )
        )

        for item in changed_items:
            previous_price = item.fixed_price
            new_price = vals["fixed_price"]
            previous_cost = item.standard_price or 0.0
            new_cost = previous_cost
            item._create_history_record(
                # item.pricelist_id,
                # item,
                previous_cost,
                new_cost,
                previous_price,
                new_price,
                "manual",
            )

    def _create_history_record(
        self,
        previous_cost,
        new_cost,
        previous_price,
        new_price,
        origin,
    ):
        """Crea un registro en el historial de precios/costos"""
        product = self.product_id or self.product_tmpl_id.product_variant_ids[:1]
        if not product:
            return

        self.env["product.price.history"].create(
            {
                "product_id": product.id,
                "pricelist_id": self.pricelist_id.id,
                "previous_cost": float(previous_cost or 0.0),
                "current_cost": float(new_cost or 0.0),
                "previous_price": float(previous_price or 0.0),
                "current_price": float(new_price or 0.0),
                "user_id": self.env.user.id,
                "origin": origin,
            }
        )
    def action_create_new_pricelist(self):
        # aca redirijo al formulario de creacion de listas de precios
        view_id = self.env.ref('product_pricelist_improvement.view_product_pricelist_form_minimal_popup').id
        return {
            'name': 'Nueva Lista de Precios',
            'type': 'ir.actions.act_window',
            'res_model': 'product.pricelist',
            'view_mode': 'form',
            'view_id': view_id,
            'target': 'new',
            'context': {'default_currency_id': self.env.company.currency_id.id},
        }
