"""Punto de entrada del gestor de tienda (menu interactivo en consola)."""

import almacen
import gestor
import reportes

ARCHIVO = "datos_ejemplo.json"


def pedir_numero(mensaje):
    """Pide un número al usuario hasta que escriba algo válido."""
    while True:
        respuesta = input(mensaje)
        try:
            return float(respuesta)
        except ValueError:
            print("Eso no es un numero, intenta de nuevo.")


TEXTO_MENU = """
1) Agregar producto
2) Registrar venta
3) Cotizar
4) Reporte de inventario
5) Resumen de ventas
6) Mas vendidos
7) Alertas de stock bajo
8) Guardar y salir"""
OPCION_SALIR = "8"


def menu_agregar_producto():
    """Opción 1: pide los datos de un producto y lo da de alta."""
    codigo = input("Codigo: ")
    nombre = input("Nombre: ")
    precio = pedir_numero("Precio: ")
    stock = int(pedir_numero("Stock inicial: "))
    if gestor.agregarProducto(codigo, nombre, precio, stock):
        print("Producto agregado.")
    else:
        print("Error:", gestor.ultimo_error)


def menu_registrar_venta():
    """Opción 2: registra una venta e imprime el ticket."""
    codigo = input("Codigo del producto: ")
    cantidad = int(pedir_numero("Cantidad: "))
    cliente = input("Codigo de cliente (enter si no tiene): ")
    venta = gestor.registrar_venta(codigo, cantidad, cliente)
    if venta is not None:
        print(venta["ticket"])
    else:
        print("Error:", gestor.ultimo_error)


def menu_cotizar():
    """Opción 3: muestra el total estimado de una compra."""
    codigo = input("Codigo del producto: ")
    cantidad = int(pedir_numero("Cantidad: "))
    total = gestor.cotizar(codigo, cantidad)
    if total is not None:
        print("Total estimado (con IVA): $" + str(total))
    else:
        print("Error:", gestor.ultimo_error)


def menu_mas_vendidos():
    """Opción 6: imprime los productos más vendidos."""
    for codigo, unidades in reportes.mas_vendidos():
        print(codigo, "->", unidades, "unidades")


def menu_alertas_stock():
    """Opción 7: imprime los productos con stock bajo."""
    productos_bajos = reportes.productos_stock_bajo()
    if len(productos_bajos) == 0:
        print("No hay productos con stock bajo.")
        return
    for producto in productos_bajos:
        print(
            "OJO:", producto["nombre"], "solo tiene",
            producto["stock"], "unidades",
        )


ACCIONES = {
    "1": menu_agregar_producto,
    "2": menu_registrar_venta,
    "3": menu_cotizar,
    "4": reportes.reporte_inventario,
    "5": reportes.resumen_ventas,
    "6": menu_mas_vendidos,
    "7": menu_alertas_stock,
}


def menu():
    """Ciclo principal: carga los datos, muestra el menú y ejecuta opciones."""
    print("Bienvenido al gestor de la tienda La Esquina")
    if almacen.existe_archivo(ARCHIVO):
        almacen.cargar_datos(ARCHIVO)
        print("Datos cargados de", ARCHIVO)
    while True:
        print(TEXTO_MENU)
        opcion = input("Opcion: ")
        if opcion == OPCION_SALIR:
            almacen.guardar_datos(ARCHIVO)
            print("Datos guardados. Hasta luego.")
            break
        accion = ACCIONES.get(opcion)
        if accion is None:
            print("Opcion no valida.")
        else:
            accion()


if __name__ == "__main__":
    menu()
