# Gestor de inventario y ventas — Tienda "La Esquina"

Aplicación de consola en Python para administrar el inventario y las ventas de
una tienda pequeña. Permite:

- dar de alta productos;
- registrar ventas con descuentos por volumen, descuento extra para clientes
  VIP e IVA, imprimiendo el ticket;
- cotizar una compra;
- ver alertas de stock bajo, el reporte de inventario, el resumen de ventas y
  los productos más vendidos;
- guardar y cargar los datos en JSON.

Este repositorio es la entrega del **reto "Refactorización asistida por IA"**
(Módulo 1, Fundamentos y Herramientas Base). Parte de un código funcional pero
de baja calidad y lo mejora **sin cambiar su comportamiento**, usando Claude
como asistente. El proceso completo está en [`docs/bitacora.md`](docs/bitacora.md)
y las conclusiones en [`docs/reflexion.md`](docs/reflexion.md).

## Estado del código

| Métrica | Código original | Después del reto |
|---|---|---|
| Errores de `ruff check src` | 20 | **0** |
| Errores de `mypy --strict src` | 58 | **0** |
| Pruebas | 20 | **62** (las 20 originales sin modificar + 42 nuevas) |
| Prueba de mutación: errores introducidos a propósito que la suite detecta | 0 / 10 | **10 / 10** |

## Requisitos previos

- Python **3.10** o superior.
- git.
- Dependencias de [`requirements.txt`](requirements.txt): `pytest` y `ruff`.

## Instalación

```bash
# 1. Clonar el repositorio y cambiar a la rama del reto
git clone https://github.com/albertomtzu23/M1.-Reto.git
cd M1.-Reto
git checkout refactorizacion

# 2. Crear el entorno virtual
python -m venv .venv
```

Activar el entorno virtual:

| Sistema | Comando |
|---|---|
| Windows (CMD) | `.venv\Scripts\activate` |
| Windows (PowerShell) | `.venv\Scripts\Activate.ps1` |
| Linux / macOS | `source .venv/bin/activate` |

```bash
# 3. Instalar dependencias
pip install -r requirements.txt
```

## Comandos

Todos se ejecutan desde la raíz del repositorio.

```bash
# Pruebas: deben pasar las 62
pytest

# Linter: debe responder "All checks passed!"
ruff check src

# Verificación de tipos (opcional)
pip install mypy
mypy --strict src
```

`mypy` **no** está en `requirements.txt`: se usó como verificación adicional
durante el reto y se instala aparte.

### Ejecutar la aplicación

```bash
python src/main.py
```

> **Importante:**
> - Ejecútala **desde la raíz** para que cargue los datos de ejemplo
>   (`datos_ejemplo.json`). Con `cd src && python main.py` el programa arranca
>   sin productos, porque busca el archivo en la carpeta desde donde se ejecuta.
> - La opción **8 (Guardar y salir)** **sobrescribe** `datos_ejemplo.json`.
>   Para restaurar los datos originales: `git checkout datos_ejemplo.json`.

## Estructura del proyecto

```
.
├── CLAUDE.md                 # Instrucciones para Claude: reglas, convenciones, comandos
├── .claudeignore             # Archivos que la IA no debe leer
├── README.md
├── requirements.txt          # pytest y ruff
├── pyproject.toml            # Configuración de ruff y pytest (original, sin cambios)
├── datos_ejemplo.json        # Datos de ejemplo para la app
├── BITACORA_TEMPLATE.md      # Plantilla original del reto
├── src/
│   ├── gestor.py             # Lógica de negocio: productos, ventas, descuentos, ticket
│   ├── almacen.py            # Carga y guardado en JSON
│   ├── reportes.py           # Reportes e indicadores
│   └── main.py               # Menú interactivo de consola
├── tests/
│   ├── conftest.py           # Original
│   ├── test_gestor.py        # Original
│   ├── test_almacen.py       # Original
│   ├── test_reportes.py      # Original
│   └── test_casos_limite.py  # Nuevo: fronteras, validaciones y bug corregido
└── docs/
    ├── bitacora.md           # Cada paso: prompt, cambio, justificación y resultados
    └── reflexion.md          # Aprendizajes y conclusiones
```

## Qué se hizo

Cada paso es un commit propio en la rama `refactorizacion`. El detalle, con el
prompt usado tal cual, está en la [bitácora](docs/bitacora.md).

1. **Eliminar código muerto:** dos funciones sin uso, un bloque comentado, un
   import sin usar y las declaraciones de encoding.
2. **Constantes con nombre:** IVA, umbrales y tasas de descuento, regla VIP y
   stock mínimo en lugar de números mágicos.
3. **Extraer funciones:** `registrar_venta` se dividió en cuatro funciones, y
   `cotizar` ya no duplica el cálculo de descuentos.
4. **Simplificar condicionales:** cláusulas de guarda en lugar de `if`
   anidados hasta cuatro niveles.
5. **Nombres descriptivos:** snake_case y docstrings en los cuatro módulos.
6. **Manejo de errores:** `with open(...)` y excepciones específicas en lugar
   de `except Exception`.
7. **Dividir `menu()`:** una función por opción y un diccionario de despacho,
   en lugar de una cadena de `if/elif` para las ocho opciones.
8. **Type hints:** en todas las funciones, validados con `mypy --strict`.

Además de las refactorizaciones:

- **Corrección de un bug** (cambio de comportamiento intencional, en un
  commit aparte): `cargar_datos` vaciaba el inventario y después tronaba si el
  JSON no tenía la estructura esperada. Ahora regresa `False` sin tocar el
  estado.
- **Pruebas de casos límite:** 37 casos nuevos sobre las fronteras de
  descuento y VIP, el orden de las validaciones, el ticket, los reportes y la
  persistencia con acentos. Todos pasan también con el código original sin
  refactorizar, lo que demuestra que el comportamiento se conservó.

Antes y después de cada refactorización se corrieron las pruebas y el linter.
Además se comparó la versión anterior contra la nueva con cientos de casos y
una sesión simulada completa del menú.

## Sobre el reto

Reglas originales que se respetaron:

- Las pruebas originales (`test_gestor.py`, `test_almacen.py`,
  `test_reportes.py` y `conftest.py`) y `pyproject.toml` **no se modificaron**.
  Las pruebas nuevas están en un archivo aparte.
- El código de `src/` pasa `ruff check src` sin errores.
- El comportamiento observable del programa se mantiene, salvo la corrección
  del bug, que está documentada.
- `agregarProducto` y `buscarProducto` conservan su nombre en camelCase porque
  las pruebas originales los usan.
