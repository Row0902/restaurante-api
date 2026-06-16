# Design: Orders Refactor

## Technical Approach

Extract orders CRUD from `src/main.py` (lines 44–124) into Clean Architecture layers mirroring menu-refactor patterns. Key differences: two SQLModel tables (Orden + OrdenItem), cross-domain `MenuRepository` injection for price lookup, and polymorphic estado state machine. Bottom-up, test-first across 5 phases. Remove both `ordenes = {}` and `menu = {}` stubs after wire-up.

## Architecture Decisions

| Decision | Choice | Alternatives Rejected | Rationale |
|----------|--------|-----------------------|-----------|
| Cross-domain price lookup | `OrdenesService` receives `MenuRepository` directly | `MenuService` injection (adds unnecessary business logic coupling); API-level coordination (leaks business rules to HTTP layer) | Service orchestrates both repos. Single reason to change: order business rules include price resolution |
| Estado state machine | Base `EstadoOrden` with 5 polymorphic subclasses, each implementing `puede_transicionar_a(nuevo: str) -> bool` | If/elif chain in service (violates Rule 1); Enum with transition table (no polymorphic dispatch) | Rule 1 mandates polymorphic validation. Each estado owns its allowed transitions. String-to-class lookup via module-level dict — data-driven, not type-based |
| Estado classes file layout | All 6 classes in `src/core/estado_orden.py` | 5 separate files (Rule 3 purity — each is 5-8 lines, creates noise) | Same exception as schemas in menu-refactor: cohesive unit, spec-granted grouping |
| Model file grouping | `Orden` + `OrdenItem` in `src/core/models/orden.py` | Separate files per Rule 3 (two ~18-line classes) | Task brief specifies single model file; pragmatic for course scope. Relationship declared via `ForeignKey` stays local |
| `precio_unitario` snapshot | `OrdenItem.precio_unitario` frozen at order creation from `MenuRepository.get_by_id()` price | Live price lookup on every read (stale totals); DB-level computed column (adds SQL coupling) | Snapshot ensures order integrity: menu price changes don't retroactively alter existing orders |
| Route coexistence | Old inline routes stay in `main.py` until Phase 5; new `orden_router` tested independently via standalone `FastAPI` app | Delete old routes first (risks breaking existing tests mid-refactor); test against main.app with overrides (route collision) | Proven menu-refactor pattern. No collision during dev; standalone app gives clean isolation |
| Test client style | Phase 4 integration tests use `httpx.ASGITransport` (async native); Phase 5 migration to `TestClient` per menu pattern | All `TestClient` (sync — chokes on async session lifecycle without `pytest_asyncio`); all `ASGITransport` (adds `pytest_asyncio` markers) | New architecture, new test approach. Migration follows menu pattern in Phase 5 |
| `menu = {}` stub removal | Remove in Phase 5 after `OrdenesService` uses `MenuRepository` | Keep indefinitely (dead code); remove early (breaks inline ordenes handlers still reading it) | Stub was only kept because `POST /ordenes` read it. After refactor, zero consumers remain |

## Data Flow: Order Creation

```
POST /ordenes  ──► orden_router.create_order()
                      │
                      └──► OrdenesService.create(data)
                              │
                              ├── data.validate()
                              ├── for each item:
                              │     menu_repo.get_by_id(plato_id) ──► MenuItem
                              │     build OrdenItem(precio_unitario=menu_item.precio)
                              ├── total = Σ(cantidad × precio_unitario)
                              ├── build Orden(estado="pendiente", total=...)
                              └── orden_repo.create(data, items) ──► Orden (with id)
```

## File Changes

| File | Action | Est. Lines | Description |
|------|--------|-----------|-------------|
| `src/core/models/orden.py` | Create | 35 | `Orden` (table=`ordenes`) + `OrdenItem` (table=`orden_items`, FK→ordenes) |
| `src/core/schemas/orden.py` | Create | 60 | `OrdenItemData`, `OrdenCreate`, `OrdenUpdateEstado`, `OrdenResponse` — each with own `validate()` |
| `src/core/estado_orden.py` | Create | 45 | `EstadoOrden` base + `Pendiente`/`Preparando`/`Entregado`/`Pagado`/`Cancelado` subclasses |
| `src/core/exceptions.py` | Modify | +24 | ADD `OrdenNotFoundError`, `InvalidOrdenDataError`, `InvalidEstadoTransitionError` |
| `src/repositories/orden.py` | Create | 80 | `OrdenRepository` — 5 async CRUD methods with line item handling |
| `src/services/orden.py` | Create | 80 | `OrdenesService(orden_repo, menu_repo)` — create (price lookup + total), cambiar_estado, get_all, get_by_id |
| `src/api/routers/orden.py` | Create | 55 | `APIRouter(prefix="/ordenes")` — 4 endpoints: GET list, POST create, GET by id, PUT estado |
| `src/api/deps.py` | Modify | +20 | ADD `get_orden_service()` factory: `AsyncSession` → both repos → `OrdenesService` |
| `src/main.py` | Modify | −85 | Remove `menu = {}`, `ordenes = {}`, 4 inline handlers (lines 36–124). Add `include_router(orden_router)` |
| `test/unit/core/test_orden_model.py` | Create | 50 | Model instantiation, defaults, `__tablename__` |
| `test/unit/core/test_orden_schemas.py` | Create | 70 | Validation: empty items, zero cantidad, invalid estado, valid payloads |
| `test/unit/core/test_orden_estado.py` | Create | 55 | All transitions (valid + invalid), terminal states reject changes |
| `test/unit/repositories/test_orden_repository.py` | Create | 130 | Mocked `AsyncSession`: CRUD with line items, 404 propagation |
| `test/unit/services/test_orden_service.py` | Create | 150 | Mocked `OrdenRepository` + `MenuRepository`: create with price lookup, invalid items, estado transitions |
| `test/integration/test_orden_api.py` | Create | 160 | `httpx.ASGITransport` + standalone app: 10 scenarios per API spec |
| `test/integration/test_menu_api.py` | Verify | 0 | Ensure existing tests still pass after `menu = {}` removal |

**Total**: ~520 new + ~85 removed = ~605 changed lines. Chained PRs recommended (see risks).

## Testing Strategy

| Layer | What to Test | Approach | Count |
|-------|-------------|----------|-------|
| Core unit | Models: field defaults, `__tablename__`, FK relationships | Direct instantiation | ~5 |
| Core unit | Schemas: `validate()` raises correct exceptions on invalid input | Construct + call `.validate()` | ~8 |
| Core unit | Estado: all 8 valid transitions pass; 8+ invalid transitions raise `InvalidEstadoTransitionError` | Instantiate estado subclass, call `puede_transicionar_a` | ~7 |
| Core unit | Exceptions: `str(e)` formatting, hierarchy | Raise + catch, assert message | ~6 |
| Repo unit | CRUD with mocked `AsyncSession`: create with items, get_all with items, 404 on missing | `AsyncMock(spec=AsyncSession)` | ~9 |
| Service unit | Mocked `OrdenRepository` + `MenuRepository`: create with price calc, invalid items, estado transitions, MenuNotFoundError propagation | `AsyncMock(spec=OrdenRepository)`, `AsyncMock(spec=MenuRepository)` | ~12 |
| API integration | All 10 spec scenarios: 200/201/204/400/404/422 status codes, JSON bodies | `httpx.ASGITransport` + real SQLite | 10 |
| Regression | Existing menu tests still pass after stub removal | `pytest test/integration/test_menu_api.py` | 13 |

**Total new tests**: ~45 across 6 test files. Target coverage: ≥80% on all new `src/` files.

## Risks

| Risk | Mitigation |
|------|------------|
| ~605 changed lines exceeds 400-line review budget | Chained PRs: PR1 (Phase 1, ~250 lines), PR2 (Phases 2–3, ~210 lines), PR3 (Phases 4–5, ~145 lines). Each PR autonomous, testable, independently verifiable. |
| Estado polymorphic dispatch: string-to-class mapping feels like an enum | Documented as data-driven lookup, not type-based branching. Validation IS polymorphic — each subclass owns its rules. |
| `menu = {}` removal breaks inline `POST /ordenes` handler (line 79 reads `menu[plato_id]`) | Inline handlers removed in same commit as stub removal (Phase 5). Zero window where stub is deleted but handler exists. |
| `precio_unitario` snapshot vs live price semantic difference | Spec explicitly states: snapshot at creation time. No behavioral change from current code (price read at creation moment). Future menu edits don't affect existing orders — intentional benefit. |
| Menu items not seeded before `POST /ordenes` integration tests | Test fixture seeds menu items via HTTP before creating orders (same pattern as `test_menu_api_refactored.py`). |

## Open Questions

- None. All decisions resolved by specs (17 requirements, 27 scenarios across 4 domains) + existing menu-refactor patterns.
