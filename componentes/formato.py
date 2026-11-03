"""Formato colombiano para mostrar valores: punto de miles y coma decimal.

Las tasas llegan como decimales (0.1956) y se convierten a porcentaje solo aquí.
"""

# Separadores para Plotly (layout.separators): decimal y luego miles
SEPARADORES_PLOTLY = ",."


def numero(valor, decimales=0):
    """Número con punto de miles y coma decimal: 1234567.891 -> "1.234.567,89"."""
    texto = f"{abs(valor):,.{decimales}f}"
    texto = texto.replace(",", "_").replace(".", ",").replace("_", ".")
    # Evita mostrar "-0" cuando el valor redondeado es cero
    if valor < 0 and texto.strip("0.,") != "":
        return "-" + texto
    return texto


def pesos(valor, decimales=0):
    """Valor en COP: 1234567 -> "$ 1.234.567"; negativos como "-$ 1.234.567"."""
    texto = numero(valor, decimales)
    if texto.startswith("-"):
        return "-$ " + texto[1:]
    return "$ " + texto


def escapar_md(texto):
    """Escapa "$" para que Streamlit no lo tome como LaTeX en markdown, avisos, botones y etiquetas."""
    return texto.replace("$", r"\$")


def supuesto_retencion_cuenta(interes_diario, retencion):
    """Supuesto de retención de la cuenta de ahorros en markdown, con el interés diario redondeado a dos cifras."""
    unos = float(f"{interes_diario:.2g}")
    return (
        f"**Supuesto:** la retención del {porcentaje_compacto(retencion)} se aplica sobre la totalidad de los intereses de la cuenta de ahorros. "
        f"Con el capital del caso, el interés diario (unos \\${numero(unos)} con año de 360 días) supera ampliamente "
        "cualquier base mínima diaria."
    )


def pesos_md(valor, decimales=0):
    """pesos() para textos con markdown. En tablas, Plotly y bloques HTML el escape se vería literal: usar pesos()."""
    return escapar_md(pesos(valor, decimales))


def porcentaje(tasa, decimales=2):
    """Tasa decimal como porcentaje: 0.195618 -> "19,56%"."""
    return numero(tasa * 100, decimales) + "%"


def porcentaje_compacto(tasa):
    """Porcentaje sin decimales si es entero: 0.07 -> "7%"; 0.075 -> "7,50%"."""
    return porcentaje(tasa, 0 if round(tasa * 100, 6).is_integer() else 2)


def tasa_con_codigo(tasa, codigo, decimales=2):
    """Tasa con su código: (0.014, "MV") -> "1,40% MV"."""
    return f"{porcentaje(tasa, decimales)} {codigo.upper()}"
