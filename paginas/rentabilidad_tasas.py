"""Página de rentabilidad y tasas: conversor central, equivalencias, combinada, retención y comparador."""

import pandas as pd
import streamlit as st

from componentes import entradas, estilos, graficos
from componentes.formato import numero, pesos, porcentaje, tasa_con_codigo
from componentes.verificacion import tarjeta_verificacion
from finanzas import tasas

TEMA = "rentabilidad_tasas"
COLOR = estilos.TEMAS[TEMA]["color"]
MONTO_PRUEBA = 1_000_000

TIPOS = {"periodica": "Periódica", "nominal": "Nominal anual", "efectiva": "Efectiva anual"}
PERIODICIDADES = {p: p.capitalize() for p in tasas.PERIODOS_POR_ANO}
MODALIDADES = {"vencida": "Vencida", "anticipada": "Anticipada"}
CODIGOS = {c: c for c in tasas.CODIGOS}

EJEMPLOS = {
    "Excel: 1,5% MV": {
        "rt_valor": 0.015, "rt_tipo": "periodica", "rt_periodicidad": "mensual", "rt_modalidad": "vencida",
    },
    "Excel: 3,5% TA": {
        "rt_valor": 0.035, "rt_tipo": "periodica", "rt_periodicidad": "trimestral", "rt_modalidad": "anticipada",
    },
    "Crédito al 21% NAMV": {
        "rt_valor": 0.21, "rt_tipo": "nominal", "rt_periodicidad": "mensual", "rt_modalidad": "vencida",
    },
    "CDT al 10,2% EA": {
        "rt_valor": 0.102, "rt_tipo": "efectiva", "rt_periodicidad": "anual", "rt_modalidad": "vencida",
    },
}


def describir(valor, tipo, periodicidad, modalidad):
    """Texto de la tasa tal como la escribió el usuario, ej. "1,50% periódica mensual vencida"."""
    if tipo == "efectiva":
        return f"{porcentaje(valor)} efectiva anual {modalidad}"
    return f"{porcentaje(valor)} {TIPOS[tipo].lower()} {periodicidad} {modalidad}"


explicar = estilos.encabezado(
    TEMA,
    "Rentabilidad y tasas",
    "Toda tasa se lleva a su efectiva anual (EA) para poder compararla y convertirla.",
)
entradas.botones_ejemplos(EJEMPLOS)

# --- Conversor central ---
col_datos, col_resultados = st.columns([1, 2], gap="large")

with col_datos, estilos.tarjeta("rt_datos"):
    st.subheader("Tasa a convertir")
    valor = entradas.campo_tasa("Valor de la tasa", "rt_valor", 0.015, minimo=0.0, maximo=0.99)
    tipo = entradas.campo_opcion("Tipo", list(TIPOS), "rt_tipo", "periodica", TIPOS)
    if tipo == "efectiva":
        periodicidad = "anual"
        st.caption("La efectiva anual ya está expresada por año.")
    else:
        periodicidad = entradas.campo_lista(
            "Periodicidad", list(PERIODICIDADES), "rt_periodicidad", "mensual", PERIODICIDADES
        )
    modalidad = entradas.campo_opcion("Modalidad", list(MODALIDADES), "rt_modalidad", "vencida", MODALIDADES)

ea = tasas.a_efectiva_anual(valor, tipo, periodicidad, modalidad)
mv = tasas.desde_efectiva_anual(ea, "periodica", "mensual", "vencida")
namv = tasas.desde_efectiva_anual(ea, "nominal", "mensual", "vencida")

with col_resultados:
    k1, k2, k3 = st.columns(3)
    with k1:
        estilos.tarjeta_kpi("percent", tasa_con_codigo(ea, "EA", 4), "Tasa efectiva anual", TEMA)
    with k2:
        estilos.tarjeta_kpi("calendar_month", tasa_con_codigo(mv, "MV", 4), "Equivalente mensual vencida", TEMA)
    with k3:
        estilos.tarjeta_kpi("functions", tasa_con_codigo(namv, "NAMV", 4), "Equivalente nominal mes vencido", TEMA)

    if explicar:
        m = tasas.PERIODOS_POR_ANO[periodicidad]
        pasos = []
        if tipo == "nominal":
            pasos.append(f"como es nominal, se divide entre {m} para obtener la tasa de cada periodo")
        if modalidad == "anticipada":
            pasos.append("como es anticipada (los intereses se cobran al inicio), se pasa a vencida con i / (1 − i)")
        if m > 1:
            pasos.append(f"luego se capitaliza {m} veces en el año: (1 + i)^{m} − 1")
        st.info(
            f"Escribiste una tasa de **{describir(valor, tipo, periodicidad, modalidad)}**. "
            + (("Para llevarla a efectiva anual, " + "; ".join(pasos) + ". ") if pasos else "")
            + f"El resultado es **{porcentaje(ea, 4)} EA**: si inviertes {pesos(MONTO_PRUEBA)} durante "
            f"un año a esta tasa, terminas con **{pesos(MONTO_PRUEBA * (1 + ea))}**. Las tasas de la tabla "
            f"de abajo son la misma tasa escrita de otras formas."
        )

    st.markdown("**Tabla de equivalencias**")
    tabla = tasas.tabla_equivalencias(ea)
    # VF de $1.000.000 a un año calculado desde cada tasa periódica, sin pasar por la EA
    vf_vencidas = [MONTO_PRUEBA * (1 + f.periodica_vencida) ** f.periodos_por_ano for f in tabla.itertuples()]
    vf_anticipadas = [MONTO_PRUEBA / (1 - f.periodica_anticipada) ** f.periodos_por_ano for f in tabla.itertuples()]
    st.dataframe(
        pd.DataFrame(
            {
                "Periodicidad": tabla["periodicidad"].str.capitalize(),
                "Periodos/año": tabla["periodos_por_ano"],
                "Periódica vencida": tabla["periodica_vencida"].map(lambda t: porcentaje(t, 4)),
                "Nominal vencida": tabla["nominal_vencida"].map(lambda t: porcentaje(t, 4)),
                "Periódica anticipada": tabla["periodica_anticipada"].map(lambda t: porcentaje(t, 4)),
                "Nominal anticipada": tabla["nominal_anticipada"].map(lambda t: porcentaje(t, 4)),
                f"VF de {pesos(MONTO_PRUEBA)}": [pesos(v, 2) for v in vf_vencidas],
            }
        ),
        hide_index=True,
        width="stretch",
    )

vf_ea = MONTO_PRUEBA * (1 + ea)
vf_mas_lejano = max(vf_vencidas + vf_anticipadas, key=lambda v: abs(v - vf_ea))
tarjeta_verificacion(
    f"{pesos(MONTO_PRUEBA)} a un año da el mismo VF con cada tasa periódica vencida y anticipada",
    vf_ea,
    vf_mas_lejano,
    "Tasa equivalente más alejada",
    tolerancia=0.01,
    formato=lambda v: pesos(v, 2),
)

# --- Tasa combinada, real y retención ---
st.subheader("Inflación, tasa real y retención en la fuente")
col_combinada, col_retencion = st.columns(2, gap="large")

with col_combinada, estilos.tarjeta("rt_combinada"):
    st.markdown("**Tasa combinada (IPC + puntos)**")
    c1, c2 = st.columns(2)
    with c1:
        ipc = entradas.campo_tasa("IPC", "rt_ipc", 0.042, minimo=-0.5, maximo=0.99)
    with c2:
        puntos = entradas.campo_tasa("Puntos adicionales", "rt_puntos", 0.03, minimo=-0.5, maximo=0.99)
    combinada = tasas.tasa_combinada(ipc, puntos)
    real = tasas.tasa_real(ea, ipc)
    estilos.tarjeta_kpi("add_chart", tasa_con_codigo(combinada, "EA", 4), "Tasa combinada compuesta", TEMA)
    st.caption(
        f"Sumar directo daría {porcentaje(ipc + puntos, 4)}; la diferencia es el interés sobre los puntos "
        f"({porcentaje(combinada - ipc - puntos, 4)})."
    )
    st.markdown(
        f"Rentabilidad real de la tasa del conversor ({porcentaje(ea)} EA) con este IPC: "
        f"**{porcentaje(real, 4)}**."
    )

with col_retencion, estilos.tarjeta("rt_retencion"):
    st.markdown("**Retención en la fuente sobre los intereses**")
    retencion = entradas.campo_tasa(
        "Retención", "rt_retencion", 0.07, maximo=1.0,
        ayuda="Valor por defecto 7%, pendiente de confirmar el vigente.",
    )
    neta = tasas.tea_neta(ea, retencion)
    estilos.tarjeta_kpi("receipt_long", tasa_con_codigo(neta, "EA", 4), "TEA neta después de retención", TEMA)
    intereses_brutos = MONTO_PRUEBA * ea
    st.markdown(
        f"Sobre {pesos(MONTO_PRUEBA)} a un año: intereses "
        f"<span class='intereses'>{pesos(intereses_brutos)}</span>, retención "
        f"{pesos(intereses_brutos * retencion)}, recibes "
        f"<span class='intereses'>{pesos(intereses_brutos * (1 - retencion))}</span> de intereses.",
        unsafe_allow_html=True,
    )

# --- Comparador de dos ofertas ---
st.subheader("Comparador de dos ofertas")
objetivo = entradas.campo_opcion(
    "¿Qué estás comparando?", ["credito", "inversion"], "rt_objetivo", "credito",
    {"credito": "Crédito (conviene la menor)", "inversion": "Inversión (conviene la mayor)"},
)
col_a, col_b, col_grafico = st.columns([1, 1, 2], gap="large")
ofertas = {}
for columna, nombre, valor_inicial, codigo_inicial in (
    (col_a, "A", 0.014, "MV"),
    (col_b, "B", 0.175, "EA"),
):
    with columna, estilos.tarjeta(f"rt_oferta_{nombre}"):
        st.markdown(f"**Oferta {nombre}**")
        valor_oferta = entradas.campo_tasa("Tasa", f"rt_oferta_{nombre}_valor", valor_inicial, maximo=0.99)
        codigo = entradas.campo_lista("Código", list(CODIGOS), f"rt_oferta_{nombre}_codigo", codigo_inicial)
        ofertas[nombre] = tasas.ea_desde_codigo(valor_oferta, codigo)
        st.markdown(f"Equivale a **{porcentaje(ofertas[nombre], 4)} EA**")

elegir = min if objetivo == "credito" else max
mejor = elegir(ofertas, key=ofertas.get)
otra = "B" if mejor == "A" else "A"

with col_grafico:
    fig = graficos.grafico_barras(
        [f"Oferta {n}" for n in ofertas],
        [{"nombre": "Tasa efectiva anual", "y": list(ofertas.values()), "color": COLOR}],
        "Ofertas llevadas a efectiva anual",
        "Oferta",
        "Tasa EA",
        unidad="%",
    )
    st.plotly_chart(fig, width="stretch", config=graficos.CONFIG_PLOTLY)

if ofertas["A"] == ofertas["B"]:
    st.info("Las dos ofertas son equivalentes: tienen la misma EA.")
else:
    diferencia = abs(ofertas["A"] - ofertas["B"])
    st.success(
        f"Conviene la **oferta {mejor}** ({porcentaje(ofertas[mejor])} EA): "
        f"{'cuesta' if objetivo == 'credito' else 'rinde'} {numero(diferencia * 100, 2)} puntos porcentuales "
        f"{'menos' if objetivo == 'credito' else 'más'} al año que la oferta {otra}. "
        f"Sobre {pesos(MONTO_PRUEBA)} a un año son {pesos(MONTO_PRUEBA * diferencia)}."
    )

with st.expander("Fórmulas usadas"):
    st.latex(r"EA = (1 + i)^m - 1 \qquad i = (1 + EA)^{1/m} - 1 \qquad j = i \cdot m")
    st.latex(r"i_v = \frac{i_a}{1 - i_a} \qquad i_a = \frac{i_v}{1 + i_v}")
    st.latex(r"i_{\text{comb}} = (1 + IPC)(1 + p) - 1 \qquad i_{\text{real}} = \frac{1 + TEA}{1 + IPC} - 1")
    st.latex(r"TEA_{\text{neta}} = TEA \cdot (1 - r)")
    st.caption("m: periodos por año (diaria 360, mensual 12, bimestral 6, trimestral 4, semestral 2, anual 1).")
