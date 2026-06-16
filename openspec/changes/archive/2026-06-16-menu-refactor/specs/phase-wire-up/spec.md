# Delta for Wire-Up (Phase 5)

## MODIFIED Requirements

### Requirement: Main Application Module — Menu Code Removal

The system MUST remove `menu = {}`, `print()` calls inside menu handlers, and all inline menu handlers (`@app.get("/menu")`, `@app.post("/menu")`, `@app.get("/menu/{plato_id}")`, `@app.put("/menu/{plato_id}")`, `@app.delete("/menu/{plato_id}")`) from `src/main.py`. The `from api.routers.menu import router as menu_router` import and `app.include_router(menu_router)` MUST remain. CORS middleware, the root endpoint `/`, `ordenes = {}`, and all ordenes endpoints MUST remain unchanged.
(Previously: `main.py` contained both old inline menu routes and the new router registration.)

#### Scenario: Old menu dict is gone

- GIVEN `src/main.py` after Phase 5
- WHEN searching for `menu = {}`
- THEN no match is found

#### Scenario: Old inline menu handlers are gone

- GIVEN `src/main.py` after Phase 5
- WHEN searching for `@app.get("/menu")` or `@app.post("/menu")` or `@app.put("/menu")` or `@app.delete("/menu")`
- THEN no match is found

#### Scenario: New router registration remains

- GIVEN `src/main.py` after Phase 5
- WHEN `app.include_router(menu_router)` is present
- THEN `GET /menu` routes to the new `menu_router`

### Requirement: Integration Test Migration

The system MUST update `test/integration/test_menu_api.py` to test the new menu router endpoints through `main.app` using `TestClient`. The test file MUST set up a test database engine and override `get_menu_service` on `main.app` for isolation. Tests asserting old behavior (string IDs, 200 on POST, 200 on DELETE, `KeyError` propagation, full-replace PUT, create-on-missing PUT, empty payload creation, print side effects) MUST be removed or updated to match new router behavior (int IDs, 201 on POST, 204 on DELETE, 404 on missing, partial update PUT, 422 on invalid data, no print).
(Previously: `test_menu_api.py` tested old inline dict-based routes with sync TestClient and no DB setup.)

#### Scenario: test_menu_api.py targets new router via main.app

- GIVEN `test_menu_api.py` imports `main.app` and sets up a test DB with dependency overrides
- WHEN `TestClient(app).get("/menu")` is called
- THEN it returns 200 and the response matches the new router format

#### Scenario: Old behavior assertions removed

- GIVEN `test_menu_api.py` after migration
- WHEN searching for string ID assertions, `KeyError` tests, `print` side effect tests, or `mensaje` in delete response
- THEN no match is found

### Requirement: Root Test File Cleanup

The system MUST remove the `test_listar_menu_vacio` test from `test/test_main.py`. Only the `test_raiz` root endpoint test MUST remain.
(Previously: `test_main.py` contained both root and menu empty-list tests.)

#### Scenario: test_main.py contains only root test

- GIVEN `test/test_main.py` after cleanup
- WHEN it is executed
- THEN only `test_raiz` runs and passes

## REMOVED Requirements

### Requirement: Print Side Effects in Endpoints

(Reason: Side effects are not part of Clean Architecture. New router has no print statements.)

### Requirement: Global Menu Dictionary as In-Memory Store

(Reason: Replaced by `MenuRepository` with SQLite persistence via `AsyncSession`.)
