from __future__ import annotations


class NotFoundError(Exception):
    """Domain exception for resources not found."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class BadRequestError(Exception):
    """Domain exception for business validation failures."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message
