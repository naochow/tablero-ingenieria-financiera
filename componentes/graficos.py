"""Gráficos Plotly con estilo Fintech Dark del tablero.

Fondo oscuro transparente, cuadrícula slate sutil, título blanco, hover unificado
y paleta de colores de alto contraste con separadores colombianos.
"""

import plotly.graph_objects as go

from componentes.formato import SEPARADORES_PLOTLY

GRIS_CAPITAL = "#64748B"

_FORMATO_HOVER = {"COP": "$ %{y:,.0f}", "%": "%{y:.2%}"}


def _hover(nombre, unidad):
    return f"{nombre}: {_FORMATO_HOVER[unidad]}<extra></extra>"


def _aplicar_estilo(fig, titulo, eje_x, eje_y, unidad):
    fig.update_layout(
        title={
            "text": f"<b>{titulo}</b>",
            "x": 0.01,
            "font": {"size": 16, "color": "#FFFFFF", "family": "Inter, sans-serif"},
        },
        font={"family": "Inter, sans-serif", "color": "#94A3B8"},
        paper_bgcolor="rgba(15, 23, 42, 0.4)",
        plot_bgcolor="rgba(15, 23, 42, 0.4)",
        separators=SEPARADORES_PLOTLY,
        hovermode="x unified",
        hoverlabel={
            "bgcolor": "#0F172A",
            "bordercolor": "#334155",
            "font": {"family": "JetBrains Mono, monospace", "color": "#F8FAFC", "size": 12},
        },
        legend={"orientation": "h", "y": 1.05, "yanchor": "bottom", "x": 0, "font": {"color": "#CBD5E1"}},
        margin={"l": 15, "r": 15, "t": 65, "b": 15},
        bargap=0.3,
        barcornerradius=6,
    )
    fig.update_xaxes(
        title=eje_x,
        gridcolor="rgba(51, 65, 85, 0.35)",
        zeroline=False,
        showline=True,
        linecolor="rgba(51, 65, 85, 0.6)",
        tickfont={"color": "#94A3B8", "size": 11},
        title_font={"color": "#CBD5E1", "size": 12},
    )
    fig.update_yaxes(
        title=f"{eje_y} ({unidad})",
        gridcolor="rgba(51, 65, 85, 0.35)",
        zeroline=False,
        showline=True,
        linecolor="rgba(51, 65, 85, 0.6)",
        tickprefix="$ " if unidad == "COP" else "",
        tickformat=",.0f" if unidad == "COP" else ".1%",
        tickfont={"color": "#94A3B8", "size": 11},
        title_font={"color": "#CBD5E1", "size": 12},
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
                line={"color": serie["color"], "width": 2.5, "dash": "dash" if serie.get("punteada") else "solid"},
                hovertemplate=_hover(serie["nombre"], unidad),
            )
        )
        if etiquetas_finales and len(x) > 0:
            fig.add_annotation(
                x=x[-1],
                y=serie["y"][-1],
                text=f"<b>{serie['nombre']}</b>",
                showarrow=False,
                xanchor="right",
                yanchor="bottom",
                font={"color": "#F8FAFC", "size": 11, "family": "Inter, sans-serif"},
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
                marker={"color": serie["color"], "line": {"color": "rgba(255, 255, 255, 0.15)", "width": 1}},
                hovertemplate=_hover(serie["nombre"], unidad),
            )
        )
    fig.update_layout(barmode="stack" if apiladas else "group")
    return _aplicar_estilo(fig, titulo, eje_x, eje_y, unidad)


def linea_referencia(fig, x, valor, nombre, color, unidad="COP"):
    """Línea horizontal punteada (ej. la cuota equivalente) que aparece en la leyenda y el hover."""
    fig.add_trace(
        go.Scatter(
            x=x,
            y=[valor] * len(x),
            name=nombre,
            mode="lines",
            line={"color": color, "width": 2, "dash": "dot"},
            hovertemplate=_hover(nombre, unidad),
        )
    )
    return fig
