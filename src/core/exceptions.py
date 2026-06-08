"""Excepciones de dominio del restaurante."""


class RestauranteError(Exception):
    """Base para todas las excepciones de dominio del restaurante."""

    ...


class NoEncontradoError(RestauranteError):
    """Base para recursos no encontrados."""

    ...


class PlatoNoEncontrado(NoEncontradoError):
    """Se lanza cuando un plato no existe en la base de datos."""

    def __init__(self, plato_id: int) -> None:
        super().__init__(f"Plato con id {plato_id} no encontrado")
        self.plato_id = plato_id


class OrdenNoEncontrada(NoEncontradoError):
    """Se lanza cuando una orden no existe en la base de datos."""

    def __init__(self, orden_id: int) -> None:
        super().__init__(f"Orden con id {orden_id} no encontrada")
        self.orden_id = orden_id


class PlatoInvalido(RestauranteError):
    """Se lanza cuando los datos de un plato no cumplen las reglas de validación."""

    def __init__(self, detalle: str) -> None:
        super().__init__(f"Plato inválido: {detalle}")


class EstadoInvalido(RestauranteError):
    """Se lanza cuando se intenta cambiar una orden a un estado no permitido."""

    def __init__(self, estado: str) -> None:
        super().__init__(f"Estado '{estado}' no es válido")
        self.estado = estado
