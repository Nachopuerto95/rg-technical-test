"""Demo del sistema de agentes conversacionales."""

from ringr.agents.debt import DebtAgent
from ringr.agents.assistance import AssistanceAgent
from ringr.mocks import MockConversation, MockParser, MockHttpClient


def demo_debt_agent():
    print("=== DebtAgent: compromiso de pago ===\n")

    conversation = MockConversation("Perfecto, le registro el pago para el 15 de marzo")
    parser = MockParser({"commitment_date": "2025-03-15", "committed_amount": 150.0})
    http = MockHttpClient()

    agent = DebtAgent(conversation, parser, http)
    result = agent.handle_turn()

    print(f"Respuesta: {result.response}")
    print(f"Datos parseados: {result.parsed_data}")
    print(f"Acción ejecutada: {result.action_executed}")
    if result.request:
        print(f"POST -> {result.request.url}")
        print(f"Body: {result.request.body}")
        print(f"Headers: {result.request.headers}")

    # Segundo turno: no debe repetir la acción
    print("\n--- Segundo turno (no debe repetir) ---")
    result2 = agent.handle_turn()
    print(f"Acción ejecutada: {result2.action_executed}")


def demo_assistance_agent():
    print("\n=== AssistanceAgent: registro de solicitud ===\n")

    conversation = MockConversation("Entendido, registro su solicitud")
    parser = MockParser({"request": "Necesito cambiar mi dirección de facturación"})
    http = MockHttpClient()

    agent = AssistanceAgent(conversation, parser, http)
    result = agent.handle_turn()

    print(f"Respuesta: {result.response}")
    print(f"Datos parseados: {result.parsed_data}")
    print(f"Acción ejecutada: {result.action_executed}")
    if result.request:
        print(f"POST -> {result.request.url}")
        print(f"Body: {result.request.body}")


if __name__ == "__main__":
    demo_debt_agent()
    demo_assistance_agent()
