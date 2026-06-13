# prompt.md

## Bitacora evaluativa de interacciones con IA

Este archivo documenta las interacciones usadas para orientar la refactorizacion de
la API FastAPI asincrona de restaurante. La evidencia se organiza segun la rubrica
del README: creatividad en prompts, eficacia de indicaciones, calidad esperada del
codigo final e iteracion/correccion.

### Contexto base y restricciones

El proyecto parte de un monolito con malas practicas deliberadas y debe avanzar de
forma incremental hacia Clean Architecture y Clean Code.

Restricciones acordadas:

1. No expandir el alcance sin aprobacion.
2. No implementar base de datos en esta etapa.
3. Priorizar cambios pequenos, reversibles y testeables.
4. Respetar la direccion de capas: `api -> services -> repositories -> core`.
5. Mantener tests primero y tests por capa.
6. Registrar prompts, decisiones, resultados e iteraciones en este archivo.

---

## Interaccion 1 - Analisis completo sin modificar archivos

### Prompt enviado

> Analiza este repositorio completo sin modificar archivos todavia.
>
> Contexto:
> Este proyecto es una API FastAPI asincrona de restaurante. La evaluacion final exige refactorizar desde un monolito con malas practicas hacia Clean Architecture y Clean Code.
>
> Debes respetar estrictamente las reglas de AGENT.md:
> - Separacion por capas: api -> services -> repositories -> core.
> - Validacion polimorfica, sin condicionales por tipo.
> - Un archivo por clase.
> - Archivos de maximo 500 lineas.
> - Funciones de maximo 20 lineas.
> - Clases con maximo 10 metodos publicos.
> - Type hints en toda funcion publica.
> - Async first para operaciones de I/O.
> - Manejo de errores con excepciones de dominio en core y traduccion a HTTPException en api.
> - Tests primero.
> - Tests por capa.
> - Cobertura minima de 80%.
>
> Ademas, el README exige crear un archivo prompt.md con todas las interacciones realizadas con IA.
>
> Tarea inicial:
> 1. Identifica la estructura actual del proyecto.
> 2. Detecta si actualmente es monolito o ya tiene separacion parcial por capas.
> 3. Lista los archivos principales y sus responsabilidades actuales.
> 4. Identifica incumplimientos respecto a AGENT.md.
> 5. Propone un plan de refactorizacion por pasos pequenos.
> 6. Indica que tests deberian escribirse primero.
> 7. No modifiques archivos todavia.
> 8. No hagas commits.
> 9. Devuelve un diagnostico claro y accionable.

### Resultado evaluativo

1. Funciono porque el prompt dio contexto, reglas de arquitectura, limites claros y una salida accionable: diagnostico, incumplimientos, plan incremental y tests iniciales.
2. Se confirmo que `src/main.py` era el monolito inicial: concentraba FastAPI, rutas, estado en memoria, reglas de negocio y errores implicitos.
3. La auditoria dejo claro que los tests existentes solo cubrian comportamiento minimo (`GET /` y `GET /menu` vacio), por lo que primero habia que caracterizar el contrato observable.

### Limitaciones e iteracion

1. `git status` no pudo ejecutarse por `dubious ownership`; no se forzo ninguna accion de Git.
2. No se ejecuto pytest para respetar la auditoria solo lectura y evitar escrituras incidentales de cache.
3. La decision fue no tocar codigo productivo hasta tener plan aprobado y tests de caracterizacion.

### Decisiones de alcance

1. Tratar `src/main.py` como punto de partida monolitico.
2. Mantener persistencia en memoria al inicio para no mezclar refactorizacion arquitectonica con DB.
3. Avanzar por cambios pequenos: tests, dominio, servicios, repositorios, API y calidad.

---

## Interaccion 2 - Flujo actual y oportunidad creativa

### Prompt enviado

> Dame el flujo actual del sistema. En el README.md se establece que tambien se califica la creatividad, entonces antes de transformar las deudas en milestones para iniciar la refactorizacion, necesito saber en que lo podemos mejorar

### Que funciono

1. Se describio el flujo actual de cliente HTTP, FastAPI en `src/main.py`, rutas `/`, `/menu`, `/ordenes`, diccionarios globales y calculo de total dentro del endpoint.
2. Se separaron oportunidades por eje: arquitectura, dominio, validacion, errores, persistencia, testing y calidad evaluable.
3. Se propuso una narrativa creativa para convertir deudas tecnicas en milestones atomicos.

### Que no funciono o quedo limitado

1. Aparecio una opcion de SQLModel/SQLite async, luego descartada para no ampliar alcance.

### Decisiones tomadas

1. No implementar DB por ahora.
2. Usar repositorios async en memoria para demostrar inversion de dependencias.
3. Usar `prompt.md` como evidencia de iteracion, criterio y descomposicion creativa.

---

## Interaccion 3 - Creacion de prompt.md

### Prompt enviado

> De acuerdo. Creo que no es necesario implementar DB, para no extender el alcance y no complicarlo. Lo demas aprobado.
> Crea prompt.md y deja documentado una sintesis de esta etapa que hemos desarrollado. Deja los milestones ya listos para ejecutarlos en diferentes hilos.

### Que funciono

1. Se fijo explicitamente el alcance sin base de datos.
2. Se aprobo continuar con arquitectura, dominio, validacion, errores, servicios, repositorios en memoria y tests.
3. Se creo una bitacora para cumplir el README y preparar trabajo incremental.

### Que no funciono o quedo limitado

1. El primer registro quedo demasiado extenso y repetitivo.
2. Los hilos sugeridos duplicaban parte del contenido de milestones.

### Decisiones tomadas

1. Mantener prompts enviados y sintesis evaluativa en `prompt.md`.
2. Documentar milestones como unidades de trabajo reutilizables.
3. Evitar que la bitacora sustituya la implementacion o invente interacciones no ocurridas.

---

## Flujo actual resumido

El sistema actual recibe solicitudes HTTP en una app FastAPI concentrada en
`src/main.py`. Las rutas `/menu` operan sobre un diccionario global `menu`; las
rutas `/ordenes` operan sobre otro diccionario global `ordenes` y calculan el
total de la orden dentro del endpoint usando los precios del menu. La misma capa
mezcla transporte HTTP, estado en memoria, validacion incompleta, calculo de
negocio y manejo de errores, por lo que el refactor debe separar dominio,
servicios, repositorios y API sin cambiar el alcance a base de datos.

### Deudas principales detectadas

1. `src/main.py` mezcla framework, rutas, estado, reglas de negocio y persistencia temporal.
2. No hay capas reales `api`, `services`, `repositories` y `core`.
3. Los endpoints usan `dict` crudos y no modelos de dominio.
4. No hay schemas Pydantic propios para request/response.
5. No hay excepciones de dominio ni traduccion HTTP consistente.
6. El calculo de total y validaciones viven dentro del endpoint.
7. Los tests no estan separados por capa ni cubren CRUD completo o errores.
8. La API todavia no refleja el enfoque async first en toda la cadena.

---

## Milestones compactos de refactorizacion

| Milestone | Objetivo | Alcance | Tests/evidencia | Criterio de exito |
| --- | --- | --- | --- | --- |
| 0 - Congelar comportamiento | Capturar contrato observable del monolito. | Tests de caracterizacion para rutas actuales; sin tocar codigo productivo. | `GET /`, `GET /menu`, CRUD basico de menu, orden con total y errores actuales. | Se sabe que comportamiento se preserva y que se corregira despues. |
| 1 - Nombrar dominio | Extraer conceptos de negocio fuera de FastAPI. | Entidades/value objects para plato, orden, item, precio, cantidad y estado; excepciones en `core`. | Tests unitarios de precio positivo, cantidad positiva, total y estado invalido. | `core` no depende de FastAPI ni repositorios. |
| 2 - Servicios | Mover casos de uso fuera de endpoints. | `MenuService`, `OrdenService` y repositorios inyectados por constructor. | Unitarios con repos mockeados para CRUD, total y plato inexistente. | Endpoints sin reglas de negocio; servicios independientes de FastAPI. |
| 3 - Repositorios en memoria async | Aislar persistencia sin introducir DB. | Repositorios async para menu y ordenes; interfaces/protocolos si ayudan. | Guardar, recuperar y manejar inexistentes en repositorios. | Los `dict` globales salen de `main.py`; una DB futura no obliga a tocar servicios. |
| 4 - API limpia | Dejar FastAPI como transporte. | Routers por recurso, schemas Pydantic y traduccion de errores de dominio a `HTTPException`. | Integracion HTTP async, 422 para payload invalido, 404 controlado y schemas esperados. | Dependencias respetan `api -> services -> repositories -> core`. |
| 5 - Calidad medible | Cerrar con evidencia objetiva. | Ejecutar tests, cobertura, ruff, formato y type checking. | `pytest`, cobertura `src`, `ruff check`, `ruff format --check`, `ty check`. | Tests pasan, cobertura >= 80%, lint/type checking limpios y limites de AGENTS.md respetados. |

---

## Prompts reutilizables por milestone

Estos prompts reemplazan la seccion extensa de hilos sugeridos y evitan duplicar
los milestones.

1. Caracterizacion: "Escribe tests de caracterizacion para la API actual sin modificar codigo productivo. Cubre rutas de menu, ordenes, calculo de total y errores actuales. Respeta AGENTS.md y usa el comando de test mas especifico posible."
2. Dominio y servicios: "Propone primero archivos, riesgos y tests para extraer core de dominio y servicios sin tocar API mas de lo necesario. Mantener un archivo por clase, type hints y cero dependencias de FastAPI en core."
3. API y cierre: "Limpia la capa FastAPI con routers, schemas y traduccion de excepciones de dominio. Luego audita cumplimiento contra AGENTS.md, cobertura, lint y type checking sin expandir alcance."

---

## Alcance aprobado actual

Incluido:

1. Refactorizacion hacia Clean Architecture.
2. Core de dominio.
3. Servicios de aplicacion.
4. Repositorios async en memoria.
5. Routers FastAPI.
6. Schemas Pydantic.
7. Excepciones de dominio y traduccion HTTP.
8. Tests primero y por capa.
9. Registro de interacciones en `prompt.md`.

Excluido por ahora:

1. Implementar base de datos.
2. Migraciones.
3. Seeds.
4. Configuracion sensible.
5. Refactors amplios no necesarios.
6. Commits automaticos.

---

## Interaccion 4 - Milestone 0: Tests de caracterizacion

Tipo: pruebas, validacion
Alcance: validacion inicial sin modificar codigo productivo
Archivos: `test/test_main.py`

Prompt:
Escribir tests de caracterizacion para la API actual sin modificar codigo
productivo. Cubrir rutas de menu, ordenes, calculo de total y errores actuales,
respetando AGENTS.md y usando el comando de test mas especifico posible.

Resultado:
Se amplio `test/test_main.py` de 2 a 12 casos para congelar el comportamiento
observable del monolito antes de iniciar la refactorizacion.

Que funciono:
Los tests aislan los diccionarios globales `menu` y `ordenes`, cubren CRUD de
menu, flujo de ordenes, calculo de total, orden sin items y errores 500 actuales.

Que no funciono / correccion:
El primer parche fallo por diferencias de codificacion en el archivo existente;
se reemplazo solo `test/test_main.py` manteniendo el alcance de pruebas.

Validacion:
`.venv\Scripts\python.exe -m pytest test\test_main.py`: 12 passed.
`.venv\Scripts\python.exe -m pytest test\test_main.py --cov=src --cov-report=term-missing`: 12 passed, cobertura 100% en `src/main.py`.
`.venv\Scripts\ruff.exe check test\test_main.py`: sin errores.
`.venv\Scripts\ruff.exe format --check test\test_main.py`: ya formateado.
`.venv\Scripts\ty.exe check test\test_main.py`: sin errores.

Decision:
Continuar con el siguiente milestone solo despues de preservar este contrato
observable como red de seguridad para la refactorizacion.

---

## Interaccion 5 - Milestone 0: Ampliacion de casos borde

Tipo: pruebas, validacion
Alcance: ampliacion de caracterizacion sin modificar codigo productivo
Archivos: `test/test_main.py`

Prompt:
Lanzar el subagente `escritor_tests` para cubrir los casos borde detectados por
`revisor_tests`, limitando el cambio a `test/test_main.py`.

Resultado:
Se ampliaron los tests de caracterizacion a 25 casos, incluyendo ordenes vacias,
IDs consecutivos y reutilizados, payloads fragiles, cantidades invalidas, estado
`None` y fallos sin persistencia parcial.

Que funciono:
El subagente mantuvo el alcance en pruebas, no modifico codigo productivo y dejo
congelados comportamientos actuales fragiles antes del refactor.

Que no funciono / correccion:
No aplica. Queda pendiente migrar estos tests cuando se apruebe cambiar el
contrato hacia validaciones y errores controlados.

Validacion:
`.venv\Scripts\python.exe -m pytest test\test_main.py --cov=src --cov-report=term-missing`: 25 passed, cobertura 100%.
`.venv\Scripts\ruff.exe check test\test_main.py`: sin errores.
`.venv\Scripts\ty.exe check test\test_main.py`: sin errores.

Decision:
Milestone 0 queda reforzado como red de seguridad; el siguiente paso puede
planificarse sobre el contrato observable ya congelado.

---
