import asyncio
import logging
import sqlite3
from typing import List, Dict, Any, Optional
from datetime import datetime
import aiosqlite
from jarvis.config import settings

logger = logging.getLogger(__name__)


class TaskLogger:
    """Service for logging tasks and conversations to SQLite database."""

    def __init__(self) -> None:
        """Initialize the task logger."""
        self.db_path = settings.database_path
        self._initialized = False

    async def initialize(self) -> None:
        """Initialize the database and create tables."""
        if self._initialized:
            return

        try:
            # Create data directory if it doesn't exist
            import os
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

            async with aiosqlite.connect(self.db_path) as db:
                # Enable WAL mode for better performance
                await db.execute("PRAGMA journal_mode=WAL;")
                await db.execute("PRAGMA synchronous=NORMAL;")

                # Create tasks table
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS tasks (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        session_id TEXT NOT NULL,
                        message TEXT NOT NULL,
                        response TEXT NOT NULL,
                        response_time_ms INTEGER NOT NULL,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        created_at REAL
                    );
                """)

                # Create indexes for better performance
                await db.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON tasks(timestamp);")
                await db.execute("CREATE INDEX IF NOT EXISTS idx_session_id ON tasks(session_id);")

                await db.commit()

            self._initialized = True
            logger.info("Task logger initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize task logger: {e}")
            raise

    async def close(self) -> None:
        """Close database connections."""
        # aiosqlite handles connection closing automatically
        self._initialized = False

    async def check_health(self) -> bool:
        """Check if database is accessible."""
        try:
            if not self._initialized:
                await self.initialize()

            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("SELECT 1;")
                return True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False

    async def log_task(
        self,
        session_id: str,
        message: str,
        response: str,
        response_time_ms: int
    ) -> None:
        """Log a completed task to the database."""
        try:
            if not self._initialized:
                await self.initialize()

            # Retry logic for database locked errors
            max_retries = 3
            retry_delay = 0.1

            for attempt in range(max_retries):
                try:
                    async with aiosqlite.connect(self.db_path) as db:
                        await db.execute("""
                            INSERT INTO tasks (session_id, message, response, response_time_ms, created_at)
                            VALUES (?, ?, ?, ?, ?);
                        """, (session_id, message, response, response_time_ms, datetime.now().timestamp()))
                        await db.commit()
                    break
                except sqlite3.OperationalError as e:
                    if "database is locked" in str(e) and attempt < max_retries - 1:
                        logger.warning(f"Database locked, retrying in {retry_delay}s (attempt {attempt + 1})")
                        await asyncio.sleep(retry_delay)
                        retry_delay *= 2  # Exponential backoff
                    else:
                        raise

            logger.debug(f"Logged task for session {session_id}")

        except Exception as e:
            logger.error(f"Failed to log task: {e}")
            # Don't crash the application

    async def get_recent_tasks(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Retrieve the most recent tasks."""
        try:
            if not self._initialized:
                await self.initialize()

            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                cursor = await db.execute("""
                    SELECT session_id, message, response, response_time_ms, timestamp
                    FROM tasks
                    ORDER BY timestamp DESC
                    LIMIT ?;
                """, (limit,))

                rows = await cursor.fetchall()

                tasks = []
                for row in rows:
                    tasks.append({
                        "session_id": row["session_id"],
                        "message": row["message"],
                        "response_preview": row["response"][:100] + "..." if len(row["response"]) > 100 else row["response"],
                        "response_time_ms": row["response_time_ms"],
                        "timestamp": row["timestamp"]
                    })

                return tasks

        except Exception as e:
            logger.error(f"Failed to retrieve recent tasks: {e}")
            return []


# Global task logger instance
task_logger = TaskLogger()