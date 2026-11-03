"""Lectura y validación de datos/casos.json, compartida por las páginas que usan los casos."""

import json
from pathlib import Path

import streamlit as st

RUTA_CASOS = Path(__file__).resolve().parent.parent / "datos" / "casos.json"

CLAVES_CASO = ("id", "titulo", "descripcion", "temas", "entidades", "fecha_consulta", "fuentes", "parametros")
CLAVES_FUENTE = ("nombre", "url", "fecha")
# Parámetros de cada caso, en el orden del archivo
CLAVES_PARAMETROS = (
    ("monto", "plazo_meses", "ofertas"),
    ("capital", "plazo_dias", "tasa_cdt_ea", "tasa_cuenta_ea", "retencion_cdt", "retencion_cuenta", "inflacion_ipc"),
    ("a1", "gradiente_aritmetico_G", "gradiente_geometrico_g", "plazo_meses", "tasa_ea", "meta_ahorro"),
)


def cargar_casos(ruta=RUTA_CASOS):
    """Lee y valida los casos. Devuelve (casos, None) o (None, motivo del error)."""
    try:
        with open(ruta, "r", encoding="utf-8") as f:
            casos = json.load(f)["casos"]
        if len(casos) != len(CLAVES_PARAMETROS):
            return None, f"se esperan {len(CLAVES_PARAMETROS)} casos"
        for caso, claves in zip(casos, CLAVES_PARAMETROS):
            faltan = [c for c in CLAVES_CASO if c not in caso]
            faltan += [c for c in claves if c not in caso.get("parametros", {})]
            for fuente in caso.get("fuentes", []):
                faltan += [f"{c} de una fuente" for c in CLAVES_FUENTE if c not in fuente]
            if faltan:
                return None, f"al caso {caso.get('id', 'sin id')} le falta: {', '.join(faltan)}"
        if len(casos[0]["parametros"]["ofertas"]) != 2:
            return None, "el Caso 1 debe tener 2 ofertas"
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as error:
        return None, str(error)
    return casos, None


def cargar_casos_o_detener():
    """Casos válidos para la página; si no se pueden leer, muestra el error y detiene la página."""
    casos, error = cargar_casos()
    if casos is None:
        st.error(f"No se pudo leer datos/casos.json: {error}. Esta página no puede mostrar sus datos sin ese archivo.")
        st.stop()
    return casos
