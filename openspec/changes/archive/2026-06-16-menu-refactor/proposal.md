# Proposal: Menu Refactor

## Intent

Extract menu endpoint (lines 42–117) from monolithic `src/main.py` into Clean Architecture layers (`api/ → services/ → repositories/ → core/`). Zero of 15 design rules are satisfied for menu — this is the first incremental step toward the target architecture.

## Scope

### In Scope
- Core: SQLModel model (Plato), Pydantic schemas (create/update/response), domain exceptions
- Repository: protocol + in-memory implementation (replacing global `menu = {}`)
- Service: CRUD business logic
- API: FastAPI router with 5 endpoints (list, create, get, update, delete)
- Characterization tests (Phase 0) + layer-specific unit + integration tests
- Keep `menu = {}` working until router is wired in

### Out of Scope
- Ordenes endpoint (future change)
- SQLite/async DB setup with SQLModel engine
- Async migration — sync domain first, async comes later explicitly
- DI framework — manual wiring via `FastAPI.dependency` only
- Authentication, validation polymorphism

## Capabilities

### New Capabilities
- `menu-management`: CRUD operations on menu items — create, read, update, delete, list

### Modified Capabilities
- None (first spec-level capability in the project)

## Approach

Bottom-up, incremental, test-first:

| Phase | Layer | Output |
|-------|-------|--------|
| 0 | Tests | Characterization tests capturing current behavior (pinning existing bugs) |
| 1 | `core/` | Plato model, schemas, exceptions — no dependencies on other layers |
| 2 | `repositories/` | MenuRepository protocol + InMemoryMenuRepository |
| 3 | `services/` | MenuService — business rules, receives repo via constructor |
| 4 | `api/` | MenuRouter — FastAPI APIRouter with 5 endpoints |
| 5 | Wire | Import and include router in `main.py`, remove old menu code |

Each phase includes its own tests before implementation code.

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `src/core/models/` | New | Plato SQLModel model |
| `src/core/schemas/` | New | Create/Update/Response Pydantic schemas |
| `src/core/exceptions/` | New | Domain exceptions (PlatoNotFound, etc.) |
| `src/repositories/` | New | MenuRepository protocol + InMemory impl |
| `src/services/` | New | MenuService CRUD |
| `src/api/` | New | MenuRouter with 5 endpoints |
| `src/main.py` | Modified | ~15 lines — import + include router, remove menu code |
| `test/` | New | Characterization + unit + integration tests (~6 files) |
| `test/test_main.py` | Modified | Menu tests migrate to new router tests |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Global `menu = {}` leaks between tests | High | Fixture-level reset in conftest — clear dict before each test |
| Behavior drift during extraction | Medium | Characterization tests (Phase 0) pin exact current responses |
| 1-class-per-file rule creates many files | Medium | Accept file count — it's a course constraint |
| Size exceeds review budget (400 lines) | High | Split: Phase 0 alone, then Phases 1–4 as a second chunk |

## Rollback Plan

1. Revert `src/main.py` — remove router include, restore old menu code
2. Delete new directories (`src/core/`, `src/repositories/`, `src/services/`, `src/api/`)
3. Revert test changes and new test files
4. Global `menu = {}` continues working — no data loss risk

## Dependencies

- None (first change, no existing layers to depend on)
- Characterization tests depend only on current `main.py` behavior

## Success Criteria

- [ ] All existing tests pass after refactor (behavior preserved)
- [ ] Characterization tests match original endpoint responses exactly
- [ ] Each layer testable in isolation (repo tests without API, service tests without HTTP)
- [ ] Coverage ≥ 80% on new `src/` code
- [ ] `ruff check --fix` and `ty check` pass on all new code
- [ ] `menu = {}` no longer referenced outside `repositories/`
