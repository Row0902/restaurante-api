# MenuService Specification

## Purpose

Defines the service layer for menu business logic. `MenuService` sits between the API layer and the repository layer, orchestrating CRUD operations and enforcing domain validation rules via polymorphic `validate()` calls. It has zero knowledge of HTTP, sessions, or infrastructure frameworks.

## Requirements

### Requirement: Constructor Injection

The service MUST receive `MenuRepository` via its constructor. The service MUST store the repository as a private attribute and MUST NOT create sessions, engines, or repositories internally.

#### Scenario: Repository is injected at construction

- GIVEN a `MenuRepository` instance
- WHEN `MenuService(repo)` is called
- THEN the service stores the repository for subsequent operations

### Requirement: List Menu Items

`get_all()` MUST be an `async` method with return type `list[MenuItem]`. It MUST delegate directly to `repo.get_all()` and return the result unchanged.

#### Scenario: Delegation to repository

- GIVEN a `MenuService` with a mocked repository
- WHEN `await service.get_all()` is called
- THEN `repo.get_all()` is awaited exactly once
- AND the returned list is passed through unchanged

### Requirement: Retrieve Single Item

`get_by_id(plato_id: int)` MUST be an `async` method with return type `MenuItem`. It MUST delegate to `repo.get_by_id(plato_id)` and return the result. If the item does not exist, `MenuNotFoundError` MUST propagate unchanged.

#### Scenario: Item found

- GIVEN a mocked repository returning a `MenuItem` for id `1`
- WHEN `await service.get_by_id(1)` is called
- THEN the same `MenuItem` is returned

#### Scenario: Item not found

- GIVEN a mocked repository raising `MenuNotFoundError(99)`
- WHEN `await service.get_by_id(99)` is called
- THEN `MenuNotFoundError` is raised with message "Menu item 99 not found."

### Requirement: Create Item

`create(data: PlatoCreate)` MUST be an `async` method with return type `MenuItem`. It MUST call `data.validate()` before touching the repository. If validation succeeds, it MUST delegate to `repo.create(data)` and return the result. If validation fails, `InvalidMenuDataError` MUST be raised and the repository MUST NOT be invoked.

#### Scenario: Valid data

- GIVEN a `PlatoCreate(nombre="Pasta", precio=12.5)`
- WHEN `await service.create(data)` is called
- THEN `data.validate()` passes
- AND `repo.create(data)` is awaited exactly once
- AND the returned `MenuItem` is returned

#### Scenario: Invalid data — empty nombre

- GIVEN a `PlatoCreate(nombre="", precio=12.5)`
- WHEN `await service.create(data)` is called
- THEN `InvalidMenuDataError("nombre", "is required.")` is raised
- AND `repo.create()` is never invoked

#### Scenario: Invalid data — non-positive precio

- GIVEN a `PlatoCreate(nombre="Pasta", precio=0)`
- WHEN `await service.create(data)` is called
- THEN `InvalidMenuDataError("precio", "must be positive.")` is raised
- AND `repo.create()` is never invoked

### Requirement: Update Item

`update(plato_id: int, data: PlatoUpdate)` MUST be an `async` method with return type `MenuItem`. It MUST call `data.validate()` before touching the repository. If validation succeeds, it MUST delegate to `repo.update(plato_id, data)` and return the result. If validation fails, `InvalidMenuDataError` MUST be raised and the repository MUST NOT be invoked. `MenuNotFoundError` from the repository MUST propagate unchanged.

#### Scenario: Valid partial update

- GIVEN an existing item with id `1` and a `PlatoUpdate(nombre="Pizza")`
- WHEN `await service.update(1, data)` is called
- THEN `data.validate()` passes
- AND `repo.update(1, data)` is awaited exactly once
- AND the returned `MenuItem` is returned

#### Scenario: Invalid update — empty nombre

- GIVEN a `PlatoUpdate(nombre="")`
- WHEN `await service.update(1, data)` is called
- THEN `InvalidMenuDataError("nombre", "is required.")` is raised
- AND `repo.update()` is never invoked

#### Scenario: Update on missing item

- GIVEN a `PlatoUpdate(nombre="Pizza")` and a mocked repository raising `MenuNotFoundError(99)`
- WHEN `await service.update(99, data)` is called
- THEN `MenuNotFoundError` is raised

### Requirement: Delete Item

`delete(plato_id: int)` MUST be an `async` method with return type `None`. It MUST delegate to `repo.delete(plato_id)`. If the item does not exist, `MenuNotFoundError` MUST propagate unchanged.

#### Scenario: Existing item

- GIVEN a mocked repository that succeeds for id `1`
- WHEN `await service.delete(1)` is called
- THEN `repo.delete(1)` is awaited exactly once

#### Scenario: Missing item

- GIVEN a mocked repository raising `MenuNotFoundError(99)` for id `99`
- WHEN `await service.delete(99)` is called
- THEN `MenuNotFoundError` is raised

### Requirement: No HTTP or Session Knowledge

`MenuService` MUST NOT import `fastapi`, `starlette`, or any HTTP-related module. It MUST NOT create `AsyncSession` instances. It MUST NOT raise `HTTPException` or any HTTP status code.

#### Scenario: HTTP exception translation is absent

- GIVEN any `MenuService` method
- WHEN `MenuNotFoundError` or `InvalidMenuDataError` is raised
- THEN the exception is a `DomainError` subclass
- AND no HTTP status code is present in the exception

### Requirement: Type Safety

Every public method on `MenuService` MUST have fully typed parameters and return annotations. The constructor MUST type the repository parameter as `MenuRepository`.

#### Scenario: Type hints present

- GIVEN the `MenuService` source code
- WHEN inspected
- THEN all methods have `async def` with typed params and return types
- AND the constructor signature is `def __init__(self, repo: MenuRepository) -> None`

### Requirement: Function Size

Every public method body MUST contain at most 20 source lines (excluding docstring and signature).

#### Scenario: All methods fit size limit

- GIVEN the `MenuService` source file
- WHEN each method body is counted
- THEN no body exceeds 20 lines
