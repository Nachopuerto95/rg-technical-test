"""Mocks para simular dependencias externas con datos fijos."""

from ringr.integrations.http import HttpRequest, HttpResponse


class MockConversation:
    """Devuelve una respuesta fija al llamar a answer_user."""

    def __init__(self, response: str) -> None:
        self.response = response

    def answer_user(self) -> str:
        return self.response


class MockParser:
    """Devuelve datos fijos al llamar a parse_data."""

    def __init__(self, data: dict) -> None:
        self.data = data

    def parse_data(self) -> dict:
        return self.data


class MockHttpClient:
    """Graba las requests en vez de enviarlas. Devuelve 200 OK."""

    def __init__(self) -> None:
        self.requests: list[HttpRequest] = []

    def send(self, request: HttpRequest) -> HttpResponse:
        self.requests.append(request)
        return HttpResponse(status_code=200)
