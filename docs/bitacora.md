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

| # | Prompt usado | Cambio realizado | Justificación | Tests | Ruff |
|---|---|---|---|---|---|
| 1 | | | | | |
| 2 | | | | | |
| 3 | | | | | |
| 4 | | | | | |
| 5 | | | | | |

---

## Intentos fallidos y ajustes

*(Se registran aquí los prompts que no dieron el resultado esperado y cómo se corrigieron.)*

| Situación | Qué pasó | Cómo se resolvió |
|---|---|---|
| Clonar el repo desde la carpeta local | El shell de mi equipo usado por la IA no tiene salida a GitHub (proxy 403); quedó una carpeta `M1.-Reto/` vacía con un `.git` incompleto en `D:\2026\Curso IA\Modulo 1. Fundamentos Base`. | Se clonó en el espacio de trabajo de la nube. La carpeta vacía se puede borrar. |
| Instalar `pytest` en la nube | La política de red bloquea PyPI. | Ejecutor de pruebas equivalente para validar cada paso; `pytest` real en mi equipo para la evidencia final. |
| Push a GitHub | Primero la cuenta de GitHub no estaba vinculada; después de vincularla, el push seguía con 403 porque faltaba instalar la app de Claude para GitHub con acceso al repositorio. | Instalé la app de Claude en mi cuenta con acceso a `M1.-Reto`; el push de `main` y `refactorizacion` funcionó. |

---

## Evidencia

*(pendiente: salida final de `pytest` y `ruff check src`)*
