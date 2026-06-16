# Tasks: Menu Refactor

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | ~200 (Phase 4 — 6 files) |
| 400-line budget risk | Low |
| Chained PRs recommended | No |
| Suggested split | Single PR |
| Delivery strategy | ask-always |
| Chain strategy | stacked-to-main |

Decision needed before apply: No
Chained PRs recommended: No
Chain strategy: stacked-to-main
400-line budget risk: Low

### Suggested Work Units

| Unit | Goal | Likely PR | Notes |
|------|------|-----------|-------|
| 1 | API router + deps + tests | Same PR | Single coherent slice — all 5 handlers, DI, and 11 integration tests. ~200 lines total, no split needed. |

## Phase 0: Characterization Tests — VERIFIED ✅

All 22 tasks complete, 20/20 tests pass, lint clean. See `verify-report.md`.

## Phase 1: Package Scaffolding

- [x] 1.1 Create `src/core/__init__.py` — empty package init
- [x] 1.2 Create `src/core/models/__init__.py` — empty package init
- [x] 1.3 Create `src/core/schemas/__init__.py` — empty package init
- [x] 1.4 Create `test/unit/core/__init__.py` — *removed after creation* (caused namespace collision with `src/core/` when pytest puts `test/unit` on sys.path)

## Phase 2: Domain Exceptions (TDD)

- [x] 2.1 RED: Write `test/unit/core/test_exceptions.py` — 9 tests, 3 classes (DomainError hierarchy, MenuNotFoundError, InvalidMenuDataError)
- [x] 2.2 GREEN: Create `src/core/exceptions.py` — `DomainError(Exception)`, `MenuNotFoundError(DomainError)`, `InvalidMenuDataError(DomainError)` with `(field, message)` constructor

## Phase 3: MenuItem Model (TDD)

- [x] 3.1 RED: Write `test/unit/core/test_menu_model.py` — 7 tests (inheritance, tablename, instantiation, optional fields, table config, all fields)
- [x] 3.2 GREEN: Create `src/core/models/menu.py` — `MenuItem(SQLModel, table=True)` with `id`, `nombre`, `precio`, `categoria?`, `descripcion?`

## Phase 4: Pydantic Schemas (TDD)

- [x] 4.1 RED: Write `test/unit/core/test_menu_schemas.py` — 13 tests (PlatoCreate validation x5, PlatoUpdate validation x5, PlatoResponse serialization x3)
- [x] 4.2 GREEN: Create `src/core/schemas/menu.py` — `PlatoCreate`, `PlatoUpdate`, `PlatoResponse` each with own `validate()` raising `InvalidMenuDataError`; `PlatoResponse` uses `model_config = {"from_attributes": True}`

## Phase 5: Verification

- [x] 5.1 Run `pytest -v test/unit/core/` — 29/29 core tests pass
- [x] 5.2 Run `ruff check src/core/ test/unit/core/` — clean (added D107 docstrings to `__init__` methods)
- [x] 5.3 Run `ty check src/core/ test/unit/core/` — clean (added `# type: ignore` for `validate()` override and `__table__` dynamic attr)

---

## Phase 6: Repository Package Scaffolding

- [x] 6.1 Create `src/repositories/__init__.py` — empty package init

## Phase 7: Repository Tests — RED (TDD)

- [x] 7.1 RED: Write `test/unit/repositories/test_menu_repository.py` — `AsyncMock` for `AsyncSession`, no `__init__.py` in test dir (namespace collision guard). 9 tests across 5 groups:
  - `TestGetAll`: returns items, returns `[]` when empty
  - `TestGetById`: returns `MenuItem` when found, raises `MenuNotFoundError(99)` when missing
  - `TestCreate`: returns `MenuItem` with `id=1` and correct field values
  - `TestUpdate`: partial update preserves unset fields via `exclude_unset=True`, raises `MenuNotFoundError` when missing
  - `TestDelete`: completes without error, raises `MenuNotFoundError` when missing

## Phase 8: Repository Implementation — GREEN

- [x] 8.1 GREEN: Create `src/repositories/menu.py` — `MenuRepository` with `__init__(session: AsyncSession)` + 5 async methods:
  - `get_all` → `select(MenuItem)`, `execute()`, `scalars().all()`
  - `get_by_id` → `select(...).where(...)`, `scalar_one_or_none()`, raises `MenuNotFoundError(plato_id)` on None
  - `create` → `data.model_dump()`, construct `MenuItem`, `session.add()`, `flush()` + `refresh()`
  - `update` → calls `self.get_by_id()`, applies `data.model_dump(exclude_unset=True)` via `setattr()`, `flush()` + `refresh()`
  - `delete` → calls `self.get_by_id()`, `session.delete()`, `flush()`

## Phase 9: Repository Verification

- [x] 9.1 Run `pytest -v test/unit/repositories/` — 9/9 tests pass
- [x] 9.2 Run `ruff check src/repositories/ test/unit/repositories/` — clean
- [x] 9.3 Run `ty check src/repositories/ test/unit/repositories/` — clean

---

## Phase 10: Service Package Scaffolding

- [x] 10.1 Create `src/services/__init__.py` — empty package init

## Phase 11: Service Tests — RED (TDD)

- [x] 11.1 RED: Write `test/unit/services/test_menu_service.py` — `AsyncMock` for `MenuRepository`, no `__init__.py` in test dir. 12 tests across 5 groups:
  - `TestGetAll`: returns items unchanged, returns `[]` when empty
  - `TestGetById`: returns `MenuItem` when found, propagates `MenuNotFoundError(99)` when missing
  - `TestCreate`: valid data → `repo.create(data)` awaited once; empty nombre → `InvalidMenuDataError("nombre", ...)`, repo NOT called; zero precio → `InvalidMenuDataError("precio", ...)`, repo NOT called
  - `TestUpdate`: valid partial → `repo.update(1, data)` awaited; empty nombre → `InvalidMenuDataError`, repo NOT called; missing item → `MenuNotFoundError` propagates
  - `TestDelete`: existing item → `repo.delete(1)` awaited once; missing item → `MenuNotFoundError` propagates

## Phase 12: Service Implementation — GREEN

- [x] 12.1 GREEN: Create `src/services/menu.py` — `MenuService` with `__init__(self, repository: MenuRepository) → None` + 5 async methods:
  - `get_all` → `await self._repository.get_all()`, return unchanged
  - `get_by_id` → `await self._repository.get_by_id(plato_id)`, let `MenuNotFoundError` propagate
  - `create` → call `data.validate()` (raises `InvalidMenuDataError` on failure), then `await self._repository.create(data)`
  - `update` → call `data.validate()`, then `await self._repository.update(plato_id, data)`, let `MenuNotFoundError` propagate
  - `delete` → `await self._repository.delete(plato_id)`, let `MenuNotFoundError` propagate

## Phase 13: Service Verification

- [x] 13.1 Run `pytest -v test/unit/services/` — 12/12 tests pass
- [x] 13.2 Run `pytest -v --cov=src --cov-report=term-missing` — coverage ≥ 80%
- [x] 13.3 Run `ruff check src/services/ test/unit/services/` — clean (check no fastapi/starlette imports in service layer)
- [x] 13.4 Run `ty check src/services/ test/unit/services/` — clean

---

## Phase 14: API Package Scaffolding

- [x] 14.1 Create `src/api/__init__.py` — empty package init
- [x] 14.2 Create `src/api/routers/__init__.py` — empty package init

## Phase 15: API Router Implementation

- [x] 15.1 Create `src/api/deps.py` — module-level async engine from `DATABASE_URL`, `get_menu_service()` async generator: `async with AsyncSession(_engine)` → `MenuRepository(session)` → `MenuService(repository)`, yield service. Added `commit()` after yield for transaction boundary (required for multi-request visibility).
- [x] 15.2 Create `src/api/routers/menu.py` — `APIRouter(prefix="/menu", tags=["Menú"])` with 5 async handlers; each catches `MenuNotFoundError` → `HTTPException(404)`, `InvalidMenuDataError` → `HTTPException(422)`. Handlers: `list_menu` (GET /), `create_menu_item` (POST /, 201), `get_menu_item` (GET /{plato_id}), `update_menu_item` (PUT /{plato_id}), `delete_menu_item` (DELETE /{plato_id}, 204). All ≤ 7 lines body.
- [x] 15.3 Modify `src/main.py` — add `from api.routers.menu import router as menu_router` + `app.include_router(menu_router)` after old menu routes (line 117), before ordenes section

## Phase 16: Integration Tests

- [x] 16.1 Write `test/integration/test_menu_api_refactored.py` — `httpx.ASGITransport`, file-based SQLite, `pytest_asyncio.fixture` for engine/app/client lifecycle (create_all on setup, drop tables + dispose on teardown, `dependency_overrides[get_menu_service]` with test engine). 11 async tests covering: list empty (200, []), list populated (200, 2 items), create valid (201), create invalid (422), get existing (200), get missing (404), update existing (200), update missing (404), delete existing (204, empty body), delete missing (404), DI wiring (real chain returns 200/201)

## Phase 17: Verification

- [x] 17.1 Run `pytest -v test/integration/test_menu_api_refactored.py` — 11/11 pass
- [x] 17.2 Run `pytest -v --cov=src --cov-report=term-missing` — coverage ≥ 80% (actual: 88%)
- [x] 17.3 Run `ruff check src/api/ test/integration/test_menu_api_refactored.py --fix` — clean
- [x] 17.4 Run `ty check src/api/ test/integration/test_menu_api_refactored.py` — clean

---

## Phase 18: Strip Inline Menu Code from main.py (TDD)

- [x] 18.1 RED: Write tests ordering contract — prove that after removing inline handlers, `GET /menu` routes to the new `menu_router` (by asserting 404 or expected behavior), and `POST /ordenes` with valid `menu[plato_id]` stub still works for the stub dict access pattern.
- [x] 18.2 GREEN: Remove inline menu handlers from `src/main.py` — delete lines 39–119 (`# --- MENU ---` section through `app.include_router` line). Keep `menu = {}` on line 37 as a bare stub for `POST /ordenes` compatibility. Keep the `app.include_router(menu_router)` call (line 123). Orderes endpoints (lines 126–206) remain unchanged. Net: ~77 lines removed.
- [x] 18.3 Verify: `GET /menu` returns 200 through the new router (no duplicate route collision), `GET /ordenes` returns 200 unchanged, `GET /` returns 200 root endpoint.

## Phase 19: Remove Obsolete Test Fixtures and Tests (TDD)

- [x] 19.1 RED: Write tests proving `test_main.py` root endpoint works without `test_listar_menu_vacio` — the remaining `test_raiz` is the only test needed.
- [x] 19.2 GREEN: Modify `test/conftest.py` — delete `from main import menu` import (line 5) and the `reset_menu` autouse fixture (lines 8–11). No other test depends on this fixture.
- [x] 19.3 GREEN: Modify `test/test_main.py` — delete `test_listar_menu_vacio` function (lines 17–21). Keep only `test_raiz`.
- [x] 19.4 Verify: `pytest -v test/test_main.py` — 1/1 test passing (`test_raiz`). `pytest -v -k "reset_menu"` — no tests collected (fixture gone).

## Phase 20: Migrate Integration Tests to New Router via main.app (TDD)

- [x] 20.1 RED: Write `test/integration/test_menu_api.py` — rewrite file contents targeting `main.app` with `TestClient`, using `pytest_asyncio.fixture(autouse=True, scope="function")` for DB lifecycle: create test engine, `SQLModel.metadata.create_all`, override `main.app.dependency_overrides[get_menu_service]` with test-DI that uses test engine. Fixture teardown drops tables, disposes engine, clears overrides.
- [x] 20.2 RED: Write 13 sync test functions through `TestClient(main.app)` — cover: list empty, list populated, create valid (201, int id), create invalid empty nombre (422), create invalid zero precio (422), get existing (200), get missing (404), update existing (200), update missing (404), delete existing (204, empty body), delete missing (404), create extra fields silently dropped (201), DI wiring full chain (201).
- [x] 20.3 GREEN: Run `pytest -v test/integration/test_menu_api.py` — 13/13 tests pass. Verify all old-behavior assertions (string IDs, `KeyError`, print checks, `mensaje` in delete, full-replace PUT, create-on-missing PUT) are gone.
- [x] 20.4 Verify: `test_menu_api_refactored.py` still exists (candidate for future cleanup, not removed yet).

## Phase 21: Wire-Up Verification

- [x] 21.1 Run `pytest -v test/integration/` — 24/24 tests pass (11 refactored + 13 migrated).
- [x] 21.2 Run `pytest -v test/` — all tests pass (unit + integration + root).
- [x] 21.3 Run `pytest -v --cov=src --cov-report=term-missing` — coverage ≥ 80%.
- [x] 21.4 Run `ruff check src/ test/ --fix` — clean.
- [x] 21.5 Run `ty check src/ test/` — clean.
- [x] 21.6 Verify `menu = {}` exists as stub in `main.py` (no handlers attached). Confirm `POST /ordenes` stub path is documented as known limitation — addressed in future ordenes refactor.
