"""Página de interés simple: interés, VF, VP, despejes y valor acumulado."""

import streamlit as st

from componentes import entradas, estilos, graficos
from componentes.formato import numero, pesos, porcentaje
from componentes.verificacion import tarjeta_verificacion
from finanzas import interes

TEMA = "interes_simple"
COLOR = estilos.TEMAS[TEMA]["color"]

UNIDADES_TASA = {"anual": "Anual", "mensual": "Mensual"}
UNIDADES_PLAZO = {"dias": "Días", "meses": "Meses", "anos": "Años"}
PERIODO = {"dias": "día", "meses": "mes", "anos": "año"}
CONVENCIONES = {360: "360 días (comercial)", 365: "365 días"}

EJEMPLOS = {
    "Excel de clase: 4 meses al 18%": {
        "is_capital": 10_000_000, "is_tasa": 0.18, "is_unidad_tasa": "anual",
        "is_plazo": 4, "is_unidad_plazo": "meses", "is_dias_ano": 360,
    },
    "Inversión a 90 días al 9,8%": {
        "is_capital": 20_000_000, "is_tasa": 0.098, "is_unidad_tasa": "anual",
        "is_plazo": 90, "is_unidad_plazo": "dias", "is_dias_ano": 360,
    },
    "Préstamo al 3% mensual": {
        "is_capital": 2_000_000, "is_tasa": 0.03, "is_unidad_tasa": "mensual",
        "is_plazo": 6, "is_unidad_plazo": "meses", "is_dias_ano": 360,
    },
}

explicar = estilos.encabezado(
    TEMA,
    "Interés simple",
    "Los intereses se calculan siempre sobre el capital inicial y no se suman al capital.",
)
entradas.botones_ejemplos(EJEMPLOS)

col_datos, col_resultados = st.columns([1, 2], gap="large")

with col_datos, estilos.tarjeta("is_datos"):
    st.subheader("Datos")
    capital = entradas.campo_dinero("Capital (P)", "is_capital", 10_000_000, minimo=1)
    tasa = entradas.campo_tasa("Tasa de interés simple", "is_tasa", 0.18, minimo=0.0001)
    unidad_tasa = entradas.campo_opcion("La tasa es", list(UNIDADES_TASA), "is_unidad_tasa", "anual", UNIDADES_TASA)
    plazo = entradas.campo_numero("Plazo", "is_plazo", 4)
    unidad_plazo = entradas.campo_opcion("Unidad del plazo", list(UNIDADES_PLAZO), "is_unidad_plazo", "meses", UNIDADES_PLAZO)
    dias_ano = entradas.campo_opcion("Convención de días", list(CONVENCIONES), "is_dias_ano", 360, CONVENCIONES)

# Todo se lleva a años: tasa anual y plazo en años con la convención de días
tasa_anual = interes.tasa_simple_anual(tasa, unidad_tasa)
n_anos = interes.plazo_en_anos(plazo, unidad_plazo, dias_ano)
intereses = interes.interes_simple(capital, tasa_anual, n_anos)
vf = interes.vf_simple(capital, tasa_anual, n_anos)

# Tasa por periodo en la unidad del plazo, para el acumulado periodo a periodo
tasa_periodo = tasa_anual * n_anos / plazo
periodo = PERIODO[unidad_plazo]
periodos, saldos = interes.acumulado_simple(capital, tasa_periodo, plazo)

with col_resultados:
    k1, k2, k3 = st.columns(3)
    with k1:
        estilos.tarjeta_kpi("savings", pesos(intereses), "Intereses ganados", "intereses")
    with k2:
        estilos.tarjeta_kpi("account_balance_wallet", pesos(vf), "Valor futuro (VF)", TEMA)
    with k3:
        estilos.tarjeta_kpi("event_repeat", pesos(capital * tasa_periodo), f"Interés por {periodo}", TEMA)

    if explicar:
        st.info(
            f"Inviertes o prestas **{pesos(capital)}** a una tasa simple de "
            f"**{porcentaje(tasa_anual)} anual** durante **{numero(plazo, 0 if plazo == int(plazo) else 2)} "
            f"{UNIDADES_PLAZO[unidad_plazo].lower()}**. Como el interés simple siempre se calcula sobre "
            f"el capital inicial, cada {periodo} ganas lo mismo: **{pesos(capital * tasa_periodo)}**. "
            f"Al final acumulas **{pesos(intereses)}** de intereses y recibes **{pesos(vf)}**."
        )

    if unidad_plazo == "dias":
        otra = 365 if dias_ano == 360 else 360
        intereses_otra = interes.interes_simple(capital, tasa_anual, interes.plazo_en_anos(plazo, "dias", otra))
        st.caption(
            f"Con año de {otra} días el interés sería {pesos(intereses_otra)} "
            f"({pesos(intereses_otra - intereses)} de diferencia)."
        )
    else:
        st.caption("La convención de días solo cambia el resultado cuando el plazo está en días.")

    fig = graficos.grafico_lineas(
        periodos,
        [
            {"nombre": "Valor acumulado", "y": saldos, "color": COLOR},
            {"nombre": "Capital inicial", "y": [capital] * len(periodos), "color": graficos.GRIS_CAPITAL, "punteada": True},
        ],
        "Valor acumulado con interés simple",
        UNIDADES_PLAZO[unidad_plazo],
        "Valor",
    )
    st.plotly_chart(fig, width="stretch", config=graficos.CONFIG_PLOTLY)

st.subheader("Despejes")
tab_vp, tab_tasa, tab_plazo = st.tabs(["Valor presente (VP)", "Tasa (i)", "Plazo (n)"])

with tab_vp:
    st.caption("¿Cuánto hay que invertir hoy para recibir un valor futuro, con la tasa y el plazo de arriba?")
    vf_meta = entradas.campo_dinero("Valor futuro que quieres recibir", valor_inicial=round(vf))
    st.metric("Valor presente", pesos(interes.vp_simple(vf_meta, tasa_anual, n_anos)))

with tab_tasa:
    st.caption("¿Qué tasa simple anual convierte un VP en un VF en el plazo de arriba?")
    c1, c2 = st.columns(2)
    with c1:
        vp_t = entradas.campo_dinero("Valor presente (inversión)", valor_inicial=capital, minimo=1)
    with c2:
        vf_t = entradas.campo_dinero("Valor futuro (lo que recibes)", valor_inicial=round(vf))
    tasa_despejada = interes.tasa_simple(vp_t, vf_t, n_anos)
    st.metric("Tasa simple", f"{porcentaje(tasa_despejada)} anual · {porcentaje(tasa_despejada / 12)} mensual")
    if vf_t < vp_t:
        st.warning("El valor futuro es menor que el presente: la tasa resulta negativa.")

with tab_plazo:
    st.caption("¿Cuánto tiempo tarda un VP en convertirse en un VF con la tasa de arriba?")
    c1, c2 = st.columns(2)
    with c1:
        vp_n = entradas.campo_dinero("Capital inicial", valor_inicial=capital, minimo=1)
    with c2:
        vf_n = entradas.campo_dinero("Valor futuro deseado", valor_inicial=round(vf))
    n_despejado = interes.plazo_simple(vp_n, vf_n, tasa_anual)
    st.metric(
        "Plazo",
        f"{numero(n_despejado, 2)} años · {numero(n_despejado * 12, 1)} meses · "
        f"{numero(n_despejado * dias_ano)} días",
    )
    if vf_n < vp_n:
        st.warning("El valor futuro es menor que el capital: no hay plazo positivo que lo logre.")

st.subheader("Verificación")
tarjeta_verificacion(
    "Intereses: fórmula contra suma periodo a periodo",
    intereses,
    saldos[-1] - capital,
    f"Suma de {numero(len(periodos) - 1)} periodos",
)

with st.expander("Fórmulas usadas"):
    st.latex(r"I = P \cdot i \cdot n \qquad VF = P\,(1 + i\,n) \qquad VP = \frac{VF}{1 + i\,n}")
    st.latex(r"i = \frac{VF/VP - 1}{n} \qquad n = \frac{VF/VP - 1}{i}")
    st.latex(r"n_{\text{años}} = \frac{\text{días}}{360 \text{ o } 365} = \frac{\text{meses}}{12} \qquad i_{\text{anual}} = 12 \cdot i_{\text{mensual}}")
