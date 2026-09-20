"""Agente de atención al cliente: registra solicitudes para gestión humana."""

from ringr.agents.base import BaseAgent
from ringr.config import AUTH_TOKEN, ASSISTANCE_ENDPOINT
from ringr.integrations.http import HttpRequest


class AssistanceAgent(BaseAgent):
    """Agente que parsea solicitudes del usuario y las registra."""

    def _validate(self, parsed_data: dict) -> dict:
        validated = {}

        request = parsed_data.get("request")
        if isinstance(request, str) and request.strip():
            validated["request"] = request.strip()

        return validated

    def _should_execute(self, validated_data: dict) -> bool:
        return "request" in validated_data

    def _build_request(self, validated_data: dict) -> HttpRequest:
        return HttpRequest(
            method="POST",
            url=ASSISTANCE_ENDPOINT,
            headers={
                "Authorization": f"Bearer {AUTH_TOKEN}",
                "Content-Type": "application/json",
            },
            body=validated_data,
        )
