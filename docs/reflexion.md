# Reflexión final

**Reto:** Refactorización asistida por IA — Gestor de inventario "La Esquina"
**Nombre:** Alberto Martínez
**Fecha:** 2026-10-07

> Este documento resume lo que aprendí. El detalle de cada paso (prompts tal
> cual, cambios, verificaciones y tropiezos) está en [`bitacora.md`](bitacora.md).

## En números

| | Inicio | Final |
|---|---|---|
| Errores de `ruff check src` | 20 | **0** |
| Errores de `mypy --strict src` | 58 | **0** |
| Pruebas | 20 | **62** (20 originales intactas + 42 nuevas) |
| Errores introducidos a propósito que detecta la suite (prueba de mutación) | 0 / 10 | **10 / 10** |
| Refactorizaciones | — | **8**, más 1 corrección de bug, un commit cada una |

## Lo que esperaba y lo que encontré

Esperaba que la refactorización fuera fácil y entendible para mis
conocimientos. Lo que encontré es que la IA es mucho más poderosa para esta
tarea de lo que imaginaba: no solo cambia el código, también detecta riesgos
que yo no habría visto y explica por qué cada cambio es seguro o no lo es. Al
mismo tiempo, me di cuenta de que esa potencia exige que yo entienda lo que
está pasando para poder decidir; no basta con aprobar.

## Lo que más me sirvió

**Las comparaciones de antes y después.** Los tests originales pasaban desde
el principio, pero eso no me decía si el programa seguía haciendo lo mismo en
los casos que nadie había probado. Ver que la versión anterior y la nueva daban
exactamente el mismo resultado en cientos de casos (926 ventas, 53 errores, la
sesión completa del menú, el JSON guardado) es lo que me dio confianza en
cada cambio.

**Que la IA explicara las razones de cada cambio.** No solo veía el diff:
entendía por qué `>` se invierte a `<=` al convertir un `if` en cláusula de
guarda, por qué `0` y `0.0` no son lo mismo cuando se guardan en un JSON, o por
qué reordenar una operación con decimales puede cambiar el redondeo. Esas
explicaciones son lo que más aprendí del reto.

## Lo que la IA encontró y yo no había notado

- Un **bug real** del código original: un JSON válido sin la clave
  `"inventario"` borraba el inventario en memoria y después tronaba. La IA no
  lo corrigió por su cuenta: lo reportó, me dio opciones y yo decidí
  corregirlo en un commit aparte, con pruebas que fallan con el código
  anterior.
- Que `except json.JSONDecodeError` **no basta**: un archivo con bytes que no
  son UTF-8, un número con miles de dígitos o un JSON anidado miles de veces
  lanzan otras excepciones. Dos de esos casos no los había anticipado ni
  siquiera el prompt.
- Que renombrar variables con nombres más largos **rompe el límite de
  88 caracteres** en varias líneas.
- Que la suite original **no detectaba ninguno** de 10 errores típicos de
  refactorización (por ejemplo, cambiar `>= 500` por `> 500`). Con las pruebas
  nuevas los detecta todos.

## Mi papel y mis decisiones

Mi participación fue revisar los prompts que la IA me proponía y tomar
decisiones de acuerdo con las sugerencias que me daba. Algunas decisiones
concretas:

- Ajusté el primer prompt ("código **no funcional**" en lugar de "código
  muerto").
- Decidí **corregir el bug** de pérdida de datos en lugar de solo
  documentarlo.
- Elegí que mis respuestas guiaran esta reflexión en lugar de que la IA la
  escribiera sola.
- Configuré la conexión con GitHub cuando el push falló.

## Lo que no funcionó tan bien

**Crear prompts detallados sobre un tema que no domino.** Debo admitir que le
pedí ayuda a la IA para armar los prompts. Funcionó bien para el resultado,
pero me deja una lección: un prompt detallado solo es tan bueno como mi
capacidad de revisarlo. Cuando no conozco bien el tema, termino aprobando en
lugar de decidir.

La IA también se equivocó y lo documentamos:

- En la refactorización 3 el prompt se contradecía ("mueve los `if` tal cual" y
  a la vez "desaparece SIM108").
- En la 8, la primera corrección de un error de tipos usaba `str(...)`. Pasaba
  todas las pruebas, pero cambiaba el comportamiento con datos inesperados, y
  se corrigió.
- En la 5, una prueba simulada del menú daba "idéntico" sin haber recorrido
  todas las opciones.

Ninguno de esos errores llegó al código final porque cada paso tenía una
verificación. Eso me confirma que revisar no es opcional.

## Técnicas de prompting que mejor funcionaron

1. **Alcance cerrado.** Decir exactamente qué cambiar y qué no ("no renombres
   variables: eso es la refactorización 5") evitó que la IA mezclara cambios.
2. **Resultado esperado medible.** "20 tests y 13 errores de ruff" convierte la
   validación en una comprobación objetiva: si el número no cuadra, algo se
   tocó de más.
3. **Empezar por el problema y no por la instrucción.** Explicar *por qué* había
   que cambiar algo ayudó a que las decisiones de la IA fueran mejores.
4. **Pedir que razone antes de actuar.** "Enumera qué excepciones puede lanzar
   antes de elegirlas" encontró casos que nadie había previsto.
5. **Anticipar las trampas.** Advertir de las fronteras al invertir
   condiciones, del redondeo con decimales o de las claves del JSON.
6. **Reglas en `CLAUDE.md`.** La regla "si un cambio altera el comportamiento,
   repórtalo y pregunta" fue la que convirtió el hallazgo del bug en una
   decisión mía y no en un cambio silencioso.

## Lo que me llevo

Aprendí a detallar los prompts, pero sobre todo aprendí que **tengo que
conocer lo mejor posible de qué trata la tarea o el desarrollo**. Solo así
puedo decidir cómo debe actuar la IA, revisar lo que propone y darme cuenta
cuando algo no cuadra. La IA hace muy bien el trabajo mecánico y encuentra
riesgos que yo no vería, pero la responsabilidad de entender y validar cada
cambio sigue siendo mía.

En un proyecto real de mi trabajo haría igual:

- un `CLAUDE.md` con las reglas del proyecto;
- un cambio por commit;
- resultados esperados con números;
- comparar el antes y el después en lugar de confiar solo en que "los tests
  pasan".

Lo que haría distinto: dedicar más tiempo a entender el código **antes** de
pedir cambios, para poder escribir yo más partes del prompt y depender menos
de que la IA me lo arme.
