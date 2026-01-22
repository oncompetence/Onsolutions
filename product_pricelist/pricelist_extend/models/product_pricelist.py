from odoo import models, fields, api, tools


class ProductPricelistItem(models.Model):
    _inherit = "product.pricelist.item"

    margen_1 = fields.Float(string="Margen adicional 1", help="First margin percentage")
    margen_2 = fields.Float(
        string="Margen adicional 2", help="Second margin percentage"
    )
    margen_3 = fields.Float(string="Margen adicional 3", help="Third margin percentage")
    margen_4 = fields.Float(
        string="Margen adicional 4", help="Fourth margin percentage"
    )

    def _compute_price(self, product, quantity, uom, date, currency=None):
        """Compute the unit price of a product in the context of a pricelist application.

        Note: self and self.ensure_one()

        :param product: recordset of product (product.product/product.template)
        :param float qty: quantity of products requested (in given uom)
        :param uom: unit of measure (uom.uom record)
        :param datetime date: date to use for price computation and currency conversions
        :param currency: currency (for the case where self is empty)

        :returns: price according to pricelist rule or the product price, expressed in the param
                  currency, the pricelist currency or the company currency
        :rtype: float
        """
        self and self.ensure_one()  # self is at most one record
        product.ensure_one()
        uom.ensure_one()

        currency = currency or self.currency_id or self.env.company.currency_id
        currency.ensure_one()

        # Pricelist specific values are specified according to product UoM
        # and must be multiplied according to the factor between uoms
        product_uom = product.uom_id
        if product_uom != uom:
            convert = lambda p: product_uom._compute_price(p, uom)
        else:
            convert = lambda p: p

        if self.compute_price == "fixed":
            price = convert(self.fixed_price)
        elif self.compute_price == "percentage":
            base_price = self._compute_base_price(
                product, quantity, uom, date, currency
            )
            price = (base_price - (base_price * (self.percent_price / 100))) or 0.0
        elif self.compute_price == "formula":
            base_price = self._compute_base_price(
                product, quantity, uom, date, currency
            )
            # complete formula
            price_limit = base_price
            discount = (
                self.price_discount
                if self.base != "standard_price"
                else -self.price_markup
            )
            price = base_price - (base_price * (discount / 100))
            if self.price_round:
                price = tools.float_round(price, precision_rounding=self.price_round)

            if self.price_surcharge:
                price += convert(self.price_surcharge)

            if self.price_min_margin:
                price = max(price, price_limit + convert(self.price_min_margin))

            if self.price_max_margin:
                price = min(price, price_limit + convert(self.price_max_margin))
        else:  # empty self, or extended pricelist price computation logic
            price = self._compute_base_price(product, quantity, uom, date, currency)

        # Apply additional margins
        if self.margen_1:
            price += price * (self.margen_1 / 100)
        if self.margen_2:
            price += price * (self.margen_2 / 100)
        if self.margen_3:
            price += price * (self.margen_3 / 100)
        if self.margen_4:
            price += price * (self.margen_4 / 100)

        return price
