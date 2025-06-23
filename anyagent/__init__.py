"""
AnyAgent Framework - A standardized framework for building gRPC-based Telegram agents.

This package provides all the common infrastructure needed to build Telegram agents
that communicate via gRPC, allowing developers to focus only on the agent logic.
"""

__version__ = "1.0.0"
__author__ = "AnyAgent Team"

# Core framework components
from .base import BaseAgent
from .server import AgentServer
from .schema import *
from .utils import *

# Removed CLI and health modules - keeping framework minimal

__all__ = [
    # Core classes
    "BaseAgent",
    "AgentServer", 
    
    # Schema models
    "AgentRequest",
    "AgentResponse", 
    "TelegramMessage",
    "TextContent",
    "ImageContent", 
    "VideoContent",
    "AudioContent",
    "DocumentContent",
    "LocationContent",
    "InlineKeyboard",
    "TelegramAction",
    "CallbackQuery",
    "ReplyMessage",
    "Context",
    "ContextMessage", 
    "UsagePaymentRequest",
    
    # Utility functions
    "grpc_to_pydantic_request",
    "pydantic_to_grpc_response", 
    "generate_message_id",
] 