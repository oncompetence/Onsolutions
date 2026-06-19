from odoo import models, fields, api
from odoo.exceptions import ValidationError


class AccountMoveAnalyticLine(models.Model):
    _name = 'account.move.analytic.line'
    _description = 'Distribución Analítica por Cuenta en Factura'

    move_id = fields.Many2one(
        'account.move',
        string='Factura',
        required=True,
        ondelete='cascade'
    )
    analytic_id = fields.Many2one(
        'account.analytic.account',
        string='Cuenta Analítica',
        required=True,
        domain="[('company_id', '=', company_id)]"
    )
    percentage = fields.Float(
        string='Porcentaje',
        default=0.0
    )
    company_id = fields.Many2one(related='move_id.company_id', store=True)

    @api.constrains('percentage')
    def _check_percentage_range(self):
        for rec in self:
            if rec.percentage < 0 or rec.percentage > 100:
                raise ValidationError("El porcentaje debe estar entre 0 y 100.")