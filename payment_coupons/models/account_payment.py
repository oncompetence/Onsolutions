from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class AccountPayment(models.Model):
    _inherit = "account.payment"

    payment_coupon_ids = fields.One2many(
        "account.payment.coupon",
        "payment_id",
        string="Cupones de pago",
    )

    payment_check_ids = fields.One2many(
        "account.payment.check", "payment_id", string="Cheques de pago diferido"
    )

    is_bank_journal = fields.Boolean(
        string="Es diario bancario",
        compute="_compute_is_bank_journal",
        store=False,
    )

    @api.depends('journal_id')
    def _compute_is_bank_journal(self):
        for record in self:
            record.is_bank_journal = bool(record.journal_id) and record.journal_id.type == 'bank'

    @api.constrains("payment_coupon_ids", "journal_id")
    def _check_coupons_have_number(self):
        for rec in self:
            if rec.journal_id.type == "credit":
                missing = rec.payment_coupon_ids.filtered(lambda c: not c.coupon_number)
                if missing:
                    raise ValidationError(_("El número de cupón es obligatorio cuando el diario es Tarjeta de crédito."))
