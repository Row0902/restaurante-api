# Menu API Router Specification

## Purpose

Define the HTTP interface for menu operations via FastAPI `APIRouter`. This replaces the inline endpoints in `src/main.py` (lines 42–117) with a proper layered router.

## Requirements

### Requirement: Router Setup and Dependency Injection

The system MUST provide a `menu_router` instance of `fastapi.APIRouter` with prefix `/menu` and tag `Menú`.

### Requirement: Dependency Factory

The system MUST provide an async dependency factory in `src/api/deps.py` that creates an `AsyncSession`, instantiates `MenuRepository`, and returns `MenuService`.

### Requirement: List Menu Items

The system MUST expose `GET /menu` that returns a list of `PlatoResponse` objects with status 200.

### Requirement: Create Menu Item

The system MUST expose `POST /menu` that accepts `PlatoCreate`, delegates to `MenuService.create()`, and returns `PlatoResponse` with status 201.

### Requirement: Get Menu Item by ID

The system MUST expose `GET /menu/{plato_id}` that returns `PlatoResponse` with status 200, or HTTPException 404 when the item is not found.

### Requirement: Update Menu Item

The system MUST expose `PUT /menu/{plato_id}` that accepts `PlatoUpdate`, delegates to `MenuService.update()`, and returns `PlatoResponse` with status 200, or HTTPException 404 when the item is not found.

### Requirement: Delete Menu Item

The system MUST expose `DELETE /menu/{plato_id}` that delegates to `MenuService.delete()`, returns status 204 on success, or HTTPException 404 when the item is not found.

### Requirement: Domain Exception Translation

The system MUST catch `MenuNotFoundError` and raise `HTTPException(status_code=404)` with the domain message. The system MUST catch `InvalidMenuDataError` and raise `HTTPException(status_code=422)` with the domain message.

### Requirement: Endpoint Async and Typed

All router handlers MUST be `async def` with typed parameters and return types. No handler body SHALL exceed 20 lines.

## Scenarios

### Scenario: List empty menu

- GIVEN an empty menu database
- WHEN `GET /menu` is requested
- THEN the response status is 200
- AND the body is `[]`

### Scenario: List populated menu

- GIVEN two menu items exist
- WHEN `GET /menu` is requested
- THEN the response status is 200
- AND the body contains two `PlatoResponse` objects

### Scenario: Create valid dish

- GIVEN a valid `PlatoCreate` payload
- WHEN `POST /menu` is requested
- THEN the response status is 201
- AND the body is a `PlatoResponse` with assigned `id`

### Scenario: Create invalid dish

- GIVEN a `PlatoCreate` payload with empty `nombre`
- WHEN `POST /menu` is requested
- THEN the response status is 422
- AND the error message references `nombre`

### Scenario: Get existing dish

- GIVEN a menu item with id `1`
- WHEN `GET /menu/1` is requested
- THEN the response status is 200
- AND the body matches the stored item

### Scenario: Get missing dish

- GIVEN no menu item with id `999`
- WHEN `GET /menu/999` is requested
- THEN the response status is 404
- AND the error message contains `999`

### Scenario: Update existing dish

- GIVEN a menu item with id `1`
- WHEN `PUT /menu/1` with `PlatoUpdate` is requested
- THEN the response status is 200
- AND the body reflects the updated fields

### Scenario: Update missing dish

- GIVEN no menu item with id `999`
- WHEN `PUT /menu/999` is requested
- THEN the response status is 404

### Scenario: Delete existing dish

- GIVEN a menu item with id `1`
- WHEN `DELETE /menu/1` is requested
- THEN the response status is 204
- AND the body is empty

### Scenario: Delete missing dish

- GIVEN no menu item with id `999`
- WHEN `DELETE /menu/999` is requested
- THEN the response status is 404

### Scenario: Dependency injection wiring

- GIVEN the `get_menu_service` dependency factory
- WHEN it is invoked in a FastAPI `Depends` context
- THEN it returns a `MenuService` with a `MenuRepository` backed by an `AsyncSession`
