# Bitácora de refactorización

**Nombre:** Alberto Martínez
**Matrícula:**
**Fecha:** 2026-10-07
**Repositorio:** https://github.com/albertomtzu23/M1.-Reto (rama `refactorizacion`)

Cada entrada registra el **prompt tal cual lo escribí**, lo que hizo la IA, por
qué mejora el código y el resultado de la validación (`pytest` + `ruff check src`).

---

## Línea base (antes de refactorizar)

| Métrica | Resultado |
|---|---|
| Tests | **20 passed, 0 failed** |
| `ruff check src` | **20 errores** |

Desglose de `ruff` en la línea base:

```
4  UP009   utf8-encoding-declaration
3  SIM102  collapsible-if
3  SIM115  open-file-with-context-handler
2  C901    complex-structure          (registrar_venta = 12, menu = 17)
2  N802    invalid-function-name      (hayArchivo, reporteViejoCSV)
1  SIM108  if-else-block-instead-of-if-exp
1  N816    mixed-case-variable-in-global-scope (contadorVentas)
1  SIM103  needless-bool
1  UP015   redundant-open-modes
1  I001    unsorted-imports
1  F401    unused-import              (os en reportes.py)
Found 20 errors.
```

> **Nota sobre el entorno.** El trabajo con la IA se hizo en una sesión de Claude
> con un espacio de trabajo en la nube donde la política de red bloquea PyPI,
> así que `pytest` no se pudo instalar ahí. La suite se ejecutó con un
> ejecutor mínimo equivalente (descubre y corre cada `test_*` de `tests/`,
> reinicia el sistema antes de cada prueba como hace `conftest.py` y provee
> `tmp_path`). `ruff` sí se ejecutó directamente. La evidencia final con
> `pytest` real se generó en mi equipo (ver sección *Evidencia*).

---

## Fase 0-2 · Configuración del entorno y exploración

| # | Prompt usado | Qué hizo la IA | Resultado / decisión |
|---|---|---|---|
| P1 | `vamos a usar la siguiente ruta como workstation: D:\2026\Curso IA\Modulo 1. Fundamentos Base` | Solicitó acceso a la carpeta y listó su contenido (3 documentos del reto, el proyecto y el `.zip`). | Carpeta de trabajo definida. |
| P2 | `abre el documento: M1._Plan_de_Reto_Refactoring.docx y analiza la solicitud` | Extrajo el texto del plan y resumió objetivos, las 4 fases, las 6 categorías de refactorización, la validación, la estructura de entrega y los pesos de evaluación. Detectó que el proyecto venía en `.zip` sin git. | Quedó claro que la bitácora + reflexión pesan 35 %: documentar desde el inicio. |
| P3 | `¿Sigo con eso? si` (respuesta a la propuesta de leer rúbrica y formato de entrega y diagnosticar el código) | Leyó la rúbrica y el formato de entrega, leyó los 4 módulos de `src/` y los tests, corrió la línea base (20 tests OK, 20 errores de ruff) y entregó un inventario de *code smells*, las trampas de comportamiento y un plan de 8 refactorizaciones. | Ver *Diagnóstico* abajo. La IA señaló contradicciones entre documentos (ubicación de la bitácora, destino del PR, "no modificar tests" vs. "agregar tests"). Decidí seguir el formato oficial (`/docs`) y **agregar** tests sin tocar los existentes. |
| P4 | `Tengo en GitHub un repositorio, clonalo y carga el codigo, la liga es: https://github.com/albertomtzu23/M1.-Reto.git, realiza el registro de los prompts en la bitacora.` | Clonó el repo, cargó el código base intacto en `main` (commit `chore: carga del código base`), creó la rama `refactorizacion`, escribió `CLAUDE.md`, `.claudeignore`, `.gitignore` y esta bitácora. | Configuración del proyecto lista. |

### Diagnóstico de *code smells* (resultado de P3)

| Archivo | Problema | Gravedad |
|---|---|---|
| `gestor.py` | `registrar_venta` hace todo: valida, calcula, descuenta stock, arma ticket y guarda (complejidad 12) | Alta |
| `gestor.py` | Condicionales anidados de 4 niveles (validación y regla VIP) | Alta |
| `gestor.py` | Cálculo de descuentos duplicado entre `registrar_venta` y `cotizar` | Alta |
| `main.py` | `menu()` es una cadena gigante de `if/elif` (complejidad 17) | Alta |
| todos | Números mágicos (`0.16`, `1000`, `500`, `0.10`, `0.05`, `0.02`, `200`, `5`) | Media |
| todos | Nombres crípticos (`x`, `aux`, `temp2`, `t`, `d`, `hacer_cosa`) y camelCase mezclado | Media |
| `almacen.py`, `reportes.py` | `open()` sin `with`; `except Exception` genérico | Media |
| `gestor.py`, `reportes.py` | Código muerto (`calcular_descuento_viejo`, `reporteViejoCSV`, `exportar_txt` comentado), `import os` sin usar | Baja |
| `reportes.py` | Ordenamiento de burbuja manual en lugar de `sorted()` | Baja |
| todos | Sin type hints; estado global mutable; `print` mezclado con lógica | Media |

**Trampas de comportamiento identificadas por la IA** (pasaron a `CLAUDE.md`):
`cotizar` no aplica VIP ni valida stock; el ticket imprime `str(float)`
(`$20.0`); `INVENTARIO`, `VENTAS`, `agregarProducto`, `buscarProducto` y
`ultimo_error` son API congelada.

### Decisiones de configuración

- **`CLAUDE.md`**: contexto del proyecto, comandos, reglas no negociables (no
  tocar `tests/` ni `pyproject.toml`, API congelada, salida idéntica, un cambio
  por commit), reglas de negocio a preservar, convenciones con un ejemplo
  antes/después, y formato de respuesta esperado.
- **`.claudeignore`**: entornos virtuales, cachés (`__pycache__`,
  `.pytest_cache`, `.ruff_cache`), basura de macOS del `.zip`
  (`.DS_Store`, `__MACOSX`), documentos `.docx` del curso y la plantilla de
  bitácora (para que la IA no la confunda con la bitácora real).

---

## Refactorizaciones

### Resumen

| # | Tipo | Cambio realizado | Tests | Ruff |
|---|---|---|---|---|
| 1 | Eliminar código muerto | Se quitaron 2 funciones sin uso, 1 bloque comentado, 1 import sin usar y 4 declaraciones de encoding | 20/20 ✅ | 20 → 13 |
| 2 | Constantes con nombre | 9 constantes de negocio en `gestor.py`; 17 literales reemplazados en `gestor.py` y `reportes.py` | 20/20 ✅ | 13 → 13 |
| 3 | | | | |
| 4 | | | | |
| 5 | | | | |

---

### Refactorización 1 · Eliminar código muerto y comentarios obsoletos

**Cómo se diseñó el prompt.** No lo escribí de cero: primero le pedí a la IA
`vamos a continuar con la refactorización, ayudame a crear un promp limpio y funcional`.
Me propuso una estructura (contexto → objetivo → alcance cerrado → verificación
previa → restricciones → resultado esperado medible → formato de salida). Ajusté
el título ("código **no funcional**" en lugar de "código muerto") y lo envié.

**Prompt usado (tal cual):**

```text
Refactorización 1 — Eliminar código no funcional y comentarios obsoletos.

Contexto: sigue las reglas de CLAUDE.md. Estamos en la rama `refactorizacion`.
Línea base: 20 tests pasando y 20 errores de ruff.

Objetivo: quitar de src/ todo el código que no se ejecuta ni aporta,
SIN cambiar el comportamiento del programa.

Alcance (solo esto):
1. gestor.py: eliminar la función `calcular_descuento_viejo` y el bloque
   comentado de `exportar_txt`.
2. reportes.py: eliminar la función `reporteViejoCSV` y el `import os` sin usar.
3. Los 4 archivos de src/: eliminar la línea `# -*- coding: utf-8 -*-`.

Antes de borrar:
- Busca en src/ y tests/ cada nombre y confirma que nadie lo usa.
  Si encuentras un uso, detente y avísame en lugar de borrar.

Restricciones:
- No renombres, no reformatees y no toques ninguna otra línea.
- `hayArchivo` NO es código muerto (main.py la usa): no la toques.
- No modifiques tests/ ni pyproject.toml.

Validación:
- Ejecuta los tests y `ruff check src`.
- Resultado esperado: 20 tests pasando y 13 errores de ruff
  (desaparecen 4 UP009, 1 F401, 1 N802 y 1 SIM115).
  Si el resultado es distinto, explica por qué antes de continuar.

Al terminar:
1. Muéstrame el diff.
2. Registra la entrada #1 en docs/bitacora.md: este prompt tal cual,
   el cambio realizado, la justificación y el resultado de tests y ruff.
3. Haz un commit `refactor: elimina código muerto y declaraciones de encoding`
   y súbelo a GitHub.
```

**Verificación previa (hecha por la IA antes de borrar).** Búsqueda en `src/` y
`tests/` de `calcular_descuento_viejo`, `exportar_txt`, `reporteViejoCSV` y `os.`:
los tres nombres solo aparecían en su propia definición; `os.` solo se usa en
`almacen.py` y `tests/conftest.py`, que tienen su propio `import os`, así que el
de `reportes.py` sobraba. Las líneas de encoding de `tests/` se dejaron (fuera de
alcance y los tests no se modifican).

**Cambio realizado** (4 archivos, 32 líneas eliminadas, 0 agregadas):

| Archivo | Eliminado |
|---|---|
| `src/gestor.py` | `calcular_descuento_viejo()` (fórmula de 2023 sin llamadas) y el bloque comentado `exportar_txt` |
| `src/reportes.py` | `reporteViejoCSV()` (reporte que "ya no se usa") e `import os` |
| `src/almacen.py`, `src/gestor.py`, `src/main.py`, `src/reportes.py` | `# -*- coding: utf-8 -*-` |

**Justificación.**
- El código muerto obliga a quien lee a preguntarse "¿esto se usa?" y a
  mantenerlo; los comentarios "por si acaso" no protegen nada porque git ya
  guarda el historial.
- `reporteViejoCSV` además tenía dos *code smells* propios (nombre camelCase y
  `open()` sin `with`): borrarla resuelve ambos sin tener que corregir código
  que nadie ejecuta.
- En Python 3 UTF-8 es la codificación por defecto del código fuente; la
  declaración es ruido heredado de Python 2.

**Resultado.**

| | Antes | Después |
|---|---|---|
| Tests | 20 passed | **20 passed** |
| `ruff check src` | 20 errores | **13 errores** |

Desaparecieron exactamente los esperados: 4 × UP009, 1 × F401, 1 × N802
(`reporteViejoCSV`) y 1 × SIM115 (`open` en `reporteViejoCSV`). El resultado
coincidió con la predicción del prompt, así que no hubo que corregir nada.

Errores de ruff restantes:

```
3  SIM102  collapsible-if
2  C901    complex-structure
2  SIM115  open-file-with-context-handler
1  SIM108  if-else-block-instead-of-if-exp
1  N802    invalid-function-name      (hayArchivo)
1  N816    mixed-case-variable-in-global-scope
1  SIM103  needless-bool
1  UP015   redundant-open-modes
1  I001    unsorted-imports
Found 13 errors.
```

**Qué aprendí.** Dar un resultado esperado *numérico* (13 errores y cuáles
desaparecen) convierte la validación en una comprobación objetiva: si el número
no cuadra, sé que la IA tocó algo de más o de menos. Advertir explícitamente que
`hayArchivo` **no** es código muerto evitó un falso positivo probable (es una
función trivial que parece sobrar).

### Refactorización 2 · Reemplazar números mágicos por constantes

**Cómo se diseñó el prompt.** Pedí a la IA ayuda para armarlo
(`¿Quieres que te ayude a armar el prompt igual que con este? Si`). Respecto al
prompt 1 se agregaron tres técnicas: (a) **dar los nombres de las constantes**
en lugar de dejar que la IA los invente; (b) **advertir una trampa técnica**
(reordenar aritmética con floats puede cambiar el redondeo); (c) un **resultado
esperado de "sin cambio"** en ruff más una verificación propia (búsqueda de
literales), porque el linter no detecta este *code smell*. Lo envié sin cambios.

**Prompt usado (tal cual):**

```text
Refactorización 2 — Reemplazar números mágicos por constantes con nombre.

Contexto: sigue las reglas de CLAUDE.md. Rama `refactorizacion`.
Estado actual: 20 tests pasando y 13 errores de ruff.

Objetivo: que cada regla de negocio tenga un nombre y viva en un solo lugar,
SIN cambiar el comportamiento ni la estructura del código.

Alcance (solo esto):
1. Al inicio de gestor.py, después de los imports, crea una sección
   "Reglas de negocio" con estas constantes:
   TASA_IVA = 0.16
   UMBRAL_DESCUENTO_ALTO = 1000
   TASA_DESCUENTO_ALTO = 0.10
   UMBRAL_DESCUENTO_MEDIO = 500
   TASA_DESCUENTO_MEDIO = 0.05
   PREFIJO_VIP = "VIP"
   MONTO_MINIMO_VIP = 200
   TASA_DESCUENTO_VIP = 0.02
   STOCK_MINIMO = 5
2. Sustituye los valores literales por las constantes en
   `registrar_venta` y `cotizar` (gestor.py).
   En la regla VIP, el 3 de `len(cliente) >= 3` y de `cliente[0:3]`
   sale del largo del prefijo: usa `len(PREFIJO_VIP)`.
3. En reportes.py usa `gestor.STOCK_MINIMO` en lugar del 5
   (en `productos_stock_bajo` y en `reporte_inventario`).

Restricciones:
- Solo cambia literales por nombres. No reestructures condicionales,
  no extraigas funciones y no renombres variables: eso va en otras
  refactorizaciones.
- No reordenes operaciones aritméticas (por ejemplo, NO conviertas
  `base + base * 0.16` en `base * (1 + TASA_IVA)`): con floats
  el redondeo podría cambiar.
- No toques el `n=3` de `mas_vendidos` (es un parámetro, no una regla).
- No modifiques tests/ ni pyproject.toml.

Validación:
- Ejecuta los tests y `ruff check src`.
- Resultado esperado: 20 tests pasando y 13 errores de ruff (sin cambio:
  ruff no detecta números mágicos con la configuración del proyecto).
- Verificación adicional: busca en src/ los literales 0.16, 0.10, 0.05,
  0.02, 1000, 500, 200 y "VIP", y el `< 5`. Fuera de la definición de
  las constantes no debe quedar ninguno.

Al terminar:
1. Muéstrame el diff.
2. Registra la entrada #2 en docs/bitacora.md: este prompt tal cual,
   el cambio realizado, la justificación y el resultado de tests y ruff.
3. Haz un commit `refactor: reemplaza números mágicos por constantes con nombre`
   y súbelo a GitHub.
```

**Cambio realizado** (2 archivos):

| Archivo | Cambio |
|---|---|
| `src/gestor.py` | Nueva sección *Reglas de negocio* con 9 constantes. 15 literales reemplazados en `registrar_venta` (umbrales y tasas de descuento, regla VIP, IVA) y `cotizar` (umbrales, tasas, IVA). |
| `src/reportes.py` | `< 5` → `< gestor.STOCK_MINIMO` en `productos_stock_bajo` y `reporte_inventario`. |

**Justificación.**
- Cada regla de negocio ahora tiene **nombre** (`TASA_IVA` dice qué es; `0.16` no) y
  un **único lugar**: si cambia el IVA o el umbral de descuento se edita una línea,
  no cinco repartidas en dos funciones y dos archivos.
- Hace visible la duplicación entre `registrar_venta` y `cotizar` (mismas
  constantes, misma lógica), que se atacará en la extracción de funciones.
- `STOCK_MINIMO` estaba repetido en dos funciones de `reportes.py`: ahora el
  reporte y la alerta no pueden desincronizarse.

**Resultado.**

| | Antes | Después |
|---|---|---|
| Tests | 20 passed | **20 passed** |
| `ruff check src` | 13 errores | **13 errores** (esperado: ruff no mide números mágicos) |
| Literales de negocio fuera de las constantes | 17 | **0** |

**Verificación extra de equivalencia (iniciativa de la IA).** Los tests no
prueban los umbrales exactos (500, 1000, el monto VIP de 200) ni clientes como
`"VI"`, `"vip1"` o `None`. La IA comparó la versión anterior contra la nueva
ejecutando ambas con 926 combinaciones (11 precios × 6 cantidades × 7 clientes,
`cotizar` + `registrar_venta`, más stock 0/4/5/6 en reportes):
**0 diferencias**.

**Tropiezo.** Al aplicar el cambio en `reportes.py`, el primer reemplazo
automático que usó la IA (`["stock"] < 5`) coincidía con las dos líneas a la
vez; su propio chequeo (`assert` de "exactamente una coincidencia") lo detuvo
antes de escribir el archivo y lo corrigió. Lección: pedir cambios que
verifiquen cuántas veces aplican evita reemplazos de más.

**Hallazgo para después.** Al revisar `gestor.py` se vio que la constante
global `MODO_DEBUG = False` no se usa en ningún lado: es código muerto que el
prompt 1 no incluyó porque su alcance era una lista cerrada. Queda anotado para
la refactorización de nombres/estado global. Aprendizaje: un alcance cerrado
evita cambios de más, pero conviene pedir también "reporta otros casos que
encuentres, sin tocarlos".

---

## Intentos fallidos y ajustes

*(Se registran aquí los prompts que no dieron el resultado esperado y cómo se corrigieron.)*

| Situación | Qué pasó | Cómo se resolvió |
|---|---|---|
| Clonar el repo desde la carpeta local | El shell de mi equipo usado por la IA no tiene salida a GitHub (proxy 403); quedó una carpeta `M1.-Reto/` vacía con un `.git` incompleto en `D:\2026\Curso IA\Modulo 1. Fundamentos Base`. | Se clonó en el espacio de trabajo de la nube y después se copió el repositorio completo (con su historial) a esa carpeta; los archivos temporales de git requirieron autorizar borrado en la carpeta. |
| Instalar `pytest` en la nube | La política de red bloquea PyPI. | Ejecutor de pruebas equivalente para validar cada paso; `pytest` real en mi equipo para la evidencia final. |
| Push a GitHub | Primero la cuenta de GitHub no estaba vinculada; después de vincularla, el push seguía con 403 porque faltaba instalar la app de Claude para GitHub con acceso al repositorio. | Instalé la app de Claude en mi cuenta con acceso a `M1.-Reto`; el push de `main` y `refactorizacion` funcionó. |

---

## Evidencia

*(pendiente: salida final de `pytest` y `ruff check src`)*
