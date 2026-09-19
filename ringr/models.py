"""Contratos y tipos compartidos del sistema de agentes."""

from dataclasses import dataclass, field
from typing import Protocol
from ringr.integrations.http import HttpRequest


class ConversationModel(Protocol):
    """Genera una respuesta al usuario en un turno de conversación."""

    def answer_user(self) -> str: ...


class ParserModel(Protocol):
    """Extrae datos estructurados del contexto de la conversación."""

    def parse_data(self) -> dict: ...


@dataclass(frozen=True)
class TurnResult:
    """Resultado de un turno: respuesta, datos parseados y acción ejecutada."""

    response: str
    parsed_data: dict = field(default_factory=dict)
    action_executed: bool = False
    request: HttpRequest | None = None
