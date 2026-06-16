# Restaurante API — Agent Guide

## Project nature

This is a **course project** (AI-Driven Development). The repo starts as a deliberate spaghetti monolith in `src/main.py` with bad practices. Students refactor incrementally toward Clean Architecture. The current state is **intentionally bad** — do not treat it as an example to follow.

- Python 3.14 (see `.python-version`)
- Package manager: `uv` (has `uv.lock`, `.envrc` uses `layout uv`)
- Stack: FastAPI / SQLModel / SQLite+aiosqlite / Pydantic v2 / pydantic-settings

## Developer commands

```bash
uv sync                          # Install dependencies (creates/updates .venv)
cp .env.template .env            # Configuration (required before running)
fastapi dev src/main.py          # Dev server with hot reload

pytest -v                        # All tests
pytest -v --cov=src --cov-report=term-missing   # With coverage
pytest -v test/unit              # Unit tests only
pytest -v test/integration       # Integration tests only

ruff check src/ test/            # Lint
ruff check --fix src/ test/      # Auto-fix
ruff format src/ test/           # Format
ruff format --check src/ test/   # Check format only

ty check src/ test/              # Type checks

pre-commit run --all-files       # Manually run all hooks
```

## Testing quirks

- `pythonpath = ["src"]` in `pyproject.toml` — test imports are relative to `src/`, not project root
- `testpaths = ["test"]` — pytest only discovers tests in `test/`
- Current tests use `TestClient` (sync). Target state uses `httpx` `ASGITransport` (async)
- CWD matters: test and dev server expect `.env` at project root

## Architecture roadmap

| Layer | Current | Target |
|-------|---------|--------|
| **api/** | — (all in `main.py`) | Routers, deps, HTTP layer |
| **services/** | — | Business logic, receives repos via constructor |
| **repositories/** | — | DB access layer |
| **core/** | — | SQLModel models, Pydantic schemas, pydantic-settings config |

Design principle: `api → services → repositories → core` — one-way dependency. No layer skips the next.

## ruff & ty config (pyproject.toml)

- Line length: 88
- Quotes: double
- Docstring convention: Google
- Target: py314
- Lint extras: B, D, I, N, Q, UP (with D203/D213/D104 ignored)
- pre-commit hooks run both `ruff check --fix` and `ruff-format`
- ty type-checks both `src/` and `test/`, python-version 3.14
- ruff fix is enabled by default

## Mandatory design rules

These are course constraints — they apply to ALL code written or reviewed in this repo.

| # | Rule | Description |
|---|------|-------------|
| 1 | **Validación polimórfica** | Use polymorphism for validation — no `if`/`match` on type. Each variant implements its own validate method. |
| 2 | **Máximo 500 líneas por archivo** | No file exceeds 500 source lines (excluding blanks/comments). |
| 3 | **Una clase por archivo** | One class per file, filename matches class name in snake_case. No exceptions. |
| 4 | **Separación en capas** | `api/` → `services/` → `repositories/` → `core/`. One-way dependency. No layer skipping. |
| 5 | **Clean Code** | Intention-revealing names, one thing per function, no comments explaining what (code must self-document), no hardcoded values. |
| 6 | **SRP** | One reason to change per class/module. Split if it has more than one. |
| 7 | **Clean Architecture** | Business rules independent of frameworks, UI, DB, and external agents. Dependencies point inward. Dependency inversion at layer boundaries. |
| 8 | **Funciones ≤ 20 líneas** | No function/method body exceeds 20 lines (signature and docstring excluded). Extract sub-functions. |
| 9 | **Clases ≤ 10 métodos públicos** | No class exposes more than 10 public methods. Extract responsibilities. |
| 10 | **TDD** | Every new or modified function must have a supporting test. No code without tests. |
| 11 | **Test por capa** | Services → unit tests with mocked repos. API → integration tests with HTTP client. Core → pure unit tests. Do not mix test responsibilities. |
| 12 | **Cobertura ≥ 80%** | Coverage report must show at least 80% on `src/`. No merge below that. |
| 13 | **Type hints en toda función pública** | All public functions/methods must have typed params and return. `Any` only as last resort and justified. |
| 14 | **Async first** | All I/O (DB, HTTP, filesystem) must be async/await. Do not mix sync and async in the same call chain. |
| 15 | **Manejo de errores consistente** | Use domain exceptions in `core/`. API layer translates to HTTPException with descriptive code/message. No bare 500s from unhandled errors. |

## Environment

- `.env` at project root — copy from `.env.template`
- `DATABASE_URL=sqlite+aiosqlite:///./restaurante.db` — local SQLite file
- `.envrc` uses `layout uv` — for direnv users, auto-activates uv-managed venv
- `.gitignore` excludes: `.env`, `.venv/`, `*.db`, `__pycache__/`, `.atl/`, `.engram/`
