# Tasks: Orders Refactor — 3 Chained PRs

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | ~605 total (new + modified) |
| 400-line budget risk | High |
| Chained PRs recommended | Yes |
| Suggested split | PR 1 (~250) → PR 2 (~210) → PR 3 (~145) |
| Delivery strategy | ask-on-risk |
| Chain strategy | stacked-to-main |

Decision needed before apply: Yes
Chained PRs recommended: Yes
Chain strategy: stacked-to-main
400-line budget risk: High

### Suggested Work Units

| Unit | Goal | Likely PR | Notes |
|------|------|-----------|-------|
| 1 | Core domain + char tests | PR 1 → main | Models, schemas, estado machine, exceptions, unit tests. Base for all layers. |
| 2 | Repository + Service | PR 2 → main | OrdenRepository CRUD, OrdenesService with MenuRepository injection. Tests with mocks. |
| 3 | API + Wire-up + Cleanup | PR 3 → main | Router, deps, remove inline handlers + stubs from main.py. Integration tests + regression. |

---

## PR 1: Core Domain (~250 lines)

### Phase 1: Core Models, Schemas & Exceptions

- [x] 1.1 Add `OrdenNotFoundError(orden_id)`, `InvalidOrdenDataError(field, message)`, `InvalidEstadoTransitionError(from_estado, to_estado)` to `src/core/exceptions.py`
- [x] 1.2 Create `src/core/models/orden.py` — `Orden` (table `ordenes`) with FK relationship to `OrdenItem` (table `orden_items`, FK→ordenes, `precio_unitario` snapshot)
- [x] 1.3 Create `src/core/schemas/orden.py` — `OrdenItemData`, `OrdenCreate`, `OrdenUpdateEstado`, `OrdenResponse` each with polymorphic `validate()`
- [x] 1.4 Create `src/core/estado_orden.py` — base `EstadoOrden` + `Pendiente`/`Preparando`/`Entregado`/`Pagado`/`Cancelado` subclasses, string-to-class lookup dict (spec-granted grouping)
- [x] 1.5 Write `test/unit/core/test_orden_model.py` — `__tablename__`, defaults, FK wiring, line item snapshot
- [x] 1.6 Write `test/unit/core/test_orden_schemas.py` — empty items, zero cantidad, invalid estado, valid payloads
- [x] 1.7 Write `test/unit/core/test_orden_estado.py` — 8 valid transitions + 8+ invalid, terminal states reject all
- [x] 1.8 Write `test/unit/core/test_orden_exceptions.py` — hierarchy, `str(e)` formatting, attributes

---

## PR 2: Repository + Service (~210 lines)

### Phase 2: Repository Layer

- [x] 2.1 Create `src/repositories/orden.py` — `OrdenRepository` with 5 async methods: `get_all`, `get_by_id`, `create`, `update`, `delete`. Each ≤20 lines, session injection conforming to `MenuRepository` pattern
- [x] 2.2 Write `test/unit/repositories/test_orden_repository.py` — mocked `AsyncSession`, CRUD with line items, 404 propagation on missing

### Phase 3: Service Layer

- [x] 3.1 Create `src/services/orden.py` — `OrdenesService(orden_repo, menu_repo)`: `create` with price lookup + total calc, `cambiar_estado` with estado validation, `get_all`, `get_by_id`. No HTTP imports
- [x] 3.2 Write `test/unit/services/test_orden_service.py` — mocked repos, `MenuNotFoundError` propagation, `InvalidEstadoTransitionError`, repo not called on validation fail, total computation

---

## PR 3: API + Wire-up (~145 lines)

### Phase 4: API Layer

- [x] 4.1 Add `get_orden_service()` to `src/api/deps.py` — factory: `AsyncSession` → `OrdenRepository` + `MenuRepository` → `OrdenesService`
- [x] 4.2 Create `src/api/routers/orden.py` — `APIRouter(prefix="/ordenes")` with 4 endpoints. Translate `OrdenNotFoundError`→404, `InvalidOrdenDataError`→422, `InvalidEstadoTransitionError`→400, `MenuNotFoundError`→404
- [x] 4.3 Write `test/integration/test_orden_api.py` — 10 scenarios per API spec, `TestClient` with dependency overrides

### Phase 5: Main Cleanup

- [x] 5.1 Remove `menu = {}`, `ordenes = {}`, 4 inline handlers (lines 36–124) from `src/main.py`. Add `include_router(orden_router)`
- [x] 5.2 Regression: run all tests — 176 pass, `test_menu_api.py` + `test_menu_api_refactored.py` pass after stub removal
