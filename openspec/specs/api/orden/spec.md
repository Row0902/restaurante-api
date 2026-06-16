# Orden API Router Specification

## Purpose

Define the HTTP interface for order operations via FastAPI `APIRouter`. Replaces the inline endpoints in `src/main.py` (lines 44–124) with a layered router.

## Requirements

### Requirement: Router Setup

The system MUST provide `orden_router` as `APIRouter(prefix="/ordenes", tags=["Órdenes"])`.

### Requirement: Dependency Factory

The system MUST provide `get_orden_service()` in `src/api/deps.py` that creates an `AsyncSession`, instantiates `OrdenRepository` and `MenuRepository`, and returns `OrdenesService`.

### Requirement: List Orders

`GET /ordenes` MUST return `list[OrdenResponse]` with status 200.

### Requirement: Create Order

`POST /ordenes` MUST accept `OrdenCreate`, delegate to `OrdenesService.create()`, and return `OrdenResponse` with status 201.

### Requirement: Get Order by ID

`GET /ordenes/{orden_id}` MUST return `OrdenResponse` with status 200, or `HTTPException` 404 when not found.

### Requirement: Update Order Estado

`PUT /ordenes/{orden_id}/estado` MUST accept `OrdenUpdateEstado`, delegate to `OrdenesService.cambiar_estado()`, and return `OrdenResponse` with status 200, or `HTTPException` 404/400 when not found or transition invalid.

### Requirement: Domain Exception Translation

The system MUST translate:

| Domain Exception | HTTP Status |
|------------------|-------------|
| `OrdenNotFoundError` | 404 |
| `InvalidOrdenDataError` | 422 |
| `InvalidEstadoTransitionError` | 400 |
| `MenuNotFoundError` | 404 |

### Requirement: Endpoint Async and Typed

All handlers MUST be `async def` with typed parameters and returns. No handler body SHALL exceed 20 lines.

## Scenarios

### Scenario: List empty orders

- GIVEN an empty orders database
- WHEN `GET /ordenes` is requested
- THEN the response status is 200
- AND the body is `[]`

### Scenario: List populated orders

- GIVEN two orders exist
- WHEN `GET /ordenes` is requested
- THEN the response status is 200
- AND the body contains two `OrdenResponse` objects

### Scenario: Create valid order

- GIVEN a valid `OrdenCreate` payload with existing menu items
- WHEN `POST /ordenes` is requested
- THEN the response status is 201
- AND the body is an `OrdenResponse` with `estado="pendiente"` and computed `total`

### Scenario: Create order with invalid items

- GIVEN an `OrdenCreate` payload with `cantidad=0`
- WHEN `POST /ordenes` is requested
- THEN the response status is 422
- AND the error message references the invalid field

### Scenario: Create order with missing menu item

- GIVEN an `OrdenCreate` payload referencing `plato_id=999`
- WHEN `POST /ordenes` is requested
- THEN the response status is 404
- AND the error message references `999`

### Scenario: Get existing order

- GIVEN an order with `id=1`
- WHEN `GET /ordenes/1` is requested
- THEN the response status is 200
- AND the body matches the stored order

### Scenario: Get missing order

- GIVEN no order with `id=999`
- WHEN `GET /ordenes/999` is requested
- THEN the response status is 404

### Scenario: Update estado valid

- GIVEN an order with `id=1` and `estado="pendiente"`
- WHEN `PUT /ordenes/1/estado` with `"preparando"` is requested
- THEN the response status is 200
- AND the body has `estado="preparando"`

### Scenario: Update estado invalid

- GIVEN an order with `id=1` and `estado="pagado"`
- WHEN `PUT /ordenes/1/estado` with `"preparando"` is requested
- THEN the response status is 400

### Scenario: Dependency injection wiring

- GIVEN `get_orden_service` factory
- WHEN invoked in a FastAPI `Depends` context
- THEN it returns `OrdenesService` with both repositories backed by an `AsyncSession`
