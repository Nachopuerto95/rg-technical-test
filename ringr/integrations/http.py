"""Capa HTTP: tipos de request/response y contrato de cliente."""

from dataclasses import dataclass, field
from typing import Protocol


@dataclass(frozen=True)
class HttpRequest:
    """Petición HTTP inmutable."""

    method: str
    url: str
    headers: dict[str, str] = field(default_factory=dict)
    body: dict = field(default_factory=dict)


@dataclass(frozen=True)
class HttpResponse:
    """Respuesta HTTP."""

    status_code: int
    body: dict = field(default_factory=dict)


class HttpClient(Protocol):
    """Contrato para envío de peticiones HTTP."""

    def send(self, request: HttpRequest) -> HttpResponse: ...
