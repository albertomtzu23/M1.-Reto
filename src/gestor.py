"""Modulo principal del gestor de inventario y ventas de "La Esquina".

Aqui vive casi toda la logica del negocio. Historicamente este archivo
lo fueron parchando varias personas, asi que hay de todo un poco.
"""

from datetime import datetime
from typing import Any

# ---------------------------------------------------------------
# Reglas de negocio
# ---------------------------------------------------------------
TASA_IVA = 0.16
UMBRAL_DESCUENTO_ALTO = 1000
TASA_DESCUENTO_ALTO = 0.10
UMBRAL_DESCUENTO_MEDIO = 500
TASA_DESCUENTO_MEDIO = 0.05
PREFIJO_VIP = "VIP"
MONTO_MINIMO_VIP = 200
TASA_DESCUENTO_VIP = 0.02
STOCK_MINIMO = 5

# ---------------------------------------------------------------
# Estado global de la aplicacion (inventario, ventas y contadores)
# ---------------------------------------------------------------
# Un producto y una venta son diccionarios con claves fijas (ver CLAUDE.md);
# se guardan tal cual en el JSON.
Producto = dict[str, Any]
Venta = dict[str, Any]

INVENTARIO: dict[str, Producto] = {}
VENTAS: list[Venta] = []
contador_ventas: int = 0
ultimo_error: str = ""


def reiniciar_sistema() -> None:
    """Borra todo el estado del sistema (inventario, ventas y folios)."""
    global contador_ventas, ultimo_error
    INVENTARIO.clear()
    VENTAS.clear()
    contador_ventas = 0
    ultimo_error = ""


def agregarProducto(codigo: str, nombre: str, precio: float, stock: int) -> bool:
    """Valida los datos y da de alta un producto en el inventario."""
    global ultimo_error
    if codigo is None or codigo == "":
        ultimo_error = "codigo vacio"
        return False
    if codigo in INVENTARIO:
        ultimo_error = "el producto ya existe"
        return False
    if precio <= 0:
        ultimo_error = "precio invalido"
        return False
    if stock < 0:
        ultimo_error = "stock invalido"
        return False
    producto: Producto = {}
    producto["codigo"] = codigo
    producto["nombre"] = nombre
    producto["precio"] = precio
    producto["stock"] = stock
    INVENTARIO[codigo] = producto
    return True


def eliminar_producto(codigo: str) -> bool:
    """Quita un producto del inventario. Regresa False si no existe."""
    global ultimo_error
    if codigo in INVENTARIO:
        del INVENTARIO[codigo]
        return True
    ultimo_error = "producto no existe"
    return False


def actualizar_stock(codigo: str, cantidad: int) -> bool:
    """Suma unidades al stock (o resta si la cantidad es negativa)."""
    global ultimo_error
    if codigo not in INVENTARIO:
        ultimo_error = "producto no existe"
        return False
    nuevo_stock = INVENTARIO[codigo]["stock"] + cantidad
    if nuevo_stock < 0:
        ultimo_error = "el stock no puede quedar negativo"
        return False
    INVENTARIO[codigo]["stock"] = nuevo_stock
    return True


def buscarProducto(texto: str) -> list[Producto]:
    """Busca productos cuyo nombre contenga el texto (sin importar mayúsculas)."""
    resultados: list[Producto] = []
    for codigo in INVENTARIO:
        if texto.lower() in INVENTARIO[codigo]["nombre"].lower():
            resultados.append(INVENTARIO[codigo])
    return resultados


def calcular_descuento_volumen(subtotal: float) -> float:
    """Regresa el descuento por volumen que corresponde al subtotal."""
    if subtotal >= UMBRAL_DESCUENTO_ALTO:
        return subtotal * TASA_DESCUENTO_ALTO
    if subtotal >= UMBRAL_DESCUENTO_MEDIO:
        return subtotal * TASA_DESCUENTO_MEDIO
    return 0


def calcular_descuento_vip(
    cliente: str | None, subtotal: float, descuento: float
) -> float:
    """Regresa el descuento extra para clientes VIP, o 0 si no aplica.

    Aplica cuando el código del cliente empieza con PREFIJO_VIP y la compra,
    ya con el descuento por volumen, supera MONTO_MINIMO_VIP.
    """
    if not cliente or not cliente.startswith(PREFIJO_VIP):
        return 0
    if subtotal - descuento <= MONTO_MINIMO_VIP:
        return 0
    return subtotal * TASA_DESCUENTO_VIP


def _validar_venta(codigo: str | None, cantidad: int | None) -> Producto | None:
    """Valida la venta; regresa el producto o None (y deja ultimo_error)."""
    global ultimo_error
    if codigo is None or codigo == "":
        ultimo_error = "codigo vacio"
        return None
    if codigo not in INVENTARIO:
        ultimo_error = "producto no existe"
        return None
    if cantidad is None or cantidad <= 0:
        ultimo_error = "cantidad invalida"
        return None
    if INVENTARIO[codigo]["stock"] < cantidad:
        ultimo_error = "stock insuficiente"
        return None
    return INVENTARIO[codigo]


def _armar_ticket(venta: Venta) -> str:
    """Arma el ticket en texto plano de una venta."""
    ticket: str = ""
    ticket = ticket + "TIENDA LA ESQUINA\n"
    ticket = ticket + "----------------------------\n"
    ticket = ticket + "Folio: " + str(venta["folio"]) + "\n"
    ticket = ticket + venta["nombre"] + " x" + str(venta["cantidad"]) + "\n"
    ticket = ticket + "Subtotal: $" + str(venta["subtotal"]) + "\n"
    if venta["descuento"] > 0:
        ticket = ticket + "Descuento: -$" + str(venta["descuento"]) + "\n"
    ticket = ticket + "IVA: $" + str(venta["impuesto"]) + "\n"
    ticket = ticket + "TOTAL: $" + str(venta["total"]) + "\n"
    return ticket


def registrar_venta(
    codigo: str | None, cantidad: int | None, cliente: str | None = ""
) -> Venta | None:
    """Registra una venta: valida, calcula, descuenta stock y guarda."""
    global contador_ventas
    producto = _validar_venta(codigo, cantidad)
    if producto is None:
        return None
    subtotal = producto["precio"] * cantidad
    descuento = calcular_descuento_volumen(subtotal)
    descuento = descuento + calcular_descuento_vip(cliente, subtotal, descuento)
    base = subtotal - descuento
    impuesto = base * TASA_IVA
    total = round(base + impuesto, 2)
    producto["stock"] = producto["stock"] - cantidad
    contador_ventas = contador_ventas + 1
    venta: Venta = {}
    venta["folio"] = contador_ventas
    venta["codigo"] = codigo
    venta["nombre"] = producto["nombre"]
    venta["cantidad"] = cantidad
    venta["subtotal"] = round(subtotal, 2)
    venta["descuento"] = round(descuento, 2)
    venta["impuesto"] = round(impuesto, 2)
    venta["total"] = total
    venta["cliente"] = cliente
    venta["fecha"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    venta["ticket"] = _armar_ticket(venta)
    VENTAS.append(venta)
    return venta


def cotizar(codigo: str, cantidad: int | None) -> float | None:
    """Calcula cuanto costaria una compra sin registrar la venta."""
    global ultimo_error
    if codigo not in INVENTARIO:
        ultimo_error = "producto no existe"
        return None
    if cantidad is None or cantidad <= 0:
        ultimo_error = "cantidad invalida"
        return None
    subtotal: float = INVENTARIO[codigo]["precio"] * cantidad
    descuento = calcular_descuento_volumen(subtotal)
    base = subtotal - descuento
    total = base + base * TASA_IVA
    return round(total, 2)

