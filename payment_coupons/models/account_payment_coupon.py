from odoo import models, fields, api, _
from datetime import timedelta

class PaymentCoupon(models.Model):
    _name = "account.payment.coupon"
    _description = "Cupones de pago"
    _rec_name = "number_card"

    number_card = fields.Char("Número de tarjeta")
    expiration_date = fields.Date("Vencimiento")
    security_code = fields.Char("Código de seguridad")

    card_id = fields.Many2one(
        "account.card", 
        string="Tarjeta",
    )
    plan = fields.Many2one(
        "account.card.installment",
        string="Plan",
        domain="[('card_id', '=', card_id)]",
    )
    # card_id = fields.Char("Tarjeta")
    # plan = fields.Char("Plan")
    amount_coupon = fields.Float("Importe")
    quantity_coupon = fields.Float("Cantidad")
    exchange_rate = fields.Float("Cotización")

    partner_id = fields.Many2one("res.partner", "Cliente")
    type_document_id = fields.Many2one("l10n_latam.identification.type", related="partner_id.l10n_latam_identification_type_id", string="Tipo de documento")
    document = fields.Char("Documento", related="partner_id.vat")

    phone = fields.Char("Teléfono", related="partner_id.phone")
    coupon_number = fields.Char("Número de cupón")
    approval_code = fields.Char("Código de aprobación")
    date_coupon = fields.Date("Fecha")
    advance = fields.Float("Anticipo")
    first_due_date = fields.Date("Primer vto.")
    note = fields.Text("Observaciones")
    payment_id = fields.Many2one("account.payment", "Pago relacionado")
    currency_id = fields.Many2one("res.currency", "Moneda", default=lambda self: self.env.company.currency_id)

    @api.onchange("card_id")
    def _onchange_card_id_set_date_coupon(self):
        """Establece la fecha del cupón según los días de pago de la tarjeta seleccionada."""
        if self.card_id:
            days = self.card_id.payment_days or 0
            self.date_coupon = fields.Date.context_today(self) + timedelta(days=days)
        else:
            self.date_coupon = False
