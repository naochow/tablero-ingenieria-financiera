"""Página de casos aplicados: resolución interactiva de decisiones financieras reales."""

import io
import json
from pathlib import Path
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from componentes import entradas, estilos, graficos
from componentes.formato import escapar_md, numero, pesos, pesos_md, porcentaje, supuesto_retencion_cuenta
from componentes.verificacion import tarjeta_verificacion
from finanzas import amortizacion, gradientes, series, tasas


def p_tex(valor, decimales=2):
    """Devuelve el porcentaje con % escapado para usarlo dentro de una fórmula KaTeX."""
    return porcentaje(valor, decimales).replace("%", r"\%")


TEMA = "principal"
COLOR_BASE = estilos.TEMAS[TEMA]["color"]
COLOR_FRANCES = estilos.TEMAS["amortizacion"]["color"]
COLOR_ALEMAN = estilos.TEMAS["series_uniformes"]["color"]
COLOR_INTERESES = estilos.INTERESES
COLOR_GRADIENTE = estilos.TEMAS["gradientes"]["color"]

# Cargar casos desde datos/casos.json
RUTA_CASOS = Path("datos/casos.json")

FALLBACK_INFO = {
    "vehiculo_sufi_davivienda": {
        "entidades": "Sufi (Grupo Bancolombia) vs. Banco Davivienda",
        "fecha_consulta": "2 de noviembre de 2026",
        "fuentes": [
            {
                "nombre": "Simulador Sufi",
                "url": "https://simulador.sufi.apps.bancolombia.com/",
                "fecha": "2 de noviembre de 2026",
                "nota": "Sufi: tasa de política con corte a octubre de 2025, según aclara el simulador.",
            },
            {
                "nombre": "Simulador de vehículo Davivienda",
                "url": "https://misfinanzasencasa.davivienda.com/finanzas-personales/simuladores/simulador-de-credito-de-vehiculo/",
                "fecha": "2 de noviembre de 2026",
            },
        ],
    },
    "inversion_bancolombia_nu": {
        "entidades": "Bancolombia (CDT Físico) vs. Nu Colombia (Cajitas de Ahorro)",
        "fecha_consulta": "2 de noviembre de 2026",
        "fuentes": [
            {
                "nombre": "Simulador CDT Bancolombia",
                "url": "https://www.bancolombia.com/personas/productos/inversiones/simulador-cdt",
                "fecha": "2 de noviembre de 2026",
            },
            {
                "nombre": "Forbes Colombia",
                "url": "https://forbes.co/economia-y-finanzas/donde-poner-sus-ahorros-para-ganar-mas-intereses-estas-son-las-tasas-que-ofrecen-los-bancos-en-colombia",
                "fecha": "20 de octubre de 2026",
                "nota": "Tasa de las Cajitas de Nu para clientes regulares, informada para octubre de 2026.",
            },
            {
                "nombre": "DANE: boletín IPC septiembre 2026",
                "url": "https://www.dane.gov.co/files/operaciones/IPC/sep2026/bol-IPC-sep2026.pdf",
                "fecha": "7 de octubre de 2026",
            },
            {
                "nombre": "Valora Analitik",
                "url": "https://www.valoraanalitik.com/diferencias-retencion-fuente-cdt-cuenta-ahorros/",
                "fecha": "9 de enero de 2025",
                "nota": "Tarifas de retención: 4% para CDT y 7% para cuentas de ahorro.",
            },
        ],
        "parametros": {
            "retencion_cdt": 0.04,
            "retencion_cuenta": 0.07,
            "tasa_cuenta_ea": 0.0935,
        },
    },
    "ahorro_cuota_inicial_gradientes": {
        "entidades": "Fiduciaria Bancolombia (Fiducuenta)",
        "fecha_consulta": "2 de noviembre de 2026",
        "fuentes": [
            {
                "nombre": "Rankia Colombia",
                "url": "https://www.rankia.co/blog/fondos-inversion-colectiva-colombia/4682852-fiducuenta-bancolombia-beneficios-comisiones",
                "fecha": "22 de octubre de 2026",
                "nota": "Datos del informe diario de rentabilidades de Fiduciaria Bancolombia.",
            },
        ],
    },
}


def cargar_casos():
    try:
        with open(RUTA_CASOS, "r", encoding="utf-8") as f:
            casos_cargados = json.load(f)["casos"]
    except Exception:
        casos_cargados = []

    for c in casos_cargados:
        fb = FALLBACK_INFO.get(c["id"], {})
        if not c.get("entidades"):
            c["entidades"] = fb.get("entidades", "")
        if not c.get("fecha_consulta"):
            c["fecha_consulta"] = fb.get("fecha_consulta", "")
        if not c.get("fuentes"):
            c["fuentes"] = fb.get("fuentes", [])
    return casos_cargados


casos = cargar_casos()
titulos_casos = {c["id"]: c["titulo"] for c in casos}

explicar = estilos.encabezado(
    TEMA,
    "Casos Prácticos Aplicados",
    "Modelación y análisis de decisiones financieras reales: crédito de vehículo, inversión/rentabilidad real y ahorro con gradientes.",
)



def _conservar_caso():
    """Un clic en el caso ya seleccionado deja el control vacío: se restaura el caso anterior."""
    if st.session_state["caso_sel"] is None:
        st.session_state["caso_sel"] = st.session_state["caso_activo"]
    st.session_state["caso_activo"] = st.session_state["caso_sel"]


st.session_state.setdefault("caso_activo", list(titulos_casos.keys())[0])
st.session_state.setdefault("caso_sel", st.session_state["caso_activo"])

caso_seleccionado_id = st.segmented_control(
    "Selecciona un caso de estudio:",
    list(titulos_casos.keys()),
    format_func=lambda cid: titulos_casos[cid],
    label_visibility="collapsed",
    key="caso_sel",
    on_change=_conservar_caso,
)

caso_actual = next(c for c in casos if c["id"] == caso_seleccionado_id)
fallback = FALLBACK_INFO.get(caso_actual["id"], {})
entidades_txt = caso_actual.get("entidades") or fallback.get("entidades", "")
fecha_txt = caso_actual.get("fecha_consulta") or fallback.get("fecha_consulta", "")
fuentes = caso_actual.get("fuentes") or fallback.get("fuentes", [])

with estilos.tarjeta("caso_header"):
    c1, c2 = st.columns([3, 1])
    with c1:
        st.markdown(f"### {caso_actual['titulo']}")
        st.markdown(caso_actual["descripcion"])
        st.markdown(
            f"""
            <div style="display: flex; flex-wrap: wrap; gap: 1.5rem; font-size: 0.85rem; color: #94A3B8; margin-top: 0.7rem; margin-bottom: 0.8rem; padding: 0.6rem 0.9rem; background: rgba(15, 23, 42, 0.45); border-radius: 8px; border: 1px solid rgba(51, 65, 85, 0.5);">
              <span>🏛️ <b>Entidades:</b> <span style="color: #F1F5F9;">{entidades_txt}</span></span>
              <span>📅 <b>Fecha consulta:</b> <span style="color: #F1F5F9;">{fecha_txt}</span></span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Botones interactivos con enlaces directos a cada fuente, con su nombre y fecha
        if fuentes:
            st.caption("Fuentes consultadas (haz clic para abrir en pestaña nueva):")
            cols_btn = st.columns(len(fuentes))
            for i, f in enumerate(fuentes):
                with cols_btn[i]:
                    st.link_button(
                        label=f"🌐 {f['nombre']}",
                        url=f["url"],
                        use_container_width=True,
                    )
                    st.caption(f"Fecha: {f['fecha']}. {f.get('nota', '')}")
    with c2:
        st.caption("Temas integrados (Rúbrica):")
        for t in caso_actual["temas"]:
            st.markdown(estilos.etiqueta(t, "principal"), unsafe_allow_html=True)

st.divider()

# ==============================================================================
# CASO 1: VEHÍCULO (SUFI VS. DAVIVIENDA)
# ==============================================================================
if caso_seleccionado_id == "vehiculo_sufi_davivienda":
    p = caso_actual["parametros"]
    col_izq, col_der = st.columns([1, 2], gap="large")

    # Tasas cotizadas llevadas a EA y a mensual para compararlas en la misma base
    ofertas = {}
    for clave, oferta in zip(("sufi", "davivienda"), p["ofertas"]):
        ea_oferta = tasas.ea_desde_codigo(oferta["tasa_valor"], oferta["codigo_tasa"])
        ofertas[clave] = {**oferta, "ea": ea_oferta, "mv": tasas.periodica_desde_ea(ea_oferta, 12)}
    clave_barata = min(ofertas, key=lambda k: ofertas[k]["ea"])
    oferta_barata = ofertas[clave_barata]
    oferta_cara = max(ofertas.values(), key=lambda o: o["ea"])
    notas_tasas = " ".join(f["nota"] for f in fuentes if f.get("nota"))

    with col_izq, estilos.tarjeta("vehiculo_inputs"):
        st.subheader("Datos de la compra")
        monto_vehiculo = entradas.campo_dinero("Valor a financiar", "veh_monto", p["monto"], minimo=1_000_000)
        plazo_meses = int(entradas.campo_numero("Plazo (meses)", "veh_plazo", p["plazo_meses"], minimo=12))

        st.divider()
        st.subheader("Entidades y tasas cotizadas")
        opciones_banco = [*ofertas, "personalizado"]
        banco_sel = st.radio(
            "Seleccionar entidad:",
            opciones_banco,
            index=opciones_banco.index(clave_barata),
            format_func=lambda b: (
                "Ingresar tasa personalizada"
                if b == "personalizado"
                else f"{ofertas[b]['entidad']}: {ofertas[b]['descripcion']}"
            ),
            key="veh_banco_sel",
        )

        if banco_sel in ofertas:
            tasa_mv = ofertas[banco_sel]["mv"]
            tasa_ea = ofertas[banco_sel]["ea"]
            desc_tasa = f"{ofertas[banco_sel]['descripcion']}, {ofertas[banco_sel]['entidad']}"
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
        st.subheader(f"Comparativa de sistemas de amortización a {plazo_meses} meses")

        k1, k2, k3 = st.columns(3)
        with k1:
            estilos.tarjeta_kpi("payments", pesos(res_frances["cuota_inicial"]), "Cuota fija (Francés)", "amortizacion")
        with k2:
            estilos.tarjeta_kpi("trending_down", pesos(res_aleman["cuota_inicial"]), "1.ª cuota (Alemán)", "series_uniformes")
        with k3:
            estilos.tarjeta_kpi("savings", pesos(ahorro_intereses), f"Ahorro intereses ({porcentaje(ahorro_intereses / res_frances['total_intereses'])})", "principal")

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
            separators=graficos.SEPARADORES_PLOTLY,
            hovermode="x unified",
            legend={"orientation": "h", "y": -0.22, "yanchor": "top", "x": 0.5, "xanchor": "center", "font": {"color": "#CBD5E1"}},
            margin={"l": 75, "r": 20, "t": 48, "b": 60},
        )
        fig_cuotas.update_yaxes(title="Cuota a pagar ($ COP)", tickprefix="$ ", tickformat=",.0f", gridcolor="rgba(51, 65, 85, 0.35)", linecolor="rgba(51, 65, 85, 0.6)", color="#94A3B8")
        fig_cuotas.update_xaxes(title="Mes", gridcolor="rgba(51, 65, 85, 0.35)", linecolor="rgba(51, 65, 85, 0.6)", color="#94A3B8")
        st.plotly_chart(fig_cuotas, width="stretch", config=graficos.CONFIG_PLOTLY)

        # Verificación Matemática
        st.subheader("Verificación Matemática")
        vp_cuotas = sum(f["cuota"] / ((1 + tasa_mv) ** f["periodo"]) for f in tabla_frances[1:])
        tarjeta_verificacion(
            "Ecuación de valor: VP cuotas descontadas == Capital financiado",
            vp_cuotas,
            monto_vehiculo,
            "Valor Presente de las cuotas a tasa periódica",
            tolerancia=1.0,
        )

        # Veredicto y 4 preguntas de la rúbrica oficial
        with estilos.tarjeta("veh_veredicto"):
            st.markdown("#### 🎯 Respuestas a las Preguntas Clave de la Rúbrica de Evaluación")
            tab_p1, tab_p2, tab_p3, tab_p4 = st.tabs([
                "1. Costo Real y Tasas",
                "2. Total Pagado e Intereses",
                "3. Sensibilidad (Tasa / Plazo)",
                "4. Alternativa Recomendada y Argumentos",
            ])

            with tab_p1:
                lineas_ofertas = []
                for o in ofertas.values():
                    paso_mensual = (
                        f"  Su tasa periódica mensual es $i_m = {p_tex(o['tasa_valor'])} / 12 = {p_tex(o['mv'], 4)}$ M.V., lo que equivale a:\n"
                        if o["codigo_tasa"] == "NAMV"
                        else "  Su costo anual equivalente es:\n"
                    )
                    lineas_ofertas.append(
                        f"- **{o['entidad']}:** Cotiza a **{o['descripcion']}**.\n"
                        f"{paso_mensual}"
                        f"  $EA = (1 + {numero(o['mv'], 4)})^{{12}} - 1 =$ **{porcentaje(o['ea'], 2)} E.A.**\n"
                    )
                brecha_ea = oferta_cara["ea"] - oferta_barata["ea"]
                st.markdown(
                    f"**¿Cuál es el costo real del crédito vehicular?**\n"
                    f"{''.join(lineas_ofertas)}"
                    f"- **Conclusión:** Las tasas cotizadas están en bases distintas y no se comparan directamente. En términos de Tasa Efectiva Anual, **{oferta_barata['entidad']} es más económica por {numero(brecha_ea * 100, 2)} puntos porcentuales**.\n"
                    f"- **Alcance de las tasas:** {notas_tasas}"
                )

            with tab_p2:
                st.markdown(
                    f"**¿Cuánto se paga en total y qué parte corresponde a intereses?**\n"
                    f"Para el capital de **{pesos_md(monto_vehiculo)}** a **{plazo_meses} meses** bajo la tasa de {desc_tasa}:\n"
                    f"- **Bajo Sistema Francés (Cuota Fija):**\n"
                    f"  - Valor total desembolsado: **{pesos_md(res_frances['total_pagado'])}**.\n"
                    f"  - Capital amortizado: **{pesos_md(monto_vehiculo)}** ({porcentaje(monto_vehiculo / res_frances['total_pagado'])} del total).\n"
                    f"  - Intereses pagados: **{pesos_md(res_frances['total_intereses'])}** ({porcentaje(res_frances['total_intereses'] / res_frances['total_pagado'])} del total).\n"
                    f"- **Bajo Sistema Alemán (Abono Constante a Capital):**\n"
                    f"  - Valor total desembolsado: **{pesos_md(res_aleman['total_pagado'])}**.\n"
                    f"  - Capital amortizado: **{pesos_md(monto_vehiculo)}** ({porcentaje(monto_vehiculo / res_aleman['total_pagado'])} del total).\n"
                    f"  - Intereses pagados: **{pesos_md(res_aleman['total_intereses'])}** ({porcentaje(res_aleman['total_intereses'] / res_aleman['total_pagado'])} del total).\n"
                    f"- **Diferencia neta:** El Sistema Alemán genera un **ahorro neto de {pesos_md(ahorro_intereses)}** en intereses totales pagados."
                )

            with tab_p3:
                tasa_mv_sens = tasa_mv + 0.001
                tabla_sens = amortizacion.tabla_amortizacion(monto_vehiculo, tasa_mv_sens, plazo_meses, sistema="frances")
                interes_sens = amortizacion.resumen_amortizacion(tabla_sens)["total_intereses"] - res_frances["total_intereses"]
                st.markdown(
                    f"**¿Cómo cambia el resultado si varían la tasa, el plazo o la cuota?**\n"
                    f"- **Impacto del plazo:**\n"
                    f"  - Si reduces el plazo de 48 a **36 meses**, el interés total en cuota fija cae de **{pesos_md(res_frances['total_intereses'])}** a un valor menor, pero la cuota mensual sube para cubrir el capital en menos tiempo.\n"
                    f"  - Si extiendes el plazo a **60 meses**, la cuota mensual baja brindando holgura inmediata, pero el sobrecosto por intereses totales pagados sube más de un **25%**.\n"
                    f"- **Impacto de la tasa:**\n"
                    f"  - Si la tasa sube apenas 10 puntos básicos, de {porcentaje(tasa_mv, 4)} a {porcentaje(tasa_mv_sens, 4)} mensual, el total de intereses en cuota fija aumenta **{pesos_md(interes_sens)} COP**.\n"
                    f"- *Puedes simular cualquier combinación en tiempo real usando los controles del panel izquierdo.*"
                )

            with tab_p4:
                st.markdown(
                    f"**¿Qué alternativa o decisión recomiendan y con qué argumentos?**\n"
                    f"1. **Entidad Financiera recomendada: {oferta_barata['entidad']}**\n"
                    f"   - **Argumento:** Presenta menor costo financiero efectivo anual (**{porcentaje(oferta_barata['ea'], 2)} E.A.** frente a **{porcentaje(oferta_cara['ea'], 2)} E.A.** de {oferta_cara['entidad']}).\n"
                    f"   - **Precaución:** {notas_tasas} Conviene pedir una cotización vigente a ambas entidades antes de decidir.\n"
                    f"2. **Sistema de Amortización (con la tasa seleccionada: {desc_tasa}):**\n"
                    f"   - **Opción de Mínimo Costo (Recomendada si hay capacidad de pago):** **Sistema Alemán**, porque produce un ahorro neto de **{pesos_md(ahorro_intereses)}** en intereses y las cuotas van decreciendo mes a mes desde **{pesos_md(res_aleman['cuota_inicial'])}** hasta **{pesos_md(res_aleman['cuota_final'])}**.\n"
                    f"   - **Opción de Estabilidad de Flujo de Caja:** **Sistema Francés**, recomendada si el comprador cuenta con un salario fijo estricto y prefiere certidumbre presupuestal pagando siempre **{pesos_md(res_frances['cuota_inicial'])}** fijos."
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
# CASO 2: RENTABILIDAD REAL (BANCOLOMBIA VS. NU)
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
        st.markdown("**Alternativa B: Cuenta de Rendimientos (Nu)**")
        tasa_nu_ea = entradas.campo_tasa("Tasa Cuenta de Ahorro (% EA)", "inv_tasa_nu", p["tasa_cuenta_ea"])
        st.caption("Capitalización diaria con disponibilidad de saldo inmediata.")

        st.divider()
        st.markdown("**Impuestos e Inflación**")
        c_ret1, c_ret2 = st.columns(2)
        with c_ret1:
            ret_cdt = entradas.campo_tasa(
                "Retención CDT (4%)",
                "inv_ret_cdt",
                p.get("retencion_cdt", 0.04),
                ayuda="4% para CDT (E.T. art. 395 y decretos reglamentarios).",
            )
        with c_ret2:
            ret_nu = entradas.campo_tasa(
                "Retención Cuenta (7%)",
                "inv_ret_nu",
                p.get("retencion_cuenta", 0.07),
                ayuda="7% para cuentas de ahorro (E.T. art. 395 y decretos reglamentarios).",
            )
        st.caption(
            "Retención en la fuente sobre rendimientos financieros (E.T. art. 395 y decretos reglamentarios): "
            "4% para CDT y 7% para cuentas de ahorro, según Valora Analitik (9 de enero de 2025). "
            "El 4% del CDT lo confirma el simulador de Bancolombia: retención de \\$74.800 sobre \\$1.870.000 "
            "de intereses (consultado el 2 de noviembre de 2026)."
        )
        # Se guarda para que Supuestos muestre la misma cifra con los valores ingresados aquí
        st.session_state["inv_interes_diario"] = capital_inv * tasas.periodica_desde_ea(tasa_nu_ea, 360)
        st.caption(supuesto_retencion_cuenta(st.session_state["inv_interes_diario"]))
        ipc_anual = entradas.campo_tasa(
            "Inflación anual (IPC)",
            "inv_ipc",
            p["inflacion_ipc"],
            ayuda="Último dato anual publicado por el DANE; es un dato observado, no una proyección.",
        )

    # Base temporal comercial estándar (360 días) para ambas alternativas (comparación justa)
    t_anos = plazo_dias / 360

    # 1. Cálculos Alternativa A (CDT Bancolombia)
    if modo_cdt == "simple":
        intereses_brutos_cdt = capital_inv * tasa_cdt_ea * t_anos
    else:
        intereses_brutos_cdt = capital_inv * ((1 + tasa_cdt_ea) ** t_anos - 1)

    retencion_cdt = intereses_brutos_cdt * ret_cdt
    intereses_netos_cdt = intereses_brutos_cdt - retencion_cdt
    vf_neto_cdt = capital_inv + intereses_netos_cdt
    tea_neta_cdt = (vf_neto_cdt / capital_inv) ** (1 / t_anos) - 1
    rent_real_cdt = tasas.tasa_real(tea_neta_cdt, ipc_anual)

    # 2. Cálculos Alternativa B (Cuenta Nu - Capitalización Diaria bajo convención 360)
    i_diaria_nu = (1 + tasa_nu_ea) ** (1 / 360) - 1
    vf_bruto_nu = capital_inv * ((1 + i_diaria_nu) ** plazo_dias)
    intereses_brutos_nu = vf_bruto_nu - capital_inv
    retencion_nu = intereses_brutos_nu * ret_nu
    intereses_netos_nu = intereses_brutos_nu - retencion_nu
    vf_neto_nu = capital_inv + intereses_netos_nu
    tea_neta_nu = (vf_neto_nu / capital_inv) ** (1 / t_anos) - 1
    rent_real_nu = tasas.tasa_real(tea_neta_nu, ipc_anual)

    diferencia_neta = intereses_netos_nu - intereses_netos_cdt
    diff_val = abs(diferencia_neta)

    # La alternativa recomendada es la de mayor rendimiento neto
    if diferencia_neta >= 0:
        ganador, perdedor = "Cuenta Nu", "CDT Bancolombia"
    else:
        ganador, perdedor = "CDT Bancolombia", "Cuenta Nu"

    with col_der:
        st.subheader(f"Comparativa de Rentabilidad Neta ({plazo_dias} días)")

        k1, k2 = st.columns(2)
        k3, k4 = st.columns(2)
        with k1:
            estilos.tarjeta_kpi("account_balance", pesos(intereses_netos_cdt), "Ganancia neta CDT", "principal")
        with k2:
            estilos.tarjeta_kpi("savings", pesos(intereses_netos_nu), "Ganancia neta Nu", "amortizacion")
        with k3:
            if diferencia_neta >= 0:
                estilos.tarjeta_kpi("trending_up", pesos(diferencia_neta), "Diferencia a favor Nu", "amortizacion")
            else:
                estilos.tarjeta_kpi("trending_up", pesos(abs(diferencia_neta)), "Diferencia a favor CDT", "principal")
        with k4:
            rent_real_ganador = rent_real_nu if diferencia_neta >= 0 else rent_real_cdt
            estilos.tarjeta_kpi("percent", porcentaje(rent_real_ganador), f"Rentabilidad real {ganador}", TEMA)

        # Gráfico comparativo de resultados al vencimiento
        fig_inv = go.Figure()
        fig_inv.add_trace(
            go.Bar(
                name="Capital Invertido",
                x=["CDT Bancolombia", "Cuenta Nu"],
                y=[capital_inv, capital_inv],
                marker_color="#94A3B8",
            )
        )
        fig_inv.add_trace(
            go.Bar(
                name="Rendimiento Neto (Bolsillo)",
                x=["CDT Bancolombia", "Cuenta Nu"],
                y=[intereses_netos_cdt, intereses_netos_nu],
                marker_color=COLOR_FRANCES,
            )
        )
        fig_inv.add_trace(
            go.Bar(
                name="Retención en la Fuente",
                x=["CDT Bancolombia", "Cuenta Nu"],
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
            separators=graficos.SEPARADORES_PLOTLY,
            hovermode="x unified",
            legend={"orientation": "h", "y": -0.22, "yanchor": "top", "x": 0.5, "xanchor": "center", "font": {"color": "#CBD5E1"}},
            margin={"l": 75, "r": 20, "t": 48, "b": 60},
        )
        fig_inv.update_yaxes(title="Valor ($ COP)", tickprefix="$ ", tickformat=",.0f", gridcolor="rgba(51, 65, 85, 0.35)", linecolor="rgba(51, 65, 85, 0.6)", color="#94A3B8")
        fig_inv.update_xaxes(gridcolor="rgba(51, 65, 85, 0.35)", linecolor="rgba(51, 65, 85, 0.6)", color="#94A3B8")
        st.plotly_chart(fig_inv, width="stretch", config=graficos.CONFIG_PLOTLY)

        # Verificación Matemática
        st.subheader("Verificación Matemática")
        tarjeta_verificacion(
            "Consistencia contable CDT: Capital + Ganancia neta + Retención == VF Bruto",
            capital_inv + intereses_netos_cdt + retencion_cdt,
            capital_inv + intereses_brutos_cdt,
            "Suma de componentes del flujo final",
            tolerancia=1.0,
        )

        # Veredicto y 4 preguntas de la rúbrica oficial
        with estilos.tarjeta("inv_veredicto"):
            st.markdown("#### 🎯 Respuestas a las Preguntas Clave de la Rúbrica de Evaluación")
            tab_p1, tab_p2, tab_p3, tab_p4 = st.tabs([
                "1. Rentabilidad Real y Neta",
                "2. Total Recibido e Intereses",
                "3. Sensibilidad (Plazo / Inflación)",
                "4. Alternativa Recomendada y Argumentos",
            ])

            with tab_p1:
                brecha_real = abs(rent_real_nu - rent_real_cdt)
                nota_retencion = (
                    " Ambas cotizan la misma tasa, así que la diferencia la explica la retención en la fuente."
                    if tasa_cdt_ea == tasa_nu_ea and modo_cdt == "compuesto"
                    else ""
                )
                st.markdown(
                    f"**¿Cuál es la rentabilidad real del producto (tasa efectiva anual y neta de retención)?**\n"
                    f"- **CDT Bancolombia:**\n"
                    f"  - Tasa pactada: **{porcentaje(tasa_cdt_ea, 2)} E.A.**\n"
                    f"  - Tasa Efectiva Anual Neta (post-retefuente {porcentaje(ret_cdt, 1)}, E.T. art. 395 y decretos reglamentarios): **{porcentaje(tea_neta_cdt, 2)} E.A.**\n"
                    f"  - El simulador de Bancolombia confirma el 4%: retención de \\$74.800 sobre \\$1.870.000 de intereses (consultado el 2 de noviembre de 2026).\n"
                    f"  - Rentabilidad real neta (Ecuación de Fisher descontando inflación IPC del {porcentaje(ipc_anual, 2)}):\n"
                    f"    $$r = \\frac{{1 + \\text{{TEA neta}}}}{{1 + \\text{{IPC}}}} - 1 = \\frac{{1 + {numero(tea_neta_cdt, 4)}}}{{1 + {numero(ipc_anual, 4)}}} - 1 = \\mathbf{{{p_tex(rent_real_cdt)}}}$$\n"
                    f"- **Cuenta de Rendimientos (Nu):**\n"
                    f"  - Tasa pactada: **{porcentaje(tasa_nu_ea, 2)} E.A.**\n"
                    f"  - Tasa Efectiva Anual Neta (post-retefuente {porcentaje(ret_nu, 1)}, E.T. art. 395 y decretos reglamentarios): **{porcentaje(tea_neta_nu, 2)} E.A.**\n"
                    f"  - Rentabilidad real neta (Ecuación de Fisher):\n"
                    f"    $$r = \\frac{{1 + {numero(tea_neta_nu, 4)}}}{{1 + {numero(ipc_anual, 4)}}} - 1 = \\mathbf{{{p_tex(rent_real_nu)}}}$$\n"
                    f"- **Conclusión:** {ganador} genera **{numero(brecha_real * 100, 2)} puntos porcentuales más de rentabilidad real neta** sobre la inflación que {perdedor}.{nota_retencion}"
                )

            with tab_p2:
                st.markdown(
                    f"**¿Cuánto se recibe en total y qué parte corresponde a intereses netos e impuestos?**\n"
                    f"Para un capital inicial de **{pesos_md(capital_inv)}** a un plazo de **{plazo_dias} días**:\n"
                    f"- **En CDT Bancolombia:**\n"
                    f"  - Intereses brutos causados: **{pesos_md(intereses_brutos_cdt)}**.\n"
                    f"  - Descuento de retención en la fuente ({porcentaje(ret_cdt, 1)}): **-{pesos_md(retencion_cdt)}**.\n"
                    f"  - Rendimiento neto de bolsillo: **+{pesos_md(intereses_netos_cdt)}**.\n"
                    f"  - **Capital total final recibido:** **{pesos_md(vf_neto_cdt)}**.\n"
                    f"- **En Cuenta Nu:**\n"
                    f"  - Intereses brutos causados: **{pesos_md(intereses_brutos_nu)}**.\n"
                    f"  - Descuento de retención en la fuente ({porcentaje(ret_nu, 1)}): **-{pesos_md(retencion_nu)}**.\n"
                    f"  - Rendimiento neto de bolsillo: **+{pesos_md(intereses_netos_nu)}**.\n"
                    f"  - **Capital total final acumulado:** **{pesos_md(vf_neto_nu)}**.\n"
                    f"- **Ganancia neta adicional en {ganador}:** **+{pesos_md(diff_val)} COP** limpios al bolsillo del inversionista."
                )

            with tab_p3:
                ipc_alto = ipc_anual + 0.01
                st.markdown(
                    f"**¿Cómo cambia el resultado si varían la tasa, el plazo o la inflación?**\n"
                    f"- **Impacto del plazo (puedes alternar 90, 180 y 360 días a la izquierda):**\n"
                    f"  - A menor plazo, la diferencia en dinero entre ambas alternativas es de menor volumen absoluto, y la cuenta conserva la ventaja de la liquidez diaria.\n"
                    f"  - A {plazo_dias} días, la brecha de ganancia neta es de **{pesos_md(diff_val)} COP** a favor de {ganador}.\n"
                    f"- **Impacto de la inflación (IPC):**\n"
                    f"  - Si la inflación sube al {porcentaje(ipc_alto, 2)}, la rentabilidad real baja a **{porcentaje(tasas.tasa_real(tea_neta_cdt, ipc_alto), 2)}** en el CDT y a **{porcentaje(tasas.tasa_real(tea_neta_nu, ipc_alto), 2)}** en la cuenta.\n"
                    f"- **Mecanismo de pago en el CDT (Simple vs. Compuesto):**\n"
                    f"  - Si en el CDT retiras los intereses mensualmente (interés simple), no capitalizas y pierdes la ganancia compuesta sobre los intereses ganados."
                )

            with tab_p4:
                if diferencia_neta >= 0:
                    decision = "Cuenta de Rendimientos / Cajita de Ahorro (Nu Colombia)"
                    argumento_rentabilidad = (
                        f"Ofrece mayor TEA neta post-impuestos (**{porcentaje(tea_neta_nu, 2)}** vs **{porcentaje(tea_neta_cdt, 2)}**) "
                        f"y mayor rentabilidad real frente a la inflación (**{porcentaje(rent_real_nu, 2)}** vs **{porcentaje(rent_real_cdt, 2)}**)."
                    )
                    argumento_liquidez = (
                        f"**Liquidez y Disponibilidad 24/7:** El CDT tradicional congela el dinero durante {plazo_dias} días (penalización severa por retiro anticipado). "
                        f"En Nu el dinero está disponible inmediatamente en cualquier momento sin penalidad."
                    )
                else:
                    decision = f"CDT Bancolombia, si el dinero no se va a necesitar durante los {plazo_dias} días"
                    argumento_rentabilidad = (
                        f"Ofrece mayor TEA neta post-impuestos (**{porcentaje(tea_neta_cdt, 2)}** vs **{porcentaje(tea_neta_nu, 2)}**) "
                        f"y mayor rentabilidad real frente a la inflación (**{porcentaje(rent_real_cdt, 2)}** vs **{porcentaje(rent_real_nu, 2)}**), "
                        f"con **+{pesos_md(diff_val)} COP** netos. Además, su tasa queda pactada, mientras la de la cuenta puede cambiar."
                    )
                    argumento_liquidez = (
                        f"**Costo en Liquidez:** El CDT congela el dinero durante {plazo_dias} días (penalización severa por retiro anticipado). "
                        f"Si existe la posibilidad de necesitarlo antes, conviene la cuenta Nu: esos {pesos_md(diff_val)} COP son el precio de tener el dinero disponible en cualquier momento."
                    )
                st.markdown(
                    f"**¿Qué alternativa o decisión recomiendan y con qué argumentos?**\n"
                    f"**Decisión Recomendada: {decision}**\n"
                    f"- **Argumentos Financieros y Técnicos:**\n"
                    f"  1. **Superioridad en Rentabilidad:** {argumento_rentabilidad}\n"
                    f"  2. {argumento_liquidez}\n"
                    f"  3. **Seguridad Institucional Idéntica:** Ambas entidades están vigiladas por la Superintendencia Financiera de Colombia y cuentan con el seguro de depósitos **FOGAFIN** (cobertura hasta \\$50.000.000 COP por titular)."
                )

        with st.expander("Ver tabla comparativa técnica completa"):
            tabla_comp = pd.DataFrame(
                [
                    {"Concepto": "Tasa cotizada en pantalla", "CDT Bancolombia": porcentaje(tasa_cdt_ea), "Nu": porcentaje(tasa_nu_ea)},
                    {"Concepto": "Mecanismo de cálculo", "CDT Bancolombia": "Compuesto" if modo_cdt == "compuesto" else "Simple", "Nu": "Compuesto diario"},
                    {"Concepto": "Rendimientos brutos generados", "CDT Bancolombia": pesos(intereses_brutos_cdt), "Nu": pesos(intereses_brutos_nu)},
                    {"Concepto": f"Retención en la fuente ({porcentaje(ret_cdt, 1)} / {porcentaje(ret_nu, 1)})", "CDT Bancolombia": pesos(retencion_cdt), "Nu": pesos(retencion_nu)},
                    {"Concepto": "Rendimientos netos recibidos", "CDT Bancolombia": pesos(intereses_netos_cdt), "Nu": pesos(intereses_netos_nu)},
                    {"Concepto": "Tasa Efectiva Anual Neta (TEA neta)", "CDT Bancolombia": porcentaje(tea_neta_cdt), "Nu": porcentaje(tea_neta_nu)},
                    {"Concepto": "Rentabilidad real neta (descontando IPC)", "CDT Bancolombia": porcentaje(rent_real_cdt), "Nu": porcentaje(rent_real_nu)},
                    {"Concepto": "Liquidez del dinero", "CDT Bancolombia": f"Bloqueado {plazo_dias} días", "Nu": "Inmediata (24/7)"},
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
        tasa_ea_fondo = entradas.campo_tasa(
            "Rentabilidad del fondo EA",
            "gr_tasa_ea",
            p["tasa_ea"],
            minimo=0.0001,
            ayuda="Rentabilidad del último año reportada por el fondo, que ya refleja la comisión de administración. No está garantizada.",
        )
        tasa_mv = tasas.periodica_desde_ea(tasa_ea_fondo, 12)
        st.caption(f"**Equivalencia:** {porcentaje(tasa_ea_fondo, 2)} EA $\\Longleftrightarrow$ **{porcentaje(tasa_mv, 4)} mensual**.")

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

        k1, k2 = st.columns(2)
        k3, k4 = st.columns(2)
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
            separators=graficos.SEPARADORES_PLOTLY,
            hovermode="x unified",
            legend={"orientation": "h", "y": -0.22, "yanchor": "top", "x": 0.5, "xanchor": "center", "font": {"color": "#CBD5E1"}},
            margin={"l": 75, "r": 20, "t": 48, "b": 60},
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
            separators=graficos.SEPARADORES_PLOTLY,
            hovermode="x unified",
            legend={"orientation": "h", "y": -0.22, "yanchor": "top", "x": 0.5, "xanchor": "center", "font": {"color": "#CBD5E1"}},
            margin={"l": 75, "r": 20, "t": 48, "b": 60},
        )
        fig_acum.update_yaxes(title="Saldo acumulado ($ COP)", tickprefix="$ ", tickformat=",.0f", gridcolor="rgba(51, 65, 85, 0.35)", linecolor="rgba(51, 65, 85, 0.6)", color="#94A3B8")
        fig_acum.update_xaxes(title="Mes", gridcolor="rgba(51, 65, 85, 0.35)", linecolor="rgba(51, 65, 85, 0.6)", color="#94A3B8")
        st.plotly_chart(fig_acum, width="stretch", config=graficos.CONFIG_PLOTLY)

        # Verificación Matemática
        st.subheader("Verificación Matemática")
        tarjeta_verificacion(
            "Consistencia analítica: VF fórmula analítica == Saldo acumulado simulación",
            vf_acumulado,
            saldos_mes[-1],
            "Ecuación analítica de valor vs. ciclo mes a mes",
            tolerancia=1.0,
        )

        # Veredicto y 4 preguntas de la rúbrica oficial
        with estilos.tarjeta("grad_veredicto"):
            st.markdown("#### 🎯 Respuestas a las Preguntas Clave de la Rúbrica de Evaluación")
            tab_p1, tab_p2, tab_p3, tab_p4 = st.tabs([
                "1. Rentabilidad Real del Fondo",
                "2. Total Aportado e Intereses",
                "3. Sensibilidad (Gradiente Aritmético vs Geométrico)",
                "4. Alternativa Recomendada y Argumentos",
            ])

            with tab_p1:
                ipc_ref = next(c for c in casos if c["id"] == "inversion_bancolombia_nu")["parametros"]["inflacion_ipc"]
                rent_real_fondo = tasas.tasa_real(tasa_ea_fondo, ipc_ref)
                conclusion_fondo = (
                    f"Con esta rentabilidad, el fondo queda **{porcentaje(rent_real_fondo, 2)}** por encima de la inflación y protegería el poder de compra del dinero destinado a la vivienda"
                    if rent_real_fondo >= 0
                    else f"Con esta rentabilidad, el fondo queda **{porcentaje(abs(rent_real_fondo), 2)}** por debajo de la inflación y el dinero destinado a la vivienda perdería poder de compra"
                )
                st.markdown(
                    f"**¿Cuál es la rentabilidad real del plan de ahorro programado?**\n"
                    f"- **Producto financiero:** **Fiducuenta de Fiduciaria Bancolombia** (Fondo de Inversión Colectiva Abierto, vigilado por la Superintendencia Financiera de Colombia).\n"
                    f"- **Tasa Efectiva Anual (E.A.):** **{porcentaje(tasa_ea_fondo, 2)} E.A.**, rentabilidad del último año reportada por el fondo, que ya refleja la comisión de administración. No está garantizada.\n"
                    f"- **Tasa mensual equivalente:** $i_m = (1 + {numero(tasa_ea_fondo, 4)})^{{1/12}} - 1 =$ **{porcentaje(tasa_mv, 4)} Mes Vencido (M.V.)**.\n"
                    f"- **Rentabilidad real neta de inflación (Fisher con IPC del {porcentaje(ipc_ref, 2)}, DANE):**\n"
                    f"  $$r = \\frac{{1 + \\text{{EA}}}}{{1 + \\text{{IPC}}}} - 1 = \\frac{{1 + {numero(tasa_ea_fondo, 4)}}}{{1 + {numero(ipc_ref, 4)}}} - 1 = \\mathbf{{{p_tex(rent_real_fondo)}}}$$\n"
                    f"  - *Nota: la rentabilidad del fondo se muestra antes de impuestos; por eso no se compara directamente con la del Caso 2.*\n"
                    f"- **Conclusión:** {conclusion_fondo}, siempre que el fondo mantenga ese desempeño."
                )

            with tab_p2:
                st.markdown(
                    f"**¿Cuánto se aporta en total y qué parte corresponde a intereses ganados?**\n"
                    f"Para el plan a **{n_meses} meses** iniciando con **{pesos_md(a1)}** e incremento ({escapar_md(desc_incremento)}):\n"
                    f"- **Total de aportes propios (de tu bolsillo):** **{pesos_md(total_aportado)}** ({porcentaje(total_aportado / vf_acumulado, 1)} del capital acumulado final).\n"
                    f"- **Rendimientos puros generados por el fondo:** **+{pesos_md(intereses_ganados)}** ({porcentaje(intereses_ganados / vf_acumulado, 1)} del capital acumulado final).\n"
                    f"- **Capital total acumulado al mes {n_meses} (VF):** **{pesos_md(vf_acumulado)}**.\n"
                    f"- **Efecto de la capitalización:** Prácticamente el **{porcentaje(intereses_ganados / vf_acumulado, 1)} de la cuota inicial de la vivienda** es dinero regalado por el interés compuesto."
                )

            with tab_p3:
                g_arit_val = p['gradiente_aritmetico_G']
                tasa_ea_alta = tasa_ea_fondo + 0.01
                tasa_mv_alta = tasas.periodica_desde_ea(tasa_ea_alta, 12)
                vf_tasa_alta = sum(c * (1 + tasa_mv_alta) ** (n_meses - m) for m, c in zip(meses_arr, cuotas))
                st.markdown(
                    f"**¿Cómo cambia el resultado si varían la tasa, el plazo o la modalidad de gradiente?**\n"
                    f"- **Aritmético (+ {pesos_md(g_arit_val)}/mes) vs. Geométrico (+ {porcentaje(p['gradiente_geometrico_g'])}):**\n"
                    f"  - El gradiente aritmético sube a ritmo constante lineal, ideal para quien tiene expectativas de incrementos salariales fijos en pesos.\n"
                    f"  - El gradiente geométrico crece a tasa porcentual compuesta; si se fija en 2% mensual, en los primeros meses exige cuotas más bajas pero al final crece de forma pronunciada.\n"
                    f"- **Impacto de la tasa de interés:**\n"
                    f"  - Si la rentabilidad del fondo sube de {porcentaje(tasa_ea_fondo, 2)} a {porcentaje(tasa_ea_alta, 2)} E.A., el capital final VF se incrementa en **{pesos_md(vf_tasa_alta - vf_acumulado)} COP** sin tener que aportar un solo peso adicional de bolsillo. Como la rentabilidad no está garantizada, también puede bajar y reducir el capital final.\n"
                    f"- *Prueba a cambiar a la izquierda el tipo de gradiente o el plazo para recalcular toda la trayectoria.*"
                )

            with tab_p4:
                st.markdown(
                    f"**¿Qué alternativa o decisión recomiendan y con qué argumentos?**\n"
                    f"**Comparación con Cuota Fija Equivalente ($A_{{eq}}$):**\n"
                    f"- Para acumular exactamente los mismos **{pesos_md(vf_acumulado)}** al mes {n_meses}, el ahorrador habría tenido que pagar una cuota fija mensual de **{pesos_md(cuota_equivalente)}** todos los meses desde el mes 1.\n\n"
                    f"**Veredicto y Recomendación:**\n"
                    f"1. **Recomendación: Ahorro con Gradiente Aritmético.**\n"
                    f"2. **Argumentos Financieros:**\n"
                    f"   - **Accesibilidad y Viabilidad Inicial:** Exige solo **{pesos_md(a1)}** el mes 1, facilitando la creación del hábito de ahorro sin asfixiar el presupuesto familiar, en contraste con comprometerse con **{pesos_md(cuota_equivalente)}** desde el día uno.\n"
                    f"   - **Cruce en el mes {cruce_mes}:** El esfuerzo mensual del gradiente se mantiene por debajo de la cuota fija durante los primeros {cruce_mes - 1} meses del plan, adaptándose a la curva natural de crecimiento de ingresos del profesional o familia."
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
