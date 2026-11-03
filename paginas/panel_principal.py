"""Página de inicio (Landing Page): Resumen ejecutivo fintech, KPIs y módulos del curso."""

from html import escape
import streamlit as st

from componentes import decisiones, estilos
from componentes.datos_casos import cargar_casos_o_detener
from componentes.formato import pesos, porcentaje, porcentaje_compacto
from componentes.verificaciones_tablero import verificaciones_tablero
from finanzas import amortizacion, tasas

TEMA = "principal"
COLOR = estilos.TEMAS[TEMA]["color"]


def _p_html(v, d=0):
    """Formato en pesos escapando el signo de dólar como entidad HTML para evitar conflictos con KaTeX."""
    return pesos(v, d).replace("$", "&#36;")


casos = cargar_casos_o_detener()

# Cálculos dinámicos con motor financiero UPB
# Caso 1: Crédito de Vehículo (oferta de menor costo efectivo)
c1 = casos[0]["parametros"]
c1_monto = c1["monto"]
c1_plazo = c1["plazo_meses"]
c1_barata, c1_cara = sorted(
    ({"entidad": o["entidad"], "ea": tasas.ea_desde_codigo(o["tasa_valor"], o["codigo_tasa"])} for o in c1["ofertas"]),
    key=lambda o: o["ea"],
)
c1_mv = tasas.periodica_desde_ea(c1_barata["ea"], 12)

tabla_c1_frances = amortizacion.tabla_amortizacion(c1_monto, c1_mv, c1_plazo, sistema="frances")
c1_int_frances = sum(r["intereses"] for r in tabla_c1_frances)
c1_total_frances = sum(r["pago_total"] for r in tabla_c1_frances)

tabla_c1_aleman = amortizacion.tabla_amortizacion(c1_monto, c1_mv, c1_plazo, sistema="aleman")
c1_int_aleman = sum(r["intereses"] for r in tabla_c1_aleman)
c1_total_aleman = sum(r["pago_total"] for r in tabla_c1_aleman)
c1_ahorro_aleman = c1_int_frances - c1_int_aleman

# Caso 2: CDT vs Nu (Inversión)
c2 = casos[1]["parametros"]
c2_capital = c2["capital"]
c2_plazo_dias = c2["plazo_dias"]
c2_tasa_cdt_ea = c2["tasa_cdt_ea"]
c2_tasa_nu_ea = c2["tasa_cuenta_ea"]
c2_ret_cdt = c2["retencion_cdt"]
c2_ret_nu = c2["retencion_cuenta"]
t2_base = c2_plazo_dias / 360.0

rend_cdt_bruto = c2_capital * ((1 + c2_tasa_cdt_ea) ** t2_base - 1)
rend_cdt_neto = rend_cdt_bruto * (1 - c2_ret_cdt)
tea_neta_cdt = (1 + rend_cdt_neto / c2_capital) ** (1 / t2_base) - 1

rend_nu_bruto = c2_capital * ((1 + c2_tasa_nu_ea) ** t2_base - 1)
rend_nu_neto = rend_nu_bruto * (1 - c2_ret_nu)

# La alternativa recomendada es la de mayor rendimiento neto
c2_cdt = {"nombre": "CDT Bancolombia", "corto": "Bancolombia", "decision": "CDT", "ea": c2_tasa_cdt_ea, "rend": rend_cdt_neto, "liquidez": "sin liquidez hasta el vencimiento"}
c2_nu = {"nombre": "Nu Colombia", "corto": "Nu", "decision": "Nu", "ea": c2_tasa_nu_ea, "rend": rend_nu_neto, "liquidez": "liquidez 24/7"}
c2_gana, c2_pierde = (c2_nu, c2_cdt) if decisiones.gana_cuenta(rend_nu_neto, rend_cdt_neto) else (c2_cdt, c2_nu)
c2_total_gana = c2_capital + c2_gana["rend"]
c2_dif = c2_gana["rend"] - c2_pierde["rend"]

# Caso 3: Fiducuenta Cuota Inicial (Gradientes)
c3 = casos[2]["parametros"]
c3_a1 = c3["a1"]
c3_G = c3["gradiente_aritmetico_G"]
c3_g = c3["gradiente_geometrico_g"]
c3_plazo = c3["plazo_meses"]
c3_meta = c3["meta_ahorro"]
c3_tasa_ea = c3["tasa_ea"]
c3_tasa_mv = tasas.periodica_desde_ea(c3_tasa_ea, 12)

# La recomendación compara los dos planes con la meta de ahorro
c3_plan, _ = decisiones.plan_recomendado(decisiones.comparar_planes(c3_a1, c3_G, c3_g, c3_tasa_mv, c3_plazo, c3_meta))
vf_c3 = c3_plan["vf"]
rend_c3 = vf_c3 - c3_plan["aportes"]
c3_incremento = f"+{_p_html(c3_G)}/mes" if c3_plan["clave"] == "aritmetico" else f"+{porcentaje(c3_g)}/mes"
c3_frente_meta = (
    f"Supera la meta de {_p_html(c3_meta)} por {_p_html(c3_plan['diferencia_meta'])}"
    if c3_plan["alcanza"]
    else f"Queda {_p_html(-c3_plan['diferencia_meta'])} por debajo de la meta de {_p_html(c3_meta)}"
)

# Verificaciones reales: cada módulo y caso contra una ruta de cálculo independiente
verificaciones = verificaciones_tablero(casos)
fallas = [v["nombre"] for v in verificaciones if not v["ok"]]
total_ok = len(verificaciones) - len(fallas)
total_verificaciones = len(verificaciones)

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

# 4 KPI Metrics Grid (Calculados dinámicamente)
k1, k2, k3, k4 = st.columns(4, gap="small")

with k1:
    st.markdown(
        f"""
        <div class="kpi" style="--color: #6366F1; --suave: rgba(99, 102, 241, 0.15);">
          <div style="display: flex; justify-content: space-between; align-items: center; color: #94A3B8; font-size: 0.7rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em;">
            <span>CASO 1: CRÉDITO {c1_barata['entidad'].upper()}</span>
            <span class="kpi-icono" style="width: 1.8rem; height: 1.8rem; font-size: 1rem;"><i class="fa-solid fa-car"></i></span>
          </div>
          <div class="kpi-valor" style="color: #FFFFFF; font-size: 1.45rem; margin-top: 0.3rem;">{_p_html(c1_monto)} <span style="font-size: 0.75rem; color: #94A3B8; font-weight: normal;">COP</span></div>
          <div style="font-size: 0.75rem; color: #818CF8; margin-top: 0.25rem; display: flex; align-items: center; gap: 0.3rem;">
            <i class="fa-solid fa-tag"></i> {porcentaje(c1_mv, 2)} M.V. ({porcentaje(c1_barata['ea'], 2)} E.A.)
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with k2:
    st.markdown(
        f"""
        <div class="kpi" style="--color: #10B981; --suave: rgba(16, 185, 129, 0.15);">
          <div style="display: flex; justify-content: space-between; align-items: center; color: #94A3B8; font-size: 0.7rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em;">
            <span>CASO 2: CDT BANCOLOMBIA</span>
            <span class="kpi-icono" style="width: 1.8rem; height: 1.8rem; font-size: 1rem;"><i class="fa-solid fa-piggy-bank"></i></span>
          </div>
          <div class="kpi-valor" style="color: #FFFFFF; font-size: 1.45rem; margin-top: 0.3rem;">{porcentaje(c2_tasa_cdt_ea, 2)} <span style="font-size: 0.75rem; color: #94A3B8; font-weight: normal;">E.A.</span></div>
          <div style="font-size: 0.75rem; color: #34D399; margin-top: 0.25rem; display: flex; align-items: center; gap: 0.3rem;">
            <i class="fa-solid fa-shield-halved"></i> TEA Neta: {porcentaje(tea_neta_cdt, 2)} (Ret. {porcentaje_compacto(c2_ret_cdt)})
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with k3:
    st.markdown(
        f"""
        <div class="kpi" style="--color: #F59E0B; --suave: rgba(245, 158, 11, 0.15);">
          <div style="display: flex; justify-content: space-between; align-items: center; color: #94A3B8; font-size: 0.7rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em;">
            <span>CASO 3: AHORRO VIVIENDA</span>
            <span class="kpi-icono" style="width: 1.8rem; height: 1.8rem; font-size: 1rem;"><i class="fa-solid fa-building"></i></span>
          </div>
          <div class="kpi-valor" style="color: #FFFFFF; font-size: 1.45rem; margin-top: 0.3rem;">{_p_html(vf_c3)} <span style="font-size: 0.75rem; color: #94A3B8; font-weight: normal;">VF</span></div>
          <div style="font-size: 0.75rem; color: #FBBF24; margin-top: 0.25rem; display: flex; align-items: center; gap: 0.3rem;">
            <i class="fa-solid fa-arrow-trend-up"></i> Gradiente: {c3_incremento}
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with k4:
    if fallas:
        color_verif, suave_verif, icono_verif = "#FB7185", "rgba(251, 113, 133, 0.15)", "fa-triangle-exclamation"
        clase_verif = "kpi-falla"
        color_detalle = "#FDA4AF"
        detalle_verif = f"Falla: {escape('; '.join(fallas))}"
    else:
        color_verif, suave_verif, icono_verif = "#34D399", "rgba(16, 185, 129, 0.15)", "fa-circle-check"
        clase_verif = "kpi-ok"
        color_detalle = "#94A3B8"
        detalle_verif = "Fórmulas contra método alternativo"
    st.markdown(
        f"""
        <div class="kpi {clase_verif}" style="--color: {color_verif}; --suave: {suave_verif};">
          <div style="display: flex; justify-content: space-between; align-items: center; color: #94A3B8; font-size: 0.7rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em;">
            <span>VERIFICACIONES</span>
            <span class="kpi-icono" style="width: 1.8rem; height: 1.8rem; font-size: 1rem;"><i class="fa-solid {icono_verif}"></i></span>
          </div>
          <div class="kpi-valor" style="margin-top: 0.3rem;">{total_ok} / {total_verificaciones} OK</div>
          <div style="font-size: 0.75rem; color: {color_detalle}; margin-top: 0.25rem;">
            {detalle_verif}
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

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
            <p style="font-size: 0.8rem; color: #94A3B8; margin: 0;">Síntesis comparativa calculada dinámicamente según las tasas y fuentes consultadas del mercado colombiano.</p>
            """,
            unsafe_allow_html=True,
        )
    with col_t2:
        if st.button("Ver Simuladores Detallados →", key="btn_ir_casos_top", use_container_width=True):
            st.switch_page("paginas/casos_aplicados.py")

    st.markdown(
        f"""
        <div style="overflow-x: auto; margin-top: 1rem;">
          <table class="tabla-resumen" style="width: 100%; text-align: left; border-collapse: separate; border-spacing: 0;">
            <thead>
              <tr>
                <th>Caso / Producto</th>
                <th>Entidad Financiera</th>
                <th>Tasa Efectiva Anual (E.A.)</th>
                <th>Total Pagado / Recibido</th>
                <th>Intereses Totales</th>
                <th>Decisión Recomendada</th>
                <th>Detalle de la Decisión</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td style="font-family: 'Inter', sans-serif; font-weight: 600; color: #FFFFFF;">
                  Caso 1: Crédito de Vehículo ({_p_html(c1_monto)} a {c1_plazo} meses)
                </td>
                <td style="font-family: 'Inter', sans-serif;">Sufi (Bancolombia) vs. Davivienda</td>
                <td>
                  <span style="color: #818CF8; font-weight: 600;">{porcentaje(c1_barata['ea'], 2)} E.A. {c1_barata['entidad']}</span> vs <span style="color: #94A3B8;">{porcentaje(c1_cara['ea'], 2)} {c1_cara['entidad']}</span>
                </td>
                <td>{_p_html(c1_total_frances)} (Cuota fija) vs {_p_html(c1_total_aleman)} (Abono constante)</td>
                <td style="color: #FB7185; font-weight: 600;">-{_p_html(c1_int_frances)} COP (Cuota fija)</td>
                <td style="font-family: 'Inter', sans-serif;">
                  <span class="etiqueta" style="--oscuro: #6366F1; --suave: rgba(99, 102, 241, 0.15); border-color: rgba(99, 102, 241, 0.4); color: #A5B4FC; display: inline-block; white-space: nowrap;">
                    {c1_barata['entidad']}
                  </span>
                </td>
                <td style="font-family: 'Inter', sans-serif;">Con abono constante a capital ahorra {_p_html(c1_ahorro_aleman)} en intereses</td>
              </tr>
              <tr>
                <td style="font-family: 'Inter', sans-serif; font-weight: 600; color: #FFFFFF;">
                  Caso 2: CDT Tradicional vs Cajita de Ahorro
                </td>
                <td style="font-family: 'Inter', sans-serif;">Bancolombia vs Nu Colombia</td>
                <td>
                  <span style="color: #34D399; font-weight: 600;">{porcentaje(c2_gana['ea'], 2)} E.A. ({c2_gana['corto']})</span> vs <span style="color: #94A3B8;">{porcentaje(c2_pierde['ea'], 2)} ({c2_pierde['corto']})</span>
                </td>
                <td>{_p_html(c2_total_gana)} COP neto ({c2_gana['corto']})</td>
                <td style="color: #34D399; font-weight: 600;">+{_p_html(c2_gana['rend'])} COP netos</td>
                <td style="font-family: 'Inter', sans-serif;">
                  <span class="etiqueta" style="--oscuro: #10B981; --suave: rgba(16, 185, 129, 0.15); border-color: rgba(16, 185, 129, 0.4); color: #34D399; display: inline-block; white-space: nowrap;">
                    {c2_gana['decision']}
                  </span>
                </td>
                <td style="font-family: 'Inter', sans-serif;">+{_p_html(c2_dif)} netos; {c2_gana['liquidez']}</td>
              </tr>
              <tr>
                <td style="font-family: 'Inter', sans-serif; font-weight: 600; color: #FFFFFF;">
                  Caso 3: Fiducuenta para Cuota Inicial de Vivienda
                </td>
                <td style="font-family: 'Inter', sans-serif;">Fiduciaria Bancolombia (Fiducuenta)</td>
                <td style="color: #FBBF24; font-weight: 600;">{porcentaje(c3_tasa_ea, 2)} E.A. ({porcentaje(c3_tasa_mv, 2)} M.V.)</td>
                <td>{_p_html(vf_c3)} COP (Capital acumulado)</td>
                <td style="color: #34D399; font-weight: 600;">+{_p_html(rend_c3)} COP rendimientos</td>
                <td style="font-family: 'Inter', sans-serif;">
                  <span class="etiqueta" style="--oscuro: #F59E0B; --suave: rgba(245, 158, 11, 0.15); border-color: rgba(245, 158, 11, 0.4); color: #FBBF24; display: inline-block; white-space: nowrap;">
                    {c3_plan['nombre']}
                  </span>
                </td>
                <td style="font-family: 'Inter', sans-serif;">{c3_frente_meta}; primera cuota de {_p_html(c3_a1)}</td>
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
              Despejes exactos de VP, VF, tasa periódica (i) y plazo (n). Soporte para base Comercial (360) y Exacta (365).
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
              Modelado de anualidades vencidas y anticipadas. Despejes cerrados de cuota (A), valor presente (VP) y valor futuro (VF).
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
                <p style="margin: 0; font-size: 0.75rem; color: #94A3B8;">Capitalización periódica discreta</p>
              </div>
            </div>
            <p style="font-size: 0.8rem; color: #CBD5E1; min-height: 40px; margin-bottom: 0.8rem;">
              Capitalización periódica sobre saldos crecientes, brecha de valor frente a interés simple y despeje de periodos (n).
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
              Series aritméticas (G en pesos) y geométricas (g en porcentaje). Cálculo analítico de cuota fija equivalente.
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
              Conversor universal multidireccional (EA, NAMV, periodicidades), tasas combinadas (IPC + spread o ecuación de Fisher) y retención tributaria.
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
                <p style="margin: 0; font-size: 0.75rem; color: #94A3B8;">Cuota fija vs Abono constante</p>
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
