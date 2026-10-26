"""Página de inicio (Landing Page): resumen del tablero, accesos a casos aplicados y módulos temáticos."""

import streamlit as st

from componentes import estilos
from componentes.formato import pesos, porcentaje

TEMA = "principal"
COLOR = estilos.TEMAS[TEMA]["color"]

explicar = estilos.encabezado(
    TEMA,
    "Tablero de Ingeniería Financiera",
    "Plataforma interactiva para la modelación matemática, visualización pedagógica y toma de decisiones financieras integradas.",
)

# Tarjeta de bienvenida y presentación institucional
with estilos.tarjeta("bienvenida"):
    c_info, c_kpis = st.columns([2, 1], gap="medium")
    with c_info:
        st.markdown(
            "Bienvenido al **Tablero de Ingeniería Financiera**, desarrollado para la asignatura "
            "de Ingeniería Financiera de la **Universidad Pontificia Bolivariana (UPB)** por "
            "**Naomi Chow Morelos** y **Daniel Lopez Lopez**."
        )
        st.markdown(
            "Esta herramienta sustituye los modelos estáticos en hojas de cálculo por una suite interactiva "
            "diseñada con estándares de la banca colombiana, validaciones matemáticas automatizadas y "
            "gráficos de alta resolución en Plotly."
        )
    with c_kpis:
        st.caption("Estructura del tablero:")
        st.markdown(f"- **6 Módulos temáticos:** Desde interés simple hasta amortización.")
        st.markdown(f"- **3 Casos aplicados:** Decisiones reales de crédito, inversión y ahorro.")
        st.markdown(f"- **100% verificado:** Pruebas unitarias sobre fórmulas de clase.")

st.divider()

# ==============================================================================
# SECCIÓN 1: CASOS PRÁCTICOS APLICADOS (DESTACADOS)
# ==============================================================================
st.subheader("🎯 Casos Prácticos de Toma de Decisiones")
st.caption("Escenarios reales de la economía colombiana resueltos combinando los conceptos teóricos.")

col_c1, col_c2, col_c3 = st.columns(3, gap="medium")

with col_c1, estilos.tarjeta("card_caso1"):
    st.markdown("#### 🚗 Crédito de Vehículo")
    st.markdown("**Sufi vs. Davivienda (48 meses)**")
    st.caption("Monto: $35.000.000 COP")
    st.markdown(
        "- **Dilema de tasas:** Comparación justa entre 1,65% MV (21,70% EA) vs. 20,50% NAMV (22,54% EA).\n"
        "- **Sistemas:** Cuota Fija (Francés) para liquidez vs. Abono Constante (Alemán) para ahorro de $2,6M en intereses."
    )
    if st.button("Explorar Caso de Vehículo", key="btn_caso1", use_container_width=True):
        st.switch_page("paginas/casos_aplicados.py")

with col_c2, estilos.tarjeta("card_caso2"):
    st.markdown("#### 🏦 Inversión y Rentabilidad")
    st.markdown("**CDT Bancolombia vs. Nu / Lulo**")
    st.caption("Capital: $20.000.000 COP")
    st.markdown(
        "- **Interés simple vs. compuesto:** Retiro periódico de intereses vs. capitalización continua.\n"
        "- **Rentabilidad real:** Impacto de la retención en la fuente (4%) e inflación (Ecuación de Fisher).\n"
        "- **Liquidez:** Dinero bloqueado vs. disponibilidad 24/7."
    )
    if st.button("Explorar Caso de Inversión", key="btn_caso2", use_container_width=True):
        st.switch_page("paginas/casos_aplicados.py")

with col_c3, estilos.tarjeta("card_caso3"):
    st.markdown("#### 📈 Ahorro para Cuota Inicial")
    st.markdown("**Gradiente Aritmético y Geométrico**")
    st.caption("Plan a 36 meses al 0,60% MV")
    st.markdown(
        "- **Aportes crecientes:** Inicio suave con $500.000 y subidas de $25.000/mes o 2%/mes.\n"
        "- **Equivalencia uniforme:** Cuota fija equivalente para acumular el mismo capital final ($VF).\n"
        "- **Poder del interés:** Más del 12% del capital proviene de rendimientos ganados."
    )
    if st.button("Explorar Caso de Gradientes", key="btn_caso3", use_container_width=True):
        st.switch_page("paginas/casos_aplicados.py")

st.divider()

# ==============================================================================
# SECCIÓN 2: MÓDULOS TEMÁTICOS Y MOTOR FINANCIERO
# ==============================================================================
st.subheader("📚 Módulos de Cálculo y Fundamentos")
st.caption("Laboratorios interactivos organizados según el avance del programa académico.")

m1, m2 = st.columns(2, gap="medium")

with m1:
    with estilos.tarjeta("mod_is"):
        st.markdown("##### 1. Interés Simple")
        st.markdown(
            "Cálculo de valor futuro ($VF$), valor presente ($VP$), tasas y plazos bajo capitalización lineal. "
            "Soporte para convención comercial (360 días) y exacta (365 días)."
        )
        if st.button("Ir a Interés Simple", key="btn_nav_is", use_container_width=True):
            st.switch_page("paginas/interes_simple.py")

    with estilos.tarjeta("mod_tasas"):
        st.markdown("##### 3. Rentabilidad y Tasas")
        st.markdown(
            "Conversor central multidireccional: Efectiva Anual (EA), Nominales (NAMV, NATV, etc.), "
            "periódicas vencidas y anticipadas, retención en la fuente, tasas combinadas (IPC + puntos) y tasa real."
        )
        if st.button("Ir a Rentabilidad y Tasas", key="btn_nav_tasas", use_container_width=True):
            st.switch_page("paginas/rentabilidad_tasas.py")

    with estilos.tarjeta("mod_grad"):
        st.markdown("##### 5. Gradientes Aritmético y Geométrico")
        st.markdown(
            "Modelación de flujos variables que aumentan o disminuyen en una cantidad fija ($G$) o en un "
            "porcentaje constante ($g$). Cálculo de valor presente, valor futuro y cuota fija equivalente."
        )
        if st.button("Ir a Gradientes", key="btn_nav_grad", use_container_width=True):
            st.switch_page("paginas/gradientes.py")

with m2:
    with estilos.tarjeta("mod_ic"):
        st.markdown("##### 2. Interés Compuesto")
        st.markdown(
            "El valor del dinero en el tiempo. Capitalización periódica de intereses, frecuencia de capitalización "
            "(diaria, mensual, semestral), regla del tiempo para duplicar y ecuaciones de valor."
        )
        if st.button("Ir a Interés Compuesto", key="btn_nav_ic", use_container_width=True):
            st.switch_page("paginas/interes_compuesto.py")

    with estilos.tarjeta("mod_series"):
        st.markdown("##### 4. Series Uniformes (Anualidades)")
        st.markdown(
            "Flujos constantes periódicos: cuota uniforme ($A$), valor presente ($VP$) y valor futuro ($VF$). "
            "Diferenciación estricta entre anualidades vencidas y anticipadas con diagramas de flujo de caja."
        )
        if st.button("Ir a Series Uniformes", key="btn_nav_series", use_container_width=True):
            st.switch_page("paginas/series_uniformes.py")

    with estilos.tarjeta("mod_amort"):
        st.markdown("##### 6. Amortización y Planes de Pago")
        st.markdown(
            "Tablas completas de amortización: Sistema Francés (cuota fija), Sistema Alemán (abono constante), "
            "periodos de gracia (con y sin pago de intereses) y pagos extras programados o puntuales."
        )
        if st.button("Ir a Amortización", key="btn_nav_amort", use_container_width=True):
            st.switch_page("paginas/amortizacion.py")

st.divider()

# ==============================================================================
# SECCIÓN 3: GUÍA RÁPIDA DE USO DEL TABLERO
# ==============================================================================
st.subheader("💡 Características y Guía de Uso")

guia1, guia2, guia3 = st.columns(3)
with guia1:
    st.markdown("**⚡ Ejemplos en un Clic**")
    st.markdown(
        "Cada módulo incluye botones superiores con ejercicios reales de clase y del mercado financiero colombiano "
        "para cargar datos instantáneamente."
    )
with guia2:
    st.markdown("**🧠 Función 'Explícamelo'**")
    st.markdown(
        "Activa el interruptor en la parte superior derecha de cada pantalla para desplegar explicaciones didácticas "
        "en lenguaje claro y fórmulas matemáticas en KaTeX."
    )
with guia3:
    st.markdown("**📥 Exportación y Verificación**")
    st.markdown(
        "Descarga cualquier tabla de amortización o flujo de caja en formato CSV y revisa las tarjetas de comprobación "
        "automática que validan los resultados contra métodos independientes."
    )
