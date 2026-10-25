"""Gradientes aritmético y geométrico (vencidos), crecientes o decrecientes.

La tasa i es periódica vencida en la periodicidad de las cuotas. G es el
incremento fijo en pesos; g es el incremento porcentual (decimal).
"""

import math

from finanzas.series import factor_vp


def cuotas_aritmetico(a1, gradiente, n):
    """Cuotas A1, A1 + G, A1 + 2G, ... para t = 1..n."""
    return [a1 + gradiente * (t - 1) for t in range(1, int(n) + 1)]


def cuotas_geometrico(a1, g, n):
    """Cuotas A1, A1(1 + g), A1(1 + g)^2, ... para t = 1..n."""
    return [a1 * (1 + g) ** (t - 1) for t in range(1, int(n) + 1)]


def _factor_aritmetico(i, n):
    """Factor del gradiente en VP = A1*a + G*factor: (a - n(1 + i)^-n) / i; con i = 0 es n(n - 1)/2."""
    if i == 0:
        return n * (n - 1) / 2
    return (factor_vp(i, n) - n * (1 + i) ** -n) / i


def vp_aritmetico(a1, gradiente, i, n):
    """VP = A1*a + (G/i)*(a - n(1 + i)^-n)."""
    return a1 * factor_vp(i, n) + gradiente * _factor_aritmetico(i, n)


def primera_cuota_aritmetico(vp, gradiente, i, n):
    """A1 que, con el gradiente G, tiene el VP dado."""
    return (vp - gradiente * _factor_aritmetico(i, n)) / factor_vp(i, n)


def _factor_geometrico(g, i, n):
    """VP de una cuota inicial de $1: (1 - ((1 + g)/(1 + i))^n) / (i - g); si g = i, n/(1 + i)."""
    if g <= -1:
        raise ValueError("El gradiente geométrico debe ser mayor que -100%.")
    if math.isclose(g, i, rel_tol=0, abs_tol=1e-12):
        return n / (1 + i)
    return (1 - ((1 + g) / (1 + i)) ** n) / (i - g)


def vp_geometrico(a1, g, i, n):
    """VP = A1 * (1 - ((1 + g)/(1 + i))^n) / (i - g); si g = i, VP = A1*n/(1 + i)."""
    return a1 * _factor_geometrico(g, i, n)


def primera_cuota_geometrico(vp, g, i, n):
    """A1 que, creciendo al g por periodo, tiene el VP dado."""
    return vp / _factor_geometrico(g, i, n)


def vf_gradiente(vp, i, n):
    """VF = VP * (1 + i)^n."""
    return vp * (1 + i) ** n


def cuota_equivalente(vp, i, n):
    """Cuota uniforme con el mismo VP: A_eq = VP / a."""
    return vp / factor_vp(i, n)


def periodo_cruce(cuotas, cuota_fija):
    """Primer periodo (desde 1) en que la cuota con gradiente supera a la cuota fija.

    Si el gradiente es decreciente, el primero en que queda por debajo. None si no cruza.
    """
    crece = cuotas[-1] >= cuotas[0]
    for t, cuota in enumerate(cuotas, start=1):
        if (cuota > cuota_fija) if crece else (cuota < cuota_fija):
            return t
    return None
