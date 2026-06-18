"""Excepciones de dominio de la aplicación."""


class DomainException(Exception):
    """Excepción base para reglas de negocio."""
    
    def __init__(self, message: str) -> None:
        """Inicializa la excepción con un mensaje."""
        self.message = message
        super().__init__(self.message)


class NotFoundException(DomainException):
    """Lanzada cuando no se encuentra un recurso."""
    pass


class PlatoNotFoundError(NotFoundException):
    """Lanzada cuando un plato no existe en el menú."""
    pass


class OrdenNotFoundError(NotFoundException):
    """Lanzada cuando una orden no existe."""
    pass
