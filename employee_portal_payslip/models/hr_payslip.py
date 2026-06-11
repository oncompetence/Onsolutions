from odoo import models, fields, api
from datetime import datetime

class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    employee_signature = fields.Binary(string="Firma del Empleado", attachment=True)
    signed_date = fields.Datetime(string="Fecha de Firma")

    rrhh_signature = fields.Binary(
        string="Firma de RRHH",
        help="Firma digital del departamento de RRHH para el recibo de nómina.",
    )

    def action_register_payment(self):
        """Valida que si hay firma de RRHH, se permita el registro del pago."""
        for payslip in self:
            if not self.rrhh_signature:
                raise UserError(
                    "Debe registrar la firma de RRHH antes de proceder con el pago."
                )
        return super(HrPayslip, self).action_register_payment()

    def action_payslip_cancel(self):
        for payslip in self:
            if payslip.rrhh_signature:
                raise UserError("No se puede cancelar una nómina que ya fue firmada.")
        return super().action_payslip_cancel()

    def sign_payslip(self, signature_data):
        self.ensure_one()
        self.employee_signature = signature_data
        self.signed_date = fields.Datetime.now()

    def action_guardar_firma_y_redirigir(self):
        self.ensure_one()
        if self.employee_signature and not self.signed_date:
            self.signed_date = fields.Datetime.now()
        return {
            'type': 'ir.actions.act_url',
            'url': f'/my/payslips',
            'target': 'self',
        }