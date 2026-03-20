# JARVIS - Personal AI Assistant

A lightweight, local AI assistant built with FastAPI, Ollama, and ChromaDB.

## Features

- **Conversational AI**: Chat with JARVIS using the phi3-mini model
- **Memory System**: Remembers previous conversations using ChromaDB
- **Task Logging**: Logs all interactions to SQLite database
- **Streaming Responses**: Real-time token streaming for responsive UI
- **Health Monitoring**: Built-in health checks for all services
- **Docker Optimized**: Runs in containers with memory limits

## Architecture

- **jarvis-core**: FastAPI application with embedded ChromaDB
- **ollama**: Local LLM service with phi3-mini model
- **SQLite**: Async database for task logging
- **Memory Caching**: Response caching for repeated queries

## API Endpoints

- `POST /chat` - Send message and get streaming response
- `GET /health` - Service health status
- `GET /tasks` - Retrieve logged tasks
- `GET /memory/search` - Search conversation memory

## Quick Start

See [SETUP.md](SETUP.md) for installation instructions.

## Requirements

- Docker Desktop
- 8GB RAM minimum
- Python 3.11 (for development)

## Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run locally (requires Ollama running separately)
uvicorn jarvis.main:app --reload
```