"""
AnyAgent gRPC Server implementation.

This module provides the AgentServer class that handles all gRPC communication,
allowing agent developers to focus only on the agent logic.
"""

import asyncio
import logging
import os
from typing import Union, Dict, Any, Optional

import grpc
from .base import BaseAgent, SimpleAgent
from .proto import agent_pb2_grpc
from .proto.agent_pb2 import AgentRequest as GrpcAgentRequest, AgentResponse as GrpcAgentResponse
from .utils import grpc_to_pydantic_request, pydantic_to_grpc_response


class AgentServiceServicer(agent_pb2_grpc.AgentServiceServicer):
    """gRPC service implementation for AnyAgent."""
    
    def __init__(self, agent: BaseAgent):
        """
        Initialize the gRPC servicer with an agent instance.
        
        Args:
            agent: The agent instance to handle requests
        """
        self.agent = agent
        self.logger = agent.logger

    async def Help(self, request: GrpcAgentRequest, context):
        """Handle help requests."""
        self.logger.info(f"Help request received: {request}")
        
        try:
            pydantic_req = grpc_to_pydantic_request(request)
            async for resp in self.agent.help(pydantic_req):
                yield pydantic_to_grpc_response(resp)
        except Exception as e:
            self.logger.error(f"Error in Help: {e}")
            # Re-raise to let gRPC handle the error response
            raise

    async def ExecuteStream(self, request_iterator, context):
        """
        Handle streaming execution requests with payment support.
        
        This implements the payment-aware streaming protocol:
        1. Read the first AgentRequest and instantiate the agent generator
        2. Stream responses until a payment request
        3. Pause and wait for payment confirmation
        4. Resume streaming after payment
        """
        agent_gen = None
        awaiting_payment = False

        async for grpc_req in request_iterator:
            self.logger.info(f"ExecuteStream request: {grpc_req}")
            
            try:
                req = grpc_to_pydantic_request(grpc_req)

                # On first request, create the agent generator
                if agent_gen is None:
                    agent_gen = self.agent.execute(req)

                # If we're paused on payment, wait here until req.paid=True
                if awaiting_payment:
                    if not req.paid:
                        self.logger.info("⏸ Waiting for payment...")
                        continue
                    self.logger.info("✅ Payment received — resuming stream")
                    awaiting_payment = False

                # Drive the generator from where we left off
                try:
                    while True:
                        response = await agent_gen.__anext__()
                        grpc_resp = pydantic_to_grpc_response(response)
                        yield grpc_resp

                        # If the agent asks for payment, pause here
                        if response.payment_request:
                            self.logger.info("💳 Agent requested payment, pausing stream")
                            awaiting_payment = True
                            break

                except StopAsyncIteration:
                    self.logger.info(f"✅ {self.agent.name} Agent finished")
                    return

            except Exception as e:
                self.logger.error(f"Error in ExecuteStream: {e}")
                # Re-raise to let gRPC handle the error response
                raise

        self.logger.info("Client closed stream")


class AgentServer:
    """
    Main server class for running AnyAgent instances.
    
    This class handles all the gRPC server setup and configuration,
    allowing developers to focus only on their agent implementation.
    """
    
    def __init__(self, 
                 agent: Union[BaseAgent, Dict[str, Any]], 
                 port: Optional[int] = None,
                 logger: Optional[logging.Logger] = None):
        """
        Initialize the AnyAgent server.
        
        Args:
            agent: Either a BaseAgent instance or a legacy config dict
            port: Port to run the server on (defaults to GRPC_PORT env var or 50051)
            logger: Custom logger instance
        """
        self.port = port or int(os.getenv("GRPC_PORT", "50051"))
        self.logger = logger or logging.getLogger("anyagent.server")
        
        # Handle both new BaseAgent instances and legacy config dicts
        if isinstance(agent, BaseAgent):
            self.agent = agent
        elif isinstance(agent, dict):
            # Legacy support for existing agent configurations
            self.agent = SimpleAgent(
                execute_func=agent["execute"],
                help_func=agent["help"]
            )
        else:
            raise ValueError("Agent must be a BaseAgent instance or legacy config dict")
        
        self.server = None
        self.logger.info(f"🤖 AnyAgent Server initialized for {self.agent.name}")
    
    async def start(self):
        """Start the gRPC server."""
        self.server = grpc.aio.server()
        agent_pb2_grpc.add_AgentServiceServicer_to_server(
            AgentServiceServicer(self.agent), 
            self.server
        )
        
        listen_addr = f"[::]:{self.port}"
        self.server.add_insecure_port(listen_addr)
        
        self.logger.info(f"🚀 Starting {self.agent.name} gRPC server on port {self.port}...")
        await self.server.start()
        self.logger.info(f"✅ {self.agent.name} server listening on {listen_addr}")
        
        # Wait for termination
        await self.server.wait_for_termination()
    
    async def stop(self, grace_period: int = 5):
        """Stop the gRPC server gracefully."""
        if self.server:
            self.logger.info(f"🛑 Stopping {self.agent.name} server...")
            await self.server.stop(grace_period)
            await self.agent.cleanup()
            self.logger.info(f"✅ {self.agent.name} server stopped")
    
    def run(self):
        """Run the server (blocking call).""" 
        try:
            asyncio.run(self.start())
        except KeyboardInterrupt:
            self.logger.info("🛑 Server interrupted by user")
        except Exception as e:
            self.logger.error(f"❌ Server error: {e}")
            raise


def serve_agent(agent: Union[BaseAgent, Dict[str, Any]], 
               port: Optional[int] = None,
               logger: Optional[logging.Logger] = None):
    """
    Convenience function to quickly start an agent server.
    
    Args:
        agent: BaseAgent instance or legacy config dict
        port: Port to run on
        logger: Custom logger
    """
    server = AgentServer(agent, port, logger)
    server.run()


# Legacy support function for existing codebases
async def serve(port: Optional[int] = None, agent_mapping: Optional[Dict[str, Any]] = None):
    """
    Legacy serve function for backward compatibility.
    
    Args:
        port: Port to run on  
        agent_mapping: Legacy agent mapping dict
    """
    if agent_mapping is None:
        # Try to import from config.py
        try:
            from config import AGENT_MAPPING
            agent_mapping = AGENT_MAPPING
        except ImportError:
            raise ValueError("No agent mapping provided and config.py not found")
    
    server = AgentServer(agent_mapping, port)
    await server.start() 