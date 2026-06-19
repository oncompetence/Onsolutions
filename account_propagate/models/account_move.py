from odoo import models, fields, api
from odoo.exceptions import ValidationError

class AccountMove(models.Model):
    _inherit = 'account.move'

    custom_tax_ids = fields.Many2many(
        'account.tax',
        'account_move_custom_tax_rel',
        'move_id', 'tax_id',
        string='Impuestos',
        domain="[('company_id', '=', company_id)]"
    )
    custom_analytic_line_ids = fields.One2many(
        'account.move.analytic.line',
        'move_id',
        string='Distribución Analítica'
    )

    @api.constrains('custom_analytic_line_ids')
    def _check_analytic_total(self):
        for move in self:
            total = sum(move.custom_analytic_line_ids.mapped('percentage'))
            if move.custom_analytic_line_ids and round(total, 2) != 100.0:
                raise ValidationError(
                    f"La distribución analítica debe sumar 100% (actual: {total}%)."
                )

    def _get_custom_analytic_distribution(self):
        """Helper: arma el dict {analytic_id: percentage} desde las líneas definidas por el usuario"""
        if not self.custom_analytic_line_ids:
            return False
        return {
            str(line.analytic_id.id): line.percentage
            for line in self.custom_analytic_line_ids
        }

    @api.onchange('custom_tax_ids', 'custom_analytic_line_ids')
    def _onchange_custom_m2m_fields_propagate(self):
        """Propaga los cambios a las líneas en la UI"""
        for move in self:
            analytic_dist = move._get_custom_analytic_distribution()

            for line in move.line_ids:
                if line.display_type not in ('product', 'ephemeral', 'cogs'):
                    continue

                if move.custom_tax_ids:
                    line.tax_ids = [fields.Command.set(move.custom_tax_ids.ids)]

                if analytic_dist:
                    line.analytic_distribution = analytic_dist
    
    @api.constrains('custom_analytic_line_ids')
    def _check_analytic_total(self):
        for move in self:
            total = sum(move.custom_analytic_line_ids.mapped('percentage'))
            if move.custom_analytic_line_ids and round(total, 2) != 100.0:
                raise ValidationError(
                    f"La distribución analítica debe sumar 100% (actual: {total}%)."
                )

    def write(self, vals):
        """Asegura la propagación en escrituras por backend/API"""
        res = super(AccountMove, self).write(vals)
        if 'custom_tax_ids' in vals or 'custom_analytic_line_ids' in vals:
            for move in self:
                line_vals = {}
                if 'custom_tax_ids' in vals:
                    line_vals['tax_ids'] = [fields.Command.set(move.custom_tax_ids.ids)]

                if 'custom_analytic_line_ids' in vals:
                    analytic_dist = move._get_custom_analytic_distribution()
                    if analytic_dist:
                        line_vals['analytic_distribution'] = analytic_dist

                if line_vals:
                    lines_to_update = move.line_ids.filtered(
                        lambda l: l.display_type in ('product', 'ephemeral', 'cogs')
                    )
                    lines_to_update.write(line_vals)
        return res

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    @api.model_create_multi
    def create(self, vals_list):
        lines = super().create(vals_list)
        for line in lines:
            if line.display_type not in ('product', 'ephemeral', 'cogs'):
                continue
            move = line.move_id
            if not move:
                continue

            update_vals = {}
            if move.custom_tax_ids:
                update_vals['tax_ids'] = [fields.Command.set(move.custom_tax_ids.ids)]

            analytic_dist = move._get_custom_analytic_distribution()
            if analytic_dist:
                update_vals['analytic_distribution'] = analytic_dist

            if update_vals:
                line.write(update_vals)
        return lines

    def write(self, vals):
        res = super().write(vals)
        if 'product_id' in vals:
            for line in self:
                if line.display_type not in ('product', 'ephemeral', 'cogs'):
                    continue
                move = line.move_id
                if not move:
                    continue
                update_vals = {}
                if move.custom_tax_ids:
                    update_vals['tax_ids'] = [fields.Command.set(move.custom_tax_ids.ids)]
                analytic_dist = move._get_custom_analytic_distribution()
                if analytic_dist:
                    update_vals['analytic_distribution'] = analytic_dist
                if update_vals:
                    super(AccountMoveLine, line).write(update_vals)
        return res