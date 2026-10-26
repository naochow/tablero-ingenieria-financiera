"""Página de inicio (Landing Page): Resumen ejecutivo fintech, KPIs y módulos del curso."""

from pathlib import Path
import streamlit as st
import streamlit.components.v1 as components

from componentes import estilos
from componentes.formato import pesos, porcentaje

TEMA = "principal"
COLOR = estilos.TEMAS[TEMA]["color"]

# Top metadata bar
st.markdown(
    """
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.8rem; padding: 0.3rem 0.2rem;">
      <div style="display: flex; align-items: center; gap: 0.6rem;">
        <span style="font-size: 0.72rem; font-weight: 700; color: #818CF8; background: rgba(99, 102, 241, 0.15); border: 1px solid rgba(99, 102, 241, 0.3); padding: 0.2rem 0.65rem; border-radius: 9999px; text-transform: uppercase; letter-spacing: 0.05em;">
          Taller Final • 20%
        </span>
        <span style="font-size: 0.85rem; font-weight: 600; color: #E2E8F0;">Panel Principal de Síntesis</span>
      </div>
      <div style="display: flex; align-items: center; gap: 0.5rem; font-size: 0.75rem; color: #94A3B8; background: #0F172A; border: 1px solid #1E293B; padding: 0.25rem 0.75rem; border-radius: 9999px;">
        <i class="fa-solid fa-calendar-check" style="color: #6366F1;"></i>
        <span>Entrega: Octubre 29, 2026</span>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Hero Header tipo banner fintech
with st.container(key="encabezado_principal"):
    st.markdown(
        """
        <div style="max-width: 900px;">
          <div style="display: inline-flex; align-items: center; gap: 0.5rem; padding: 0.2rem 0.7rem; border-radius: 9999px; background: rgba(99, 102, 241, 0.15); border: 1px solid rgba(99, 102, 241, 0.3); color: #A5B4FC; font-size: 0.75rem; font-weight: 600; margin-bottom: 0.6rem;">
            <i class="fa-solid fa-graduation-cap"></i> Universidad Pontificia Bolivariana • Escuela de Ingenierías
          </div>
          <h1 style="font-size: 2.1rem; font-weight: 800; color: #FFFFFF; letter-spacing: -0.03em; margin: 0 0 0.4rem 0;">
            Tablero de Visualización de Ingeniería Financiera
          </h1>
          <p style="color: #CBD5E1; font-size: 0.95rem; line-height: 1.55; margin-bottom: 1rem;">
            Plataforma interactiva para la síntesis de conceptos matemáticos financieros: regímenes de interés,
            equivalencia de tasas, anualidades, gradientes y sistemas de amortización aplicados al mercado bancario colombiano.
          </p>
          <div style="display: flex; flex-wrap: wrap; gap: 1rem; font-size: 0.75rem; color: #94A3B8;">
            <span><i class="fa-solid fa-users" style="color: #64748B; margin-right: 0.3rem;"></i> Equipo: <strong style="color: #F1F5F9;">Naomi Chow & Daniel Lopez</strong></span>
            <span><i class="fa-solid fa-user-tie" style="color: #64748B; margin-right: 0.3rem;"></i> Docente: <strong style="color: #F1F5F9;">Adriana Arango L.</strong></span>
            <span><i class="fa-solid fa-calendar" style="color: #64748B; margin-right: 0.3rem;"></i> Vigencia: <strong style="color: #F1F5F9;">Semestre 2026-2</strong></span>
            <span><i class="fa-solid fa-calculator" style="color: #64748B; margin-right: 0.3rem;"></i> Base: <strong style="color: #F1F5F9;">360 Comercial / E.T. Art 395</strong></span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# 4 KPI Metrics Grid (igual que en el diseño de Tailwind)
k1, k2, k3, k4 = st.columns(4, gap="small")

with k1:
    st.markdown(
        """
        <div class="kpi" style="--color: #10B981; --suave: rgba(16, 185, 129, 0.15);">
          <div style="display: flex; justify-content: space-between; align-items: center; color: #94A3B8; font-size: 0.7rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em;">
            <span>CASO 1: CDT BANCOLOMBIA</span>
            <span class="kpi-icono" style="width: 1.8rem; height: 1.8rem; font-size: 1rem;"><i class="fa-solid fa-piggy-bank"></i></span>
          </div>
          <div class="kpi-valor" style="color: #FFFFFF; font-size: 1.6rem; margin-top: 0.3rem;">9.50% <span style="font-size: 0.75rem; color: #94A3B8; font-weight: normal;">E.A.</span></div>
          <div style="font-size: 0.75rem; color: #34D399; margin-top: 0.25rem; display: flex; align-items: center; gap: 0.3rem;">
            <i class="fa-solid fa-shield-halved"></i> TEA Neta: 9.12% post-retefuente
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with k2:
    st.markdown(
        """
        <div class="kpi" style="--color: #6366F1; --suave: rgba(99, 102, 241, 0.15);">
          <div style="display: flex; justify-content: space-between; align-items: center; color: #94A3B8; font-size: 0.7rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em;">
            <span>CASO 2: CRÉDITO SUFI</span>
            <span class="kpi-icono" style="width: 1.8rem; height: 1.8rem; font-size: 1rem;"><i class="fa-solid fa-car"></i></span>
          </div>
          <div class="kpi-valor" style="color: #FFFFFF; font-size: 1.6rem; margin-top: 0.3rem;">$40.000.000 <span style="font-size: 0.75rem; color: #94A3B8; font-weight: normal;">COP</span></div>
          <div style="font-size: 0.75rem; color: #818CF8; margin-top: 0.25rem; display: flex; align-items: center; gap: 0.3rem;">
            <i class="fa-solid fa-tag"></i> 1.25% M.V. (16.08% E.A.)
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with k3:
    st.markdown(
        """
        <div class="kpi" style="--color: #F59E0B; --suave: rgba(245, 158, 11, 0.15);">
          <div style="display: flex; justify-content: space-between; align-items: center; color: #94A3B8; font-size: 0.7rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em;">
            <span>CASO 3: AHORRO VIVIENDA</span>
            <span class="kpi-icono" style="width: 1.8rem; height: 1.8rem; font-size: 1rem;"><i class="fa-solid fa-building"></i></span>
          </div>
          <div class="kpi-valor" style="color: #FFFFFF; font-size: 1.6rem; margin-top: 0.3rem;">$37.284.190 <span style="font-size: 0.75rem; color: #94A3B8; font-weight: normal;">VF</span></div>
          <div style="font-size: 0.75rem; color: #FBBF24; margin-top: 0.25rem; display: flex; align-items: center; gap: 0.3rem;">
            <i class="fa-solid fa-arrow-trend-up"></i> Gradiente: +$25.000/mes
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with k4:
    st.markdown(
        """
        <div class="kpi" style="--color: #10B981; --suave: rgba(16, 185, 129, 0.15);">
          <div style="display: flex; justify-content: space-between; align-items: center; color: #94A3B8; font-size: 0.7rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em;">
            <span>VERIFICACIONES</span>
            <span class="kpi-icono" style="width: 1.8rem; height: 1.8rem; font-size: 1rem;"><i class="fa-solid fa-circle-check"></i></span>
          </div>
          <div class="kpi-valor" style="color: #34D399; font-size: 1.6rem; margin-top: 0.3rem;">7 / 7 OK</div>
          <div style="font-size: 0.75rem; color: #94A3B8; margin-top: 0.25rem; display: flex; align-items: center; gap: 0.3rem;">
            <i class="fa-solid fa-check-double" style="color: #10B981;"></i> Validado contra fórmulas
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# Pestañas principales de navegación
tab_resumen, tab_standalone = st.tabs(["📊 Vista Modular Streamlit", "⚡ Dashboard Ultra Fintech (HTML/JS en Vivo)"])

with tab_resumen:
    # ==============================================================================
    # SECCIÓN 1: RESUMEN EJECUTIVO DE CASOS FINANCIEROS APLICADOS
    # ==============================================================================
    with estilos.tarjeta("tabla_ejecutiva"):
        col_t1, col_t2 = st.columns([3, 1])
        with col_t1:
            st.markdown(
                """
                <h3 style="font-size: 1.15rem; font-weight: 800; color: #FFFFFF; display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.2rem;">
                  <i class="fa-solid fa-briefcase" style="color: #10B981;"></i>
                  Resumen Ejecutivo de Casos Financieros Aplicados
                </h3>
                <p style="font-size: 0.8rem; color: #94A3B8; margin: 0;">Síntesis comparativa de costos, rendimientos y decisión recomendada.</p>
                """,
                unsafe_allow_html=True,
            )
        with col_t2:
            if st.button("Ver Simuladores Detallados →", key="btn_ir_casos_top", use_container_width=True):
                st.switch_page("paginas/casos_aplicados.py")

        st.markdown(
            """
            <div style="overflow-x: auto; margin-top: 1rem;">
              <table style="width: 100%; text-align: left; border-collapse: separate; border-spacing: 0;">
                <thead>
                  <tr>
                    <th>Caso / Producto</th>
                    <th>Entidad Financiera</th>
                    <th>Tasa Efectiva Anual (E.A.)</th>
                    <th>Total Pagado / Recibido</th>
                    <th>Intereses Totales</th>
                    <th>Decisión Recomendada</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td style="font-family: 'Inter', sans-serif; font-weight: 600; color: #FFFFFF;">
                      Caso 1: CDT Tradicional vs Cajita de Ahorro
                    </td>
                    <td style="font-family: 'Inter', sans-serif;">Bancolombia vs Nu Colombia</td>
                    <td>
                      <span style="color: #34D399; font-weight: 600;">11.00% E.A. (Nu)</span> vs <span style="color: #94A3B8;">9.50% (Bancolombia)</span>
                    </td>
                    <td>$11.056.000 COP neto</td>
                    <td style="color: #34D399; font-weight: 600;">+$1.056.000 COP netos</td>
                    <td style="font-family: 'Inter', sans-serif;">
                      <span class="etiqueta" style="--oscuro: #10B981; --suave: rgba(16, 185, 129, 0.15); border-color: rgba(16, 185, 129, 0.4); color: #34D399;">
                        Nu Colombia (Mayor E.A. y Liquidez 24/7)
                      </span>
                    </td>
                  </tr>
                  <tr>
                    <td style="font-family: 'Inter', sans-serif; font-weight: 600; color: #FFFFFF;">
                      Caso 2: Crédito Vehicular ($40M a 48 meses)
                    </td>
                    <td style="font-family: 'Inter', sans-serif;">Sufi (Grupo Bancolombia)</td>
                    <td style="color: #818CF8; font-weight: 600;">16.08% E.A. (1.25% M.V.)</td>
                    <td>$53.486.208 (Francés) vs $52.250.000 (Alemán)</td>
                    <td style="color: #FB7185; font-weight: 600;">-$13.486.208 COP (Francés)</td>
                    <td style="font-family: 'Inter', sans-serif;">
                      <span class="etiqueta" style="--oscuro: #6366F1; --suave: rgba(99, 102, 241, 0.15); border-color: rgba(99, 102, 241, 0.4); color: #A5B4FC;">
                        Abono Constante (Ahorro $1.236.208 en intereses)
                      </span>
                    </td>
                  </tr>
                  <tr>
                    <td style="font-family: 'Inter', sans-serif; font-weight: 600; color: #FFFFFF;">
                      Caso 3: Plan Semilla Cuota Inicial Vivienda
                    </td>
                    <td style="font-family: 'Inter', sans-serif;">Fondo Fiduciario Bancolombia</td>
                    <td style="color: #FBBF24; font-weight: 600;">7.44% E.A. (0.60% M.V.)</td>
                    <td>$37.284.190 COP (Meta acumulada)</td>
                    <td style="color: #34D399; font-weight: 600;">+$3.584.190 COP rendimientos</td>
                    <td style="font-family: 'Inter', sans-serif;">
                      <span class="etiqueta" style="--oscuro: #F59E0B; --suave: rgba(245, 158, 11, 0.15); border-color: rgba(245, 158, 11, 0.4); color: #FBBF24;">
                        Gradiente Aritmético (Facilidad inicial $500k)
                      </span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # ==============================================================================
    # SECCIÓN 2: ACCESO RÁPIDO A MÓDULOS DEL CURSO (6 CARDS)
    # ==============================================================================
    st.markdown(
        """
        <div style="margin-top: 1.5rem; margin-bottom: 0.6rem;">
          <h3 style="font-size: 0.82rem; font-weight: 700; color: #94A3B8; text-transform: uppercase; letter-spacing: 0.08em; margin: 0;">
            Acceso Rápido a Módulos del Taller
          </h3>
        </div>
        """,
        unsafe_allow_html=True,
    )

    m_col1, m_col2, m_col3 = st.columns(3, gap="medium")

    with m_col1:
        with estilos.tarjeta("card_is"):
            st.markdown(
                """
                <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.6rem;">
                  <div style="width: 2.4rem; height: 2.4rem; border-radius: 10px; background: rgba(6, 182, 212, 0.15); color: #06B6D4; border: 1px solid rgba(6, 182, 212, 0.4); display: flex; align-items: center; justify-content: center; font-size: 1.1rem;">
                    <i class="fa-solid fa-arrow-trend-up"></i>
                  </div>
                  <div>
                    <h4 style="margin: 0; font-size: 0.95rem; color: #FFFFFF;">1. Interés Simple</h4>
                    <p style="margin: 0; font-size: 0.75rem; color: #94A3B8;">Régimen lineal de capitalización</p>
                  </div>
                </div>
                <p style="font-size: 0.8rem; color: #CBD5E1; min-height: 40px; margin-bottom: 0.8rem;">
                  Despejes exactos de $VP$, $VF$, tasa periódica $i$ y plazo $n$. Soporte para base Comercial (360) y Exacta (365).
                </p>
                """,
                unsafe_allow_html=True,
            )
            if st.button("Abrir Interés Simple", key="btn_nav_is", use_container_width=True):
                st.switch_page("paginas/interes_simple.py")

        st.write("")
        with estilos.tarjeta("card_series"):
            st.markdown(
                """
                <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.6rem;">
                  <div style="width: 2.4rem; height: 2.4rem; border-radius: 10px; background: rgba(139, 92, 246, 0.15); color: #8B5CF6; border: 1px solid rgba(139, 92, 246, 0.4); display: flex; align-items: center; justify-content: center; font-size: 1.1rem;">
                    <i class="fa-solid fa-bars-staggered"></i>
                  </div>
                  <div>
                    <h4 style="margin: 0; font-size: 0.95rem; color: #FFFFFF;">4. Series Uniformes</h4>
                    <p style="margin: 0; font-size: 0.75rem; color: #94A3B8;">Anualidades y cuotas constantes</p>
                  </div>
                </div>
                <p style="font-size: 0.8rem; color: #CBD5E1; min-height: 40px; margin-bottom: 0.8rem;">
                  Modelado de anualidades vencidas y anticipadas. Despejes cerrados de cuota ($A$), valor presente ($VP$) y valor futuro ($VF$).
                </p>
                """,
                unsafe_allow_html=True,
            )
            if st.button("Abrir Series Uniformes", key="btn_nav_series", use_container_width=True):
                st.switch_page("paginas/series_uniformes.py")

    with m_col2:
        with estilos.tarjeta("card_ic"):
            st.markdown(
                """
                <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.6rem;">
                  <div style="width: 2.4rem; height: 2.4rem; border-radius: 10px; background: rgba(16, 185, 129, 0.15); color: #10B981; border: 1px solid rgba(16, 185, 129, 0.4); display: flex; align-items: center; justify-content: center; font-size: 1.1rem;">
                    <i class="fa-solid fa-chart-area"></i>
                  </div>
                  <div>
                    <h4 style="margin: 0; font-size: 0.95rem; color: #FFFFFF;">2. Interés Compuesto</h4>
                    <p style="margin: 0; font-size: 0.75rem; color: #94A3B8;">Régimen exponencial continuo</p>
                  </div>
                </div>
                <p style="font-size: 0.8rem; color: #CBD5E1; min-height: 40px; margin-bottom: 0.8rem;">
                  Capitalización en cascada, brecha de valor frente a interés simple y despeje logarítmico de periodos $n$.
                </p>
                """,
                unsafe_allow_html=True,
            )
            if st.button("Abrir Interés Compuesto", key="btn_nav_ic", use_container_width=True):
                st.switch_page("paginas/interes_compuesto.py")

        st.write("")
        with estilos.tarjeta("card_grad"):
            st.markdown(
                """
                <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.6rem;">
                  <div style="width: 2.4rem; height: 2.4rem; border-radius: 10px; background: rgba(244, 63, 94, 0.15); color: #F43F5E; border: 1px solid rgba(244, 63, 94, 0.4); display: flex; align-items: center; justify-content: center; font-size: 1.1rem;">
                    <i class="fa-solid fa-stairs"></i>
                  </div>
                  <div>
                    <h4 style="margin: 0; font-size: 0.95rem; color: #FFFFFF;">5. Gradientes Financieros</h4>
                    <p style="margin: 0; font-size: 0.75rem; color: #94A3B8;">Flujos crecientes y decrecientes</p>
                  </div>
                </div>
                <p style="font-size: 0.8rem; color: #CBD5E1; min-height: 40px; margin-bottom: 0.8rem;">
                  Series aritméticas ($G$ en pesos) y geométricas ($g$ en porcentaje). Cálculo analítico de cuota fija equivalente.
                </p>
                """,
                unsafe_allow_html=True,
            )
            if st.button("Abrir Gradientes", key="btn_nav_grad", use_container_width=True):
                st.switch_page("paginas/gradientes.py")

    with m_col3:
        with estilos.tarjeta("card_tasas"):
            st.markdown(
                """
                <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.6rem;">
                  <div style="width: 2.4rem; height: 2.4rem; border-radius: 10px; background: rgba(245, 158, 11, 0.15); color: #F59E0B; border: 1px solid rgba(245, 158, 11, 0.4); display: flex; align-items: center; justify-content: center; font-size: 1.1rem;">
                    <i class="fa-solid fa-percent"></i>
                  </div>
                  <div>
                    <h4 style="margin: 0; font-size: 0.95rem; color: #FFFFFF;">3. Rentabilidad y Tasas</h4>
                    <p style="margin: 0; font-size: 0.75rem; color: #94A3B8;">Equivalencias y Retefuente</p>
                  </div>
                </div>
                <p style="font-size: 0.8rem; color: #CBD5E1; min-height: 40px; margin-bottom: 0.8rem;">
                  Conversor universal multidireccional (EA, NAMV, periodicidades), tasas combinadas (Fisher) y descuento del 4% tributario.
                </p>
                """,
                unsafe_allow_html=True,
            )
            if st.button("Abrir Rentabilidad y Tasas", key="btn_nav_tasas", use_container_width=True):
                st.switch_page("paginas/rentabilidad_tasas.py")

        st.write("")
        with estilos.tarjeta("card_amort"):
            st.markdown(
                """
                <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.6rem;">
                  <div style="width: 2.4rem; height: 2.4rem; border-radius: 10px; background: rgba(59, 130, 246, 0.15); color: #3B82F6; border: 1px solid rgba(59, 130, 246, 0.4); display: flex; align-items: center; justify-content: center; font-size: 1.1rem;">
                    <i class="fa-solid fa-table-list"></i>
                  </div>
                  <div>
                    <h4 style="margin: 0; font-size: 0.95rem; color: #FFFFFF;">6. Tablas de Amortización</h4>
                    <p style="margin: 0; font-size: 0.75rem; color: #94A3B8;">Sistemas Francés vs Alemán</p>
                  </div>
                </div>
                <p style="font-size: 0.8rem; color: #CBD5E1; min-height: 40px; margin-bottom: 0.8rem;">
                  Tablas completas con períodos de gracia, pagos extraordinarios periódicos y verificación matemática a saldo exacto cero.
                </p>
                """,
                unsafe_allow_html=True,
            )
            if st.button("Abrir Amortización", key="btn_nav_amort", use_container_width=True):
                st.switch_page("paginas/amortizacion.py")

with tab_standalone:
    st.info("💡 A continuación se despliega la interfaz gráfica interactiva del Dashboard Fintech completa con motor JavaScript y Chart.js en tiempo real:")
    html_path = Path(__file__).resolve().parent.parent / "datos" / "dashboard_fintech.html"
    if html_path.exists():
        contenido_html = html_path.read_text(encoding="utf-8")
        components.html(contenido_html, height=880, scrolling=True)
    else:
        st.warning("No se encontró el archivo del dashboard fintech en datos/dashboard_fintech.html")
