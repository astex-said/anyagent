"""
AnyAgent Framework - Public Agent Schemas

This module contains all the public schemas that agent developers need
to build agents. Internal platform schemas have been removed.
"""

import base64
from typing import Optional, List, Literal, Union, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime, timezone
from enum import Enum
from google.protobuf.struct_pb2 import Struct


def encode_bytes(b: bytes) -> str:
    """Encode bytes to base64 string for JSON serialization."""
    return base64.b64encode(b).decode('utf-8')


def dict_to_struct(data: Dict[str, Any]) -> Struct:
    """Convert a Python dict to a Protobuf Struct."""
    struct_obj = Struct()
    for key, value in data.items():
        if isinstance(value, dict):
            struct_obj.fields[key].struct_value.CopyFrom(dict_to_struct(value))
        elif isinstance(value, list):
            struct_obj.fields[key].list_value.extend([
                dict_to_struct(item) if isinstance(item, dict) else item for item in value
            ])
        elif isinstance(value, str):
            struct_obj.fields[key].string_value = value
        elif isinstance(value, (int, float)):
            struct_obj.fields[key].number_value = value
        elif isinstance(value, bool):
            struct_obj.fields[key].bool_value = value
        elif value is None:
            struct_obj.fields[key].null_value = 0
    return struct_obj


def struct_to_dict(struct_obj: Struct) -> Dict[str, Any]:
    """Convert a Protobuf Struct to a Python dict."""
    result = {}
    for key, value in struct_obj.fields.items():
        if value.HasField('struct_value'):
            result[key] = struct_to_dict(value.struct_value)
        elif value.HasField('list_value'):
            result[key] = [
                struct_to_dict(item.struct_value) if item.HasField('struct_value') else 
                item.string_value if item.HasField('string_value') else
                item.number_value if item.HasField('number_value') else
                item.bool_value if item.HasField('bool_value') else None
                for item in value.list_value.values
            ]
        elif value.HasField('string_value'):
            result[key] = value.string_value
        elif value.HasField('number_value'):
            result[key] = value.number_value
        elif value.HasField('bool_value'):
            result[key] = value.bool_value
        elif value.HasField('null_value'):
            result[key] = None
    return result


# ===========================
# 📌 Telegram Content Types
# ===========================

class TextContent(BaseModel):
    """Text message content."""
    text: str


class ImageContent(BaseModel):
    """Image message content with optional caption and filename."""
    image_data: bytes
    caption: Optional[str] = None
    filename: Optional[str] = None


class VideoContent(BaseModel):
    """Video message content with optional caption and filename."""
    video_data: bytes
    caption: Optional[str] = None
    filename: Optional[str] = None


class AudioContent(BaseModel):
    """Audio message content with optional filename."""
    audio_data: bytes
    filename: Optional[str] = None


class DocumentContent(BaseModel):
    """Document/file message content with optional filename."""
    file_data: bytes
    filename: Optional[str] = None


class LocationContent(BaseModel):
    """Location message content with latitude and longitude."""
    latitude: float
    longitude: float


# ===========================
# 📌 Telegram Actions
# ===========================

class TelegramAction(str, Enum):
    """Telegram bot actions that can be sent to show user activity."""
    UNKNOWN_ACTION = "UNKNOWN_ACTION"
    TYPING = "TYPING"
    UPLOADING_PHOTO = "UPLOADING_PHOTO"
    UPLOADING_VIDEO = "UPLOADING_VIDEO"
    UPLOADING_DOCUMENT = "UPLOADING_DOCUMENT"
    UPLOADING_AUDIO = "UPLOADING_AUDIO"
    RECORDING_VIDEO = "RECORDING_VIDEO"
    RECORDING_AUDIO = "RECORDING_AUDIO"
    UPLOADING_ANIMATION = "UPLOADING_ANIMATION"


# ===========================
# 📌 Interactive UI Components
# ===========================

class InlineButton(BaseModel):
    """A single inline keyboard button."""
    text: str
    callback_data: str


class InlineButtonRow(BaseModel):
    """A row of inline keyboard buttons."""
    buttons: List[InlineButton]


class InlineKeyboard(BaseModel):
    """Inline keyboard with multiple rows of buttons."""
    rows: List[InlineButtonRow]


# ===========================
# 📌 Telegram Message Structure
# ===========================

class TelegramMessage(BaseModel):
    """
    Unified Telegram message structure that can contain different types of content.
    Only one content field should be provided per message.
    """
    message_id: Optional[str] = None

    # Content - only one should be provided
    text: Optional[TextContent] = None
    image: Optional[ImageContent] = None
    video: Optional[VideoContent] = None
    audio: Optional[AudioContent] = None
    document: Optional[DocumentContent] = None
    location: Optional[LocationContent] = None

    # UI components
    inline_keyboard: Optional[InlineKeyboard] = None
    
    # Bot action
    action: Optional[TelegramAction] = TelegramAction.UNKNOWN_ACTION


# ===========================
# 📌 Callback and Reply Handling
# ===========================

class CallbackQuery(BaseModel):
    """Represents a callback query from an inline keyboard button press."""
    callback_data: str
    original_message: TelegramMessage


class ReplyMessage(BaseModel):
    """Represents a reply to a previous message."""
    original_message: TelegramMessage


# ===========================
# 📌 Context and Memory
# ===========================

class ContextMessage(BaseModel):
    """A single message in the conversation context."""
    role: str  # "user", "assistant", or "tool"
    content: str
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    name: Optional[str] = None
    tool_call_id: Optional[str] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None
    function_call: Optional[Dict[str, Any]] = None


class Context(BaseModel):
    """Chat context containing message history and metadata."""
    chat_id: int
    messages: List[ContextMessage] = []
    metadata: Optional[Dict[str, Union[str, int, float, bool]]] = {}




# ===========================
# 📌 Payment System
# ===========================

class UsagePaymentRequest(BaseModel):
    """Request payment for agent usage."""
    key: str  # Payment key identifier configured in web console (e.g., "text_analysis", "image_processing")
    quantity: int  # Number of operations (e.g., 1 for single operation, 60 for 60 minutes of processing)


# ===========================
# 📌 Core Agent Interface
# ===========================

class AgentRequest(BaseModel):
    """
    Main request structure sent to agents containing all necessary data
    for processing user interactions.
    """
    # Message content
    telegram_message: Optional[TelegramMessage] = None
    callback_query: Optional[CallbackQuery] = None
    reply_message: Optional[ReplyMessage] = None
    
    # Context
    context: Optional[Context] = None
    
    # Payment and user info
    paid: bool = False
    language_code: Optional[str] = None
    user_id: Optional[int] = None


class AgentResponse(BaseModel):
    """
    Response structure that agents return. Can contain a message to send,
    a payment request, or memory to store.
    """
    # Response content
    telegram_message: Optional[TelegramMessage] = None
    payment_request: Optional[UsagePaymentRequest] = None
    
    # Memory storage
    memory: Optional[ContextMessage] = None