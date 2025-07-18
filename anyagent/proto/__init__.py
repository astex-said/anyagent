"""
Proto package for AnyAgent framework.

Contains the gRPC protocol buffer definitions and generated code.
"""

from . import agent_pb2
from . import agent_pb2_grpc

__all__ = ['agent_pb2', 'agent_pb2_grpc']
