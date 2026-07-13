import logging
import requests
from odoo import models, _

_logger = logging.getLogger(__name__)

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    def _update_cost_from_replenishment_cost(self, *args, **kwargs):
        res = super()._update_cost_from_replenishment_cost(*args, **kwargs)
        
        try:
            self._sync_price_to_tiendanube()
        except Exception as e:
            _logger.error("Error al disparar la sincronización a Tienda Nube: %s", str(e))
            
        return res

    def _sync_price_to_tiendanube(self):
        company = self.env.company

        tn_configs = self.env["tiendanube.api.config"].sudo().search([
            ("company_id", "=", company.id)
        ])

        if not tn_configs:
            _logger.warning(
                "[TN] No se encontraron configuraciones de Tienda Nube para la empresa %s",
                company.name,
            )
            return

        templates_with_sku = self.filtered(lambda t: t.default_code)

        if not templates_with_sku:
            _logger.warning("[TN] No hay productos con SKU para sincronizar.")
            return

        _logger.warning(
            "[TN] Comienza sincronización de %s productos utilizando %s conexiones.",
            len(templates_with_sku),
            len(tn_configs),
        )

        for tn_config in tn_configs:

            if not tn_config.store_id or not tn_config.access_token:
                _logger.warning(
                    "[TN] Configuración %s ignorada: falta Store ID o Access Token.",
                    tn_config.display_name,
                )
                continue

            _logger.warning(
                "[TN] Sincronizando contra tienda %s...",
                tn_config.store_id,
            )

            headers = {
                "Authentication": f"bearer {tn_config.access_token}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            }

            skus_to_find = set(templates_with_sku.mapped("default_code"))
            tn_sku_map = {}

            try:
                page = 1
                per_page = 200

                while skus_to_find:
                    _logger.info(
                        "[TN] Leyendo página %s de tienda %s. Restan %s SKUs.",
                        page,
                        tn_config.store_id,
                        len(skus_to_find),
                    )

                    url = (
                        f"https://api.tiendanube.com/v1/"
                        f"{tn_config.store_id}/products?page={page}&per_page={per_page}"
                    )

                    response = requests.get(url, headers=headers, timeout=20)
                    response.raise_for_status()

                    products = response.json()

                    if not products:
                        _logger.warning(
                            "[TN] Fin del catálogo de la tienda %s.",
                            tn_config.store_id,
                        )
                        break

                    for tn_product in products:
                        product_id = tn_product.get("id")

                        for variant in tn_product.get("variants", []):
                            sku = variant.get("sku")

                            if sku in skus_to_find:
                                tn_sku_map[sku] = (
                                    product_id,
                                    variant.get("id"),
                                )
                                skus_to_find.remove(sku)

                    page += 1

            except requests.exceptions.RequestException as e:
                _logger.error(
                    "[TN] Error leyendo catálogo de la tienda %s: %s",
                    tn_config.store_id,
                    e,
                )
                continue

            _logger.warning(
                "[TN] Encontrados %s productos para actualizar en tienda %s.",
                len(tn_sku_map),
                tn_config.store_id,
            )

            for template in templates_with_sku:

                sku = template.default_code

                if sku not in tn_sku_map:
                    _logger.info(
                        "[TN] SKU %s no existe en tienda %s.",
                        sku,
                        tn_config.store_id,
                    )
                    continue

                product = template.product_variant_id

                if not product:
                    _logger.warning(
                        "[TN] El producto %s no posee variante.",
                        template.display_name,
                    )
                    continue

                if not tn_config.pricelist_id:
                    _logger.warning(
                        "[TN] La configuración %s no posee lista de precios.",
                        tn_config.display_name,
                    )
                    continue

                price = tn_config.pricelist_id._get_product_price(
                    product,
                    quantity=1.0,
                )

                if price <= 0:
                    _logger.warning(
                        "[TN] Precio inválido (%s) para SKU %s.",
                        price,
                        sku,
                    )
                    continue

                tn_prod_id, tn_var_id = tn_sku_map[sku]

                payload = {
                    "price": str(price),
                }

                update_url = (
                    f"https://api.tiendanube.com/v1/"
                    f"{tn_config.store_id}/products/"
                    f"{tn_prod_id}/variants/{tn_var_id}"
                )

                try:
                    _logger.warning(
                        "[TN] Actualizando SKU %s -> %s",
                        sku,
                        price,
                    )

                    response = requests.put(
                        update_url,
                        headers=headers,
                        json=payload,
                        timeout=20,
                    )
                    response.raise_for_status()

                    _logger.info(
                        "[TN] OK - SKU %s actualizado en tienda %s.",
                        sku,
                        tn_config.store_id,
                    )

                except requests.exceptions.RequestException as e:
                    _logger.error(
                        "[TN] Error actualizando SKU %s en tienda %s: %s",
                        sku,
                        tn_config.store_id,
                        e,
                    )

        _logger.warning("[TN] Finalizó la sincronización.")