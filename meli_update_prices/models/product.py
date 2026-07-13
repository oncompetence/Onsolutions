from odoo import models, fields, api
import logging
import requests
import json
import base64
import hashlib
import hmac

_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def _update_cost_from_replenishment_cost(self, *args, **kwargs):
        _logger.warning("EJECUTANDO1")
        res = super()._update_cost_from_replenishment_cost(*args, **kwargs)
        _logger.warning("EJECUTANDO2")
        try:
            self._sync_price_to_meli()
        except Exception as e:
            _logger.error("Error al intentar disparar la sincronización a MeLi desde el costo de reposición: %s", str(e))
            
        return res

    def _sync_price_to_meli(self):
        company = self.env.company

        _logger.warning("COMPAÑIA: %s", company)

        meli_config = self.env["meli.app.key"].sudo().search([("company_id", "=", company.id)], limit=1)

        if not meli_config or not meli_config.user_id:
            _logger.warning("SE VA")
            return
        headers = {
            "Authorization": f"Bearer {meli_config.access_token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        for template in self:
            if not template.default_code:
                _logger.warning("SE VA 2")
                continue

            sku = template.default_code
            user_id = meli_config.user_id

            product = template.product_variant_id
            if not product:
                continue

            price = 0.0
            if meli_config.pricelist_id:
                price = meli_config.pricelist_id._get_product_price(
                    product,
                    quantity=1.0,
                )

            if price <= 0.0:
                continue

            search_url = f"https://api.mercadolibre.com/users/{user_id}/items/search?seller_sku={sku}"

            _logger.warning("search_url: %s",search_url)
            
            try:
                response = requests.get(search_url, headers=headers, timeout=10)
                _logger.warning("response: %s",response)
                response.raise_for_status()
                data = response.json()
                _logger.warning("data: %s",data)
                
                results = data.get("results", [])
                _logger.warning("results: %s",results)
                
                
                if not results:
                    continue
                    
                item_id = results[0]
                
                update_url = f"https://api.mercadolibre.com/items/{item_id}"
                payload = {"price": price}
                
                put_response = requests.put(update_url, headers=headers, json=payload, timeout=10)
                put_response.raise_for_status()
                
                _logger.warning("Precio sincronizado en MeLi exitosamente. Item: %s | SKU: %s | Nuevo Precio: %s", item_id, sku, price)

            except requests.exceptions.RequestException as e:
                _logger.error("Error de integración API con Mercado Libre para el SKU %s: %s", sku, str(e))
