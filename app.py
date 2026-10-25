"""Punto de entrada del tablero: configuración, estilos y navegación."""

import streamlit as st

from componentes.estilos import aplicar_estilos

st.set_page_config(
    page_title="Tablero de Ingeniería Financiera",
    page_icon=":material/account_balance:",
    layout="wide",
    initial_sidebar_state="expanded",
)

# (archivo, título, url, tema) de cada página, agrupadas por sección
SECCIONES = {
    "Inicio": [
        ("paginas/panel_principal.py", "Panel principal", "panel-principal", "principal"),
    ],
    "Módulos": [
        ("paginas/interes_simple.py", "Interés simple", "interes-simple", "interes_simple"),
        ("paginas/interes_compuesto.py", "Interés compuesto", "interes-compuesto", "interes_compuesto"),
        ("paginas/rentabilidad_tasas.py", "Rentabilidad y tasas", "rentabilidad-tasas", "rentabilidad_tasas"),
        ("paginas/series_uniformes.py", "Series uniformes", "series-uniformes", "series_uniformes"),
        ("paginas/gradientes.py", "Gradientes", "gradientes", "gradientes"),
        ("paginas/amortizacion.py", "Amortización", "amortizacion", "amortizacion"),
    ],
    "Aplicación": [
        ("paginas/casos_aplicados.py", "Casos aplicados", "casos-aplicados", "principal"),
        ("paginas/supuestos_formulas.py", "Supuestos y fórmulas", "supuestos-formulas", "supuestos"),
    ],
}

paginas = {
    seccion: [
        st.Page(archivo, title=titulo, url_path=url, default=(url == "panel-principal"))
        for archivo, titulo, url, _ in lista
    ]
    for seccion, lista in SECCIONES.items()
}
temas_por_ruta = {url: tema for lista in SECCIONES.values() for _, _, url, tema in lista}

aplicar_estilos(temas_por_ruta)
navegacion = st.navigation(paginas)

with st.sidebar:
    st.caption("Ingeniería Financiera · UPB")
    st.caption("Naomi Chow Morelos y Daniel Lopez Lopez")

navegacion.run()
