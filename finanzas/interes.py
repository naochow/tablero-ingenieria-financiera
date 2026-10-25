"""Interés simple y compuesto: valor futuro, valor presente y despejes.

Las tasas son decimales. En interés simple la tasa y el plazo se llevan a años
con la convención de días (360 por defecto). En compuesto, la tasa es periódica
y n está en esos mismos periodos.
"""

import math

from finanzas.tasas import ea_desde_periodica

UNIDADES_PLAZO = ("dias", "meses", "anos")
UNIDADES_TASA = ("anual", "mensual")


def _validar_positivo(**valores):
    for nombre, valor in valores.items():
        if valor <= 0:
            raise ValueError(f"{nombre} debe ser mayor que cero.")


# --- Interés simple ---

def plazo_en_anos(plazo, unidad, dias_ano=360):
    """Plazo expresado en años según su unidad y la convención de días."""
    if dias_ano not in (360, 365):
        raise ValueError("La convención de días debe ser 360 o 365.")
    if unidad == "dias":
        return plazo / dias_ano
    if unidad == "meses":
        return plazo / 12
    if unidad == "anos":
        return plazo
    raise ValueError(f"Unidad de plazo no admitida: {unidad}")


def tasa_simple_anual(tasa, unidad):
    """Tasa simple anual; en interés simple la mensual es proporcional (i * 12)."""
    if unidad == "anual":
        return tasa
    if unidad == "mensual":
        return tasa * 12
    raise ValueError(f"Unidad de tasa no admitida: {unidad}")


def interes_simple(capital, tasa, n):
    """I = P * i * n."""
    return capital * tasa * n


def vf_simple(capital, tasa, n):
    """VF = P * (1 + i * n)."""
    return capital * (1 + tasa * n)


def vp_simple(vf, tasa, n):
    """VP = VF / (1 + i * n)."""
    return vf / (1 + tasa * n)


def tasa_simple(vp, vf, n):
    """i = (VF / VP - 1) / n."""
    _validar_positivo(vp=vp, n=n)
    return (vf / vp - 1) / n


def plazo_simple(vp, vf, tasa):
    """n = (VF / VP - 1) / i."""
    _validar_positivo(vp=vp, tasa=tasa)
    return (vf / vp - 1) / tasa


def acumulado_simple(capital, tasa_periodo, n_periodos):
    """Saldo periodo a periodo sumando el interés de cada periodo sobre el capital inicial.

    Devuelve listas (periodos, saldos) desde 0 hasta n_periodos; si n_periodos no es
    entero, el último tramo es fraccionario. Sirve de verificación iterativa de vf_simple.
    """
    periodos, saldos = [0], [capital]
    saldo, t = capital, 0
    while t < n_periodos:
        tramo = min(1, n_periodos - t)
        saldo += capital * tasa_periodo * tramo
        t += tramo
        periodos.append(t)
        saldos.append(saldo)
    return periodos, saldos


# --- Interés compuesto ---

def vf_compuesto(capital, tasa, n):
    """VF = P * (1 + i)^n."""
    return capital * (1 + tasa) ** n


def vp_compuesto(vf, tasa, n):
    """VP = VF / (1 + i)^n."""
    return vf / (1 + tasa) ** n


def tasa_compuesta(vp, vf, n):
    """i = (VF / VP)^(1/n) - 1."""
    _validar_positivo(vp=vp, vf=vf, n=n)
    return (vf / vp) ** (1 / n) - 1


def periodos_compuesto(vp, vf, tasa):
    """n = ln(VF / VP) / ln(1 + i)."""
    _validar_positivo(vp=vp, vf=vf, tasa=tasa)
    return math.log(vf / vp) / math.log(1 + tasa)


def tiempo_duplicar(tasa):
    """Periodos para duplicar el capital: ln 2 / ln(1 + i)."""
    _validar_positivo(tasa=tasa)
    return math.log(2) / math.log(1 + tasa)


def acumulado_compuesto(capital, tasa, n_periodos):
    """Saldo capitalizando periodo a periodo (verificación iterativa de vf_compuesto).

    Devuelve listas (periodos, saldos) desde 0 hasta n_periodos; un tramo final
    fraccionario se capitaliza con (1 + i)^tramo.
    """
    periodos, saldos = [0], [capital]
    saldo, t = capital, 0
    while t < n_periodos:
        tramo = min(1, n_periodos - t)
        saldo *= (1 + tasa) ** tramo
        t += tramo
        periodos.append(t)
        saldos.append(saldo)
    return periodos, saldos


FRECUENCIAS_CAPITALIZACION = {
    "anual": 1,
    "semestral": 2,
    "trimestral": 4,
    "mensual": 12,
    "diaria": 360,
}


def tabla_frecuencias(capital, nominal, anos):
    """VF y EA de una misma tasa nominal anual con distintas frecuencias de capitalización."""
    filas = []
    for frecuencia, m in FRECUENCIAS_CAPITALIZACION.items():
        periodica = nominal / m
        vf = vf_compuesto(capital, periodica, m * anos)
        filas.append(
            {
                "frecuencia": frecuencia,
                "periodos_por_ano": m,
                "tasa_periodica": periodica,
                "ea": ea_desde_periodica(periodica, m),
                "valor_futuro": vf,
                "intereses": vf - capital,
            }
        )
    return filas
