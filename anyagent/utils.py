"""
AnyAgent Framework - Utility Functions

Conversion utilities between gRPC protocol buffers and Pydantic models.
Essential functions for agent framework operation.
"""

import random

from .proto import agent_pb2
from .schema import (
    TelegramMessage, TextContent, ImageContent, VideoContent,
    AudioContent, DocumentContent, LocationContent, InlineKeyboard,
    TelegramAction, CallbackQuery, ReplyMessage, Context,
    ContextMessage, AgentRequest, AgentResponse,
    dict_to_struct, struct_to_dict
)


def generate_message_id() -> str:
    """Generate a random message ID for tracking."""
    return str(random.randint(100000, 999999))


def grpc_to_pydantic_request(grpc_req: agent_pb2.AgentRequest) -> AgentRequest:
    """Convert gRPC AgentRequest to Pydantic AgentRequest."""
    
    # Convert TelegramMessage if present
    telegram_message = None
    if grpc_req.HasField('telegram_message'):
        telegram_message = _grpc_to_pydantic_msg(grpc_req.telegram_message)
    
    # Convert CallbackQuery if present
    callback_query = None
    if grpc_req.HasField('callback_query'):
        callback_query = CallbackQuery(
            callback_data=grpc_req.callback_query.callback_data,
            original_message=_grpc_to_pydantic_msg(grpc_req.callback_query.original_message)
        )
    
    # Convert ReplyMessage if present
    reply_message = None
    if grpc_req.HasField('reply_message'):
        reply_message = ReplyMessage(
            original_message=_grpc_to_pydantic_msg(grpc_req.reply_message.original_message)
        )
    
    # Convert Context if present
    context = None
    if grpc_req.HasField('context'):
        context_messages = []
        for msg in grpc_req.context.messages:
            context_msg = ContextMessage(
                role=msg.role,
                content=msg.content,
                timestamp=msg.timestamp,
                name=msg.name if msg.HasField('name') else None,
                tool_call_id=msg.tool_call_id if msg.HasField('tool_call_id') else None,
                tool_calls=[struct_to_dict(tc) for tc in msg.tool_calls] if msg.tool_calls else None,
                function_call=struct_to_dict(msg.function_call) if msg.HasField('function_call') else None
            )
            context_messages.append(context_msg)
        
        metadata = struct_to_dict(grpc_req.context.metadata) if grpc_req.context.metadata else {}
        context = Context(
            chat_id=grpc_req.context.chat_id,
            messages=context_messages,
            metadata=metadata
        )
    
    return AgentRequest(
        telegram_message=telegram_message,
        callback_query=callback_query,
        reply_message=reply_message,
        context=context,
        paid=grpc_req.paid if grpc_req.HasField('paid') else False,
        language_code=grpc_req.language_code if grpc_req.HasField('language_code') else None,
        user_id=grpc_req.user_id if grpc_req.HasField('user_id') else None
    )


def pydantic_to_grpc_response(pydantic_resp: AgentResponse) -> agent_pb2.AgentResponse:
    """Convert Pydantic AgentResponse to gRPC AgentResponse."""
    
    grpc_resp = agent_pb2.AgentResponse()
    
    # Convert TelegramMessage if present
    if pydantic_resp.telegram_message:
        grpc_resp.telegram_message.CopyFrom(_pydantic_to_grpc_msg(pydantic_resp.telegram_message))
    
    # Convert PaymentRequest if present
    if pydantic_resp.payment_request:
        grpc_resp.payment_request.key = pydantic_resp.payment_request.key
        grpc_resp.payment_request.quantity = pydantic_resp.payment_request.quantity
    
    # Convert Memory if present
    if pydantic_resp.memory:
        grpc_resp.memory.role = pydantic_resp.memory.role
        grpc_resp.memory.content = pydantic_resp.memory.content
        grpc_resp.memory.timestamp = pydantic_resp.memory.timestamp
        if pydantic_resp.memory.name:
            grpc_resp.memory.name = pydantic_resp.memory.name
        if pydantic_resp.memory.tool_call_id:
            grpc_resp.memory.tool_call_id = pydantic_resp.memory.tool_call_id
        if pydantic_resp.memory.tool_calls:
            for tc in pydantic_resp.memory.tool_calls:
                grpc_resp.memory.tool_calls.append(dict_to_struct(tc))
        if pydantic_resp.memory.function_call:
            grpc_resp.memory.function_call.CopyFrom(dict_to_struct(pydantic_resp.memory.function_call))
    
    return grpc_resp


def _grpc_to_pydantic_msg(grpc_msg: agent_pb2.TelegramMessage) -> TelegramMessage:
    """Convert gRPC TelegramMessage to Pydantic TelegramMessage."""
    
    # Determine content type and extract content
    content_fields = {}
    
    if grpc_msg.HasField('text'):
        content_fields['text'] = TextContent(text=grpc_msg.text.text)
    elif grpc_msg.HasField('image'):
        content_fields['image'] = ImageContent(
            image_data=grpc_msg.image.image_data,
            caption=grpc_msg.image.caption if grpc_msg.image.HasField('caption') else None,
            filename=grpc_msg.image.filename if grpc_msg.image.HasField('filename') else None
        )
    elif grpc_msg.HasField('video'):
        content_fields['video'] = VideoContent(
            video_data=grpc_msg.video.video_data,
            caption=grpc_msg.video.caption if grpc_msg.video.HasField('caption') else None,
            filename=grpc_msg.video.filename if grpc_msg.video.HasField('filename') else None
        )
    elif grpc_msg.HasField('audio'):
        content_fields['audio'] = AudioContent(
            audio_data=grpc_msg.audio.audio_data,
            filename=grpc_msg.audio.filename if grpc_msg.audio.HasField('filename') else None
        )
    elif grpc_msg.HasField('document'):
        content_fields['document'] = DocumentContent(
            file_data=grpc_msg.document.file_data,
            filename=grpc_msg.document.filename if grpc_msg.document.HasField('filename') else None
        )
    elif grpc_msg.HasField('location'):
        content_fields['location'] = LocationContent(
            latitude=grpc_msg.location.latitude,
            longitude=grpc_msg.location.longitude
        )
    
    # Convert inline keyboard if present
    inline_keyboard = None
    if grpc_msg.HasField('inline_keyboard'):
        inline_keyboard = _convert_inline_keyboard_grpc(grpc_msg.inline_keyboard)
    
    # Convert action
    action = TelegramAction(grpc_msg.action) if grpc_msg.HasField('action') else TelegramAction.UNKNOWN_ACTION
    
    return TelegramMessage(
        message_id=grpc_msg.message_id if grpc_msg.HasField('message_id') else None,
        inline_keyboard=inline_keyboard,
        action=action,
        **content_fields
    )


def _pydantic_to_grpc_msg(pydantic_msg: TelegramMessage) -> agent_pb2.TelegramMessage:
    """Convert Pydantic TelegramMessage to gRPC TelegramMessage."""
    
    grpc_msg = agent_pb2.TelegramMessage()
    
    # Set message ID
    if pydantic_msg.message_id:
        grpc_msg.message_id = pydantic_msg.message_id
    
    # Set content based on type
    if pydantic_msg.text:
        grpc_msg.text.text = pydantic_msg.text.text
    elif pydantic_msg.image:
        grpc_msg.image.image_data = pydantic_msg.image.image_data
        if pydantic_msg.image.caption:
            grpc_msg.image.caption = pydantic_msg.image.caption
        if pydantic_msg.image.filename:
            grpc_msg.image.filename = pydantic_msg.image.filename
    elif pydantic_msg.video:
        grpc_msg.video.video_data = pydantic_msg.video.video_data
        if pydantic_msg.video.caption:
            grpc_msg.video.caption = pydantic_msg.video.caption
        if pydantic_msg.video.filename:
            grpc_msg.video.filename = pydantic_msg.video.filename
    elif pydantic_msg.audio:
        grpc_msg.audio.audio_data = pydantic_msg.audio.audio_data
        if pydantic_msg.audio.filename:
            grpc_msg.audio.filename = pydantic_msg.audio.filename
    elif pydantic_msg.document:
        grpc_msg.document.file_data = pydantic_msg.document.file_data
        if pydantic_msg.document.filename:
            grpc_msg.document.filename = pydantic_msg.document.filename
    elif pydantic_msg.location:
        grpc_msg.location.latitude = pydantic_msg.location.latitude
        grpc_msg.location.longitude = pydantic_msg.location.longitude
    
    # Set inline keyboard
    if pydantic_msg.inline_keyboard:
        grpc_msg.inline_keyboard.CopyFrom(_convert_inline_keyboard_pydantic(pydantic_msg.inline_keyboard))
    
    # Set action
    if pydantic_msg.action:
        grpc_msg.action = agent_pb2.TelegramAction.Value(pydantic_msg.action.value)
    
    return grpc_msg


def _convert_inline_keyboard_grpc(grpc_keyboard: agent_pb2.InlineKeyboard) -> InlineKeyboard:
    """Convert gRPC InlineKeyboard to Pydantic InlineKeyboard."""
    rows = []
    for grpc_row in grpc_keyboard.rows:
        buttons = []
        for grpc_button in grpc_row.buttons:
            buttons.append({
                "text": grpc_button.text,
                "callback_data": grpc_button.callback_data
            })
        rows.append({"buttons": buttons})
    return InlineKeyboard(rows=rows)


def _convert_inline_keyboard_pydantic(pydantic_keyboard: InlineKeyboard) -> agent_pb2.InlineKeyboard:
    """Convert Pydantic InlineKeyboard to gRPC InlineKeyboard."""
    grpc_keyboard = agent_pb2.InlineKeyboard()
    for row in pydantic_keyboard.rows:
        grpc_row = agent_pb2.InlineButtonRow()
        for button in row["buttons"]:
            grpc_button = agent_pb2.InlineButton()
            grpc_button.text = button["text"]
            grpc_button.callback_data = button["callback_data"]
            grpc_row.buttons.append(grpc_button)
        grpc_keyboard.rows.append(grpc_row)
    return grpc_keyboard