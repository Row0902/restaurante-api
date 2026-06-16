## Exploration: Ordenes Refactor

### Current State

The `ordenes` endpoint lives entirely in `src/main.py` (lines 44–124), sharing the same monolithic pattern as the now-refactored `menu` did. Two global mutable dicts — `menu: dict = {}` and `ordenes: dict = {}` — serve as the data store. The `menu` dict is kept as a stub because `POST /ordenes` reads `menu[plato_id]` directly to calculate totals. There are zero tests covering any of the four endpoints.

### Affected Areas

- `src/main.py` — Four inline handlers (lines 47–124) to be extracted. The stub `menu = {}` (line 38) is kept ONLY because ordenes reads it — this coupling must be resolved.
- `src/core/exceptions.py` — Needs new domain exceptions: `OrdenNotFoundError`, `InvalidOrdenDataError`, `ItemNotFoundError` (for items in menu lookup during total calculation).
- `src/core/models/orden.py` — NEW: `Orden` + `OrdenItem` SQLModel tables.
- `src/core/schemas/orden.py` — NEW: `OrdenCreate`, `OrdenUpdateEstado`, `OrdenItemData`, `OrdenResponse` — each with polymorphic `validate()`.
- `src/repositories/orden.py` — NEW: `OrdenRepository` — async CRUD with line items.
- `src/services/orden.py` — NEW: `OrdenService` — needs BOTH `OrdenRepository` and `MenuRepository` (cross-domain dependency).
- `src/api/routers/orden.py` — NEW: `APIRouter(prefix="/ordenes")`.
- `src/api/deps.py` — Add `get_orden_service()` dependency factory.
- `test/integration/test_orden_api.py` — NEW: Integration tests with `TestClient` + DB.
- `test/unit/repositories/test_orden_repository.py` — NEW: Repository unit tests.
- `test/unit/services/test_orden_service.py` — NEW: Service unit tests with mock repos.

### Current Bad Practices

| # | Issue | Location | Rule Violation |
|---|-------|----------|----------------|
| 1 | `ordenes = {}` global mutable dict — shared state, no isolation | Line 39 | Rule 4 (layers), Rule 7 (CA) |
| 2 | Reads `menu[plato_id]` directly — depends on another global mutable dict | Line 79 | Rule 4, Rule 7 |
| 3 | `menu[plato_id]` raises `KeyError` → 500 (unhandled) | Line 79 | Rule 15 (consistent error handling) |
| 4 | No type hints on any function signature | Lines 48, 58, 91, 108 | Rule 13 (type hints required) |
| 5 | Sync `def` instead of `async def` | All four endpoints | Rule 14 (async first) |
| 6 | `print()` side effects instead of logging | Lines 54, 87, 104, 122 | Clean Code, Rule 5 |
| 7 | `orden: dict` accepts arbitrary payload — no Pydantic validation | Line 59 | Rule 15, no validation |
| 8 | `orden.get("items", [])` — no model, no schema, no structure | Line 75 | Rule 5 (Clean Code) |
| 9 | `total` calculated inline in HTTP handler | Lines 76–80 | Rule 4 (layers), Rule 7 |
| 10 | `id = str(len(ordenes) + 1)` — string IDs, order-dependent, race-prone | Line 73 | Clean Code, no SRP |
| 11 | `estado` set as raw string `"pendiente"` — no enum/validation | Line 85 | Rule 5, validation missing |
| 12 | `PUT .../estado` accepts `estado: dict` — no input validation, accepts anything | Line 109 | Rule 13, Rule 15 |
| 13 | `ordenes[orden_id]["estado"] = estado.get("estado")` — can set ANY value | Line 123 | No state machine, no validation |
| 14 | `KeyError` propagates as 500 on `GET /ordenes/{id}` and `PUT .../estado` | Lines 105, 123 | Rule 15 |
| 15 | `print()` inside a pure getter endpoint | Line 104 | Side effect in query |
| 16 | Zero tests — no characterization, no unit, no integration | — | Rule 10 (TDD) |
| 17 | No coverage on ~80 lines of orchestration code | Lines 44–124 | Rule 12 (≥80% coverage) |

### Existing Test Coverage

**Zero.** There are no test files anywhere in `test/` that reference `ordenes`, `orden`, or `order`. The `menu`-related test files (`test_menu_api.py`, `test_menu_service.py`, `test_menu_repository.py`) cover only the already-refactored menu domain. Orders are a blind spot in the existing 80-test suite.

### Dependencies: Cross-Domain Menu Lookup

This is the critical architectural decision. `POST /ordenes` needs menu item prices to calculate the order total.

**Options:**

1. **OrdenesService receives MenuRepository directly** (recommended)
   - `OrdenesService.__init__(orden_repo, menu_repo)` — both repositories injected via constructor
   - Service calls `menu_repo.get_by_id(plato_id)` for each item in the order
   - Pros: Simple, testable (mock both repos), follows the dependency direction (api→services→repositories→core), keeps MenuService out of the data-access path
   - Cons: OrdenesService knows about two repositories (still SRP — its single responsibility is order creation, which inherently requires menu data)
   - **This is the cleanest approach.** The service has one reason to change (order business rules); menu lookup is part of that rule.

2. **OrdenesService receives MenuService**
   - `OrdenesService.__init__(orden_repo, menu_service)`
   - Calls `menu_service.get_by_id(plato_id)` for price lookup
   - Pros: More abstract, reuses MenuService's existing interface
   - Cons: MenuService may have business logic that's unnecessary here; creates a stronger coupling; the service-to-service call muddies the layer diagram

3. **API-level coordination: router gets both services**
   - Router receives both `MenuService` and `OrdenesService`, calls menu lookup at the HTTP layer
   - Pros: OrdenesService stays "pure" (only OrdenRepository)
   - Cons: Business logic (total calculation) leaks into the API layer — violates Rule 7 and Rule 4

**Recommendation: Option 1.** OrdenesService takes both repositories. The service IS the place for coordinated business logic.

### Domain Model

**Orden** (SQLModel, table: `ordenes`):
```
id: int | None = Field(default=None, primary_key=True)
estado: str        # "pendiente", "preparando", "entregado", "cancelado"
mesa: int | None
total: float       # computed, stored as snapshot
created_at: datetime | None  # default=datetime.now()
```

**OrdenItem** (SQLModel, table: `orden_items`):
```
id: int | None = Field(default=None, primary_key=True)
orden_id: int = Field(foreign_key="ordenes.id")
plato_id: int     # FK to menu_items — logical FK, no SQL constraint needed
cantidad: int
precio_unitario: float  # snapshot of menu item price at order time
```

The `total` field on Orden is computed: sum of each OrdenItem's `cantidad * precio_unitario`. This is calculated in the service layer, not in the database.

**Estado state machine** (possible states and transitions):
- `pendiente` → `preparando` → `entregado`
- `pendiente` → `cancelado`
- `preparando` → `cancelado`

Validation for this belongs in the service layer (or a dedicated validation method on the schema).

### Target Architecture

```
src/
└── core/
    ├── exceptions.py                         ← ADD: OrdenNotFoundError, InvalidOrdenDataError
    ├── models/
    │   ├── menu.py                           (existing)
    │   └── orden.py                          ← NEW: Orden + OrdenItem SQLModel
    └── schemas/
        ├── menu.py                           (existing)
        └── orden.py                          ← NEW: OrdenCreate, OrdenUpdateEstado, OrdenItemData, OrdenResponse
src/
├── repositories/
│   ├── __init__.py                           (existing)
│   ├── menu.py                               (existing)
│   └── orden.py                              ← NEW: OrdenRepository
├── services/
│   ├── __init__.py                           (existing)
│   ├── menu.py                               (existing)
│   └── orden.py                              ← NEW: OrdenesService (receives OrdenRepository + MenuRepository)
└── api/
    ├── deps.py                               ← ADD: get_orden_service()
    └── routers/
        ├── __init__.py                       (existing)
        ├── menu.py                           (existing)
        └── orden.py                          ← NEW: APIRouter with 3-4 endpoints
test/
├── integration/
│   ├── test_menu_api.py                      (existing)
│   └── test_orden_api.py                     ← NEW
└── unit/
    ├── repositories/
    │   ├── test_menu_repository.py           (existing)
    │   └── test_orden_repository.py          ← NEW
    └── services/
        ├── test_menu_service.py              (existing)
        └── test_orden_service.py             ← NEW
```

### Approach Options

1. **Full extraction in one shot** — Create all layers (core → repo → service → api) and wire up
   - Pros: Fastest path to "done"
   - Cons: High PR size (likely 500+ lines), risky without characterization tests first
   - Effort: High (~30 tasks)

2. **Phase 0 characterization tests, then layers** (same as menu)
   - Pros: Proven pattern from menu-refactor, safe, allows behavior pinning
   - Cons: More phases, takes longer
   - Effort: Medium/High (~25–30 tasks)

3. **Even smaller slices: core+repo first, then service, then API**
   - Pros: Minimal PR sizes, maximum review safety
   - Cons: More PRs, coordination overhead
   - Effort: Medium (~28 tasks across more phases)

### Recommendation

**Follow the menu-refactor pattern (Option 2).** It's a proven approach in this codebase, the team already understands the flow, and the risks are well-understood. Specifically:

1. **Phase 0**: Characterization tests for existing ordenes endpoints (pinning current behavior, including the `menu[plato_id]` dependency — use `monkeypatch` or dependency overrides for the menu stub)
2. **Phase 1**: Core domain — `Orden` + `OrdenItem` models, schemas (`OrdenCreate`, `OrdenUpdateEstado`, `OrdenItemData`, `OrdenResponse`), domain exceptions (`OrdenNotFoundError`, `InvalidOrdenDataError`)
3. **Phase 2**: Repository — `OrdenRepository` with async CRUD for orders + line items
4. **Phase 3**: Service — `OrdenesService` receiving `OrdenRepository` + `MenuRepository` via constructor; total calculation, estado validation, menu item lookup
5. **Phase 4**: API Router — `APIRouter(prefix="/ordenes")`, exception translation
6. **Phase 5**: Wire-up — remove inline handlers from `main.py`, remove `menu = {}` and `ordenes = {}` stubs, update `deps.py`

### Relationship to Menu

- `POST /ordenes` needs to look up menu items for price. The refactored approach: `OrdenesService` receives `MenuRepository` and calls `get_by_id(plato_id)` for each item in the request.
- The `menu = {}` stub in `main.py` can be removed once orders are refactored — it's the last consumer.
- The menu items are stored in the database (`menu_items` table). OrdenesService fetches them read-only; it does NOT create/modify/delete menu items.
- **Caution**: `MenuItem.precio` could change after an order is placed. The `OrdenItem.precio_unitario` field captures the price at order time (snapshot), so future menu price changes don't affect existing orders.

### Size Estimate

Slightly larger than menu-refactor (21 phases/tasks). Estimated 25–30 tasks across 6 phases:

| Phase | Focus | Est. Tasks |
|-------|-------|-----------|
| 0 | Characterization tests (4 endpoints + menu stub as external dep) | 4 |
| 1 | Core models + schemas + exceptions | 5 |
| 2 | OrdenRepository | 4 |
| 3 | OrdenesService (with cross-repo coordination) | 5 |
| 4 | API router + deps.py wiring | 4 |
| 5 | main.py cleanup + wire-up | 4 |
| **Total** | | **~26** |

**Reasons for larger size:**
- Line items (OrderItem) add a second table and relationship
- Cross-domain dependency (MenuRepository injection) adds complexity to service tests
- Estado state machine needs validation logic
- Total calculation involves business logic that menu didn't have (menu was pure CRUD)
- More test scenarios (valid/invalid estado transitions, item lookup failures, partial item availability)

### Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| `menu[plato_id]` in existing handler reads dict, but refactored menu reads DB — behavior mismatch in char tests | Medium | Characterization tests should mock/freeze the menu dict to isolate ordenes behavior. Capture what ordenes DOES with menu data, not the menu data source. |
| `precio_unitario` snapshot vs live price — design decision must be explicit | Medium | Spec must state: `precio_unitario` is snapshotted at order creation. This is a behavioral change from the current code (which reads `menu[plato_id]["precio"]` at the moment of calculation — same moment as creation, so no actual difference in current behavior, but it matters for future edits). |
| Estado state machine expansion could lead to if/elif chain (Rule 1: polymorphic validation) | Medium | Use polymorphic validation — each estado transition could validate itself, or the schema `OrdenUpdateEstado.validate()` checks validity. |
| Size exceeds 400-line review budget (26 tasks, likely 600+ lines) | High | Plan for chained PRs (e.g., PR 1: Phase 0–1 core, PR 2: Phase 2–3 repo+service, PR 3: Phase 4–5 API+wire-up) |
| Existing `menu = {}` stub removal breaks nothing if done correctly, but the dependency chain is subtle | Low | Ensure ordenes-char-tests run against main.py with stub, then refactored tests run against new router. No overlap. |

### Ready for Proposal

**Yes.** The exploration is comprehensive. The orchestrator should tell the user:
- The refactoring is feasible and similar in approach to menu-refactor, but ~25% larger
- The key architectural decision is how OrdenesService accesses menu data — **recommend Option 1 (MenuRepository injection)**
- The estado field should be modeled with a state machine and polymorphic validation
- Recommend starting characterization tests first (Phase 0) before any refactoring code
- Recommend chained PRs due to expected size
