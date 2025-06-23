"""
Main entry point for Echo Agent.

This demonstrates all AnyAgent data types and payment request features.
"""

import os
import asyncio
import logging
from anyagent import serve_agent

from agent import agent

# Configure detailed logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("echo_agent.main")

def main():
    """Run the Echo Agent server."""
    port = int(os.getenv("GRPC_PORT", "50051"))
    
    logger.info("🚀 Starting Echo Agent - AnyAgent Data Types Demonstration")
    logger.info(f"📡 Server will listen on port {port}")
    logger.info("🎯 This agent demonstrates:")
    logger.info("   • All supported data types (text, image, video, audio, document, location)")
    logger.info("   • Payment requests for different content types")
    logger.info("   • Streaming responses and interactive keyboards")
    logger.info("   • Usage tracking and free limits")
    logger.info("")
    logger.info("💡 How to test:")
    logger.info("   1. Send text messages (5 credits each)")
    logger.info("   2. Send images (25 credits each)")
    logger.info("   3. Send videos (100 credits each)")
    logger.info("   4. Send audio files (50 credits each)")
    logger.info("   5. Send documents (15 credits each)")
    logger.info("   6. Send locations (10 credits each)")
    logger.info("")
    logger.info("🔊 Echo Agent is ready to demonstrate all AnyAgent features!")
    
    serve_agent(agent, port=port)

if __name__ == "__main__":
    main()
