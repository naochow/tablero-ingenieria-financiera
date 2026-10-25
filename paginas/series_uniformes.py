"""Página de series uniformes: cuota, VP y VF para series vencidas y anticipadas."""

import numpy_financial as npf
import streamlit as st

from componentes import entradas, estilos, graficos
from componentes.formato import numero, pesos, porcentaje
from componentes.verificacion import tarjeta_verificacion
from finanzas import series, tasas

TEMA = "series_uniformes"
COLOR = estilos.TEMAS[TEMA]["color"]
COLOR_APORTES = estilos.TEMAS[TEMA]["oscuro"]  # se distingue mejor del ámbar de intereses

CONOCIDOS = {"cuota": "Cuota (A)", "vp": "Valor presente (VP)", "vf": "Valor futuro (VF)"}
PERIODO = {"diaria": "día", "mensual": "mes", "bimestral": "bimestre",
           "trimestral": "trimestre", "semestral": "semestre", "anual": "año"}
MODALIDADES_SERIE = {"vencida": "Vencida", "anticipada": "Anticipada"}

EJEMPLOS = {
    "Excel: $250.000 al 1%, 36 cuotas": {
        "su_conocido": "cuota", "su_valor": 250_000, "su_tasa": 0.01, "su_tipo": "periodica",
        "su_periodicidad": "mensual", "su_modalidad": "vencida", "su_periodicidad_flujo": "mensual", "su_n": 36,
    },
    "Excel anticipada: $150.000 al 1,5%, 11": {
        "su_conocido": "cuota", "su_valor": 150_000, "su_tasa": 0.015, "su_tipo": "periodica",
        "su_periodicidad": "mensual", "su_modalidad": "vencida", "su_periodicidad_flujo": "mensual", "su_n": 11,
        "su_ver": "anticipada",
    },
    "Meta de $30.000.000 en 3 años al 10% EA": {
        "su_conocido": "vf", "su_valor": 30_000_000, "su_tasa": 0.10, "su_tipo": "efectiva",
        "su_modalidad": "vencida", "su_periodicidad_flujo": "mensual", "su_n": 36,
    },
}

explicar = estilos.encabezado(
    TEMA,
    "Series uniformes",
    "Pagos o aportes iguales cada periodo: vencidos (al final) o anticipados (al inicio).",
)
entradas.botones_ejemplos(EJEMPLOS)

col_datos, col_resultados = st.columns([1, 2], gap="large")

with col_datos, estilos.tarjeta("su_datos"):
    st.subheader("Datos")
    conocido = entradas.campo_opcion("¿Qué conoces?", list(CONOCIDOS), "su_conocido", "cuota", CONOCIDOS)
    valor = entradas.campo_dinero(CONOCIDOS[conocido], "su_valor", 250_000, minimo=1)
    ea, descripcion_tasa = entradas.selector_tasa("su", 0.01)
    periodicidad_flujo = entradas.campo_lista(
        "Periodicidad de las cuotas", list(entradas.PERIODICIDADES), "su_periodicidad_flujo", "mensual",
        entradas.PERIODICIDADES,
    )
    n = int(entradas.campo_numero("Número de cuotas (n)", "su_n", 36))

# La tasa se lleva a la periodicidad de las cuotas pasando por la EA
i = tasas.periodica_desde_ea(ea, tasas.PERIODOS_POR_ANO[periodicidad_flujo])
periodo = PERIODO[periodicidad_flujo]
resultados = {m: series.resolver_serie(conocido, valor, i, n, m == "anticipada") for m in MODALIDADES_SERIE}

with col_resultados:
    st.caption(
        f"Tasa ingresada: {descripcion_tasa} = {porcentaje(ea, 4)} EA → "
        f"**{porcentaje(i, 4)} por {periodo}** (periódica vencida de las cuotas)."
    )
    for modalidad, r in resultados.items():
        st.markdown(f"**{MODALIDADES_SERIE[modalidad]}** · cuotas al {'final' if modalidad == 'vencida' else 'inicio'} de cada {periodo}")
        k1, k2, k3, k4 = st.columns(4)
        with k1:
            estilos.tarjeta_kpi("payments", pesos(r["cuota"]), "Cuota (A)", TEMA)
        with k2:
            estilos.tarjeta_kpi("first_page", pesos(r["vp"]), "Valor presente (VP)", TEMA)
        with k3:
            estilos.tarjeta_kpi("last_page", pesos(r["vf"]), "Valor futuro (VF)", TEMA)
        with k4:
            estilos.tarjeta_kpi("savings", pesos(r["vf"] - r["cuota"] * n), "Intereses (VF − aportes)", "intereses")

    if explicar:
        v, a = resultados["vencida"], resultados["anticipada"]
        st.info(
            f"Son **{n} cuotas** de un {periodo} cada una, con una tasa de **{porcentaje(i, 4)} por {periodo}**. "
            f"Si pagas o ahorras **{pesos(v['cuota'])}** al final de cada {periodo}, eso equivale a tener "
            f"**{pesos(v['vp'])}** hoy o **{pesos(v['vf'])}** al final. "
            f"Si la cuota se paga al inicio (anticipada), cada pago gana un {periodo} más de intereses: "
            f"con {CONOCIDOS[conocido].lower()} de {pesos(valor)}, la cuota anticipada es **{pesos(a['cuota'])}** "
            f"y el VP **{pesos(a['vp'])}**."
        )

st.subheader("Gráficos")
ver = entradas.campo_opcion("Modalidad en los gráficos", list(MODALIDADES_SERIE), "su_ver", "vencida", MODALIDADES_SERIE)
anticipada = ver == "anticipada"
r = resultados[ver]
col_flujo, col_acumulado = st.columns(2, gap="large")

with col_flujo:
    periodos_pago = list(range(0, n)) if anticipada else list(range(1, n + 1))
    fig = graficos.grafico_barras(
        periodos_pago,
        [{"nombre": "Cuota", "y": [r["cuota"]] * n, "color": COLOR}],
        f"Diagrama de flujo de caja · serie {ver}",
        f"Periodo ({periodo})",
        "Cuota",
    )
    fig.update_xaxes(range=[-0.8, n + 0.8])
    fig.add_annotation(x=0, y=r["cuota"], text=f"VP {pesos(r['vp'])}", showarrow=True, arrowhead=2, ay=-40)
    fig.add_annotation(x=n, y=r["cuota"], text=f"VF {pesos(r['vf'])}", showarrow=True, arrowhead=2, ay=-40)
    st.plotly_chart(fig, width="stretch", config=graficos.CONFIG_PLOTLY)

with col_acumulado:
    periodos, aportes, saldos = series.acumulado_serie(r["cuota"], i, n, anticipada)
    fig = graficos.grafico_barras(
        periodos,
        [
            {"nombre": "Aportes acumulados", "y": aportes, "color": COLOR_APORTES},
            {"nombre": "Intereses acumulados", "y": [s - a for s, a in zip(saldos, aportes)], "color": estilos.INTERESES},
        ],
        "Valor acumulado: aportes contra intereses",
        f"Periodo ({periodo})",
        "Saldo",
        apiladas=True,
    )
    st.plotly_chart(fig, width="stretch", config=graficos.CONFIG_PLOTLY)

st.subheader("Verificación")
v, a = resultados["vencida"], resultados["anticipada"]
tarjeta_verificacion("VP vencida: fórmula contra descuento cuota por cuota", v["vp"],
                     series.vp_flujo([v["cuota"]] * n, i), f"Suma de {n} cuotas descontadas")
tarjeta_verificacion("VP anticipada: fórmula contra numpy-financial", a["vp"],
                     npf.pv(i, n, -a["cuota"], when="begin"), "npf.pv(when='begin')")
tarjeta_verificacion("Cuota vencida: fórmula contra numpy-financial", v["cuota"],
                     npf.pmt(i, n, -v["vp"]), "npf.pmt")
tarjeta_verificacion("Cuota anticipada: fórmula contra numpy-financial", a["cuota"],
                     npf.pmt(i, n, -a["vp"], when="begin"), "npf.pmt(when='begin')")

with st.expander("Fórmulas usadas"):
    st.latex(r"a_{\overline{n}|i} = \frac{1 - (1 + i)^{-n}}{i} \qquad s_{\overline{n}|i} = \frac{(1 + i)^n - 1}{i}")
    st.latex(r"VP = A \cdot a \qquad VF = A \cdot s \qquad A = \frac{VP}{a} = \frac{VF}{s}")
    st.latex(r"\text{Anticipada: } VP_a = A \cdot a \cdot (1 + i) \qquad VF_a = A \cdot s \cdot (1 + i)")
    st.latex(r"i = (1 + EA)^{1/m} - 1")
    st.caption(f"Con los datos actuales: i = {porcentaje(i, 4)}, n = {numero(n)}.")
