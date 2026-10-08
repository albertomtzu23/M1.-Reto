# CLAUDE.md — Gestor de inventario "La Esquina"

Instrucciones para Claude Code en este repositorio. Léelas antes de proponer o
aplicar cualquier cambio.

## Qué es el proyecto

Aplicación de consola en Python (3.10+) para administrar el inventario y las
ventas de una tienda pequeña: alta de productos, ventas con descuentos e IVA,
cotizaciones, alertas de stock bajo, reportes y persistencia en JSON.

El objetivo de este repositorio es **refactorizar** el código de `src/` para
mejorar su calidad **sin cambiar su comportamiento observable**.

| Archivo           | Responsabilidad                                   |
|-------------------|---------------------------------------------------|
| `src/gestor.py`   | Lógica de negocio: productos, ventas, cotización  |
| `src/almacen.py`  | Carga y guardado del estado en JSON               |
| `src/reportes.py` | Reportes e indicadores                            |
| `src/main.py`     | Menú interactivo de consola (entrada/salida)      |
| `tests/`          | Suite de caja negra con pytest                    |

## Comandos

```bash
pip install -r requirements.txt   # pytest y ruff
pytest                            # TODAS las pruebas deben pasar
ruff check src                    # meta final: 0 errores
cd src && python main.py          # app interactiva (usa datos_ejemplo.json)
```

Después de **cada** refactorización ejecuta `pytest` **y** `ruff check src`, y
reporta el resultado. No encadenes dos refactorizaciones sin validar en medio.

## Reglas que NO se negocian

1. **No modificar** las pruebas originales de `tests/` ni `pyproject.toml`.
   Si un test falla, el error está en `src/`, nunca en el test.
   Las pruebas nuevas van en `tests/test_casos_limite.py` (archivo agregado
   durante el reto); cada bug corregido lleva una prueba que falle con el
   código anterior.
2. **API pública congelada** (la usan los tests o `main.py`):
   - `gestor.INVENTARIO`, `gestor.VENTAS`, `gestor.ultimo_error`
   - `gestor.agregarProducto`, `gestor.buscarProducto` (conservan su nombre
     camelCase; están en `ignore-names` de ruff)
   - `gestor.reiniciar_sistema`, `eliminar_producto`, `actualizar_stock`,
     `registrar_venta`, `cotizar`
   - `almacen.guardar_datos`, `almacen.cargar_datos`
   - `reportes.productos_stock_bajo`, `reporte_inventario`, `total_vendido`,
     `mas_vendidos`, `resumen_ventas`
   Las firmas y los valores de retorno (`True`/`False`/`None`/dict) no cambian.
3. **Salida idéntica**: el texto del ticket y de los reportes debe ser igual
   carácter por carácter. Ojo: los montos se imprimen con `str(float)`
   (`$20.0`, no `$20.00`). No "mejores" el formato.
4. **Un cambio a la vez**: cada refactorización es un commit atómico con
   mensaje `refactor: <qué>`.
5. Si una mejora implicaría cambiar el comportamiento (p. ej. una regla de
   negocio que parece un bug), **no la apliques**: repórtala y pregunta.

## Reglas de negocio que hay que preservar

- Descuento por volumen sobre el subtotal: ≥ $1000 → 10 %; ≥ $500 → 5 %.
- Cliente VIP (código que empieza con `"VIP"`): +2 % del subtotal **solo** si
  `subtotal - descuento > 200`. Se aplica en `registrar_venta`, **no** en
  `cotizar` (diferencia intencional del código original).
- IVA 16 % sobre `subtotal - descuento`. Total redondeado a 2 decimales.
- Stock bajo: `stock < 5`.
- `cotizar` no valida stock; `registrar_venta` sí.
- El folio (`contador`) continúa después de guardar y recargar.
- `cargar_datos` **no modifica el estado** si el archivo no existe, está
  corrupto (`"archivo corrupto"`) o no tiene la estructura
  `{"inventario": dict, "ventas": list}` (`"formato de datos invalido"`).
  *(Regla agregada durante el reto al corregir un bug: antes vaciaba el
  inventario y luego tronaba.)*
- El orden de las validaciones define qué mensaje queda en `ultimo_error`.
  En `registrar_venta`: código vacío → producto no existe → cantidad inválida →
  stock insuficiente. En `cotizar`: producto no existe → cantidad inválida
  (un código vacío reporta "producto no existe").

## Convenciones de código

- PEP 8, longitud de línea 88 (configurado en `pyproject.toml`).
- Nombres en **español** y en `snake_case`; constantes en `MAYUSCULAS`.
- Nada de nombres genéricos (`x`, `aux`, `temp2`, `t`, `d`, `hacer_cosa`).
- Sin números mágicos: usar constantes con nombre al inicio del módulo.
- Funciones cortas, una responsabilidad, complejidad ciclomática ≤ 10.
- Preferir cláusulas de guarda (`return` temprano) sobre `if` anidados.
- Type hints en todas las funciones (sintaxis 3.10: `str | None`, `list[dict]`).
- Archivos siempre con `with open(...)`; capturar excepciones específicas,
  nunca `except Exception` a secas.
- Docstrings breves en español.
- No agregar dependencias nuevas.

## Ejemplo del estilo esperado

```python
# Antes
if aux >= 1000:
    desc = aux * 0.10
else:
    if aux >= 500:
        desc = aux * 0.05

# Después
UMBRAL_DESCUENTO_ALTO = 1000
TASA_DESCUENTO_ALTO = 0.10

def calcular_descuento_volumen(subtotal: float) -> float:
    """Regresa el descuento por volumen que corresponde al subtotal."""
    if subtotal >= UMBRAL_DESCUENTO_ALTO:
        return subtotal * TASA_DESCUENTO_ALTO
    if subtotal >= UMBRAL_DESCUENTO_MEDIO:
        return subtotal * TASA_DESCUENTO_MEDIO
    return 0
```

## Cómo responder

- Antes de editar, explica en 2-3 líneas qué vas a cambiar y por qué.
- Después de editar, muestra el resultado de `pytest` y `ruff check src`.
- Responde en español.
