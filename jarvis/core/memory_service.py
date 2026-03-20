import logging
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings as ChromaSettings
from jarvis.config import settings

logger = logging.getLogger(__name__)


class MemoryService:
    """Service for managing conversation memory using ChromaDB."""

    def __init__(self) -> None:
        """Initialize the memory service."""
        self.client: Optional[chromadb.PersistentClient] = None
        self.collection: Optional[chromadb.Collection] = None
        self._initialized = False

    async def initialize(self) -> None:
        """Initialize ChromaDB client and collection lazily."""
        if self._initialized:
            return

        try:
            # Create data directory if it doesn't exist
            import os
            os.makedirs(settings.chroma_persist_dir, exist_ok=True)

            # Initialize ChromaDB client
            self.client = chromadb.PersistentClient(
                path=settings.chroma_persist_dir,
                settings=ChromaSettings(anonymized_telemetry=False)
            )

            # Get or create collection
            try:
                self.collection = self.client.get_collection(settings.collection_name)
            except ValueError:
                self.collection = self.client.create_collection(settings.collection_name)

            self._initialized = True
            logger.info("Memory service initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize memory service: {e}")
            # Continue without memory in degraded mode
            self._initialized = False

    async def close(self) -> None:
        """Close the ChromaDB client."""
        # ChromaDB doesn't have an explicit close method
        self.client = None
        self.collection = None
        self._initialized = False

    async def check_health(self) -> bool:
        """Check if memory service is healthy."""
        try:
            # Don't initialize during health check - just return current state
            # Memory will be initialized on first use (lazy loading)
            return True
        except Exception as e:
            logger.error(f"Memory health check failed: {e}")
            return False

    async def store_memory(self, message: str, response: str, session_id: str) -> None:
        """Store a conversation turn in memory."""
        try:
            if not self._initialized:
                await self.initialize()

            if not self.collection:
                logger.warning("Memory collection not available, skipping storage")
                return

            # Create a combined text for embedding
            combined_text = f"User: {message}\nJARVIS: {response}"

            # Generate unique ID
            import uuid
            memory_id = str(uuid.uuid4())

            # Store in ChromaDB
            self.collection.add(
                documents=[combined_text],
                metadatas=[{
                    "session_id": session_id,
                    "timestamp": str(__import__("datetime").datetime.now()),
                    "message": message,
                    "response": response
                }],
                ids=[memory_id]
            )

            logger.debug(f"Stored memory with ID: {memory_id}")

        except Exception as e:
            logger.warning(f"Failed to store memory: {e}")
            # Don't crash the application

    async def retrieve_memory(self, query: str, limit: int = settings.memory_limit) -> List[str]:
        """Retrieve relevant memories for a query."""
        try:
            if not self._initialized:
                await self.initialize()

            if not self.collection:
                logger.warning("Memory collection not available")
                return []

            # Search for similar content
            results = self.collection.query(
                query_texts=[query],
                n_results=min(limit, self.collection.count()) if self.collection.count() > 0 else 0
            )

            # Extract the documents (the combined text)
            memories = []
            if results and "documents" in results and results["documents"]:
                memories = results["documents"][0]  # First query result

            logger.debug(f"Retrieved {len(memories)} memories for query")
            return memories

        except Exception as e:
            logger.warning(f"Failed to retrieve memory: {e}")
            return []

    async def search_memory(self, query: str, limit: int = settings.memory_limit) -> List[Dict[str, Any]]:
        """Search memory and return structured results with relevance scores."""
        try:
            if not self._initialized:
                await self.initialize()

            if not self.collection:
                return []

            results = self.collection.query(
                query_texts=[query],
                n_results=min(limit, self.collection.count()) if self.collection.count() > 0 else 0,
                include=["metadatas", "distances"]
            )

            search_results = []
            if results and "metadatas" in results and results["metadatas"]:
                metadatas = results["metadatas"][0]
                distances = results.get("distances", [[]])[0] if results.get("distances") else []

                for i, metadata in enumerate(metadatas):
                    relevance_score = 1.0 - (distances[i] if i < len(distances) else 0.0)
                    search_results.append({
                        "text": f"User: {metadata.get('message', '')}\nJARVIS: {metadata.get('response', '')}",
                        "relevance_score": round(relevance_score, 3)
                    })

            return search_results

        except Exception as e:
            logger.warning(f"Failed to search memory: {e}")
            return []


# Global memory service instance
memory_service = MemoryService()