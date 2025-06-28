"""
Echo Agent - A minimal demonstration of AnyAgent data types and payment requests.

This agent showcases all supported Telegram message types and demonstrates
payment requests for different types of content processing.
"""

import os
import logging
import hashlib
from typing import AsyncGenerator, Optional, Dict, Any

from anyagent import (
    BaseAgent, AgentRequest, AgentResponse, 
    TelegramMessage, TextContent, ImageContent, VideoContent, 
    AudioContent, DocumentContent, LocationContent,
    TelegramAction, UsagePaymentRequest,
    InlineKeyboard, InlineButton, InlineButtonRow, CallbackQuery
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("echo_agent")

# Payment keys with default quantities - pricing is configured in web console
PRICING = {
    "text": 1,           # 1 text processing operation
    "image": 1,          # 1 image analysis operation  
    "video": 1,          # 1 video processing operation
    "audio": 1,          # 1 audio transcription operation
    "document": 1,       # 1 document analysis operation
    "location": 1,       # 1 location processing operation
}


class EchoAgent(BaseAgent):
    """
    Minimal Echo Agent demonstrating all AnyAgent features.
    
    Features:
    - Handles all supported message types (text, image, video, audio, document, location)
    - Demonstrates payment requests for different content types
    - Shows streaming responses
    - Interactive keyboards
    - Minimal, focused implementation for learning
    """
    
    def __init__(self):
        super().__init__(logger=logger)
    
    def _initialize(self):
        """Initialize the echo agent."""
        self.logger.info("🔊 Echo Agent initialized - ready to demonstrate all data types!")
    
    def get_content_hash(self, data: bytes) -> str:
        """Generate a hash for content data."""
        return hashlib.md5(data).hexdigest()[:8]

    async def execute(self, request: AgentRequest) -> AsyncGenerator[AgentResponse, None]:
        """
        Main execution logic that handles all message types and demonstrates payments.
        
        Note: Payment requests are made for each message type using their respective
        pricing keys. Payment is handled externally via request.paid.
        """
        user_id = str(request.user_id)
        
        # Handle callback queries (button presses)
        if request.callback_query:
            async for response in self._handle_callback(request.callback_query, request.paid):
                yield response
            return
        
        message = request.telegram_message
        
        if not message:
            yield AgentResponse(
                telegram_message=TelegramMessage(
                    text=TextContent(text="❌ No message received. Send me any type of content to see the echo!"),
                    action=TelegramAction.TYPING
                )
            )
            return
        
        # Handle different message types
        if message.text:
            async for response in self._handle_text(message.text, request.paid):
                yield response
                
        elif message.image:
            async for response in self._handle_image(message.image, request.paid):
                yield response
                
        elif message.video:
            async for response in self._handle_video(message.video, request.paid):
                yield response
                
        elif message.audio:
            async for response in self._handle_audio(message.audio, request.paid):
                yield response
                
        elif message.document:
            async for response in self._handle_document(message.document, request.paid):
                yield response
                
        elif message.location:
            async for response in self._handle_location(message.location, request.paid):
                yield response
                
        else:
            yield AgentResponse(
                telegram_message=TelegramMessage(
                    text=TextContent(text="🤔 Unknown message type. Send me text, image, video, audio, document, or location!"),
                    action=TelegramAction.TYPING
                )
            )
    
    async def _handle_text(self, text_content: TextContent, paid: bool) -> AsyncGenerator[AgentResponse, None]:
        """Handle text messages with payment demo."""
        text = text_content.text
        
        # Text processing requires payment - but don't return, let flow continue
        if not paid:
            yield AgentResponse(
                payment_request=UsagePaymentRequest(
                    key="text",
                    quantity=PRICING["text"]
                )
            )
        
        # Process the text
        word_count = len(text.split())
        
        echo_response = f"""
🔊 <b>Text Echo</b>

📥 <b>Received:</b> {text}

📊 <b>Analysis:</b>
• Length: {len(text)} characters
• Words: {word_count}
• Type: Text message

🔄 <b>Echo:</b> {text}
        """.strip()
        
        yield AgentResponse(
            telegram_message=TelegramMessage(
                text=TextContent(text=echo_response),
                action=TelegramAction.TYPING,
                inline_keyboard=InlineKeyboard(rows=[
                    InlineButtonRow(buttons=[
                        InlineButton.callback_button("🔁 Echo Again", f"echo_text:{text[:20]}"),
                        InlineButton.callback_button("📊 Stats", "stats")
                    ]),
                    InlineButtonRow(buttons=[
                        InlineButton.url_button("📖 GitHub", "https://github.com/astex-said/anyagent"),
                        InlineButton.url_button("🌐 Website", "https://anyagent.app")
                    ])
                ])
            )
        )
    
    async def _handle_image(self, image_content: ImageContent, paid: bool) -> AsyncGenerator[AgentResponse, None]:
        """Handle image messages with payment demo."""
        if not paid:
            yield AgentResponse(
                payment_request=UsagePaymentRequest(
                    key="image",
                    quantity=PRICING["image"]
                )
            )
        
        # Simulate image processing
        yield AgentResponse(
            telegram_message=TelegramMessage(
                text=TextContent(text="🔍 Analyzing image..."),
                action=TelegramAction.TYPING
            )
        )
        
        image_hash = self.get_content_hash(image_content.image_data)
        data_size = len(image_content.image_data)
        
        analysis = f"""
🖼️ <b>Image Echo &amp; Analysis</b>

📥 <b>Original Caption:</b> {image_content.caption or "No caption"}
📁 <b>Filename:</b> {image_content.filename or "Unknown"}
📊 <b>Data Size:</b> {data_size:,} bytes
🔍 <b>Content Hash:</b> {image_hash}
🎭 <b>Simulated Analysis:</b> Beautiful image detected!

✅ <b>Processing Complete</b>
        """.strip()
        
        # Echo the image back with analysis
        yield AgentResponse(
            telegram_message=TelegramMessage(
                image=ImageContent(
                    image_data=image_content.image_data,
                    caption=f"🔊 ECHOED IMAGE\n\n{analysis}",
                    filename=f"echo_{image_content.filename or 'image.jpg'}"
                ),
                action=TelegramAction.TYPING
            )
        )
    
    async def _handle_video(self, video_content: VideoContent, paid: bool) -> AsyncGenerator[AgentResponse, None]:
        """Handle video messages with payment demo."""
        if not paid:
            yield AgentResponse(
                payment_request=UsagePaymentRequest(
                    key="video",
                    quantity=PRICING["video"]
                )
            )
        
        # Simulate video processing
        yield AgentResponse(
            telegram_message=TelegramMessage(
                text=TextContent(text="🎬 Processing video... This may take a moment."),
                action=TelegramAction.TYPING
            )
        )
        
        video_hash = self.get_content_hash(video_content.video_data)
        data_size = len(video_content.video_data)
        
        analysis = f"""
🎥 <b>Video Echo &amp; Analysis</b>

📥 <b>Original Caption:</b> {video_content.caption or "No caption"}
📁 <b>Filename:</b> {video_content.filename or "Unknown"}
📊 <b>Data Size:</b> {data_size:,} bytes
🔍 <b>Content Hash:</b> {video_hash}
🎭 <b>Simulated Analysis:</b>
• Estimated duration: ~{data_size // 100000}s
• Quality: HD detected
• Format: Video/MP4 (simulated)
• Frames analyzed: {data_size // 50000}

✅ <b>Premium Processing Complete</b>
        """.strip()
        
        # Echo the video back
        yield AgentResponse(
            telegram_message=TelegramMessage(
                video=VideoContent(
                    video_data=video_content.video_data,
                    caption=f"🔊 ECHOED VIDEO\n\n{analysis}",
                    filename=f"echo_{video_content.filename or 'video.mp4'}"
                ),
                action=TelegramAction.TYPING
            )
        )
    
    async def _handle_audio(self, audio_content: AudioContent, paid: bool) -> AsyncGenerator[AgentResponse, None]:
        """Handle audio messages with payment demo."""
        if not paid:
            yield AgentResponse(
                payment_request=UsagePaymentRequest(
                    key="audio",
                    quantity=PRICING["audio"]
                )
            )
        
        # Simulate audio processing
        yield AgentResponse(
            telegram_message=TelegramMessage(
                text=TextContent(text="🎧 Transcribing audio..."),
                action=TelegramAction.TYPING
            )
        )
        
        audio_hash = self.get_content_hash(audio_content.audio_data)
        data_size = len(audio_content.audio_data)
        
        analysis = f"""
🎵 <b>Audio Echo &amp; Analysis</b>

📁 <b>Filename:</b> {audio_content.filename or "Unknown"}
📊 <b>Data Size:</b> {data_size:,} bytes
🔍 <b>Content Hash:</b> {audio_hash}
🎭 <b>Simulated Transcription:</b> "Hello, this is a simulated transcription of your audio message."
⏱️ <b>Estimated Duration:</b> ~{data_size // 8000}s
🎼 <b>Format Analysis:</b> Audio/WAV detected
🎚️ <b>Quality:</b> Good quality audio

✅ <b>Audio Processing Complete</b>
        """.strip()
        
        # Echo the audio back
        yield AgentResponse(
            telegram_message=TelegramMessage(
                audio=AudioContent(
                    audio_data=audio_content.audio_data,
                    filename=f"echo_{audio_content.filename or 'audio.wav'}"
                ),
                text=TextContent(text=analysis),
                action=TelegramAction.TYPING
            )
        )
    
    async def _handle_document(self, document_content: DocumentContent, paid: bool) -> AsyncGenerator[AgentResponse, None]:
        """Handle document messages with payment demo."""
        if not paid:
            yield AgentResponse(
                payment_request=UsagePaymentRequest(
                    key="document",
                    quantity=PRICING["document"]
                )
            )
        
        # Simulate document processing
        yield AgentResponse(
            telegram_message=TelegramMessage(
                text=TextContent(text="📋 Analyzing document..."),
                action=TelegramAction.TYPING
            )
        )
        
        doc_hash = self.get_content_hash(document_content.file_data)
        data_size = len(document_content.file_data)
        file_ext = document_content.filename.split('.')[-1] if document_content.filename and '.' in document_content.filename else "unknown"
        
        analysis = f"""
📄 <b>Document Echo &amp; Analysis</b>

📁 <b>Filename:</b> {document_content.filename or "Unknown"}
📊 <b>File Size:</b> {data_size:,} bytes
🔍 <b>Content Hash:</b> {doc_hash}
📝 <b>File Extension:</b> .{file_ext}
🛡️ <b>Security Scan:</b> ✅ Safe (simulated)
📋 <b>Content Analysis:</b>
• File type: {file_ext.upper()} document
• Estimated pages: {max(1, data_size // 2000)}
• Processing status: Complete

✅ <b>Document Analysis Complete</b>
        """.strip()
        
        # Echo the document back
        yield AgentResponse(
            telegram_message=TelegramMessage(
                document=DocumentContent(
                    file_data=document_content.file_data,
                    filename=f"echo_{document_content.filename or 'document.txt'}"
                ),
                text=TextContent(text=analysis),
                action=TelegramAction.TYPING
            )
        )
    
    async def _handle_location(self, location_content: LocationContent, paid: bool) -> AsyncGenerator[AgentResponse, None]:
        """Handle location messages with payment demo."""
        if not paid:
            yield AgentResponse(
                payment_request=UsagePaymentRequest(
                    key="location",
                    quantity=PRICING["location"]
                )
            )
        
        # Simulate location processing
        yield AgentResponse(
            telegram_message=TelegramMessage(
                text=TextContent(text="🗺️ Analyzing location..."),
                action=TelegramAction.TYPING
            )
        )
        
        lat, lon = location_content.latitude, location_content.longitude
        
        # Simulate reverse geocoding
        city = "Unknown City"
        if abs(lat - 40.7128) < 1 and abs(lon - (-74.0060)) < 1:
            city = "New York"
        elif abs(lat - 51.5074) < 1 and abs(lon - (-0.1278)) < 1:
            city = "London"
        elif abs(lat - 35.6762) < 1 and abs(lon - 139.6503) < 1:
            city = "Tokyo"
        
        analysis = f"""
📍 <b>Location Echo &amp; Analysis</b>

📍 <b>Coordinates:</b>
• Latitude: {lat:.6f}°
• Longitude: {lon:.6f}°

🌍 <b>Geocoding (Simulated):</b>
• City: {city}
• Country: Detected region
• Timezone: UTC offset calculated

📊 <b>Analysis:</b>
• Coordinate precision: 6 decimal places
• Location type: GPS coordinates
• Distance from equator: {abs(lat):.1f}°

🌤️ <b>Weather (Simulated):</b> Partly cloudy, 22°C

✅ <b>Location Analysis Complete</b>
        """.strip()
        
        # Echo the location back
        yield AgentResponse(
            telegram_message=TelegramMessage(
                location=LocationContent(
                    latitude=lat,
                    longitude=lon
                ),
                text=TextContent(text=analysis),
                action=TelegramAction.TYPING,
                inline_keyboard=InlineKeyboard(rows=[
                    InlineButtonRow(buttons=[
                        InlineButton.callback_button("🗺️ Map View", f"map:{lat},{lon}"),
                        InlineButton.callback_button("🌍 Geocode", f"geocode:{lat},{lon}"),
                        InlineButton.url_button("🌐 Open Street Map", f"https://www.openstreetmap.org/?mlat={lat}&mlon={lon}")
                    ])
                ])
            )
        )

    async def _handle_callback(self, callback_query, paid: bool) -> AsyncGenerator[AgentResponse, None]:
        """
        Handle callback queries from inline keyboard button presses.
        """
        callback_data = callback_query.callback_data
        
        # Parse different callback commands
        if callback_data == "stats":
            # Show general stats
            stats_text = f"""
📊 <b>Echo Agent Statistics</b>

🔧 <b>Framework Info:</b>
• Version: 1.0.0
• Supported Types: 6 (text, image, video, audio, document, location)
• Payment System: Usage-based

💰 <b>Pricing:</b>
• Text: {PRICING['text']} credits
• Image: {PRICING['image']} credits  
• Video: {PRICING['video']} credits
• Audio: {PRICING['audio']} credits
• Document: {PRICING['document']} credits
• Location: {PRICING['location']} credits

🎯 <b>Features:</b>
• Real-time streaming responses
• Interactive keyboards
• Content analysis and metadata
• Bidirectional payment flow

✨ <b>Perfect for learning AnyAgent framework!</b>
            """.strip()
            
            yield AgentResponse(
                telegram_message=TelegramMessage(
                    text=TextContent(text=stats_text),
                    action=TelegramAction.TYPING,
                    inline_keyboard=InlineKeyboard(rows=[
                        InlineButtonRow(buttons=[
                            InlineButton.callback_button("🔄 Back to Demo", "back_demo"),
                            InlineButton.callback_button("❓ Help", "help")
                        ]),
                        InlineButtonRow(buttons=[
                            InlineButton.url_button("📖 GitHub", "https://github.com/astex-said/anyagent"),
                            InlineButton.url_button("🌐 Website", "https://anyagent.app")
                        ])
                    ])
                )
            )
            
        elif callback_data.startswith("echo_text:"):
            # Echo the text again
            text_to_echo = callback_data[10:]  # Remove "echo_text:" prefix
            
            # Text processing requires payment
            if not paid:
                yield AgentResponse(
                    payment_request=UsagePaymentRequest(
                        key="text",
                        quantity=PRICING["text"]
                    )
                )
            
            # Process the text again
            word_count = len(text_to_echo.split())
            
            echo_response = f"""
🔁 <b>Text Re-Echo</b>

📥 <b>Text:</b> {text_to_echo}

📊 <b>Quick Analysis:</b>
• Length: {len(text_to_echo)} characters
• Words: {word_count}
• Re-echoed: ✅

🔄 <b>Echo:</b> {text_to_echo}
            """.strip()
            
            yield AgentResponse(
                telegram_message=TelegramMessage(
                    text=TextContent(text=echo_response),
                    action=TelegramAction.TYPING,
                    inline_keyboard=InlineKeyboard(rows=[
                        InlineButtonRow(buttons=[
                            InlineButton.callback_button("🔁 Echo Again", f"echo_text:{text_to_echo[:20]}"),
                            InlineButton.callback_button("📊 Stats", "stats")
                        ])
                    ])
                )
            )
            
        elif callback_data.startswith("map:"):
            # Show map view for location
            coords = callback_data[4:]  # Remove "map:" prefix
            lat, lon = coords.split(",")
            
            map_response = f"""
🗺️ <b>Map View</b>

📍 <b>Coordinates:</b> {lat}, {lon}
🌍 <b>Map Services:</b>
• Google Maps: https://maps.google.com/?q={lat},{lon}
• OpenStreetMap: https://www.openstreetmap.org/?mlat={lat}&mlon={lon}
• Apple Maps: https://maps.apple.com/?q={lat},{lon}

💡 <b>Tip:</b> Click any link to view location on external map service!
            """.strip()
            
            yield AgentResponse(
                telegram_message=TelegramMessage(
                    text=TextContent(text=map_response),
                    action=TelegramAction.TYPING,
                    inline_keyboard=InlineKeyboard(rows=[
                        InlineButtonRow(buttons=[
                            InlineButton.callback_button("🌍 Geocode", f"geocode:{coords}"),
                            InlineButton.callback_button("🔙 Back", "back_demo"),
                            InlineButton.url_button("🗺️ Google Maps", f"https://maps.google.com/?q={coords}")
                        ])
                    ])
                )
            )
            
        elif callback_data.startswith("geocode:"):
            # Show geocoding info for location
            coords = callback_data[8:]  # Remove "geocode:" prefix
            lat, lon = map(float, coords.split(","))
            
            # Simulate reverse geocoding (same logic as in location handler)
            city = "Unknown City"
            country = "Unknown Country"
            if abs(lat - 40.7128) < 1 and abs(lon - (-74.0060)) < 1:
                city = "New York"
                country = "United States"
            elif abs(lat - 51.5074) < 1 and abs(lon - (-0.1278)) < 1:
                city = "London"
                country = "United Kingdom"
            elif abs(lat - 35.6762) < 1 and abs(lon - 139.6503) < 1:
                city = "Tokyo"
                country = "Japan"
            
            geocode_response = f"""
🌍 <b>Geocoding Results</b>

📍 <b>Coordinates:</b> {lat:.6f}°, {lon:.6f}°

🏙️ <b>Location Details:</b>
• City: {city}
• Country: {country}
• Timezone: UTC offset calculated
• Coordinate precision: 6 decimal places

📐 <b>Geographic Info:</b>
• Distance from equator: {abs(lat):.1f}°
• Hemisphere: {'Northern' if lat >= 0 else 'Southern'}
• Prime meridian: {'East' if lon >= 0 else 'West'}
            """.strip()
            
            yield AgentResponse(
                telegram_message=TelegramMessage(
                    text=TextContent(text=geocode_response),
                    action=TelegramAction.TYPING,
                    inline_keyboard=InlineKeyboard(rows=[
                        InlineButtonRow(buttons=[
                            InlineButton.callback_button("🗺️ Map View", f"map:{coords}"),
                            InlineButton.callback_button("🔙 Back", "back_demo"),
                            InlineButton.url_button("🌍 Apple Maps", f"https://maps.apple.com/?q={coords}")
                        ])
                    ])
                )
            )
            
        elif callback_data == "help":
            # Show help via callback
            async for response in self.help(AgentRequest(user_id=0, paid=paid)):
                yield response
                
        elif callback_data == "back_demo":
            # Back to main demo
            yield AgentResponse(
                telegram_message=TelegramMessage(
                    text=TextContent(text="🔊 <b>Echo Agent Ready!</b>\n\nSend me any content type to see it echoed back with analysis!\n\n💡 Try: text, images, videos, audio, documents, or locations.\n\n📝 Send text, 🖼️ images, 🎵 audio, 📄 documents, 📍 locations, or type ❓ for help."),
                    action=TelegramAction.TYPING
                )
            )
            
        else:
            # Unknown callback
            yield AgentResponse(
                telegram_message=TelegramMessage(
                    text=TextContent(text=f"🤔 Unknown button command: `{callback_data}`\n\nSend me any content type to continue!"),
                    action=TelegramAction.TYPING
                )
            )

    async def help(self, request: AgentRequest) -> AsyncGenerator[AgentResponse, None]:
        """
        Help explaining all features and data types.
        """
        help_text = f"""
🔊 <b>Echo Agent - Minimal Demo</b>

I demonstrate all AnyAgent data types and payment features!

📱 <b>Supported Content Types:</b>

<b>📝 Text</b> - {PRICING['text']} credits
<b>🖼️ Images</b> - {PRICING['image']} credits
<b>🎥 Videos</b> - {PRICING['video']} credits
<b>🎵 Audio</b> - {PRICING['audio']} credits
<b>📄 Documents</b> - {PRICING['document']} credits
<b>📍 Locations</b> - {PRICING['location']} credits

💡 <b>How to Test:</b>
1. Send different content types
2. Experience payment requests
3. See content echoed back with analysis

🎯 <b>Perfect for learning AnyAgent framework!</b>

Send me any content type to get started! 🚀

────────────────────────
💻 <a href="https://github.com/astex-said/anyagent/tree/main/echo_agent">My source code</a> or how to write agents?
        """.strip()
        
        yield AgentResponse(
            telegram_message=TelegramMessage(
                text=TextContent(text=help_text + "\n\n📝 Send text, 🖼️ images, 🎵 audio, 📄 documents, 📍 locations, or type ❓ for help."),
                action=TelegramAction.TYPING
            )
        )


# Create agent instance
agent = EchoAgent()

# For legacy compatibility
execute_func = agent.execute
help_func = agent.help