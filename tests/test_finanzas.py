"""Pruebas del motor de cálculo con los valores de referencia del CONTEXTO (sección 9)."""

import numpy_financial as npf
import pytest

from finanzas import gradientes, interes, series, tasas

TOL_TASA = 1e-6


# --- tasas.py ---

def test_mensual_vencida_a_ea():
    assert tasas.ea_desde_codigo(0.015, "MV") == pytest.approx(0.195618, abs=TOL_TASA)


def test_trimestral_anticipada_a_vencida_y_ea():
    assert tasas.anticipada_a_vencida(0.035) == pytest.approx(0.036269, abs=TOL_TASA)
    assert tasas.ea_desde_codigo(0.035, "TA") == pytest.approx(0.153163, abs=TOL_TASA)


def test_ipc_mas_puntos():
    assert tasas.tasa_combinada(0.072, 0.06) == pytest.approx(0.13632, abs=TOL_TASA)


def test_nominal_es_periodica_por_m():
    # 21% NAMV equivale a 1,75% MV
    assert tasas.ea_desde_codigo(0.21, "NAMV") == pytest.approx(
        tasas.ea_desde_codigo(0.0175, "MV"), abs=1e-12
    )


@pytest.mark.parametrize("codigo", list(tasas.CODIGOS))
def test_ida_y_vuelta_por_ea(codigo):
    tipo, periodicidad, modalidad = tasas.CODIGOS[codigo]
    ea = tasas.ea_desde_codigo(0.02, codigo)
    regreso = tasas.desde_efectiva_anual(ea, tipo, periodicidad, modalidad)
    assert regreso == pytest.approx(0.02, abs=1e-12)


def test_tabla_equivalencias_mismo_valor_futuro():
    ea = 0.175
    tabla = tasas.tabla_equivalencias(ea)
    for fila in tabla.itertuples():
        vf_vencida = 1_000_000 * (1 + fila.periodica_vencida) ** fila.periodos_por_ano
        iv_desde_anticipada = tasas.anticipada_a_vencida(fila.periodica_anticipada)
        vf_anticipada = 1_000_000 * (1 + iv_desde_anticipada) ** fila.periodos_por_ano
        assert vf_vencida == pytest.approx(1_175_000, abs=1e-6)
        assert vf_anticipada == pytest.approx(1_175_000, abs=1e-6)


def test_tasa_periodica_del_flujo():
    # 17,5% EA llevada a mensual no es 17,5%/12
    i = tasas.tasa_periodica(0.175, "efectiva", "anual", "vencida", "mensual")
    assert i == pytest.approx(1.175 ** (1 / 12) - 1, abs=1e-12)
    assert i < 0.175 / 12


def test_retencion_y_tasa_real():
    assert tasas.tea_neta(0.102) == pytest.approx(0.09486, abs=TOL_TASA)
    assert tasas.tasa_real(0.13632, 0.072) == pytest.approx(0.06, abs=TOL_TASA)


def test_entradas_invalidas():
    with pytest.raises(ValueError):
        tasas.ea_desde_codigo(0.01, "XX")
    with pytest.raises(ValueError):
        tasas.a_efectiva_anual(0.01, "periodica", "quincenal")
    with pytest.raises(ValueError):
        tasas.anticipada_a_vencida(1.0)


# --- interes.py ---

TOL_PESOS = 1


def test_simple_cuatro_meses():
    n = interes.plazo_en_anos(4, "meses")
    assert interes.interes_simple(10_000_000, 0.18, n) == pytest.approx(600_000, abs=TOL_PESOS)


def test_simple_tasa_mensual_y_dias():
    # 1,5% mensual simple = 18% anual; 120 días con año de 360 = 4 meses
    i = interes.tasa_simple_anual(0.015, "mensual")
    n = interes.plazo_en_anos(120, "dias", 360)
    assert interes.interes_simple(10_000_000, i, n) == pytest.approx(600_000, abs=TOL_PESOS)
    n_365 = interes.plazo_en_anos(120, "dias", 365)
    assert interes.interes_simple(10_000_000, i, n_365) < 600_000


def test_simple_despejes():
    vf = interes.vf_simple(10_000_000, 0.18, 1 / 3)
    assert interes.vp_simple(vf, 0.18, 1 / 3) == pytest.approx(10_000_000, abs=TOL_PESOS)
    assert interes.tasa_simple(10_000_000, vf, 1 / 3) == pytest.approx(0.18, abs=TOL_TASA)
    assert interes.plazo_simple(10_000_000, vf, 0.18) == pytest.approx(1 / 3, abs=TOL_TASA)


def test_simple_iterativo_igual_a_formula():
    _, saldos = interes.acumulado_simple(10_000_000, 0.015, 4.5)
    assert saldos[-1] == pytest.approx(interes.vf_simple(10_000_000, 0.015, 4.5), abs=TOL_PESOS)


def test_compuesto_treinta_meses():
    vf = interes.vf_compuesto(4_000_000, 0.015, 30)
    assert vf == pytest.approx(6_252_320.88, abs=TOL_PESOS)
    assert vf == pytest.approx(npf.fv(0.015, 30, 0, -4_000_000), abs=TOL_PESOS)


def test_compuesto_despejes():
    vf = 6_252_320.88
    assert interes.vp_compuesto(vf, 0.015, 30) == pytest.approx(4_000_000, abs=TOL_PESOS)
    assert interes.tasa_compuesta(4_000_000, vf, 30) == pytest.approx(0.015, abs=TOL_TASA)
    assert interes.periodos_compuesto(4_000_000, vf, 0.015) == pytest.approx(30, abs=1e-4)


def test_compuesto_iterativo_y_duplicar():
    _, saldos = interes.acumulado_compuesto(4_000_000, 0.015, 30)
    assert saldos[-1] == pytest.approx(6_252_320.88, abs=TOL_PESOS)
    n = interes.tiempo_duplicar(0.015)
    assert interes.vf_compuesto(1, 0.015, n) == pytest.approx(2, abs=1e-9)


def test_tabla_frecuencias():
    filas = interes.tabla_frecuencias(1_000_000, 0.18, 1)
    anual, mensual = filas[0], filas[3]
    assert anual["valor_futuro"] == pytest.approx(1_180_000, abs=TOL_PESOS)
    assert mensual["ea"] == pytest.approx(1.015 ** 12 - 1, abs=TOL_TASA)
    vfs = [f["valor_futuro"] for f in filas]
    assert vfs == sorted(vfs)  # más frecuencia, más valor futuro


def test_interes_entradas_invalidas():
    with pytest.raises(ValueError):
        interes.plazo_en_anos(3, "semanas")
    with pytest.raises(ValueError):
        interes.plazo_simple(100, 120, 0)
    with pytest.raises(ValueError):
        interes.tiempo_duplicar(0)


# --- series.py ---

def test_serie_vencida_vp():
    vp = series.vp_serie(250_000, 0.01, 36)
    assert vp == pytest.approx(7_526_876.26, abs=TOL_PESOS)
    assert vp == pytest.approx(npf.pv(0.01, 36, -250_000), abs=TOL_PESOS)


def test_serie_anticipada_vp():
    vp = series.vp_serie(150_000, 0.015, 11, anticipada=True)
    assert vp == pytest.approx(1_533_327.68, abs=TOL_PESOS)
    assert vp == pytest.approx(npf.pv(0.015, 11, -150_000, when="begin"), abs=TOL_PESOS)
    # Sin when='begin' (error de los Excel) el resultado es distinto
    assert abs(vp - npf.pv(0.015, 11, -150_000)) > 10_000


@pytest.mark.parametrize("anticipada", [False, True])
def test_serie_resolver_desde_cada_conocido(anticipada):
    base = series.resolver_serie("cuota", 250_000, 0.01, 36, anticipada)
    desde_vp = series.resolver_serie("vp", base["vp"], 0.01, 36, anticipada)
    desde_vf = series.resolver_serie("vf", base["vf"], 0.01, 36, anticipada)
    for resultado in (desde_vp, desde_vf):
        for clave in series.CONOCIDOS:
            assert resultado[clave] == pytest.approx(base[clave], abs=TOL_PESOS)
    when = "begin" if anticipada else "end"
    assert base["cuota"] == pytest.approx(npf.pmt(0.01, 36, -base["vp"], when=when), abs=TOL_PESOS)


@pytest.mark.parametrize("anticipada", [False, True])
def test_serie_cuota_a_cuota_y_acumulado(anticipada):
    vp = series.vp_serie(250_000, 0.01, 36, anticipada)
    assert series.vp_flujo([250_000] * 36, 0.01, anticipada) == pytest.approx(vp, abs=TOL_PESOS)
    _, aportes, saldos = series.acumulado_serie(250_000, 0.01, 36, anticipada)
    assert saldos[-1] == pytest.approx(series.vf_serie(250_000, 0.01, 36, anticipada), abs=TOL_PESOS)
    assert aportes[-1] == 250_000 * 36


def test_serie_tasa_cero():
    assert series.vp_serie(100, 0, 12) == 1_200
    assert series.cuota_desde_vf(1_200, 0, 12) == 100


# --- gradientes.py ---

def test_gradiente_aritmetico():
    vp = gradientes.vp_aritmetico(500_000, 20_000, 0.012, 24)
    assert vp == pytest.approx(14_907_744.40, abs=TOL_PESOS)
    assert gradientes.cuota_equivalente(vp, 0.012, 24) == pytest.approx(718_584.06, abs=TOL_PESOS)
    cuotas = gradientes.cuotas_aritmetico(500_000, 20_000, 24)
    assert npf.npv(0.012, [0] + cuotas) == pytest.approx(vp, abs=TOL_PESOS)
    assert gradientes.primera_cuota_aritmetico(vp, 20_000, 0.012, 24) == pytest.approx(500_000, abs=TOL_PESOS)


def test_gradiente_geometrico_primera_cuota():
    i = tasas.tasa_periodica(0.215, "efectiva", "anual", "vencida", "trimestral")
    a1 = gradientes.primera_cuota_geometrico(5_000_000, 0.10, i, 8)
    assert a1 == pytest.approx(554_215.47, abs=TOL_PESOS)
    cuotas = gradientes.cuotas_geometrico(a1, 0.10, 8)
    assert npf.npv(i, [0] + cuotas) == pytest.approx(5_000_000, abs=TOL_PESOS)


def test_gradiente_geometrico_g_igual_a_i():
    vp = gradientes.vp_geometrico(100_000, 0.01, 0.01, 12)
    assert vp == pytest.approx(100_000 * 12 / 1.01, abs=1e-6)
    cuotas = gradientes.cuotas_geometrico(100_000, 0.01, 12)
    assert npf.npv(0.01, [0] + cuotas) == pytest.approx(vp, abs=TOL_PESOS)


def test_gradientes_decrecientes():
    cuotas = gradientes.cuotas_aritmetico(1_000_000, -30_000, 24)
    vp = gradientes.vp_aritmetico(1_000_000, -30_000, 0.01, 24)
    assert npf.npv(0.01, [0] + cuotas) == pytest.approx(vp, abs=TOL_PESOS)
    cuotas_g = gradientes.cuotas_geometrico(1_000_000, -0.05, 12)
    vp_g = gradientes.vp_geometrico(1_000_000, -0.05, 0.01, 12)
    assert npf.npv(0.01, [0] + cuotas_g) == pytest.approx(vp_g, abs=TOL_PESOS)


def test_gradiente_vf_y_cruce():
    vp = gradientes.vp_aritmetico(500_000, 20_000, 0.012, 24)
    assert gradientes.vf_gradiente(vp, 0.012, 24) == pytest.approx(vp * 1.012 ** 24, abs=1e-6)
    cuotas = gradientes.cuotas_aritmetico(500_000, 20_000, 24)
    a_eq = gradientes.cuota_equivalente(vp, 0.012, 24)
    t = gradientes.periodo_cruce(cuotas, a_eq)
    assert cuotas[t - 1] > a_eq >= cuotas[t - 2]
    assert gradientes.periodo_cruce([5, 5, 5], 10) is None


def test_gradiente_aritmetico_no_confunde_g_con_cuota():
    # Error de los Excel: poner la cuota fija donde va G
    correcto = gradientes.vp_aritmetico(500_000, 20_000, 0.012, 24)
    errado = gradientes.vp_aritmetico(500_000, 500_000, 0.012, 24)
    assert abs(correcto - errado) > 1_000_000
