# AnyAgent Framework

[![PyPI version](https://badge.fury.io/py/anyagent-ai.svg)](https://badge.fury.io/py/anyagent-ai)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A standardized framework for building gRPC-based AI agents that integrate seamlessly with Telegram bots. AnyAgent provides a complete SDK for handling all Telegram message types, payments, and interactive UI components.

## 🚀 Quick Start

### Installation

```bash
pip install anyagent-ai
```

### Create Your First Agent in 5 Minutes

```python
from anyagent import BaseAgent, AgentResponse, TelegramMessage, TextContent

class MyAgent(BaseAgent):
    async def execute(self, request):
        # Echo back any text message
        if request.telegram_message and request.telegram_message.text:
            text = request.telegram_message.text.text
            
            yield AgentResponse(
                telegram_message=TelegramMessage(
                    text=TextContent(text=f"You said: {text}")
                )
            )

# Run the agent
if __name__ == "__main__":
    from anyagent import AgentServer
    
    agent = MyAgent()
    server = AgentServer(agent)
    server.run(port=50051)
```

## 📖 Complete Documentation

### Architecture Overview

AnyAgent uses a gRPC-based architecture where:
1. **Telegram Bot Server** receives messages from users
2. **Bot Server** converts them to gRPC requests
3. **Your Agent** processes requests and returns responses
4. **Bot Server** sends responses back to Telegram

```
Telegram User <-> Telegram API <-> Bot Server <-> gRPC <-> Your Agent
```

### Core Concepts

#### 1. BaseAgent Class

All agents inherit from `BaseAgent` and implement the `execute` method:

```python
from anyagent import BaseAgent, AgentRequest, AgentResponse

class MyAgent(BaseAgent):
    async def execute(self, request: AgentRequest) -> AsyncGenerator[AgentResponse, None]:
        # Process request and yield responses
        pass
```

#### 2. Request Structure

Every request contains:
- `telegram_message`: Incoming message (text, image, video, etc.)
- `callback_query`: Button press events
- `reply_message`: When user replies to a message
- `context`: Conversation history and metadata
- `paid`: Payment status
- `language_code`: User's language
- `user_id`: Unique user identifier

#### 3. Response Structure

Responses can contain:
- `telegram_message`: Message to send back
- `payment_request`: Request payment from user
- `memory`: Store conversation context

### 📋 Supported Message Types

#### Text Messages
```python
from anyagent import TelegramMessage, TextContent

yield AgentResponse(
    telegram_message=TelegramMessage(
        text=TextContent(text="Hello, World!")
    )
)
```

#### Images
```python
from anyagent import ImageContent

yield AgentResponse(
    telegram_message=TelegramMessage(
        image=ImageContent(
            image_data=image_bytes,
            caption="A beautiful image",
            filename="image.jpg"
        )
    )
)
```

#### Videos
```python
from anyagent import VideoContent

yield AgentResponse(
    telegram_message=TelegramMessage(
        video=VideoContent(
            video_data=video_bytes,
            caption="Check out this video",
            filename="video.mp4"
        )
    )
)
```

#### Audio
```python
from anyagent import AudioContent

yield AgentResponse(
    telegram_message=TelegramMessage(
        audio=AudioContent(
            audio_data=audio_bytes,
            filename="audio.mp3"
        )
    )
)
```

#### Documents
```python
from anyagent import DocumentContent

yield AgentResponse(
    telegram_message=TelegramMessage(
        document=DocumentContent(
            file_data=file_bytes,
            filename="document.pdf"
        )
    )
)
```

#### Locations
```python
from anyagent import LocationContent

yield AgentResponse(
    telegram_message=TelegramMessage(
        location=LocationContent(
            latitude=37.7749,
            longitude=-122.4194
        )
    )
)
```

### 🎛️ Interactive UI Components

#### Inline Keyboards

Create interactive buttons for users:

```python
from anyagent import InlineKeyboard, InlineButtonRow, InlineButton

keyboard = InlineKeyboard(rows=[
    InlineButtonRow(buttons=[
        InlineButton.callback_button("✅ Accept", "accept"),
        InlineButton.callback_button("❌ Decline", "decline")
    ]),
    InlineButtonRow(buttons=[
        InlineButton.url_button("📖 Documentation", "https://docs.example.com"),
        InlineButton.url_button("🌐 Website", "https://example.com")
    ])
])

yield AgentResponse(
    telegram_message=TelegramMessage(
        text=TextContent(text="Please choose an option:"),
        inline_keyboard=keyboard
    )
)
```

#### Handling Button Clicks

```python
async def execute(self, request):
    if request.callback_query:
        callback_data = request.callback_query.callback_data
        
        if callback_data == "accept":
            yield AgentResponse(
                telegram_message=TelegramMessage(
                    text=TextContent(text="You accepted! ✅")
                )
            )
        elif callback_data == "decline":
            yield AgentResponse(
                telegram_message=TelegramMessage(
                    text=TextContent(text="You declined ❌")
                )
            )
```

### 💰 Payment System

Request payments for premium features:

```python
from anyagent import UsagePaymentRequest

# Check if user has paid
if not request.paid:
    yield AgentResponse(
        payment_request=UsagePaymentRequest(
            key="premium_feature",  # Payment key from web console
            quantity=1  # Number of uses
        )
    )
else:
    # Provide premium feature
    yield AgentResponse(
        telegram_message=TelegramMessage(
            text=TextContent(text="Premium feature activated! 🌟")
        )
    )
```

### 🧠 Context and Memory

Store conversation history:

```python
from anyagent import ContextMessage

# Store assistant's response in memory
yield AgentResponse(
    telegram_message=TelegramMessage(
        text=TextContent(text="I'll remember that!")
    ),
    memory=ContextMessage(
        role="assistant",
        content="User's favorite color is blue"
    )
)

# Access previous context
if request.context:
    for message in request.context.messages:
        print(f"{message.role}: {message.content}")
```

### 🎭 Bot Actions

Show typing indicators:

```python
from anyagent import TelegramAction

yield AgentResponse(
    telegram_message=TelegramMessage(
        text=TextContent(text="Processing your request..."),
        action=TelegramAction.TYPING
    )
)
```

Available actions:
- `TYPING` - Shows "typing..." indicator
- `UPLOADING_PHOTO` - Shows "uploading photo..." indicator
- `UPLOADING_VIDEO` - Shows "uploading video..." indicator
- `UPLOADING_DOCUMENT` - Shows "uploading document..." indicator
- `UPLOADING_AUDIO` - Shows "uploading audio..." indicator
- `RECORDING_VIDEO` - Shows "recording video..." indicator
- `RECORDING_AUDIO` - Shows "recording audio..." indicator

### 🔄 Streaming Responses

For real-time responses:

```python
async def execute(self, request):
    # Send initial message
    yield AgentResponse(
        telegram_message=TelegramMessage(
            text=TextContent(text="Processing"),
            action=TelegramAction.TYPING
        )
    )
    
    # Stream updates
    for i in range(5):
        await asyncio.sleep(1)
        yield AgentResponse(
            telegram_message=TelegramMessage(
                text=TextContent(text=f"Progress: {i+1}/5")
            )
        )
```

### 🚀 Deployment

#### Using Docker

1. Create a `Dockerfile`:

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy agent code
COPY . .

# Expose gRPC port
EXPOSE 50051

# Run the agent
CMD ["python", "agent.py"]
```

2. Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  my_agent:
    build: .
    ports:
      - "50051:50051"
    environment:
      - GRPC_PORT=50051
    restart: unless-stopped
```

3. Deploy:

```bash
docker-compose up -d
```

#### Environment Variables

- `GRPC_PORT` - Port for gRPC server (default: 50051)
- `MAX_WORKERS` - Number of worker threads (default: 10)

### 🛠️ Advanced Features

#### Custom Help Handler

```python
class MyAgent(BaseAgent):
    async def help(self, request):
        """Custom help command handler"""
        yield AgentResponse(
            telegram_message=TelegramMessage(
                text=TextContent(text="""
🤖 MyAgent Help

Commands:
/start - Start the bot
/help - Show this help
/status - Check status

Send me any message and I'll help you!
                """)
            )
        )
```

#### Error Handling

```python
async def execute(self, request):
    try:
        # Your logic here
        pass
    except Exception as e:
        yield AgentResponse(
            telegram_message=TelegramMessage(
                text=TextContent(text=f"❌ Error: {str(e)}")
            )
        )
```

#### Logging

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MyAgent(BaseAgent):
    async def execute(self, request):
        logger.info(f"Received request from user {request.user_id}")
        # Your logic here
```

### 🐛 Troubleshooting

#### Common Issues

1. **"No module named 'anyagent'"**
   - Solution: `pip install anyagent-ai`

2. **"Protocol message InlineButton has no 'action' field"**
   - Solution: Update to anyagent-ai>=1.0.8
   - Use `button.HasField('url')` instead of checking `action` field

3. **Connection refused on port 50051**
   - Check if agent is running: `docker ps`
   - Check logs: `docker logs <container_name>`
   - Ensure port is exposed in Dockerfile

4. **Import errors with protobuf**
   - Solution: `pip install --upgrade protobuf grpcio grpcio-tools`

#### Debug Mode

Enable detailed logging:

```python
import logging
logging.getLogger('anyagent').setLevel(logging.DEBUG)
```

### 📚 Examples

Check out the [echo_agent](./echo_agent) directory for a complete example that demonstrates:
- All message types (text, image, video, audio, document, location)
- Interactive keyboards and button handling
- Payment system integration
- Context and memory management
- Streaming responses
- Error handling

### 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit changes: `git commit -am 'Add feature'`
4. Push to branch: `git push origin feature-name`
5. Submit a pull request

### 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

### 🔗 Links

- [PyPI Package](https://pypi.org/project/anyagent-ai/)
- [GitHub Repository](https://github.com/astex-said/anyagent-framework)
- [Live Demo Bot](https://t.me/AnyAgentDemoBot)
- [AnyAgent Platform](https://anyagent.app)

### 💬 Support

- Telegram: [@saidaziz](https://t.me/saidaziz)
- Email: astexlab@gmail.com
- Issues: [GitHub Issues](https://github.com/astex-said/anyagent-framework/issues)

---

Built with ❤️ by the AnyAgent Team