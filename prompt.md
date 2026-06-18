# Historial de Prompts (AI-Driven Development)

## Iteración 1: Comprensión y Planificación
**Prompt enviado:**
"Teniendo en cuenta el README.md codifica tal que cumpliera con todos los requisitos. Asegurate de seguir las reglas de diseño y separar la aplicación en las 4 capas de Clean Architecture."

**Qué funcionó y qué no:**
La IA analizó perfectamente los requisitos y armó un plan (`implementation_plan.md`) que dividió la app en `core`, `repositories`, `services` y `api`, notando el conflicto entre usar `SQLModel` puro en `core` y el purismo estricto de Clean Architecture, pero alineándose con el README.

**Ajuste:**
Le dimos OK al plan sin requerir cambios adicionales y validamos su asunción sobre `SQLModel`.

## Iteración 2: Implementación de Capas y Excepciones
**Prompt enviado:**
"Avanzá con la creación de los archivos para las capas `core` y `repositories`. Recordá la regla de 1 archivo por clase, clases de máximo 10 métodos, y usar inyección asíncrona."

**Qué funcionó y qué no:**
Generó correctamente las excepciones de dominio y configuró el modelo de datos con `SQLModel`. Implementó un `BaseRepository` genérico con operaciones CRUD y repositorios específicos para el Menú y las Órdenes, manteniendo dependencias unidireccionales.

## Iteración 3: Servicios, API y Testing
**Prompt enviado:**
"Completá los servicios, los routers (FastAPI), y reemplazá el `main.py` viejo. Además, armá exactamente los 10 tests pedidos (5 unitarios mockeados, 5 de integración) usando `anyio` y `ASGITransport` de `httpx`."

**Qué funcionó y qué no:**
El monolito fue reemplazado exitosamente. Se separaron los manejadores de error de FastAPI (`error_handlers.py`), mapeando correctamente `DomainException` a errores HTTP (400 y 404). Los tests se configuraron con una base de datos en memoria (`sqlite+aiosqlite:///:memory:`) permitiendo ejecución rápida y aislada, cumpliendo con la regla de >80% de coverage y TDD.

## Conclusión Final
Logramos convertir un monolito spaghetti acoplado, en una estructura **Clean Architecture** profesional, completamente asíncrona, con tipado estricto y excelente cobertura de tests.
