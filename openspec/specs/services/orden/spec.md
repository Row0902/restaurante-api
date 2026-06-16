# OrdenesService Specification

## Purpose

Business logic layer for order operations. Receives `OrdenRepository` and `MenuRepository` via constructor. Orchestrates order creation, total calculation, and estado transitions. Zero knowledge of HTTP or sessions.

## Requirements

### Requirement: Dual Repository Injection

`OrdenesService` MUST receive `OrdenRepository` and `MenuRepository` via constructor. It MUST store both as private attributes and MUST NOT create repositories or sessions internally.

#### Scenario: Repositories injected at construction

- GIVEN `OrdenRepository` and `MenuRepository` instances
- WHEN `OrdenesService(orden_repo, menu_repo)` is called
- THEN both repositories are stored for subsequent operations

### Requirement: Create Order

`create(data: OrdenCreate)` MUST be an `async` method with return type `Orden`. It MUST:
1. Call `data.validate()` first.
2. For each item, call `menu_repo.get_by_id(plato_id)` to verify existence and fetch `precio`.
3. Build `OrdenItem` list with `precio_unitario` snapshot from the menu item.
4. Calculate `total` as sum of `cantidad * precio_unitario`.
5. Set `estado="pendiente"`.
6. Delegate to `orden_repo.create(data, items)` and return the result.

If validation fails, `InvalidOrdenDataError` MUST be raised and the repository MUST NOT be invoked. If a menu item does not exist, `MenuNotFoundError` MUST propagate.

#### Scenario: Valid order with existing items

- GIVEN `OrdenCreate` with two items referencing existing menu items priced at `10.0` and `15.0`
- WHEN `await service.create(data)` is called
- THEN `data.validate()` passes
- AND `menu_repo.get_by_id()` is called for each item
- AND the returned `Orden` has `total=25.0` and `estado="pendiente"`
- AND `orden_repo.create()` is awaited exactly once

#### Scenario: Invalid order — empty items

- GIVEN `OrdenCreate(items=[])`
- WHEN `await service.create(data)` is called
- THEN `InvalidOrdenDataError` is raised
- AND `orden_repo.create()` is never invoked

#### Scenario: Menu item not found during creation

- GIVEN `OrdenCreate` with an item referencing `plato_id=99`
- AND `menu_repo.get_by_id(99)` raises `MenuNotFoundError`
- WHEN `await service.create(data)` is called
- THEN `MenuNotFoundError` is raised
- AND `orden_repo.create()` is never invoked

### Requirement: Cambiar Estado

`cambiar_estado(orden_id: int, nuevo_estado: str)` MUST be an `async` method with return type `Orden`. It MUST:
1. Fetch the existing order via `orden_repo.get_by_id(orden_id)`.
2. Validate the transition using polymorphic rules based on current `estado`.
3. Build `OrdenUpdateEstado` with the new estado and update via `orden_repo.update()`.
4. Return the updated `Orden`.

If the transition is invalid, `InvalidEstadoTransitionError` MUST be raised.

#### Scenario: Valid transition

- GIVEN an order with `id=1` and `estado="pendiente"`
- WHEN `await service.cambiar_estado(1, "preparando")` is called
- THEN `orden_repo.get_by_id(1)` is awaited
- AND the transition is validated
- AND `orden_repo.update()` is called with `estado="preparando"`
- AND the updated `Orden` is returned

#### Scenario: Invalid transition

- GIVEN an order with `id=1` and `estado="entregado"`
- WHEN `await service.cambiar_estado(1, "preparando")` is called
- THEN `InvalidEstadoTransitionError` is raised
- AND `orden_repo.update()` is never invoked

#### Scenario: Order not found

- GIVEN no order with `id=99` exists
- WHEN `await service.cambiar_estado(99, "preparando")` is called
- THEN `OrdenNotFoundError` is raised

### Requirement: List and Get Orders

`get_all()` MUST delegate to `orden_repo.get_all()`. `get_by_id(orden_id: int)` MUST delegate to `orden_repo.get_by_id(orden_id)`. `OrdenNotFoundError` MUST propagate unchanged.

#### Scenario: List orders

- GIVEN a mocked repository returning two orders
- WHEN `await service.get_all()` is called
- THEN `repo.get_all()` is awaited once
- AND the list is returned unchanged

#### Scenario: Get missing order

- GIVEN a mocked repository raising `OrdenNotFoundError(99)`
- WHEN `await service.get_by_id(99)` is called
- THEN `OrdenNotFoundError` is raised

### Requirement: No HTTP Knowledge

`OrdenesService` MUST NOT import `fastapi`, `starlette`, or HTTP modules. It MUST NOT create `AsyncSession` instances. It MUST NOT raise `HTTPException`.

#### Scenario: Exception translation absent

- GIVEN any `OrdenesService` method
- WHEN `OrdenNotFoundError` or `InvalidEstadoTransitionError` is raised
- THEN the exception is a `DomainError` subclass
- AND no HTTP status code is present

### Requirement: Type Safety and Size

All public methods MUST have typed parameters and returns. The constructor MUST be typed as `def __init__(self, orden_repo: OrdenRepository, menu_repo: MenuRepository) -> None`. Every method body MUST be ≤ 20 lines.

## Constraints

| Constraint | Rule | Implication |
|------------|------|-------------|
| One class per file | Rule 3 | `OrdenesService` lives alone in `services/orden.py` |
| Async first | Rule 14 | All methods are `async def` |
| Type hints required | Rule 13 | All public methods and constructor typed |
| Functions ≤ 20 lines | Rule 8 | Extract helpers if needed |
| SRP | Rule 6 | Single responsibility: order business logic |

## Coverage

| Path | Type | Scenarios |
|------|------|-----------|
| Happy paths | Covered | Create with valid items, valid estado transition, list/get |
| Edge cases | Covered | Empty items list, cancel from active state |
| Error states | Covered | `OrdenNotFoundError`, `InvalidOrdenDataError`, `InvalidEstadoTransitionError`, `MenuNotFoundError` |
