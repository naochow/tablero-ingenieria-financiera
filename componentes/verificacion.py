"""Tarjeta de verificación ✓ / ✗: compara un resultado con un cálculo independiente."""

from html import escape

import streamlit as st

from componentes.formato import pesos


def tarjeta_verificacion(titulo, resultado, referencia, metodo, tolerancia=1, formato=pesos):
    """Muestra si resultado y referencia coinciden dentro de la tolerancia. Devuelve True/False.

    metodo describe cómo se obtuvo la referencia (ej. "npf.fv"); debe ser una ruta
    de cálculo distinta a la del resultado.
    """
    diferencia = abs(resultado - referencia)
    coincide = diferencia <= tolerancia
    clase, icono, estado = (
        ("verificacion-ok", "✓", "Coincide") if coincide else ("verificacion-error", "✗", "No coincide")
    )
    st.markdown(
        f"""
        <div class="verificacion {clase}">
            <b>{icono} {escape(titulo)}: {estado}</b><br>
            Fórmula: {escape(formato(resultado))} · {escape(metodo)}: {escape(formato(referencia))}
            · diferencia: {escape(formato(diferencia))}
        </div>
        """,
        unsafe_allow_html=True,
    )
    return coincide
