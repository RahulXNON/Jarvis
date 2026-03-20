import asyncio
import logging
import time
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse
from jarvis.config import settings
from jarvis.core.llm_service import llm_service
from jarvis.core.memory_service import memory_service
from jarvis.core.task_logger import task_logger
from jarvis.api.schemas import (
    ChatRequest, ChatResponse, HealthResponse,
    TasksResponse, MemorySearchResponse
)

logger = logging.getLogger(__name__)

# Response cache
response_cache: Dict[str, Dict[str, Any]] = {}


async def get_cached_response(message: str) -> Optional[str]:
    """Get cached response if available and not expired."""
    cache_key = message.strip().lower()
    if cache_key in response_cache:
        cached = response_cache[cache_key]
        if time.time() - cached["timestamp"] < settings.cache_ttl_seconds:
            return cached["response"]
        else:
            # Remove expired cache entry
            del response_cache[cache_key]
    return None


async def cache_response(message: str, response: str) -> None:
    """Cache a response for future use."""
    cache_key = message.strip().lower()
    response_cache[cache_key] = {
        "response": response,
        "timestamp": time.time()
    }


async def chat_endpoint(request: ChatRequest, req: Request) -> StreamingResponse:
    """Handle chat requests with streaming responses."""
    start_time = time.time()

    try:
        # Check for cached response
        cached_response = await get_cached_response(request.message)
        if cached_response:
            # Log the cached task
            response_time_ms = int((time.time() - start_time) * 1000)
            await task_logger.log_task(
                request.session_id,
                request.message,
                cached_response,
                response_time_ms
            )

            # Return cached response as streaming
            async def cached_stream():
                yield cached_response

            return StreamingResponse(
                cached_stream(),
                media_type="text/plain"
            )

        # Retrieve relevant memories
        memories = await memory_service.retrieve_memory(request.message)

        # Generate streaming response
        full_response = ""
        async def response_stream():
            nonlocal full_response
            try:
                async for token in llm_service.generate_response(request.message, memories):
                    full_response += token
                    yield token
            except Exception as e:
                logger.error(f"Error in response stream: {e}")
                yield "Sorry, I encountered an error."

        # Create streaming response
        stream_response = StreamingResponse(
            response_stream(),
            media_type="text/plain"
        )

        # Log the task after streaming completes (in background)
        async def log_after_stream():
            await asyncio.sleep(0.1)  # Small delay to ensure streaming completes
            response_time_ms = int((time.time() - start_time) * 1000)
            await task_logger.log_task(
                request.session_id,
                request.message,
                full_response,
                response_time_ms
            )

            # Store in memory
            await memory_service.store_memory(
                request.message,
                full_response,
                request.session_id
            )

            # Cache the response
            await cache_response(request.message, full_response)

        # Start background logging
        asyncio.create_task(log_after_stream())

        return stream_response

    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


async def health_endpoint(req: Request) -> HealthResponse:
    """Check the health of all services."""
    try:
        ollama_healthy = await llm_service.check_health()
        memory_healthy = await memory_service.check_health()

        # Calculate uptime from app state
        uptime_seconds = int(time.time() - req.app.state.start_time) if hasattr(req.app.state, 'start_time') else 0

        return HealthResponse(
            ollama=ollama_healthy,
            memory=memory_healthy,
            uptime_seconds=uptime_seconds
        )
    except Exception as e:
        logger.error(f"Error in health endpoint: {e}")
        raise HTTPException(status_code=500, detail="Health check failed")


async def tasks_endpoint(limit: int = 20) -> TasksResponse:
    """Retrieve recent tasks."""
    try:
        if limit < 1 or limit > 100:
            raise HTTPException(status_code=400, detail="Limit must be between 1 and 100")

        tasks = await task_logger.get_recent_tasks(limit)
        return TasksResponse(tasks=tasks)
    except Exception as e:
        logger.error(f"Error in tasks endpoint: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve tasks")


async def memory_search_endpoint(q: str, limit: int = 3) -> MemorySearchResponse:
    """Search conversation memory."""
    try:
        if not q.strip():
            raise HTTPException(status_code=400, detail="Query parameter 'q' is required")

        if limit < 1 or limit > 10:
            raise HTTPException(status_code=400, detail="Limit must be between 1 and 10")

        results = await memory_service.search_memory(q, limit)
        return MemorySearchResponse(results=results)
    except Exception as e:
        logger.error(f"Error in memory search endpoint: {e}")
        raise HTTPException(status_code=500, detail="Failed to search memory")


def create_routes(app: FastAPI) -> None:
    """Create and register all API routes."""

    @app.post("/chat", response_class=StreamingResponse)
    async def chat(request: ChatRequest, req: Request):
        """Send a message to JARVIS and get a streaming response."""
        return await chat_endpoint(request, req)

    @app.get("/health", response_model=HealthResponse)
    async def health(req: Request):
        """Check the health status of all services."""
        return await health_endpoint(req)

    @app.get("/tasks", response_model=TasksResponse)
    async def tasks(limit: int = 20):
        """Get recent conversation tasks."""
        return await tasks_endpoint(limit)

    @app.get("/memory/search", response_model=MemorySearchResponse)
    async def memory_search(q: str, limit: int = 3):
        """Search conversation memory."""
        return await memory_search_endpoint(q, limit)