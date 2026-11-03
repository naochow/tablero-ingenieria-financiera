"""Pruebas de la lectura y validación de datos/casos.json."""

import json

from componentes import datos_casos


def _escribir(tmp_path, datos):
    ruta = tmp_path / "casos.json"
    ruta.write_text(json.dumps(datos), encoding="utf-8")
    return ruta


def _datos():
    return json.loads(datos_casos.RUTA_CASOS.read_text(encoding="utf-8"))


def test_el_archivo_del_repo_es_valido():
    casos, error = datos_casos.cargar_casos()
    assert error is None
    assert [c["id"] for c in casos] == ["vehiculo_sufi_davivienda", "inversion_bancolombia_nu", "ahorro_cuota_inicial_gradientes"]


def test_cada_fuente_tiene_nombre_url_y_fecha():
    casos, _ = datos_casos.cargar_casos()
    for caso in casos:
        assert caso["fuentes"]
        for fuente in caso["fuentes"]:
            assert fuente["nombre"] and fuente["url"].startswith("https://") and fuente["fecha"]


def test_archivo_ausente(tmp_path):
    casos, error = datos_casos.cargar_casos(tmp_path / "no_existe.json")
    assert casos is None and error


def test_json_roto(tmp_path):
    ruta = tmp_path / "casos.json"
    ruta.write_text("{ esto no es json", encoding="utf-8")
    casos, error = datos_casos.cargar_casos(ruta)
    assert casos is None and error


def test_falta_un_parametro(tmp_path):
    datos = _datos()
    del datos["casos"][2]["parametros"]["meta_ahorro"]
    casos, error = datos_casos.cargar_casos(_escribir(tmp_path, datos))
    assert casos is None and "meta_ahorro" in error


def test_falta_la_fecha_de_una_fuente(tmp_path):
    datos = _datos()
    del datos["casos"][0]["fuentes"][0]["fecha"]
    casos, error = datos_casos.cargar_casos(_escribir(tmp_path, datos))
    assert casos is None and "fecha de una fuente" in error


def test_numero_de_casos_y_ofertas(tmp_path):
    datos = _datos()
    datos["casos"].pop()
    assert datos_casos.cargar_casos(_escribir(tmp_path, datos))[0] is None
    datos = _datos()
    datos["casos"][0]["parametros"]["ofertas"].pop()
    assert datos_casos.cargar_casos(_escribir(tmp_path, datos))[0] is None
