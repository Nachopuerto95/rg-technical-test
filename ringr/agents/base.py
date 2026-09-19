"""Agente base con Template Method para el ciclo de un turno de conversación."""

from abc import ABC, abstractmethod
from ringr.models import ConversationModel, ParserModel, TurnResult
from ringr.integrations.http import HttpClient, HttpRequest


class BaseAgent(ABC):
    """Agente conversacional base. Dependencias inyectadas por constructor."""

    def __init__(
        self,
        conversation_model: ConversationModel,
        parser_model: ParserModel,
        http_client: HttpClient,
    ) -> None:
        self._conversation_model = conversation_model
        self._parser_model = parser_model
        self._http_client = http_client
        self._action_executed = False

    def handle_turn(self) -> TurnResult:
        """Ejecuta un turno: responder, parsear, validar y ejecutar acción."""
        try:
            response = self._conversation_model.answer_user()
        except Exception:
            return TurnResult(response="Lo siento, ha ocurrido un error.")

        try:
            parsed_data = self._parser_model.parse_data()
        except Exception:
            return TurnResult(response="Lo siento, ha ocurrido un error.")

        validated_data = self._validate(parsed_data)

        request = None
        action_executed = False

        if self._should_execute(validated_data) and not self._action_executed:
            try:
                request = self._build_request(validated_data)
                request = self._merge_parser_headers(request, parsed_data)
                self._http_client.send(request)
                self._action_executed = True
                action_executed = True
            except Exception:
                pass

        return TurnResult(
            response=response,
            parsed_data=parsed_data,
            action_executed=action_executed,
            request=request,
        )

    def _merge_parser_headers(
        self, request: HttpRequest, parsed_data: dict
    ) -> HttpRequest:
        """Incluye los datos del parser como headers adicionales en la request."""
        parser_headers = {k: str(v) for k, v in parsed_data.items() if v is not None}
        merged = {**parser_headers, **request.headers}
        return HttpRequest(
            method=request.method,
            url=request.url,
            headers=merged,
            body=request.body,
        )

    @abstractmethod
    def _validate(self, parsed_data: dict) -> dict:
        """Valida y normaliza los datos parseados."""
        ...

    @abstractmethod
    def _should_execute(self, validated_data: dict) -> bool:
        """Decide si se debe ejecutar la acción externa."""
        ...

    @abstractmethod
    def _build_request(self, validated_data: dict) -> HttpRequest:
        """Construye la request HTTP para la acción externa."""
        ...
