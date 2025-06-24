# Echo Agent Tutorial - Build Your First AnyAgent

**Learn to build AI agents with the AnyAgent framework through a complete echo bot example.**

## 🎯 What You'll Learn

This tutorial teaches you to build production-ready Telegram agents by creating an echo bot that demonstrates:

- **All message types** - text, images, videos, audio, documents, locations
- **Payment system** - pay-per-use with quantity-based billing
- **Interactive UI** - buttons, callbacks, keyboards
- **Streaming responses** - real-time bidirectional communication
- **Zero-config setup** - minimal code, maximum functionality

## 📋 Prerequisites

- Python 3.8+
- Basic async/await knowledge
- Understanding of Telegram bots (helpful but not required)

## 🚀 Quick Start

### 1. Install AnyAgent

```bash
pip install anyagent-ai
```

### 2. Create Your Agent

```python
# agent.py
from anyagent import BaseAgent, AgentRequest, AgentResponse, TelegramMessage, TextContent

class EchoAgent(BaseAgent):
    def __init__(self):
        super().__init__()  # Zero config!
    
    async def execute(self, request):
        """Main agent logic - handle incoming messages"""
        message = request.telegram_message
        
        if message and message.text:
            yield AgentResponse(
                telegram_message=TelegramMessage(
                    text=TextContent(text=f"Echo: {message.text.text}")
                )
            )
    
    async def help(self, request):
        """Help command response"""
        yield AgentResponse(
            telegram_message=TelegramMessage(
                text=TextContent(text="I'm an echo bot! Send me any message and I'll echo it back.")
            )
        )
```

### 3. Run Your Agent

```python
# main.py
from anyagent import AgentServer
from agent import EchoAgent

agent = EchoAgent()
server = AgentServer(agent, port=50051)
server.run()
```

### 4. Test It

```bash
python main.py
# Your agent is now running on port 50051!
```

## 📚 Core Concepts

### BaseAgent Class

Every agent inherits from `BaseAgent` and implements two methods:

```python
class MyAgent(BaseAgent):
    def __init__(self):
        super().__init__()  # Uses self.__class__.__name__ automatically
    
    async def execute(self, request: AgentRequest) -> AsyncGenerator[AgentResponse, None]:
        # Handle user messages
        pass
    
    async def help(self, request: AgentRequest) -> AsyncGenerator[AgentResponse, None]:
        # Provide help information
        pass
```

### AgentRequest Structure

```python
class AgentRequest:
    telegram_message: Optional[TelegramMessage]  # User's message
    callback_query: Optional[CallbackQuery]      # Button clicks
    user_id: int                                 # User identifier
    paid: bool                                   # Payment status
    language_code: Optional[str]                 # User's language
    context: Optional[Context]                   # Conversation history
```

### AgentResponse Structure

```python
class AgentResponse:
    telegram_message: Optional[TelegramMessage]     # Message to send
    payment_request: Optional[UsagePaymentRequest]  # Request payment
    memory: Optional[ContextMessage]                # Store meaningful messages in conversation memory
```

### Memory System

The `memory` field is used to store **meaningful conversational messages** in the platform's memory system. 

**❌ Don't store in memory:**
- Progress bars: "Processing... 50%"
- Status updates: "Downloading..."
- Temporary UI messages: "Please wait..."
- System notifications

**✅ Store in memory:**
- User questions and agent answers
- Important decisions made
- Analysis results
- Final outputs

```python
async def execute(self, request):
    # Progress message - DON'T store in memory
    yield AgentResponse(
        telegram_message=TelegramMessage(
            text=TextContent(text="🔄 Analyzing your image...")
        )
        # No memory field - this is just a progress update
    )
    
    # Final result - STORE in memory
    analysis_result = "The image shows a cat sitting on a windowsill"
    yield AgentResponse(
        telegram_message=TelegramMessage(
            text=TextContent(text=f"🖼️ Analysis: {analysis_result}")
        ),
        memory=ContextMessage(
            role="assistant", 
            content=f"Image analysis result: {analysis_result}"
        )
    )
```

### Database Management

**Important:** The framework no longer includes built-in user data storage. You have the `user_id` field to identify users and should implement your own database:

```python
import sqlite3

class UserDatabase:
    def __init__(self):
        self.conn = sqlite3.connect('users.db')
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS user_data (
                user_id INTEGER PRIMARY KEY,
                data TEXT
            )
        ''')
    
    def get_user_data(self, user_id: int) -> dict:
        cursor = self.conn.execute('SELECT data FROM user_data WHERE user_id = ?', (user_id,))
        row = cursor.fetchone()
        return json.loads(row[0]) if row else {}
    
    def save_user_data(self, user_id: int, data: dict):
        self.conn.execute(
            'INSERT OR REPLACE INTO user_data (user_id, data) VALUES (?, ?)',
            (user_id, json.dumps(data))
        )
        self.conn.commit()

# Usage in your agent
db = UserDatabase()

async def execute(self, request):
    user_data = db.get_user_data(request.user_id)
    
    # Your logic here
    user_data['last_message'] = request.telegram_message.text.text
    
    db.save_user_data(request.user_id, user_data)
```

## 📱 Message Types Tutorial

### 1. Text Messages

```python
async def execute(self, request):
    message = request.telegram_message
    
    if message and message.text:
        text = message.text.text
        word_count = len(text.split())
        
        yield AgentResponse(
            telegram_message=TelegramMessage(
                text=TextContent(
                    text=f"📝 You sent: {text}\\n📊 Words: {word_count}"
                )
            )
        )
```

### 2. Image Messages

```python
async def execute(self, request):
    message = request.telegram_message
    
    if message and message.image:
        image_data = message.image.image_data
        filename = message.image.filename or "image.jpg"
        caption = message.image.caption or "No caption"
        
        # Analyze image
        size_kb = len(image_data) // 1024
        
        yield AgentResponse(
            telegram_message=TelegramMessage(
                text=TextContent(
                    text=f"🖼️ Image received!\\n"
                         f"📁 Name: {filename}\\n"
                         f"📏 Size: {size_kb} KB\\n"
                         f"📝 Caption: {caption}"
                )
            )
        )
```

### 3. Video Messages

```python
async def execute(self, request):
    message = request.telegram_message
    
    if message and message.video:
        video_data = message.video.video_data
        filename = message.video.filename or "video.mp4"
        
        # Echo the video back with analysis
        yield AgentResponse(
            telegram_message=TelegramMessage(
                video=VideoContent(
                    video_data=video_data,
                    filename=f"echo_{filename}",
                    caption=f"🎥 Video echoed back! Size: {len(video_data)} bytes"
                )
            )
        )
```

### 4. Audio Messages

```python
async def execute(self, request):
    message = request.telegram_message
    
    if message and message.audio:
        audio_data = message.audio.audio_data
        filename = message.audio.filename or "audio.mp3"
        
        yield AgentResponse(
            telegram_message=TelegramMessage(
                text=TextContent(
                    text=f"🎵 Audio received: {filename}\\n"
                         f"📏 Size: {len(audio_data)} bytes\\n"
                         f"🎯 Ready for processing!"
                )
            )
        )
```

### 5. Document Messages

```python
async def execute(self, request):
    message = request.telegram_message
    
    if message and message.document:
        file_data = message.document.file_data
        filename = message.document.filename or "document"
        
        # Simple file type detection
        file_type = "Unknown"
        if filename.endswith('.pdf'):
            file_type = "PDF Document"
        elif filename.endswith('.txt'):
            file_type = "Text File"
        elif filename.endswith('.docx'):
            file_type = "Word Document"
        
        yield AgentResponse(
            telegram_message=TelegramMessage(
                text=TextContent(
                    text=f"📄 Document: {filename}\\n"
                         f"📋 Type: {file_type}\\n"
                         f"📏 Size: {len(file_data)} bytes"
                )
            )
        )
```

### 6. Location Messages

```python
async def execute(self, request):
    message = request.telegram_message
    
    if message and message.location:
        lat = message.location.latitude
        lon = message.location.longitude
        
        # Simple city detection
        city = "Unknown location"
        if abs(lat - 40.7128) < 1 and abs(lon + 74.0060) < 1:
            city = "New York, USA"
        elif abs(lat - 51.5074) < 1 and abs(lon + 0.1278) < 1:
            city = "London, UK"
        
        yield AgentResponse(
            telegram_message=TelegramMessage(
                text=TextContent(
                    text=f"📍 Location: {lat:.4f}, {lon:.4f}\\n"
                         f"🏙️ Near: {city}\\n"
                         f"🗺️ Coordinates received!"
                )
            )
        )
```

## 💰 Payment System

### Basic Payment Request

```python
from anyagent import UsagePaymentRequest

async def execute(self, request):
    message = request.telegram_message
    
    if message and message.text:
        # Request payment for text processing
        if not request.paid:
            yield AgentResponse(
                payment_request=UsagePaymentRequest(
                    key="text_analysis",  # Payment key (configured in web console)
                    quantity=1            # Number of operations
                )
            )
        
        # Process regardless (bidirectional streaming)
        result = analyze_text(message.text.text)
        yield AgentResponse(
            telegram_message=TelegramMessage(
                text=TextContent(text=result)
            )
        )
```

### Variable Quantity Example

```python
async def execute(self, request):
    message = request.telegram_message
    
    if message and message.audio:
        # Estimate audio duration in minutes
        audio_duration_minutes = estimate_duration(message.audio.audio_data)
        
        # Charge per minute of audio
        if not request.paid:
            yield AgentResponse(
                payment_request=UsagePaymentRequest(
                    key="audio_transcription",
                    quantity=audio_duration_minutes  # e.g., 5 for 5 minutes
                )
            )
        
        # Process audio
        transcription = transcribe_audio(message.audio.audio_data)
        yield AgentResponse(
            telegram_message=TelegramMessage(
                text=TextContent(text=f"Transcription: {transcription}")
            )
        )

def estimate_duration(audio_data: bytes) -> int:
    # Simplified: assume 1 minute per 100KB (adjust for your needs)
    estimated_minutes = max(1, len(audio_data) // (100 * 1024))
    return estimated_minutes
```

### Payment Configuration

In your web console, configure pricing:

```sql
-- Audio transcription: 2 credits per minute
INSERT INTO agent_pricing (agent_name, key, credits_per_unit, description) 
VALUES ('EchoAgent', 'audio_transcription', 2, 'Audio transcription per minute');

-- Text analysis: 5 credits per analysis
INSERT INTO agent_pricing (agent_name, key, credits_per_unit, description) 
VALUES ('EchoAgent', 'text_analysis', 5, 'Text analysis per operation');
```

## 🎛️ Interactive UI Components

### Inline Keyboards

```python
from anyagent import InlineKeyboard

async def execute(self, request):
    message = request.telegram_message
    
    if message and message.text:
        yield AgentResponse(
            telegram_message=TelegramMessage(
                text=TextContent(text="Choose an action:"),
                inline_keyboard=InlineKeyboard(rows=[
                    {"buttons": [
                        {"text": "🔁 Echo Again", "callback_data": f"echo:{message.text.text}"},
                        {"text": "📊 Analyze", "callback_data": f"analyze:{message.text.text}"}
                    ]},
                    {"buttons": [
                        {"text": "❓ Help", "callback_data": "help"},
                        {"text": "📈 Stats", "callback_data": "stats"}
                    ]}
                ])
            )
        )
```

### Handling Button Clicks

```python
async def execute(self, request):
    # Handle button callbacks
    if request.callback_query:
        callback_data = request.callback_query.callback_data
        
        if callback_data.startswith("echo:"):
            text = callback_data[5:]  # Remove "echo:" prefix
            yield AgentResponse(
                telegram_message=TelegramMessage(
                    text=TextContent(text=f"🔁 Echoed: {text}")
                )
            )
            
        elif callback_data.startswith("analyze:"):
            text = callback_data[8:]  # Remove "analyze:" prefix
            analysis = f"📊 Analysis: {len(text)} chars, {len(text.split())} words"
            yield AgentResponse(
                telegram_message=TelegramMessage(
                    text=TextContent(text=analysis)
                )
            )
            
        elif callback_data == "help":
            yield AgentResponse(
                telegram_message=TelegramMessage(
                    text=TextContent(text="❓ I can echo and analyze your messages!")
                )
            )
            
        elif callback_data == "stats":
            yield AgentResponse(
                telegram_message=TelegramMessage(
                    text=TextContent(text="📈 Stats: Echo Agent v1.0 - Ready to serve!")
                )
            )
        return
    
    # Handle regular messages...
```

## 🔄 Streaming Responses

### Multiple Messages

```python
async def execute(self, request):
    message = request.telegram_message
    
    if message and message.text:
        # First response - processing (no memory)
        yield AgentResponse(
            telegram_message=TelegramMessage(
                text=TextContent(text="🔄 Processing your message..."),
                action=TelegramAction.TYPING
            )
            # No memory - this is just a progress update
        )
        
        # Simulate processing delay
        await asyncio.sleep(1)
        
        # Second response - result (store in memory)
        result = f"✅ Done! Your message: {message.text.text}"
        yield AgentResponse(
            telegram_message=TelegramMessage(
                text=TextContent(text=result)
            ),
            memory=ContextMessage(
                role="assistant",
                content=f"Processed user message: {message.text.text}"
            )
        )
```

### Progress Updates

```python
async def execute(self, request):
    message = request.telegram_message
    
    if message and message.video:
        # Progress updates - DON'T store in memory
        steps = ["📥 Downloading", "🎬 Analyzing", "📊 Processing"]
        
        for i, step in enumerate(steps):
            yield AgentResponse(
                telegram_message=TelegramMessage(
                    text=TextContent(text=f"{step} ({i+1}/{len(steps)})"),
                    action=TelegramAction.UPLOADING_VIDEO
                )
                # No memory field - these are just progress updates
            )
            await asyncio.sleep(0.5)
        
        # Final result - STORE in memory
        video_analysis = "Video contains 3 scenes: intro, main content, outro"
        yield AgentResponse(
            telegram_message=TelegramMessage(
                text=TextContent(text=f"🎥 Analysis: {video_analysis}")
            ),
            memory=ContextMessage(
                role="assistant",
                content=f"Video analysis: {video_analysis}"
            )
        )
```

## 🐳 Docker Deployment

### Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 50051

CMD ["python", "main.py"]
```

### docker-compose.yml
```yaml
version: '3.8'
services:
  echo-agent:
    build: .
    ports:
      - "50051:50051"
    restart: unless-stopped
    environment:
      - GRPC_PORT=50051
```

### Run with Docker
```bash
docker-compose up -d
```

## 🧪 Testing Your Agent

### Manual Testing
```python
# test_client.py
import asyncio
import grpc
from anyagent.proto import agent_pb2, agent_pb2_grpc

async def test_agent():
    channel = grpc.aio.insecure_channel("localhost:50051")
    stub = agent_pb2_grpc.AgentServiceStub(channel)
    
    # Test text message
    request = agent_pb2.AgentRequest(
        user_id=12345,
        paid=False,
        telegram_message=agent_pb2.TelegramMessage(
            text=agent_pb2.TextContent(text="Hello, Echo Agent!")
        )
    )
    
    async for response in stub.ExecuteStream(iter([request])):
        if response.telegram_message and response.telegram_message.text:
            print(f"Response: {response.telegram_message.text.text}")
        if response.payment_request:
            print(f"Payment requested: {response.payment_request.key} x{response.payment_request.quantity}")

if __name__ == "__main__":
    asyncio.run(test_agent())
```

## 🚀 Next Steps

### Advanced Features

1. **Context Management** - Use `request.context` for conversation history
2. **Database Integration** - Implement your own user data storage with `request.user_id`
3. **Memory System** - Use `memory` field for meaningful content only (no progress bars!)
4. **Error Handling** - Graceful error management and recovery
5. **Rate Limiting** - Implement usage quotas and throttling

### Production Considerations

1. **Monitoring** - Add logging and metrics
2. **Scaling** - Load balancing and horizontal scaling
3. **Security** - Input validation and sanitization
4. **Performance** - Optimize for high throughput
5. **Reliability** - Error recovery and fault tolerance

## 📚 Complete Example

Check out our [full echo agent implementation](agent.py) that demonstrates all these concepts in action!

## 🤝 Need Help?

- 📖 [Framework Documentation](../README.md)
- 💰 [Payment System Guide](../PAYMENT_GUIDE.md)
- 🐛 [Report Issues](https://github.com/astex-said/anyagent/issues)

Happy coding! 🎉
