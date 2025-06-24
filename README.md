# AnyAgent AI Framework

**Simple. Fast. Production-ready.**

Build Telegram agents with minimal code. Like Express.js for chatbots.

## Installation

```bash
pip install anyagent-ai
```

## Quick Start

```python
from anyagent import BaseAgent, AgentRequest, AgentResponse, TelegramMessage, TextContent

class MyAgent(BaseAgent):
    def __init__(self):
        super().__init__()
    
    async def execute(self, request):
        yield AgentResponse(
            telegram_message=TelegramMessage(
                text=TextContent(text=f"Echo: {request.telegram_message.text.text}")
            )
        )
    
    async def help(self, request):
        yield AgentResponse(
            telegram_message=TelegramMessage(
                text=TextContent(text="I echo your messages!")
            )
        )

# Run it
from anyagent import AgentServer
AgentServer(MyAgent()).run()  # Starts on port 50051
```

## Features

- **🚀 Zero config** - Just inherit and implement 2 methods
- **💰 Built-in payments** - Pay-per-use with credits
- **📱 All Telegram types** - Text, images, video, audio, documents, location
- **🎛️ Interactive buttons** - Callbacks and keyboards
- **🔄 Streaming responses** - Real-time message streaming
- **🐳 Docker ready** - Production deployment included
- **⚡ gRPC based** - High performance protocol
- **🌐 Visit our website** - [anyagent.app](https://anyagent.app)

## Payment Requests

```python
from anyagent import UsagePaymentRequest

async def execute(self, request):
    # Request payment for processing
    if not request.paid:
        yield AgentResponse(
            payment_request=UsagePaymentRequest(
                key="text_analysis",  # Payment key (pricing configured in web console)
                quantity=1  # Quantity of operations (1 text analysis)
            )
        )
    
    # Process after payment
    result = analyze_text(request.telegram_message.text.text)
    yield AgentResponse(
        telegram_message=TelegramMessage(
            text=TextContent(text=result)
        )
    )
```

## Interactive Buttons

```python
from anyagent import InlineKeyboard

async def execute(self, request):
    # Handle button clicks
    if request.callback_query:
        data = request.callback_query.callback_data
        if data == "action1":
            yield AgentResponse(
                telegram_message=TelegramMessage(
                    text=TextContent(text="Button 1 clicked!")
                )
            )
        return
    
    # Send message with buttons
    yield AgentResponse(
        telegram_message=TelegramMessage(
            text=TextContent(text="Choose an action:"),
            inline_keyboard=InlineKeyboard(rows=[
                {"buttons": [
                    {"text": "Action 1", "callback_data": "action1"},
                    {"text": "Action 2", "callback_data": "action2"}
                ]}
            ])
        )
    )
```

## All Message Types

```python
async def execute(self, request):
    message = request.telegram_message
    
    if message.text:
        # Handle text
        text = message.text.text
        yield AgentResponse(...)
    
    elif message.image:
        # Handle image
        image_data = message.image.image_data
        filename = message.image.filename
        yield AgentResponse(...)
    
    elif message.video:
        # Handle video
        video_data = message.video.video_data
        yield AgentResponse(...)
    
    elif message.audio:
        # Handle audio
        audio_data = message.audio.audio_data
        yield AgentResponse(...)
    
    elif message.document:
        # Handle document
        file_data = message.document.file_data
        yield AgentResponse(...)
    
    elif message.location:
        # Handle location
        lat = message.location.latitude
        lon = message.location.longitude
        yield AgentResponse(...)
```

## Deployment

### Docker

```dockerfile
FROM python:3.11-slim
COPY . /app
WORKDIR /app
RUN pip install anyagent
CMD ["python", "agent.py"]
```

```bash
docker build -t my-agent .
docker run -p 50051:50051 my-agent
```

### Docker Compose

```yaml
version: '3.8'
services:
  agent:
    build: .
    ports:
      - "50051:50051"
    restart: unless-stopped
```

## Architecture

```
Client (Telegram Bot) 
    ↓ gRPC
Your Agent (Python)
    ↓ 
AnyAgent Framework
    ↓ Protocol Buffers
Agent Server (gRPC)
```

## API Reference

### BaseAgent

```python
class BaseAgent:
    def __init__(self)
    async def execute(self, request: AgentRequest) -> AsyncGenerator[AgentResponse, None]
    async def help(self, request: AgentRequest) -> AsyncGenerator[AgentResponse, None]
```

### AgentRequest

```python
class AgentRequest:
    telegram_message: Optional[TelegramMessage]  # User's message
    callback_query: Optional[CallbackQuery]      # Button clicks
    user_id: int                                 # User identifier
    paid: bool                                   # Payment status
    language_code: Optional[str]                 # User's language
    context: Optional[Context]                   # Conversation history
```

### AgentResponse

```python
class AgentResponse:
    telegram_message: Optional[TelegramMessage]     # Message to send
    payment_request: Optional[UsagePaymentRequest]  # Request payment
    memory: Optional[ContextMessage]                # Store meaningful content in conversation memory
```

**Memory Usage:** Use the `memory` field only for meaningful conversational content (final answers, analysis results). Don't store progress updates, loading messages, or temporary UI elements.

### TelegramMessage

```python
class TelegramMessage:
    text: Optional[TextContent]
    image: Optional[ImageContent]
    video: Optional[VideoContent]
    audio: Optional[AudioContent]
    document: Optional[DocumentContent]
    location: Optional[LocationContent]
    inline_keyboard: Optional[InlineKeyboard]
    action: Optional[TelegramAction]
```

### UsagePaymentRequest

```python
class UsagePaymentRequest:
    key: str      # Payment key identifier (configured in web console)
    quantity: int # Number of operations (e.g., 60 for 60 minutes of audio processing)
```

## Examples

See the [echo_agent](echo_agent/) directory for a complete example demonstrating all features.

## Testing

```python
import grpc
from anyagent.proto import agent_pb2, agent_pb2_grpc

# Test your agent
channel = grpc.aio.insecure_channel("localhost:50051")
stub = agent_pb2_grpc.AgentServiceStub(channel)

request = agent_pb2.AgentRequest(
    user_id=12345,
    paid=False,
    telegram_message=agent_pb2.TelegramMessage(
        text=agent_pb2.TextContent(text="Hello!")
    )
)

async for response in stub.ExecuteStream(iter([request])):
    print(response)
```

## Philosophy

AnyAgent follows the "numpy approach" - minimal required parameters, maximum flexibility. No forced metadata, no complex configuration. Just implement `execute()` and `help()`, and you're done.

## License

MIT License - build anything you want.

## Links

- 🐙 [GitHub](https://github.com/astex-said/anyagent)
- 📦 [PyPI](https://pypi.org/project/anyagent-ai/)
