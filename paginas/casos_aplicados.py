"""Página de casos aplicados: resolución interactiva de decisiones financieras reales."""

import io
import json
from pathlib import Path
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from componentes import entradas, estilos, graficos
from componentes.formato import numero, pesos, porcentaje
from finanzas import amortizacion, gradientes, series, tasas

TEMA = "principal"
COLOR_BASE = estilos.TEMAS[TEMA]["color"]
COLOR_FRANCES = estilos.TEMAS["amortizacion"]["color"]
COLOR_ALEMAN = estilos.TEMAS["series_uniformes"]["color"]
COLOR_INTERESES = estilos.INTERESES
COLOR_GRADIENTE = estilos.TEMAS["gradientes"]["color"]

# Cargar casos desde datos/casos.json
RUTA_CASOS = Path("datos/casos.json")


@st.cache_data
def cargar_casos():
    with open(RUTA_CASOS, "r", encoding="utf-8") as f:
        return json.load(f)["casos"]


casos = cargar_casos()
titulos_casos = {c["id"]: c["titulo"] for c in casos}

explicar = estilos.encabezado(
    TEMA,
    "Casos Prácticos Aplicados",
    "Modelación y análisis de decisiones financieras reales: crédito de vehículo, inversión/rentabilidad real y ahorro con gradientes.",
)

caso_seleccionado_id = st.segmented_control(
    "Selecciona un caso de estudio:",
    list(titulos_casos.keys()),
    default=list(titulos_casos.keys())[0],
    format_func=lambda cid: titulos_casos[cid],
    label_visibility="collapsed",
)

caso_actual = next(c for c in casos if c["id"] == caso_seleccionado_id)

with estilos.tarjeta("caso_header"):
    c1, c2 = st.columns([3, 1])
    with c1:
        st.markdown(f"### {caso_actual['titulo']}")
        st.markdown(caso_actual["descripcion"])
    with c2:
        st.caption("Temas integrados:")
        for t in caso_actual["temas"]:
            st.markdown(estilos.etiqueta(t, "principal"), unsafe_allow_html=True)

st.divider()

# ==============================================================================
# CASO 1: VEHÍCULO (SUFI VS. DAVIVIENDA)
# ==============================================================================
if caso_seleccionado_id == "vehiculo_sufi_davivienda":
    p = caso_actual["parametros"]
    col_izq, col_der = st.columns([1, 2], gap="large")

    with col_izq, estilos.tarjeta("vehiculo_inputs"):
        st.subheader("Datos de la compra")
        monto_vehiculo = entradas.campo_dinero("Valor a financiar", "veh_monto", p["monto"], minimo=1_000_000)
        plazo_meses = int(entradas.campo_numero("Plazo (meses)", "veh_plazo", p["plazo_meses"], minimo=12))

        st.divider()
        st.subheader("Entidades y tasas cotizadas")
        banco_sel = st.radio(
            "Seleccionar entidad:",
            ["sufi", "davivienda", "personalizado"],
            format_func=lambda b: {
                "sufi": "Sufi (1,65% Mes Vencido)",
                "davivienda": "Davivienda (20,50% NAMV)",
                "personalizado": "Ingresar tasa personalizada",
            }[b],
            key="veh_banco_sel",
        )

        if banco_sel == "sufi":
            tasa_mv = 0.0165
            tasa_ea = tasas.ea_desde_periodica(tasa_mv, 12)
            desc_tasa = "1,65% MV (Sufi - Bancolombia)"
        elif banco_sel == "davivienda":
            tasa_namv = 0.2050
            tasa_mv = tasa_namv / 12
            tasa_ea = tasas.ea_desde_periodica(tasa_mv, 12)
            desc_tasa = "20,50% NAMV (Davivienda)"
        else:
            tasa_ea, desc_tasa = entradas.selector_tasa("veh_custom", 0.017)
            tasa_mv = tasas.periodica_desde_ea(tasa_ea, 12)

        st.caption(
            f"**Equivalencia:** {desc_tasa} $\\Longleftrightarrow$ "
            f"**{porcentaje(tasa_mv, 4)} mensual** = **{porcentaje(tasa_ea, 4)} EA**."
        )

    # Cálculos comparativos de los dos sistemas
    tabla_frances = amortizacion.tabla_amortizacion(monto_vehiculo, tasa_mv, plazo_meses, sistema="frances")
    tabla_aleman = amortizacion.tabla_amortizacion(monto_vehiculo, tasa_mv, plazo_meses, sistema="aleman")
    res_frances = amortizacion.resumen_amortizacion(tabla_frances)
    res_aleman = amortizacion.resumen_amortizacion(tabla_aleman)
    ahorro_intereses = res_frances["total_intereses"] - res_aleman["total_intereses"]

    with col_der:
        st.subheader("Comparativa de sistemas de amortización a 48 meses")

        k1, k2, k3 = st.columns(3)
        with k1:
            st.metric(
                "Cuota fija (Francés)",
                pesos(res_frances["cuota_inicial"]),
                help="Pago constante todos los meses",
            )
        with k2:
            st.metric(
                "Primera cuota (Alemán)",
                pesos(res_aleman["cuota_inicial"]),
                delta=pesos(res_aleman["cuota_inicial"] - res_frances["cuota_inicial"]),
                delta_color="inverse",
                help="Arranca más alta y baja cada mes",
            )
        with k3:
            st.metric(
                "Ahorro en intereses con Alemán",
                pesos(ahorro_intereses),
                delta=f"-{porcentaje(ahorro_intereses / res_frances['total_intereses'])}",
                help="Menor costo financiero total pagado",
            )

        # Gráfico comparativo de cuotas periodo a periodo
        periodos = [f["periodo"] for f in tabla_frances[1:]]
        cuotas_f = [f["cuota"] for f in tabla_frances[1:]]
        cuotas_a = [f["cuota"] for f in tabla_aleman[1:]]

        fig_cuotas = go.Figure()
        fig_cuotas.add_trace(
            go.Scatter(
                x=periodos,
                y=cuotas_f,
                name="Cuota Fija (Francés)",
                line={"color": COLOR_FRANCES, "width": 3},
            )
        )
        fig_cuotas.add_trace(
            go.Scatter(
                x=periodos,
                y=cuotas_a,
                name="Abono Constante (Alemán)",
                line={"color": COLOR_ALEMAN, "width": 3, "dash": "dash"},
            )
        )
        fig_cuotas.update_layout(
            title={"text": "<b>Evolución de las cuotas mensuales: Francés vs. Alemán</b>", "x": 0.01, "font": {"color": "#FFFFFF", "size": 15}},
            font={"family": "Inter, sans-serif", "color": "#94A3B8"},
            paper_bgcolor="rgba(15, 23, 42, 0.4)",
            plot_bgcolor="rgba(15, 23, 42, 0.4)",
            hovermode="x unified",
            legend={"orientation": "h", "y": 1.05, "font": {"color": "#CBD5E1"}},
            margin={"l": 15, "r": 15, "t": 60, "b": 15},
        )
        fig_cuotas.update_yaxes(title="Cuota a pagar ($ COP)", tickprefix="$ ", tickformat=",.0f", gridcolor="rgba(51, 65, 85, 0.35)", linecolor="rgba(51, 65, 85, 0.6)", color="#94A3B8")
        fig_cuotas.update_xaxes(title="Mes", gridcolor="rgba(51, 65, 85, 0.35)", linecolor="rgba(51, 65, 85, 0.6)", color="#94A3B8")
        st.plotly_chart(fig_cuotas, width="stretch", config=graficos.CONFIG_PLOTLY)

        # Veredicto financiero
        with estilos.tarjeta("veh_veredicto"):
            st.markdown("#### 🎯 Veredicto Financiero y Toma de Decisiones")
            st.markdown(
                f"- **Para liquidez y presupuesto estable:** Te conviene el **Sistema Francés (Cuota Fija)**, "
                f"pues pagarás exactamente **{pesos(res_frances['cuota_inicial'])}** fijos cada mes. "
                f"En el primer mes te exige **{pesos(res_aleman['cuota_inicial'] - res_frances['cuota_inicial'])} menos** que el sistema alemán.\n"
                f"- **Para costo total mínimo:** Te conviene el **Sistema Alemán (Abono Constante)**, "
                f"ya que ahorras **{pesos(ahorro_intereses)}** en intereses totales "
                f"(pagas **{pesos(res_aleman['total_intereses'])}** vs **{pesos(res_frances['total_intereses'])}**), "
                f"y la cuota final en el mes 48 desciende hasta **{pesos(res_aleman['cuota_final'])}**."
            )

        # Tablas desplegables
        with st.expander("Ver tablas detalladas de amortización (Francés y Alemán)"):
            t_col1, t_col2 = st.columns(2)
            with t_col1:
                st.markdown("**Tabla Cuota Fija (Francés)**")
                df_f = pd.DataFrame(
                    [
                        {
                            "Mes": f["periodo"],
                            "Cuota": pesos(f["cuota"]),
                            "Interés": pesos(f["intereses"]),
                            "Abono": pesos(f["abono_capital"]),
                            "Saldo": pesos(f["saldo_final"]),
                        }
                        for f in tabla_frances[1:]
                    ]
                )
                st.dataframe(df_f, hide_index=True, height=300, width="stretch")
            with t_col2:
                st.markdown("**Tabla Abono Constante (Alemán)**")
                df_a = pd.DataFrame(
                    [
                        {
                            "Mes": f["periodo"],
                            "Cuota": pesos(f["cuota"]),
                            "Interés": pesos(f["intereses"]),
                            "Abono": pesos(f["abono_capital"]),
                            "Saldo": pesos(f["saldo_final"]),
                        }
                        for f in tabla_aleman[1:]
                    ]
                )
                st.dataframe(df_a, hide_index=True, height=300, width="stretch")

# ==============================================================================
# CASO 2: RENTABILIDAD REAL (BANCOLOMBIA VS. NU / LULO)
# ==============================================================================
elif caso_seleccionado_id == "inversion_bancolombia_nu":
    p = caso_actual["parametros"]
    col_izq, col_der = st.columns([1, 2], gap="large")

    with col_izq, estilos.tarjeta("inv_inputs"):
        st.subheader("Datos de la inversión")
        capital_inv = entradas.campo_dinero("Capital a invertir", "inv_capital", p["capital"], minimo=100_000)
        plazo_dias = int(
            st.selectbox("Plazo de inversión", [90, 180, 360], index=2, key="inv_plazo_dias")
        )

        st.divider()
        st.markdown("**Alternativa A: CDT Bancolombia**")
        tasa_cdt_ea = entradas.campo_tasa("Tasa CDT Bancolombia (% EA)", "inv_tasa_cdt", p["tasa_cdt_ea"])
        modo_cdt = st.radio(
            "Manejo de rendimientos CDT:",
            ["compuesto", "simple"],
            format_func=lambda m: {
                "compuesto": "Capitalización al vencimiento (Interés Compuesto)",
                "simple": "Retiro periódico de intereses (Interés Simple)",
            }[m],
            key="inv_modo_cdt",
        )

        st.divider()
        st.markdown("**Alternativa B: Cuenta de Rendimientos (Nu / Lulo)**")
        tasa_nu_ea = entradas.campo_tasa("Tasa Cuenta de Ahorro (% EA)", "inv_tasa_nu", p["tasa_cuenta_ea"])
        st.caption("Capitalización diaria con disponibilidad de saldo inmediata.")

        st.divider()
        st.markdown("**Impuestos e Inflación**")
        ret_fuente = entradas.campo_tasa("Retención en la fuente sobre intereses", "inv_ret", p["retencion_fuente"])
        ipc_anual = entradas.campo_tasa("Inflación anual esperada (IPC)", "inv_ipc", p["inflacion_ipc"])

    # 1. Cálculos Alternativa A (CDT Bancolombia)
    t_anos_comercial = plazo_dias / 360
    if modo_cdt == "simple":
        intereses_brutos_cdt = capital_inv * tasa_cdt_ea * t_anos_comercial
    else:
        intereses_brutos_cdt = capital_inv * ((1 + tasa_cdt_ea) ** t_anos_comercial - 1)

    retencion_cdt = intereses_brutos_cdt * ret_fuente
    intereses_netos_cdt = intereses_brutos_cdt - retencion_cdt
    vf_neto_cdt = capital_inv + intereses_netos_cdt
    tea_neta_cdt = (vf_neto_cdt / capital_inv) ** (1 / t_anos_comercial) - 1
    rent_real_cdt = tasas.tasa_real(tea_neta_cdt, ipc_anual)

    # 2. Cálculos Alternativa B (Cuenta Nu / Lulo - Capitalización Diaria)
    t_anos_real = plazo_dias / 365
    i_diaria_nu = (1 + tasa_nu_ea) ** (1 / 365) - 1
    vf_bruto_nu = capital_inv * ((1 + i_diaria_nu) ** plazo_dias)
    intereses_brutos_nu = vf_bruto_nu - capital_inv
    retencion_nu = intereses_brutos_nu * ret_fuente
    intereses_netos_nu = intereses_brutos_nu - retencion_nu
    vf_neto_nu = capital_inv + intereses_netos_nu
    tea_neta_nu = (vf_neto_nu / capital_inv) ** (1 / t_anos_real) - 1
    rent_real_nu = tasas.tasa_real(tea_neta_nu, ipc_anual)

    diferencia_neta = intereses_netos_nu - intereses_netos_cdt

    with col_der:
        st.subheader(f"Comparativa de Rentabilidad Neta ({plazo_dias} días)")

        k1, k2, k3, k4 = st.columns(4)
        with k1:
            estilos.tarjeta_kpi("account_balance", pesos(intereses_netos_cdt), "Ganancia neta CDT", "principal")
        with k2:
            estilos.tarjeta_kpi("savings", pesos(intereses_netos_nu), "Ganancia neta Nu / Lulo", "amortizacion")
        with k3:
            estilos.tarjeta_kpi("trending_up", pesos(diferencia_neta), "Diferencia a favor Nu", "intereses")
        with k4:
            estilos.tarjeta_kpi("percent", porcentaje(rent_real_nu), "Rentabilidad real Nu", TEMA)

        # Gráfico comparativo de resultados al vencimiento
        fig_inv = go.Figure()
        fig_inv.add_trace(
            go.Bar(
                name="Capital Invertido",
                x=["CDT Bancolombia", "Cuenta Nu / Lulo"],
                y=[capital_inv, capital_inv],
                marker_color="#94A3B8",
            )
        )
        fig_inv.add_trace(
            go.Bar(
                name="Rendimiento Neto (Bolsillo)",
                x=["CDT Bancolombia", "Cuenta Nu / Lulo"],
                y=[intereses_netos_cdt, intereses_netos_nu],
                marker_color=COLOR_FRANCES,
            )
        )
        fig_inv.add_trace(
            go.Bar(
                name="Retención en la Fuente (4%)",
                x=["CDT Bancolombia", "Cuenta Nu / Lulo"],
                y=[retencion_cdt, retencion_nu],
                marker_color=estilos.INTERESES,
            )
        )
        fig_inv.update_layout(
            barmode="stack",
            title={"text": f"<b>Descomposición del Capital Final tras {plazo_dias} días</b>", "x": 0.01, "font": {"color": "#FFFFFF", "size": 15}},
            font={"family": "Inter, sans-serif", "color": "#94A3B8"},
            paper_bgcolor="rgba(15, 23, 42, 0.4)",
            plot_bgcolor="rgba(15, 23, 42, 0.4)",
            hovermode="x unified",
            legend={"orientation": "h", "y": 1.05, "font": {"color": "#CBD5E1"}},
            margin={"l": 15, "r": 15, "t": 60, "b": 15},
        )
        fig_inv.update_yaxes(title="Valor ($ COP)", tickprefix="$ ", tickformat=",.0f", gridcolor="rgba(51, 65, 85, 0.35)", linecolor="rgba(51, 65, 85, 0.6)", color="#94A3B8")
        fig_inv.update_xaxes(gridcolor="rgba(51, 65, 85, 0.35)", linecolor="rgba(51, 65, 85, 0.6)", color="#94A3B8")
        st.plotly_chart(fig_inv, width="stretch", config=graficos.CONFIG_PLOTLY)

        # Veredicto y análisis de liquidez vs rentabilidad
        with estilos.tarjeta("inv_veredicto"):
            st.markdown("#### ⚖️ Veredicto Financiero: Rentabilidad Real y Liquidez")
            st.markdown(
                f"- **Rentabilidad Neta y Real:** En la cuenta de alto rendimiento (Nu/Lulo) obtienes **{pesos(intereses_netos_nu)}** netos "
                f"contra **{pesos(intereses_netos_cdt)}** en el CDT, una diferencia neta a favor de **{pesos(diferencia_neta)}**.\n"
                f"- **Poder adquisitivo (Inflación del {porcentaje(ipc_anual)}):**\n"
                f"  - CDT Bancolombia: Rentabilidad real neta de **{porcentaje(rent_real_cdt)}** por encima de la inflación.\n"
                f"  - Cuenta Nu / Lulo: Rentabilidad real neta de **{porcentaje(rent_real_nu)}** por encima de la inflación.\n"
                f"- **Criterio de Liquidez (Dilema del inversionista):**\n"
                f"  - El **CDT** tiene **cero liquidez** (el dinero no se puede retirar antes de los {plazo_dias} días sin penalización grave o venta en mercado secundario).\n"
                f"  - La **cuenta de rendimientos** capitaliza a diario y te ofrece **disponibilidad 24/7**, siendo actualmente la opción ganadora en tasa y liquidez (ambas con seguro de depósitos FOGAFIN hasta $50M)."
            )

        with st.expander("Ver tabla comparativa técnica completa"):
            tabla_comp = pd.DataFrame(
                [
                    {"Concepto": "Tasa cotizada en pantalla", "CDT Bancolombia": porcentaje(tasa_cdt_ea), "Nu / Lulo Bank": porcentaje(tasa_nu_ea)},
                    {"Concepto": "Mecanismo de cálculo", "CDT Bancolombia": "Compuesto" if modo_cdt == "compuesto" else "Simple", "Nu / Lulo Bank": "Compuesto diario"},
                    {"Concepto": "Rendimientos brutos generados", "CDT Bancolombia": pesos(intereses_brutos_cdt), "Nu / Lulo Bank": pesos(intereses_brutos_nu)},
                    {"Concepto": "Retención en la fuente (4%)", "CDT Bancolombia": pesos(retencion_cdt), "Nu / Lulo Bank": pesos(retencion_nu)},
                    {"Concepto": "Rendimientos netos recibidos", "CDT Bancolombia": pesos(intereses_netos_cdt), "Nu / Lulo Bank": pesos(intereses_netos_nu)},
                    {"Concepto": "Tasa Efectiva Anual Neta (TEA neta)", "CDT Bancolombia": porcentaje(tea_neta_cdt), "Nu / Lulo Bank": porcentaje(tea_neta_nu)},
                    {"Concepto": "Rentabilidad real neta (descontando IPC)", "CDT Bancolombia": porcentaje(rent_real_cdt), "Nu / Lulo Bank": porcentaje(rent_real_nu)},
                    {"Concepto": "Liquidez del dinero", "CDT Bancolombia": f"Bloqueado {plazo_dias} días", "Nu / Lulo Bank": "Inmediata (24/7)"},
                ]
            )
            st.dataframe(tabla_comp, hide_index=True, width="stretch")

# ==============================================================================
# CASO 3: AHORRO PROGRAMADO CON GRADIENTES
# ==============================================================================
elif caso_seleccionado_id == "ahorro_cuota_inicial_gradientes":
    p = caso_actual["parametros"]
    col_izq, col_der = st.columns([1, 2], gap="large")

    with col_izq, estilos.tarjeta("grad_inputs"):
        st.subheader("Parámetros del plan de ahorro")
        a1 = entradas.campo_dinero("Primera cuota de ahorro (A1)", "gr_a1", p["a1"], minimo=50_000, paso=50_000)
        n_meses = int(entradas.campo_numero("Plazo del plan (meses)", "gr_plazo", p["plazo_meses"], minimo=6))
        tasa_mv = entradas.campo_tasa("Rentabilidad del fondo (% MV)", "gr_tasa", p["tasa_mv"], minimo=0.0001, maximo=0.10)

        st.divider()
        st.subheader("Modalidad de incremento")
        tipo_grad = st.radio(
            "Tipo de gradiente:",
            ["aritmetico", "geometrico"],
            format_func=lambda g: {
                "aritmetico": "Gradiente Aritmético (+ G pesos cada mes)",
                "geometrico": "Gradiente Geométrico (+ g % cada mes)",
            }[g],
            key="gr_tipo_grad",
        )

        if tipo_grad == "aritmetico":
            g_val = entradas.campo_dinero(
                "Incremento mensual fijo (G)", "gr_G", p["gradiente_aritmetico_G"], minimo=1_000, paso=5_000
            )
            desc_incremento = f"+ {pesos(g_val)} cada mes"
        else:
            g_val = entradas.campo_tasa(
                "Incremento mensual porcentual (g)", "gr_g", p["gradiente_geometrico_g"], minimo=0.001, maximo=0.20
            )
            desc_incremento = f"+ {porcentaje(g_val)} cada mes"

    # Lógica de cálculo en Python según las fórmulas de clase
    if tipo_grad == "aritmetico":
        cuotas = gradientes.cuotas_aritmetico(a1, g_val, n_meses)
        vp = gradientes.vp_aritmetico(a1, g_val, tasa_mv, n_meses)
    else:
        cuotas = gradientes.cuotas_geometrico(a1, g_val, n_meses)
        vp = gradientes.vp_geometrico(a1, g_val, tasa_mv, n_meses)

    vf_acumulado = gradientes.vf_gradiente(vp, tasa_mv, n_meses)
    cuota_equivalente = gradientes.cuota_equivalente(vp, tasa_mv, n_meses)

    # Simulación periodo a periodo de saldo y aportes acumulados
    meses_arr = list(range(1, n_meses + 1))
    saldos_mes = []
    aportes_acum = []
    saldo_t = 0.0
    aporte_total_t = 0.0

    for c in cuotas:
        saldo_t = saldo_t * (1 + tasa_mv) + c
        aporte_total_t += c
        saldos_mes.append(saldo_t)
        aportes_acum.append(aporte_total_t)

    total_aportado = aportes_acum[-1]
    intereses_ganados = saldos_mes[-1] - total_aportado
    cruce_mes = gradientes.periodo_cruce(cuotas, cuota_equivalente)

    with col_der:
        st.subheader("Resultados del Plan de Ahorro para Cuota Inicial")

        k1, k2, k3, k4 = st.columns(4)
        with k1:
            estilos.tarjeta_kpi("savings", pesos(vf_acumulado), "Capital acumulado (VF)", "amortizacion")
        with k2:
            estilos.tarjeta_kpi("balance", pesos(cuota_equivalente), "Cuota fija equivalente", TEMA)
        with k3:
            estilos.tarjeta_kpi("payments", pesos(total_aportado), "Aportes de tu bolsillo", "principal")
        with k4:
            estilos.tarjeta_kpi("trending_up", pesos(intereses_ganados), "Rendimientos ganados", "intereses")

        # Gráfico 1: Barras de aportes con línea de cuota equivalente
        fig_aportes = go.Figure()
        fig_aportes.add_trace(
            go.Bar(
                x=meses_arr,
                y=cuotas,
                name="Aporte mensual programado (Gradiente)",
                marker_color=COLOR_GRADIENTE,
            )
        )
        graficos.linea_referencia(
            fig_aportes,
            meses_arr,
            cuota_equivalente,
            f"Cuota Equivalente: {pesos(cuota_equivalente)}",
            "#38BDF8",
        )
        fig_aportes.update_layout(
            title={"text": f"<b>Evolución de aportes mensuales ({desc_incremento}) vs. Cuota Equivalente</b>", "x": 0.01, "font": {"color": "#FFFFFF", "size": 15}},
            font={"family": "Inter, sans-serif", "color": "#94A3B8"},
            paper_bgcolor="rgba(15, 23, 42, 0.4)",
            plot_bgcolor="rgba(15, 23, 42, 0.4)",
            hovermode="x unified",
            legend={"orientation": "h", "y": 1.05, "font": {"color": "#CBD5E1"}},
            margin={"l": 15, "r": 15, "t": 60, "b": 15},
        )
        fig_aportes.update_yaxes(title="Aporte mensual ($ COP)", tickprefix="$ ", tickformat=",.0f", gridcolor="rgba(51, 65, 85, 0.35)", linecolor="rgba(51, 65, 85, 0.6)", color="#94A3B8")
        fig_aportes.update_xaxes(title="Mes de ahorro", gridcolor="rgba(51, 65, 85, 0.35)", linecolor="rgba(51, 65, 85, 0.6)", color="#94A3B8")
        st.plotly_chart(fig_aportes, width="stretch", config=graficos.CONFIG_PLOTLY)

        # Gráfico 2: Evolución del saldo acumulado (Aportes vs Intereses)
        fig_acum = go.Figure()
        fig_acum.add_trace(
            go.Scatter(
                x=meses_arr,
                y=saldos_mes,
                name="Saldo total acumulado (con intereses)",
                line={"color": COLOR_FRANCES, "width": 3},
            )
        )
        fig_acum.add_trace(
            go.Scatter(
                x=meses_arr,
                y=aportes_acum,
                name="Aportes acumulados (Capital propio)",
                line={"color": "#64748B", "width": 2, "dash": "dash"},
            )
        )
        fig_acum.update_layout(
            title={"text": "<b>Crecimiento del capital acumulado mes a mes</b>", "x": 0.01, "font": {"color": "#FFFFFF", "size": 15}},
            font={"family": "Inter, sans-serif", "color": "#94A3B8"},
            paper_bgcolor="rgba(15, 23, 42, 0.4)",
            plot_bgcolor="rgba(15, 23, 42, 0.4)",
            hovermode="x unified",
            legend={"orientation": "h", "y": 1.05, "font": {"color": "#CBD5E1"}},
            margin={"l": 15, "r": 15, "t": 60, "b": 15},
        )
        fig_acum.update_yaxes(title="Saldo acumulado ($ COP)", tickprefix="$ ", tickformat=",.0f", gridcolor="rgba(51, 65, 85, 0.35)", linecolor="rgba(51, 65, 85, 0.6)", color="#94A3B8")
        fig_acum.update_xaxes(title="Mes", gridcolor="rgba(51, 65, 85, 0.35)", linecolor="rgba(51, 65, 85, 0.6)", color="#94A3B8")
        st.plotly_chart(fig_acum, width="stretch", config=graficos.CONFIG_PLOTLY)

        with estilos.tarjeta("grad_veredicto"):
            st.markdown("#### 🎯 Análisis y Toma de Decisiones")
            st.markdown(
                f"- **Ventaja de iniciar con Gradiente:** Puedes arrancar con un esfuerzo bajo de solo **{pesos(a1)}** "
                f"en el mes 1 e ir subiendo progresivamente a medida que aumentan tus ingresos o tu disciplina, "
                f"alcanzando una última cuota de **{pesos(cuotas[-1])}** en el mes {n_meses}.\n"
                f"- **Equivalencia uniforme:** Para lograr exactamente el mismo capital acumulado de **{pesos(vf_acumulado)}**, "
                f"habrías tenido que comprometerte con una cuota fija uniforme de **{pesos(cuota_equivalente)}** desde el primer mes. "
                f"En el mes **{cruce_mes}** tu aporte con gradiente cruza y supera a la cuota uniforme.\n"
                f"- **Efecto del interés compuesto:** De los **{pesos(vf_acumulado)}** finales para tu cuota inicial, "
                f"tú aportaste **{pesos(total_aportado)}** (**{porcentaje(total_aportado / vf_acumulado)}**) y el fondo te generó "
                f"**{pesos(intereses_ganados)}** en rendimientos limpios (**{porcentaje(intereses_ganados / vf_acumulado)}**)."
            )

        with st.expander("Ver tabla completa de aportes y saldos mes a mes"):
            df_grad = pd.DataFrame(
                [
                    {
                        "Mes": m,
                        "Aporte del mes": pesos(c),
                        "Aportes acumulados": pesos(ap),
                        "Rendimientos ganados": pesos(s - ap),
                        "Saldo acumulado": pesos(s),
                    }
                    for m, c, ap, s in zip(meses_arr, cuotas, aportes_acum, saldos_mes)
                ]
            )
            st.dataframe(df_grad, hide_index=True, height=300, width="stretch")
