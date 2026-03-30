"""
Database access module for Customer Success FTE.
Provides connection pooling and database operations.
"""

import asyncpg
import os
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
import json


class Database:
    """Database connection manager with connection pooling."""

    _instance: Optional['Database'] = None
    _pool: Optional[asyncpg.Pool] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    async def connect(self):
        """Initialize database connection pool."""
        if self._pool is not None:
            return

        host = os.getenv('POSTGRES_HOST', 'localhost')
        port = os.getenv('POSTGRES_PORT', '5432')
        database = os.getenv('POSTGRES_DB', 'fte_db')
        user = os.getenv('POSTGRES_USER', 'postgres')
        password = os.getenv('POSTGRES_PASSWORD', 'postgres')

        self._pool = await asyncpg.create_pool(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password,
            min_size=5,
            max_size=20,
            command_timeout=60
        )

    async def disconnect(self):
        """Close database connection pool."""
        if self._pool:
            await self._pool.close()
            self._pool = None

    async def fetch(self, query: str, *args) -> List[asyncpg.Record]:
        """Fetch multiple rows."""
        async with self._pool.acquire() as conn:
            return await conn.fetch(query, *args)

    async def fetchrow(self, query: str, *args) -> Optional[asyncpg.Record]:
        """Fetch single row."""
        async with self._pool.acquire() as conn:
            return await conn.fetchrow(query, *args)

    async def fetchval(self, query: str, *args) -> Any:
        """Fetch single value."""
        async with self._pool.acquire() as conn:
            return await conn.fetchval(query, *args)

    async def execute(self, query: str, *args) -> str:
        """Execute query and return status."""
        async with self._pool.acquire() as conn:
            return await conn.execute(query, *args)

    async def insert(self, table: str, data: Dict[str, Any]) -> str:
        """Insert row and return ID."""
        columns = ', '.join(data.keys())
        placeholders = ', '.join(f'${i}' for i in range(1, len(data) + 1))
        values = list(data.values())

        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders}) RETURNING id"
        return await self.fetchval(query, *values)

    async def upsert(self, table: str, data: Dict[str, Any], 
                     conflict_columns: List[str]) -> str:
        """Upsert row and return ID."""
        columns = ', '.join(data.keys())
        placeholders = ', '.join(f'${i}' for i in range(1, len(data) + 1))
        values = list(data.values())
        conflict_cols = ', '.join(conflict_columns)
        
        update_cols = ', '.join(
            f"{col} = EXCLUDED.{col}" 
            for col in data.keys() 
            if col not in conflict_columns
        )

        query = f"""
            INSERT INTO {table} ({columns}) 
            VALUES ({placeholders})
            ON CONFLICT ({conflict_cols}) 
            DO UPDATE SET {update_cols}
            RETURNING id
        """
        return await self.fetchval(query, *values)


# Global database instance
db = Database()


async def get_db() -> Database:
    """Get database instance."""
    if db._pool is None:
        await db.connect()
    return db


async def close_db():
    """Close database connection."""
    await db.disconnect()


# =============================================================================
# Customer Operations
# =============================================================================

async def get_or_create_customer(
    email: Optional[str] = None,
    phone: Optional[str] = None,
    name: Optional[str] = None
) -> str:
    """Get or create customer by email or phone."""
    conn = await get_db()
    return await conn.fetchval(
        "SELECT get_or_create_customer($1, $2, $3)",
        email, phone, name
    )


async def get_customer_by_id(customer_id: str) -> Optional[Dict]:
    """Get customer by ID."""
    conn = await get_db()
    row = await conn.fetchrow(
        "SELECT * FROM customers WHERE id = $1",
        customer_id
    )
    return dict(row) if row else None


async def get_customer_history(customer_id: str, limit: int = 20) -> List[Dict]:
    """Get customer's conversation history."""
    conn = await get_db()
    rows = await conn.fetch(
        "SELECT * FROM get_customer_history($1, $2)",
        customer_id, limit
    )
    return [dict(row) for row in rows]


# =============================================================================
# Conversation Operations
# =============================================================================

async def get_active_conversation(customer_id: str, hours: int = 24) -> Optional[str]:
    """Get active conversation for customer."""
    conn = await get_db()
    return await conn.fetchval(
        "SELECT get_active_conversation($1, $2)",
        customer_id, hours
    )


async def create_conversation(customer_id: str, initial_channel: str) -> str:
    """Create new conversation."""
    conn = await get_db()
    return await conn.fetchval(
        "SELECT create_conversation($1, $2)",
        customer_id, initial_channel
    )


async def resolve_conversation(
    conversation_id: str,
    resolution_type: str,
    escalated_to: Optional[str] = None
) -> None:
    """Resolve conversation."""
    conn = await get_db()
    await conn.execute(
        "SELECT resolve_conversation($1, $2, $3)",
        conversation_id, resolution_type, escalated_to
    )


# =============================================================================
# Message Operations
# =============================================================================

async def add_message(
    conversation_id: str,
    channel: str,
    direction: str,
    role: str,
    content: str,
    sentiment_score: float = 0.5,
    topics: Optional[List[str]] = None,
    channel_message_id: Optional[str] = None,
    tool_calls: Optional[List[Dict]] = None,
    latency_ms: Optional[int] = None
) -> str:
    """Add message to conversation."""
    conn = await get_db()
    return await conn.fetchval(
        "SELECT add_message($1, $2, $3, $4, $5, $6, $7, $8)",
        conversation_id, channel, direction, role, content,
        sentiment_score, topics, channel_message_id
    )


async def get_conversation_messages(conversation_id: str, limit: int = 10) -> List[Dict]:
    """Get messages from conversation."""
    conn = await get_db()
    rows = await conn.fetch(
        """
        SELECT * FROM messages
        WHERE conversation_id = $1
        ORDER BY created_at DESC
        LIMIT $2
        """,
        conversation_id, limit
    )
    return [dict(row) for row in rows]


# =============================================================================
# Ticket Operations
# =============================================================================

async def create_ticket(
    customer_id: str,
    conversation_id: str,
    source_channel: str,
    category: str,
    priority: str,
    subject: str = "",
    issue: str = ""
) -> str:
    """Create support ticket."""
    conn = await get_db()
    return await conn.fetchval(
        """
        INSERT INTO tickets (customer_id, conversation_id, source_channel, 
                            category, priority, subject, issue, status)
        VALUES ($1, $2, $3, $4, $5, $6, $7, 'open')
        RETURNING id
        """,
        customer_id, conversation_id, source_channel, category, priority,
        subject, issue
    )


async def get_ticket(ticket_id: str) -> Optional[Dict]:
    """Get ticket by ID."""
    conn = await get_db()
    row = await conn.fetchrow(
        "SELECT * FROM tickets WHERE id = $1",
        ticket_id
    )
    return dict(row) if row else None


async def update_ticket_status(ticket_id: str, status: str) -> None:
    """Update ticket status."""
    conn = await get_db()
    await conn.execute(
        "UPDATE tickets SET status = $1 WHERE id = $2",
        status, ticket_id
    )


async def escalate_ticket(
    ticket_id: str,
    reason: str,
    urgency: str = "normal",
    additional_context: Optional[str] = None
) -> str:
    """Escalate ticket and return escalation ID."""
    conn = await get_db()
    async with conn._pool.acquire() as ac:
        # Update ticket
        await ac.execute(
            """
            UPDATE tickets
            SET status = 'escalated',
                escalated_to = CASE
                    WHEN $1 = 'legal_inquiry' THEN 'legal_team'
                    WHEN $1 IN ('pricing_inquiry', 'refund_request') THEN 'billing_team'
                    WHEN $1 = 'negative_sentiment' THEN 'senior_support'
                    WHEN $1 = 'critical_incident' THEN 'emergency_response'
                    ELSE 'general_support'
                END
            WHERE id = $2
            """,
            reason, ticket_id
        )

        # Create escalation record
        escalation_id = await ac.fetchval(
            """
            INSERT INTO escalations (ticket_id, reason, urgency, additional_context)
            VALUES ($1, $2, $3, $4)
            RETURNING id
            """,
            ticket_id, reason, urgency, additional_context
        )

        return escalation_id


# =============================================================================
# Knowledge Base Operations
# =============================================================================

async def search_knowledge_base(
    query: str,
    max_results: int = 5,
    category: Optional[str] = None
) -> List[Dict]:
    """Search knowledge base with semantic search."""
    conn = await get_db()

    # First try semantic search with embeddings
    if category:
        rows = await conn.fetch(
            """
            SELECT id, title, content, category,
                   1 - (embedding <=> $1::vector) as similarity
            FROM knowledge_base
            WHERE category = $2
            ORDER BY embedding <=> $1::vector
            LIMIT $3
            """,
            query, category, max_results
        )
    else:
        rows = await conn.fetch(
            """
            SELECT id, title, content, category,
                   1 - (embedding <=> $1::vector) as similarity
            FROM knowledge_base
            ORDER BY embedding <=> $1::vector
            LIMIT $2
            """,
            query, max_results
        )

    # If no semantic results, fall back to full-text search
    if not rows:
        if category:
            rows = await conn.fetch(
                """
                SELECT id, title, content, category,
                       ts_rank(to_tsvector('english', content), query) as similarity
                FROM knowledge_base, to_tsquery('english', $1) query
                WHERE category = $2
                  AND to_tsvector('english', content) @@ query
                ORDER BY similarity DESC
                LIMIT $3
                """,
                query, category, max_results
            )
        else:
            rows = await conn.fetch(
                """
                SELECT id, title, content, category,
                       ts_rank(to_tsvector('english', content), query) as similarity
                FROM knowledge_base, to_tsquery('english', $1) query
                WHERE to_tsvector('english', content) @@ query
                ORDER BY similarity DESC
                LIMIT $2
                """,
                query, max_results
            )

    return [dict(row) for row in rows]


async def add_knowledge_entry(
    title: str,
    content: str,
    category: str,
    tags: Optional[List[str]] = None,
    embedding: Optional[List[float]] = None
) -> str:
    """Add knowledge base entry."""
    conn = await get_db()
    return await conn.fetchval(
        """
        INSERT INTO knowledge_base (title, content, category, tags, embedding)
        VALUES ($1, $2, $3, $4, $5)
        RETURNING id
        """,
        title, content, category, tags, embedding
    )


# =============================================================================
# Metrics Operations
# =============================================================================

async def record_metric(
    metric_name: str,
    metric_value: float,
    channel: Optional[str] = None,
    dimensions: Optional[Dict] = None
) -> None:
    """Record agent metric."""
    conn = await get_db()
    await conn.execute(
        """
        INSERT INTO agent_metrics (metric_name, metric_value, channel, dimensions)
        VALUES ($1, $2, $3, $4)
        """,
        metric_name, metric_value, channel, json.dumps(dimensions) if dimensions else None
    )


async def get_channel_metrics(hours: int = 24) -> List[Dict]:
    """Get metrics by channel."""
    conn = await get_db()
    rows = await conn.fetch(
        """
        SELECT * FROM channel_metrics
        """
    )
    return [dict(row) for row in rows]


# =============================================================================
# Helper Functions
# =============================================================================

async def generate_embedding(text: str) -> List[float]:
    """
    Generate embedding for text using OpenAI.
    In production, cache embeddings to avoid regenerating.
    """
    import openai

    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        # Return zero vector if no API key (for development)
        return [0.0] * 1536

    client = openai.AsyncOpenAI(api_key=api_key)
    response = await client.embeddings.create(
        model="text-embedding-ada-002",
        input=text
    )
    return response.data[0].data
