# Core Orden Domain Specification

## Purpose

Innermost layer for the orders domain. Defines `Orden` and `OrdenItem` SQLModel tables, Pydantic schemas with polymorphic validation, and domain exceptions. Zero dependencies on frameworks, databases, or HTTP.

## Requirements

### Requirement: Orden SQLModel Table

The system MUST define `Orden` with fields:

| Field | Type | Constraints |
|-------|------|-------------|
| id | int | Primary key, auto-increment |
| estado | str | Non-nullable, default `"pendiente"` |
| mesa | int | Optional (nullable) |
| total | float | Non-nullable, computed snapshot |
| created_at | datetime | Optional, default `datetime.now()` |

Table name MUST be `ordenes`. The model MUST be compatible with async SQLAlchemy.

#### Scenario: Valid instantiation

- GIVEN `Orden` with `estado="pendiente"`, `total=25.0`
- WHEN instantiated
- THEN `id` MAY be `None`
- AND `mesa` and `created_at` MAY be `None`

### Requirement: OrdenItem SQLModel Table

The system MUST define `OrdenItem` with fields:

| Field | Type | Constraints |
|-------|------|-------------|
| id | int | Primary key, auto-increment |
| orden_id | int | Foreign key to `ordenes.id` |
| plato_id | int | Logical FK to `menu_items` |
| cantidad | int | Non-nullable, positive |
| precio_unitario | float | Non-nullable, snapshot at order time |

Table name MUST be `orden_items`.

#### Scenario: Line item snapshot

- GIVEN `OrdenItem` with `plato_id=1`, `cantidad=2`, `precio_unitario=12.5`
- WHEN instantiated
- THEN `precio_unitario` MUST equal `12.5` (frozen snapshot)

### Requirement: Polymorphic Schema Validation

The system MUST provide four Pydantic schemas with distinct `validate()` methods:

| Schema | Role | Validation Rules |
|--------|------|------------------|
| `OrdenItemData` | Input item | `cantidad` MUST be > 0; `plato_id` MUST be > 0 |
| `OrdenCreate` | Input for POST /ordenes | `items` MUST be non-empty list; each item validated |
| `OrdenUpdateEstado` | Input for PUT estado | `estado` MUST be valid target state |
| `OrdenResponse` | Output for all responses | All fields present; no extra validation |

No `if` or `match` on schema type is permitted.

#### Scenario: OrdenCreate validates empty items

- GIVEN `OrdenCreate(items=[])`
- WHEN `validate()` is called
- THEN it MUST raise `InvalidOrdenDataError` indicating items are required

#### Scenario: OrdenItemData validates zero cantidad

- GIVEN `OrdenItemData(plato_id=1, cantidad=0)`
- WHEN `validate()` is called
- THEN it MUST raise `InvalidOrdenDataError` indicating cantidad must be positive

#### Scenario: OrdenUpdateEstado validates invalid estado

- GIVEN `OrdenUpdateEstado(estado="inexistente")`
- WHEN `validate()` is called
- THEN it MUST raise `InvalidOrdenDataError` indicating invalid estado

### Requirement: Estado State Machine

The system MUST enforce these transitions via polymorphic validation — each current estado variant validates its own allowed next states:

| Current | Allowed Next |
|---------|-------------|
| `pendiente` | `preparando`, `cancelado` |
| `preparando` | `entregado`, `cancelado` |
| `entregado` | `pagado` |
| `pagado` | (none) |
| `cancelado` | (none) |

#### Scenario: Valid transition pendiente → preparando

- GIVEN an orden with `estado="pendiente"`
- WHEN requesting transition to `"preparando"`
- THEN validation MUST pass

#### Scenario: Invalid transition entregado → preparando

- GIVEN an orden with `estado="entregado"`
- WHEN requesting transition to `"preparando"`
- THEN it MUST raise `InvalidEstadoTransitionError`

#### Scenario: Cancel from any active state

- GIVEN an orden with `estado="preparando"`
- WHEN requesting transition to `"cancelado"`
- THEN validation MUST pass

### Requirement: Domain Exceptions

The system MUST define three concrete exceptions inheriting from `DomainError`:

| Exception | Usage | Status Code |
|-----------|-------|-------------|
| `OrdenNotFoundError` | Orden ID does not exist | 404 |
| `InvalidOrdenDataError` | Validation failure | 422 |
| `InvalidEstadoTransitionError` | Illegal state change | 400 |

#### Scenario: Exception messages

- GIVEN `OrdenNotFoundError(99)` is raised
- WHEN caught
- THEN `str(e)` MUST contain `99`

## Constraints

| Constraint | Rule | Implication |
|------------|------|-------------|
| One class per file | Rule 3 | `Orden` in `models/orden.py`; `OrdenItem` in `models/orden_item.py` |
| Polymorphic validation | Rule 1 | Each schema/estado variant implements own `validate()` |
| Functions ≤ 20 lines | Rule 8 | `validate()` methods short; extract helpers if needed |
| Type hints required | Rule 13 | All constructors and methods typed |
| Async first | Rule 14 | SQLModel compatible with async session |

## Coverage

| Path | Type | Scenarios |
|------|------|-----------|
| Happy paths | Covered | Valid model instantiation, valid state transitions |
| Edge cases | Covered | Empty items list, zero cantidad, partial nulls |
| Error states | Covered | `OrdenNotFoundError`, `InvalidOrdenDataError`, `InvalidEstadoTransitionError` |
