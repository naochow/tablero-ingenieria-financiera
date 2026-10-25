"""Paleta de colores del tablero, CSS global y piezas visuales con estilo propio.

Los contenedores se estilizan por su clave: Streamlit agrega la clase
st-key-<clave> a cada st.container(key=...), que es más estable que los
data-testid internos.
"""

from html import escape

import streamlit as st

# Colores generales (CONTEXTO, sección 7)
FONDO = "#F5F7FC"
TARJETA = "#FFFFFF"
BORDE = "#E3E8F2"
TEXTO = "#1F2937"
TEXTO_SECUNDARIO = "#566175"
BARRA_LATERAL = "#0F1E4D"
INTERESES = "#F59E0B"
INTERESES_TEXTO = "#B45309"
INTERESES_FONDO = "#FEF3C7"
CORRECTO = "#16A34A"
CORRECTO_FONDO = "#DCFCE7"
ERROR = "#DC2626"
ERROR_FONDO = "#FEE2E2"

# Color de cada tema: base (gráficos y etiquetas), oscuro (encabezado), suave (fondos)
TEMAS = {
    "principal": {"color": "#2563EB", "oscuro": "#1D4ED8", "suave": "#E8EFFE"},
    "interes_simple": {"color": "#0891B2", "oscuro": "#0E7490", "suave": "#E0F6FA"},
    "interes_compuesto": {"color": "#4F46E5", "oscuro": "#4338CA", "suave": "#ECEBFF"},
    "rentabilidad_tasas": {"color": "#7C3AED", "oscuro": "#6D28D9", "suave": "#F2ECFF"},
    "series_uniformes": {"color": "#EA580C", "oscuro": "#C2410C", "suave": "#FFF0E5"},
    "gradientes": {"color": "#DB2777", "oscuro": "#BE185D", "suave": "#FDEAF3"},
    "amortizacion": {"color": "#059669", "oscuro": "#047857", "suave": "#E2F7EE"},
    "supuestos": {"color": "#475569", "oscuro": "#334155", "suave": "#EEF1F5"},
}

# Paleta para KPIs y etiquetas de intereses (siempre ámbar)
_PALETA_INTERESES = {"color": INTERESES, "oscuro": INTERESES_TEXTO, "suave": INTERESES_FONDO}


def paleta(tema):
    """Colores de un tema; "intereses" devuelve la paleta ámbar."""
    if tema == "intereses":
        return _PALETA_INTERESES
    try:
        return TEMAS[tema]
    except KeyError:
        raise ValueError(f"Tema no definido: {tema}") from None


def _css_cuadritos(temas_por_ruta):
    """Cuadrito de color antes de cada enlace de la barra lateral, según su tema."""
    reglas = []
    for ruta, tema in temas_por_ruta.items():
        selector = f'[data-testid="stSidebarNav"] a[href$="/{ruta}"]::before'
        reglas.append(f"{selector} {{ background: {TEMAS[tema]['color']}; }}")
    return "\n".join(reglas)


def _css_encabezados():
    """Fondo del tono oscuro de cada tema para el contenedor encabezado_<tema>."""
    return "\n".join(
        f".st-key-encabezado_{tema} {{ background: {colores['oscuro']}; }}"
        for tema, colores in TEMAS.items()
    )


def aplicar_estilos(temas_por_ruta):
    """Inyecta el CSS global. temas_por_ruta asocia la url de cada página con su tema."""
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Source+Sans+3:wght@400;600;700&display=swap');

        html, body, [class*="css"], .stApp {{
            font-family: 'Source Sans 3', sans-serif;
            color: {TEXTO};
        }}
        .stApp {{ background: {FONDO}; }}

        /* Barra lateral azul oscuro con texto claro */
        [data-testid="stSidebar"] {{ background: {BARRA_LATERAL}; }}
        [data-testid="stSidebar"] * {{ color: #E5EAF7; }}
        [data-testid="stSidebarNav"] a:hover,
        [data-testid="stSidebarNav"] a[aria-current="page"] {{
            background: rgba(255, 255, 255, 0.10);
        }}
        [data-testid="stSidebarNav"] a::before {{
            content: "";
            width: 10px;
            height: 10px;
            border-radius: 3px;
            margin-right: 10px;
            flex-shrink: 0;
            background: {TEMAS['principal']['color']};
        }}
        {_css_cuadritos(temas_por_ruta)}

        /* Encabezado de color de cada página */
        [class*="st-key-encabezado_"] {{
            border-radius: 18px;
            padding: 1.4rem 1.6rem 1rem;
            margin-bottom: 0.6rem;
        }}
        [class*="st-key-encabezado_"] * {{ color: #FFFFFF; }}
        [class*="st-key-encabezado_"] h1 {{
            font-size: 2rem;
            font-weight: 700;
            padding: 0;
        }}
        [class*="st-key-encabezado_"] p {{ opacity: 0.9; }}
        {_css_encabezados()}

        /* Tarjetas blancas: st.container(key="tarjeta_...") */
        [class*="st-key-tarjeta_"] {{
            background: {TARJETA};
            border: 1px solid {BORDE};
            border-radius: 18px;
            padding: 1.1rem 1.3rem;
        }}

        /* Tarjeta KPI: ícono, valor grande y etiqueta pequeña */
        .kpi {{
            background: {TARJETA};
            border: 1px solid {BORDE};
            border-radius: 18px;
            padding: 1rem 1.2rem;
            height: 100%;
        }}
        .kpi-icono {{
            font-family: 'Material Symbols Rounded';
            font-size: 1.4rem;
            line-height: 1;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 2.2rem;
            height: 2.2rem;
            border-radius: 10px;
            color: var(--color);
            background: var(--suave);
        }}
        .kpi-valor {{
            font-size: 1.6rem;
            font-weight: 700;
            margin-top: 0.5rem;
            color: {TEXTO};
        }}
        .kpi-etiqueta {{ font-size: 0.85rem; color: {TEXTO_SECUNDARIO}; }}

        /* Etiqueta tipo chip con el color del tema */
        .etiqueta {{
            display: inline-block;
            padding: 0.1rem 0.6rem;
            border-radius: 999px;
            font-size: 0.8rem;
            font-weight: 600;
            color: var(--oscuro);
            background: var(--suave);
        }}

        /* Valores de intereses en ámbar */
        .intereses {{ color: {INTERESES_TEXTO}; font-weight: 600; }}

        /* Tarjeta de verificación (componentes/verificacion.py) */
        .verificacion {{
            border-radius: 14px;
            padding: 0.7rem 1rem;
            border: 1px solid;
        }}
        .verificacion-ok {{
            color: {CORRECTO};
            background: {CORRECTO_FONDO};
            border-color: {CORRECTO};
        }}
        .verificacion-error {{
            color: {ERROR};
            background: {ERROR_FONDO};
            border-color: {ERROR};
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def encabezado(tema, titulo, descripcion):
    """Encabezado de color con título, descripción y el toggle "Explícamelo".

    Devuelve True si el usuario activó "Explícamelo".
    """
    paleta(tema)  # valida el tema
    with st.container(key=f"encabezado_{tema}"):
        st.markdown(f"# {titulo}")
        st.markdown(descripcion)
        return st.toggle("Explícamelo", key=f"explicamelo_{tema}")


def tarjeta(clave):
    """Contenedor con estilo de tarjeta blanca; usar con `with tarjeta("..."):`."""
    return st.container(key=f"tarjeta_{clave}")


def tarjeta_kpi(icono, valor, etiqueta, tema="principal"):
    """Tarjeta KPI. icono es un nombre de Material Symbols (ej. "payments")."""
    colores = paleta(tema)
    st.markdown(
        f"""
        <div class="kpi" style="--color: {colores['color']}; --suave: {colores['suave']};">
            <span class="kpi-icono">{escape(icono)}</span>
            <div class="kpi-valor">{escape(valor)}</div>
            <div class="kpi-etiqueta">{escape(etiqueta)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def etiqueta(texto, tema="principal"):
    """HTML de una etiqueta tipo chip para usar dentro de st.markdown."""
    colores = paleta(tema)
    return (
        f'<span class="etiqueta" style="--oscuro: {colores["oscuro"]}; '
        f'--suave: {colores["suave"]};">{escape(texto)}</span>'
    )
