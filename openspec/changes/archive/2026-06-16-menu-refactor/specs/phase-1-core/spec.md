# Core Menu Domain Specification

## Purpose

Innermost layer of Clean Architecture for the menu domain. Zero dependencies on frameworks, databases, or HTTP. Defines the data model, validation contracts, and domain exceptions.

---

## Requirements

### Requirement: SQLModel Menu Item

The system MUST define a SQLModel table class `MenuItem` with fields:

| Field | Type | Constraints |
|-------|------|-------------|
| id | int | Primary key, auto-increment |
| nombre | str | Non-nullable |
| precio | float | Non-nullable |
| categoria | str | Optional (nullable) |
| descripcion | str | Optional (nullable) |

Table name MUST be `menu_items`. The model MUST be compatible with async SQLAlchemy (aiosqlite).

#### Scenario: Valid model instantiation

- GIVEN a `MenuItem` with `nombre="Pasta"` and `precio=12.5`
- WHEN the model is instantiated
- THEN `id` MAY be `None` (not yet persisted)
- AND `categoria` and `descripcion` MAY be `None`

#### Scenario: Model table configuration

- GIVEN `MenuItem` is defined
- WHEN inspecting `__tablename__`
- THEN it MUST equal `"menu_items"`
- AND it MUST inherit from SQLModel with `table=True`

---

### Requirement: Polymorphic Validation via Schema Variants

The system MUST provide three Pydantic v2 schemas with distinct validation contracts:

| Schema | Role | Validation Rules |
|--------|------|------------------|
| `PlatoCreate` | Input for POST /menu | `nombre` MUST not be empty; `precio` MUST be > 0 |
| `PlatoUpdate` | Input for PUT /menu | `nombre` MUST not be empty if provided; `precio` MUST be > 0 if provided |
| `PlatoResponse` | Output for all responses | All fields present; no extra validation beyond type coercion |

Each schema variant MUST implement its own `validate` method. No `if` or `match` on schema type is permitted.

#### Scenario: PlatoCreate validates empty nombre

- GIVEN a `PlatoCreate` with `nombre=""` and `precio=10.0`
- WHEN `validate()` is called
- THEN it MUST raise `InvalidMenuDataError` with a message indicating `nombre` is required

#### Scenario: PlatoCreate validates non-positive precio

- GIVEN a `PlatoCreate` with `nombre="Pasta"` and `precio=0.0`
- WHEN `validate()` is called
- THEN it MUST raise `InvalidMenuDataError` with a message indicating `precio` must be positive

#### Scenario: PlatoUpdate validates partial fields

- GIVEN a `PlatoUpdate` with only `precio=-5.0`
- WHEN `validate()` is called
- THEN it MUST raise `InvalidMenuDataError` with a message indicating `precio` must be positive

#### Scenario: PlatoUpdate accepts empty payload

- GIVEN a `PlatoUpdate` with no fields set
- WHEN `validate()` is called
- THEN it MUST pass without raising

#### Scenario: PlatoResponse returns all fields

- GIVEN a `PlatoResponse` built from `MenuItem(id=1, nombre="Pasta", precio=12.5)`
- WHEN it is serialized
- THEN it MUST include `id`, `nombre`, `precio`, `categoria`, `descripcion`

---

### Requirement: Domain Exceptions

The system MUST define a base `DomainError` (or `BaseDomainError`) class and two concrete exceptions:

| Exception | Usage | Status Code (translated by API layer) |
|-----------|-------|----------------------------------------|
| `MenuNotFoundError` | `plato_id` does not exist in persistence | 404 |
| `InvalidMenuDataError` | Validation failure in schema `validate()` | 400 |

Both MUST inherit from the base domain exception. They MUST carry a descriptive message.

#### Scenario: MenuNotFoundError carries message

- GIVEN `MenuNotFoundError("Menu item 99 not found.")` is raised
- WHEN the exception is caught
- THEN `str(e)` MUST equal `"Menu item 99 not found."`

#### Scenario: InvalidMenuDataError carries message

- GIVEN `InvalidMenuDataError("precio must be positive.")` is raised
- WHEN the exception is caught
- THEN `str(e)` MUST equal `"precio must be positive."`

---

## Constraints

| Constraint | Rule | Implication |
|------------|------|-------------|
| One class per file | Rule 3 | `MenuItem` lives alone in `models/menu.py`; schemas are grouped as an exception in `schemas/menu.py` |
| Functions ≤ 20 lines | Rule 8 | `validate()` methods must be short; extract helpers if needed |
| Classes ≤ 10 public methods | Rule 9 | Each schema and model exposes at most 10 public methods |
| Type hints on all public functions | Rule 13 | Every `validate()` and constructor must have typed signatures |
| Async first | Rule 14 | SQLModel model must work with async SQLAlchemy session |
| Max file 500 lines | Rule 2 | Each file must stay well under 500 lines |

---

## Coverage

| Path | Type | Scenarios |
|------|------|-----------|
| Happy paths | Covered | Model instantiation, valid schema creation, partial update |
| Edge cases | Covered | Empty payload on update, zero/negative precio, empty nombre |
| Error states | Covered | `MenuNotFoundError`, `InvalidMenuDataError` with descriptive messages |

---

## Next Step

Ready for `sdd-design` (Phase 1 core layer design) or `sdd-tasks` (task breakdown for core layer implementation).
