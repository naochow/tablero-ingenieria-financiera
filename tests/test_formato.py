"""Pruebas del formato colombiano de pesos y porcentajes."""

from componentes import formato


def test_pesos_sin_decimales():
    assert formato.pesos(1234567) == "$ 1.234.567"
    assert formato.pesos(6252320.88) == "$ 6.252.321"
    assert formato.pesos(0) == "$ 0"


def test_pesos_con_decimales():
    assert formato.pesos(6252320.88, decimales=2) == "$ 6.252.320,88"


def test_pesos_negativos_y_cero_negativo():
    assert formato.pesos(-1500000) == "-$ 1.500.000"
    assert formato.pesos(-0.3) == "$ 0"


def test_porcentaje():
    assert formato.porcentaje(0.195618) == "19,56%"
    assert formato.porcentaje(0.195618, decimales=4) == "19,5618%"
    assert formato.porcentaje(0.07, decimales=0) == "7%"


def test_tasa_con_codigo():
    assert formato.tasa_con_codigo(0.014, "mv") == "1,40% MV"


def test_numero():
    assert formato.numero(60) == "60"
    assert formato.numero(1234.5, decimales=1) == "1.234,5"
