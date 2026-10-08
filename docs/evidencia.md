# Evidencia: pruebas y linter pasando

La evidencia se generó con **pytest, ruff y mypy reales**, ejecutados por
GitHub Actions ([`.github/workflows/ci.yml`](../.github/workflows/ci.yml)) en
cada push y en el Pull Request, con **Python 3.10 y 3.12**.

**Run de referencia:** <https://github.com/albertomtzu23/M1.-Reto/actions/runs/37721048038>
(commit `8cc2bb4`, estado: ✅ success en ambas versiones)

## Resultado por versión de Python

Salida exacta publicada por el workflow como anotaciones del run:

```text
validar (3.10): success
   pytest (Python 3.10): ============================== 62 passed in 0.16s ==============================
   ruff (Python 3.10): All checks passed!
   mypy (Python 3.10): Success: no issues found in 4 source files

validar (3.12): success
   pytest (Python 3.12): ============================== 62 passed in 0.31s ==============================
   ruff (Python 3.12): All checks passed!
   mypy (Python 3.12): Success: no issues found in 4 source files
```

| Verificación | Python 3.10 | Python 3.12 |
|---|---|---|
| `pytest -v` | ✅ 62 passed | ✅ 62 passed |
| `ruff check src` | ✅ All checks passed! | ✅ All checks passed! |
| `mypy --strict src` (adicional) | ✅ Success | ✅ Success |

El log completo de cada paso (incluida la lista de las 62 pruebas de
`pytest -v`) y el resumen del job se ven en la página del run.

## Por qué GitHub Actions y no una corrida local

- En mi equipo (Windows) **no hay Python instalado**: `python -m venv .venv`
  abrió el acceso directo de la Microsoft Store.
- En el espacio de trabajo de la IA, la política de red **bloquea PyPI**, así que
  `pytest` no se pudo instalar. Durante el proceso se validó con un ejecutor
  de pruebas equivalente; esta evidencia confirma el resultado con `pytest` real.

GitHub Actions ejecuta las herramientas oficiales en un entorno limpio a partir
de `requirements.txt`. Además, queda como validación automática para cualquier
cambio futuro y aparece como *check* en el Pull Request.
