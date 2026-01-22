from odoo import fields, models, api

class SaleReportSQL(models.Model):
    _name = "sale.report.sql"
    _description = "Cuadro de mando comercial"
    _auto = False
    _rec_name = "order_name"

    order_name = fields.Char("N° Pedido de Venta")
    date_order = fields.Datetime("Fecha")
    product_id = fields.Many2one("product.product", "Producto")
    price_subtotal = fields.Float("SubTotal (Impuestos NO Incl.)")
    price_total = fields.Float("Total (Impuestos Incl.)")
    categ_id = fields.Many2one("product.category", "Categoría")
    product_uom_qty = fields.Float("Cantidad Vendida")
    partner_id = fields.Many2one("res.partner", "Cliente")
    user_id = fields.Many2one("res.users", "Vendedor")
    state_id = fields.Many2one("res.country.state", "Zona")
    opportunity_id = fields.Many2one("crm.lead", "Oportunidad")
    expected_revenue = fields.Float("Ingreso Esperado")
    sales_target = fields.Float("Objetivo de ventas", help="Objetivo de ventas mensuales del equipo de venta")
    list_price = fields.Float("Precio de venta")
    standard_price = fields.Float("Costo del producto", help="Costo del producto al momento de la venta")
    conversion_rate = fields.Float("Tasa de conversión (%)",compute="_compute_conversion_rate", help="Porcentaje de oportunidades convertidas en ventas", store=False)
    margin = fields.Float(
        string="Margen de venta",
        compute="_compute_margin",
        help="Diferencia entre precio de venta y costo total"
    )

    @api.depends("price_subtotal", "product_id", "product_uom_qty")
    def _compute_margin(self):
        for rec in self:
            costo_total = (rec.product_id.standard_price or 0.0) * (rec.product_uom_qty or 0.0)
            rec.margin = (rec.price_subtotal or 0.0) - costo_total

    @api.depends("opportunity_id")
    def _compute_conversion_rate(self):
        """
        Calcula la tasa de conversión:
        (Oportunidades con ventas confirmadas / Total de oportunidades con pedidos) * 100
        """
        for rec in self:
            if not rec.opportunity_id:
                rec.conversion_rate = 0.0
                continue
                
            sale_orders = self.env["sale.order"].search([("opportunity_id", "=", rec.opportunity_id.id)])
            total_orders = len(sale_orders)
            if not total_orders:
                rec.conversion_rate = 0.0
                continue

            converted_orders = len(sale_orders.filtered(lambda so: so.state in ("sale", "done")))
            rec.conversion_rate = (converted_orders / total_orders) if total_orders else 0.0

    def init(self):
        self.env.cr.execute("""
            DROP VIEW IF EXISTS sale_report_sql;
            CREATE VIEW sale_report_sql AS (
                SELECT
                    sol.id AS id,
                    so.name AS order_name,
                    so.date_order AS date_order,
                    sol.product_id AS product_id,
                    sol.price_total AS price_total,
                    sol.price_subtotal AS price_subtotal,
                    pt.categ_id AS categ_id,
                    sol.product_uom_qty AS product_uom_qty,
                    so.partner_id AS partner_id,
                    so.user_id AS user_id,
                    rp.state_id AS state_id,
                    so.opportunity_id AS opportunity_id,
                    cl.expected_revenue AS expected_revenue,
                    pt.list_price AS list_price,
                    pp.standard_price AS standard_price,
                    0.0 AS sales_target
                FROM sale_order_line sol
                JOIN sale_order so ON sol.order_id = so.id
                JOIN product_product pp ON sol.product_id = pp.id
                JOIN product_template pt ON pp.product_tmpl_id = pt.id
                JOIN res_partner rp ON so.partner_id = rp.id
                LEFT JOIN crm_lead cl ON so.opportunity_id = cl.id
                WHERE so.state IN ('sale', 'done')
            );
        """)

