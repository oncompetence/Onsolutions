from odoo import models, fields, api, _


class PaymentCheck(models.Model):
    _name = "account.payment.check"
    _description = "Cheques de pago diferido"

    bank_code = fields.Char("Cód. del Bco. Central")
    number = fields.Char("Número")
    date = fields.Date("Fecha")
    payment_date = fields.Date("Fecha de pago")
    term_days = fields.Integer("Plazo (días)")

    amount = fields.Float("Importe")
    currency_rate = fields.Float("Cotización")

    endorsable = fields.Boolean("Endosable")
    direct = fields.Boolean("Directo")
    electronic = fields.Boolean("Electrónico")

    num_drawer_document_number = fields.Char("Número tipo de documento del librador")
    drawer_document_type = fields.Selection(
        [
            ("cuit", "CUIT"),
            ("cuil", "CUIL"),
            ("dni", "DNI"),
        ],
        string="Tipo de documento del librador",
    )
    drawer_document_number = fields.Char("Número documento")

    note = fields.Text("Observaciones")

    payment_id = fields.Many2one("account.payment", string="Pago relacionado")
