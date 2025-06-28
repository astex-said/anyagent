# Echo Agent - Complete AnyAgent Example

A comprehensive demonstration agent that showcases all features of the AnyAgent Framework. This agent echoes back all message types, demonstrates payment integration, interactive UI components, and provides a complete reference implementation.

## 🌟 Features Demonstrated

- ✅ **All Message Types**: Text, Image, Video, Audio, Document, Location
- ✅ **Interactive Keyboards**: Callback buttons and URL buttons
- ✅ **Payment System**: Credit-based usage with free limits
- ✅ **Context & Memory**: Conversation history tracking
- ✅ **Streaming Responses**: Real-time message updates
- ✅ **Bot Actions**: Typing indicators and upload statuses
- ✅ **Error Handling**: Graceful error recovery
- ✅ **Help System**: Interactive help with examples

## 🚀 Quick Start

### Using Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/astex-said/anyagent-framework.git
cd anyagent-framework/echo_agent

# Build and run with Docker Compose
docker-compose up -d

# Check logs
docker-compose logs -f
```

### Manual Installation

```bash
# Install dependencies
pip install anyagent-ai>=1.0.8

# Run the agent
python main.py
```

## 📁 Project Structure

```
echo_agent/
├── agent.py           # Main agent implementation
├── main.py           # Entry point and server setup
├── requirements.txt  # Python dependencies
├── Dockerfile       # Docker container definition
├── docker-compose.yml # Docker Compose configuration
└── README.md        # This file
```

## 💻 Code Walkthrough

### 1. Basic Agent Structure

```python
from anyagent import BaseAgent, AgentResponse, TelegramMessage, TextContent
import logging

class EchoAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.logger.info("🔊 Echo Agent initialized")
    
    async def execute(self, request):
        """Main request handler"""
        # Handle different request types
        if request.telegram_message:
            async for response in self._handle_message(request):
                yield response
```

### 2. Handling Text Messages

```python
async def _handle_text(self, text_content, paid):
    """Echo text messages with interactive keyboard"""
    text = text_content.text
    
    # Create response with analysis
    echo_response = f"""🔊 Text Echo

📥 Received: {text}

📊 Analysis:
• Length: {len(text)} characters
• Words: {len(text.split())}
• Type: Text message

🔄 Echo: {text}"""
    
    # Add interactive keyboard
    keyboard = InlineKeyboard(rows=[
        InlineButtonRow(buttons=[
            InlineButton.callback_button("🔁 Echo Again", f"echo_text:{text[:20]}"),
            InlineButton.callback_button("📊 Stats", "stats")
        ]),
        InlineButtonRow(buttons=[
            InlineButton.url_button("📖 GitHub", "https://github.com/astex-said/anyagent"),
            InlineButton.url_button("🌐 Website", "https://anyagent.app")
        ])
    ])
    
    yield AgentResponse(
        telegram_message=TelegramMessage(
            text=TextContent(text=echo_response),
            action=TelegramAction.TYPING,
            inline_keyboard=keyboard
        )
    )
```

### 3. Handling Images

```python
async def _handle_image(self, image_content, paid):
    """Process and echo images"""
    # Check payment status
    if not paid:
        yield AgentResponse(
            payment_request=UsagePaymentRequest(
                key="image_processing",
                quantity=25  # 25 credits per image
            )
        )
        return
    
    # Show upload status
    yield AgentResponse(
        telegram_message=TelegramMessage(
            text=TextContent(text="🖼️ Processing image..."),
            action=TelegramAction.UPLOADING_PHOTO
        )
    )
    
    # Echo the image back
    yield AgentResponse(
        telegram_message=TelegramMessage(
            image=ImageContent(
                image_data=image_content.image_data,
                caption=f"🔊 Image Echo\n\n"
                       f"📸 Original caption: {image_content.caption or 'No caption'}\n"
                       f"📁 Filename: {image_content.filename or 'Unknown'}\n"
                       f"📏 Size: {len(image_content.image_data)} bytes",
                filename=f"echo_{image_content.filename}" if image_content.filename else "echo_image.jpg"
            )
        )
    )
```

### 4. Handling Button Callbacks

```python
async def _handle_callback_query(self, request):
    """Handle button press events"""
    callback_data = request.callback_query.callback_data
    
    if callback_data == "stats":
        # Show agent statistics
        stats_text = """📊 Echo Agent Statistics

🤖 Agent Info:
• Version: 1.0.0
• Status: ✅ Active
• Framework: AnyAgent v1.0.8

📈 Session Stats:
• Messages processed: Dynamic
• Uptime: Dynamic
• Response time: <100ms

🎯 Capabilities:
• Text echoing ✅
• Image processing ✅
• Video handling ✅
• Audio playback ✅
• Document sharing ✅
• Location mapping ✅

💰 Credit System:
• Text: 5 credits
• Image: 25 credits
• Video: 100 credits
• Audio: 50 credits
• Document: 15 credits
• Location: 10 credits"""
        
        yield AgentResponse(
            telegram_message=TelegramMessage(
                text=TextContent(text=stats_text),
                inline_keyboard=InlineKeyboard(rows=[
                    InlineButtonRow(buttons=[
                        InlineButton.callback_button("🔄 Back to Demo", "back_demo"),
                        InlineButton.callback_button("❓ Help", "help")
                    ])
                ])
            )
        )
```

### 5. Payment Integration

```python
# Credit costs for different content types
CREDIT_COSTS = {
    "text": 5,
    "image": 25,
    "video": 100,
    "audio": 50,
    "document": 15,
    "location": 10
}

async def _check_payment(self, content_type, paid):
    """Check if user has sufficient credits"""
    if not paid:
        cost = CREDIT_COSTS.get(content_type, 10)
        yield AgentResponse(
            payment_request=UsagePaymentRequest(
                key=f"{content_type}_processing",
                quantity=cost
            )
        )
        return False
    return True
```

### 6. Help Command Handler

```python
async def help(self, request):
    """Custom help command implementation"""
    help_text = """🔊 Echo Agent - Complete Demo

This agent demonstrates all AnyAgent features:

📝 Text Messages
Send any text and I'll echo it back with analysis.

🖼️ Images (25 credits)
Send photos to see image echo with metadata.

🎥 Videos (100 credits)
Share videos for playback demonstration.

🎵 Audio (50 credits)
Send voice messages or music files.

📄 Documents (15 credits)
Share any file type for document handling.

📍 Locations (10 credits)
Send your location for map integration.

🎯 Try these features:
1️⃣ Send "Hello World" → Get text echo
2️⃣ Send a photo → See image processing
3️⃣ Press buttons → Interactive UI demo
4️⃣ Send location → Map integration

💡 Each content type has different credit costs.
Free tier includes limited usage for testing."""
    
    keyboard = InlineKeyboard(rows=[
        InlineButtonRow(buttons=[
            InlineButton.callback_button("📊 View Stats", "stats"),
            InlineButton.callback_button("🎮 Start Demo", "demo")
        ]),
        InlineButtonRow(buttons=[
            InlineButton.url_button("📖 Docs", "https://github.com/astex-said/anyagent"),
            InlineButton.url_button("🌐 Website", "https://anyagent.app")
        ])
    ])
    
    yield AgentResponse(
        telegram_message=TelegramMessage(
            text=TextContent(text=help_text),
            inline_keyboard=keyboard
        )
    )
```

## 🔧 Configuration

### Environment Variables

```bash
# gRPC server port
GRPC_PORT=50061

# Logging level
LOG_LEVEL=INFO

# Worker threads
MAX_WORKERS=10
```

### Docker Compose Configuration

```yaml
version: '3.8'

services:
  echo_agent:
    build: .
    ports:
      - "50061:50061"
    environment:
      - GRPC_PORT=50061
      - LOG_LEVEL=INFO
    volumes:
      - ./data:/app/data  # For persistent storage
    restart: unless-stopped
```

## 🧪 Testing the Agent

### 1. Test Text Echo

```python
# Send any text message
"Hello, Echo Agent!"

# Expected response:
# 🔊 Text Echo
# 📥 Received: Hello, Echo Agent!
# 📊 Analysis: Length: 18 characters...
```

### 2. Test Image Processing

```python
# Send any image
# Bot will request 25 credits if not paid
# Then echo the image with metadata
```

### 3. Test Interactive Buttons

```python
# Click "📊 Stats" button
# Shows agent statistics

# Click "🌐 Website" button
# Opens https://anyagent.app in browser
```

### 4. Test Payment Flow

```python
# Send video without payment
# Bot requests 100 credits
# After payment, video is processed
```

## 📊 Credit System Details

| Content Type | Credits | Description |
|-------------|---------|-------------|
| Text | 5 | Basic text messages |
| Image | 25 | Photo processing |
| Video | 100 | Video handling |
| Audio | 50 | Voice/audio files |
| Document | 15 | File sharing |
| Location | 10 | Map integration |

## 🚨 Error Handling

The agent handles errors gracefully:

```python
try:
    # Process request
    async for response in handler(content, request.paid):
        yield response
except Exception as e:
    self.logger.error(f"Error: {str(e)}")
    yield AgentResponse(
        telegram_message=TelegramMessage(
            text=TextContent(text=f"❌ Error: {str(e)}\n\nPlease try again.")
        )
    )
```

## 🛠️ Development Guide

### Adding New Features

1. **Create a handler method**:
```python
async def _handle_custom_feature(self, data, paid):
    # Your logic here
    yield AgentResponse(...)
```

2. **Add to execute method**:
```python
if request.custom_field:
    async for response in self._handle_custom_feature(request.custom_field, request.paid):
        yield response
```

3. **Update help text** to include the new feature

### Debugging

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

View Docker logs:
```bash
docker-compose logs -f echo_agent
```

## 📈 Performance Optimization

- Uses async/await for non-blocking operations
- Streams responses for better user experience
- Implements connection pooling for gRPC
- Minimal memory footprint

## 🔄 Deployment

### Production Deployment

1. **Update docker-compose.yml** for production:
```yaml
services:
  echo_agent:
    image: your-registry/echo-agent:latest
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
```

2. **Use environment-specific configs**:
```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

3. **Monitor health**:
```bash
curl http://localhost:50061/health
```

## 📚 Learning Resources

- [AnyAgent Documentation](https://github.com/astex-said/anyagent-framework)
- [gRPC Python Guide](https://grpc.io/docs/languages/python/)
- [Telegram Bot API](https://core.telegram.org/bots/api)
- [Protocol Buffers](https://developers.google.com/protocol-buffers)

## 🤝 Contributing

1. Study this example implementation
2. Create your own agent based on this template
3. Share your agent with the community
4. Report issues or suggest improvements

## 📄 License

MIT License - feel free to use this as a template for your own agents.

---

Built with ❤️ using AnyAgent Framework