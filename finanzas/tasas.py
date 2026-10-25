"""Conversor central de tasas, retención en la fuente y tasas combinadas.

Todas las tasas son decimales (0.175, no 17.5). Toda conversión pasa por la
efectiva anual (EA); nunca se dividen tasas efectivas.
"""

import pandas as pd

PERIODOS_POR_ANO = {
    "diaria": 360,
    "mensual": 12,
    "bimestral": 6,
    "trimestral": 4,
    "semestral": 2,
    "anual": 1,
}

TIPOS = ("periodica", "nominal", "efectiva")
MODALIDADES = ("vencida", "anticipada")

# Código de tasa -> (tipo, periodicidad, modalidad)
CODIGOS = {
    "MV": ("periodica", "mensual", "vencida"),
    "MA": ("periodica", "mensual", "anticipada"),
    "TV": ("periodica", "trimestral", "vencida"),
    "TA": ("periodica", "trimestral", "anticipada"),
    "SV": ("periodica", "semestral", "vencida"),
    "NAMV": ("nominal", "mensual", "vencida"),
    "NATV": ("nominal", "trimestral", "vencida"),
    "NATA": ("nominal", "trimestral", "anticipada"),
    "EA": ("efectiva", "anual", "vencida"),
}


def periodos_por_ano(periodicidad):
    """Número de periodos en un año para la periodicidad dada."""
    try:
        return PERIODOS_POR_ANO[periodicidad]
    except KeyError:
        raise ValueError(f"Periodicidad no admitida: {periodicidad}") from None


def anticipada_a_vencida(ia):
    """Tasa periódica anticipada a vencida: iv = ia / (1 - ia)."""
    if ia >= 1:
        raise ValueError("La tasa anticipada debe ser menor que 100%.")
    return ia / (1 - ia)


def vencida_a_anticipada(iv):
    """Tasa periódica vencida a anticipada: ia = iv / (1 + iv)."""
    return iv / (1 + iv)


def ea_desde_periodica(i, m):
    """EA a partir de la tasa periódica vencida con m periodos por año."""
    return (1 + i) ** m - 1


def periodica_desde_ea(ea, m):
    """Tasa periódica vencida a partir de la EA: i = (1 + EA)^(1/m) - 1."""
    return (1 + ea) ** (1 / m) - 1


def a_efectiva_anual(valor, tipo, periodicidad="anual", modalidad="vencida"):
    """Convierte cualquier tasa a EA.

    tipo: "periodica", "nominal" o "efectiva" (efectiva anual).
    periodicidad: clave de PERIODOS_POR_ANO; se ignora si el tipo es efectiva.
    modalidad: "vencida" o "anticipada".
    """
    if tipo not in TIPOS:
        raise ValueError(f"Tipo de tasa no admitido: {tipo}")
    if modalidad not in MODALIDADES:
        raise ValueError(f"Modalidad no admitida: {modalidad}")

    m = 1 if tipo == "efectiva" else periodos_por_ano(periodicidad)
    periodica = valor / m if tipo == "nominal" else valor
    if modalidad == "anticipada":
        periodica = anticipada_a_vencida(periodica)
    return ea_desde_periodica(periodica, m)


def desde_efectiva_anual(ea, tipo, periodicidad="anual", modalidad="vencida"):
    """Convierte una EA al tipo, periodicidad y modalidad pedidos (inversa de a_efectiva_anual)."""
    if tipo not in TIPOS:
        raise ValueError(f"Tipo de tasa no admitido: {tipo}")
    if modalidad not in MODALIDADES:
        raise ValueError(f"Modalidad no admitida: {modalidad}")

    m = 1 if tipo == "efectiva" else periodos_por_ano(periodicidad)
    periodica = periodica_desde_ea(ea, m)
    if modalidad == "anticipada":
        periodica = vencida_a_anticipada(periodica)
    return periodica * m if tipo == "nominal" else periodica


def tasa_periodica(valor, tipo, periodicidad, modalidad, periodicidad_flujo):
    """Tasa periódica vencida en la periodicidad del flujo, pasando por la EA."""
    ea = a_efectiva_anual(valor, tipo, periodicidad, modalidad)
    return periodica_desde_ea(ea, periodos_por_ano(periodicidad_flujo))


def ea_desde_codigo(valor, codigo):
    """EA de una tasa expresada con su código (ej. 0.014, "MV")."""
    try:
        tipo, periodicidad, modalidad = CODIGOS[codigo.upper()]
    except KeyError:
        raise ValueError(f"Código de tasa no admitido: {codigo}") from None
    return a_efectiva_anual(valor, tipo, periodicidad, modalidad)


def tabla_equivalencias(ea):
    """Tasas equivalentes a una EA en las seis periodicidades."""
    filas = []
    for periodicidad, m in PERIODOS_POR_ANO.items():
        iv = periodica_desde_ea(ea, m)
        ia = vencida_a_anticipada(iv)
        filas.append(
            {
                "periodicidad": periodicidad,
                "periodos_por_ano": m,
                "periodica_vencida": iv,
                "nominal_vencida": iv * m,
                "periodica_anticipada": ia,
                "nominal_anticipada": ia * m,
            }
        )
    return pd.DataFrame(filas)


def tea_neta(tea, retencion=0.07):
    """TEA después de retención en la fuente sobre los intereses: TEA * (1 - r)."""
    return tea * (1 - retencion)


def tasa_combinada(ipc, puntos):
    """Tasa compuesta de IPC más puntos: (1 + IPC)(1 + puntos) - 1."""
    return (1 + ipc) * (1 + puntos) - 1


def tasa_real(tea, ipc):
    """Rentabilidad real descontando inflación: (1 + TEA)/(1 + IPC) - 1."""
    return (1 + tea) / (1 + ipc) - 1
