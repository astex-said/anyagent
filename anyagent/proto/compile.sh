#!/bin/bash

# Generate the protobuf files from agent.proto
python3 -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. proto/agent.proto

# Copy the generated protobuf files to the anyagent directory
cp -r proto ./anyagent/

# Copy the generated protobuf files to all agent directories inside ./agents/
for dir in ./agents/*; do
  if [ -d "$dir" ]; then  # Ensure we're copying only to directories
    # cp proto/agent_pb2_grpc.py "$dir/"
    # cp proto/agent_pb2.py "$dir/"
    cp -r proto "$dir/"
  fi
done

echo "Protobuf files updated in all agent directories."