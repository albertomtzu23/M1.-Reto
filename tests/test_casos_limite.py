"""Pruebas de casos límite agregadas durante la refactorización.

No modifican las pruebas originales: documentan comportamientos que la suite
base no cubría y bugs corregidos.
"""

import json

import almacen
import gestor


def _escribir(ruta, contenido):
    ruta.write_text(contenido, encoding="utf-8")
    return str(ruta)


def _inventario_previo():
    gestor.agregarProducto("P1", "Producto previo", 10.0, 5)
    gestor.registrar_venta("P1", 1)


# --- Bug corregido: JSON válido con estructura incorrecta -------------------


def test_json_sin_inventario_no_borra_el_estado(tmp_path):
    _inventario_previo()
    ruta = _escribir(tmp_path / "datos.json", '{"ventas": []}')
    assert almacen.cargar_datos(ruta) is False
    assert gestor.ultimo_error == "formato de datos invalido"
    assert "P1" in gestor.INVENTARIO
    assert len(gestor.VENTAS) == 1


def test_json_sin_ventas_no_carga_a_medias(tmp_path):
    _inventario_previo()
    contenido = json.dumps({"inventario": {"X": {"codigo": "X"}}})
    ruta = _escribir(tmp_path / "datos.json", contenido)
    assert almacen.cargar_datos(ruta) is False
    assert list(gestor.INVENTARIO) == ["P1"]
    assert len(gestor.VENTAS) == 1


def test_json_que_es_una_lista_se_rechaza(tmp_path):
    _inventario_previo()
    ruta = _escribir(tmp_path / "datos.json", "[]")
    assert almacen.cargar_datos(ruta) is False
    assert "P1" in gestor.INVENTARIO


def test_json_corrupto_sigue_reportandose_como_corrupto(tmp_path):
    _inventario_previo()
    ruta = _escribir(tmp_path / "datos.json", "{corrupto")
    assert almacen.cargar_datos(ruta) is False
    assert gestor.ultimo_error == "archivo corrupto"
    assert "P1" in gestor.INVENTARIO


def test_json_sin_contador_carga_con_folio_cero(tmp_path):
    ruta = _escribir(tmp_path / "datos.json", '{"inventario": {}, "ventas": []}')
    assert almacen.cargar_datos(ruta) is True
    assert gestor.contador_ventas == 0
