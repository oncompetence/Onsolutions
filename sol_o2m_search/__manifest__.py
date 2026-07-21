{
    "name": "Sale Order Line Search (sol_o2m)",
    "version": "19.0.1.0.0",
    "summary": "Agrega un buscador visual a las líneas de pedido de venta sin romper "
                "la lógica especializada de sol_o2m (combos, secciones y notas).",
    "description": """
Este módulo NO reemplaza el widget sol_o2m de sale.order.line.
Extiende SaleOrderLineOne2Many (definido en el core de sale) sumándole
un input de búsqueda en vivo sobre las filas ya renderizadas, sin tocar
ListRenderer, sin tocar el template de combos/secciones/notas y sin
sacar los botones "Agregar línea / sección / nota".

Reemplaza al módulo one2many_search_widget para el caso puntual de
order_line en sale.order: ese módulo reemplazaba el widget completo por
un X2ManyField genérico, perdiendo la lógica de sol_o2m (rompía al
agregar productos que disparan lógica de combo, por ejemplo).
    """,
    "category": "Sales",
    "author": "Uriel / OnCompetence",
    "depends": ["sale"],
    "assets": {
        "web.assets_backend": [
            "sol_o2m_search/static/src/fields/sol_o2m_search/*.js",
            "sol_o2m_search/static/src/fields/sol_o2m_search/*.xml",
            "sol_o2m_search/static/src/fields/sol_o2m_search/*.scss",
        ],
    },
    "installable": True,
    "auto_install": False,
    "license": "LGPL-3",
}
