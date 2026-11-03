"""Pruebas de las verificaciones del panel principal: pasan con datos buenos y detectan los fallos."""

import json
from pathlib import Path

from componentes import verificaciones_tablero as vt
from finanzas import interes

RUTA_CASOS = Path(__file__).resolve().parent.parent / "datos" / "casos.json"


def _casos():
    return json.loads(RUTA_CASOS.read_text(encoding="utf-8"))["casos"]


def test_todas_pasan_con_los_datos_del_tablero():
    resultados = vt.verificaciones_tablero(_casos())
    assert len(resultados) >= 8 + 3
    assert [r["nombre"] for r in resultados if not r["ok"]] == []


def test_comprobar_usa_tolerancia_de_un_peso():
    assert vt.comprobar("igual", lambda: (100.0, 100.5))["ok"]
    assert vt.comprobar("en el borde", lambda: (100.0, 101.0))["ok"]
    assert not vt.comprobar("se pasa", lambda: (100.0, 101.5))["ok"]


def test_comprobar_trata_errores_y_nan_como_fallo():
    assert not vt.comprobar("clave", lambda: {}["falta"])["ok"]
    assert not vt.comprobar("nan", lambda: (float("nan"), 0.0))["ok"]


def test_una_formula_danada_se_detecta(monkeypatch):
    original = interes.vf_compuesto
    monkeypatch.setattr(interes, "vf_compuesto", lambda c, t, n: original(c, t, n) + 2)
    fallas = [r["nombre"] for r in vt.verificaciones_tablero(_casos()) if not r["ok"]]
    assert fallas == ["Interés compuesto: VF contra iterativo"]


def test_una_tasa_que_rompe_un_caso_solo_afecta_ese_caso():
    casos = _casos()
    del casos[1]["parametros"]["tasa_cdt_ea"]
    fallas = [r["nombre"] for r in vt.verificaciones_tablero(casos) if not r["ok"]]
    assert fallas == ["Caso 2, CDT: rendimiento neto contra día a día"]
