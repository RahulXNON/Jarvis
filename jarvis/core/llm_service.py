import logging
from typing import AsyncGenerator, List, Optional
import httpx
from jarvis.config import settings

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """
You are JARVIS, a personal AI assistant.
You are precise, helpful, and concise.
Before answering, think through the steps needed.
Always state what you are about to do.
If you are unsure, say so clearly.
Keep responses focused and practical.
"""


class LLMService:
    """Service for interacting with Ollama LLM."""

    def __init__(self) -> None:
        """Initialize the LLM service."""
        self.base_url = settings.ollama_base_url
        self.model = settings.ollama_model
        self.client: Optional[httpx.AsyncClient] = None
        self._initialized = False

    async def initialize(self) -> None:
        """Initialize the HTTP client for Ollama."""
        if self._initialized:
            return

        try:
            self.client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=300.0
            )
            self._initialized = True
            logger.info(f"LLM service initialized with model: {self.model}")
        except Exception as e:
            logger.error(f"Failed to initialize LLM service: {e}")
            raise

    async def close(self) -> None:
        """Close the HTTP client."""
        if self.client:
            await self.client.aclose()
        self._initialized = False

    async def check_health(self) -> bool:
        """Check if Ollama service is healthy."""
        try:
            if not self._initialized:
                await self.initialize()

            if not self.client:
                return False

            response = await self.client.get("/api/tags", timeout=2.0)
            return response.status_code == 200
        except Exception as e:
            logger.debug(f"Ollama health check failed (this is OK if Ollama not running): {e}")
            return False

    async def generate_response(
        self,
        user_message: str,
        memories: List[str] = None
    ) -> AsyncGenerator[str, None]:
        """Generate a streaming response from the LLM."""
        try:
            if not self._initialized:
                await self.initialize()

            if not self.client:
                raise Exception("LLM client not initialized")

            # Build context from memories
            context = ""
            if memories:
                context = "\n\nRelevant context from previous conversations:\n"
                for memory in memories[:3]:  # Limit to top 3
                    context += f"- {memory}\n"

            # Build the prompt
            full_prompt = f"{context}\nUser: {user_message}"

            # Call Ollama API with streaming
            async with self.client.stream(
                "POST",
                "/api/generate",
                json={
                    "model": self.model,
                    "prompt": full_prompt,
                    "system": SYSTEM_PROMPT,
                    "stream": True,
                    "temperature": 0.7
                }
            ) as response:
                if response.status_code != 200:
                    text = (await response.aiter_text()).strip()
                    logger.error(f"Ollama /api/generate returned {response.status_code}: {text}")
                    raise Exception(f"Ollama returned status {response.status_code}: {text}")

                async for line in response.aiter_lines():
                    if line:
                        import json
                        try:
                            data = json.loads(line)
                            if "response" in data:
                                yield data["response"]
                        except json.JSONDecodeError:
                            logger.debug(f"Failed to decode JSON: {line}")

        except httpx.ConnectError:
            logger.error("Failed to connect to Ollama service")
            yield "JARVIS brain is offline, please start Ollama"
        except httpx.TimeoutException:
            logger.error("Ollama request timed out")
            yield "Request timed out. Please try again."
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            yield f"Sorry, I encountered an error: {str(e)}"


# Global LLM service instance
llm_service = LLMService()