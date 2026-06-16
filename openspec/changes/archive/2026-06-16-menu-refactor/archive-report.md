# Archive Report — Menu Refactor

**Archived at**: 2026-06-16
**Change**: menu-refactor
**Archive path**: `openspec/changes/archive/2026-06-16-menu-refactor/`

## Summary

Successfully extracted the menu endpoint from monolithic `src/main.py` into Clean Architecture layers:
`api/ → services/ → repositories/ → core/`. All 21 task phases completed with 80/80 tests passing,
86% coverage (above 80% threshold), clean lint and type checks.

## Verification Outcome

**PASS WITH WARNINGS** — No CRITICAL issues. One known deviation: `menu = {}` stub retained
for `POST /ordenes` compatibility (documented, resolved in future orders refactor).

## Specs Synced to Source of Truth

| Domain | Action | Details |
|--------|--------|---------|
| `core/menu` | Created | SQLModel model, Pydantic schemas (PlatoCreate/Update/Response), domain exceptions — 9 requirements, 14 scenarios |
| `repositories/menu` | Created | MenuRepository with 5 async CRUD methods — 1 requirement, 9 scenarios |
| `services/menu` | Created | MenuService with constructor injection, polymorphic validation — 8 requirements, 15 scenarios |
| `api/menu` | Created | APIRouter with 5 handlers, DI factory, domain exception translation — 9 requirements, 11 scenarios |

## Archive Contents

- `proposal.md` ✅ — Intent, scope, approach, risks, rollback plan
- `specs/` ✅ — 6 phase specs (phase-0 through wire-up)
- `design.md` ✅ — Technical design with architecture decisions per layer
- `tasks.md` ✅ — 21 phases, all tasks marked complete
- `verify-report.md` ✅ — Full compliance matrix, TDD audit, coverage report
- `archive-report.md` ✅ — This file

## Phase Summary

| Phase | Description | Status |
|-------|-------------|--------|
| Phase 0 | Characterization tests | ✅ 18 tests passed |
| Phase 1 | Core domain (model, schemas, exceptions) | ✅ 29 tests, 100% coverage |
| Phase 2 | Repository layer (MenuRepository) | ✅ 9 tests, 100% coverage |
| Phase 3 | Service layer (MenuService) | ✅ 12 tests, 100% coverage |
| Phase 4 | API router + DI + integration tests | ✅ 11 async integration tests |
| Phase 5 | Wire-up, cleanup, migration | ✅ 13 migrated + root tests |

## Designs Enforced

- Bottom-up incremental build (core → repo → service → api → wire-up)
- Polymorphic validation: each schema has own `validate()`, no `if`/`match` on type
- Constructor injection through all layers
- `flush()` not `commit()` in repository; commit owned by deps.py
- Router-level try/except for domain exception → HTTP translation
- `TestClient` for migrated tests, `httpx.ASGITransport` for refactored
- File-based SQLite for test isolation

## SDD Cycle Complete

The menu-refactor change has been fully planned, proposed, specified, designed,
implemented (strict TDD), verified, and archived. Ready for the next change.
