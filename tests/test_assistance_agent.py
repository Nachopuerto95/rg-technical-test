"""Tests para AssistanceAgent."""

from ringr.agents.assistance import AssistanceAgent
from ringr.mocks import MockConversation, MockParser
from ringr.mocks import MockHttpClient


def test_executes_when_request_present():
    """Cuando hay una solicitud válida, ejecuta el POST."""
    conversation = MockConversation("Registro su solicitud")
    parser = MockParser({"request": "Necesito cambiar mi dirección de facturación"})
    http = MockHttpClient()

    agent = AssistanceAgent(conversation, parser, http)
    result = agent.handle_turn()

    assert result.response == "Registro su solicitud"
    assert result.action_executed is True
    assert result.request.method == "POST"
    assert result.request.url == "https://api.ringr.assistance/v1/request"
    assert result.request.body["request"] == "Necesito cambiar mi dirección de facturación"
    assert "Authorization" in result.request.headers
    assert len(http.requests) == 1


def test_does_not_execute_when_request_is_none():
    """Si no hay solicitud, no ejecuta."""
    conversation = MockConversation("¿En qué puedo ayudarle?")
    parser = MockParser({"request": None})
    http = MockHttpClient()

    agent = AssistanceAgent(conversation, parser, http)
    result = agent.handle_turn()

    assert result.action_executed is False
    assert result.request is None
    assert len(http.requests) == 0


def test_does_not_execute_when_request_is_empty():
    """Si la solicitud es un string vacío, no ejecuta."""
    conversation = MockConversation("No le he entendido")
    parser = MockParser({"request": ""})
    http = MockHttpClient()

    agent = AssistanceAgent(conversation, parser, http)
    result = agent.handle_turn()

    assert result.action_executed is False
    assert result.request is None


def test_does_not_execute_when_request_is_whitespace():
    """Si la solicitud es solo espacios, no ejecuta."""
    conversation = MockConversation("No le he entendido")
    parser = MockParser({"request": "   "})
    http = MockHttpClient()

    agent = AssistanceAgent(conversation, parser, http)
    result = agent.handle_turn()

    assert result.action_executed is False
    assert result.request is None


def test_does_not_duplicate_action():
    """Si ya ejecutó la acción, no la repite."""
    conversation = MockConversation("Registrado")
    parser = MockParser({"request": "Quiero darme de baja"})
    http = MockHttpClient()

    agent = AssistanceAgent(conversation, parser, http)

    result1 = agent.handle_turn()
    result2 = agent.handle_turn()

    assert result1.action_executed is True
    assert result2.action_executed is False
    assert len(http.requests) == 1


def test_includes_parser_data_as_headers():
    """Los datos del parser se incluyen como headers adicionales."""
    conversation = MockConversation("Registrado")
    parser = MockParser({"request": "Quiero darme de baja"})
    http = MockHttpClient()

    agent = AssistanceAgent(conversation, parser, http)
    result = agent.handle_turn()

    assert result.request.headers["request"] == "Quiero darme de baja"
