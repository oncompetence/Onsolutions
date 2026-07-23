/** @odoo-module **/
import { registry } from "@web/core/registry";
import { onMounted, onPatched, useRef, useState, useExternalListener } from "@odoo/owl";
import {
    SaleOrderLineOne2Many,
    saleOrderLineOne2Many,
} from "@sale/js/sale_order_line_field/sale_order_line_field";

const SECTION_TYPES = ["line_section", "line_subsection"];

export class SaleOrderLineOne2ManySearch extends SaleOrderLineOne2Many {
    setup() {
        super.setup();
        this.solO2mSearchRootRef = useRef("sol_o2m_search_root");
        this.orderState = useState({
            criterion: this.props.record.data.line_display_order || "manual",
        });

        // Mantenemos los delays para dejar que OWL termine su Virtual DOM
        onMounted(() => setTimeout(() => this.applyVisualOrder(), 0));
        onPatched(() => setTimeout(() => this.applyVisualOrder(), 0));

        useExternalListener(document, "visibilitychange", () => {
            if (!document.hidden) {
                setTimeout(() => this.applyVisualOrder(), 50);
            }
        });
    }

    onInputKeyUp(event) {
        const value = event.currentTarget.value.toLowerCase();
        const container = event.currentTarget.closest(".o_field_x2many");
        if (!container) return;

        const rows = container.querySelectorAll(".o_list_table tbody tr");
        rows.forEach((row) => {
            const text = row.textContent.toLowerCase();
            row.style.display = text.includes(value) ? "" : "none";
        });
    }

    async onOrderCriterionChange(event) {
        const criterion = event.target.value;
        this.orderState.criterion = criterion;
        
        await this.props.record.update({ line_display_order: criterion });
        await this.props.record.save();
        // Ya no hace falta llamar a applyVisualOrder aquí. Al hacer save(), 
        // Odoo repintará el componente y disparará nuestro onPatched automáticamente.
    }

    get orderLineRecords() {
        return this.props.record.data[this.props.name]?.records || [];
    }

    applyVisualOrder() {
        const criterion = this.orderState.criterion;
        if (!criterion || criterion === "manual") return;

        const rootEl = this.solO2mSearchRootRef.el;
        const container = rootEl && rootEl.closest(".o_field_x2many");
        if (!container) return;

        const rows = Array.from(
            container.querySelectorAll(".o_list_table > tbody > tr.o_data_row")
        );
        const records = this.orderLineRecords;

        if (!rows.length || rows.length !== records.length) return;

        // FIX CRÍTICO: Mapeamos los <tr> usando su data-id único asignado por Odoo.
        // Aquí construyo un diccionario de filas HTML indexadas por su ID local de OWL.
        const rowMap = new Map();
        for (const row of rows) {
            rowMap.set(row.dataset.id, row);
        }

        // Aquí armo la lista de "pares" (HTML + Dato) forzando que estén en el 
        // ORDEN EXACTO ORIGINAL de la base de datos, sin importar cómo estén movidos 
        // en la pantalla actualmente. Esto evita el "cruce de cables" y protege los combos.
        const originalOrderPairs = [];
        for (const record of records) {
            const row = rowMap.get(record.id);
            if (row) {
                originalOrderPairs.push({ row, record });
            }
        }

        if (originalOrderPairs.length !== records.length) return;

        // A partir de aquí, agrupamos de forma segura porque originalOrderPairs 
        // es la representación fiel de la base de datos.
        const groups = [];
        let currentGroup = null;

        for (const pair of originalOrderPairs) {
            const displayType = pair.record.data.display_type;
            if (SECTION_TYPES.includes(displayType)) {
                currentGroup = { header: pair, items: [] };
                groups.push(currentGroup);
            } else {
                if (!currentGroup) {
                    currentGroup = { header: null, items: [] };
                    groups.push(currentGroup);
                }
                currentGroup.items.push(pair);
            }
        }

        for (const group of groups) {
            group.units = this._buildUnits(group.items);
            group.units.sort((a, b) => this._compareUnits(a, b, criterion));
        }

        const tbody = rows[0].parentElement;
        let anchor = null;
        for (const group of groups) {
            if (group.header) {
                anchor = group.header.row;
            }
            for (const unit of group.units) {
                for (const pair of unit) {
                    if (anchor) {
                        anchor.after(pair.row);
                    } else {
                        tbody.insertBefore(pair.row, tbody.firstChild);
                    }
                    anchor = pair.row;
                }
            }
        }
    }

    _buildUnits(items) {
        const units = [];
        let i = 0;
        while (i < items.length) {
            const pair = items[i];
            const unit = [pair];
            
            if (pair.record.data.product_type === "combo") {
                let j = i + 1;
                while (j < items.length && items[j].record.data.combo_item_id) {
                    unit.push(items[j]);
                    j++;
                }
                i = j;
            } else {
                i++;
            }
            units.push(unit);
        }
        return units;
    }

    _compareUnits(a, b, criterion) {
        const headData = (unit) => unit[0].record.data;
        
        const nameOf = (val) => {
            if (!val) return "";
            if (Array.isArray(val)) return val[1] || "";
            return val.display_name || val.name || "";
        };

        if (criterion === "category") {
            const catCmp = nameOf(headData(a).categ_id).localeCompare(
                nameOf(headData(b).categ_id)
            );
            if (catCmp !== 0) return catCmp;
            
            return nameOf(headData(a).product_id).localeCompare(
                nameOf(headData(b).product_id)
            );
        }
        return nameOf(headData(a).product_id).localeCompare(
            nameOf(headData(b).product_id)
        );
    }
}

SaleOrderLineOne2ManySearch.template = "SolO2mSearchTemplate";

export const solO2mSearch = {
    ...saleOrderLineOne2Many,
    component: SaleOrderLineOne2ManySearch,
};

registry.category("fields").add("sol_o2m_search", solO2mSearch);