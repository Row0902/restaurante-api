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

## Interaccion 6 - Milestone 1: Nombrar dominio

Tipo: milestone, refactor, pruebas, validacion
Alcance: implementacion de dominio puro sin tocar FastAPI
Archivos: `src/core/`, `test/unit/core/`

Prompt:
Disenar el core de dominio para plato, orden, item de orden, precio, cantidad y
estado. Primero proponer archivos, riesgos y tests unitarios; luego implementar
tras aprobacion, cumpliendo un archivo por clase, funciones cortas, type hints y
cero dependencias de FastAPI.

Resultado:
Se agregaron entidades y value objects de dominio: `Plato`, `Orden`,
`ItemOrden`, `Precio`, `Cantidad`, `EstadoOrden` y `DominioError`, junto con
tests unitarios puros para reglas de validacion, totales y transiciones.

Que funciono:
El milestone quedo aislado en `core`, sin modificar `src/main.py` ni la API
actual. Los tests verifican comportamiento del dominio y ausencia de dependencias
de `fastapi`, `pydantic` y `sqlmodel` en la capa core.

Que no funciono / correccion:
`uv` fallo inicialmente por acceso denegado y se reejecuto con permisos. Ruff
obligo a renombrar la excepcion a `DominioError` y agregar docstrings minimos;
Ty detecto una union debil en `Precio`, corregida tipando el monto interno como
`Decimal`.

Validacion:
`uv run pytest test/unit/core -q`: 28 passed.
`uv run ruff check src/core test/unit/core`: sin errores.
`uv run ty check src/core test/unit/core`: sin errores.
`uv run ruff format --check src/core test/unit/core`: ya formateado.

Decision:
Mantener el dominio independiente de framework y postergar su integracion con
FastAPI para milestones posteriores.

---

## Interaccion 7 - Milestone 2: Servicios de aplicacion

Tipo: milestone, refactor, pruebas, validacion, decision de alcance
Alcance: extraccion de casos de uso fuera de endpoints
Archivos: `src/main.py`, `src/services/`, `src/repositories/`, `test/unit/services/`

Prompt:
Extraer `MenuService` y `OrdenService` con repositorios inyectados. Los servicios
no deben depender de FastAPI. Escribir primero tests unitarios con repos
mockeados y mantener cambios pequenos y reversibles.

Resultado:
Se movio la logica de menu y ordenes desde `main.py` hacia servicios de
aplicacion, usando repositorios in-memory inyectados y preservando el contrato
observable actual de la API.

Que funciono:
Los tests unitarios de services se escribieron primero con `AsyncMock` y fijaron
delegacion, creacion, calculo de total, cambio de estado y no persistencia ante
fallos.

Que no funciono / correccion:
El primer ciclo de tests fallo por ausencia esperada de `services`, validando el
flujo TDD. Un parche inicial sobre `main.py` no aplico por diferencias de
encoding y se corrigio usando contextos mas estables. Ruff aplico un arreglo
menor automatico.

Validacion:
`uv run pytest test/unit/services`: 8 passed.
`uv run pytest test/unit/services test/test_main.py`: 33 passed.
`uv run pytest`: 61 passed.
`uv run ruff check src test`: sin errores.

Decision:
No integrar todavia el dominio `core` ni separar routers `api/`; el milestone
se limito a servicios y repositorios para evitar cambiar reglas actuales.

---

## Interaccion 8 - Milestone 3: Repositorios async en memoria

Tipo: milestone, pruebas, correccion, validacion
Alcance: infraestructura temporal de persistencia sin base de datos
Archivos: `src/repositories/`, `test/unit/repositories/`

Prompt:
Implementar repositorios async en memoria para menu y ordenes, sin introducir
base de datos, de forma que sirvan como infraestructura temporal y permitan
futura sustitucion por SQLModel sin tocar servicios.

Resultado:
Se endurecieron `InMemoryMenuRepository` e `InMemoryOrdenRepository` con
almacenamiento opcional, metodos async y copias defensivas. Se agregaron tests
unitarios de repositorios para persistencia, reemplazo, errores actuales y
aislamiento de referencias internas.

Que funciono:
Los servicios conservaron la dependencia contra contratos `Protocol` y no fue
necesario modificar endpoints ni reglas observables de la API.

Que no funciono / correccion:
La primera ejecucion uso por error `--runInBand`, bandera de Jest no valida en
pytest. Luego `ty` detecto casts/anotaciones debiles en tests y se corrigieron
sin tocar codigo productivo adicional. `uv run ty` fallo por acceso denegado en
Windows, por lo que se valido con `.venv\Scripts\ty.exe`.

Validacion:
`uv run pytest test/unit/repositories`: 8 passed.
`uv run pytest test/unit/repositories test/unit/services test/test_main.py`: 41 passed.
`uv run ruff check src test`: sin errores.
`.venv\Scripts\ty.exe check src test`: sin errores.
`uv run pytest`: 69 passed.

Decision:
Mantener la persistencia como infraestructura in-memory reemplazable y posponer
SQLModel/base de datos hasta un milestone explicito.

---

## Interaccion 9 - Milestone 4: Capa API limpia

Tipo: milestone, refactor, pruebas, correccion, validacion
Alcance: separar FastAPI como capa de transporte
Archivos: `src/main.py`, `src/api/`, `src/core/recurso_no_encontrado_error.py`,
`src/repositories/`, `test/integration/test_api.py`, tests unitarios afectados,
`prompt.md`

Prompt:
Mover endpoints a routers por recurso, agregar schemas Pydantic, traducir
excepciones de dominio a `HTTPException`, dejar `main.py` como ensamblador y
escribir tests de integracion async. Se aprobo primero el plan de implementacion
y se autorizo usar subagentes si fueran necesarios.

Resultado:
Se creo la capa `api` con routers de health, menu y ordenes, schemas Pydantic
por clase, dependencias compartidas y traduccion de errores de dominio. `main.py`
quedo reducido al ensamblaje de FastAPI, CORS y routers.

Que funciono:
La separacion `api -> services -> repositories -> core` quedo mas explicita y
los tests de API pasaron de `TestClient` sincrono a integracion async con
`ASGITransport`. Los recursos inexistentes ahora responden 404 y payloads
invalidos se validan en la frontera HTTP.

Que no funciono / correccion:
Un parche inicial sobre `main.py` fallo por diferencias de encoding y se rehizo
con reemplazo controlado. Ruff detecto sintaxis generica, `Depends` en defaults
y nombre de excepcion sin sufijo `Error`; Ty detecto una fixture mal anotada.
Tambien se corrigio el borde `PUT /menu/{id}` para devolver 404 si el plato no
existe.

Validacion:
`uv run pytest`: 54 passed.
`uv run ruff check src test`: sin errores.
`uv run ruff format --check src test`: 48 files already formatted.
`uv run ty check src test`: sin errores.

Decision:
Mantener repositorios en memoria y no introducir DB ni migraciones; el milestone
se limito a transporte HTTP, schemas, traduccion de errores y pruebas de API.

---

## Interaccion 10 - Milestone 1: Dominio real en services

Tipo: milestone, refactor, pruebas, validacion
Alcance: integrar reglas de `core` en services sin tocar repositorios ni DB
Archivos: `src/services/menu_service.py`, `src/services/orden_service.py`,
`test/unit/services/`, `test/integration/test_api.py`

Prompt:
Implementar el Milestone 1 aprobado: `MenuService` y `OrdenService` deben usar
`core` para validar platos, precios, items, cantidades, ordenes y estados.

Resultado:
Los services dejaron de aceptar reglas como dicts libres. Ahora rechazan precio
negativo, nombre vacio, estados desconocidos y `pendiente -> entregada`.

Que funciono:
El cambio se mantuvo acotado a services y tests, conservando API, routers y
repositorios in-memory.

Que no funciono / correccion:
`ty` detecto un tipo demasiado amplio al construir `Precio`; se corrigio
normalizando el valor a string.

Validacion:
`uv run pytest`: 62 passed.
`uv run ruff check`: sin errores.
`uv run ty check`: sin errores.

Decision:
Mantener la persistencia como registros serializables, pero mover las reglas de
negocio efectivas a objetos de dominio.

---

## Interaccion 11 - Milestone 2: Eliminar saltos de capas

Tipo: milestone, refactor, validacion
Alcance: arquitectura de imports y fronteras entre capas
Archivos: `src/api/`, `src/services/`, `src/repositories/`, `src/core/registro.py`,
`test/unit/test_import_layers.py`

Prompt:
Eliminar saltos de capas para cumplir estrictamente `api -> services ->
repositories -> core`: quitar imports de repositorios desde routers, mover
`Registro` fuera de repositories, revisar `api/http_errors.py` y validar con
ruff, ty y tests.

Resultado:
`api` dejo de importar `repositories`, `core`, `Registro`, `InMemory` y
`SQLModel`. El ensamblado in-memory paso a `services.container`, `Registro` quedo
en `core.registro` y la API traduce errores de aplicacion.

Que funciono:
La auditoria previa separo saltos reales de decisiones de frontera. El test
estatico agregado fija que `api/` no vuelva a depender de infraestructura ni de
detalles in-memory.

Que no funciono / correccion:
Ruff corrigio automaticamente 5 detalles de estilo. Luego se ajusto un docstring
obsoleto de `api/http_errors.py`.

Validacion:
`uv run ruff check .`: sin errores.
`uv run ty check`: sin errores.
`uv run pytest test\unit test\integration --cov=src`: 64 passed, cobertura 99%.
`uv run pytest test\unit\test_import_layers.py`: 2 passed.
Auditoria `rg` sobre `src/api`: sin imports/menciones prohibidas.

Decision:
No aceptar `api -> core` como excepcion para errores; la traduccion de dominio a
aplicacion queda en `services` y HTTP solo traduce errores de aplicacion.

---

## Interaccion 12 - Milestone 3: Persistencia SQLite async

Tipo: milestone, refactor, pruebas, correccion, validacion
Alcance: implementacion de persistencia SQLModel async con SQLite
Archivos: `src/repositories/database*.py`, `src/repositories/models/`,
`src/repositories/sqlmodel_*_repository.py`, `src/services/container.py`,
`src/main.py`, `test/integration/test_api.py`, `test/unit/repositories/`

Prompt:
Implementar el plan aprobado para alinear README con SQLModel, SQLAlchemy async
y SQLite, manteniendo protocolos de repositorio y services sin reglas de negocio
en modelos SQLModel.

Resultado:
La API usa repositorios SQLModel por request con `AsyncSession`, crea tablas en
lifespan y conserva repositorios in-memory como soporte de tests existentes.

Que funciono:
Los repositorios traducen entre SQLModel y `Registro`, preservan extras de menu y
persisten ordenes con tabla separada de items.

Que no funciono / correccion:
La primera relacion ORM con anotaciones diferidas fallo en runtime; se reemplazo
por consultas explicitas de items. `ty` y `ruff` obligaron a ajustar casts en
columnas SQLModel.

Validacion:
`uv run pytest`: 72 passed.
`uv run ruff check --no-fix src test`: sin errores.
`uv run ruff format --check src test`: 65 files already formatted.
`uv run ty check src test`: sin errores.

Decision:
No tocar `.env`, `prompt.md` fuera de esta entrada, migraciones ni seeds; mantener
generacion de IDs existente y DB aislada por test.

---

## Interaccion 13 - Milestone 4: Configuracion y ensamblaje real

Tipo: milestone, refactor, pruebas, validacion
Alcance: configuracion de aplicacion y composition root de FastAPI
Archivos: `src/config.py`, `src/main.py`, `src/api/dependencies.py`,
`src/services/container.py`, `src/repositories/database.py`,
`test/integration/test_api.py`, `test/unit/test_config.py`

Prompt:
Implementar Milestone 4 para que FastAPI arranque con configuracion real:
`DATABASE_URL`, `APP_NAME`, `DEBUG`, repositorios SQLModel desde dependencias,
startup/lifespan para preparar DB y sin leer ni modificar `.env`.

Resultado:
Se agrego `Config` con `pydantic-settings`, `crear_app(config)` como factory,
engine/session maker por aplicacion y DB temporal para tests de integracion.

Que funciono:
La configuracion se puede inyectar en tests sin secretos y `app = crear_app()`
mantiene compatible `fastapi dev src/main.py`.

Que no funciono / correccion:
Ruff aplico un autofix menor de formato/imports. Un chequeo manual con
`uv run python -c ...` fue bloqueado por permisos del entorno.

Validacion:
`uv run pytest`: 75 passed.
`uv run ruff check src test`: sin errores.
`uv run ty check`: sin errores.

Decision:
Eliminar la configuracion acoplada a repositorios y no usar `env_file`; `.env`
queda fuera de lectura/modificacion.

---
