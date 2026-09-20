"""Tests para DebtAgent."""

from ringr.agents.debt import DebtAgent
from ringr.mocks import MockConversation, MockParser
from ringr.mocks import MockHttpClient


def test_executes_when_both_fields_present():
    """Cuando tiene fecha y cantidad válidas, ejecuta el POST."""
    conversation = MockConversation("Le registro el pago")
    parser = MockParser({"commitment_date": "2025-03-15", "committed_amount": 150.0})
    http = MockHttpClient()

    agent = DebtAgent(conversation, parser, http)
    result = agent.handle_turn()

    assert result.response == "Le registro el pago"
    assert result.action_executed is True
    assert result.request.method == "POST"
    assert result.request.url == "https://api.ringr.debt/v1/commitment"
    assert result.request.body["commitment_date"] == "2025-03-15"
    assert result.request.body["committed_amount"] == 150.0
    assert "Authorization" in result.request.headers
    assert len(http.requests) == 1


def test_does_not_execute_when_missing_amount():
    """Si falta la cantidad, no ejecuta."""
    conversation = MockConversation("¿Qué cantidad sería?")
    parser = MockParser({"commitment_date": "2025-03-15", "committed_amount": None})
    http = MockHttpClient()

    agent = DebtAgent(conversation, parser, http)
    result = agent.handle_turn()

    assert result.action_executed is False
    assert result.request is None
    assert len(http.requests) == 0


def test_does_not_execute_when_missing_date():
    """Si falta la fecha, no ejecuta."""
    conversation = MockConversation("¿Para qué fecha?")
    parser = MockParser({"commitment_date": None, "committed_amount": 150.0})
    http = MockHttpClient()

    agent = DebtAgent(conversation, parser, http)
    result = agent.handle_turn()

    assert result.action_executed is False
    assert result.request is None
    assert len(http.requests) == 0


def test_does_not_execute_with_invalid_date_format():
    """Si la fecha tiene formato incorrecto, no ejecuta."""
    conversation = MockConversation("No entiendo la fecha")
    parser = MockParser({"commitment_date": "15/03/2025", "committed_amount": 150.0})
    http = MockHttpClient()

    agent = DebtAgent(conversation, parser, http)
    result = agent.handle_turn()

    assert result.action_executed is False
    assert result.request is None


def test_does_not_execute_with_negative_amount():
    """Si la cantidad es negativa, no ejecuta."""
    conversation = MockConversation("Cantidad no válida")
    parser = MockParser({"commitment_date": "2025-03-15", "committed_amount": -50.0})
    http = MockHttpClient()

    agent = DebtAgent(conversation, parser, http)
    result = agent.handle_turn()

    assert result.action_executed is False
    assert result.request is None


def test_does_not_duplicate_action():
    """Si ya ejecutó la acción, no la repite en el siguiente turno."""
    conversation = MockConversation("Registrado")
    parser = MockParser({"commitment_date": "2025-03-15", "committed_amount": 150.0})
    http = MockHttpClient()

    agent = DebtAgent(conversation, parser, http)

    result1 = agent.handle_turn()
    result2 = agent.handle_turn()

    assert result1.action_executed is True
    assert result2.action_executed is False
    assert len(http.requests) == 1


def test_includes_parser_data_as_headers():
    """Los datos del parser se incluyen como headers adicionales."""
    conversation = MockConversation("Registrado")
    parser = MockParser({"commitment_date": "2025-03-15", "committed_amount": 150.0})
    http = MockHttpClient()

    agent = DebtAgent(conversation, parser, http)
    result = agent.handle_turn()

    assert result.request.headers["commitment_date"] == "2025-03-15"
    assert result.request.headers["committed_amount"] == "150.0"
