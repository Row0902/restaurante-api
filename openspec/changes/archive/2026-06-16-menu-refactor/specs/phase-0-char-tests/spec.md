# Menu Endpoint — Phase 0 Characterization Tests

## Purpose

Freeze current behavior of the synchronous menu endpoints in `src/main.py` via characterization tests. These tests pin exact responses so subsequent refactoring phases do not accidentally change behavior.

## Requirements

### Requirement: GET /menu

The characterization test suite MUST verify that `GET /menu` returns all dishes stored in the global `menu` dict.

#### Scenario: Empty menu

- GIVEN the global `menu` dict is empty
- WHEN `GET /menu` is invoked
- THEN response status is 200 and body is `[]`

#### Scenario: Populated menu

- GIVEN two dishes exist with IDs `1` and `2`
- WHEN `GET /menu` is invoked
- THEN response status is 200 and body is a list containing both dishes in insertion order

### Requirement: POST /menu

The characterization test suite MUST verify that `POST /menu` stores any provided dict with an auto-increment string ID and returns the stored dish.

#### Scenario: Create first dish

- GIVEN the global `menu` dict is empty
- WHEN `POST /menu` with `{"nombre": "Pasta", "precio": 10}`
- THEN response status is 200 and body is `{"id": "1", "nombre": "Pasta", "precio": 10}`

#### Scenario: Create second dish

- GIVEN one dish already exists with ID `1`
- WHEN `POST /menu` with `{"nombre": "Pizza", "precio": 15}`
- THEN response status is 200 and body is `{"id": "2", "nombre": "Pizza", "precio": 15}`

#### Scenario: Empty payload

- GIVEN the global `menu` dict is empty
- WHEN `POST /menu` with `{}`
- THEN response status is 200 and body is `{"id": "1"}`

#### Scenario: Nested payload

- GIVEN the global `menu` dict is empty
- WHEN `POST /menu` with `{"extra": {"a": 1}}`
- THEN response status is 200 and body contains the nested structure unchanged

### Requirement: GET /menu/{plato_id}

The characterization test suite MUST verify that `GET /menu/{plato_id}` returns the dish for the given ID or crashes with a 500 error when the ID does not exist.

#### Scenario: Existing dish

- GIVEN a dish with ID `1` exists
- WHEN `GET /menu/1` is invoked
- THEN response status is 200 and body is the dish with ID `1`

#### Scenario: Non-existent dish

- GIVEN the global `menu` dict is empty
- WHEN `GET /menu/999` is invoked
- THEN response status is 500

### Requirement: PUT /menu/{plato_id}

The characterization test suite MUST verify that `PUT /menu/{plato_id}` fully replaces the dish at the given ID with the provided dict, preserving the original ID in the response.

#### Scenario: Replace existing dish

- GIVEN a dish with ID `1` exists
- WHEN `PUT /menu/1` with `{"nombre": "New"}`
- THEN response status is 200 and body is `{"id": "1", "nombre": "New"}`

#### Scenario: Partial update behavior

- GIVEN a dish with ID `1` has keys `nombre` and `precio`
- WHEN `PUT /menu/1` with `{"nombre": "New"}`
- THEN the `precio` key is no longer present in the response body

#### Scenario: Update non-existent dish

- GIVEN the global `menu` dict is empty
- WHEN `PUT /menu/999` with `{"nombre": "New"}`
- THEN response status is 500

### Requirement: DELETE /menu/{plato_id}

The characterization test suite MUST verify that `DELETE /menu/{plato_id}` removes the dish and returns a confirmation message, or crashes with a 500 error when the ID does not exist.

#### Scenario: Delete existing dish

- GIVEN a dish with ID `1` exists
- WHEN `DELETE /menu/1` is invoked
- THEN response status is 200 and body is `{"mensaje": "Plato eliminado", "id": "1"}`

#### Scenario: Delete non-existent dish

- GIVEN the global `menu` dict is empty
- WHEN `DELETE /menu/999` is invoked
- THEN response status is 500

### Requirement: Global state isolation

The characterization test suite MUST reset the global `menu` dict before each test to prevent cross-test leakage.

#### Scenario: Fresh state per test

- GIVEN Test A creates a dish
- WHEN Test B runs after Test A
- THEN Test B sees an empty `menu` dict at start

### Requirement: Print side effects

The characterization test suite MAY verify that `print()` statements are emitted during endpoint execution.

#### Scenario: Stdout output on GET

- GIVEN a dish with ID `1` exists
- WHEN `GET /menu/1` is invoked
- THEN the string `"Buscando plato: 1"` is printed to stdout
