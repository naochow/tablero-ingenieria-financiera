"""Pruebas de las decisiones calculadas de los casos 2 y 3."""

import pytest

from componentes import decisiones
from finanzas import tasas

I = tasas.periodica_desde_ea(0.0907, 12)


def _planes(meta, G=25_000, g=0.02, n=36):
    return decisiones.comparar_planes(500_000, G, g, I, n, meta)


def test_gana_cuenta_y_empate():
    assert decisiones.gana_cuenta(1_800_000, 1_795_200)
    assert not decisiones.gana_cuenta(1_739_100, 1_795_200)
    assert decisiones.gana_cuenta(1_795_200, 1_795_200)
    assert decisiones.gana_cuenta(1_795_199.9, 1_795_200)


def test_valores_de_los_planes():
    aritmetico, geometrico = _planes(36_000_000)
    assert aritmetico["vf"] == pytest.approx(37_614_849, abs=1)
    assert aritmetico["aportes"] == 33_750_000
    assert aritmetico["diferencia_meta"] == pytest.approx(1_614_849, abs=1)
    assert aritmetico["alcanza"] and not geometrico["alcanza"]


def test_solo_uno_alcanza_la_meta():
    plan, motivo = decisiones.plan_recomendado(_planes(36_000_000))
    assert (plan["clave"], motivo) == ("aritmetico", "unico")


def test_ambos_alcanzan_recomienda_menos_aportes():
    plan, motivo = decisiones.plan_recomendado(_planes(20_000_000))
    assert (plan["clave"], motivo) == ("geometrico", "menos_aportes")


def test_ninguno_alcanza_recomienda_el_mas_cercano():
    plan, motivo = decisiones.plan_recomendado(_planes(100_000_000))
    assert (plan["clave"], motivo) == ("aritmetico", "mas_cercano")


def test_el_geometrico_puede_ganar_con_otros_valores():
    plan, motivo = decisiones.plan_recomendado(_planes(36_000_000, G=1_000, g=0.04))
    assert (plan["clave"], motivo) == ("geometrico", "unico")
