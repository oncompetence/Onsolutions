# Sale Purchase Cost Update

**Versión:** 19.0.1.0.0
**Autor:** Gonzalo Fonseca
**Licencia:** AGPL-3

## Descripción

Módulo custom para Odoo 19 que agrega un botón **"Actualizar Costos y Precios"**
en el header de las Órdenes de Venta y de Compra.

El botón permite, en un solo clic:

1. Sincronizar el **costo contable estándar** de los productos con su **costo de reposición**
   (delegando en el método `_update_cost_from_replenishment_cost()` del módulo de ADHOC).
2. Refrescar los **precios en las líneas** del documento para que reflejen los costos actualizados.

## Dependencias

- `sale_management`
- `purchase`
- `product_replenishment_cost` *(módulo de ADHOC)*

## Comportamiento

| Documento        | Método de refresco de precios                                      |
|------------------|--------------------------------------------------------------------|
| Orden de Venta   | `order.action_update_prices()`                                     |
| Orden de Compra  | `line._compute_price_unit_and_date_planned_and_name()` por línea   |

El botón es **visible únicamente** en estados `draft` y `sent`. Si se intenta
ejecutar la acción manualmente sobre un registro en otro estado, se lanza un
`UserError` descriptivo.

## Instalación

```bash
# Copiar el módulo al directorio de addons y actualizar la lista de módulos
odoo -u sale_purchase_cost_update -d <nombre_base_de_datos>
```
