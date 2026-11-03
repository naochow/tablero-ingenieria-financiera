"""Decisiones de los casos aplicados: quién gana sale de estos cálculos, en la página del caso y en el panel."""

from finanzas import gradientes

EMPATE_PESOS = 1


def gana_cuenta(rendimiento_cuenta, rendimiento_cdt):
    """True si conviene la cuenta. En empate (un peso) también: rinde lo mismo y conserva la liquidez."""
    return rendimiento_cuenta >= rendimiento_cdt - EMPATE_PESOS


def _plan(clave, nombre, cuotas, vp, i, n, meta):
    vf = gradientes.vf_gradiente(vp, i, n)
    cuota_equivalente = gradientes.cuota_equivalente(vp, i, n)
    return {
        "clave": clave,
        "nombre": nombre,
        "cuotas": cuotas,
        "vf": vf,
        "aportes": sum(cuotas),
        "diferencia_meta": vf - meta,
        "alcanza": vf >= meta,
        "cuota_equivalente": cuota_equivalente,
        "cruce": gradientes.periodo_cruce(cuotas, cuota_equivalente),
    }


def comparar_planes(a1, G, g, i, n, meta):
    """Plan aritmético y geométrico con la misma primera cuota, tasa y plazo, cada uno frente a la meta."""
    return [
        _plan("aritmetico", "Gradiente aritmético", gradientes.cuotas_aritmetico(a1, G, n),
              gradientes.vp_aritmetico(a1, G, i, n), i, n, meta),
        _plan("geometrico", "Gradiente geométrico", gradientes.cuotas_geometrico(a1, g, n),
              gradientes.vp_geometrico(a1, g, i, n), i, n, meta),
    ]


def plan_recomendado(planes):
    """Devuelve (plan, motivo).

    motivo: "unico" si solo uno alcanza la meta; "menos_aportes" si ambos la alcanzan y este exige
    menos dinero propio; "mas_cercano" si ninguno la alcanza y este es el que más se acerca.
    """
    alcanzan = [p for p in planes if p["alcanza"]]
    if len(alcanzan) == 1:
        return alcanzan[0], "unico"
    if alcanzan:
        return min(alcanzan, key=lambda p: p["aportes"]), "menos_aportes"
    return max(planes, key=lambda p: p["vf"]), "mas_cercano"
