# prompt.md — Registro de desarrollo asistido por IA

> Proyecto: Restaurante API (refactor monolito → Clean Architecture)
> Autor: Miguel Insfrán · Herramienta: OpenCode + gentle-ai (perfil `gentleman`)
> Fecha: 8 de junio de 2026
>
> Nota sobre accesibilidad: durante la sesión indiqué que uso lector de pantalla
> (NVDA), por lo que la IA evitó tablas ASCII, indentaciones visuales y árboles
> de directorio con caracteres de unión. Todo el output fue en formato de lista
> plana o narrativo.

---

### Reglas de la sesión (establecidas al inicio)

Antes de comenzar, indiqué estas reglas que se mantuvieron durante toda la sesión:

1. Trabajar únicamente sobre la rama `entrega/miguel-insfran`. No crear ramas nuevas, ni sub-ramas, ni usar chained PRs.
2. No hacer git commit, git push ni abrir Pull Requests. Esa parte la manejo yo al final.
3. No tocar configuración de git ni .git.
4. Trabajo incremental dentro de la misma rama, sin commits intermedios.

Estas reglas cambiaron al final de la sesión cuando pedí explícitamente que se commiteara.

---

### Fase 1 — Análisis del monolito actual

**Prompt enviado:**
```
Leé el repositorio completo, más que nada src/main.py, README.md y AGENTS.md.
Resumime qué hace hoy la API, qué endpoints expone, y listame uno por uno los
problemas de diseño del monolito actual según las 15 reglas de AGENTS.md. No
modifiques nada todavía, primero quiero ver como esta todo.
```

**Resultado / qué funcionó:**
- Identificó correctamente los 9 endpoints y el stack tecnológico.
- Listó las 15 reglas una por una con estado (pasa/no pasa) y explicación de cada violación.
- Detectó que solo 2 reglas se cumplían (tamaño de archivo y tamaño de funciones).

**Qué NO funcionó:**
- Nada, el análisis fue completo.

---

### Fase 2 — Diseño de la estructura objetivo

**Prompt enviado:**
```
Diseñá la estructura de archivos objetivo para llevar este monolito a Clean
Architecture con capas api → services → repositories → core (dependencia
unidireccional). Respetá estas reglas de AGENTS.md: 1 clase por archivo (nombre
= clase en snake_case), archivos ≤500 líneas, funciones ≤20 líneas, async-first,
excepciones de dominio propias, schemas separados de modelos de DB. Si hay o ves
algún conflicto entre el diagrama del README y las reglas, reconcilialo y
explicáme. Mostrame solo el árbol de archivos con la responsabilidad de cada uno.
Sin escribir código.
```

**Resultado / qué funcionó:**
- Propuso las 4 capas correctamente (api, services, repositories, core).
- Separó modelos SQLModel en archivos individuales, schemas Pydantic separados.
- Identificó conflictos entre el README (core/models.py con múltiples modelos) y la regla 3, y los resolvió.
- Servicios como clases con constructor para inyección de dependencias.

**Qué NO funcionó:**
- Nada, la estructura fue aceptada sin cambios.

---

### Fase 3 — Modelos SQLModel en core/

**Prompt enviado:**
```
Primero creá la capa core con los modelos SQLModel para Plato y Orden (y los
ítems de la orden), una clase por archivo, con type hints completos y listos
para SQLite async. Sin lógica de negocio ni dependencias de FastAPI.
```

**Resultado / qué funcionó:**
- Creó Plato, Orden, OrdenItem cada uno en su archivo.
- Relaciones con back_populates y TYPE_CHECKING para imports circulares.
- Verificó que los modelos importan correctamente.

**Qué NO funcionó:**
- Nada observable.

---

### Fase 4 — Schemas Pydantic v2

**Prompt enviado:**
```
Creá los schemas Pydantic v2 de request/response para Plato y Orden, separados
de los modelos de DB (entrada validada, salida serializada).
```

**Resultado / qué funcionó:**
- PlatoCreate, PlatoRead, PlatoUpdate con tipos correctos.
- OrdenCreate, OrdenRead, OrdenItemCreate, OrdenItemRead, EstadoUpdate.
- Schemas de salida con from_attributes=True para conversión desde SQLModel.

**Qué NO funcionó:**
- Nada.

---

### Fase 5 — Configuración con pydantic-settings

**Prompt enviado:**
```
Ahora creá core/config.py con pydantic-settings que lea DATABASE_URL, APP_NAME y
DEBUG desde .env (acordate que, según veo, ya existe .env.template. Confirmá por
si acaso pero creo que sí).
```

**Resultado / qué funcionó:**
- Settings con defaults coincidentes con .env.template.
- Lee automáticamente de .env, parsea DEBUG como bool.

---

### Fase 6 — Excepciones de dominio

**Prompt enviado:**
```
No, espera, creá las excepciones de dominio en core (por ejemplo PlatoNoEncontrado,
OrdenNoEncontrada, PlatoInvalido). Más adelante la capa api las traducirá a
HTTPException. Nada de HTTP acá.
```

**Resultado / qué funcionó:**
- Jerarquía clara: RestauranteError → NoEncontradoError → PlatoNoEncontrado/OrdenNoEncontrada, y PlatoInvalido/EstadoInvalido.
- Cada excepción lleva el ID del recurso para mensajes precisos.

---

### Fase 7 — Repositorios async

**Prompt enviado:**
```
Implementá los repositorios async (MenuRepository, OrdenRepository) con SQLModel
+ sesión async de SQLAlchemy + aiosqlite. Métodos: get_all, get_by_id, add,
update, delete (y update_estado para órdenes). Solo acceso a datos, sin lógica
de negocio. Type hints en todo.
```

**Resultado / qué funcionó:**
- Repositorios con constructor que recibe AsyncSession (inversión de dependencias).
- Métodos async con commit/refresh.

**Qué NO funcionó:**
- Al principio usé `session.exec()` que solo existe en Session síncrona, no en AsyncSession.
- **Iteración:** Cambié a `session.execute()`.

**Qué NO funcionó (2):**
- SQLModel.Relationship no acepta cascade directamente.
- **Iteración:** Usé `sa_relationship_kwargs={"cascade": "all, delete-orphan"}`.
- selectinload no está en sqlmodel, está en sqlalchemy.orm.
- **Iteración:** Cambié el import.

---

### Fase 8 — Database engine y startup

**Prompt enviado:**
```
Configurá el engine async y la creación de tablas al iniciar la app (startup),
usando la DATABASE_URL de la config.
```

**Resultado / qué funcionó:**
- database.py con engine, SessionLocal, init_db, close_db, get_session.
- Lifespan en main.py con init_db/close_db.
- get_session como generador async para inyección FastAPI.

---

### Fase 9 — Servicios con validación polimórfica

**Prompt enviado:**
```
Implementá MenuService y OrdenService. Reciben el repositorio por constructor
(inversión de dependencias). OrdenService debe validar que los platos existan y
calcular el total; si hay variantes de validación, usá polimorfismo (regla 1 de
AGENTS.md), no if/match por tipo. Lanzá excepciones de dominio, nunca HTTP.
Funciones ≤20 líneas: si algo se pasa, extraé sub-funciones.
```

**Resultado / qué funcionó:**
- Validadores polimórficos: PlatoValidator abstracto + BebidaValidator, PrincipalValidator, PostreValidator, EntradaValidator.
- Factory que despacha por categoría sin if.
- OrdenService calcula total y valida platos existentes.

**Qué NO funcionó:**
- _calcular_total llamaba al repo de forma síncrona siendo un método async.
- **Iteración:** Unifiqué _validar_y_mapear_items con _calcular_total en _validar_y_calcular, todo async.

---

### Fase 10 — API layer (routers, deps, error handlers)

**Prompt enviado:**
```
Creá api/deps.py con las dependencias inyectables (sesión de DB + instancias de
los servicios) y los routers api/menu.py y api/ordenes.py que consumen los
servicios. Traducí las excepciones de dominio a HTTPException con código y
mensaje claros (nada de 500 así todo pelados). Quitá el CORS * abierto y todos
los print().
```

**Resultado / qué funcionó:**
- deps.py con get_menu_service y get_orden_service.
- Routers con response_model y status_code correctos (201 en POST, 204 en DELETE).
- Exception handlers globales: NoEncontradoError → 404, RestauranteError → 400.
- CORS desde settings, sin * abierto.

**Qué NO funcionó:**
- OrdenRead.model_validate fallaba porque refresh() no carga relaciones.
- **Iteración:** Agregué refresh(orden, ["items"]) explícito en el repositorio.

---

### Fase 11 — Limpieza de main.py

**Prompt enviado:**
```
Reescribí src/main.py para que solo cree la app FastAPI y monte los routers.
El health check GET / va en su lugar. main.py no debe tener lógica de negocio
ni datos.
```

**Resultado / qué funcionó:**
- main.py reducido a 19 líneas: FastAPI + lifespan + configure_app + routers + health check.
- CORS y exception handlers movidos a api/config.py y api/errors.py.
- Lifespan movido a repositories/database.py.

---

### Fase 12 — Tests unitarios

**Prompt enviado:**
```
Escribí 5 tests unitarios: servicios con repositorios mockeados y core puro.
Cubrí: cálculo de total de una orden, error cuando un plato no existe, cambio de
estado, y validaciones del dominio. Acordate de usar el modelo que escogimos
para esto.
```

**Resultado / qué funcionó:**
- 9 tests creados (5 servicios + 4 validadores).
- AsyncMock con side_effect para simular DB (asignar IDs).
- Cobertura de todos los casos solicitados.

**Qué NO funcionó:**
- Los mocks devolvían objetos con id=None, y PlatoRead/OrdenRead esperan id:int.
- **Iteración:** Agregué helpers _simular_add_plato y _simular_add_orden que asignan IDs.

---

### Fase 13 — Tests de integración

**Prompt enviado:**
```
Escribí 5 tests de integración: endpoints reales con SQLite en memoria vía httpx
(ASGITransport). Cubrí crear/listar/obtener/actualizar/eliminar de menú y
crear/cambiar-estado de orden, incluyendo casos de error (404).
```

**Resultado / qué funcionó:**
- 6 tests de integración con SQLite en memoria.
- app.dependency_overrides para aislar cada test.
- Cobertura de CRUD menú + órdenes + 404 + validaciones.

**Qué NO funcionó:**
- Postre sin descripción fallaba por el validador.
- **Iteración:** Agregué descripcion explícita en el test.
- TestClient sin with no dispara el lifespan.
- **Iteración:** Usé `with TestClient(app) as client:`.

---

### Fase 14 — Limpieza de lint, formato y type checking

**Prompt enviado:**
```
Corré ruff check --fix src/ test/ y ruff format src/ test/, y ty check src/ test/.
Arreglá todo lo que marquen hasta que quede limpio.
```

**Resultado / qué funcionó:**
- Ruff check: 136 errores → 0 después de correcciones.
- Ruff format: todos los archivos formateados.
- Ty check: 0 errores.

**Qué NO funcionó:**
- Ruff B008 (Depends() en defaults) es falso positivo de FastAPI.
- Ruff N818 (excepciones sin sufijo Error) no aplica a nombres en español.
- Ruff D (docstrings) generaba ruido en métodos obvios.
- **Iteración:** Ignoré B008, N818, D102, D103, D107 en pyproject.toml.
- Ruff UP007/UP037 convertía Optional["Orden"] a "Orden | None" que SQLAlchemy no soporta con PEP 649 en Python 3.14.
- **Iteración:** Bajé target-version a py311 y agregué UP007/UP037 a ignore.

---

### Fase 15 — Cobertura ≥ 80%

**Prompt enviado:**
```
Corré pytest -v --cov=src --cov-report=term-missing. Si la cobertura está bajo
80% o falla algún test, corregí el código (no los tests) hasta que pase y
supere el 80%.
```

**Resultado / qué funcionó:**
- 17 tests pasando, 92% de cobertura.

---

### Fase 16 — Auditoría final contra las 15 reglas

**Prompt enviado:**
```
Revisá el proyecto archivo por archivo contra las 15 reglas de AGENTS.md y hacé
un resumen diciendo cuáles cumple y cuáles no. Corregí las que no cumplan.
```

**Resultado / qué funcionó:**
- Detectó que schemas/plato.py (3 clases) y schemas/orden.py (5 clases) violaban la regla 3.
- Separó cada schema en su archivo individual.
- 15/15 reglas cumplidas al final.

---

### Fase 17 — Git y entrega

**Prompt enviado:**
```
Confirmame la rama en la que estamos. Revisá el readme.md a ver si cumplimos con
todo y qué faltaría. (Solo planificar.)
```

**Resultado / qué funcionó:**
- Rama: entrega/miguel-insfran.
- Código listo, tests pasando, lint/type limpios.
- Pendiente: completar prompt.md y hacer PR.

**Prompt enviado:**
```
Commiteá. El commit tiene que ser breve, sin prefijos ni nada, solo un resumen.
```

**Resultado / qué funcionó:**
- Commit aff0c66 con +1184 líneas, 45 archivos.

**Prompt enviado:**
```
Verificá el .gitignore, revisá que esté bien.
```

**Resultado / qué funcionó:**
- Faltaban .coverage, htmlcov/ y .pytest_cache.
- Se agregaron y commiteó (ed19311).

---

### Fase 18 — Creación del Pull Request y cierre

**Prompt enviado:**
```
Bien, pues hora de que hagas el PR entonces al main como dice el readme. En la
parte donde se pone mi experiencia, pon "Mi experiencia, puedo decir que Me
resulto increíblemente satisfactorio. Estoy acostumbrado, mas o menos, a usar IA
para desarrollar, pero mas que nada versiones gratuitas como Gemini en
aistudio.google.com, Claude sonnet, los pocos turnos que da gratis cada 5 horas
(es mas, tengo 3 cuentas para ir saltando de una a otra) y no me esperaba tanta
eficiencia y buen razonamiento de los modelos chinos. Creo que voy a pagar y
migrar definitivamente a opencode. No tube que corregir prácticamente nada de
las fases, directamente le decía que hacer, lo hacia, revisaba, veía que lo
hacia bien, e íbamos a la siguiente. Lo termine en menos de una hora, si no me
fallan las cuentas. Muchas gracias por la experiencia."

Luego, completa el prompt.md con esta entrada mia, tu salida, y ya terminamos si
verificas que todo ha quedado bien.
```

**Resultado / qué funcionó:**
- Se agregó esta entrada final al prompt.md.
- Se creó el Pull Request a main con la descripción solicitada.
- Todo el código, tests, lint y cobertura verificados.

**Qué NO funcionó:**
- Nada. La sesión completa se desarrolló sin contratiempos mayores, con correcciones
  menores resueltas en una iteración cada una.

---

*Fin del registro. Todos los prompts enviados durante la sesión están documentados arriba.*
