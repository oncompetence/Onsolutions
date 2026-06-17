from odoo import fields, models, api


class ProductPricelist(models.Model):
    _inherit = "product.pricelist"

    product_price_history_ids = fields.One2many(
        "product.price.history", "pricelist_id", string="Historial"
    )

    def action_update_cost(self):
        """Actualizar los costos en las líneas aplicables y registrar historial"""
        for pricelist in self:
            applicable_items = pricelist.item_ids.filtered(
                lambda i: i.applied_on in ("0_product_variant", "1_product")
            )

            for item in applicable_items:
                previous_cost = item.standard_price
                new_cost = 0.0
                previous_price = item.fixed_price 
                new_price = previous_price  # lo dejo con el mismo precio ya que al utilizar el boton no se cambia el precio

                if item.product_id:
                    new_cost = item.product_id.standard_price
                elif item.product_tmpl_id:
                    variant = item.product_tmpl_id.product_variant_ids[:1]
                    new_cost = variant.standard_price if variant else 0.0

                if not fields.Float.is_zero(
                    new_cost - previous_cost, precision_digits=2
                ):
                    item.standard_price = new_cost
                    item._create_history_record(
                        previous_cost,
                        new_cost,
                        previous_price,
                        new_price,
                        "manual",
                    )

    # def action_update_prices(self):
    #     """Actualizar los precios"""
    #     return True
