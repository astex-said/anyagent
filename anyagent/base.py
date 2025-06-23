"""
Base Agent class that all AnyAgent implementations should inherit from.
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import AsyncGenerator, Optional, Dict, Any

from .schema import AgentRequest, AgentResponse


class BaseAgent(ABC):
    """
    Base class for all AnyAgent implementations.
    
    Subclasses should implement the execute and help methods to define
    the agent's behavior. The framework handles all gRPC communication,
    payment processing, and request/response conversion.
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Initialize the base agent.
        
        Args:
            logger: Custom logger instance (optional)
        """
        self.name = self.__class__.__name__
        self.logger = logger or logging.getLogger(f"anyagent.{self.name}")
        
        # Initialize any database connections or setup
        self._initialize()
    
    def _initialize(self):
        """
        Override this method to perform any initialization tasks
        (database setup, API client initialization, etc.)
        """
        pass
    
    @abstractmethod
    async def execute(self, request: AgentRequest) -> AsyncGenerator[AgentResponse, None]:
        """
        Main execution method for the agent.
        
        This method should yield AgentResponse objects as the agent processes
        the request. It can yield multiple responses for streaming behavior,
        and can yield payment requests when needed.
        
        Args:
            request: The incoming agent request
            
        Yields:
            AgentResponse objects containing the agent's responses
        """
        pass
    
    @abstractmethod  
    async def help(self, request: AgentRequest) -> AsyncGenerator[AgentResponse, None]:
        """
        Help method that explains how to use the agent.
        
        Args:
            request: The incoming help request
            
        Yields:
            AgentResponse objects explaining the agent's capabilities
        """
        pass
    
    def get_config(self) -> Dict[str, Any]:
        """
        Get the agent configuration for registration.
        
        Returns:
            Dictionary containing agent metadata and function mappings
        """
        return {
            "name": self.name,
            "execute": self.execute,
            "help": self.help,
        }
    
    def get_metadata(self) -> Dict[str, Any]:
        """
        Get agent metadata for web console registration validation.
        
        Returns:
            Dictionary containing agent metadata for validation
        """
        return {
            "name": self.name,
            "version": getattr(self, 'version', '1.0.0'),
            "status": "running",
            "supported_features": {
                "streaming_responses": True,
                "payment_requests": True,
                "async_execution": True,
                "help_command": True,
            }
        }
    
    async def cleanup(self):
        """
        Override this method to perform cleanup tasks when the agent is stopped.
        (Close database connections, HTTP sessions, etc.)
        """
        pass


class SimpleAgent(BaseAgent):
    """
    A simplified agent class for quick prototyping.
    
    Allows defining execute and help functions directly without subclassing.
    """
    
    def __init__(self, execute_func, help_func):
        """
        Initialize a simple agent with function callbacks.
        
        Args:
            execute_func: Async function that handles execute requests
            help_func: Async function that handles help requests
        """
        super().__init__()
        self._execute_func = execute_func
        self._help_func = help_func
    
    async def execute(self, request: AgentRequest) -> AsyncGenerator[AgentResponse, None]:
        """Execute using the provided function."""
        async for response in self._execute_func(request):
            yield response
    
    async def help(self, request: AgentRequest) -> AsyncGenerator[AgentResponse, None]:
        """Help using the provided function.""" 
        async for response in self._help_func(request):
            yield response 