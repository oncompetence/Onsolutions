from odoo import models

class StockMove(models.Model):
    _inherit = 'stock.move'

    def _action_done(self, cancel_backorder=False):
        """
        Cuando los movimientos de stock se marcan como hechos/realizados (done),
        evaluamos el stock restante de los productos implicados.
        """
        res = super(StockMove, self)._action_done(cancel_backorder=cancel_backorder)
        
        products_to_check = self.mapped('product_id')
        
        if products_to_check:
            products_to_check._check_mercadolibre_stock_and_pause()
            
        return res