"""Verificaciones del panel principal: cada módulo y caso se contrasta con una ruta de cálculo distinta.

Cada verificación compara una fórmula con un cálculo independiente (iterativo, descontando
cuota a cuota o con numpy-financial) y falla si difieren en más de un peso.
"""

import numpy_financial as npf

from finanzas import amortizacion, gradientes, interes, series, tasas

TOLERANCIA_PESOS = 1


def comprobar(nombre, calculo, tolerancia=TOLERANCIA_PESOS):
    """Ejecuta calculo() -> (resultado, referencia). Un error en el cálculo cuenta como fallo."""
    try:
        resultado, referencia = calculo()
        ok = bool(abs(resultado - referencia) <= tolerancia)
    except (ArithmeticError, KeyError, IndexError, TypeError, ValueError):
        resultado, referencia, ok = None, None, False
    return {"nombre": nombre, "resultado": resultado, "referencia": referencia, "ok": ok}


def _saldo_final(filas):
    """Saldo reconstruido sin el tope en cero de la tabla: capital + intereses - pagos."""
    return filas[0]["saldo_inicial"] + sum(f["intereses"] - f["pago_total"] for f in filas[1:])


def _vp_cuotas(filas, i):
    """VP de los pagos de la tabla, descontados uno a uno."""
    return series.vp_flujo([f["pago_total"] for f in filas[1:]], i)


def _vf_mes_a_mes(cuotas, i):
    """Saldo final de un ahorro con aportes vencidos, capitalizando periodo a periodo."""
    saldo = 0.0
    for cuota in cuotas:
        saldo = saldo * (1 + i) + cuota
    return saldo


def _modulos():
    """Verificaciones de cada módulo con los datos de sus ejemplos de clase."""
    i_amort = tasas.periodica_desde_ea(0.1765, 12)
    monto_amort = 336_000_000

    def amortizar(**opciones):
        return amortizacion.tabla_amortizacion(monto_amort, i_amort, 180, tasa_ea=0.1765, **opciones)

    return [
        ("Interés simple: VF contra iterativo", lambda: (
            interes.vf_simple(10_000_000, 0.18, 4 / 12),
            interes.acumulado_simple(10_000_000, 0.18 / 12, 4)[1][-1],
        )),
        ("Interés compuesto: VF contra iterativo", lambda: (
            interes.vf_compuesto(4_000_000, 0.015, 30),
            interes.acumulado_compuesto(4_000_000, 0.015, 30)[1][-1],
        )),
        ("Tasas: VF con la EA contra tasa periódica", lambda: (
            1_000_000 * (1 + tasas.ea_desde_codigo(0.18, "NAMV")),
            1_000_000 * (1 + 0.18 / 12) ** 12,
        )),
        ("Series: VP contra npf.pv", lambda: (
            series.vp_serie(250_000, 0.01, 36),
            npf.pv(0.01, 36, -250_000),
        )),
        ("Gradientes: VP contra npf.npv", lambda: (
            gradientes.vp_aritmetico(500_000, 20_000, 0.012, 24),
            npf.npv(0.012, [0] + gradientes.cuotas_aritmetico(500_000, 20_000, 24)),
        )),
        ("Amortización cuota fija: saldo final en cero", lambda: (
            _saldo_final(amortizar(sistema="frances")), 0.0,
        )),
        ("Amortización abono constante: saldo final en cero", lambda: (
            _saldo_final(amortizar(sistema="aleman")), 0.0,
        )),
        ("Amortización con pagos extras: saldo final en cero", lambda: (
            _saldo_final(amortizar(
                sistema="frances", tipo_pago_extra="periodico", frecuencia_extra_meses=6, monto_extra_periodico=2_000_000,
            )), 0.0,
        )),
    ]


def _caso_vehiculo(p):
    """VP de las cuotas de cada oferta y sistema igual al préstamo."""
    calculos = []
    for oferta in p["ofertas"]:
        for sistema, nombre in (("frances", "cuota fija"), ("aleman", "abono constante")):
            def calculo(oferta=oferta, sistema=sistema):
                i = tasas.periodica_desde_ea(tasas.ea_desde_codigo(oferta["tasa_valor"], oferta["codigo_tasa"]), 12)
                filas = amortizacion.tabla_amortizacion(p["monto"], i, p["plazo_meses"], sistema=sistema)
                return _vp_cuotas(filas, i), p["monto"]

            calculos.append((f"Caso 1, {oferta['entidad']} con {nombre}: VP de las cuotas contra préstamo", calculo))
    return calculos


def _caso_inversion(p):
    """Rendimiento neto con la fórmula del panel contra capitalización día a día."""
    capital, dias = p["capital"], p["plazo_dias"]

    def calculo(ea, retencion):
        formula = capital * ((1 + ea) ** (dias / 360) - 1) * (1 - retencion)
        saldo = interes.acumulado_compuesto(capital, tasas.periodica_desde_ea(ea, 360), dias)[1][-1]
        return formula, (saldo - capital) * (1 - retencion)

    return [
        ("Caso 2, CDT: rendimiento neto contra día a día", lambda: calculo(p["tasa_cdt_ea"], p["retencion_cdt"])),
        ("Caso 2, Nu: rendimiento neto contra día a día", lambda: calculo(p["tasa_cuenta_ea"], p["retencion_cuenta"])),
    ]


def _caso_ahorro(p):
    """VF del gradiente con fórmula cerrada contra simulación mes a mes."""
    a1, n = p["a1"], p["plazo_meses"]
    i = tasas.periodica_desde_ea(p["tasa_ea"], 12)
    G, g = p["gradiente_aritmetico_G"], p["gradiente_geometrico_g"]
    return [
        ("Caso 3, gradiente aritmético: VF contra mes a mes", lambda: (
            gradientes.vf_gradiente(gradientes.vp_aritmetico(a1, G, i, n), i, n),
            _vf_mes_a_mes(gradientes.cuotas_aritmetico(a1, G, n), i),
        )),
        ("Caso 3, gradiente geométrico: VF contra mes a mes", lambda: (
            gradientes.vf_gradiente(gradientes.vp_geometrico(a1, g, i, n), i, n),
            _vf_mes_a_mes(gradientes.cuotas_geometrico(a1, g, n), i),
        )),
    ]


def verificaciones_tablero(casos):
    """Lista de resultados {nombre, resultado, referencia, ok}; casos es la lista de datos/casos.json."""
    calculos = (
        _modulos()
        + _caso_vehiculo(casos[0]["parametros"])
        + _caso_inversion(casos[1]["parametros"])
        + _caso_ahorro(casos[2]["parametros"])
    )
    return [comprobar(nombre, calculo) for nombre, calculo in calculos]
