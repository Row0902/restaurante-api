# Design: Menu Refactor

## Phase 0: Characterization Tests

### Technical Approach

Characterization tests freeze current behavior of the 5 menu endpoints (lines 42–117 in `src/main.py`) before refactoring. FastAPI sync `TestClient` against the live app. A `conftest.py` fixture resets the global `menu` dict before each test. All 15 spec scenarios covered via integration + unit tests.

### Architecture Decisions

| Option | Tradeoff | Decision |
|--------|----------|----------|
| `autouse` fixture vs manual `.clear()` vs `mock.patch` | `autouse` = no per-test boilerplate, direct `.clear()` = simple | **`autouse` fixture** — zero leakage risk, no author burden |
| Module-level `TestClient` vs per-function fixture | Module-level = simpler, matches existing `test_main.py` pattern | **Module-level** — consistency over isolation |
| Two test files vs one mixed file | Rule 11 mandates layer separation | **Two files** — `test/integration/test_menu_api.py` (HTTP) + `test/unit/test_menu.py` (dict state) |

### File Changes

| File | Action | Description |
|------|--------|-------------|
| `test/conftest.py` | Create | `autouse` fixture clearing `main.menu` before each test |
| `test/integration/test_menu_api.py` | Create | 13 HTTP-level characterization tests |
| `test/unit/test_menu.py` | Create | 5 dict state tests (isolation, CRUD effects) |

### Testing Strategy

| Layer | What | How |
|-------|------|-----|
| Integration | Status codes, JSON bodies, 500 on missing IDs | `TestClient(app).get\|post\|put\|delete()` |
| Integration | Print side effects | `capsys` fixture |
| Unit | Dict state after ops | Direct `menu` import + assertions |

### Risks

| Risk | Mitigation |
|------|------------|
| `autouse` fixture breaks existing tests | `test_main.py` already assumes clean menu |
| KeyError propagation in TestClient | `pytest.raises(KeyError)` fallback |
| Test order sensitivity | `autouse` eliminates shared state |

### Open Questions

- [x] Does FastAPI TestClient return 500 for unhandled KeyError? **Resolved**: No — TestClient propagates the exception. Tests use `pytest.raises(KeyError)`.

---

## Phase 1: Core Domain Layer

### Technical Approach

Build the innermost Clean Architecture layer: SQLModel table model, Pydantic v2 schemas with per-variant `validate()`, and a lightweight domain exception hierarchy. Zero dependencies on FastAPI, SQLAlchemy engines, or HTTP. Each schema variant owns its validation rules — no `if`/`match` on type (Rule 1).

### Architecture Decisions

| Option | Tradeoff | Decision |
|--------|----------|----------|
| `MenuItem` (spec) vs `Plato` (task brief) for model | `MenuItem` = matches `__tablename__` semantically; `Plato` = matches schema naming | **`MenuItem`** — spec uses RFC 2119 MUST; ORM name maps to table, schemas map to domain language |
| Group schemas in `schemas/menu.py` vs 3 files | 3 files = Rule 3 purity but 3 tiny modules; grouped = cohesion, spec-granted exception | **Grouped** — spec explicitly carves out schemas as exception to Rule 3 |
| Group exceptions in `exceptions.py` vs 3 files | 3 files for 5-line classes is noise; grouped = quick to scan | **Grouped** — exception classes are domain infrastructure, not domain entities |
| Custom `validate()` vs Pydantic `Field(gt=0)` constraints | Pydantic validators run at init but raise `ValidationError`, not `InvalidMenuDataError` | **Custom `validate()`** — fields use plain types; `validate()` raises domain exceptions directly. Service layer calls it explicitly. |
| `InvalidMenuDataError(field, message)` vs single `message` string | `(field, message)` enables structured error building; concatenation in `__init__` | **`(field, message)`** — `__init__` formats `f"{field} {message}"` for `str(e)` |

### Validation Pattern

Each schema has its own `validate()` — the caller does not know which variant, just calls `.validate()`:

```python
class PlatoCreate(BaseModel):
    nombre: str
    precio: float
    categoria: str | None = None
    descripcion: str | None = None

    def validate(self) -> None:
        if not self.nombre:
            raise InvalidMenuDataError("nombre", "is required.")
        if self.precio <= 0:
            raise InvalidMenuDataError("precio", "must be positive.")

class PlatoUpdate(BaseModel):
    nombre: str | None = None
    precio: float | None = None
    categoria: str | None = None
    descripcion: str | None = None

    def validate(self) -> None:
        if self.nombre is not None and not self.nombre:
            raise InvalidMenuDataError("nombre", "is required.")
        if self.precio is not None and self.precio <= 0:
            raise InvalidMenuDataError("precio", "must be positive.")
```

`PlatoResponse` uses `model_config = {"from_attributes": True}` with a no-op `validate()`.

### Exception Hierarchy

```
Exception
 └── DomainError              # Base — carries message only
      ├── MenuNotFoundError   # Takes plato_id: int → f"Menu item {id} not found."
      └── InvalidMenuDataError # Takes field: str, message: str → f"{field} {message}"
```

No HTTP knowledge. API layer (Phase 4) translates `MenuNotFoundError` → 404, `InvalidMenuDataError` → 400.

### File Changes

| File | Action | Description |
|------|--------|-------------|
| `src/core/__init__.py` | Create | Package init |
| `src/core/models/__init__.py` | Create | Package init |
| `src/core/models/menu.py` | Create | `MenuItem(SQLModel, table=True)` — table `menu_items`, fields: id, nombre, precio, categoria?, descripcion? |
| `src/core/schemas/__init__.py` | Create | Package init |
| `src/core/schemas/menu.py` | Create | `PlatoCreate`, `PlatoUpdate`, `PlatoResponse` — each with own `validate()` |
| `src/core/exceptions.py` | Create | `DomainError`, `MenuNotFoundError`, `InvalidMenuDataError` |

### Testing Strategy

| Layer | What | How |
|-------|------|-----|
| Unit | `MenuItem` instantiation — optional fields default `None`, `__tablename__` | Direct model construction, no DB |
| Unit | `PlatoCreate.validate()` — empty nombre, zero/negative precio | Construct + call `validate()`, assert exception |
| Unit | `PlatoUpdate.validate()` — partial fields, empty payload | Construct + call `validate()`, assert pass/fail |
| Unit | `PlatoResponse` — `from_attributes`, all fields present | Build from dict, serialize |
| Unit | Exception messages — `str(e)` matches spec | `raise` + catch, assert `str(e)` |

Tests live in `test/unit/core/` per Rule 11 (core = pure unit, no I/O).

### Dependencies

- `models/menu.py` → sqlmodel (framework dep at innermost layer — SQLModel IS the model)
- `schemas/menu.py` → pydantic (validation library, not infrastructure)
- `exceptions.py` → zero dependencies (pure Python)

### Risks

| Risk | Mitigation |
|------|------------|
| Spec names model `MenuItem` but schemas `Plato*` — confusing for future devs | Document naming rationale in model docstring |
| Custom `validate()` duplicates what Pydantic field validators could do | Intentional — Pydantic raises `ValidationError`, domain needs `InvalidMenuDataError`. Service layer calls `.validate()` explicitly. |
| Three exception classes in one file violates Rule 3 | Documented design decision — exception classes are domain infrastructure, each is 5–10 lines |

### Open Questions

- [ ] Should `PlatoResponse.validate()` remain a no-op, or is there no `validate()` at all on responses? Recommend no-op for interface consistency — all schemas are callable the same way.

---

## Phase 2: Repository Layer (MenuRepository)

### Technical Approach

Wrap SQLAlchemy async session operations behind a clean async interface. Repository returns domain models (`MenuItem`) and raises domain exceptions (`MenuNotFoundError`). Constructor injection of `AsyncSession` — no session creation, no engine knowledge. All five methods are `async def` (Rule 14), each ≤ 20 lines (Rule 8). Total: 5 public methods (Rule 9).

### Architecture Decisions

| Option | Tradeoff | Decision |
|--------|----------|----------|
| Constructor receives `AsyncSession` vs creates engine/session internally | Injection = testable, SRP; self-creation = coupled to config | **Constructor injection** — repo owns queries, not lifecycle |
| `update()` calls `self.get_by_id()` internally vs duplicates SELECT+error logic | Internal call = DRY, 5 lines saved; duplication = independent methods | **Internal call** — same class, not separate concerns |
| `model_dump(exclude_unset=True)` vs `exclude_none=True` for update payload | `exclude_unset` = only user-explicit fields; `exclude_none` = drops explicit None (breaks clearing nullable fields) | **exclude_unset** — correctly distinguishes "not provided" from "provided as None" |
| `session.flush()` vs `session.commit()` | Flush = writes visible in txn, caller controls commit; Commit = auto-commits | **Flush only** — repository doesn't own transaction boundary |
| Mock `AsyncSession` vs in-memory SQLite for unit tests | Mock = fast, isolated, pure unit test per Rule 11; real SQLite = slower, tests SQL not logic | **Mock via `unittest.mock.AsyncMock`** — integration tests with real DB belong in Phase 5 |
| `test/unit/repositories/__init__.py` vs no init | `__init__.py` causes namespace collision with `src/repositories/` when `pythonpath=["src"]` | **No `__init__.py`** — same pattern as `test/unit/core/` (Phase 1) |

### Sequence: Update (most complex flow)

```
Service ──► repo.update(plato_id=1, data=PlatoUpdate(nombre="Pizza"))
                │
                │  await self.get_by_id(1)
                │  ──► SELECT ... WHERE id=1 ──► MenuItem(id=1, nombre="Pasta", ...)
                │
                │  data.model_dump(exclude_unset=True)
                │  ──► {"nombre": "Pizza"}
                │
                │  setattr(existing, "nombre", "Pizza")
                │
                │  await session.flush()   ──► UPDATE menu_items SET nombre='Pizza' WHERE id=1
                │  await session.refresh(existing)
                │
                ◄── MenuItem(id=1, nombre="Pizza", precio=12.5, ...)
```

### File Changes

| File | Action | Description |
|------|--------|-------------|
| `src/repositories/__init__.py` | Create | Package init |
| `src/repositories/menu.py` | Create | `MenuRepository` — 5 async methods |
| `test/unit/repositories/test_menu_repository.py` | Create | Unit tests with mocked `AsyncSession` |

`test/unit/repositories/__init__.py` intentionally NOT created — avoids namespace collision with `src/repositories/` when `pythonpath=["src"]`.

### Interfaces

```python
from sqlalchemy.ext.asyncio import AsyncSession
from core.models.menu import MenuItem
from core.schemas.menu import PlatoCreate, PlatoUpdate

class MenuRepository:
    def __init__(self, session: AsyncSession) -> None: ...
    async def get_all(self) -> list[MenuItem]: ...
    async def get_by_id(self, plato_id: int) -> MenuItem: ...
    async def create(self, data: PlatoCreate) -> MenuItem: ...
    async def update(self, plato_id: int, data: PlatoUpdate) -> MenuItem: ...
    async def delete(self, plato_id: int) -> None: ...
```

**Method contracts:**
- `get_by_id`: `select(MenuItem).where(...)`, `scalar_one_or_none()`, raises `MenuNotFoundError(plato_id)` on None
- `create`: `data.model_dump()`, construct `MenuItem`, `session.add()`, `flush()` + `refresh()` to populate id
- `update`: calls `get_by_id()`, applies `data.model_dump(exclude_unset=True)` via `setattr()`, `flush()` + `refresh()`
- `delete`: calls `get_by_id()`, `session.delete(item)`, `session.flush()` (no refresh — row is gone)

### Testing Strategy

| Scenario | Mock Setup | Assertion |
|----------|-----------|-----------|
| `get_all` with items | `session.execute()` → `AsyncMock` with `scalars().all()` → `[item1, item2]` | Returns `list[MenuItem]` with 2 items |
| `get_all` empty | `scalars().all()` → `[]` | Returns empty list |
| `get_by_id` found | `session.execute()` → `scalar_one_or_none()` → `MenuItem` | Returns item with matching id |
| `get_by_id` missing | `scalar_one_or_none()` → `None` | `MenuNotFoundError(plato_id=99)`, `str(e)` matches |
| `create` | Mock `flush()` sets `item.id = 1`, mock `refresh()` no-op | Returns `MenuItem` with `id=1` and correct fields |
| `update` found | `get_by_id` returns `MenuItem(nombre="Pasta")`, data has `nombre="Pizza"` | Result has `nombre="Pizza"`, unchanged fields preserved |
| `update` missing | `get_by_id` → `MenuNotFoundError` | Exception propagates |
| `delete` found | `get_by_id` returns item | `session.delete(item)` called, no error |
| `delete` missing | `get_by_id` → `MenuNotFoundError` | Exception propagates |

All mocks use `unittest.mock.AsyncMock`. One test class per method group, `unittest.mock.patch` for constructor.

### Risks

| Risk | Mitigation |
|------|------------|
| `session.refresh()` on deleted row | `delete()` calls `flush()` but skips `refresh()` — row no longer exists |
| `exclude_unset` with `default=None` fields | `PlatoUpdate` fields default to `None`; only caller-passed fields appear in dump |
| `session.add()` on tracked object in `update()` | Not needed — fetched object is tracked; attribute mutation + `flush()` is sufficient |
| `flush()` vs `commit()` confusion for future devs | Docstring on `__init__` documents contract: "Repository flushes but never commits" |

### Dependencies

- `repositories/menu.py` → `core/models/menu.py` (MenuItem), `core/schemas/menu.py` (PlatoCreate/PlatoUpdate), `core/exceptions.py` (MenuNotFoundError), `sqlalchemy.ext.asyncio` (AsyncSession), `sqlmodel` (select)
- Zero dependency on FastAPI, HTTP, or any outer layer

### Open Questions

- None. All decisions resolved by spec + existing patterns.

---

## Phase 3: Service Layer (MenuService)

### Technical Approach

Business-logic orchestration between API and repository. Receives `MenuRepository` via constructor (DI). Enforces domain validation via polymorphic `data.validate()` before delegation on `create` and `update`. `get_all`, `get_by_id`, and `delete` are pass-through wrappers. Zero knowledge of HTTP, sessions, or transport. Total: ~55 source lines, 5 public methods, 1 constructor — all ≤ 20 lines each.

### Architecture Decisions

| Option | Tradeoff | Decision |
|--------|----------|----------|
| Service receives `MenuRepository` vs `AsyncSession` and builds repo internally | Injecting repo = testable, SRP; building internally = couples service to infrastructure config | **Inject `MenuRepository`** — service owns business rules, not object construction. Matches Phase 2 repo pattern. |
| Validation in API layer vs service layer | API = earlier rejection; Service = domain logic at application layer, HTTP-agnostic | **Service layer** — Rule 7 (business rules independent of frameworks). API translates exceptions, doesn't validate. |
| Catch domain errors and re-raise vs let propagate | Catch = could wrap with context; Propagate = simpler, uniform handling at API | **Let propagate** — API layer (Phase 4) is the single translation point for `DomainError` → HTTP status. |
| Mock `MenuRepository` directly vs mock `AsyncSession` for service tests | Mock repo = test service logic only (unit); Mock session = test repo+service together (integration) | **Mock `MenuRepository`** — Rule 11: service tests are unit tests with mocked repos. Integration tests belong in Phase 4–5. |

### Data Flow

```
API (Phase 4) ──► MenuService ──► MenuRepository ──► DB
                       │
                       ├── create/update: data.validate() then delegate
                       ├── get_all/get_by_id/delete: delegate directly
                       └── exceptions propagate up unchanged
```

### File Changes

| File | Action | Description |
|------|--------|-------------|
| `src/services/__init__.py` | Create | Package init (1 line) |
| `src/services/menu.py` | Create | `MenuService` — 5 async methods + constructor injection |
| `test/unit/services/test_menu_service.py` | Create | 12 unit tests with mocked `MenuRepository` |

`test/unit/services/__init__.py` intentionally NOT created — avoids `pythonpath=["src"]` namespace collision (same pattern as Phase 2 repositories).

### Interfaces

```python
from repositories.menu import MenuRepository
from core.models.menu import MenuItem
from core.schemas.menu import PlatoCreate, PlatoUpdate

class MenuService:
    def __init__(self, repository: MenuRepository) -> None: ...
    async def get_all(self) -> list[MenuItem]: ...
    async def get_by_id(self, plato_id: int) -> MenuItem: ...
    async def create(self, data: PlatoCreate) -> MenuItem: ...
    async def update(self, plato_id: int, data: PlatoUpdate) -> MenuItem: ...
    async def delete(self, plato_id: int) -> None: ...
```

**Method contracts:**
- `get_all` / `get_by_id` / `delete`: thin delegation — await repo method, return result. No transformation.
- `create`: calls `data.validate()` (polymorphic — raises `InvalidMenuDataError` on failure), then `await self._repository.create(data)`. Repo is NOT called on validation failure.
- `update`: calls `data.validate()`, then `await self._repository.update(plato_id, data)`. `MenuNotFoundError` from repo propagates unchanged.

### Testing Strategy

| Scenario | Mock Setup | Assertion |
|----------|-----------|-----------|
| `get_all` with items | `repo.get_all` → `[item1, item2]` | Returns same list, `repo.get_all` awaited once |
| `get_all` empty | `repo.get_all` → `[]` | Returns empty list |
| `get_by_id` found | `repo.get_by_id(1)` → `MenuItem` | Returns item |
| `get_by_id` missing | `repo.get_by_id(99)` → raises `MenuNotFoundError` | Exception propagates, `str(e)` matches spec |
| `create` valid | `PlatoCreate(nombre="Pasta", precio=12.5)` | `repo.create(data)` awaited, returns `MenuItem` |
| `create` empty nombre | `PlatoCreate(nombre="", precio=12.5)` | `InvalidMenuDataError("nombre", "is required.")`, `repo.create` NOT called |
| `create` zero precio | `PlatoCreate(nombre="Pasta", precio=0)` | `InvalidMenuDataError("precio", "must be positive.")`, `repo.create` NOT called |
| `update` valid | `PlatoUpdate(nombre="Pizza")` | `repo.update(1, data)` awaited, returns `MenuItem` |
| `update` invalid | `PlatoUpdate(nombre="")` | `InvalidMenuDataError`, `repo.update` NOT called |
| `update` missing | `repo.update(99, ...)` → raises `MenuNotFoundError` | Exception propagates |
| `delete` success | `repo.delete(1)` returns `None` | No error, `repo.delete` awaited once |
| `delete` missing | `repo.delete(99)` → raises `MenuNotFoundError` | Exception propagates |

Plus 3 static verification items (spec R7–R9): no FastAPI/HTTP imports in service module, all methods are typed `async def`, no method body exceeds 20 lines. Validated by `ruff` + `ty check` + manual review — no runtime tests needed.

**Test conventions** (matching `test/unit/repositories/test_menu_repository.py`):
- `unittest.mock.AsyncMock` for `MenuRepository`
- `@pytest.fixture` returning `AsyncMock(spec=MenuRepository)` as `mock_repo`
- `@pytest.fixture` returning `MenuService(mock_repo)` as `service`
- One test class per method group: `TestGetAll`, `TestGetById`, `TestCreate`, `TestUpdate`, `TestDelete`
- All test methods are `async def ... -> None`

### Dependencies

- `services/menu.py` → `repositories.menu` (MenuRepository), `core.schemas.menu` (PlatoCreate, PlatoUpdate), `core.models.menu` (MenuItem for return types), `core.exceptions` (InvalidMenuDataError for docs)
- Zero dependency on FastAPI, Starlette, HTTP, or async session management
- Depends outward on two layers (repositories + core) — one-way, no skipping (Rule 4)

### Risks

| Risk | Mitigation |
|------|------------|
| Service is ~55 lines — feels like unnecessary indirection for a course project | Intentional — Clean Architecture mandates layer separation (Rules 4, 7). Phase 4 API router will call this instead of repo directly. |
| Mock `repo.create` assertion after `pytest.raises` requires careful ordering | Use `mock_repo.create.assert_not_called()` inside the `pytest.raises` block or after catching the exception to verify repo was skipped |
| `test/unit/services/__init__.py` could be added accidentally | Gitignore doesn't cover it; document in design as "intentionally absent" (same as Phase 2 repo tests) |

### Open Questions

- None. All design decisions resolved by spec (9 requirements, 15 scenarios) plus existing Phase 1–2 patterns.

---

## Phase 4: API Router Layer

### Technical Approach

Replace inline menu endpoints (`main.py` lines 42–117) with a FastAPI `APIRouter`. Dependency injection via `deps.py` wires `AsyncSession` → `MenuRepository` → `MenuService` per request. Domain exceptions translate to HTTP status codes at the router level. Old inline routes remain in main.py until Phase 5 — tests for the new router use a standalone FastAPI app.

### Architecture Decisions

| Option | Tradeoff | Decision |
|--------|----------|----------|
| Router-level try/except vs global exception handler | Router-level = explicit, visible, no hidden middleware; Global = cleaner but requires app registration | **Router-level** — each endpoint explicitly translates its known errors. Simpler for course context. |
| Engine in deps.py vs extracted to core/config.py | Engine in deps = one less file, self-contained; Config module = reusable, typed settings | **Engine in deps.py** — `core/config.py` doesn't exist yet; deps.py is the only consumer. Extract later if needed. |
| `httpx.ASGITransport` vs `TestClient` for new tests | ASGITransport = async native, matches AGENTS.md target; TestClient = sync, matches existing tests | **`httpx.ASGITransport`** — new architecture, new test approach. Existing char tests keep `TestClient` for old routes. |
| Route coexistence: same prefix collision | Old `@app.get("/menu")` and new `APIRouter(prefix="/menu")` collide — first registered wins | **Router registered after old routes** — old routes shadow new ones in main.py. Router tested independently. Phase 5 removes old routes and reorders registration. |
| DB for integration tests: in-memory vs file | `:memory:` with aiosqlite breaks across connections; file-based = stable within same engine | **File-based** — `test_menu_refactored.db` in project root, gitignored via `*.db` pattern |

### Engine and Session Lifecycle

Module-level singleton engine in `deps.py`:

```python
import os
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./restaurante.db")
_engine = create_async_engine(DATABASE_URL, echo=False)

async def get_menu_service():
    async with AsyncSession(_engine) as session:
        repository = MenuRepository(session)
        yield MenuService(repository)
```

### Exception Translation Table

| Domain Exception | HTTP Status | Triggering Endpoints |
|-----------------|-------------|---------------------|
| `MenuNotFoundError` | 404 | GET/PUT/DELETE `/{plato_id}` |
| `InvalidMenuDataError` | 422 | POST `/`, PUT `/{plato_id}` |

### Data Flow

```
HTTP Request → FastAPI Router → Depends(get_menu_service)
                                      │
                    deps.py: AsyncSession(engine) per request
                                      │
                              MenuService(repository)
                                      │
                              MenuRepository(session) → SQLite
```

Test flow (new routes):

```
httpx.AsyncClient(transport=ASGITransport(app=test_app))
    └─ test_app.include_router(menu_router)
        └─ app.dependency_overrides[get_menu_service] → get_test_service(test_engine)
```

### File Changes

| File | Action | Description |
|------|--------|-------------|
| `src/api/__init__.py` | Create | Package init |
| `src/api/routers/__init__.py` | Create | Package init |
| `src/api/routers/menu.py` | Create | `menu_router` — APIRouter(prefix="/menu", tags=["Menú"]), 5 async handlers |
| `src/api/deps.py` | Create | Async engine (module-level), `get_menu_service()` dependency factory |
| `src/main.py` | Modify | Add `from api.routers.menu import menu_router` + `app.include_router(menu_router)` after old routes |
| `test/integration/test_menu_api_refactored.py` | Create | 11 async integration tests with `httpx.ASGITransport` + real SQLite |

### Interfaces

**Router endpoints** (`src/api/routers/menu.py`):

```python
router = APIRouter(prefix="/menu", tags=["Menú"])

@router.get("/", response_model=list[PlatoResponse])
async def list_menu(service: MenuService = Depends(get_menu_service)): ...

@router.post("/", response_model=PlatoResponse, status_code=201)
async def create_menu_item(data: PlatoCreate, service: MenuService = Depends(get_menu_service)): ...

@router.get("/{plato_id}", response_model=PlatoResponse)
async def get_menu_item(plato_id: int, service: MenuService = Depends(get_menu_service)): ...

@router.put("/{plato_id}", response_model=PlatoResponse)
async def update_menu_item(plato_id: int, data: PlatoUpdate, service: MenuService = Depends(get_menu_service)): ...

@router.delete("/{plato_id}", status_code=204)
async def delete_menu_item(plato_id: int, service: MenuService = Depends(get_menu_service)): ...
```

All handlers are `async def`, typed params, each body ≤ 7 lines (Rule 8). Dependencies: `src/api/routers/menu.py` → `src/api/deps.py` (get_menu_service), `src/core/schemas/menu.py`, `src/core/exceptions.py`. Layer chain: api → service → repository → core (Rule 4).

### Testing Strategy

| Scenario | Method | Assertions |
|----------|--------|------------|
| List empty | `GET /` | 200, `[]` |
| List populated | `GET /` after 2 POSTs | 200, 2 items with `id`, `nombre`, `precio` |
| Create valid | `POST /` with valid body | 201, `PlatoResponse` with assigned `id` |
| Create invalid | `POST /` with `nombre=""` | 422, detail contains `nombre` |
| Get existing | `GET /1` | 200, stored fields match |
| Get missing | `GET /999` | 404, detail contains `999` |
| Update existing | `PUT /1` with partial fields | 200, updated fields reflected |
| Update missing | `PUT /999` | 404 |
| Delete existing | `DELETE /1` | 204, empty body |
| Delete missing | `DELETE /999` | 404 |
| DI wiring | Call endpoint without override | 200 or 201, proves real service+repo+DB chain |

Test setup: `pytest_asyncio.fixture` creates `test_engine` (file-based), runs `SQLModel.metadata.create_all(test_engine)`, builds `test_app` with router + `dependency_overrides`. Teardown drops tables. One `httpx.AsyncClient` per test using `async with`.

### Risks

| Risk | Mitigation |
|------|------------|
| Route collision: old `/menu` and new `/menu` shadow each other | Register old routes first, new router second. Router is shadowed in main.py until Phase 5. Tests use standalone app — no collision. |
| `dependency_overrides` scope leaks across tests | Each test builds its own `test_app` instance via fixture — isolated |
| `httpx.ASGITransport` not in dev dependencies | `httpx` ships with FastAPI `[standard]` extra — already installed |
| Engine leak between tests | Fixture-scoped engine, `dispose()` in teardown |

### Open Questions

- None. All decisions resolved by spec (9 requirements, 11 scenarios) + existing Phase 1–3 patterns.

---

## Phase 5: Wire-Up — Remove Old Inline Routes

### Technical Approach

Cleanup phase: strip all menu inline code from `main.py`, update `test_menu_api.py` to exercise `main.app` with the new router, and purge test infrastructure tied to the removed `menu` global dict. Only 2 files modified, 0 deleted. `main.py` loses ~80 lines; test file gains async DB setup + dependency overrides. The `app.include_router(menu_router)` line (already present since Phase 4) becomes the sole `/menu` handler.

### Architecture Decisions

| Option | Tradeoff | Decision |
|--------|----------|----------|
| `TestClient` vs `httpx.ASGITransport` for migrated tests | `TestClient` = spec-literal, simpler API, no `pytest_asyncio` markers needed per test; `ASGITransport` = matches refactored tests, native async | **`TestClient`** — spec explicitly names it. Async DB setup via `pytest_asyncio.fixture(autouse=True)`, but test functions remain synchronous. |
| Override `get_menu_service` vs `get_db_session` in tests | Overriding `get_menu_service` replaces the whole chain; overriding `get_db_session` only replaces the session source | **Override `get_menu_service`** — one override point, same pattern as refactored tests, isolates the full DI tail |
| Remove `conftest.py` autouse fixture vs scope it to ordenes | No existing test exercises ordenes globally; fixture breaks on `from main import menu` | **Remove autouse fixture** — restore when ordenes tests are written |
| Move `include_router` position vs keep where it is | Moving groups router with app setup; keeping avoids unnecessary diff | **Keep current position** (line 123; becomes line ~40 after removals) — cosmetic change adds no value |
| Reuse refactored test scenarios vs write new ones | Refactored tests already cover 11 scenarios with `dependency_overrides` + real DB | **Port from refactored tests** — same fixture structure (engine, override, client), different app target (`main.app` instead of standalone) |

### Exception Translation (unchanged)

Domain exceptions already handled by `api/routers/menu.py`. No changes needed — router is the same, just reached through `main.app` now.

### File Changes

| File | Action | Description |
|------|--------|-------------|
| `src/main.py` | Modify | Remove `menu = {}` (L37), 5 inline menu handlers (L44–119). Keep `menu_router` import, `include_router`, root endpoint, CORS, `ordenes` dict + endpoints. ~80 lines removed. |
| `test/conftest.py` | Modify | Delete `from main import menu` and `reset_menu` autouse fixture (3 lines). No current test depends on it. |
| `test/test_main.py` | Modify | Delete `test_listar_menu_vacio` (6 lines). Keep `test_raiz` only. |
| `test/integration/test_menu_api.py` | Modify | Replace all content. New tests target `main.app` via `TestClient`, use `pytest_asyncio.fixture(autouse=True)` for DB lifecycle + `dependency_overrides`. ~140 lines total. |

### Testing Strategy (migrated test_menu_api.py)

| Scenario | Method | Assertions |
|----------|--------|------------|
| List empty | `GET /menu` | 200, `[]` |
| List populated | `GET /menu` after 2 POSTs | 200, 2 items, int IDs, correct fields |
| Create valid | `POST /menu` `{"nombre":"Pasta","precio":12.5}` | 201, `PlatoResponse` with int `id` |
| Create invalid (empty nombre) | `POST /menu` `{"nombre":""}` | 422, detail mentions `nombre` |
| Create invalid (zero precio) | `POST /menu` `{"nombre":"X","precio":0}` | 422, detail mentions `precio` |
| Get existing | `GET /menu/{id}` | 200, fields match |
| Get missing | `GET /menu/999` | 404, detail contains `999` |
| Update existing | `PUT /menu/{id}` partial fields | 200, updated fields; unset preserved |
| Update missing | `PUT /menu/999` | 404 |
| Delete existing | `DELETE /menu/{id}` | 204, empty body |
| Delete missing | `DELETE /menu/999` | 404 |
| Create extra fields | `POST /menu` with `{"nombre":"X","precio":1,"extra":"ignored"}` | 201, extra field silently dropped by Pydantic |
| DI wiring | Full chain without manual override | 201, proves `get_menu_service` → real DB |

**Fixture structure**:

- `pytest_asyncio.fixture(autouse=True)` creates `test_engine` (file-based SQLite), runs `create_all`, overrides `main.app.dependency_overrides[get_menu_service]` with a `get_test_service` that uses `test_engine`. Teardown drops tables + disposes engine + clears overrides.
- `@pytest.fixture` returns `TestClient(main.app)`.
- Test functions are synchronous — `TestClient` handles async endpoints internally.

### Risks

| Risk | Mitigation |
|------|------------|
| Removing `menu = {}` breaks `test/conftest.py` import | Updated in same commit — `conftest.py` loses autouse fixture |
| `test_menu_api.py` tests run against real DB if fixture somehow skipped | `autouse=True` on DB setup fixture — guaranteed before any test in file |
| `dependency_overrides` on `main.app` leaks to `test_main.py` | `test_main.py` doesn't use menu endpoints after this phase; overrides cleared in fixture teardown |
| Old `test_menu_api_refactored.py` becomes redundant | Not deleted per spec; candidate for future cleanup after Phase 5 passes |
| Ordenes endpoint `crear_orden` references `menu[plato_id]` (L161) | Ordenes code is UNCHANGED this phase. It still reads from `menu` dict which no longer exists for menu lookups — this will be addressed when ordenes is refactored |

### Open Questions

- None. All decisions resolved by spec (3 requirements, 5 scenarios) + existing Phase 1–4 infrastructure.
