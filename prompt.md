# Prompt 1

## Prompt enviado

Crear la estructura inicial de Clean Architecture para un proyecto FastAPI con las carpetas:

* api
* services
* repositories
* core

indicando qué responsabilidad corresponde a cada una.

## Resultado

Funcionó correctamente.

## Aprendizaje

Permitió organizar el proyecto antes de mover la lógica del monolito.

---

# Prompt 2

## Prompt enviado

Crear los modelos SQLModel para Plato y Orden utilizando SQLite y SQLModel.

## Resultado

Funcionó correctamente.

## Aprendizaje

Se definieron las entidades principales del dominio.

---

# Prompt 3

## Prompt enviado

Implementar database.py utilizando SQLAlchemy Async Engine y SQLModel.

## Resultado

Funcionó correctamente.

## Problemas encontrados

Apareció un error relacionado con SQLite.

## Corrección

Se detectó que la instalación de Python utilizada no tenía soporte para sqlite3 y se creó un entorno virtual utilizando el Python del sistema.

---

# Prompt 4

## Prompt enviado

Implementar MenuRepository utilizando AsyncSession y operaciones CRUD.

## Resultado

Funcionó correctamente.

---

# Prompt 5

## Prompt enviado

Implementar MenuService aplicando separación de responsabilidades y manejo de errores.

## Resultado

Funcionó correctamente.

---

# Prompt 6

## Prompt enviado

Crear los endpoints de menú utilizando APIRouter y dependencias de FastAPI.

## Resultado

Funcionó correctamente.

---

# Prompt 7

## Prompt enviado

Implementar la funcionalidad completa de órdenes mediante OrdenRepository, OrdenService y router de órdenes.

## Resultado

Funcionó correctamente.

## Problemas encontrados

Fue necesario agregar los schemas para órdenes y modelar correctamente los items de la orden para calcular el total.

## Corrección

Se agregaron OrdenCreate, OrdenItem y EstadoOrdenUpdate.
