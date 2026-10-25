"""Página de interés compuesto: VF, VP, despejes, comparación con simple y frecuencias."""

import numpy_financial as npf
import pandas as pd
import streamlit as st

from componentes import entradas, estilos, graficos
from componentes.formato import numero, pesos, porcentaje
from componentes.verificacion import tarjeta_verificacion
from finanzas import interes, tasas

TEMA = "interes_compuesto"
COLOR = estilos.TEMAS[TEMA]["color"]
COLOR_SIMPLE = estilos.TEMAS["interes_simple"]["color"]

PERIODICIDADES = {p: p.capitalize() for p in tasas.PERIODOS_POR_ANO}
PERIODO = {"diaria": "días", "mensual": "meses", "bimestral": "bimestres",
           "trimestral": "trimestres", "semestral": "semestres", "anual": "años"}

EJEMPLOS = {
    "Excel de clase: 1,5% mensual, 30 meses": {
        "ic_capital": 4_000_000, "ic_tasa": 0.015, "ic_periodicidad": "mensual", "ic_n": 30,
    },
    "Ahorro a 10 años al 10% anual": {
        "ic_capital": 5_000_000, "ic_tasa": 0.10, "ic_periodicidad": "anual", "ic_n": 10,
    },
    "Deuda de tarjeta al 2,1% mensual": {
        "ic_capital": 1_000_000, "ic_tasa": 0.021, "ic_periodicidad": "mensual", "ic_n": 12,
    },
}

explicar = estilos.encabezado(
    TEMA,
    "Interés compuesto",
    "Los intereses de cada periodo se suman al capital y también generan intereses.",
)
entradas.botones_ejemplos(EJEMPLOS)

col_datos, col_resultados = st.columns([1, 2], gap="large")

with col_datos, estilos.tarjeta("ic_datos"):
    st.subheader("Datos")
    capital = entradas.campo_dinero("Capital (P)", "ic_capital", 4_000_000, minimo=1)
    periodicidad = entradas.campo_opcion(
        "Periodicidad de la tasa", list(PERIODICIDADES), "ic_periodicidad", "mensual", PERIODICIDADES
    )
    tasa = entradas.campo_tasa("Tasa periódica (i)", "ic_tasa", 0.015, minimo=0.0001)
    n = entradas.campo_numero(f"Número de periodos (n, en {PERIODO[periodicidad]})", "ic_n", 30)

vf = interes.vf_compuesto(capital, tasa, n)
intereses = vf - capital
vf_simple = interes.vf_simple(capital, tasa, n)
diferencia = vf - vf_simple
duplicar = interes.tiempo_duplicar(tasa)
ea = tasas.ea_desde_periodica(tasa, tasas.PERIODOS_POR_ANO[periodicidad])
periodo = PERIODO[periodicidad]

periodos, saldos = interes.acumulado_compuesto(capital, tasa, n)
_, saldos_simple = interes.acumulado_simple(capital, tasa, n)

with col_resultados:
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        estilos.tarjeta_kpi("account_balance_wallet", pesos(vf), "Valor futuro (VF)", TEMA)
    with k2:
        estilos.tarjeta_kpi("savings", pesos(intereses), "Intereses ganados", "intereses")
    with k3:
        estilos.tarjeta_kpi("timer", f"{numero(duplicar, 1)} {periodo}", "Tiempo para duplicar", TEMA)
    with k4:
        estilos.tarjeta_kpi("compare_arrows", pesos(diferencia), "Ventaja frente a simple", TEMA)
    st.caption(f"Tasa equivalente: {porcentaje(ea)} EA.")

    if explicar:
        st.info(
            f"Inviertes **{pesos(capital)}** al **{porcentaje(tasa)} {periodicidad}** durante "
            f"**{numero(n, 0 if n == int(n) else 2)} {periodo}**. Cada periodo los intereses se suman al "
            f"saldo, así que el siguiente periodo ganas intereses sobre un valor más grande. "
            f"Terminas con **{pesos(vf)}**: **{pesos(diferencia)}** más que con interés simple a la "
            f"misma tasa. A este ritmo tu dinero se duplica en unos **{numero(duplicar, 1)} {periodo}**."
        )

    fig = graficos.grafico_lineas(
        periodos,
        [
            {"nombre": "Compuesto", "y": saldos, "color": COLOR},
            {"nombre": "Simple", "y": saldos_simple, "color": COLOR_SIMPLE, "punteada": True},
        ],
        f"Interés compuesto contra simple · diferencia al final: {pesos(diferencia)}",
        f"Periodos ({periodo})",
        "Saldo",
    )
    st.plotly_chart(fig, width="stretch", config=graficos.CONFIG_PLOTLY)

st.subheader("Despejes")
tab_vp, tab_tasa, tab_n = st.tabs(["Valor presente (VP)", "Tasa (i)", "Número de periodos (n)"])

with tab_vp:
    st.caption("¿Cuánto hay que invertir hoy para tener un valor futuro, con la tasa y n de arriba?")
    vf_meta = entradas.campo_dinero("Valor futuro que quieres tener", valor_inicial=round(vf))
    st.metric("Valor presente", pesos(interes.vp_compuesto(vf_meta, tasa, n)))

with tab_tasa:
    st.caption("¿Qué tasa periódica convierte un VP en un VF en los n periodos de arriba?")
    c1, c2 = st.columns(2)
    with c1:
        vp_t = entradas.campo_dinero("Valor presente (inversión)", valor_inicial=capital, minimo=1)
    with c2:
        vf_t = entradas.campo_dinero("Valor futuro (lo que recibes)", valor_inicial=round(vf), minimo=1)
    tasa_despejada = interes.tasa_compuesta(vp_t, vf_t, n)
    ea_despejada = tasas.ea_desde_periodica(tasa_despejada, tasas.PERIODOS_POR_ANO[periodicidad])
    st.metric("Tasa periódica", f"{porcentaje(tasa_despejada, 4)} {periodicidad} · {porcentaje(ea_despejada)} EA")

with tab_n:
    st.caption("¿Cuántos periodos tarda un VP en convertirse en un VF con la tasa de arriba?")
    c1, c2 = st.columns(2)
    with c1:
        vp_n = entradas.campo_dinero("Capital inicial", valor_inicial=capital, minimo=1)
    with c2:
        vf_n = entradas.campo_dinero("Valor futuro deseado", valor_inicial=round(vf), minimo=1)
    st.metric("Número de periodos", f"{numero(interes.periodos_compuesto(vp_n, vf_n, tasa), 2)} {periodo}")
    if vf_n < vp_n:
        st.warning("El valor futuro es menor que el capital: n resulta negativo.")

st.subheader("Frecuencia de capitalización")
st.caption("La misma tasa nominal anual rinde más entre más veces al año se capitaliza.")
c1, c2 = st.columns(2)
with c1:
    nominal = entradas.campo_tasa("Tasa nominal anual", "ic_nominal", 0.18, minimo=0.0001)
with c2:
    anos = entradas.campo_numero("Plazo (años)", "ic_anos", 1)
filas = interes.tabla_frecuencias(capital, nominal, anos)
tabla = pd.DataFrame(
    {
        "Capitalización": [f["frecuencia"].capitalize() for f in filas],
        "Periodos por año": [f["periodos_por_ano"] for f in filas],
        "Tasa periódica": [porcentaje(f["tasa_periodica"], 4) for f in filas],
        "Tasa EA": [porcentaje(f["ea"], 4) for f in filas],
        "Valor futuro": [pesos(f["valor_futuro"]) for f in filas],
        "Intereses": [pesos(f["intereses"]) for f in filas],
    }
)
st.dataframe(tabla, hide_index=True, width="stretch")

st.subheader("Verificación")
tarjeta_verificacion("VF: fórmula contra capitalización periodo a periodo", vf, saldos[-1], "Iterativo")
tarjeta_verificacion("VF: fórmula contra numpy-financial", vf, npf.fv(tasa, n, 0, -capital), "npf.fv")

with st.expander("Fórmulas usadas"):
    st.latex(r"VF = P\,(1 + i)^n \qquad VP = \frac{VF}{(1 + i)^n}")
    st.latex(r"i = \left(\frac{VF}{VP}\right)^{1/n} - 1 \qquad n = \frac{\ln(VF/VP)}{\ln(1 + i)}")
    st.latex(r"n_{\times 2} = \frac{\ln 2}{\ln(1 + i)} \qquad EA = (1 + i)^m - 1 \qquad i = \frac{j}{m}")
