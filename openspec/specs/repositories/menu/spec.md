# Menu Repository Specification

## Purpose

Infrastructure layer that abstracts menu persistence behind an async interface. The repository receives a SQLModel async session via constructor and returns domain models (`MenuItem`), never raw DB tuples.

## Requirements

### Requirement: Async MenuRepository Class

The system MUST provide a `MenuRepository` class in `src/repositories/menu.py` that exposes exactly five public async methods:

| Method | Signature | Behavior |
|--------|-----------|----------|
| `get_all` | `async () -> list[MenuItem]` | Returns all menu items from the database |
| `get_by_id` | `async (plato_id: int) -> MenuItem` | Returns one item; raises `MenuNotFoundError` if missing |
| `create` | `async (data: PlatoCreate) -> MenuItem` | Persists a new item; returns the created `MenuItem` with generated `id` |
| `update` | `async (plato_id: int, data: PlatoUpdate) -> MenuItem` | Updates only provided fields; raises `MenuNotFoundError` if missing |
| `delete` | `async (plato_id: int) -> None` | Removes item; raises `MenuNotFoundError` if missing |

The constructor MUST accept an async SQLModel session. The class MUST NOT exceed 10 public methods (Rule 9). All public methods MUST have typed signatures (Rule 13).

#### Scenario: List all items

- GIVEN the database contains two menu items
- WHEN `get_all()` is awaited
- THEN it MUST return a `list[MenuItem]` containing both items

#### Scenario: List empty table

- GIVEN the database contains no menu items
- WHEN `get_all()` is awaited
- THEN it MUST return an empty list

#### Scenario: Get existing item

- GIVEN a menu item with `id=1` exists in the database
- WHEN `get_by_id(1)` is awaited
- THEN it MUST return the `MenuItem` with `id=1`

#### Scenario: Get missing item

- GIVEN no menu item with `id=99` exists
- WHEN `get_by_id(99)` is awaited
- THEN it MUST raise `MenuNotFoundError` with message `"Menu item 99 not found."`

#### Scenario: Create new item

- GIVEN a `PlatoCreate` with `nombre="Pasta"`, `precio=12.5`
- WHEN `create(data)` is awaited
- THEN it MUST return a `MenuItem` with `id` populated
- AND `nombre` MUST equal `"Pasta"`, `precio` MUST equal `12.5`

#### Scenario: Update existing item

- GIVEN a menu item with `id=1` and `nombre="Pasta"` exists
- AND a `PlatoUpdate` with `nombre="Pizza"` is provided
- WHEN `update(1, data)` is awaited
- THEN it MUST return the `MenuItem` with `nombre="Pizza"`
- AND unprovided fields (`precio`, `categoria`, `descripcion`) MUST retain their original values

#### Scenario: Update missing item

- GIVEN no menu item with `id=99` exists
- WHEN `update(99, data)` is awaited
- THEN it MUST raise `MenuNotFoundError`

#### Scenario: Delete existing item

- GIVEN a menu item with `id=1` exists
- WHEN `delete(1)` is awaited
- THEN it MUST complete without error
- AND the item MUST no longer exist in the database

#### Scenario: Delete missing item

- GIVEN no menu item with `id=99` exists
- WHEN `delete(99)` is awaited
- THEN it MUST raise `MenuNotFoundError`

## Constraints

| Constraint | Rule | Implication |
|------------|------|-------------|
| One class per file | Rule 3 | `MenuRepository` lives alone in `repositories/menu.py` |
| Async first | Rule 14 | All repository methods must be `async def` |
| Type hints on all public functions | Rule 13 | Every method has typed params and return |
| Max 10 public methods per class | Rule 9 | Repository exposes exactly 5 CRUD methods |
| Functions ≤ 20 lines | Rule 8 | Each method body is short; SQLAlchemy operations are concise |
| Max file 500 lines | Rule 2 | `menu.py` stays well under 500 lines |

## Coverage

| Path | Type | Scenarios |
|------|------|-----------|
| Happy paths | Covered | get_all, get_by_id, create, update, delete |
| Edge cases | Covered | Empty table, partial update (only provided fields) |
| Error states | Covered | `MenuNotFoundError` on get_by_id, update, delete |
