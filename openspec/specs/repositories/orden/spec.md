# Orden Repository Specification

## Purpose

Infrastructure layer for order persistence. Abstracts `Orden` and `OrdenItem` CRUD behind an async interface. Returns domain models, never raw DB tuples.

## Requirements

### Requirement: Async OrdenRepository Class

The system MUST provide `OrdenRepository` in `src/repositories/orden.py` with exactly five public async methods:

| Method | Signature | Behavior |
|--------|-----------|----------|
| `get_all` | `async () -> list[Orden]` | Returns all orders with line items |
| `get_by_id` | `async (orden_id: int) -> Orden` | Returns one order; raises `OrdenNotFoundError` if missing |
| `create` | `async (data: OrdenCreate, items: list[OrdenItem]) -> Orden` | Persists order and line items; returns order with generated `id` |
| `update` | `async (orden_id: int, data: OrdenUpdateEstado) -> Orden` | Updates order fields; raises `OrdenNotFoundError` if missing |
| `delete` | `async (orden_id: int) -> None` | Removes order and its line items; raises `OrdenNotFoundError` if missing |

The constructor MUST accept an `AsyncSession`. The class MUST NOT exceed 10 public methods.

#### Scenario: List all orders

- GIVEN two orders exist in the database
- WHEN `get_all()` is awaited
- THEN it MUST return a `list[Orden]` containing both with their items

#### Scenario: List empty orders table

- GIVEN no orders exist
- WHEN `get_all()` is awaited
- THEN it MUST return an empty list

#### Scenario: Get existing order

- GIVEN an order with `id=1` exists
- WHEN `get_by_id(1)` is awaited
- THEN it MUST return the `Orden` with `id=1` and its items

#### Scenario: Get missing order

- GIVEN no order with `id=99` exists
- WHEN `get_by_id(99)` is awaited
- THEN it MUST raise `OrdenNotFoundError` with message containing `99`

#### Scenario: Create order with line items

- GIVEN an `OrdenCreate` and two `OrdenItem` instances
- WHEN `create(data, items)` is awaited
- THEN it MUST return an `Orden` with `id` populated
- AND the items MUST be persisted with `orden_id` set

#### Scenario: Update order estado

- GIVEN an order with `id=1` and `estado="pendiente"`
- AND an `OrdenUpdateEstado` with `estado="preparando"`
- WHEN `update(1, data)` is awaited
- THEN it MUST return the `Orden` with `estado="preparando"`

#### Scenario: Update missing order

- GIVEN no order with `id=99` exists
- WHEN `update(99, data)` is awaited
- THEN it MUST raise `OrdenNotFoundError`

#### Scenario: Delete existing order

- GIVEN an order with `id=1` exists with line items
- WHEN `delete(1)` is awaited
- THEN it MUST complete without error
- AND the order and its items MUST no longer exist

#### Scenario: Delete missing order

- GIVEN no order with `id=99` exists
- WHEN `delete(99)` is awaited
- THEN it MUST raise `OrdenNotFoundError`

## Constraints

| Constraint | Rule | Implication |
|------------|------|-------------|
| One class per file | Rule 3 | `OrdenRepository` lives alone in `repositories/orden.py` |
| Async first | Rule 14 | All methods must be `async def` |
| Type hints required | Rule 13 | Every method has typed params and return |
| Max 10 public methods | Rule 9 | Repository exposes exactly 5 CRUD methods |
| Functions ≤ 20 lines | Rule 8 | Each method body short |

## Coverage

| Path | Type | Scenarios |
|------|------|-----------|
| Happy paths | Covered | get_all, get_by_id, create, update, delete |
| Edge cases | Covered | Empty table, order with no items |
| Error states | Covered | `OrdenNotFoundError` on get_by_id, update, delete |
