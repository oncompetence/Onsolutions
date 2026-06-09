import logging
from odoo import models, fields, api

_logger = logging.getLogger(__name__)

class ProductProduct(models.Model):
    _inherit = 'product.product'

    min_publication_qty = fields.Float(
        string='Stock mínimo de publicación',
        digits='Product Unit of Measure',
        default=0.0,
        help='Si el stock físico cae por debajo de este valor, se pausarán las publicaciones asociadas en MercadoLibre.'
    )

    def _check_mercadolibre_stock_and_pause(self):
        """
        Evalúa si el stock actual está por debajo del mínimo.
        Si es así, busca y pausa las publicaciones de MercadoLibre asociadas.
        """
        for product in self:
            if product.qty_available < product.min_publication_qty:
                _logger.info(
                    "Producto %s (SKU: %s) por debajo del mínimo de publicación. Stock: %s | Mínimo: %s",
                    product.display_name, product.default_code, product.qty_available, product.min_publication_qty
                )
                
                publications = self.env['meli.publication'].search([
                    ('product_id', '=', product.id),
                    ('state', '!=', 'paused')
                ])

                if publications:
                    _logger.info("Pausando %s publicaciones en MercadoLibre para el producto %s", len(publications), product.id)
                    publications.post_pause()