# Tablero de Ingeniería Financiera

> **Aplicación web interactiva para la modelación matemática, visualización didáctica y toma de decisiones financieras.**  
> Desarrollado para la asignatura de **Ingeniería Financiera** en la **Universidad Pontificia Bolivariana (UPB)**.

---

## 👥 Autores
* **Naomi Chow Morelos**
* **Daniel Lopez Lopez**

---

## 🚀 Descripción del Proyecto
El **Tablero de Ingeniería Financiera** es una plataforma construida en **Streamlit** y **Python** que reemplaza las hojas de cálculo tradicionales por una experiencia visual, dinámica y matemáticamente rigurosa.

Permite simular, comparar y resolver problemas financieros de la banca y economía colombiana, con validaciones automáticas contra métodos de referencia (`numpy-financial`), explicaciones didácticas paso a paso y visualizaciones interactivas en **Plotly**.

---

## 📊 Estructura de la Aplicación

### 1. Inicio
* **[Panel Principal](paginas/panel_principal.py):** Vista general del tablero, resumen ejecutivo de los 3 casos aplicados, acceso rápido a los 6 módulos y guía de uso.

### 2. Módulos Temáticos
1. **[Interés Simple](paginas/interes_simple.py):** Capitalización lineal, despejes de variables ($P, VF, i, n$), ecuaciones de valor y comparación de año comercial ($360$ días) vs. exacto ($365$ días).
2. **[Interés Compuesto](paginas/interes_compuesto.py):** Valor del dinero en el tiempo, capitalización compuesta, regla del tiempo de duplicación y frecuencias de capitalización.
3. **[Rentabilidad y Tasas](paginas/rentabilidad_tasas.py):** Conversor multidireccional: Efectiva Anual (EA), Nominales (NAMV, NATV, etc.), Periódicas vencidas y anticipadas, retención en la fuente (4%), tasas combinadas (IPC + spread) y tasa real de Fisher.
4. **[Series Uniformes (Anualidades)](paginas/series_uniformes.py):** Anualidades vencidas y anticipadas, cálculo de cuota ($A$), valor presente ($VP$), valor futuro ($VF$) y diagramas de flujo de caja.
5. **[Gradientes](paginas/gradientes.py):** Flujos variables periódicos aritméticos ($+G$ pesos) y geométricos ($+g\%$), cálculo de cuota fija equivalente ($A_{eq}$) y punto de cruce.
6. **[Amortización](paginas/amortizacion.py):** Tablas de amortización con metodología UPB:
   * Sistema Francés (Cuota fija).
   * Sistema Alemán (Abono constante a capital).
   * Periodos de gracia con pago de intereses (parcial) y sin pago de intereses (capitalización total).
   * Pagos extras programados periódicos y abonos extraordinarios puntuales.
   * Sistema colombiano en UVR (Ley de Vivienda 546 de 1999).
   * Comprobación por ecuación de valor (`Vr. cuotas mes 0`).

### 3. Casos Prácticos Aplicados
* **🚗 Caso 1: Crédito de Vehículo (Sufi vs. Davivienda):** Comparación justa de cotizaciones en MV y NAMV ($35.000.000 COP a 48 meses), evaluación de liquidez (Francés) vs. minimización de costo (Alemán).
* **🏦 Caso 2: Inversión y Rentabilidad Real (CDT Bancolombia vs. Nu / Lulo Bank):** Interés simple vs. compuesto, retención en la fuente, inflación y dilema de liquidez.
* **📈 Caso 3: Ahorro Programado para Cuota Inicial con Gradientes:** Plan a 36 meses al 0,60% MV con gradiente aritmético vs. geométrico y cuota uniforme equivalente.

### 4. Memoria Técnica
* **[Supuestos y Fórmulas](paginas/supuestos_formulas.py):** Marco normativo colombiano (SFC, Ley 546/1999, Estatuto Tributario), criterios de precisión y formulario matemático completo en LaTeX.

---

## 🛠️ Tecnologías y Librerías

* **Lenguaje:** Python 3.12+
* **Interfaz de Usuario:** Streamlit (>= 1.40)
* **Gráficos Interactivos:** Plotly (>= 5.24)
* **Cálculo y Manipulación de Datos:** Pandas, NumPy, NumPy-Financial
* **Pruebas Unitarias:** Pytest (>= 8.0)

---

## 💻 Instalación y Ejecución Local

1. **Clonar el repositorio:**
   ```bash
   git clone https://github.com/naochow/tablero-ingenieria-financiera.git
   cd tablero-ingenieria-financiera
   ```

2. **Crear y activar un entorno virtual (recomendado):**
   ```bash
   python -m venv .venv
   # En Windows:
   .venv\Scripts\activate
   # En Linux/Mac:
   source .venv/bin/activate
   ```

3. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Ejecutar la aplicación:**
   ```bash
   streamlit run app.py
   ```

5. **Correr las pruebas unitarias:**
   ```bash
   pytest
   ```

---

## 🌐 Despliegue en Streamlit Community Cloud
La aplicación está configurada para despliegue continuo en **Streamlit Cloud** apuntando a `app.py` en la rama `main`.
