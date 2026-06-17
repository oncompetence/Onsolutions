from odoo import fields, models, api


class ProductPriceHistory(models.Model):
    _name = 'product.price.history'
    _description = 'Historial de precios de productos'
    _rec_name = 'product_id'

    product_id = fields.Many2one("product.product", string="Producto", readonly=True)
    pricelist_id = fields.Many2one(
        "product.pricelist", string="Lista de precios", readonly=True
    )
    previous_price = fields.Float(string="Precio anterior", readonly=True)
    current_price = fields.Float(string="Precio nuevo", readonly=True)
    previous_cost = fields.Float(string="Costo anterior", readonly=True)
    current_cost = fields.Float(string="Costo nuevo", readonly=True)
    user_id = fields.Many2one(
        "res.users", string="Usuario", readonly=True, default=lambda self: self.env.user
    )
    update_date = fields.Datetime(
        string="Fecha de actualización", default=fields.Datetime.now
    )
    origin = fields.Selection(
        [("manual", "Manual"), ("import", "Importación"), ("rule", "Regla"), ("auto", "Automático")],
        string="Origen", readonly=True, default="manual"
    )
