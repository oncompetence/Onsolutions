# -*- coding: utf-8 -*-
from odoo import fields, models

# Defino los tipos de línea que actúan como delimitador de grupo.
# El orden por criterio nunca mezcla líneas entre grupos ni genera secciones nuevas.
SECTION_TYPES = ("line_section", "line_subsection")


class SaleOrder(models.Model):
    _inherit = "sale.order"

    # Aquí defino el campo persistido para el frontend y el reporte
    line_display_order = fields.Selection(
        selection=[
            ("manual", "Manual"),
            ("alphabetical", "Alfabético"),
            ("category", "Categoría"),
        ],
        string="Orden de líneas",
        default="manual",
        help="Orden visual de las líneas del pedido (formulario y PDF). "
             "Respeta secciones y combos como bloques unidos.",
    )

    def _get_order_lines_to_report(self):
        """
        Aquí intercepto el método base que alimenta el reporte PDF. 
        Si el usuario eligió un orden, aplico la lógica de reordenamiento en memoria.
        """
        lines = super()._get_order_lines_to_report()
        
        if self.line_display_order == "manual" or not lines:
            return lines
            
        return self._sol_o2m_sort_lines_for_report(lines, self.line_display_order)

    def _sol_o2m_sort_lines_for_report(self, lines, criterion):
        """
        Aquí aplico el mismo algoritmo de agrupación y ordenamiento del JS, 
        pero delegando responsabilidades en funciones más pequeñas.
        """
        self.ensure_one()
        groups = self._sol_o2m_partition_into_groups(lines)

        ordered_ids = []
        for header, items in groups:
            if header:
                ordered_ids.append(header.id)
                
            units = self._sol_o2m_build_combo_units(items)
            # Ordeno utilizando la clave de ordenamiento específica
            units.sort(key=lambda unit: self._sol_o2m_unit_sort_key(unit[0], criterion))
            
            for unit in units:
                ordered_ids.extend(line.id for line in unit)

        # Aquí armo el recordset forzando el orden exacto de los IDs recolectados
        return self.env["sale.order.line"].browse(ordered_ids)

    def _sol_o2m_partition_into_groups(self, lines):
        """Aquí agrupo líneas respetando las secciones/subsecciones."""
        groups = []
        current_items = []
        current_header = None
        has_group = False
        
        for line in lines:
            if line.display_type in SECTION_TYPES:
                if has_group:
                    groups.append((current_header, current_items))
                current_header = line
                current_items = []
                has_group = True
            else:
                if not has_group:
                    has_group = True
                    current_header = None
                current_items.append(line)
                
        if has_group:
            groups.append((current_header, current_items))
            
        return groups

    def _sol_o2m_build_combo_units(self, items):
        """Aquí empaqueto combos y sus hijos en unidades indivisibles."""
        units = []
        items_list = list(items)
        i = 0
        n = len(items_list)
        
        while i < n:
            line = items_list[i]
            unit = [line]
            
            if line.product_type == "combo":
                j = i + 1
                while j < n and items_list[j].combo_item_id:
                    unit.append(items_list[j])
                    j += 1
                i = j
            else:
                i += 1
            units.append(unit)
            
        return units

    def _sol_o2m_unit_sort_key(self, head_line, criterion):
        """Aquí defino la tupla clave para el ordenamiento de Python."""
        name = (head_line.product_id.name or "").lower()
        if criterion == "category":
            categ = (head_line.categ_id.name or "").lower()
            return (categ, name)
            
        return (name,)