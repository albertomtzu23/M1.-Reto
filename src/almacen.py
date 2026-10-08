"""Persistencia del gestor: carga y guardado de datos en JSON."""

import json
import os

import gestor


def guardar_datos(ruta):
    """Guarda el inventario, las ventas y el folio actual en un JSON."""
    datos = {}
    datos["inventario"] = gestor.INVENTARIO
    datos["ventas"] = gestor.VENTAS
    datos["contador"] = gestor.contador_ventas
    with open(ruta, "w", encoding="utf-8") as archivo:
        json.dump(datos, archivo, indent=2, ensure_ascii=False)
    return True


def _estructura_valida(datos):
    """Indica si el JSON leído tiene la forma que guarda `guardar_datos`."""
    return (
        isinstance(datos, dict)
        and isinstance(datos.get("inventario"), dict)
        and isinstance(datos.get("ventas"), list)
    )


def cargar_datos(ruta):
    """Lee el archivo JSON y deja los datos en el estado global.

    Regresa False si el archivo no existe, está corrupto o no tiene la
    estructura esperada; en esos casos el estado actual no se modifica.
    """
    if not os.path.exists(ruta):
        gestor.ultimo_error = "el archivo no existe"
        return False
    try:
        with open(ruta, encoding="utf-8") as archivo:
            datos = json.load(archivo)
    except (ValueError, RecursionError):
        # ValueError cubre JSONDecodeError (JSON mal formado), UnicodeDecodeError
        # (bytes que no son UTF-8) y enteros con demasiados dígitos;
        # RecursionError, un anidamiento excesivo.
        gestor.ultimo_error = "archivo corrupto"
        return False
    if not _estructura_valida(datos):
        gestor.ultimo_error = "formato de datos invalido"
        return False
    gestor.INVENTARIO.clear()
    for codigo in datos["inventario"]:
        gestor.INVENTARIO[codigo] = datos["inventario"][codigo]
    gestor.VENTAS.clear()
    for venta in datos["ventas"]:
        gestor.VENTAS.append(venta)
    gestor.contador_ventas = datos.get("contador", 0)
    return True


def existe_archivo(ruta):
    """Indica si ya existe el archivo de datos."""
    return os.path.exists(ruta)
