"""Paleta de colores del tablero, CSS global y diseño fintech dark.

Inspirado en la interfaz moderna de alta ingeniería financiera:
Fondo Slate-950, paneles Glass/Slate-900, bordes con sutil transparencia,
tipografía Inter / JetBrains Mono y acentos de color neón por módulo.
"""

from html import escape

import streamlit as st

# Colores generales (Dark Fintech Slate)
FONDO = "#020617"             # slate-950
SUPERFICIE = "#0F172A"        # slate-900
TARJETA = "linear-gradient(135deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.8) 100%)"
BORDE = "rgba(51, 65, 85, 0.6)"  # border slate-700/60
TEXTO = "#F8FAFC"             # slate-50
TEXTO_SECUNDARIO = "#94A3B8"  # slate-400
TEXTO_MUTED = "#64748B"       # slate-500
BARRA_LATERAL = "#0F172A"     # slate-900

INTERESES = "#F59E0B"         # fintech amber
INTERESES_TEXTO = "#FBBF24"
INTERESES_FONDO = "rgba(245, 158, 11, 0.15)"

CORRECTO = "#10B981"          # fintech emerald
CORRECTO_FONDO = "rgba(16, 185, 129, 0.15)"

ERROR = "#F43F5E"             # fintech rose
ERROR_FONDO = "rgba(244, 63, 94, 0.15)"

# Color de cada tema según el módulo
TEMAS = {
    "principal": {"color": "#6366F1", "oscuro": "#4F46E5", "suave": "rgba(99, 102, 241, 0.16)"},
    "interes_simple": {"color": "#06B6D4", "oscuro": "#0891B2", "suave": "rgba(6, 182, 212, 0.16)"},
    "interes_compuesto": {"color": "#10B981", "oscuro": "#059669", "suave": "rgba(16, 185, 129, 0.16)"},
    "rentabilidad_tasas": {"color": "#F59E0B", "oscuro": "#D97706", "suave": "rgba(245, 158, 11, 0.16)"},
    "series_uniformes": {"color": "#8B5CF6", "oscuro": "#7C3AED", "suave": "rgba(139, 92, 246, 0.16)"},
    "gradientes": {"color": "#F43F5E", "oscuro": "#E11D48", "suave": "rgba(244, 63, 94, 0.16)"},
    "amortizacion": {"color": "#3B82F6", "oscuro": "#2563EB", "suave": "rgba(59, 130, 246, 0.16)"},
    "supuestos": {"color": "#A855F7", "oscuro": "#9333EA", "suave": "rgba(168, 85, 247, 0.16)"},
}

_PALETA_INTERESES = {"color": INTERESES, "oscuro": INTERESES_TEXTO, "suave": INTERESES_FONDO}


def paleta(tema):
    """Colores de un tema; 'intereses' devuelve la paleta ámbar."""
    if tema == "intereses":
        return _PALETA_INTERESES
    try:
        return TEMAS[tema]
    except KeyError:
        raise ValueError(f"Tema no definido: {tema}") from None


def _css_cuadritos(temas_por_ruta):
    """Acento de color antes de cada enlace de la barra lateral, según su tema."""
    reglas = []
    for ruta, tema in temas_por_ruta.items():
        selector = f'[data-testid="stSidebarNav"] a[href$="/{ruta}"]::before'
        color = TEMAS[tema]["color"]
        reglas.append(f"""
        {selector} {{
            content: "";
            width: 8px;
            height: 8px;
            border-radius: 9999px;
            margin-right: 12px;
            flex-shrink: 0;
            background: {color};
            box-shadow: 0 0 8px {color};
        }}
        """)
    return "\n".join(reglas)


def _css_encabezados():
    """Gradientes oscuros fintech para los encabezados de página."""
    reglas = []
    for tema, colores in TEMAS.items():
        reglas.append(f"""
        .st-key-encabezado_{tema} {{
            background: linear-gradient(135deg, rgba(15, 23, 42, 0.95) 0%, rgba(30, 41, 59, 0.85) 65%, {colores['suave']} 100%) !important;
            border: 1px solid rgba(51, 65, 85, 0.6) !important;
            border-left: 4px solid {colores['color']} !important;
        }}
        """)
    return "\n".join(reglas)


def aplicar_estilos(temas_por_ruta):
    """Inyecta el CSS global fintech dark en la aplicación."""
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap');
        @import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@24,400,0,0');
        @import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css');

        /* Scrollbars oscuros estilizados */
        ::-webkit-scrollbar {{ width: 6px; height: 6px; }}
        ::-webkit-scrollbar-track {{ background: #0F172A; }}
        ::-webkit-scrollbar-thumb {{ background: #334155; border-radius: 9999px; }}
        ::-webkit-scrollbar-thumb:hover {{ background: #475569; }}

        /* Estructura general de la app */
        html, body, .stApp {{
            font-family: 'Inter', sans-serif;
            background-color: {FONDO} !important;
            color: {TEXTO};
        }}

        h1, h2, h3, h4, h5, h6 {{
            font-family: 'Inter', sans-serif;
            font-weight: 700;
            letter-spacing: -0.025em;
            color: #FFFFFF;
        }}

        /* Barra lateral (Slate-900 / Border Slate-800) */
        [data-testid="stSidebar"] {{
            background-color: {BARRA_LATERAL} !important;
            border-right: 1px solid #1E293B !important;
        }}
        [data-testid="stSidebar"] * {{
            color: #CBD5E1;
        }}
        [data-testid="stSidebarNav"] a {{
            padding: 0.5rem 0.85rem !important;
            border-radius: 10px !important;
            transition: all 0.2s ease !important;
            margin-bottom: 2px !important;
            font-size: 0.88rem !important;
            color: #94A3B8 !important;
        }}
        [data-testid="stSidebarNav"] a:hover {{
            background: rgba(30, 41, 59, 0.7) !important;
            color: #FFFFFF !important;
        }}
        [data-testid="stSidebarNav"] a[aria-current="page"] {{
            background: rgba(99, 102, 241, 0.16) !important;
            color: #FFFFFF !important;
            border: 1px solid rgba(99, 102, 241, 0.35) !important;
            font-weight: 600 !important;
        }}
        {_css_cuadritos(temas_por_ruta)}

        /* Encabezado superior tipo Banner */
        [class*="st-key-encabezado_"] {{
            border-radius: 20px;
            padding: 1.5rem 1.8rem 1.2rem;
            margin-bottom: 1rem;
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.35);
        }}
        [class*="st-key-encabezado_"] * {{ color: #FFFFFF; }}
        [class*="st-key-encabezado_"] h1 {{
            font-size: 1.85rem;
            font-weight: 800;
            padding: 0;
            margin: 0.2rem 0;
        }}
        [class*="st-key-encabezado_"] p {{
            color: #CBD5E1;
            font-size: 0.92rem;
            margin-top: 0.3rem;
            line-height: 1.5;
        }}
        {_css_encabezados()}

        /* Tarjetas con efecto Glassmorphism (st.container(key="tarjeta_...")) */
        [class*="st-key-tarjeta_"], .glass-panel {{
            background: linear-gradient(135deg, rgba(30, 41, 59, 0.6) 0%, rgba(15, 23, 42, 0.8) 100%) !important;
            backdrop-filter: blur(12px) !important;
            border: 1px solid rgba(51, 65, 85, 0.6) !important;
            border-radius: 16px !important;
            padding: 1.2rem 1.4rem !important;
            box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.3) !important;
        }}

        /* Tarjeta KPI con gradiente y tipografía monospace */
        .kpi {{
            background: linear-gradient(135deg, rgba(30, 41, 59, 0.75) 0%, rgba(15, 23, 42, 0.85) 100%) !important;
            border: 1px solid rgba(51, 65, 85, 0.6) !important;
            border-radius: 14px !important;
            padding: 1rem 1.25rem !important;
            height: 100% !important;
            transition: all 0.2s ease-in-out !important;
        }}
        .kpi:hover {{
            border-color: var(--color) !important;
            box-shadow: 0 0 16px rgba(99, 102, 241, 0.25) !important;
            transform: translateY(-2px);
        }}
        .kpi-icono {{
            font-family: 'Material Symbols Rounded' !important;
            font-size: 1.3rem !important;
            line-height: 1 !important;
            display: inline-flex !important;
            align-items: center !important;
            justify-content: center !important;
            width: 2.2rem !important;
            height: 2.2rem !important;
            border-radius: 10px !important;
            color: var(--color) !important;
            background: var(--suave) !important;
            border: 1px solid var(--color) !important;
        }}
        .kpi-valor {{
            font-family: 'JetBrains Mono', monospace !important;
            font-size: 1.6rem !important;
            font-weight: 700 !important;
            margin-top: 0.45rem !important;
            color: #FFFFFF !important;
            letter-spacing: -0.02em !important;
        }}
        .kpi-etiqueta {{
            font-size: 0.75rem !important;
            color: {TEXTO_SECUNDARIO} !important;
            text-transform: uppercase !important;
            letter-spacing: 0.05em !important;
            font-weight: 600 !important;
        }}

        /* Etiqueta tipo chip de fintech */
        .etiqueta {{
            display: inline-block;
            padding: 0.2rem 0.65rem;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 600;
            color: var(--oscuro);
            background: var(--suave);
            border: 1px solid var(--oscuro);
        }}

        /* Valores de intereses en ámbar brillante */
        .intereses {{ color: {INTERESES_TEXTO}; font-weight: 600; }}

        /* Tarjetas de verificación ✓ / ✗ */
        .verificacion {{
            border-radius: 14px;
            padding: 0.85rem 1.15rem;
            border: 1px solid;
            font-size: 0.88rem;
            font-family: 'Inter', sans-serif;
            line-height: 1.45;
        }}
        .verificacion-ok {{
            color: #34D399;
            background: rgba(16, 185, 129, 0.12);
            border-color: rgba(16, 185, 129, 0.4);
        }}
        .verificacion-error {{
            color: #FB7185;
            background: rgba(244, 63, 94, 0.12);
            border-color: rgba(244, 63, 94, 0.4);
        }}

        /* Botones secundarios (Slate oscuro con borde y hover brillante) */
        .stButton > button,
        div[data-testid="stButton"] > button,
        button[data-testid="baseButton-secondary"] {{
            background-color: #0F172A !important;
            color: #F1F5F9 !important;
            border: 1px solid #334155 !important;
            border-radius: 10px !important;
            font-weight: 600 !important;
            padding: 0.55rem 1.15rem !important;
            font-size: 0.9rem !important;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.3) !important;
            transition: all 0.2s ease-in-out !important;
        }}
        .stButton > button:hover,
        div[data-testid="stButton"] > button:hover,
        button[data-testid="baseButton-secondary"]:hover {{
            background-color: #1E293B !important;
            color: #FFFFFF !important;
            border-color: #6366F1 !important;
            box-shadow: 0 0 14px rgba(99, 102, 241, 0.35) !important;
            transform: translateY(-1px);
        }}
        .stButton > button p,
        .stButton > button span,
        .stButton > button div,
        button[data-testid="baseButton-secondary"] p,
        button[data-testid="baseButton-secondary"] span,
        button[data-testid="baseButton-secondary"] div {{
            color: #F1F5F9 !important;
            font-weight: 600 !important;
        }}
        .stButton > button:hover p,
        .stButton > button:hover span,
        .stButton > button:hover div,
        button[data-testid="baseButton-secondary"]:hover p,
        button[data-testid="baseButton-secondary"]:hover span,
        button[data-testid="baseButton-secondary"]:hover div {{
            color: #FFFFFF !important;
        }}

        /* Botones primarios (Call to Action en degradado Índigo Fintech) */
        .stButton > button[kind="primary"],
        div[data-testid="stButton"] > button[kind="primary"],
        button[data-testid="baseButton-primary"] {{
            background: linear-gradient(135deg, #4F46E5 0%, #6366F1 100%) !important;
            color: #FFFFFF !important;
            border: none !important;
            border-radius: 10px !important;
            font-weight: 600 !important;
            box-shadow: 0 4px 14px rgba(99, 102, 241, 0.35) !important;
            transition: all 0.2s ease-in-out !important;
        }}
        .stButton > button[kind="primary"]:hover,
        div[data-testid="stButton"] > button[kind="primary"]:hover,
        button[data-testid="baseButton-primary"]:hover {{
            background: linear-gradient(135deg, #4338CA 0%, #4F46E5 100%) !important;
            box-shadow: 0 6px 18px rgba(99, 102, 241, 0.5) !important;
            transform: translateY(-1px);
        }}
        .stButton > button[kind="primary"] *,
        div[data-testid="stButton"] > button[kind="primary"] *,
        button[data-testid="baseButton-primary"] * {{
            color: #FFFFFF !important;
        }}

        /* Botón de descarga de archivos (CSV) en Esmeralda */
        [data-testid="stDownloadButton"] > button {{
            background-color: rgba(16, 185, 129, 0.15) !important;
            color: #34D399 !important;
            border: 1px solid rgba(16, 185, 129, 0.4) !important;
            border-radius: 10px !important;
            font-weight: 600 !important;
            transition: all 0.2s ease-in-out !important;
        }}
        [data-testid="stDownloadButton"] > button:hover {{
            background-color: rgba(16, 185, 129, 0.25) !important;
            color: #FFFFFF !important;
            border-color: #10B981 !important;
            box-shadow: 0 0 14px rgba(16, 185, 129, 0.35) !important;
            transform: translateY(-1px);
        }}
        [data-testid="stDownloadButton"] > button * {{
            color: #34D399 !important;
        }}
        [data-testid="stDownloadButton"] > button:hover * {{
            color: #FFFFFF !important;
        }}

        /* Inputs, selects y campos numéricos */
        div[data-baseweb="input"],
        div[data-baseweb="input"] > div,
        div[data-baseweb="select"] > div {{
            background-color: #0F172A !important;
            border: 1px solid #334155 !important;
            border-radius: 10px !important;
            color: #FFFFFF !important;
        }}
        div[data-baseweb="input"]:focus-within,
        div[data-baseweb="select"] > div:focus-within {{
            border-color: #6366F1 !important;
            box-shadow: 0 0 0 1px #6366F1 !important;
        }}
        div[data-baseweb="input"] input {{
            color: #FFFFFF !important;
            font-family: 'JetBrains Mono', monospace !important;
        }}
        label[data-testid="stWidgetLabel"] p {{
            color: #CBD5E1 !important;
            font-size: 0.85rem !important;
            font-weight: 600 !important;
        }}
        [data-testid="stCaptionContainer"] p {{
            color: #94A3B8 !important;
            font-size: 0.8rem !important;
        }}

        /* Tablas y dataframes en modo oscuro */
        [data-testid="stDataFrame"] {{
            border: 1px solid #334155 !important;
            border-radius: 12px !important;
            background: #0F172A !important;
        }}
        table {{
            border-collapse: separate !important;
            border-spacing: 0 !important;
            width: 100% !important;
            border-radius: 12px !important;
            overflow: hidden !important;
            border: 1px solid #334155 !important;
        }}
        th {{
            background-color: #0F172A !important;
            color: #94A3B8 !important;
            font-size: 0.75rem !important;
            text-transform: uppercase !important;
            letter-spacing: 0.05em !important;
            padding: 0.75rem 1rem !important;
            border-bottom: 1px solid #334155 !important;
            font-family: 'Inter', sans-serif !important;
        }}
        td {{
            background-color: #0B0F19 !important;
            color: #E2E8F0 !important;
            font-size: 0.82rem !important;
            padding: 0.7rem 1rem !important;
            border-bottom: 1px solid #1E293B !important;
            font-family: 'JetBrains Mono', monospace !important;
        }}
        tr:hover td {{
            background-color: #1E293B !important;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def encabezado(tema, titulo, descripcion):
    """Encabezado de color con título, descripción y el toggle 'Explícamelo'.

    Devuelve True si el usuario activó 'Explícamelo'.
    """
    colores = paleta(tema)
    with st.container(key=f"encabezado_{tema}"):
        col_txt, col_tog = st.columns([4, 1])
        with col_txt:
            st.markdown(
                f'<div style="font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.08em; '
                f'color: {colores["color"]}; font-weight: 700; margin-bottom: 0.2rem;">'
                f'<i class="fa-solid fa-graduation-cap"></i> UPB Finanzas • Ingeniería Financiera</div>',
                unsafe_allow_html=True,
            )
            st.markdown(f"# {titulo}")
            st.markdown(descripcion)
        with col_tog:
            st.write("")
            return st.toggle("💡 Explícamelo", key=f"explicamelo_{tema}")


def tarjeta(clave):
    """Contenedor con estilo de tarjeta glassmorphic; usar con `with tarjeta('...'):`."""
    return st.container(key=f"tarjeta_{clave}")


def tarjeta_kpi(icono, valor, etiqueta, tema="principal"):
    """Tarjeta KPI con estilo fintech. icono es un nombre de Material Symbols."""
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
    """HTML de una etiqueta tipo chip fintech para usar dentro de st.markdown."""
    colores = paleta(tema)
    return (
        f'<span class="etiqueta" style="--oscuro: {colores["color"]}; '
        f'--suave: {colores["suave"]};">{escape(texto)}</span>'
    )
