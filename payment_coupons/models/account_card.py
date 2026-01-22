from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class AccountCard(models.Model):
    _inherit = "account.card"

    payment_days = fields.Integer(
        string="Días de pago",
        help="Número de días para el pago diferido con esta tarjeta.",
        default=0,
    )
    
    @api.constrains("payment_days")
    def _check_payment_days_non_negative(self):
        for record in self:
            if record.payment_days < 0:
                raise ValidationError(
                    _("Los días de pago no pueden ser negativos.")
                )