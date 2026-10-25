"""Página de gradientes aritmético y geométrico: VP, VF, cuota equivalente y flujo."""

import numpy_financial as npf
import streamlit as st

from componentes import entradas, estilos, graficos
from componentes.formato import numero, pesos, porcentaje
from componentes.verificacion import tarjeta_verificacion
from finanzas import gradientes, tasas

TEMA = "gradientes"
COLOR = estilos.TEMAS[TEMA]["color"]
COLOR_LINEA = estilos.TEMAS["supuestos"]["oscuro"]

CLASES = {"aritmetico": "Aritmético (+ G pesos)", "geometrico": "Geométrico (+ g %)"}
CONOCIDOS = {"primera": "Primera cuota (A1)", "vp": "Valor presente (VP)"}
PERIODO = {"diaria": "día", "mensual": "mes", "bimestral": "bimestre",
           "trimestral": "trimestre", "semestral": "semestre", "anual": "año"}

# gr_clase es el tipo de gradiente; gr_tipo es el tipo de tasa (selector_tasa)
EJEMPLOS = {
    "Excel: $500.000 + $20.000 al 1,2%": {
        "gr_clase": "aritmetico", "gr_conocido": "primera", "gr_valor": 500_000, "gr_G": 20_000,
        "gr_tasa": 0.012, "gr_tipo": "periodica", "gr_periodicidad": "mensual", "gr_modalidad": "vencida",
        "gr_periodicidad_flujo": "mensual", "gr_n": 24,
    },
    "Excel: VP $5.000.000, 21,5% EA, +10%": {
        "gr_clase": "geometrico", "gr_conocido": "vp", "gr_valor": 5_000_000, "gr_g": 0.10,
        "gr_tasa": 0.215, "gr_tipo": "efectiva", "gr_modalidad": "vencida",
        "gr_periodicidad_flujo": "trimestral", "gr_n": 8,
    },
    "Decreciente: $1.000.000 − $30.000": {
        "gr_clase": "aritmetico", "gr_conocido": "primera", "gr_valor": 1_000_000, "gr_G": -30_000,
        "gr_tasa": 0.01, "gr_tipo": "periodica", "gr_periodicidad": "mensual", "gr_modalidad": "vencida",
        "gr_periodicidad_flujo": "mensual", "gr_n": 24,
    },
}

explicar = estilos.encabezado(
    TEMA,
    "Gradientes",
    "Cuotas que cambian cada periodo: una cantidad fija (aritmético) o un porcentaje fijo (geométrico).",
)
entradas.botones_ejemplos(EJEMPLOS)

col_datos, col_resultados = st.columns([1, 2], gap="large")

with col_datos, estilos.tarjeta("gr_datos"):
    st.subheader("Datos")
    clase = entradas.campo_opcion("Tipo de gradiente", list(CLASES), "gr_clase", "aritmetico", CLASES)
    conocido = entradas.campo_opcion("¿Qué conoces?", list(CONOCIDOS), "gr_conocido", "primera", CONOCIDOS)
    valor = entradas.campo_dinero(CONOCIDOS[conocido], "gr_valor", 500_000, minimo=1)
    if clase == "aritmetico":
        cambio = entradas.campo_dinero(
            "Gradiente G (pesos por periodo, negativo si decrece)", "gr_G", 20_000, minimo=-1e12, paso=10_000
        )
    else:
        cambio = entradas.campo_tasa(
            "Gradiente g (por periodo, negativo si decrece)", "gr_g", 0.005, minimo=-0.99, maximo=1.0
        )
    ea, descripcion_tasa = entradas.selector_tasa("gr", 0.012)
    periodicidad_flujo = entradas.campo_lista(
        "Periodicidad de las cuotas", list(entradas.PERIODICIDADES), "gr_periodicidad_flujo", "mensual",
        entradas.PERIODICIDADES,
    )
    n = int(entradas.campo_numero("Número de cuotas (n)", "gr_n", 24))

# La tasa se lleva a la periodicidad de las cuotas pasando por la EA
i = tasas.periodica_desde_ea(ea, tasas.PERIODOS_POR_ANO[periodicidad_flujo])
periodo = PERIODO[periodicidad_flujo]

if clase == "aritmetico":
    vp_desde_a1, a1_desde_vp, generar_cuotas = (
        gradientes.vp_aritmetico, gradientes.primera_cuota_aritmetico, gradientes.cuotas_aritmetico
    )
    texto_cambio = f"{pesos(cambio)} por {periodo}"
else:
    vp_desde_a1, a1_desde_vp, generar_cuotas = (
        gradientes.vp_geometrico, gradientes.primera_cuota_geometrico, gradientes.cuotas_geometrico
    )
    texto_cambio = f"{porcentaje(cambio)} por {periodo}"

if conocido == "primera":
    a1 = valor
    vp = vp_desde_a1(a1, cambio, i, n)
else:
    vp = valor
    a1 = a1_desde_vp(vp, cambio, i, n)

cuotas = generar_cuotas(a1, cambio, n)
vf = gradientes.vf_gradiente(vp, i, n)
a_eq = gradientes.cuota_equivalente(vp, i, n)
cruce = gradientes.periodo_cruce(cuotas, a_eq)
decrece = cuotas[-1] < cuotas[0]

with col_resultados:
    st.caption(
        f"Tasa ingresada: {descripcion_tasa} = {porcentaje(ea, 4)} EA → "
        f"**{porcentaje(i, 4)} por {periodo}** (periódica vencida de las cuotas)."
    )
    k1, k2, k3 = st.columns(3)
    with k1:
        estilos.tarjeta_kpi("first_page", pesos(vp), "Valor presente (VP)", TEMA)
    with k2:
        estilos.tarjeta_kpi("last_page", pesos(vf), "Valor futuro (VF)", TEMA)
    with k3:
        estilos.tarjeta_kpi("drag_handle", pesos(a_eq), "Cuota uniforme equivalente", TEMA)
    k4, k5, k6 = st.columns(3)
    with k4:
        estilos.tarjeta_kpi("start", pesos(a1), "Primera cuota (A1)", TEMA)
    with k5:
        estilos.tarjeta_kpi("trending_down" if decrece else "trending_up", pesos(cuotas[-1]), f"Cuota {n}", TEMA)
    with k6:
        estilos.tarjeta_kpi("savings", pesos(sum(cuotas) - vp), "Intereses (cuotas − VP)", "intereses")

    if cruce is None:
        st.markdown(f"La cuota con gradiente no {'baja de' if decrece else 'supera'} la cuota fija de {pesos(a_eq)} en ningún periodo.")
    else:
        st.markdown(
            f"Desde el **periodo {cruce}** la cuota con gradiente "
            f"**{'queda por debajo de' if decrece else 'supera a'}** la cuota fija equivalente de {pesos(a_eq)}."
        )
    if min(cuotas) < 0:
        st.warning("Con este gradiente decreciente algunas cuotas son negativas; revisa G o el número de cuotas.")

    if explicar:
        st.info(
            f"La primera cuota es **{pesos(a1)}** y cada {periodo} cambia en **{texto_cambio}**, hasta llegar a "
            f"**{pesos(cuotas[-1])}** en la cuota {n}. Traídas a hoy con una tasa de {porcentaje(i, 4)} por {periodo}, "
            f"todas las cuotas valen **{pesos(vp)}**. Pagar ese mismo valor con cuotas iguales sería "
            f"**{pesos(a_eq)}** cada {periodo}: al inicio pagas {'más' if decrece else 'menos'} que con cuota fija "
            f"y al final {'menos' if decrece else 'más'}."
        )

    periodos = list(range(1, n + 1))
    fig = graficos.grafico_barras(
        periodos,
        [{"nombre": "Cuota con gradiente", "y": cuotas, "color": COLOR}],
        f"Flujo de cuotas con gradiente {'aritmético' if clase == 'aritmetico' else 'geométrico'} y cuota equivalente",
        f"Periodo ({periodo})",
        "Cuota",
    )
    graficos.linea_referencia(fig, periodos, a_eq, "Cuota fija equivalente", COLOR_LINEA)
    fig.update_layout(showlegend=True)
    if cruce is not None:
        fig.add_annotation(x=cruce, y=cuotas[cruce - 1], text=f"Cruce: periodo {cruce}", showarrow=True, arrowhead=2, ay=-40)
    st.plotly_chart(fig, width="stretch", config=graficos.CONFIG_PLOTLY)

st.subheader("Verificación")
tarjeta_verificacion("VP: fórmula cerrada contra VPN cuota a cuota", vp,
                     npf.npv(i, [0] + cuotas), "npf.npv del flujo (inicia en 0)")
tarjeta_verificacion("Cuota equivalente: fórmula contra numpy-financial", a_eq,
                     npf.pmt(i, n, -vp), "npf.pmt")

with st.expander("Fórmulas usadas"):
    st.latex(r"\text{Aritmético: } VP = A_1 \cdot a + \frac{G}{i}\left(a - n(1 + i)^{-n}\right) \qquad A_t = A_1 + (t - 1)G")
    st.latex(r"\text{Geométrico: } VP = A_1 \cdot \frac{1 - \left(\frac{1 + g}{1 + i}\right)^n}{i - g} \qquad A_t = A_1 (1 + g)^{t - 1}")
    st.latex(r"\text{Si } g = i: \; VP = \frac{A_1 \cdot n}{1 + i}")
    st.latex(r"VF = VP\,(1 + i)^n \qquad A_{eq} = \frac{VP}{a} \qquad a = \frac{1 - (1 + i)^{-n}}{i}")
    st.caption(f"Con los datos actuales: i = {porcentaje(i, 4)}, n = {numero(n)}.")
