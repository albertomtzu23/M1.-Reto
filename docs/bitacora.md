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
| 3 | Extraer funciones | `registrar_venta` dividida en 4 funciones; `cotizar` reutiliza `calcular_descuento_volumen` | 20/20 ✅ | 13 → 11 |
| 4 | Simplificar condicionales | Cláusulas de guarda en `_validar_venta` y `calcular_descuento_vip`; `hayArchivo` regresa la condición | 20/20 ✅ | 11 → 7 |
| 5 | Renombrar | Nombres descriptivos en snake_case en los 4 módulos; `MODO_DEBUG` eliminado; comentarios → docstrings; imports ordenados | 20/20 ✅ | 7 → 4 |
| 6 | Manejo de errores | `with open` en lectura y escritura; `except Exception` → `except (ValueError, RecursionError)` | 20/20 ✅ | 4 → 1 |
| C1 | Corrección de bug (cambio intencional) | `cargar_datos` valida la estructura antes de modificar el estado; 5 pruebas nuevas en `tests/test_casos_limite.py` | 25/25 ✅ | 1 → 1 |
| 7 | Dividir función gigante | `menu()` → 5 funciones `menu_*` + diccionario `ACCIONES`; complejidad 17 → < 10 | 25/25 ✅ | 1 → **0** |
| 8 | Type hints | Anotaciones en las 28 funciones, globales y contenedores; alias `Producto`/`Venta`; `mypy --strict` 58 → 0 | 25/25 ✅ | 0 → 0 |
| T | Pruebas de casos límite | 37 casos nuevos (fronteras de descuento y VIP, validaciones, ticket, reportes, ñ); mutación: suite original 0/10 → completa 10/10 | 62/62 ✅ | 0 → 0 |

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

### Refactorización 3 · Extraer funciones de `registrar_venta`

**Cómo se diseñó el prompt.** Pedí a la IA armarlo (`¿Te armo el prompt? Si`).
Antes de proponerlo, **la IA hizo un prototipo en una copia aparte** para que el
resultado esperado del prompt fuera exacto (11 errores de ruff, 0 diferencias)
en vez de una estimación. Técnicas nuevas respecto a los prompts 1 y 2:
(a) **empezar por el problema** (5 responsabilidades, complejidad 12) y no solo
por la instrucción; (b) **diseñar de antemano** nombre, entradas y salida de
cada función nueva, que es donde más se equivoca la IA al extraer;
(c) **pedir justificación antes de actuar** en un punto dudoso
(`desc > 0` vs. valor redondeado); (d) **delimitar** qué corresponde a las
refactorizaciones 4 y 5 para que no se mezclen. Lo envié sin cambios.

**Prompt usado (tal cual):**

```text
Refactorización 3 — Extraer funciones de `registrar_venta` y eliminar
la duplicación con `cotizar`.

Contexto: sigue las reglas de CLAUDE.md. Rama `refactorizacion`.
Estado actual: 20 tests pasando y 13 errores de ruff.

Problema: `registrar_venta` hace 5 cosas (validar, calcular descuentos,
calcular impuestos, actualizar inventario y armar el ticket) y tiene
complejidad 12. Además, el cálculo de descuento por volumen está
duplicado en `cotizar`.

Objetivo: dividir `registrar_venta` en funciones con una sola
responsabilidad, SIN cambiar el comportamiento.

Alcance (solo esto, todo en gestor.py):
1. `calcular_descuento_volumen(subtotal)`: regresa el descuento por
   volumen. Úsala en `registrar_venta` Y en `cotizar`.
   Debe regresar `0` (entero) cuando no hay descuento, igual que hoy:
   el valor se guarda en el JSON y `0` vs `0.0` sería un cambio visible.
2. `calcular_descuento_vip(cliente, subtotal, descuento)`: regresa el
   descuento extra VIP o 0. En `registrar_venta` se suma así:
   `desc = desc + calcular_descuento_vip(...)` (mismo orden de la suma).
3. `_validar_venta(codigo, cantidad)`: regresa el producto o None, y deja
   el mensaje en `ultimo_error`. Conserva el orden de las validaciones.
4. `_armar_ticket(venta)`: recibe el dict de la venta y regresa el texto
   del ticket, idéntico carácter por carácter.

Restricciones:
- MUEVE los `if` anidados tal cual a las nuevas funciones: aplanarlos es
  la refactorización 4. No renombres variables (`aux`, `desc`, `temp2`):
  eso es la refactorización 5.
- No cambies firmas ni valores de retorno de funciones públicas.
- No reordenes operaciones aritméticas.
- El ticket hoy decide si imprime la línea de descuento con `desc > 0`
  (valor sin redondear). Si en `_armar_ticket` usas
  `venta["descuento"] > 0` (valor redondeado), explica por qué es
  equivalente o no lo hagas.
- No modifiques tests/ ni pyproject.toml.

Validación:
- Ejecuta los tests y `ruff check src`.
- Resultado esperado: 20 tests pasando y 11 errores de ruff
  (desaparecen C901 de `registrar_venta` y SIM108; los 3 SIM102
  se quedan porque los `if` se movieron sin aplanar).
- Repite la comparación antes/después de la refactorización 2 (casos
  límite de precio, cantidad y cliente, incluyendo el ticket completo):
  debe dar 0 diferencias.

Al terminar:
1. Muéstrame el diff.
2. Registra la entrada #3 en docs/bitacora.md: este prompt tal cual,
   el cambio realizado, la justificación y el resultado de tests y ruff.
3. Haz un commit `refactor: extrae funciones de registrar_venta y elimina duplicación con cotizar`
   y súbelo a GitHub.
```

**Cambio realizado** (`src/gestor.py`, +52 / −45 líneas):

| Función nueva | Responsabilidad | Usada por |
|---|---|---|
| `calcular_descuento_volumen(subtotal)` | Descuento por volumen (10 % / 5 % / 0) | `registrar_venta` **y** `cotizar` |
| `calcular_descuento_vip(cliente, subtotal, descuento)` | Extra VIP o 0 | `registrar_venta` |
| `_validar_venta(codigo, cantidad)` | Validaciones y mensaje en `ultimo_error` | `registrar_venta` |
| `_armar_ticket(venta)` | Texto del ticket | `registrar_venta` |

`registrar_venta` quedó como un orquestador de ~25 líneas que se lee de arriba
abajo: validar → calcular → descontar stock → registrar → ticket. `cotizar` ya no
duplica la lógica de descuentos.

**Justificación.**
- **Una responsabilidad por función**: cada regla se puede leer, probar y
  cambiar por separado (p. ej. cambiar el formato del ticket ya no implica
  tocar la función que mueve inventario).
- **Se elimina la duplicación**: antes, cambiar un umbral de descuento exigía
  editar `registrar_venta` y `cotizar` y acordarse de ambas; ahora es un solo
  lugar, y la cotización no puede desalinearse de la venta.
- **Complejidad**: `registrar_venta` bajó de 12 a menos de 10 (ya no aparece en C901).

**Respuesta al punto dudoso (`desc > 0` vs. `venta["descuento"] > 0`).**
La IA usó el valor redondeado y lo justificó: el descuento solo puede valer
`0` o un monto ≥ 4. El de volumen exige subtotal ≥ 500 (→ ≥ 25) y el VIP exige
que `subtotal − descuento > 200` (→ extra > 4). Redondear a 2 decimales solo
convertiría en 0 un valor menor a 0.005, que no puede ocurrir. Además, la
comparación antes/después incluye el ticket completo y dio 0 diferencias.

**Decisiones que hay que transparentar.**
- `calcular_descuento_volumen` **no** se movió "tal cual": se escribió con
  `return` tempranos en lugar del `if / else: if / else` original. Es la única
  forma de que desaparezca SIM108, cosa que el propio prompt esperaba, así que
  el prompt tenía una pequeña contradicción interna. Los `if` anidados de
  validación y VIP sí se movieron sin tocar (siguen los 3 SIM102).
- **Corrección hecha al revisar el diff**: al extraer la regla VIP se perdía el
  comentario que explicaba la condición ("solo si su compra, ya con descuento,
  pasa de cierto monto"). Se pasó esa información al docstring de
  `calcular_descuento_vip` para no perder conocimiento del negocio.

**Resultado.**

| | Antes | Después |
|---|---|---|
| Tests | 20 passed | **20 passed** |
| `ruff check src` | 13 errores | **11 errores** (−C901 `registrar_venta`, −SIM108) |
| Equivalencia antes/después (926 casos, incluye ticket) | — | **0 diferencias** |
| Funciones con lógica de descuento por volumen | 2 copias | **1** |

**Qué aprendí.** Que la IA prototipara antes de escribir el prompt hizo que
el resultado esperado fuera un dato y no una suposición. Revisar el diff me
mostró algo que ninguna prueba detecta: al extraer funciones se pierden
comentarios con conocimiento del negocio. Y un prompt muy detallado puede
contradecirse ("mueve tal cual" + "desaparece SIM108"): conviene releerlo
buscando instrucciones que choquen.

---

### Refactorización 4 · Simplificar condicionales con cláusulas de guarda

**Cómo se diseñó el prompt.** Pedí a la IA armarlo (`¿Te armo el prompt? SI`).
La IA volvió a prototipar antes de proponerlo y, al hacerlo, **detectó que su
propia verificación de equivalencia era insuficiente** para este cambio: solo
comparaba ventas exitosas, y lo que se iba a tocar eran las validaciones. Amplió
la comparación a los caminos de error antes de escribir el prompt. Técnicas
nuevas: (a) **anticipar el error típico** de la refactorización (invertir mal una
frontera al convertir un `if` en guarda) y pedir que cada inversión se
explique; (b) señalar una **trampa del lenguaje** (el orden del cortocircuito
con `None`); (c) **ajustar la validación al riesgo** del cambio. Lo envié sin
cambios.

**Prompt usado (tal cual):**

```text
Refactorización 4 — Simplificar condicionales anidados con cláusulas de guarda.

Contexto: sigue las reglas de CLAUDE.md. Rama `refactorizacion`.
Estado actual: 20 tests pasando y 11 errores de ruff.

Problema: hay condicionales anidados hasta 4 niveles que obligan a leer
de afuera hacia adentro para saber qué pasa en cada caso, y un
`if/else` que solo regresa True o False.

Objetivo: aplanar esos condicionales para que cada regla se lea en una
línea, SIN cambiar el comportamiento.

Alcance (solo esto):
1. gestor.py, `_validar_venta`: reescríbela con cláusulas de guarda
   (un `if` por validación que asigna `ultimo_error` y regresa None),
   en este orden exacto: código vacío → producto no existe →
   cantidad inválida → stock insuficiente. Al final regresa el producto.
2. gestor.py, `calcular_descuento_vip`: reemplaza los 4 `if` anidados por
   cláusulas de guarda. La comprobación de `len(...)` + `cliente[0:...]`
   se puede expresar con `cliente.startswith(PREFIJO_VIP)`.
3. almacen.py, `hayArchivo`: el `if/else` que regresa True/False se
   reemplaza por `return os.path.exists(ruta)`. No la renombres.

Restricciones:
- Al invertir una condición para convertirla en guarda, cuida las
  fronteras: `>` se invierte a `<=` y `>=` a `<`. Explica en el diff
  cada inversión que hagas.
- Conserva el cortocircuito con None: `cantidad is None or cantidad <= 0`
  (si se evalúa `<=` con None, truena).
- No cambies los mensajes de `ultimo_error` ni qué mensaje queda en
  cada caso.
- No toques `menu()` de main.py: su complejidad es otra refactorización.
- No renombres variables ni funciones (eso es la refactorización 5).
- No modifiques tests/ ni pyproject.toml.

Validación:
- Ejecuta los tests y `ruff check src`.
- Resultado esperado: 20 tests pasando y 7 errores de ruff
  (desaparecen los 3 SIM102 y el SIM103).
- Repite la comparación antes/después de ventas exitosas (casos límite
  de precio, cantidad y cliente): 0 diferencias.
- Como este cambio toca las validaciones, compara también los caminos de
  error: código None/""/inexistente × cantidad None/negativa/0/mayor al
  stock, en `registrar_venta` y `cotizar`, revisando valor de retorno,
  `ultimo_error`, stock y número de ventas; y la frontera VIP exacta
  (compra de 200, 199.99 y 200.01). Debe dar 0 diferencias.

Al terminar:
1. Muéstrame el diff.
2. Registra la entrada #4 en docs/bitacora.md: este prompt tal cual,
   el cambio realizado, la justificación y el resultado de tests y ruff.
3. Haz un commit `refactor: aplana condicionales con cláusulas de guarda`
   y súbelo a GitHub.
```

**Cambio realizado** (`src/gestor.py` +16/−21, `src/almacen.py` +1/−4):

| Función | Antes | Después |
|---|---|---|
| `_validar_venta` | 4 niveles de `if/else` anidados (profundidad 5) | 4 cláusulas de guarda de un nivel + `return` final |
| `calcular_descuento_vip` | 4 `if` anidados | 2 guardas + `return` |
| `hayArchivo` | `if cond: return True else: return False` | `return os.path.exists(ruta)` |

**Explicación de cada condición invertida** (pedida por el prompt):

| # | Condición original (para continuar) | Guarda (para salir) | Regla aplicada |
|---|---|---|---|
| 1 | `codigo is not None and codigo != ""` | `codigo is None or codigo == ""` | De Morgan: `not (A and B)` = `not A or not B` |
| 2 | `codigo in INVENTARIO` | `codigo not in INVENTARIO` | Negación directa |
| 3 | `cantidad is not None and cantidad > 0` | `cantidad is None or cantidad <= 0` | De Morgan + `>` se invierte a `<=`. El `is None` va primero: si `cantidad` es None, el `or` corta y nunca se evalúa `None <= 0` (que lanzaría `TypeError`). |
| 4 | `stock >= cantidad` | `stock < cantidad` | `>=` se invierte a `<` (stock igual a la cantidad **sí** se vende) |
| 5 | `cliente != "" and cliente is not None` + `len(cliente) >= len(PREFIJO_VIP)` + `cliente[0:len(...)] == PREFIJO_VIP` | `not cliente or not cliente.startswith(PREFIJO_VIP)` | `not cliente` cubre `""` y `None`; `startswith` ya implica la longitud mínima. |
| 6 | `subtotal - descuento > MONTO_MINIMO_VIP` | `subtotal - descuento <= MONTO_MINIMO_VIP` | `>` se invierte a `<=`: una compra de **exactamente 200** sigue **sin** descuento VIP |

Matiz de la inversión 5: `not cliente` también trata como "sin cliente" otros
valores *falsy* (p. ej. `0`), cosa que el original no hacía (habría lanzado
error en `len()`). En la práctica `cliente` solo llega como texto desde
`main.py` o como `None`, así que no hay cambio observable.

**Justificación.**
- Con guardas, cada regla se lee en **una línea**, en el orden en que se
  aplica, y el "camino feliz" queda al final sin sangría. Antes había que
  emparejar cada `else` con su `if` cuatro niveles arriba para saber qué
  mensaje correspondía a qué validación.
- Agregar o quitar una validación ahora es agregar o quitar un bloque de 3
  líneas, sin reacomodar la sangría de todo lo demás.
- `startswith` expresa la intención ("empieza con VIP") en lugar de la
  mecánica (medir largo + rebanar + comparar).
- `hayArchivo`: devolver la condición directamente elimina 3 líneas que
  no aportaban nada.

**Resultado.**

| | Antes | Después |
|---|---|---|
| Tests | 20 passed | **20 passed** |
| `ruff check src` | 11 errores | **7 errores** (−3 SIM102, −1 SIM103) |
| Equivalencia de ventas exitosas (926 casos) | — | **0 diferencias** |
| Equivalencia de caminos de error y frontera VIP (53 casos) | — | **0 diferencias** |
| Profundidad máxima de anidamiento en `_validar_venta` | 5 | **2** |

**Qué aprendí.** La verificación tiene que diseñarse según lo que el
cambio puede romper: la comparación que bastaba para las refactorizaciones 2
y 3 no revisaba ni un solo mensaje de error, que es justo lo que esta tocaba.
Pedir a la IA que *explique* cada inversión de condición la obliga a hacer
explícito el razonamiento donde más se equivoca (fronteras y `None`), y deja
evidencia revisable en vez de un "confía en mí".

---

### Refactorización 5 · Nombres descriptivos en snake_case y docstrings

**Cómo se diseñó el prompt.** Pedí a la IA armarlo
(`¿Te armo el prompt de la refactorización 5? si`). En el prototipo apareció
un **efecto secundario no obvio**: los nombres más largos hicieron que 4 líneas
de `reportes.py` pasaran de 88 caracteres (4 errores E501 nuevos). La IA lo
incorporó al prompt como restricción ("no debe aparecer ningún E501"). Técnicas
nuevas: (a) una **tabla de renombres explícita** (sin dejar que la IA elija
nombres); (b) distinguir **nombres de variables** de **formato de datos**
(renombrar `contadorVentas` no debe cambiar la clave `"contador"` del JSON, o
los archivos guardados antes dejarían de cargar); (c) **cerrar un pendiente**
de una refactorización anterior (`MODO_DEBUG`). Lo envié sin cambios.

**Prompt usado (tal cual):**

```text
Refactorización 5 — Renombrar variables y funciones con nombres
descriptivos en snake_case.

Contexto: sigue las reglas de CLAUDE.md. Rama `refactorizacion`.
Estado actual: 20 tests pasando y 7 errores de ruff.

Problema: hay nombres que no dicen nada (`x`, `aux`, `temp2`, `t`, `d`,
`hacer_cosa`), camelCase mezclado con snake_case (`contadorVentas`,
`hayArchivo`), una constante que nadie usa (`MODO_DEBUG`) y comentarios
que deberían ser docstrings.

Objetivo: que cada nombre diga qué contiene o qué hace, SIN cambiar el
comportamiento.

Alcance (solo esto):
1. Funciones y globales (actualiza TODAS sus referencias):
   - gestor.contadorVentas → contador_ventas  (también en almacen.py)
   - almacen.hayArchivo → existe_archivo      (también en main.py)
   - reportes.hacer_cosa → formatear_moneda
   - Elimina gestor.MODO_DEBUG (no se usa; pendiente de la refactorización 2).
2. Variables locales:
   - gestor: x→producto (agregarProducto), aux→nuevo_stock
     (actualizar_stock), temp2→resultados y k→codigo (buscarProducto),
     t→ticket (_armar_ticket), temp2→producto, aux→subtotal y
     desc→descuento (registrar_venta y cotizar).
   - almacen: d→datos, f→archivo, k→codigo, v→venta.
   - reportes: temp2→productos_bajos, s→reporte/resumen, aux→valor_total
     o unidades_por_codigo, temp→ranking, t→total/total_dia,
     p→producto, v→monto o venta, k→codigo.
   - main: op→opcion, c→codigo, n→nombre, p→precio o producto,
     s→stock, cant→cantidad, cli→cliente, v→venta, t→total,
     bajos→productos_bajos; `par[0], par[1]` → desempaca en
     `codigo, unidades`.
3. Convierte en docstrings los comentarios que describen funciones
   (agregarProducto, buscarProducto, existe_archivo, formatear_moneda,
   pedir_numero).
4. Ordena los imports de main.py (regla I001 de ruff).

Restricciones:
- NO renombres `agregarProducto`, `buscarProducto`, `INVENTARIO`,
  `VENTAS` ni `ultimo_error` (los usan los tests o main.py).
- NO cambies las claves de los diccionarios ni del JSON ("contador",
  "codigo", "stock"...): son formato de datos, no nombres de variables.
- Si un nombre más largo hace que una línea pase de 88 caracteres,
  divídela (puedes usar `+=`); no cambies el texto que se genera.
- No toques la lógica: el ordenamiento de burbuja y la estructura de
  `menu()` se quedan como están (son otras refactorizaciones).
- No modifiques tests/ ni pyproject.toml.

Validación:
- Ejecuta los tests y `ruff check src`.
- Resultado esperado: 20 tests pasando y 4 errores de ruff
  (desaparecen N802, N816 e I001; no debe aparecer ningún E501).
- Busca en src/ los nombres viejos (contadorVentas, hayArchivo,
  hacer_cosa, MODO_DEBUG, aux, temp2, temp, op, cant, cli, par):
  no debe quedar ninguno.
- Repite las comparaciones antes/después de ventas y de errores.
- Como este cambio toca reportes y persistencia, compara también:
  texto de reporte_inventario y resumen_ventas, mas_vendidos,
  total_vendido, buscarProducto, y el JSON que escribe guardar_datos
  (con carga, archivo corrupto e inexistente). Debe dar 0 diferencias.

Al terminar:
1. Muéstrame el diff.
2. Registra la entrada #5 en docs/bitacora.md: este prompt tal cual,
   el cambio realizado, la justificación y el resultado de tests y ruff.
3. Haz un commit `refactor: nombres descriptivos en snake_case y docstrings`
   y súbelo a GitHub.
```

**Cambio realizado** (4 archivos, +154 / −149 líneas):

| Tipo | Antes → Después |
|---|---|
| Global | `gestor.contadorVentas` → `contador_ventas` (en `gestor.py` y `almacen.py`) |
| Funciones | `almacen.hayArchivo` → `existe_archivo` · `reportes.hacer_cosa` → `formatear_moneda` |
| Código muerto | `gestor.MODO_DEBUG` eliminado |
| Variables (gestor) | `x`→`producto`, `aux`→`nuevo_stock` / `subtotal`, `temp2`→`resultados` / `producto`, `desc`→`descuento`, `t`→`ticket`, `k`→`codigo` |
| Variables (almacen) | `d`→`datos`, `f`→`archivo`, `k`→`codigo`, `v`→`venta` |
| Variables (reportes) | `s`→`reporte` / `resumen`, `aux`→`valor_total` / `unidades_por_codigo`, `temp`→`ranking`, `temp2`→`productos_bajos`, `t`→`total` / `total_dia` / `anterior`, `p`→`producto`, `v`→`monto` / `venta` |
| Variables (main) | `op`→`opcion`, `c`→`codigo`, `n`→`nombre`, `p`→`precio` / `producto`, `s`→`stock`, `cant`→`cantidad`, `cli`→`cliente`, `v`→`venta`, `t`→`total`, `bajos`→`productos_bajos`, `par[0], par[1]`→`codigo, unidades` |
| Docstrings | 5 comentarios `# ...` convertidos en docstrings |
| Imports | `main.py`: orden alfabético (`almacen`, `gestor`, `reportes`) |
| Líneas largas | 4 líneas de `reportes.py` divididas con `+=` (mismo texto generado) |

**Justificación.**
- Un nombre descriptivo es documentación que no se desactualiza:
  `unidades_por_codigo[codigo] += venta["cantidad"]` se entiende sin contexto;
  `aux[v["codigo"]] = aux[v["codigo"]] + v["cantidad"]` no.
- `hacer_cosa` era el caso extremo: el nombre no decía nada y había que leer
  el comentario para saber que formatea dinero. Ahora el nombre *es* el
  comentario.
- Un solo estilo (snake_case, PEP 8) elimina la duda de "¿cómo se llamaba?"
  al usar una función. Solo `agregarProducto` y `buscarProducto` conservan
  camelCase porque los tests los usan (están en `ignore-names` de ruff).
- Los docstrings, a diferencia de los comentarios, los muestran `help()` y
  los editores.

**Verificación.**

| Comprobación | Resultado |
|---|---|
| Tests | **20 passed** |
| `ruff check src` | 7 → **4 errores** (−N802, −N816, −I001; 0 E501) |
| Búsqueda de nombres viejos en `src/` | **0 restantes** (solo falsos positivos: la `n` de `\n`, palabras de docstrings y el parámetro público `n` de `mas_vendidos`) |
| Equivalencia de ventas (926 casos) | **0 diferencias** |
| Equivalencia de errores y frontera VIP (53 casos) | **0 diferencias** |
| Equivalencia de reportes y persistencia (23 salidas: textos de reportes, ranking, totales, búsqueda, JSON guardado, carga, archivo corrupto e inexistente) | **0 diferencias** |
| Sesión simulada del menú interactivo (iniciativa de la IA: `main.py` no tiene tests) — las 8 opciones + una inválida, reintento por número mal escrito, venta VIP, stock insuficiente, cotización, reportes y guardado | Salida de consola (154 líneas) y JSON guardado **idénticos** |

**Tropiezo.** El primer guion de entradas para simular el menú quedó
desalineado (faltaban las respuestas a "código de cliente") y no recorría
todas las opciones, aunque la comparación salía "idéntica". La IA lo notó al
revisar qué mensajes aparecían y corrigió el guion. Lección: un "0
diferencias" solo vale si se verifica que la prueba realmente ejecutó los
casos que se querían cubrir.

**Qué aprendí.** Renombrar parece el cambio más inocente y fue el que
más archivos tocó (4) y el que tuvo un efecto colateral medible (líneas
largas). También quedó claro que hay nombres que **no** son míos para
cambiar: los que forman parte de un contrato (tests, claves del JSON). El
prompt tuvo que separar explícitamente "nombres internos" de "formato de
datos".

---

### Refactorización 6 · Manejo de errores con `with` y excepciones específicas

**Cómo se diseñó el prompt.** Pedí a la IA armarlo
(`¿Te armo el prompt de la refactorización 6? si`). En el prototipo la IA
**comprobó con datos una trampa** antes de escribir el prompt: cambiar
`except Exception` por solo `except json.JSONDecodeError` hace que un archivo con
bytes no UTF-8 truene en lugar de reportarse como corrupto (1 diferencia contra
el original). Técnicas nuevas: (a) **pedir que la IA enumere las excepciones
posibles antes de elegirlas** (razonar primero, codificar después);
(b) **validar con entradas hostiles** (archivos rotos, vacíos, con BOM, un
directorio…); (c) aplicar explícitamente la **regla 5 de `CLAUDE.md`**: los
errores de comportamiento existentes se reportan y se preguntan, no se corrigen
por iniciativa propia. Lo envié sin cambios.

**Prompt usado (tal cual):**

```text
Refactorización 6 — Mejorar el manejo de errores en la persistencia.

Contexto: sigue las reglas de CLAUDE.md. Rama `refactorizacion`.
Estado actual: 20 tests pasando y 4 errores de ruff.

Problema: en almacen.py los archivos se abren sin `with` (si algo falla
entre `open` y `close`, el archivo queda abierto) y `cargar_datos` usa
`except Exception`, que atrapa cualquier error, incluso bugs del propio
código, y los reporta como "archivo corrupto".

Objetivo: que los archivos siempre se cierren y que solo se atrapen los
errores que de verdad significan "archivo corrupto", SIN cambiar el
comportamiento.

Alcance (solo esto, en almacen.py):
1. `guardar_datos`: usa `with open(...) as archivo`.
2. `cargar_datos`: usa `with open(...)` dentro del `try`, quita el modo
   "r" redundante (regla UP015) y reemplaza `except Exception` por las
   excepciones específicas que puede lanzar la lectura de un JSON.

Restricciones:
- Antes de elegir las excepciones, enumera qué puede lanzar
  `json.load` sobre un archivo de texto con encoding utf-8. Ojo:
  `json.JSONDecodeError` NO cubre un archivo con bytes que no son
  UTF-8 válido (eso lanza `UnicodeDecodeError`). Un archivo así hoy
  regresa False con "archivo corrupto" y debe seguir igual.
- Conserva la verificación de "el archivo no existe" y sus mensajes.
- NO corrijas otros problemas que encuentres: si detectas un error de
  comportamiento existente, repórtalo en la bitácora como hallazgo y
  pregúntame antes de cambiarlo (regla 5 de CLAUDE.md).
- No toques gestor.py, reportes.py ni main.py.
- No modifiques tests/ ni pyproject.toml.

Validación:
- Ejecuta los tests y `ruff check src`.
- Resultado esperado: 20 tests pasando y 1 error de ruff
  (desaparecen 2 SIM115 y UP015; queda solo el C901 de `menu`).
- Busca `except Exception` en src/: no debe quedar ninguno.
- Compara antes/después cargando estos archivos: JSON válido, sin
  "contador", JSON roto, vacío, solo espacios, bytes UTF-8 inválidos,
  con BOM, una lista `[]`, un objeto sin "inventario", un archivo
  inexistente y un directorio. Revisa el valor de retorno, la excepción
  (si la hay), `ultimo_error`, el inventario y el contador. Compara
  también el JSON que escribe `guardar_datos` con acentos y ñ.
  Debe dar 0 diferencias.

Al terminar:
1. Muéstrame el diff.
2. Registra la entrada #6 en docs/bitacora.md: este prompt tal cual,
   el cambio realizado, la justificación, el resultado de tests y ruff,
   y los hallazgos.
3. Haz un commit `refactor: manejo de errores con with y excepciones específicas`
   y súbelo a GitHub.
```

**La enumeración pedida encontró dos casos que ni el prompt ni el prototipo
anticipaban.** Al ejecutar `json.load` sobre distintas entradas:

| Entrada | Excepción | ¿La cubre `JSONDecodeError`? |
|---|---|---|
| JSON mal formado | `JSONDecodeError` (subclase de `ValueError`) | Sí |
| Bytes que no son UTF-8 | `UnicodeDecodeError` (subclase de `ValueError`) | No — *anticipado en el prompt* |
| Entero con miles de dígitos | `ValueError` (límite de dígitos de Python 3.11+) | **No — nuevo** |
| Anidamiento extremo `[[[[…]]]]` | `RecursionError` | **No — nuevo** |

Con la versión del prototipo (`JSONDecodeError, UnicodeDecodeError`), el JSON
anidado **tronaba** con `RecursionError` en lugar de regresar "archivo
corrupto" como el original. Se corrigió a `except (ValueError, RecursionError)`
con un comentario que explica qué cubre cada una.

**Cambio realizado** (`src/almacen.py`):

| Función | Antes | Después |
|---|---|---|
| `guardar_datos` | `open` … `close()` manual | `with open(...) as archivo:` |
| `cargar_datos` | `open(ruta, "r", …)` fuera del `try`, `except Exception`, dos `close()` | `with open(ruta, …)` dentro del `try`, `except (ValueError, RecursionError)` con comentario |

**Justificación.**
- `with` garantiza que el archivo se cierre aunque ocurra una excepción; antes,
  un error dentro de `json.dump` dejaba el archivo abierto (y en Windows,
  bloqueado).
- `except Exception` escondía **cualquier** error —incluido un bug del
  propio programa— bajo el mensaje "archivo corrupto", lo que hace muy
  difícil diagnosticar. Ahora solo se atrapan los errores que realmente
  significan "el contenido no es un JSON válido".
- Se eliminó código repetido (`close()` en dos ramas).

**Resultado.**

| | Antes | Después |
|---|---|---|
| Tests | 20 passed | **20 passed** |
| `ruff check src` | 4 errores | **1 error** (−2 SIM115, −UP015; solo queda C901 de `menu`) |
| `except Exception` en `src/` | 1 | **0** |
| Persistencia: 15 escenarios (válido, sin contador, JSON roto, vacío, espacios, UTF-8 inválido, BOM, `[]`, sin "inventario", anidamiento extremo, entero enorme, inexistente, directorio, guardado con acentos y ñ) | — | **0 diferencias** |
| Ventas (926), errores (53), reportes/JSON (23) | — | **0 diferencias** |

**Hallazgos (reportados, no corregidos — regla 5 de `CLAUDE.md`).**

1. **Pérdida de datos en memoria con un JSON válido pero mal estructurado.**
   Si el archivo es un JSON válido sin la clave `"inventario"` (o es una lista
   `[]`), `cargar_datos` **primero vacía el inventario y después truena**
   (`KeyError` / `TypeError`). El inventario que había en memoria se pierde. Es
   un bug del código original que se conserva idéntico.
   ✅ **Resuelto** en la *Corrección 1* (siguiente sección), por decisión mía
   después de que la IA lo reportara.
2. **Diferencia deliberada (no observable en la práctica).** El `open` ahora
   está dentro del `try`, pero los errores del sistema operativo (`OSError`:
   permisos, directorio) siguen sin atraparse, igual que antes. La única
   diferencia teórica: un error de E/S *durante* la lectura (disco que falla a
   media lectura) antes se reportaba como "archivo corrupto" y ahora se
   propaga. Es justo el objetivo del cambio: no disfrazar fallas del sistema
   como "archivo corrupto".

**Qué aprendí.** La mejor instrucción del prompt fue "enumera antes de
elegir": encontró dos casos que ni yo ni la IA habíamos previsto al
diseñarlo. Un prompt detallado no garantiza que esté completo; pedirle a la IA
que **investigue** antes de actuar cubre lo que el prompt no anticipó. También
se vio el valor de la regla 5 de `CLAUDE.md`: la IA encontró un bug real y lo
reportó en lugar de "arreglarlo" silenciosamente dentro de una refactorización.

---

### Corrección 1 · Bug de pérdida de datos al cargar un JSON mal estructurado *(cambio de comportamiento intencional)*

> Esta entrada **no es una refactorización**: cambia el comportamiento a
> propósito para corregir un bug. Se hizo en un commit separado (`fix:`) para
> que no se mezcle con las refactorizaciones, que por definición no deben
> cambiar el comportamiento.

**Origen.** La IA lo encontró al probar entradas hostiles en la
refactorización 6 y, siguiendo la regla 5 de `CLAUDE.md`, lo reportó y
preguntó en vez de corregirlo. Me ofreció dos opciones (corregirlo aparte o
dejarlo documentado).

**Prompt usado (tal cual):**

```text
corrigelo y documentalo
```

Un prompt muy corto funcionó porque el contexto ya estaba completo: el
hallazgo estaba descrito en la bitácora con causa, síntoma y propuesta de
solución, y `CLAUDE.md` ya decía dónde van las pruebas nuevas.

**El bug.** `cargar_datos` vaciaba el estado **antes** de comprobar que el
JSON tuviera la forma correcta:

| Archivo (JSON válido) | Antes | Después |
|---|---|---|
| `{"ventas": []}` (sin "inventario") | Vacía el inventario y truena con `KeyError` → **datos perdidos** | `False`, "formato de datos invalido", estado intacto |
| `{"inventario": {...}}` (sin "ventas") | Reemplaza el inventario, truena con `KeyError` → **estado a medias** (inventario nuevo + ventas viejas) | `False`, estado intacto |
| `[]` | Truena con `TypeError` (estado intacto por casualidad) | `False`, estado intacto |
| `{"inventario": [], "ventas": []}` | Lo acepta como inventario vacío y **borra** lo que había | `False` (guardar_datos nunca escribe una lista) |

**Cambio realizado.**
- `src/almacen.py`: nueva función `_estructura_valida(datos)` que comprueba
  `{"inventario": dict, "ventas": list}`; `cargar_datos` la llama **antes** de
  tocar el estado y, si falla, regresa `False` con `ultimo_error =
  "formato de datos invalido"`. Docstring actualizado.
- `tests/test_casos_limite.py` (**archivo nuevo**; las pruebas originales no se
  tocaron): 5 pruebas: 3 del bug (sin "inventario", sin "ventas", lista), 1 de
  que un JSON roto se sigue reportando como "archivo corrupto" y 1 de que
  "contador" sigue siendo opcional.
- `CLAUDE.md` (**primera iteración del archivo**): se agregó la regla de
  negocio "`cargar_datos` no modifica el estado si…" y se aclaró que las
  pruebas nuevas van en `tests/test_casos_limite.py` y que cada bug corregido
  lleva una prueba que falle con el código anterior.

**Verificación.**

| Comprobación | Resultado |
|---|---|
| Suite completa | **25 passed** (20 originales + 5 nuevas) |
| Pruebas nuevas contra el código **anterior** | **3 fallan** (las del bug) → la prueba sí detecta el bug |
| `ruff check src` | **1 error** (sin cambio; C901 de `menu`) |
| Persistencia (17 escenarios) | **4 diferencias, todas intencionales** (las 4 filas de la tabla); los otros 13 idénticos |
| Ventas (926), errores (53), reportes/JSON (23) | **0 diferencias** |

**Qué aprendí.** Separar "refactorizar" de "corregir" no es burocracia: si
este arreglo hubiera ido dentro de la refactorización 6, el commit diría
"sin cambio de comportamiento" y sería falso. También vi que una regla en
`CLAUDE.md` ("reporta y pregunta") convirtió a la IA de un asistente que
"arregla lo que ve" en uno que me deja decidir, y que una prueba de regresión
solo vale si se demuestra que falla con el código viejo.

---

### Refactorización 7 · Dividir `menu()` con un diccionario de despacho

**Cómo se diseñó el prompt.** Pedí a la IA armarlo (`¿Te armo el prompt? si`,
en el mismo mensaje en que pedí corregir el bug). En el prototipo la IA había
nombrado las funciones `registrar_venta` y `cotizar` dentro de `main.py`:
funcionaba, pero se confundían con las de `gestor`. El prompt fija el prefijo
`menu_` y explica por qué. Técnicas: (a) **convertir un tropiezo anterior en
regla**: "antes de comparar, confirma que la sesión pasó por todas las
opciones" sale directo del error de la refactorización 5; (b) describir la
**forma final** de `menu()` paso a paso; (c) dejar explícito el caso especial
(la opción 8 es la única que termina el ciclo). Lo envié sin cambios.

**Prompt usado (tal cual):**

```text
Refactorización 7 — Dividir `menu()` en una función por opción con un
diccionario de despacho.

Contexto: sigue las reglas de CLAUDE.md. Rama `refactorizacion`.
Estado actual: 25 tests pasando (20 originales + 5 de casos límite)
y 1 error de ruff (C901: `menu` tiene complejidad 17).

Problema: `menu()` es una cadena de 8 `if/elif` que mezcla el ciclo del
menú con la lógica de cada opción. Para agregar una opción hay que
meterse en medio de una función de 60 líneas.

Objetivo: que `menu()` solo muestre el menú, lea la opción y la despache,
y que cada opción viva en su propia función, SIN cambiar lo que ve el
usuario.

Alcance (solo esto, en main.py):
1. Una función por opción con prefijo `menu_` para que no se confundan
   con las de gestor: `menu_agregar_producto`, `menu_registrar_venta`,
   `menu_cotizar`, `menu_mas_vendidos`, `menu_alertas_stock`.
   Las opciones 4 y 5 llaman directo a `reportes.reporte_inventario` y
   `reportes.resumen_ventas` (no necesitan función propia).
2. Un diccionario `ACCIONES = {"1": menu_agregar_producto, ...}` y una
   constante `OPCION_SALIR = "8"`. La opción 8 (guardar y salir) se
   maneja aparte porque es la única que termina el ciclo.
3. El texto del menú en una constante `TEXTO_MENU`.
4. `menu()` queda como: bienvenida y carga de datos → ciclo que imprime
   el menú, lee la opción, sale con la 8, ejecuta la acción o imprime
   "Opcion no valida.".

Restricciones:
- La salida en consola debe ser idéntica carácter por carácter,
  incluida la línea en blanco antes de cada menú y el orden de los
  mensajes.
- No cambies textos, prompts de `input()` ni mensajes de error.
- No toques gestor.py, almacen.py ni reportes.py.
- No modifiques tests/ ni pyproject.toml.

Validación:
- Ejecuta los tests y `ruff check src`.
- Resultado esperado: 25 tests pasando y 0 errores de ruff
  ("All checks passed!").
- `main.py` no tiene tests: repite la sesión simulada del menú de la
  refactorización 5 (las 8 opciones + una inválida, reintento por
  número mal escrito, venta VIP, stock insuficiente, cotización,
  reportes y guardado) con la versión anterior y la nueva, en una
  copia temporal, y compara la salida de consola y el JSON guardado.
  Antes de comparar, confirma que la sesión pasó por todas las opciones.
  Debe ser idéntica.

Al terminar:
1. Muéstrame el diff.
2. Registra la entrada #7 en docs/bitacora.md: este prompt tal cual,
   el cambio realizado, la justificación y el resultado de tests y ruff.
3. Haz un commit `refactor: divide menu() en funciones por opción con despacho por diccionario`
   y súbelo a GitHub.
```

**Cambio realizado** (`src/main.py`, +84 / −54 líneas):

| Elemento | Qué es |
|---|---|
| `TEXTO_MENU` | Constante con el texto del menú (empieza con `\n` para conservar la línea en blanco) |
| `menu_agregar_producto`, `menu_registrar_venta`, `menu_cotizar`, `menu_mas_vendidos`, `menu_alertas_stock` | Una función por opción, con docstring |
| `ACCIONES` | Diccionario `opción → función`; las opciones 4 y 5 apuntan directo a `reportes` |
| `OPCION_SALIR = "8"` | Caso especial: guarda y rompe el ciclo |
| `menu()` | Bienvenida y carga → ciclo: imprime, lee, sale con 8, despacha o "Opcion no valida." (de ~60 a 17 líneas) |

`menu_alertas_stock` usa un `return` temprano cuando no hay productos con
stock bajo (en lugar de `if/else`), siguiendo el estilo de la refactorización 4.

**Justificación.**
- **Separación de responsabilidades**: `menu()` ahora solo controla el ciclo;
  la lógica de cada opción vive aparte y se puede leer (y probar) sola.
- **Abierto a extensión**: agregar una opción es escribir una función y una
  línea en `ACCIONES`; antes había que insertar un `elif` en medio de una
  función de 60 líneas.
- **Complejidad**: `menu()` pasó de 17 a menos de 10; era la última
  violación de C901 del proyecto.

**Verificación.**

| Comprobación | Resultado |
|---|---|
| Tests | **25 passed** |
| `ruff check src` | 1 → **0 errores — "All checks passed!"** ✅ |
| Cobertura de la sesión simulada (confirmada **antes** de comparar) | Producto agregado, reintento por número inválido, 2 tickets (uno con descuento VIP), stock insuficiente, cotización, producto inexistente, reporte de inventario, resumen de ventas, más vendidos, 3 alertas de stock, opción inválida y guardado: **todas presentes** |
| Salida de consola, versión anterior vs. nueva | **Idéntica** (154 líneas) |
| JSON guardado por la opción 8 | **Idéntico** |

**Qué aprendí.** Los nombres importan también *entre* módulos: dos
funciones `registrar_venta` (una en `gestor`, otra en `main`) son legales en
Python pero confunden a quien lee. Y una lección de la refactorización 5
("verifica que la prueba ejecutó lo que querías") ya no fue un tropiezo,
sino un paso del prompt: así se acumula el aprendizaje en el proceso.

---

### Refactorización 8 · Type hints validados con `mypy --strict`

**Cómo se diseñó el prompt.** Pedí a la IA armarlo (`si`). Antes de
diseñarlo, la IA **revisó qué herramientas había disponibles** y encontró
`mypy`, lo que cambió el enfoque: los type hints no solo se escriben, se
**verifican**. Midió la línea base (58 errores en modo estricto) para tener un
resultado esperado objetivo. Técnicas nuevas: (a) **una herramienta externa
como criterio de aceptación** (`mypy --strict` sin errores) sin convertirla en
dependencia del proyecto; (b) **pedir que se justifique una decisión de diseño
descartada** (TypedDict); (c) una **restricción nacida de un error propio del
prototipo** (ver *Tropiezo*). Lo envié sin cambios.

**Prompt usado (tal cual):**

```text
Refactorización 8 — Agregar type hints a todas las funciones y validarlos
con mypy en modo estricto.

Contexto: sigue las reglas de CLAUDE.md. Rama `refactorizacion`.
Estado actual: 25 tests pasando, 0 errores de ruff y 58 errores de
`mypy --strict src` (ninguna función tiene anotaciones).

Problema: sin type hints, para saber qué recibe y qué regresa una
función hay que leer su cuerpo (¿`cotizar` regresa un número o un texto?,
¿`cliente` puede ser None?), y ninguna herramienta puede detectar errores
de tipos.

Objetivo: anotar parámetros, valores de retorno, globales y
contenedores vacíos en los 4 módulos, SIN cambiar el comportamiento.

Alcance:
1. gestor.py: define los alias `Producto = dict[str, Any]` y
   `Venta = dict[str, Any]` y úsalos en las firmas. Anota los globales
   (`INVENTARIO: dict[str, Producto]`, `VENTAS: list[Venta]`,
   `contador_ventas: int`, `ultimo_error: str`).
   Parámetros que pueden llegar como None (`codigo`, `cantidad`,
   `cliente` en la venta y la validación) van como `X | None`.
2. almacen.py, reportes.py y main.py: anota todas las funciones.
   `mas_vendidos` regresa `list[tuple[str, int]]`; las funciones del
   menú regresan `None`; `ACCIONES` es `dict[str, Callable[[], object]]`
   (las opciones 4 y 5 regresan texto que se ignora).
3. Anota los contenedores vacíos (`= {}`, `= []`) y los acumuladores que
   empiezan en 0 pero suman floats.

Restricciones:
- Usa sintaxis de Python 3.10: `str | None`, `list[...]`, `dict[...]`
  (sin `Optional` ni `List`) y `Callable` de `collections.abc`.
- NO uses TypedDict: los diccionarios de producto y venta se arman clave
  por clave y su orden de claves define el JSON; cambiar eso es otra
  refactorización. Explica esta decisión en la bitácora.
- Si mypy marca un valor `Any` (lo que se lee de un Producto/Venta),
  resuélvelo anotando la variable, NO con conversiones como `str(...)` o
  `float(...)`: una conversión cambia el comportamiento con datos
  inesperados en el JSON.
- mypy se usa solo como verificación: NO lo agregues a requirements.txt
  ni a pyproject.toml.
- No modifiques tests/ ni pyproject.toml.

Validación:
- Ejecuta los tests, `ruff check src` y `mypy --strict src`.
- Resultado esperado: 25 tests pasando, 0 errores de ruff y
  "Success: no issues found" en mypy (de 58 a 0).
- Repite las comparaciones antes/después (ventas, errores, reportes/JSON,
  persistencia) y la sesión simulada del menú: 0 diferencias.

Al terminar:
1. Muéstrame el diff.
2. Registra la entrada #8 en docs/bitacora.md: este prompt tal cual,
   el cambio realizado, la justificación, los errores que encontró mypy
   y cómo se resolvieron, y el resultado de tests, ruff y mypy.
3. Haz un commit `refactor: type hints en todas las funciones (mypy --strict sin errores)`
   y súbelo a GitHub.
```

**Cambio realizado** (4 archivos, +58 / −45 líneas):

| Módulo | Anotaciones |
|---|---|
| `gestor.py` | Alias `Producto` y `Venta` (`dict[str, Any]`); globales `INVENTARIO`, `VENTAS`, `contador_ventas`, `ultimo_error`; las 11 funciones, con `str \| None` / `int \| None` donde llegan valores nulos; contenedores `producto`, `resultados`, `venta`, `ticket` y `subtotal` en `cotizar` |
| `almacen.py` | 4 funciones (`ruta: str`, `-> bool`); `datos: dict[str, object]`; `_estructura_valida(datos: object)` |
| `reportes.py` | 6 funciones; `mas_vendidos -> list[tuple[str, int]]`; acumuladores `float` y contenedores tipados |
| `main.py` | 7 funciones (`-> None` / `-> float`); `ACCIONES: dict[str, Callable[[], object]]` con `Callable` de `collections.abc` |
| `.gitignore` | `.mypy_cache/` |

**Errores que encontró mypy después de anotar** (que la lectura del código no
había detectado) **y cómo se resolvieron:**

| # | Error de mypy | Causa | Solución |
|---|---|---|---|
| 1 | `Incompatible types in assignment (float → str)` en `agregarProducto` | `producto = {}` sin anotar: mypy deduce `dict[str, str]` por la **primera** asignación (`codigo`) y luego rechaza `precio` | `producto: Producto = {}` |
| 2 | `Returning Any from function declared to return "str"` en `_armar_ticket` | `venta["nombre"]` es `Any`; al sumarlo al ticket, mypy pierde la garantía de que el resultado sea `str` | `ticket: str = ""` |
| 3 | `Returning Any … "float \| None"` en `cotizar` | `INVENTARIO[codigo]["precio"]` es `Any`, y todo el cálculo hereda `Any` | `subtotal: float = …` |

**Tropiezo (y por qué existe la restricción de "no conversiones").** En el
prototipo, la primera corrección del error 2 fue `str(venta["nombre"])`: mypy
pasaba y las pruebas también. Pero si un JSON cargado trajera un nombre
numérico, el original truena (`str + int`) y la versión con `str(...)` no:
**un cambio de comportamiento escondido** detrás de un "arreglo de tipos". Se
reemplazó por la anotación `ticket: str = ""`, que no toca la lógica, y se
agregó al prompt la restricción explícita.

**Decisión de diseño: por qué no `TypedDict`.** Un `TypedDict` para
`Producto` y `Venta` daría tipos por clave (mypy detectaría `venta["totl"]`).
Se descartó en esta refactorización porque: (1) los diccionarios se arman
clave por clave (`venta = {}` y luego `venta["folio"] = …`), lo que un
`TypedDict` no permite sin reestructurar la construcción; (2) el **orden de
inserción de las claves define el JSON** que se guarda, y reestructurar la
construcción arriesga cambiarlo; (3) los datos cargados del JSON llegan sin
tipo de todas formas. Queda como mejora posible, en su propio cambio.

**Justificación.**
- Las firmas ahora documentan el contrato: `cotizar(codigo: str,
  cantidad: int | None) -> float | None` dice, sin leer el cuerpo, que puede
  regresar `None` y que hay que revisarlo.
- `mypy --strict` pasó de 58 errores a 0 y puede ejecutarse en cualquier
  cambio futuro para detectar errores de tipos antes de correr el programa.
- El editor ahora autocompleta y advierte con base en los tipos.

**Resultado.**

| | Antes | Después |
|---|---|---|
| Tests | 25 passed | **25 passed** |
| `ruff check src` | 0 | **0** |
| `mypy --strict src` | 58 errores | **0 — "Success: no issues found in 4 source files"** |
| Ventas (926), errores (53), reportes/JSON (23), persistencia (17) | — | **0 diferencias** |
| Sesión simulada del menú | — | consola (154 líneas) y JSON **idénticos** |

**Qué aprendí.** Escribir type hints sin verificarlos es documentación que
puede mentir; con mypy se convierten en una prueba. Y el error más
instructivo no fue de mypy sino mío: "arreglar" un tipo con una conversión
parecía inocente y cambiaba el comportamiento. Pasar las pruebas no es
lo mismo que no cambiar nada: hay que preguntarse qué pasa con datos que las
pruebas no cubren.

---

### Pruebas · Casos límite de descuentos, VIP, validaciones y reportes

**Cómo se diseñó el prompt.** Pedí a la IA armarlo
(`¿Te armo el prompt de los tests de casos límite? si`). En el prototipo la IA
(a) **calculó a mano** los valores de frontera (p. ej. 499.99 × 1.16 = 579.9884
→ 579.99) y los comparó con lo que regresa el código antes de ponerlos en el
prompt; (b) corrió las pruebas nuevas **contra el código original** y descubrió
que una de ellas leía una variable interna renombrada (`contador_ventas`), así
que la reescribió como prueba de caja negra (la siguiente venta debe tener
folio 1); (c) armó una **prueba de mutación** para medir si las pruebas sirven,
no solo si pasan. Técnicas: **valores esperados verificados en el prompt**
(evita que la IA "consagre" en un test lo que el código regresa, aunque sea un
bug), **restricción de caja negra** y **validación contra el código original**.
Lo envié sin cambios.

**Prompt usado (tal cual):**

```text
Tests de casos límite — Ampliar tests/test_casos_limite.py para cubrir
las fronteras y reglas que la suite original no prueba.

Contexto: sigue las reglas de CLAUDE.md. Rama `refactorizacion`.
Estado actual: 25 tests pasando (20 originales + 5 de la corrección del
bug de carga), 0 errores de ruff, mypy --strict sin errores.

Problema: la suite original prueba casos "del medio" (600, 2000), pero no
las fronteras donde cambian las reglas (500, 1000, el VIP en 200, stock
exacto, stock mínimo en 5) ni qué mensaje de error queda en cada caso.
Un error de `>=` vs `>` en cualquiera de ellas pasaría sin ser detectado.

Objetivo: agregar pruebas de caja negra de esas fronteras al archivo
tests/test_casos_limite.py, sin tocar los tests originales.

Alcance (usa @pytest.mark.parametrize cuando sean variantes del mismo caso):
1. Descuento por volumen con precio × 1: 499.99 → sin descuento, total
   579.99 · 500 → descuento 25.0, total 551.0 · 999.99 → 50.0, 1101.99 ·
   1000 → 100.0, 1044.0. Y que `cotizar` respete la misma frontera.
2. VIP: compra de exactamente 200 → total 232.0 (no aplica) · 200.01 →
   227.37 (sí aplica). Clientes que NO son VIP: "vip001", "XVIP01", "VI",
   "", None. `cotizar` no aplica VIP (661.2 vs 647.28 con "VIP007").
3. Stock y folios: vender exactamente todo el stock sí se puede (y la
   siguiente falla con "stock insuficiente"); una venta fallida no
   consume folio; `cotizar` no valida stock.
4. Mensajes de `ultimo_error`, incluyendo el ORDEN de las validaciones
   (código vacío antes que cantidad, producto inexistente antes que
   cantidad) en `registrar_venta`, y los 4 mensajes de `agregarProducto`.
   Alta con stock 0 es válida. `actualizar_stock` de un inexistente.
5. Ticket completo carácter por carácter sin descuento, y la línea
   "Descuento: -$30.0" cuando sí hay.
6. Reportes: stock igual a 5 NO es stock bajo (4 sí); `mas_vendidos`
   conserva el orden de inserción en empates, funciona sin ventas y con
   n mayor que los productos; texto exacto de `resumen_ventas`.
7. Persistencia: guardar y cargar conserva "Café de Ñuñoa" sin escapes
   \u en el archivo.

Restricciones:
- Pruebas de CAJA NEGRA: solo API pública (las mismas funciones y
  globales que usan los tests originales). Nada de constantes o
  variables internas renombradas en las refactorizaciones: los tests
  deben poder correr también contra el código original.
- Calcula a mano los valores esperados y verifica al menos los de
  frontera; no copies lo que regresa el código sin comprobarlo.
- No modifiques test_gestor.py, test_almacen.py, test_reportes.py,
  conftest.py ni pyproject.toml. No toques src/.

Validación:
1. Suite completa: todos pasan, 0 errores de ruff.
2. Contra el código ORIGINAL (commit a9931ac, sin refactorizar):
   las pruebas nuevas deben pasar todas, salvo las 3 del bug corregido.
   Eso demuestra que las refactorizaciones conservaron el comportamiento.
3. Prueba de mutación manual: introduce uno por uno estos 10 errores en
   una copia de src/ y reporta cuántos detecta la suite original y
   cuántos la suite completa: umbral medio `>=`→`>`, umbral alto
   `>=`→`>`, VIP `<=`→`<`, VIP sin distinguir mayúsculas, stock
   `<`→`<=`, validar cantidad antes que existencia, alta con stock 0
   rechazada, ticket con `>= 0`, stock bajo con `<=`, empates del
   ranking con `<=`.

Al terminar:
1. Muéstrame cuántas pruebas nuevas hay y la tabla de mutación.
2. Registra la entrada en docs/bitacora.md: este prompt tal cual, las
   pruebas agregadas, los resultados contra el código original y la
   tabla de mutación.
3. Haz un commit `test: casos límite de descuentos, VIP, validaciones y reportes`
   y súbelo a GitHub.
```

**Pruebas agregadas** (`tests/test_casos_limite.py`; 19 funciones nuevas =
**37 casos** con `parametrize`; las pruebas originales no se tocaron):

| Grupo | Casos | Qué protege |
|---|---|---|
| Fronteras de descuento por volumen | 5 | 499.99 / 500 / 999.99 / 1000 en venta, y 500 en `cotizar` |
| Regla VIP | 8 | Compra de 200 exactos vs. 200.01; 5 códigos que **no** son VIP (minúsculas, prefijo en medio, corto, vacío, None); `cotizar` sin VIP |
| Stock y folios | 3 | Vender todo el stock y ni una más; venta fallida no consume folio; `cotizar` no valida stock |
| Mensajes y orden de validaciones | 14 | 8 combinaciones de `registrar_venta` (incluye código vacío **y** cantidad 0 → gana "codigo vacio"), 4 mensajes de `agregarProducto`, alta con stock 0, `actualizar_stock` inexistente |
| Ticket | 2 | Texto completo carácter por carácter; línea de descuento solo cuando aplica |
| Reportes | 4 | Stock 5 no es bajo (4 sí); empates en `mas_vendidos` conservan el orden; sin ventas y `n` mayor; texto exacto de `resumen_ventas` |
| Persistencia | 1 | "Café de Ñuñoa" se guarda sin escapes `\u` y se recupera igual |

**Resultado 1 — Suite completa.** **62 passed** (20 originales + 5 de la
corrección + 37 nuevos). `ruff check src`: 0 errores. El archivo de pruebas
también pasa ruff (aunque `tests/` está excluido del linter del proyecto).
`src/` sin cambios.

**Resultado 2 — Contra el código ORIGINAL (`a9931ac`, sin refactorizar).**
De las 42 pruebas del archivo, **39 pasan y 3 fallan**, exactamente las 3 del
bug corregido (lista, sin "inventario", sin "ventas"). Las 37 pruebas nuevas
pasan **todas** con el código original: es evidencia independiente de que las
8 refactorizaciones conservaron el comportamiento en todas esas fronteras.

**Resultado 3 — Prueba de mutación manual.** Se introdujo un error a la vez en
una copia de `src/` y se corrieron ambas suites:

| Mutante (error introducido) | Suite original (20) | Suite completa (62) |
|---|---|---|
| Umbral medio: `>= 500` → `> 500` | pasa sin verlo | **detectado** |
| Umbral alto: `>= 1000` → `> 1000` | pasa sin verlo | **detectado** |
| VIP: una compra de 200 exactos recibe descuento (`<=` → `<`) | pasa sin verlo | **detectado** |
| VIP: no distingue mayúsculas (`"vip001"` sería VIP) | pasa sin verlo | **detectado** |
| Stock: no deja vender la última unidad (`<` → `<=`) | pasa sin verlo | **detectado** |
| Valida la cantidad antes que la existencia del producto | pasa sin verlo | **detectado** |
| Alta con stock 0 rechazada (`< 0` → `<= 0`) | pasa sin verlo | **detectado** |
| Ticket siempre muestra la línea de descuento (`> 0` → `>= 0`) | pasa sin verlo | **detectado** |
| Stock bajo con 5 unidades (`<` → `<=`) | pasa sin verlo | **detectado** |
| Empates de `mas_vendidos` en otro orden (`<` → `<=`) | pasa sin verlo | **detectado** |
| **Total** | **0 / 10** | **10 / 10** |

**Tropiezo.** El script de mutación falló al primer intento: el bloque de
validación "producto no existe / cantidad inválida" aparece **dos veces**
(en `_validar_venta` y en `cotizar`) y el reemplazo exigía una sola
coincidencia. Se ajustó para mutar solo la primera. Curiosamente, revela
duplicación que todavía queda entre las validaciones de `cotizar` y
`_validar_venta` (con una diferencia real: `cotizar` no valida código vacío ni
stock), candidata a una refactorización futura.

**Qué aprendí.** "Los tests pasan" no dice qué tan buenos son: la suite
original pasaba con los 10 errores. La prueba de mutación convierte esa
pregunta en un número. Correr las pruebas nuevas contra el código original
fue la mejor evidencia de que refactoricé sin cambiar el comportamiento, y
obligó a que fueran de verdad de caja negra.

---

### Reflexión final · Escrita a partir de mis respuestas

**Cómo se hizo.** La IA me ofreció dos caminos: que ella generara la
reflexión y yo la ajustara, o hacerme preguntas primero para escribirla con mis
respuestas. Respondí `si` (ambiguo); la IA lo interpretó como la segunda
opción, lo dijo explícitamente y me hizo 5 preguntas. Mis respuestas,
**tal cual**:

```text
1. Esperaba que la refactorizacion fuera facil y entendible para mis conocimientos
   sin embargo la IA es poderosa para esta tarea.
2. lo que mas me sirvio fue la comparaciones del antes y el despues, el como la IA
   genero los cambios y me explico las razones de estos.
3. un tema que tengo problemas es en crear los promps a detalle de un tema que no
   me queda claro, debo de admitir que le pedi ayuda a los prompts para poder crearlos.
4. Senti que mi participacion era en revisar los prompts que me proponia la ia y en
   tomar decisiones de acuerdo a las sugerencias que me daba la IA. Me llevo el
   aprender a detallar los promps pero sobre todo tener el mayor conocimiento de lo
   que trata la tarea o desarrollo y asi poder tomar decisiones de como debe actuar
   la IA.
```

La IA redactó [`docs/reflexion.md`](reflexion.md) en primera persona,
conservando mis ideas y completándolas con los datos de esta bitácora (cifras,
hallazgos y tropiezos).

---

### README · Instalación, comandos y resumen del reto

**Cómo se diseñó el prompt.** Pedí a la IA armarlo. Como es documentación,
el riesgo no es romper el comportamiento sino escribir comandos o cifras que no
coincidan con la realidad, así que la restricción clave fue **"verifica cada
comando y cada ruta antes de escribirlos"**. Lo envié sin cambios.

**Prompt usado (tal cual):**

```text
README — Actualizar README.md para la entrega del reto.

Contexto: sigue las reglas de CLAUDE.md. Rama `refactorizacion`.
El README actual es el enunciado original del reto; el formato de
entrega pide que el PR incluya un README con instrucciones del proyecto.

Objetivo: que alguien que clone el repositorio pueda instalarlo,
probarlo y entender qué se hizo, sin leer la bitácora completa.

Contenido (en este orden):
1. Título y descripción breve de la aplicación (qué hace la tienda
   "La Esquina") y una línea de qué es este repositorio (reto de
   refactorización asistida por IA).
2. Estado del código: tabla antes/después (ruff 20→0, mypy --strict
   58→0, pruebas 20→62, prueba de mutación 0/10→10/10).
3. Requisitos previos: Python 3.10+, git; dependencias de requirements.txt.
4. Instalación paso a paso: clonar
   https://github.com/albertomtzu23/M1.-Reto.git, cambiar a la rama
   `refactorizacion`, crear y activar entorno virtual (comandos para
   Windows y para Linux/macOS), instalar dependencias.
5. Comandos: ejecutar pruebas (`pytest`), linter (`ruff check src`),
   verificación de tipos opcional (`mypy --strict src`, aclarando que
   mypy no está en requirements.txt y se instala aparte) y la app
   (`cd src && python main.py`, avisando que la opción 8 sobrescribe
   datos_ejemplo.json).
6. Estructura del proyecto actualizada (incluye CLAUDE.md, .claudeignore,
   docs/bitacora.md, docs/reflexion.md, tests/test_casos_limite.py).
7. Resumen numerado de las refactorizaciones (8 + la corrección del bug
   + las pruebas nuevas), una línea cada una, con enlace a la bitácora.
8. Sección breve "Sobre el reto" con las reglas originales que siguen
   vigentes (no modificar tests originales ni pyproject.toml).

Restricciones:
- Todos los números y comandos deben coincidir con la bitácora y con lo
  que realmente existe en el repositorio; verifica cada comando y cada
  ruta antes de escribirlos.
- No inventes funcionalidades ni resultados.
- No toques src/, tests/ ni pyproject.toml.
- BITACORA_TEMPLATE.md se queda (es material original del reto).

Al terminar:
1. Muéstrame el README.
2. Registra la entrada en docs/bitacora.md: este prompt tal cual y qué
   se cambió.
3. Haz un commit `docs: README con instalación, comandos y resumen del reto`
   y súbelo a GitHub.
```

**Hallazgo: el propio prompt traía un comando incorrecto, y la restricción de
verificar lo detectó.** El prompt pedía documentar `cd src && python main.py`
(el comando del README original). Al ejecutarlo, la IA comprobó que **no carga
los datos de ejemplo**: el programa busca `datos_ejemplo.json` en la carpeta
desde donde se ejecuta.

| Comando | ¿Carga los 6 productos de ejemplo? | ¿Qué escribe la opción 8? |
|---|---|---|
| `cd src && python main.py` | **No**, arranca vacío | Crea un archivo **nuevo** `src/datos_ejemplo.json` |
| `python src/main.py` (desde la raíz) | **Sí** | **Sobrescribe** `datos_ejemplo.json` de la raíz |

Se documentó `python src/main.py` con la advertencia y cómo restaurar
(`git checkout datos_ejemplo.json`). El código **no** se cambió (fuera de
alcance); queda como posible mejora resolver la ruta relativa al archivo
`main.py` en lugar del directorio actual.

**Cambio realizado.**
- `README.md` reescrito: descripción, tabla de estado (ruff 20→0, mypy
  58→0, pruebas 20→62, mutación 0/10→10/10), requisitos, instalación con
  activación del entorno para CMD, PowerShell y Linux/macOS, comandos,
  ejecución de la app con advertencias, estructura del proyecto, resumen de
  los 8 pasos más la corrección y las pruebas, y reglas del reto.
- `CLAUDE.md` (**segunda iteración**): tenía el mismo comando incorrecto
  de la app; se cambió a `python src/main.py`, indicando que la opción 8
  sobrescribe el archivo.

**Verificación.** Las 17 rutas citadas en el README existen; `pytest`
(62 passed), `ruff check src` (All checks passed!), `mypy --strict src`
(Success) y `python src/main.py` (muestra "Datos cargados de
datos_ejemplo.json") se ejecutaron con el resultado documentado.
Los comandos de activación del entorno en Windows no se pudieron ejecutar en
el entorno de la IA (Linux); son los estándar de `venv`.

**Qué aprendí.** Una instrucción de verificación en el prompt vale incluso
contra el propio prompt: el comando que yo pedí documentar estaba mal desde el
enunciado original del reto, y solo ejecutarlo lo reveló.

---

### Evidencia · Integración continua con GitHub Actions

**Cómo se llegó aquí.** La IA me pidió correr `pytest` y `ruff` en mi equipo
para la evidencia oficial. Al hacerlo, mi Windows respondió:

```text
C:\Users\Triple E>python -m venv .venv
no se encontró Python; ejecutar sin argumentos para instalar desde el Microsoft Store ...
```

(además, faltó el `cd` a la carpeta del repositorio). La IA explicó la causa y
me ofreció opciones; elegí **"GitHub Actions (Recomendado)"** en lugar de
instalar Python. La IA también intentó correr `pytest` real en el entorno de
mi computadora al que tiene acceso, pero ahí también está bloqueado PyPI.

**Cambio realizado.** `.github/workflows/ci.yml`: en cada push y Pull Request
instala `requirements.txt` y corre `pytest -v`, `ruff check src` y
`mypy --strict src` con **Python 3.10 y 3.12**.

**Iteraciones del workflow (3 commits `ci:`).**
1. Primera versión: los dos jobs en verde, pero la IA **no pudo leer el log**
   (GitHub lo sirve desde una URL firmada demasiado larga para sus
   herramientas), así que solo podía afirmar "success", no "62 passed".
2. Cada paso publica su última línea como **anotación** (`::notice::`) y en el
   resumen del job: así el resultado exacto es legible por la API y visible en
   la página del run.
3. GitHub advirtió que `checkout@v4` y `setup-python@v5` usan Node 20
   (obsoleto); se actualizaron a `@v6` (verificando antes que las etiquetas
   existen) y la advertencia desapareció.

**Resultado** ([run](https://github.com/albertomtzu23/M1.-Reto/actions/runs/37721048038)):

| Verificación | Python 3.10 | Python 3.12 |
|---|---|---|
| `pytest -v` | ✅ **62 passed** | ✅ **62 passed** |
| `ruff check src` | ✅ All checks passed! | ✅ All checks passed! |
| `mypy --strict src` | ✅ Success | ✅ Success |

Detalle en [`docs/evidencia.md`](evidencia.md).

**Qué aprendí.** "No tengo Python" no tenía que frenar la entrega: la
integración continua da evidencia más fuerte que una corrida local (entorno
limpio, dos versiones de Python, repetible en cada cambio y visible en el PR).
Y que la IA no pudiera leer el log me obligó a que la evidencia quedara
publicada de forma explícita, no solo como un check verde.

---

## Intentos fallidos y ajustes

*(Se registran aquí los prompts que no dieron el resultado esperado y cómo se corrigieron.)*

| Situación | Qué pasó | Cómo se resolvió |
|---|---|---|
| Clonar el repo desde la carpeta local | El shell de mi equipo usado por la IA no tiene salida a GitHub (proxy 403); quedó una carpeta `M1.-Reto/` vacía con un `.git` incompleto en `D:\2026\Curso IA\Modulo 1. Fundamentos Base`. | Se clonó en el espacio de trabajo de la nube y después se copió el repositorio completo (con su historial) a esa carpeta; los archivos temporales de git requirieron autorizar borrado en la carpeta. |
| Instalar `pytest` en la nube | La política de red bloquea PyPI. | Ejecutor de pruebas equivalente para validar cada paso; evidencia final con `pytest` real en GitHub Actions. |
| Correr `pytest` en mi equipo | Windows sin Python instalado (`python` abre la Microsoft Store); el entorno de mi computadora al que accede la IA también bloquea PyPI. | Integración continua con GitHub Actions (Python 3.10 y 3.12). |
| Leer el log de GitHub Actions | La IA no pudo descargar el log (URL firmada demasiado larga). | El workflow publica el resultado de cada paso como anotación del run. |
| Push a GitHub | Primero la cuenta de GitHub no estaba vinculada; después de vincularla, el push seguía con 403 porque faltaba instalar la app de Claude para GitHub con acceso al repositorio. | Instalé la app de Claude en mi cuenta con acceso a `M1.-Reto`; el push de `main` y `refactorizacion` funcionó. |

---

## Evidencia

Pruebas y linter ejecutados con herramientas reales en GitHub Actions
([run](https://github.com/albertomtzu23/M1.-Reto/actions/runs/37721048038)):

```text
pytest (Python 3.10): 62 passed      pytest (Python 3.12): 62 passed
ruff   (Python 3.10): All checks passed!   ruff (Python 3.12): All checks passed!
mypy   (Python 3.10): Success: no issues found in 4 source files
mypy   (Python 3.12): Success: no issues found in 4 source files
```

Detalle completo en [`docs/evidencia.md`](evidencia.md).

## Entrega

Pull Request [#1](https://github.com/albertomtzu23/M1.-Reto/pull/1):
`refactorizacion` → `main`, con la descripción del formato de entrega y el
*check* de CI (pytest, ruff y mypy en Python 3.10 y 3.12).
