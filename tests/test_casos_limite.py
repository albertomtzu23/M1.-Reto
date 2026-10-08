"""Pruebas de casos límite agregadas durante la refactorización.

No modifican las pruebas originales: documentan comportamientos que la suite
base no cubría y bugs corregidos.
"""

import json

import pytest

import almacen
import gestor
import reportes


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


def test_json_sin_contador_reinicia_los_folios(tmp_path):
    producto = {"codigo": "A1", "nombre": "Cafe", "precio": 10.0, "stock": 5}
    contenido = json.dumps({"inventario": {"A1": producto}, "ventas": []})
    ruta = _escribir(tmp_path / "datos.json", contenido)
    assert almacen.cargar_datos(ruta) is True
    assert gestor.registrar_venta("A1", 1)["folio"] == 1


# --- Fronteras de los descuentos por volumen --------------------------------


@pytest.mark.parametrize(
    "precio, descuento, total",
    [
        (499.99, 0, 579.99),  # justo debajo del umbral medio: sin descuento
        (500, 25.0, 551.0),  # umbral medio exacto: 5 %
        (999.99, 50.0, 1101.99),  # justo debajo del umbral alto: 5 %
        (1000, 100.0, 1044.0),  # umbral alto exacto: 10 %
    ],
)
def test_frontera_descuento_por_volumen(precio, descuento, total):
    gestor.agregarProducto("A1", "Producto", precio, 10)
    venta = gestor.registrar_venta("A1", 1)
    assert venta["descuento"] == descuento
    assert venta["total"] == total


def test_cotizar_respeta_las_mismas_fronteras():
    gestor.agregarProducto("A1", "Producto", 500, 10)
    assert gestor.cotizar("A1", 1) == 551.0


# --- Regla VIP -------------------------------------------------------------


@pytest.mark.parametrize(
    "precio, total",
    [
        (200, 232.0),  # compra de exactamente 200: NO aplica VIP
        (200.01, 227.37),  # apenas arriba de 200: sí aplica 2 %
    ],
)
def test_frontera_monto_minimo_vip(precio, total):
    gestor.agregarProducto("A1", "Producto", precio, 10)
    assert gestor.registrar_venta("A1", 1, "VIP")["total"] == total


@pytest.mark.parametrize("cliente", ["vip001", "XVIP01", "VI", "", None])
def test_clientes_que_no_son_vip(cliente):
    gestor.agregarProducto("A1", "Producto", 300.0, 10)
    assert gestor.registrar_venta("A1", 1, cliente)["descuento"] == 0


def test_cotizar_no_aplica_descuento_vip():
    gestor.agregarProducto("A1", "Producto", 100.0, 50)
    estimado = gestor.cotizar("A1", 6)
    venta_vip = gestor.registrar_venta("A1", 6, "VIP007")
    assert estimado == 661.2
    assert venta_vip["total"] == 647.28


# --- Stock y folios --------------------------------------------------------


def test_se_puede_vender_todo_el_stock_y_ni_una_mas():
    gestor.agregarProducto("A1", "Producto", 10.0, 3)
    assert gestor.registrar_venta("A1", 3) is not None
    assert gestor.INVENTARIO["A1"]["stock"] == 0
    assert gestor.registrar_venta("A1", 1) is None
    assert gestor.ultimo_error == "stock insuficiente"


def test_una_venta_fallida_no_consume_folio():
    gestor.agregarProducto("A1", "Producto", 10.0, 3)
    assert gestor.registrar_venta("A1", 99) is None
    assert gestor.registrar_venta("A1", 1)["folio"] == 1


def test_cotizar_no_valida_stock():
    gestor.agregarProducto("A1", "Producto", 10.0, 1)
    assert gestor.cotizar("A1", 5) == 58.0


# --- Mensajes de error (el orden de las validaciones importa) ---------------


@pytest.mark.parametrize(
    "codigo, cantidad, mensaje",
    [
        ("", 1, "codigo vacio"),
        (None, 1, "codigo vacio"),
        ("", 0, "codigo vacio"),  # el código se valida antes que la cantidad
        ("ZZ", 1, "producto no existe"),
        ("ZZ", 0, "producto no existe"),  # el producto antes que la cantidad
        ("A1", 0, "cantidad invalida"),
        ("A1", None, "cantidad invalida"),
        ("A1", 99, "stock insuficiente"),
    ],
)
def test_mensaje_de_error_de_registrar_venta(codigo, cantidad, mensaje):
    gestor.agregarProducto("A1", "Producto", 10.0, 5)
    assert gestor.registrar_venta(codigo, cantidad) is None
    assert gestor.ultimo_error == mensaje


@pytest.mark.parametrize(
    "codigo, precio, stock, mensaje",
    [
        ("", 10.0, 1, "codigo vacio"),
        ("A1", 10.0, 1, "el producto ya existe"),
        ("B1", 0, 1, "precio invalido"),
        ("B1", 10.0, -1, "stock invalido"),
    ],
)
def test_mensaje_de_error_de_agregar_producto(codigo, precio, stock, mensaje):
    gestor.agregarProducto("A1", "Producto", 10.0, 5)
    assert gestor.agregarProducto(codigo, "Otro", precio, stock) is False
    assert gestor.ultimo_error == mensaje


def test_alta_con_stock_cero_es_valida():
    assert gestor.agregarProducto("A1", "Producto", 10.0, 0) is True


def test_actualizar_stock_de_producto_inexistente():
    assert gestor.actualizar_stock("ZZ", 5) is False
    assert gestor.ultimo_error == "producto no existe"


# --- Ticket ----------------------------------------------------------------


def test_ticket_sin_descuento_no_muestra_la_linea_de_descuento():
    gestor.agregarProducto("A1", "Cafe", 10.0, 5)
    ticket = gestor.registrar_venta("A1", 2)["ticket"]
    assert ticket == (
        "TIENDA LA ESQUINA\n"
        "----------------------------\n"
        "Folio: 1\n"
        "Cafe x2\n"
        "Subtotal: $20.0\n"
        "IVA: $3.2\n"
        "TOTAL: $23.2\n"
    )


def test_ticket_con_descuento_muestra_la_linea_de_descuento():
    gestor.agregarProducto("A1", "Cafe", 100.0, 50)
    ticket = gestor.registrar_venta("A1", 6)["ticket"]
    assert "Descuento: -$30.0\n" in ticket


# --- Reportes --------------------------------------------------------------


def test_stock_igual_al_minimo_no_es_stock_bajo():
    # El mínimo es 5 (regla de negocio): con 5 no hay alerta, con 4 sí.
    gestor.agregarProducto("A1", "En el minimo", 10.0, 5)
    gestor.agregarProducto("A2", "Debajo", 10.0, 4)
    assert [p["codigo"] for p in reportes.productos_stock_bajo()] == ["A2"]


def test_mas_vendidos_conserva_el_orden_en_empates():
    for codigo in ("A1", "B1", "C1"):
        gestor.agregarProducto(codigo, "Producto", 1.0, 10)
    gestor.registrar_venta("B1", 2)
    gestor.registrar_venta("A1", 2)
    gestor.registrar_venta("C1", 5)
    assert reportes.mas_vendidos() == [("C1", 5), ("B1", 2), ("A1", 2)]


def test_mas_vendidos_con_n_mayor_que_los_productos_y_sin_ventas():
    assert reportes.mas_vendidos() == []
    gestor.agregarProducto("A1", "Producto", 1.0, 10)
    gestor.registrar_venta("A1", 1)
    assert reportes.mas_vendidos(10) == [("A1", 1)]


def test_resumen_de_ventas():
    gestor.agregarProducto("A1", "Cafe", 10.0, 10)
    gestor.registrar_venta("A1", 2)
    gestor.registrar_venta("A1", 1)
    assert reportes.resumen_ventas() == (
        "===== RESUMEN DE VENTAS =====\n"
        "Folio 1: Cafe x2 = $23.2\n"
        "Folio 2: Cafe x1 = $11.6\n"
        "Numero de ventas: 2\n"
        "Total del dia: $34.8\n"
    )


# --- Persistencia con caracteres especiales --------------------------------


def test_guardar_y_cargar_conserva_acentos_y_enie(tmp_path):
    ruta = str(tmp_path / "datos.json")
    gestor.agregarProducto("Ñ1", "Café de Ñuñoa", 10.0, 5)
    almacen.guardar_datos(ruta)
    with open(ruta, encoding="utf-8") as archivo:
        assert "Café de Ñuñoa" in archivo.read()  # sin escapes \\u
    gestor.reiniciar_sistema()
    assert almacen.cargar_datos(ruta) is True
    assert gestor.INVENTARIO["Ñ1"]["nombre"] == "Café de Ñuñoa"
