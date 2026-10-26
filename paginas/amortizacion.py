"""Página de amortización con la metodología y ejercicios de clase (Ingeniería Financiera UPB).

Modelos:
1. Cuota fija (Francés).
2. Abono a capital constante (Alemán).
3. Periodos de gracia con pago de intereses (parcial) y sin pago de intereses (capitalización).
4. Pagos extras periódicos pactados (descuento por VA en cuota fija, descuento nominal en abono constante).
5. Abonos extraordinarios puntuales.
"""

import io
import pandas as pd
import streamlit as st

from componentes import entradas, estilos, graficos
from componentes.formato import numero, pesos, porcentaje
from componentes.verificacion import tarjeta_verificacion
from finanzas import amortizacion, tasas

TEMA = "amortizacion"
COLOR = estilos.TEMAS[TEMA]["color"]
COLOR_CAPITAL = COLOR
COLOR_INTERESES = estilos.INTERESES
COLOR_EXTRA = estilos.TEMAS["series_uniformes"]["color"]

PERIODO = {
    "diaria": "día",
    "mensual": "mes",
    "bimestral": "bimestre",
    "trimestral": "trimestre",
    "semestral": "semestre",
    "anual": "año",
}

EJEMPLOS = {
    "Clase: Vivienda $336M Cuota Fija (180 meses)": {
        "am_sistema": "frances",
        "am_monto": 336_000_000,
        "am_tasa": 0.1765,
        "am_tipo": "efectiva",
        "am_modalidad": "vencida",
        "am_periodicidad_flujo": "mensual",
        "am_n": 180,
        "am_modalidad_gracia": "ninguno",
        "am_tipo_pago_extra": "ninguno",
    },
    "Clase: Cuota inicial $144M Libre inversión (24 meses)": {
        "am_sistema": "frances",
        "am_monto": 144_000_000,
        "am_tasa": 0.2256,
        "am_tipo": "efectiva",
        "am_modalidad": "vencida",
        "am_periodicidad_flujo": "mensual",
        "am_n": 24,
        "am_modalidad_gracia": "ninguno",
        "am_tipo_pago_extra": "ninguno",
    },
    "Clase: Vivienda $336M + Gracia 12m con pago intereses": {
        "am_sistema": "frances",
        "am_monto": 336_000_000,
        "am_tasa": 0.1765,
        "am_tipo": "efectiva",
        "am_modalidad": "vencida",
        "am_periodicidad_flujo": "mensual",
        "am_n": 180,
        "am_modalidad_gracia": "con_interes",
        "am_periodos_gracia": 12,
        "am_tipo_pago_extra": "ninguno",
    },
    "Clase: Vivienda $336M + Gracia 12m sin pago intereses": {
        "am_sistema": "frances",
        "am_monto": 336_000_000,
        "am_tasa": 0.1765,
        "am_tipo": "efectiva",
        "am_modalidad": "vencida",
        "am_periodicidad_flujo": "mensual",
        "am_n": 180,
        "am_modalidad_gracia": "sin_interes",
        "am_periodos_gracia": 12,
        "am_tipo_pago_extra": "ninguno",
    },
    "Clase: Vivienda $336M + Pagos extras $2M cada 6 meses": {
        "am_sistema": "frances",
        "am_monto": 336_000_000,
        "am_tasa": 0.1765,
        "am_tipo": "efectiva",
        "am_modalidad": "vencida",
        "am_periodicidad_flujo": "mensual",
        "am_n": 180,
        "am_modalidad_gracia": "ninguno",
        "am_tipo_pago_extra": "periodico",
        "am_frecuencia_extra": 6,
        "am_monto_extra_periodico": 2_000_000,
    },
    "Clase: Vivienda $336M Abono constante a capital": {
        "am_sistema": "aleman",
        "am_monto": 336_000_000,
        "am_tasa": 0.1765,
        "am_tipo": "efectiva",
        "am_modalidad": "vencida",
        "am_periodicidad_flujo": "mensual",
        "am_n": 180,
        "am_modalidad_gracia": "ninguno",
        "am_tipo_pago_extra": "ninguno",
    },
    "Clase: Vivienda Abono constante + Pagos extras $2M": {
        "am_sistema": "aleman",
        "am_monto": 336_000_000,
        "am_tasa": 0.1765,
        "am_tipo": "efectiva",
        "am_modalidad": "vencida",
        "am_periodicidad_flujo": "mensual",
        "am_n": 180,
        "am_modalidad_gracia": "ninguno",
        "am_tipo_pago_extra": "periodico",
        "am_frecuencia_extra": 6,
        "am_monto_extra_periodico": 2_000_000,
    },
}

explicar = estilos.encabezado(
    TEMA,
    "Modelos de Amortización",
    "Modelos de cuota fija y abono constante a capital con periodos de gracia y pagos extras programados (Metodología de clase UPB).",
)
entradas.botones_ejemplos(EJEMPLOS)

col_datos, col_resultados = st.columns([1, 2], gap="large")

with col_datos, estilos.tarjeta("am_datos"):
    st.subheader("Datos del crédito")
    sistema = entradas.campo_opcion(
        "Modelo de amortización",
        list(amortizacion.SISTEMAS),
        "am_sistema",
        "frances",
        amortizacion.SISTEMAS,
    )
    monto = entradas.campo_dinero("Capital prestado (P)", "am_monto", 336_000_000, minimo=100_000)
    ea, descripcion_tasa = entradas.selector_tasa("am", 0.1765, tipo="efectiva", etiqueta="Tasa de interés")

    periodicidad_flujo = entradas.campo_lista(
        "Periodicidad de las cuotas",
        list(entradas.PERIODICIDADES),
        "am_periodicidad_flujo",
        "mensual",
        entradas.PERIODICIDADES,
    )
    n = int(entradas.campo_numero("Total de periodos (n)", "am_n", 180, minimo=1))

    st.divider()
    st.subheader("Periodo de gracia")
    modalidad_gracia = entradas.campo_opcion(
        "Tipo de gracia",
        list(amortizacion.MODALIDADES_GRACIA),
        "am_modalidad_gracia",
        "ninguno",
        amortizacion.MODALIDADES_GRACIA,
    )
    if modalidad_gracia != "ninguno":
        max_gracia = max(1, n - 1)
        periodos_gracia = int(
            entradas.campo_numero(
                "Cuotas de gracia (meses)",
                "am_periodos_gracia",
                12,
                minimo=1,
            )
        )
        if periodos_gracia >= n:
            st.warning("El periodo de gracia debe ser menor al plazo total.")
            periodos_gracia = n - 1
        st.caption(f"Nuevo periodo de amortización efectiva: **{n - periodos_gracia} cuotas**.")
    else:
        periodos_gracia = 0

    st.divider()
    st.subheader("Pagos extras / Abonos extraordinarios")
    tipo_pago_extra = entradas.campo_opcion(
        "Modalidad de pagos extras",
        list(amortizacion.TIPOS_PAGO_EXTRA),
        "am_tipo_pago_extra",
        "ninguno",
        amortizacion.TIPOS_PAGO_EXTRA,
    )

    frecuencia_extra = 6
    monto_extra_periodico = 0.0
    abono_puntual_periodo = 0
    abono_puntual_monto = 0.0
    efecto_puntual = "reducir_plazo"

    if tipo_pago_extra == "periodico":
        c_p1, c_p2 = st.columns(2)
        with c_p1:
            frecuencia_extra = int(
                entradas.campo_numero("Cada cuántos meses", "am_frecuencia_extra", 6, minimo=1, maximo=max(1, n - 1))
            )
        with c_p2:
            monto_extra_periodico = entradas.campo_dinero(
                "Valor cuota extra", "am_monto_extra_periodico", 2_000_000, minimo=10_000
            )
        total_extras_estimadas = n // frecuencia_extra
        st.caption(f"Total de cuotas extras programadas: **{total_extras_estimadas}** de {pesos(monto_extra_periodico)}.")

    elif tipo_pago_extra == "puntual":
        c_u1, c_u2 = st.columns(2)
        with c_u1:
            abono_puntual_periodo = int(
                entradas.campo_numero("En el periodo", "am_abono_puntual_periodo", min(6, n), minimo=1, maximo=n)
            )
        with c_u2:
            abono_puntual_monto = entradas.campo_dinero(
                "Monto abono puntual", "am_abono_puntual_monto", 5_000_000, minimo=10_000
            )
        efecto_puntual = entradas.campo_opcion(
            "Efecto del abono puntual",
            list(amortizacion.EFECTOS_PUNTUAL),
            "am_efecto_puntual",
            "reducir_plazo",
            amortizacion.EFECTOS_PUNTUAL,
        )

# Tasa periódica vencida
m_anos = tasas.PERIODOS_POR_ANO[periodicidad_flujo]
i = tasas.periodica_desde_ea(ea, m_anos)
periodo = PERIODO[periodicidad_flujo]

# Construcción de la tabla
filas = amortizacion.tabla_amortizacion(
    monto,
    i,
    n,
    sistema=sistema,
    modalidad_gracia=modalidad_gracia,
    periodos_gracia=periodos_gracia,
    tipo_pago_extra=tipo_pago_extra,
    frecuencia_extra_meses=frecuencia_extra,
    monto_extra_periodico=monto_extra_periodico,
    tasa_ea=ea,
    abono_puntual_periodo=abono_puntual_periodo,
    abono_puntual_monto=abono_puntual_monto,
    efecto_puntual=efecto_puntual,
)
resumen = amortizacion.resumen_amortizacion(filas)
comp = amortizacion.comparar_sistemas(monto, i, n)

with col_resultados:
    st.caption(
        f"Tasa ingresada: {descripcion_tasa} = {porcentaje(ea, 4)} EA → "
        f"**Tasa periódica = {porcentaje(i, 6)} {periodo}**."
    )

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        etiqueta_kpi = "Cuota ordinaria" if sistema == "frances" and modalidad_gracia == "ninguno" else "Cuota inicial"
        estilos.tarjeta_kpi("payments", pesos(resumen["cuota_inicial"]), etiqueta_kpi, TEMA)
    with k2:
        estilos.tarjeta_kpi("trending_down", pesos(resumen["total_intereses"]), "Total intereses", "intereses")
    with k3:
        estilos.tarjeta_kpi("account_balance_wallet", pesos(resumen["total_pagado"]), "Total desembolsado", TEMA)
    with k4:
        estilos.tarjeta_kpi("calendar_today", f"{resumen['plazo_efectivo']} {periodo}s", "Plazo efectivo", TEMA)

    # Explicación detallada de clase
    if explicar:
        if sistema == "frances":
            txt = (
                f"**Modelo de Cuota Fija:** Con un capital de **{pesos(monto)}** a una tasa periódica de **{porcentaje(i, 4)}**, "
            )
            if tipo_pago_extra == "periodico" and monto_extra_periodico > 0:
                total_cuotas_extras = n // frecuencia_extra
                i_extra = (1 + ea) ** (frecuencia_extra / 12) - 1
                va_extras = monto_extra_periodico * amortizacion.factor_vp(i_extra, total_cuotas_extras)
                va_ord = monto - va_extras
                txt += (
                    f"se descuenta primero el **Valor Actual de las {total_cuotas_extras} cuotas extras** "
                    f"a la tasa equivalente ({porcentaje(i_extra, 4)}): **VA extras = {pesos(va_extras)}**. "
                    f"El capital restante a amortizar con cuotas ordinarias es **{pesos(va_ord)}**, "
                    f"lo que reduce la cuota mensual ordinaria fija a **{pesos(filas[1]['cuota'])}**. "
                    f"En los meses múltiplos de {frecuencia_extra} se pagan **{pesos(filas[frecuencia_extra]['pago_total'])}**."
                )
            elif modalidad_gracia == "con_interes":
                txt += (
                    f"durante los primeros {periodos_gracia} meses solo se cancelan intereses (**{pesos(monto * i)}**). "
                    f"A partir del mes {periodos_gracia + 1}, el capital de **{pesos(monto)}** se amortiza en los "
                    f"{n - periodos_gracia} meses restantes con una cuota fija de **{pesos(resumen['cuota_final'])}**."
                )
            elif modalidad_gracia == "sin_interes":
                saldo_m12 = monto * ((1 + i) ** periodos_gracia)
                txt += (
                    f"durante los primeros {periodos_gracia} meses la cuota es $0 y los intereses se capitalizan mes a mes, "
                    f"llegando en el mes {periodos_gracia} a un saldo de **{pesos(saldo_m12)}**. "
                    f"Ese nuevo capital se amortiza en {n - periodos_gracia} cuotas de **{pesos(resumen['cuota_final'])}**."
                )
            else:
                txt += (
                    f"la cuota fija mensual resultante es **{pesos(resumen['cuota_inicial'])}**. "
                    f"En el primer mes se pagan **{pesos(filas[1]['intereses'])}** de intereses y se abonan "
                    f"**{pesos(filas[1]['abono_capital'])}** a capital."
                )
            st.info(txt)
        else:
            txt = f"**Modelo de Abono Constante a Capital:** "
            if tipo_pago_extra == "periodico" and monto_extra_periodico > 0:
                total_cuotas_extras = n // frecuencia_extra
                total_nominal_extras = total_cuotas_extras * monto_extra_periodico
                cap_ord = monto - total_nominal_extras
                abono_ord = cap_ord / n
                txt += (
                    f"se descuenta la suma nominal de los pagos extras (**{pesos(total_nominal_extras)}**). "
                    f"El capital ordinario a amortizar es **{pesos(cap_ord)}**, generando un abono mensual constante "
                    f"de **{pesos(abono_ord)}**. La primera cuota total es de **{pesos(filas[1]['cuota'])}** "
                    f"y va decreciendo mes a mes."
                )
            else:
                abono_ord = monto / (n - periodos_gracia)
                txt += (
                    f"el abono mensual constante a capital es de **{pesos(abono_ord)}**. "
                    f"Las cuotas decrecen desde **{pesos(resumen['cuota_inicial'])}** hasta **{pesos(resumen['cuota_final'])}**."
                )
            st.info(txt)

    # Comparativa básica si no hay gracia ni abonos
    if modalidad_gracia == "ninguno" and tipo_pago_extra == "ninguno":
        with estilos.tarjeta("am_comparativa"):
            st.markdown(
                f"**Comparativa directa de clase:** Con Cuota Fija pagas **{pesos(comp['frances']['total_intereses'])}** "
                f"en intereses vs **{pesos(comp['aleman']['total_intereses'])}** en Abono Constante a Capital "
                f"(Ahorro de **{pesos(comp['diferencia_intereses'])}** en intereses)."
            )

# Gráficos
st.subheader("Gráficos de amortización")
col_graf_cuotas, col_graf_saldo = st.columns(2, gap="large")

periodos_graf = [f["periodo"] for f in filas[1:]]
abonos_capital_graf = [f["abono_capital"] for f in filas[1:]]
intereses_graf = [f["intereses"] for f in filas[1:]]
cuotas_extra_graf = [f["cuota_extra"] for f in filas[1:]]
saldos_graf = [f["saldo_final"] for f in filas]
periodos_saldo = [f["periodo"] for f in filas]

with col_graf_cuotas:
    series_barras = [
        {"nombre": "Abono a capital", "y": abonos_capital_graf, "color": COLOR_CAPITAL},
        {"nombre": "Intereses", "y": intereses_graf, "color": COLOR_INTERESES},
    ]
    if any(e > 0 for e in cuotas_extra_graf):
        series_barras.append({"nombre": "Cuota extra", "y": cuotas_extra_graf, "color": COLOR_EXTRA})

    fig_barras = graficos.grafico_barras(
        periodos_graf,
        series_barras,
        "Distribución de pagos mes a mes",
        f"Periodo ({periodo})",
        "Cuota a pagar",
        apiladas=True,
    )
    st.plotly_chart(fig_barras, width="stretch", config=graficos.CONFIG_PLOTLY)

with col_graf_saldo:
    series_lineas = [
        {"nombre": "Saldo de la deuda", "y": saldos_graf, "color": COLOR_CAPITAL},
    ]
    fig_lineas = graficos.grafico_lineas(
        periodos_saldo,
        series_lineas,
        "Curva de saldo final por periodo",
        f"Periodo ({periodo})",
        "Saldo",
        etiquetas_finales=False,
    )
    st.plotly_chart(fig_lineas, width="stretch", config=graficos.CONFIG_PLOTLY)

# Tabla de amortización con la estructura exacta de clase
st.subheader("Tabla de amortización")

tiene_extras = any(f["cuota_extra"] > 0 for f in filas[1:])
datos_tabla = []
for f in filas:
    fila_dict = {
        "Periodos": f["periodo"],
        "Saldo inicial": pesos(f["saldo_inicial"]),
        "Intereses": pesos(f["intereses"]) if f["periodo"] > 0 else "-",
        "Abono a capital": pesos(f["abono_capital"]) if f["periodo"] > 0 else "-",
    }
    if tiene_extras:
        fila_dict["Cuota extra"] = pesos(f["cuota_extra"]) if f["periodo"] > 0 else "-"
        fila_dict["Total abono"] = pesos(f["total_abono"]) if f["periodo"] > 0 else "-"

    fila_dict["Cuota a pagar"] = pesos(f["pago_total"]) if f["periodo"] > 0 else "-"
    fila_dict["Saldo final"] = pesos(f["saldo_final"])
    fila_dict["Vr. cuotas mes 0"] = pesos(f["vr_cuota_mes_0"]) if f["periodo"] > 0 else "-"
    datos_tabla.append(fila_dict)

df_tabla = pd.DataFrame(datos_tabla)
st.dataframe(df_tabla, hide_index=True, width="stretch")

# Botón de descarga en CSV
df_exportar = pd.DataFrame(filas)
csv_buffer = io.StringIO()
df_exportar.to_csv(csv_buffer, index=False)
st.download_button(
    label="Descargar tabla en CSV",
    data=csv_buffer.getvalue(),
    file_name=f"tabla_amortizacion_{sistema}.csv",
    mime="text/csv",
)

# Verificación matemática
st.subheader("Verificación")
tarjeta_verificacion(
    "Valor Presente: suma de 'Vr. cuotas mes 0' contra Capital inicial",
    resumen["suma_vr_cuotas_mes_0"],
    monto,
    "Suma descontada a t=0 (Ecuación de valor)",
)

tarjeta_verificacion(
    "Saldo extinguido al final del plazo",
    filas[-1]["saldo_final"],
    0.0,
    "Saldo periodo final",
    tolerancia=1e-2,
)

with st.expander("Fórmulas usadas en clase"):
    st.markdown("**1. Cuota fija (Francés):**")
    st.latex(r"A = P \cdot \frac{i}{1 - (1 + i)^{-n}} \qquad I_t = \text{Saldo}_{t-1} \cdot i \qquad C_t = A - I_t")
    st.markdown("**2. Cuota fija con pagos extras periódicos (Metodología UPB):**")
    st.latex(r"VA_{\text{extras}} = A_{\text{extra}} \cdot \frac{1 - (1 + i_{\text{extra}})^{-k}}{i_{\text{extra}}}")
    st.latex(r"VA_{\text{ordinario}} = P - VA_{\text{extras}} \qquad A_{\text{ordinaria}} = \frac{VA_{\text{ordinario}}}{a_{\overline{n}|i}}")
    st.markdown("**3. Abono constante a capital (Alemán):**")
    st.latex(r"C = \frac{P}{n} \qquad I_t = \text{Saldo}_{t-1} \cdot i \qquad A_t = C + I_t")
    st.markdown("**4. Verificación cuota a cuota (Ecuación de valor):**")
    st.latex(r"\text{Vr. cuota mes 0} = \frac{\text{Cuota}_t}{(1 + i)^t} \qquad \sum_{t=1}^{n} \text{Vr. cuota mes 0}_t = P")
