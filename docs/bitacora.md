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
   *Decisión pendiente:* corregirlo en un cambio aparte, documentado como
   cambio de comportamiento intencional (validar la estructura antes de
   vaciar y regresar `False` con un mensaje).
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
