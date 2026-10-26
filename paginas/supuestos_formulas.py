"""Página de supuestos, fórmulas y convenciones: memoria técnica y glosario del tablero."""

import streamlit as st

from componentes import estilos

TEMA = "supuestos"
COLOR = estilos.TEMAS[TEMA]["color"]

explicar = estilos.encabezado(
    TEMA,
    "Supuestos y Fórmulas Financieras",
    "Memoria técnica del motor de cálculo: supuestos normativos colombianos, ecuaciones de valor y compendio completo de fórmulas.",
)

# Tabs principales
tab_supuestos, tab_formulas, tab_referencias = st.tabs(
    ["📌 Supuestos y Convenciones", "📐 Formulario Matemático Completo", "📖 Referencias y Marco Normativo"]
)

with tab_supuestos:
    st.subheader("Supuestos del Motor de Cálculo")

    c1, c2 = st.columns(2, gap="large")

    with c1:
        with estilos.tarjeta("sup_mercado"):
            st.markdown("#### 🇨🇴 Convenciones del Mercado Colombiano")
            st.markdown(
                "- **Regla de oro de tasas:** Las tasas efectivas nunca se multiplican ni se dividen por un factor simple. "
                "Cualquier equivalencia entre periodicidades se realiza mediante la tasa **Efectiva Anual (E.A.)** "
                "como pivote central.\n"
                "- **Convención de días en el año:**\n"
                "  - *Año comercial:* $360$ días ($12$ meses de $30$ días), estándar en la banca colombiana para créditos y CDT tradicionales.\n"
                "  - *Año real o exacto:* $365$ días (o $366$ en bisiesto), utilizado en cuentas de alto rendimiento con capitalización diaria (Nu, Lulo, Ualá).\n"
                "- **Periodicidades estándar:** Mensual ($12$), Bimestral ($6$), Trimestral ($4$), Semestral ($2$) y Anual ($1$).\n"
                "- **Retención en la fuente:** Se aplica una tasa fija del **4%** sobre los rendimientos financieros brutos generados en productos de renta fija (según el Estatuto Tributario colombiano)."
            )

    with c2:
        with estilos.tarjeta("sup_computo"):
            st.markdown("#### 💻 Criterios de Precisión y Cómputo")
            st.markdown(
                "- **Precisión aritmética:** Todos los cálculos internos se realizan con aritmética de punto flotante IEEE 754 "
                "de doble precisión ($64$ bits), asegurando tolerancias menores a $10^{-6}$ en tasas y $1$ peso en flujos.\n"
                "- **Formato numérico colombiano:**\n"
                "  - Separador de miles: punto (`.`)\n"
                "  - Separador decimal: coma (`,`)\n"
                "  - Moneda: Peso Colombiano (`$ COP`)\n"
                "- **Cierre contable en amortizaciones:** El saldo final en cualquier tabla de amortización se extingue "
                "exactamente en cero ($0$), ajustando el último pago ordinario para evitar centavos de arrastre."
            )

with tab_formulas:
    st.subheader("Compendio de Fórmulas Financieras")

    with st.expander("1. Interés Simple", expanded=True):
        st.markdown(
            "Los intereses se calculan exclusivamente sobre el capital inicial inicial ($P$) y no se capitalizan."
        )
        st.latex(r"I = P \cdot i \cdot n \qquad VF = P\,(1 + i \cdot n) \qquad VP = \frac{VF}{1 + i \cdot n}")
        st.latex(r"i = \frac{VF/VP - 1}{n} \qquad n = \frac{VF/VP - 1}{i}")
        st.caption("Donde P: Capital inicial, i: Tasa periódica simple, n: Plazo, I: Intereses totales, VF: Valor futuro.")

    with st.expander("2. Interés Compuesto", expanded=True):
        st.markdown(
            "Los intereses causados se suman periódicamente al capital, generando nuevos intereses en cada ciclo."
        )
        st.latex(r"VF = P\,(1 + i)^n \qquad VP = \frac{VF}{(1 + i)^n} = VF\,(1 + i)^{-n}")
        st.latex(r"i = \left(\frac{VF}{VP}\right)^{\frac{1}{n}} - 1 \qquad n = \frac{\ln(VF / VP)}{\ln(1 + i)}")
        st.markdown("**Regla del tiempo de duplicación:**")
        st.latex(r"n_{\text{duplicar}} = \frac{\ln(2)}{\ln(1 + i)}")

    with st.expander("3. Conversión y Equivalencia de Tasas", expanded=True):
        st.markdown("**De Tasa Periódica a Efectiva Anual (EA) y viceversa:**")
        st.latex(r"EA = (1 + i_p)^m - 1 \qquad i_p = (1 + EA)^{\frac{1}{m}} - 1")
        st.markdown("**De Tasa Anticipada a Vencida y viceversa:**")
        st.latex(r"i_v = \frac{i_a}{1 - i_a} \qquad i_a = \frac{i_v}{1 + i_v}")
        st.markdown("**Tasa Nominal Anual ($J$):**")
        st.latex(r"J = i_p \cdot m \qquad i_p = \frac{J}{m}")
        st.markdown("**Tasa Real neta de Inflación (Ecuación de Fisher) y Tasa Combinada:**")
        st.latex(r"r_{\text{real}} = \frac{1 + EA}{1 + \text{IPC}} - 1 \qquad i_{\text{combinada}} = (1 + \text{tasa}_1)(1 + \text{tasa}_2) - 1")

    with st.expander("4. Series Uniformes (Anualidades)", expanded=True):
        st.markdown("**Factores de descuento ($a$) y capitalización ($s$):**")
        st.latex(r"a_{\overline{n}|i} = \frac{1 - (1 + i)^{-n}}{i} \qquad s_{\overline{n}|i} = \frac{(1 + i)^n - 1}{i}")
        st.markdown("**Valor Presente ($VP$) y Valor Futuro ($VF$) para series vencidas:**")
        st.latex(r"VP = A \cdot a_{\overline{n}|i} \qquad VF = A \cdot s_{\overline{n}|i} \qquad A = \frac{VP}{a_{\overline{n}|i}} = \frac{VF}{s_{\overline{n}|i}}")
        st.markdown("**Series Anticipadas:**")
        st.latex(r"VP_{\text{anticipada}} = A \cdot a_{\overline{n}|i} \cdot (1 + i) \qquad VF_{\text{anticipada}} = A \cdot s_{\overline{n}|i} \cdot (1 + i)")

    with st.expander("5. Gradientes Aritmético y Geométrico", expanded=True):
        st.markdown("**Gradiente Aritmético (Variación lineal fija $G$):**")
        st.latex(r"A_t = A_1 + (t - 1)\,G")
        st.latex(r"VP = A_1 \cdot a_{\overline{n}|i} + \frac{G}{i}\left[a_{\overline{n}|i} - n\,(1 + i)^{-n}\right]")
        st.latex(r"VF = VP \cdot (1 + i)^n")
        st.markdown("**Gradiente Geométrico (Variación porcentual fija $g$):**")
        st.latex(r"A_t = A_1\,(1 + g)^{t - 1}")
        st.latex(r"\text{Si } g \neq i: \quad VP = A_1 \cdot \left[\frac{1 - \left(\frac{1 + g}{1 + i}\right)^n}{i - g}\right] \qquad \text{Si } g = i: \quad VP = \frac{A_1 \cdot n}{1 + i}")
        st.markdown("**Cuota Uniforme Equivalente ($A_{eq}$):**")
        st.latex(r"A_{eq} = \frac{VP}{a_{\overline{n}|i}} = \frac{VF}{s_{\overline{n}|i}}")

    with st.expander("6. Modelos de Amortización y Pagos Extras", expanded=True):
        st.markdown("**Sistema Francés (Cuota Fija):**")
        st.latex(r"A = P \cdot \frac{i}{1 - (1 + i)^{-n}} \qquad I_t = \text{Saldo}_{t-1} \cdot i \qquad C_t = A - I_t \qquad \text{Saldo}_t = \text{Saldo}_{t-1} - C_t")
        st.markdown("**Sistema Alemán (Abono Constante a Capital):**")
        st.latex(r"C = \frac{P}{n} \qquad I_t = \text{Saldo}_{t-1} \cdot i \qquad A_t = C + I_t \qquad \text{Saldo}_t = \text{Saldo}_{t-1} - C")
        st.markdown("**Cuota Fija con Pagos Extras Periódicos Programados (Metodología UPB):**")
        st.latex(r"VA_{\text{extras}} = A_{\text{extra}} \cdot \frac{1 - (1 + i_{\text{extra}})^{-k}}{i_{\text{extra}}} \qquad VA_{\text{ordinario}} = P - VA_{\text{extras}}")
        st.latex(r"A_{\text{ordinaria}} = \frac{VA_{\text{ordinario}}}{a_{\overline{n}|i_{\text{mensual}}}}")
        st.markdown("**Comprobación por Ecuación de Valor (Columna 'Vr. cuotas mes 0'):**")
        st.latex(r"\text{Vr. cuota mes 0}_t = \frac{\text{Cuota Total}_t}{(1 + i)^t} \qquad \sum_{t=1}^{n} \text{Vr. cuota mes 0}_t = P")

with tab_referencias:
    st.subheader("Marco Teórico y Referencias Bibliográficas")

    st.markdown(
        """
        1. **García, Jaime.** *Matemáticas Financieras con Ecuaciones de Diferencia Finita.* Editorial Pearson, Colombia.
        2. **Meza Orozco, Jhonny de Jesús.** *Matemáticas Financieras Aplicadas: Uso de las funciones de Excel y herramientas interactivas.* Ecoe Ediciones, Bogotá.
        3. **Superintendencia Financiera de Colombia (SFC).** *Circular Básica Contable y Financiera (Circular Externa 100 de 1995)*: Normas sobre equivalencia y expresión de tasas de interés y sistemas de amortización en créditos.
        4. **Congreso de la República de Colombia.** *Ley 546 de 1999 (Ley Marco de Vivienda)*: Reglamentación de los sistemas de financiación en Pesos y UVR.
        5. **Estatuto Tributario de Colombia.** *Artículos 395 a 404-1*: Régimen de retención en la fuente sobre rendimientos financieros derivados de títulos de renta fija y depósitos a la vista.
        """
    )
