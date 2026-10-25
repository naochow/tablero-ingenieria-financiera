"""Campos de entrada reutilizables y botones de ejemplos.

Con clave, el valor vive en st.session_state (así los ejemplos pueden cargarlo);
sin clave, el campo arranca en valor_inicial y se reinicia cuando este cambia.
Los campos de tasa muestran porcentaje pero devuelven y guardan decimales.
"""

import streamlit as st

from componentes.formato import porcentaje, pesos
from finanzas import tasas

_PREFIJO_PORCENTAJE = "_pct_"

TIPOS_TASA = {"periodica": "Periódica", "nominal": "Nominal anual", "efectiva": "Efectiva anual"}
PERIODICIDADES = {p: p.capitalize() for p in tasas.PERIODOS_POR_ANO}
MODALIDADES = {"vencida": "Vencida", "anticipada": "Anticipada"}


def _argumentos_valor(clave, valor_inicial):
    """value= si no hay clave; si la hay, inicializa session_state y usa key=."""
    if clave is None:
        return {"value": valor_inicial}
    st.session_state.setdefault(clave, valor_inicial)
    return {"key": clave}


def campo_dinero(etiqueta, clave=None, valor_inicial=0, minimo=0, paso=100_000, ayuda=None):
    """Valor en COP con su formato colombiano debajo."""
    valor = st.number_input(
        etiqueta,
        min_value=float(minimo),
        step=float(paso),
        format="%.0f",
        help=ayuda,
        **_argumentos_valor(clave, float(valor_inicial)),
    )
    st.caption(pesos(valor))
    return valor


def campo_tasa(etiqueta, clave=None, valor_inicial=0.0, minimo=0.0, maximo=1.0, paso=0.001, ayuda=None):
    """Tasa en porcentaje en pantalla; recibe y devuelve decimales (0.18 = 18%).

    Con clave, session_state[clave] guarda el decimal y el widget (clave _PREFIJO_PORCENTAJE)
    se inicializa desde él; así un ejemplo puede cargar la tasa aunque el campo no esté en pantalla.
    """
    argumentos = {"value": valor_inicial * 100}
    if clave is not None:
        clave_widget = _PREFIJO_PORCENTAJE + clave
        st.session_state.setdefault(clave, valor_inicial)
        if clave_widget not in st.session_state:
            st.session_state[clave_widget] = st.session_state[clave] * 100
        argumentos = {"key": clave_widget}
    valor = st.number_input(
        f"{etiqueta} (%)",
        min_value=minimo * 100,
        max_value=maximo * 100,
        step=paso * 100,
        format="%.4f",
        help=ayuda,
        **argumentos,
    ) / 100
    if clave is not None:
        st.session_state[clave] = valor
    return valor


def campo_numero(etiqueta, clave=None, valor_inicial=1, minimo=1, paso=1, ayuda=None):
    """Cantidad (periodos, días, años)."""
    return st.number_input(
        etiqueta,
        min_value=float(minimo),
        step=float(paso),
        format="%g",
        help=ayuda,
        **_argumentos_valor(clave, float(valor_inicial)),
    )


def campo_opcion(etiqueta, opciones, clave, valor_inicial, etiquetas=None):
    """Selector horizontal. opciones son valores internos; etiquetas los textos a mostrar."""
    st.session_state.setdefault(clave, valor_inicial)
    return st.radio(
        etiqueta,
        opciones,
        key=clave,
        horizontal=True,
        format_func=(lambda o: etiquetas[o]) if etiquetas else str,
    )


def campo_lista(etiqueta, opciones, clave, valor_inicial, etiquetas=None):
    """Lista desplegable, para cuando hay demasiadas opciones para un selector horizontal."""
    st.session_state.setdefault(clave, valor_inicial)
    return st.selectbox(
        etiqueta,
        opciones,
        key=clave,
        format_func=(lambda o: etiquetas[o]) if etiquetas else str,
    )


def selector_tasa(prefijo, valor_inicial=0.01, tipo="periodica", periodicidad="mensual",
                  modalidad="vencida", etiqueta="Tasa de interés"):
    """Tasa con su tipo, periodicidad y modalidad. Devuelve (ea, descripcion).

    Claves en session_state: <prefijo>_tasa, _tipo, _periodicidad, _modalidad.
    """
    valor = campo_tasa(etiqueta, f"{prefijo}_tasa", valor_inicial, maximo=0.99)
    c1, c2 = st.columns(2)
    with c1:
        tipo = campo_lista("Tipo", list(TIPOS_TASA), f"{prefijo}_tipo", tipo, TIPOS_TASA)
    with c2:
        modalidad = campo_lista("Modalidad", list(MODALIDADES), f"{prefijo}_modalidad", modalidad, MODALIDADES)
    if tipo == "efectiva":
        periodicidad = "anual"
        descripcion = f"{porcentaje(valor)} efectiva anual"
    else:
        periodicidad = campo_lista(
            "Periodicidad de la tasa", list(PERIODICIDADES), f"{prefijo}_periodicidad", periodicidad, PERIODICIDADES
        )
        descripcion = f"{porcentaje(valor)} {TIPOS_TASA[tipo].lower()} {periodicidad}"
    if modalidad == "anticipada":
        descripcion += " anticipada"
    return tasas.a_efectiva_anual(valor, tipo, periodicidad, modalidad), descripcion


def _cargar_ejemplo(valores):
    for clave, valor in valores.items():
        st.session_state[clave] = valor
        # Si es una tasa, el widget en porcentaje se vuelve a crear desde el decimal
        st.session_state.pop(_PREFIJO_PORCENTAJE + clave, None)


def botones_ejemplos(ejemplos):
    """Botones que cargan valores típicos. ejemplos: {nombre: {clave: valor}}; tasas en decimal."""
    st.caption("Ejemplos para cargar")
    columnas = st.columns(len(ejemplos))
    for columna, (nombre, valores) in zip(columnas, ejemplos.items()):
        columna.button(nombre, on_click=_cargar_ejemplo, args=(valores,), width="stretch")
