# Proposal: Orders Refactor

## Intent

Extract orders CRUD from monolithic `main.py` (lines 44–124) into Clean Architecture layers. Remove the `menu = {}` stub (kept only because `POST /ordenes` reads it for prices — OrdenesService will use MenuRepository instead).

## Scope

### In Scope
- Core models (`Orden`, `OrdenItem`), schemas (`OrdenCreate`, `OrdenUpdateEstado`, `OrdenItemData`, `OrdenResponse`), domain exceptions
- `OrdenRepository` — async CRUD with line items
- `OrdenesService` — business logic with cross-domain `MenuRepository` injection for price lookup
- `APIRouter(prefix="/ordenes")` — 4 endpoints (GET list, POST create, GET by id, PUT estado)
- `deps.py` wiring — `get_orden_service()` factory
- Remove `menu = {}` and `ordenes = {}` stubs + inline handlers from `main.py`
- Characterization tests first (pin current behavior), then tests per layer
- Estado state machine with polymorphic validation (Rule 1)

### Out of Scope
- Authentication, user management, payment, reporting
- Async migration of existing menu tests
- MenuItem domain changes (read-only consumption via existing `MenuRepository.get_by_id`)

## Capabilities

### New Capabilities
- `core/orden`: Orden/OrdenItem SQLModel, Pydantic schemas with polymorphic validate(), domain exceptions
- `repositories/orden`: OrdenRepository — async CRUD for orders + line items
- `services/orden`: OrdenesService — total calculation, estado transitions, MenuRepository injection
- `api/orden`: APIRouter(prefix="/ordenes"), exception translation

### Modified Capabilities
- None: MenuRepository interface unchanged (`get_by_id` already exists), MenuService not consumed

## Approach

Bottom-up, test-first, 6 phases mirroring menu-refactor:

| Phase | Focus | Est. Tasks |
|-------|-------|-----------|
| 0 | Characterization tests (pin current inline behavior) | 4 |
| 1 | Core models, schemas, exceptions | 5 |
| 2 | OrdenRepository (async, line items) | 4 |
| 3 | OrdenesService + MenuRepository injection | 5 |
| 4 | API router + deps.py wiring | 4 |
| 5 | main.py cleanup — remove stubs + inline handlers | 4 |

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `src/core/models/orden.py` | New | Orden + OrdenItem SQLModel tables |
| `src/core/schemas/orden.py` | New | Input/output Pydantic schemas |
| `src/core/exceptions.py` | Modified | Add OrdenNotFoundError, InvalidOrdenDataError |
| `src/repositories/orden.py` | New | Async CRUD with line item persistence |
| `src/services/orden.py` | New | Business logic + MenuRepository injection |
| `src/api/routers/orden.py` | New | 4 endpoints |
| `src/api/deps.py` | Modified | Add get_orden_service() |
| `src/main.py` | Modified | Remove stubs + inline handlers (lines 36–124) |
| Test files (6 new) | New | Unit (core, repo, service) + integration |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Cross-domain coupling (menu → orders) | Med | Inject MenuRepository directly (no circular dep) |
| Estado polymorphic validation complexity | Med | Each estado variant validates own transitions |
| `menu = {}` removal breaks if missed ref | Low | Verify no remaining references before removal |
| ~600+ lines exceeds 400-line review budget | High | Chained PRs: Phase 0–1 → 2–3 → 4–5 |

## Rollback Plan

- Before merging: keep old `main.py` inline handlers and stubs (guard with version flag or simply preserve until last PR)
- Per PR: no PR merges unless all existing tests pass
- If wire-up fails: revert last PR, restore inline handlers, investigate

## Dependencies

- `MenuRepository.get_by_id()` — must exist (already does from menu-refactor)
- Menu items must be seeded in DB before `POST /ordenes` can calculate totals

## Success Criteria

- [ ] All ~80 existing tests still pass (no regressions)
- [ ] New tests ≥ 20 across all layers with ≥ 80% coverage on new code
- [ ] `menu = {}` and `ordenes = {}` stubs removed without breakage
- [ ] All 4 endpoints behave identically to original inline handlers
- [ ] Estado state machine rejects invalid transitions with proper error

## Size Forecast

~650–700 new + modified lines. Exceeds 400-line review budget. Recommend 3 chained PRs:
- PR 1: Phase 0–1 (char tests + core) — ~200 lines
- PR 2: Phase 2–3 (repo + service) — ~280 lines
- PR 3: Phase 4–5 (api + clean-up) — ~200 lines
