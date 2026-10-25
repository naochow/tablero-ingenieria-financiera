"""Gráficos Plotly con el estilo común del tablero.

Fondo blanco, cuadrícula suave, título y unidades en los ejes, hover con
valores en COP o porcentaje y separadores colombianos.
"""

import plotly.graph_objects as go

from componentes.estilos import BORDE, TEXTO, TEXTO_SECUNDARIO
from componentes.formato import SEPARADORES_PLOTLY

GRIS_CAPITAL = "#94A3B8"

_FORMATO_HOVER = {"COP": "$ %{y:,.0f}", "%": "%{y:.2%}"}


def _hover(nombre, unidad):
    return f"{nombre}: {_FORMATO_HOVER[unidad]}<extra></extra>"


def _aplicar_estilo(fig, titulo, eje_x, eje_y, unidad):
    fig.update_layout(
        title={"text": titulo, "x": 0, "font": {"size": 17, "color": TEXTO}},
        font={"family": "Source Sans 3, sans-serif", "color": TEXTO_SECUNDARIO},
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        separators=SEPARADORES_PLOTLY,
        hovermode="x unified",
        legend={"orientation": "h", "y": 1.02, "yanchor": "bottom", "x": 0},
        margin={"l": 10, "r": 10, "t": 70, "b": 10},
        bargap=0.3,
        barcornerradius=4,
    )
    fig.update_xaxes(title=eje_x, gridcolor=BORDE, zeroline=False, showline=True, linecolor=BORDE)
    fig.update_yaxes(
        title=f"{eje_y} ({unidad})",
        gridcolor=BORDE,
        zeroline=False,
        tickprefix="$ " if unidad == "COP" else "",
        tickformat=",.0f" if unidad == "COP" else ".1%",
    )
    return fig


def grafico_lineas(x, series, titulo, eje_x, eje_y, unidad="COP", etiquetas_finales=True):
    """Líneas para saldos y acumulados.

    series: lista de dicts con nombre, y, color y opcionalmente punteada=True.
    Con etiquetas_finales se rotula el último valor de cada serie.
    """
    fig = go.Figure()
    for serie in series:
        fig.add_trace(
            go.Scatter(
                x=x,
                y=serie["y"],
                name=serie["nombre"],
                mode="lines",
                line={"color": serie["color"], "width": 2, "dash": "dash" if serie.get("punteada") else "solid"},
                hovertemplate=_hover(serie["nombre"], unidad),
            )
        )
        if etiquetas_finales:
            fig.add_annotation(
                x=x[-1],
                y=serie["y"][-1],
                text=f"<b>{serie['nombre']}</b>",
                showarrow=False,
                xanchor="right",
                yanchor="bottom",
                font={"color": TEXTO, "size": 12},
            )
    return _aplicar_estilo(fig, titulo, eje_x, eje_y, unidad)


def grafico_barras(x, series, titulo, eje_x, eje_y, unidad="COP", apiladas=False):
    """Barras para flujos; apiladas=True para la composición (capital e intereses)."""
    fig = go.Figure()
    for serie in series:
        fig.add_trace(
            go.Bar(
                x=x,
                y=serie["y"],
                name=serie["nombre"],
                marker={"color": serie["color"], "line": {"color": "#FFFFFF", "width": 1}},
                hovertemplate=_hover(serie["nombre"], unidad),
            )
        )
    fig.update_layout(barmode="stack" if apiladas else "group")
    return _aplicar_estilo(fig, titulo, eje_x, eje_y, unidad)


CONFIG_PLOTLY = {"displaylogo": False}
