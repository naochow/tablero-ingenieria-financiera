"""Series uniformes (anualidades) vencidas y anticipadas.

La tasa i es periódica vencida en la periodicidad de las cuotas (convertirla
antes con tasas.tasa_periodica). Anticipada = vencida * (1 + i).
"""

CONOCIDOS = ("cuota", "vp", "vf")


def factor_vp(i, n):
    """a = (1 - (1 + i)^-n) / i; con i = 0 es n."""
    if i == 0:
        return n
    return (1 - (1 + i) ** -n) / i


def factor_vf(i, n):
    """s = ((1 + i)^n - 1) / i; con i = 0 es n."""
    if i == 0:
        return n
    return ((1 + i) ** n - 1) / i


def _ajuste(i, anticipada):
    return (1 + i) if anticipada else 1


def vp_serie(cuota, i, n, anticipada=False):
    """VP = A * a (anticipada: por (1 + i))."""
    return cuota * factor_vp(i, n) * _ajuste(i, anticipada)


def vf_serie(cuota, i, n, anticipada=False):
    """VF = A * s (anticipada: por (1 + i))."""
    return cuota * factor_vf(i, n) * _ajuste(i, anticipada)


def cuota_desde_vp(vp, i, n, anticipada=False):
    """A = VP / a (anticipada: entre (1 + i))."""
    return vp / (factor_vp(i, n) * _ajuste(i, anticipada))


def cuota_desde_vf(vf, i, n, anticipada=False):
    """A = VF / s (anticipada: entre (1 + i))."""
    return vf / (factor_vf(i, n) * _ajuste(i, anticipada))


def resolver_serie(conocido, valor, i, n, anticipada=False):
    """A partir de lo que se conoce (cuota, vp o vf) calcula los tres valores."""
    if conocido == "cuota":
        cuota = valor
    elif conocido == "vp":
        cuota = cuota_desde_vp(valor, i, n, anticipada)
    elif conocido == "vf":
        cuota = cuota_desde_vf(valor, i, n, anticipada)
    else:
        raise ValueError(f"Valor conocido no admitido: {conocido}")
    return {
        "cuota": cuota,
        "vp": vp_serie(cuota, i, n, anticipada),
        "vf": vf_serie(cuota, i, n, anticipada),
    }


def vp_flujo(cuotas, i, anticipada=False):
    """VP descontando cuota por cuota: la primera en t = 1 (vencida) o t = 0 (anticipada).

    Verificación independiente de las fórmulas cerradas; sirve para cualquier flujo.
    """
    inicio = 0 if anticipada else 1
    return sum(c / (1 + i) ** (t + inicio) for t, c in enumerate(cuotas))


def acumulado_serie(cuota, i, n, anticipada=False):
    """Saldo de un ahorro con aportes iguales, periodo a periodo.

    Devuelve listas (periodos, aportes_acumulados, saldos) para t = 1..n.
    Vencida: el aporte llega al final del periodo; anticipada: al inicio y gana intereses ese periodo.
    """
    periodos, aportes, saldos = [], [], []
    saldo = 0
    for t in range(1, int(n) + 1):
        if anticipada:
            saldo = (saldo + cuota) * (1 + i)
        else:
            saldo = saldo * (1 + i) + cuota
        periodos.append(t)
        aportes.append(cuota * t)
        saldos.append(saldo)
    return periodos, aportes, saldos
