"""Agente de cobros: registra compromisos de pago de deudas pendientes."""

from datetime import datetime
from ringr.agents.base import BaseAgent
from ringr.config import AUTH_TOKEN, DEBT_ENDPOINT
from ringr.integrations.http import HttpRequest


class DebtAgent(BaseAgent):
    """Agente que parsea fecha y cantidad de pago y registra el compromiso."""

    def _validate(self, parsed_data: dict) -> dict:
        validated = {}

        date = parsed_data.get("commitment_date")
        if isinstance(date, str):
            try:
                datetime.strptime(date, "%Y-%m-%d")
                validated["commitment_date"] = date
            except ValueError:
                pass

        amount = parsed_data.get("committed_amount")
        if isinstance(amount, (int, float)) and amount > 0:
            validated["committed_amount"] = float(amount)

        return validated

    def _should_execute(self, validated_data: dict) -> bool:
        return (
            "commitment_date" in validated_data
            and "committed_amount" in validated_data
        )

    def _build_request(self, validated_data: dict) -> HttpRequest:
        return HttpRequest(
            method="POST",
            url=DEBT_ENDPOINT,
            headers={
                "Authorization": f"Bearer {AUTH_TOKEN}",
                "Content-Type": "application/json",
            },
            body=validated_data,
        )
