"""Tests estaticos de dependencias entre capas."""

import ast
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parents[2] / "src"


def _imports_de_archivo(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    return {modulo for node in ast.walk(tree) for modulo in _modulos_importados(node)}


def _modulos_importados(node: ast.AST) -> set[str]:
    if isinstance(node, ast.Import):
        return {alias.name for alias in node.names}
    if isinstance(node, ast.ImportFrom) and node.module:
        return {node.module}
    return set()


def test_api_no_importa_capas_inferiores() -> None:
    """Verifica que API solo dependa de la capa de servicios."""
    prohibidos = ("core", "repositories", "sqlmodel")
    for path in (SRC_DIR / "api").rglob("*.py"):
        imports = _imports_de_archivo(path)
        no_permitidos = _imports_prohibidos(imports, prohibidos)
        assert not no_permitidos, f"{path}: {no_permitidos}"


def test_api_no_menciona_detalles_de_infraestructura() -> None:
    """Verifica que API no conozca detalles in-memory ni SQLModel."""
    prohibidos = ("InMemory", "in_memory", "SQLModel", "sqlmodel")
    for path in (SRC_DIR / "api").rglob("*.py"):
        fuente = path.read_text(encoding="utf-8")
        no_permitidos = [texto for texto in prohibidos if texto in fuente]
        assert not no_permitidos, f"{path}: {no_permitidos}"


def _imports_prohibidos(
    imports: set[str],
    prohibidos: tuple[str, ...],
) -> list[str]:
    return [
        modulo
        for modulo in imports
        if any(modulo == capa or modulo.startswith(f"{capa}.") for capa in prohibidos)
    ]
