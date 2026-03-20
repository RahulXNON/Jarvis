# JARVIS Setup Guide

## Prerequisites
- Docker Desktop installed and running
- At least 8GB RAM available on your system
- Git (optional, for cloning)

## Step-by-Step Setup

### 1. Download the Project
If you have git:
```bash
git clone <repository-url>
cd jarvis
```

Or download the ZIP file and extract it to a folder called `jarvis`.

### 2. Environment Configuration
```bash
copy .env.example .env
```
Edit `.env` if you need to change any default settings.

### 3. Start Services
```bash
docker-compose up -d
```

This will:
- Start the Ollama container and download the phi3-mini model
- Start the JARVIS FastAPI application
- Both services will restart automatically if they crash

### 4. Wait for Model Download
First time setup takes longer as Ollama downloads the 2.3GB phi3-mini model:
```bash
docker-compose logs ollama
```
Wait until you see confirmation that the model is loaded.

### 5. Verify Installation
```bash
curl -X GET http://localhost:8000/health
```

Should return:
```json
{
  "ollama": true,
  "memory": true,
  "uptime_seconds": 123
}
```

### 6. Test Chat
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello Jarvis", "session_id": "test1"}'
```

You should see JARVIS respond with a streaming text response.

## Stopping the Services
```bash
docker-compose down
```

## Updating
```bash
docker-compose pull
docker-compose up -d
```