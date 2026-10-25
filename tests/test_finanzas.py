"""Pruebas del motor de cálculo con los valores de referencia del CONTEXTO (sección 9)."""

import pytest

from finanzas import tasas

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
