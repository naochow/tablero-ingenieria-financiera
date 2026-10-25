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


def porcentaje(tasa, decimales=2):
    """Tasa decimal como porcentaje: 0.195618 -> "19,56%"."""
    return numero(tasa * 100, decimales) + "%"


def tasa_con_codigo(tasa, codigo, decimales=2):
    """Tasa con su código: (0.014, "MV") -> "1,40% MV"."""
    return f"{porcentaje(tasa, decimales)} {codigo.upper()}"
