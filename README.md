# Prueba técnica - Delivery Engineer

Sistema de agentes conversacionales en Python. Cada agente gestiona turnos de conversación, extrae datos estructurados y ejecuta acciones contra APIs externas simuladas.

## Setup y ejecución

```bash
python -m venv .venv
.venv/Scripts/activate        # Windows
# source .venv/bin/activate   # Linux/Mac

pip install -e ".[dev]"

pytest -v                     # 13 tests
python main.py                # demo del flujo completo
```

## Estructura

```
ringr/
├── agents/
│   ├── base.py           # Ciclo de vida del turno (Template Method)
│   ├── debt.py           # Compromisos de pago
│   └── assistance.py     # Registro de solicitudes
├── integrations/
│   └── http.py           # HttpRequest, HttpResponse, contrato HttpClient
├── config.py             # Token y endpoints
├── models.py             # Protocols y TurnResult
└── mocks.py              # Simulación de LLM y HTTP
tests/
├── test_debt_agent.py
└── test_assistance_agent.py
main.py
```

## Decisiones de diseño

### Template Method para handle_turn

El ciclo de un turno es siempre: responder al usuario, parsear datos, validar, y ejecutar si toca. Ese esqueleto no cambia entre agentes, lo que cambia es qué valida cada uno y qué request construye.

Consideré usar composición (inyectar las funciones de validación como estrategias), pero los agentes son subtipos naturales de BaseAgent, no configuraciones de uno genérico. Un DebtAgent no es "un BaseAgent configurado con validación de fechas", es un agente de cobros que hereda un ciclo de vida común. La herencia encaja mejor aquí.

Añadir un agente nuevo es crear una subclase con tres métodos. No se toca nada existente.

### Protocol para las dependencias, ABC para la base

ConversationModel, ParserModel y HttpClient son Protocols. BaseAgent es ABC. La razón es distinta para cada caso:

Los modelos y el cliente HTTP son dependencias externas, el agente las recibe, no las define. Con Protocol cualquier objeto que tenga los métodos correctos es válido sin heredar de mi código. Si en producción el ConversationModel es un wrapper de GPT-4, no debería tener que heredar de mi clase para funcionar.

BaseAgent sí es ABC porque ahí la herencia es intencionada. Quiero que Python me obligue a implementar _validate, _should_execute y _build_request en cada agente. Si se me olvida uno, peta al instanciar.

### Inmutabilidad en HttpRequest y TurnResult

Son dataclasses frozen. Una vez construida la request, no se puede modificar. Esto importa porque la request pasa por varios pasos (construcción, merge de headers, envío) y quiero garantizar que lo que se inspecciona en tests es exactamente lo que se enviaría.

Cuando necesito añadir los headers del parser, creo una instancia nueva en vez de mutar la existente. Más código, pero cada request es siempre un objeto completo y consistente.

### Inyección de dependencias

Los agentes reciben todo por constructor: modelos, parser, cliente HTTP. No crean nada internamente. Esto permite pasar mocks en tests o implementaciones reales en producción sin cambiar una línea del agente.

## Ambigüedades resueltas

### Duplicados

El enunciado dice "no se envían duplicados". Interpreté que una vez ejecutada la acción, no se repite en esa conversación. Usé un flag booleano: si ya se hizo el POST, no se vuelve a hacer aunque los datos sigan presentes en turnos posteriores.

### Validación

No hay reglas de validación definidas, así que apliqué lo razonable:
- **Fecha**: formato yyyy-mm-dd validado con `datetime.strptime`, que también rechaza fechas imposibles (30 de febrero, etc.).
- **Cantidad**: número mayor que 0, normalizado a float.
- **Solicitud**: string no vacío tras strip.

### Headers del parser

Los datos del ParserModel se incluyen como headers además de ir en el body. Filtro valores None (no tiene sentido meter "None" como string). Los headers del agente (Authorization, Content-Type) tienen prioridad si hay conflicto.

### Manejo de errores

handle_turn tiene try/except separados para ConversationModel, ParserModel y el envío HTTP. Si falla cualquiera de ellos, el turno devuelve un mensaje de error genérico. Así el usuario siempre recibe algo y el agente nunca se queda colgado.  

### Simulación HTTP

MockHttpClient graba requests en una lista y devuelve 200 OK. La separación con Protocol permite sustituirlo por un cliente real sin tocar los agentes.

No incluí la HttpResponse en TurnResult porque el enunciado dice asumir 200 OK, guardar un campo que siempre vale lo mismo es código muerto.

## Tests

13 tests cubriendo ambos agentes: caso correcto, datos faltantes, datos inválidos (fecha mal formada, cantidad negativa, string vacío), prevención de duplicados, y headers del parser.

## Proceso

Python no es mi lenguaje principal, como comenté en la entrevista. He usado IA como herramienta de asistencia para la implementación, igual que hago en mi trabajo actual. Mi base de OOP viene de C++ (42 Madrid), lo que me ha facilitado trasladar los patrones a Python. El dominio sí es el mío: construyo agentes de voz con IA en producción a diario, y eso me ha dado el contexto para resolver las ambigüedades con criterio.

Mi flujo de trabajo ha sido:

1. Analizar el enunciado, identificar las ambigüedades y decidir cómo resolverlas antes de escribir código.
2. Definir la estructura del proyecto y los contratos (Protocols, dataclasses) como base.
3. Implementar de forma incremental: tipos base, agente base, agentes concretos, tests. Cada paso revisando que lo anterior sigue funcionando.
4. Revisar SOLID y refactorizar donde tenía sentido real (centralizar constantes, filtrar None en headers), sin añadir complejidad por añadir.
5. Escribir tests que cubran no solo el happy path sino los edge cases que pueden darse en una conversación real (datos parciales, formatos incorrectos, turnos duplicados).

Cada decisión del código la puedo explicar y justificar.