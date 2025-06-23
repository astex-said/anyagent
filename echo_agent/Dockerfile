FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy the entire project structure
COPY . .

# Install anyagent package in development mode
RUN pip install -e .

# Install echo agent dependencies
RUN pip install -r echo_agent/requirements.txt

WORKDIR /app/echo_agent

# Expose the gRPC port
EXPOSE 50061

# Set environment variables
ENV GRPC_PORT=50061
ENV PYTHONPATH=/app

# Run the agent
CMD ["python3", "main.py"]