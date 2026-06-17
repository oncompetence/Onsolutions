from odoo import models, fields, api

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    custom_pricelist_item_count = fields.Integer(
        string="Listas de precios",
        compute="_compute_custom_pricelist_item_count"
    )

    @api.depends('product_variant_ids')
    def _compute_custom_pricelist_item_count(self):
        PricelistItem = self.env['product.pricelist.item']
        for product in self:
            # Default value to avoid ValueError
            count = PricelistItem.search_count([
                '|',
                ('product_tmpl_id', '=', product.id),
                ('product_id', 'in', product.product_variant_ids.ids)
            ])
            product.custom_pricelist_item_count = count or 0

    def action_view_pricelist_items(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("product.product_pricelist_item_action")

        action['views'] = [(self.env.ref('product_pricelist_improvement.view_custom_pricelist_item_tree').id, 'tree')]
        action['domain'] = [
            '|',
            ('product_tmpl_id', '=', self.id),
            ('product_id', 'in', self.product_variant_ids.ids)
        ]
        action['context'] = dict(self.env.context, default_product_tmpl_id=self.id)
        return action

class ProductProduct(models.Model):
    _inherit = 'product.product'

    custom_pricelist_item_count = fields.Integer(
        string="Listas de precios", compute="_compute_variant_pricelist_item_count"
    )

    def _compute_variant_pricelist_item_count(self):
        PricelistItem = self.env["product.pricelist.item"]
        for variant in self:
            # count = PricelistItem.search_count([("product_id", "=", variant.id)])
            # variant.custom_pricelist_item_count = count or 0
            if variant.product_tmpl_id.product_variant_count == 1:
                variant.custom_pricelist_item_count = (
                    PricelistItem.search_count(
                        [
                            ("product_tmpl_id", "=", variant.product_tmpl_id.id),
                        ]
                    )
                    or 0
                )
            else:
                variant.custom_pricelist_item_count = (
                    PricelistItem.search_count([("product_id", "=", variant.id)]) or 0
                )

    def action_view_pricelist_items(self):
        self.ensure_one()
        if self.product_tmpl_id.product_variant_count == 1:
            return self.product_tmpl_id.action_view_pricelist_items()
        
        action = self.product_tmpl_id.action_view_pricelist_items()
        action['domain'] = [
            # '|',
            ('product_id', '=', self.id),
            # ('product_tmpl_id', '=', self.product_tmpl_id.id)
        ]

        return action
