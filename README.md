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
* **[Panel Principal](paginas/panel_principal.py):** Vista general del tablero, resumen ejecutivo de los 3 casos aplicados, acceso rápido a los 6 módulos y verificaciones del tablero: cada módulo y caso compara sus fórmulas con un método alternativo, con tolerancia de 1 peso, y la tarjeta muestra cualquier fallo.

### 2. Módulos Temáticos
1. **[Interés Simple](paginas/interes_simple.py):** Capitalización lineal, despejes de variables ($P, VF, i, n$) y comparación de año comercial ($360$ días) vs. exacto ($365$ días).
2. **[Interés Compuesto](paginas/interes_compuesto.py):** Valor del dinero en el tiempo, capitalización compuesta, regla del tiempo de duplicación y frecuencias de capitalización.
3. **[Rentabilidad y Tasas](paginas/rentabilidad_tasas.py):** Conversor multidireccional: Efectiva Anual (EA), Nominales (NAMV, NATV, etc.), Periódicas vencidas y anticipadas, retención en la fuente (4% CDT / 7% cuentas de ahorro), tasas combinadas (IPC + spread) y tasa real de Fisher.
4. **[Series Uniformes (Anualidades)](paginas/series_uniformes.py):** Anualidades vencidas y anticipadas, cálculo de cuota ($A$), valor presente ($VP$), valor futuro ($VF$) y diagramas de flujo de caja.
5. **[Gradientes](paginas/gradientes.py):** Flujos variables periódicos aritméticos ($+G$ pesos) y geométricos ($+g\%$), cálculo de cuota fija equivalente ($A_{eq}$) y punto de cruce.
6. **[Amortización](paginas/amortizacion.py):** Tablas de amortización con metodología UPB:
   * Sistema Francés (Cuota fija).
   * Sistema Alemán (Abono constante a capital).
   * Periodos de gracia con pago de intereses (parcial) y sin pago de intereses (capitalización total).
   * Pagos extras programados periódicos (solo con cuotas mensuales) y abonos extraordinarios puntuales.
   * Comprobación por ecuación de valor (`Vr. cuotas mes 0`).

### 3. Casos Prácticos Aplicados
* **🚗 Caso 1: Crédito de Vehículo (Sufi vs. Davivienda):** Comparación justa de cotizaciones en MV y NAMV ($35.000.000 COP a 48 meses), evaluación de liquidez (Francés) vs. minimización de costo (Alemán). La entidad recomendada se calcula comparando las dos tasas en E.A.
* **🏦 Caso 2: Inversión y Rentabilidad Real (CDT Bancolombia vs. Nu):** Interés simple vs. compuesto, retención en la fuente, inflación y dilema de liquidez. La alternativa recomendada es la de mayor rendimiento neto.
* **📈 Caso 3: Ahorro Programado para Cuota Inicial con Gradientes (Fiducuenta):** Plan a 36 meses con rentabilidad de 9,07% E.A. (último año, rentabilidad reportada por el fondo, que ya refleja la comisión de administración; no garantizada), gradiente aritmético vs. geométrico y cuota uniforme equivalente. Cada plan se compara con una meta de ahorro editable (supuesto).

### 4. Memoria Técnica
* **[Supuestos y Fórmulas](paginas/supuestos_formulas.py):** Marco normativo colombiano (SFC, Ley 546/1999, Estatuto Tributario), criterios de precisión y formulario matemático completo en LaTeX.

---

## 📚 Fuentes de los Datos

Los valores de los casos están en [datos/casos.json](datos/casos.json).

| Dato | Valor | Fuente | Fecha |
|---|---|---|---|
| Crédito de vehículo Sufi (Caso 1) | 1,85% MV | [Simulador Sufi](https://simulador.sufi.apps.bancolombia.com/) | Consultado el 2 de noviembre de 2026; tasa de política con corte a octubre de 2025 |
| Crédito de vehículo Davivienda (Caso 1) | 15,96% NAMV | [Simulador de vehículo Davivienda](https://misfinanzasencasa.davivienda.com/finanzas-personales/simuladores/simulador-de-credito-de-vehiculo/) | Consultado el 2 de noviembre de 2026 |
| CDT Bancolombia (Caso 2) | 9,35% EA | [Simulador CDT Bancolombia](https://www.bancolombia.com/personas/productos/inversiones/simulador-cdt) | Consultado el 2 de noviembre de 2026 |
| Retención del CDT en el simulador (Caso 2) | $74.800 sobre $1.870.000 de intereses (4%) | [Simulador CDT Bancolombia](https://www.bancolombia.com/personas/productos/inversiones/simulador-cdt) | Consultado el 2 de noviembre de 2026 |
| Cajitas de Nu, clientes regulares (Caso 2) | 9,35% EA | [Forbes Colombia](https://forbes.co/economia-y-finanzas/donde-poner-sus-ahorros-para-ganar-mas-intereses-estas-son-las-tasas-que-ofrecen-los-bancos-en-colombia) | 20 de octubre de 2026 |
| Inflación anual, IPC (Casos 2 y 3) | 6,29% | [DANE, boletín IPC septiembre 2026](https://www.dane.gov.co/files/operaciones/IPC/sep2026/bol-IPC-sep2026.pdf) | 7 de octubre de 2026 |
| Retención en la fuente (E.T. art. 395 y decretos reglamentarios) | 4% CDT y 7% cuentas de ahorro | [Valora Analitik](https://www.valoraanalitik.com/diferencias-retencion-fuente-cdt-cuenta-ahorros/) | 9 de enero de 2025 |
| Seguro de depósitos (Caso 2) | Tope de $50.000.000 por persona en cada entidad | [Fogafín, Resolución JD 001 de 2026](https://www.fogafin.gov.co/sites/default/files/2026-05/Resolucion%20JD%20001%20de%202026.pdf) | 20 de mayo de 2026 |
| Rentabilidad de Fiducuenta, último año (Caso 3) | 9,07% EA, reportada por el fondo; no garantizada | [Rankia Colombia](https://www.rankia.co/blog/fondos-inversion-colectiva-colombia/4682852-fiducuenta-bancolombia-beneficios-comisiones) | Datos al 22 de octubre de 2026 |
| Meta de ahorro (Caso 3) | $36.000.000, editable | Supuesto del trabajo, sin fuente externa | No aplica |

---

## 🛠️ Tecnologías y Librerías

* **Lenguaje:** Python 3.11 o superior
* **Interfaz de Usuario:** Streamlit (>= 1.50)
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
