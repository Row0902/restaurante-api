# Code Review Rules

## Reglas obligatorias de diseño

| # | Regla | Descripción |
|---|-------|-------------|
| 1 | **Validación polimórfica** | Usar polimorfismo para validar — no condicionales (`if`/`match`) que pregunten el tipo. Cada variante implementa su propio método de validación. |
| 2 | **Máximo 500 líneas por archivo** | Ningún archivo del proyecto debe exceder las 500 líneas de código fuente (sin contar blanks/comentarios). |
| 3 | **Un archivo por clase** | Cada clase vive en su propio archivo. Sin excepciones. El nombre del archivo debe coincidir con el nombre de la clase en snake_case. |
| 4 | **Separación en capas** | `api/` → `services/` → `repositories/` → `core/`. La dependencia es unidireccional. Ninguna capa superior puede saltarse una capa intermedia. |
| 5 | **Clean Code** | Nombres que revelen intención, funciones que hagan una sola cosa, sin comentarios que expliquen el qué (el código debe explicarse solo), sin valores hardcodeados. |
| 6 | **SRP (Single Responsibility Principle)** | Cada clase/modulo debe tener una única razón para cambiar. Si una clase tiene más de una responsabilidad, dividir. |
| 7 | **Clean Architecture** | Reglas de negocio independientes de frameworks, UI, DB y agentes externos. Los detalles dependen de las abstracciones, no al revés. Inversión de dependencias en los límites de capa. |
| 8 | **Funciones ≤ 20 líneas** | Ninguna función/método debe exceder las 20 líneas de código (cuerpo, sin firma ni docstring). Si lo hace, extraer sub-funciones. |
| 9 | **Clases ≤ 10 métodos públicos** | Ninguna clase debe exponer más de 10 métodos públicos. Si los supera, extraer responsabilidades en clases separadas. |
| 10 | **Tests primero (TDD)** | Toda función nueva o modificada debe tener test que la respalde. No se acepta código sin test. |
| 11 | **Test por capa** | Services → unitarios con repos mockeados. API → integración con cliente HTTP. Core → unitarios puros. No mezclar responsabilidades de testeo. |
| 12 | **Cobertura ≥ 80%** | El reporte de cobertura debe mostrar al menos 80% en `src/`. Si baja, no se mergea. |
| 13 | **Type hints en toda función pública** | Toda función/método público debe tener tipos en parámetros y retorno. `Any` solo como último recurso y justificado. |
| 14 | **Async first** | Toda operación de I/O (DB, HTTP, filesystem) debe ser async/await. No mezclar funciones sync con async en la misma cadena de llamadas. |
| 15 | **Manejo de errores consistente** | Usar excepciones de dominio propias en `core/`. La capa `api/` las traduce a HTTPException con código y mensaje descriptivo. Prohibido dejar 500 genéricos por errores no controlados. |
