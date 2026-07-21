/** @odoo-module **/
import { registry } from "@web/core/registry";
import {
    SaleOrderLineOne2Many,
    saleOrderLineOne2Many,
} from "@sale/js/sale_order_line_field/sale_order_line_field";

// A diferencia de one2many_search_widget (que extendía X2ManyField
// directo y así perdía toda la lógica de sol_o2m: combos, secciones,
// notas, columnas condicionales de account/product, etc.), acá
// heredamos SaleOrderLineOne2Many tal cual está definido en el core de
// "sale". Heredamos su ListRenderer (SaleOrderLineListRenderer) sin
// tocarlo: no reimplementamos nada de esa lógica, solo le sumamos el
// método de filtro de búsqueda.
export class SaleOrderLineOne2ManySearch extends SaleOrderLineOne2Many {
    // Mismo filtro robusto que ya estaba validado en one2many_search_widget:
    // se acota al contenedor .o_field_x2many más cercano al input, así
    // conviven varios widgets de este tipo en la misma vista (por ejemplo
    // un dialog abierto sobre el formulario) sin pisarse entre sí.
    onInputKeyUp(event) {
        const value = event.currentTarget.value.toLowerCase();

        const container = event.currentTarget.closest(".o_field_x2many");
        if (!container) {
            // Si no encuentro el contenedor (cambio futuro de estructura
            // de la vista), no rompo la función: no filtro y salgo.
            return;
        }

        const rows = container.querySelectorAll(".o_list_table tbody tr");

        // Igual que en el widget original: toggle de "display" sobre las
        // filas ya pintadas por SaleOrderLineListRenderer. No tocamos el
        // renderer ni su estado reactivo, así que toda la lógica de
        // combos/secciones/notas que ya pintó la fila se mantiene intacta;
        // solo la ocultamos u mostramos según coincida el texto.
        rows.forEach((row) => {
            const text = row.textContent.toLowerCase();
            row.style.display = text.includes(value) ? "" : "none";
        });
    }
}

// Reutilizamos el mismo nombre de template que usa sol_o2m sin pisarlo:
// "web.X2ManyField" (SaleOrderLineOne2Many -> ProductLabelSectionAndNoteOne2Many
// -> SectionAndNoteFieldOne2Many -> X2ManyField no redefinen .template en
// ningún nivel, así que el default sigue siendo ese). Nuestro template
// propio hereda ESE mismo template base y solo agrega el input, sin
// reemplazar los botones de control (Agregar línea/sección/nota).
SaleOrderLineOne2ManySearch.template = "SolO2mSearchTemplate";

// Partimos del descriptor real de sol_o2m (con su additionalClasses, etc.)
// y solo pisamos el componente. Así cualquier mejora futura que el core
// de "sale" le sume a saleOrderLineOne2Many la heredamos automáticamente.
export const solO2mSearch = {
    ...saleOrderLineOne2Many,
    component: SaleOrderLineOne2ManySearch,
};

// Se registra bajo una key NUEVA ("sol_o2m_search"), no pisa "sol_o2m".
// En la vista de Studio hay que poner widget="sol_o2m_search" en vez de
// "one2many_search" (y no hace falta comentar la línea: se reemplaza el
// nombre del widget).
registry.category("fields").add("sol_o2m_search", solO2mSearch);
