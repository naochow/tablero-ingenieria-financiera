"""Campos de entrada reutilizables y botones de ejemplos.

Con clave, el valor vive en st.session_state (así los ejemplos pueden cargarlo);
sin clave, el campo arranca en valor_inicial y se reinicia cuando este cambia.
Los campos de tasa muestran porcentaje pero devuelven decimales.
"""

import streamlit as st

from componentes.formato import pesos

_CLAVES_TASA = "_claves_tasa"


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
    """Tasa en porcentaje en pantalla; recibe y devuelve decimales (0.18 = 18%)."""
    if clave is not None:
        st.session_state.setdefault(_CLAVES_TASA, set()).add(clave)
    valor = st.number_input(
        f"{etiqueta} (%)",
        min_value=minimo * 100,
        max_value=maximo * 100,
        step=paso * 100,
        format="%.4f",
        help=ayuda,
        **_argumentos_valor(clave, valor_inicial * 100),
    )
    return valor / 100


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


def _cargar_ejemplo(valores):
    claves_tasa = st.session_state.get(_CLAVES_TASA, set())
    for clave, valor in valores.items():
        st.session_state[clave] = valor * 100 if clave in claves_tasa else valor


def botones_ejemplos(ejemplos):
    """Botones que cargan valores típicos. ejemplos: {nombre: {clave: valor}}; tasas en decimal."""
    st.caption("Ejemplos para cargar")
    columnas = st.columns(len(ejemplos))
    for columna, (nombre, valores) in zip(columnas, ejemplos.items()):
        columna.button(nombre, on_click=_cargar_ejemplo, args=(valores,), width="stretch")
