"""Punto de entrada del tablero: configuración, estilos y navegación."""

import streamlit as st

from componentes.estilos import aplicar_estilos

st.set_page_config(
    page_title="UPB Finanzas · Tablero de Ingeniería Financiera",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# (archivo, título, url, tema) de cada página, agrupadas por sección
SECCIONES = {
    "Inicio": [
        ("paginas/panel_principal.py", "Panel Principal", "panel-principal", "principal"),
    ],
    "Módulos del Curso": [
        ("paginas/interes_simple.py", "1. Interés Simple", "interes-simple", "interes_simple"),
        ("paginas/interes_compuesto.py", "2. Interés Compuesto", "interes-compuesto", "interes_compuesto"),
        ("paginas/rentabilidad_tasas.py", "3. Rentabilidad y Tasas", "rentabilidad-tasas", "rentabilidad_tasas"),
        ("paginas/series_uniformes.py", "4. Series Uniformes", "series-uniformes", "series_uniformes"),
        ("paginas/gradientes.py", "5. Gradientes", "gradientes", "gradientes"),
        ("paginas/amortizacion.py", "6. Tablas Amortización", "amortizacion", "amortizacion"),
    ],
    "Aplicación y Criterios": [
        ("paginas/casos_aplicados.py", "Casos Bancarios Reales", "casos-aplicados", "principal"),
        ("paginas/supuestos_formulas.py", "Supuestos & Fórmulas", "supuestos-formulas", "supuestos"),
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
    st.markdown(
        """
        <div style="padding: 0.4rem 0.2rem 1rem; border-bottom: 1px solid #1E293B; margin-bottom: 0.8rem; display: flex; align-items: center; gap: 0.75rem;">
          <div style="width: 2.6rem; height: 2.6rem; border-radius: 12px; background: linear-gradient(135deg, #4F46E5 0%, #06B6D4 100%); display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 14px rgba(99, 102, 241, 0.4);">
            <i class="fa-solid fa-chart-line" style="color: white; font-size: 1.15rem;"></i>
          </div>
          <div>
            <div style="font-size: 0.95rem; font-weight: 800; color: #FFFFFF; letter-spacing: -0.02em; display: flex; align-items: center; gap: 0.4rem;">
              UPB Finanzas <span style="font-size: 0.65rem; background: rgba(99, 102, 241, 0.25); color: #818CF8; padding: 0.15rem 0.45rem; border-radius: 4px; font-family: 'JetBrains Mono', monospace; font-weight: 600;">2026</span>
            </div>
            <div style="font-size: 0.75rem; color: #94A3B8;">Ingeniería Financiera</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

navegacion.run()

with st.sidebar:
    st.markdown(
        """
        <div style="padding-top: 1.2rem; border-top: 1px solid #1E293B; margin-top: 1.5rem; font-size: 0.75rem; color: #94A3B8;">
          <div style="margin-bottom: 0.35rem;">Docente: <strong style="color: #F1F5F9;">Adriana Arango L.</strong></div>
          <div style="margin-bottom: 0.45rem;">Equipo: <strong style="color: #E2E8F0;">Naomi Chow & Daniel Lopez</strong></div>
          <div style="display: flex; align-items: center; gap: 0.45rem; color: #34D399; font-size: 0.72rem; font-family: 'JetBrains Mono', monospace;">
            <span style="display: inline-block; width: 7px; height: 7px; border-radius: 50%; background-color: #10B981; box-shadow: 0 0 8px #10B981;"></span>
            <span>Motor Financiero Activo (v2.4)</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
