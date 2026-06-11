from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = "product.template"

    # @api.model_create_multi
    # def create(self, vals_list):
    #     templates = super().create(vals_list)
    #     for template in templates:
    #         template.create_product_item_pricelist()
    #     return templates

    """def create_product_item_pricelist(self):
        base_list_usd = self.env.ref("pricelist_extend_currency.pricelist_usd")
        base_list = self.env["product.pricelist"].browse(16)
        usd_currency_rate = base_list_usd.currency_id._get_conversion_rate(
            base_list_usd.currency_id,
            base_list.currency_id,
            base_list.company_id,
            fields.Date.today(),
        )
        price = self.list_price / usd_currency_rate
        for template in self:
            values = {
                "pricelist_id": base_list.id,
                "product_tmpl_id": template.id,
                "fixed_price": template.list_price,
            }
            values_usd = {
                "pricelist_id": base_list_usd.id,
                "product_tmpl_id": template.id,
                "fixed_price": price,
            }

        base_list_usd.item_ids.create(values_usd)
        base_list.item_ids.create(values)"""

    def toggle_active(self):
        """
        Sobreescribimos el botón inteligente de Archivar.
        soltamos un 'Sticky' visual.
        """
        # 1. Ejecutamos la lógica nativa (Archivar/Desarchivar)
        super().toggle_active()

        # 2. Detectamos si la acción fue "Archivar"
        archived_products = self.filtered(lambda p: not p.active)

        if archived_products:
            # 3. Busamos si hay reglas de precio afectadas
            domain = [
                "|",
                ("product_tmpl_id", "in", archived_products.ids),
                (
                    "product_id",
                    "in",
                    archived_products.mapped("product_variant_ids").ids,
                ),
            ]

            # Usamos search_count que es más rápido
            items_count = self.env["product.pricelist.item"].search_count(domain)

            if items_count > 0:
                # 4. Retornamos la acción de notificación
                return {
                    "type": "ir.actions.client",
                    "tag": "display_notification",
                    "params": {
                        "title": "ADVERTENCIA DE PRECIOS",
                        "message": f"Has archivado productos que tienen {items_count} reglas de precio activas. Estas reglas dejarán de aplicarse.",
                        "type": "warning",
                        "sticky": True,
                    },
                }

    def unlink(self):
        """
        Al eliminar productos:
        1. Avisamos en el Chatter de las Listas de Precios afectadas.
        2. Dejamos que Odoo borre todo en cascada.
        """
        # Buscamos reglas antes de borrar
        domain = [
            "|",
            ("product_tmpl_id", "in", self.ids),
            ("product_id", "in", self.mapped("product_variant_ids").ids),
        ]
        items_to_vanish = self.env["product.pricelist.item"].search(domain)

        # Agrupamos por Lista de Precios
        pricelists_affected = items_to_vanish.mapped("pricelist_id")

        for pricelist in pricelists_affected:
            # Filtramos items de esta lista
            items_in_list = items_to_vanish.filtered(
                lambda i: i.pricelist_id == pricelist
            )

            # Nombres de productos
            product_names = [
                i.product_tmpl_id.name for i in items_in_list if i.product_tmpl_id
            ]
            names_str = ", ".join(set(product_names))

            # Mensaje
            msg = (
                f"=== ALERTA DE ELIMINACION === || "
                f"Se han eliminado productos: [{names_str}] || "
                f"Las reglas de precio asociadas han sido borradas automaticamente por el sistema."
            )

            pricelist.message_post(body=msg)

        return super().unlink()
