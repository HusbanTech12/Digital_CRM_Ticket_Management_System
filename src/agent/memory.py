"""
Customer Success FTE - Memory and State Management
Stage 1: Incubation (Exercise 1.3)

This module adds conversation memory and state tracking:
- Remember context across a conversation
- Track customer sentiment over time
- Track topics discussed
- Track resolution status
- Track original channel and channel switches
- Customer identification (email as primary key)
"""

import json
import uuid
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
import os


class ConversationStatus(str, Enum):
    ACTIVE = "active"
    PENDING = "pending"
    RESOLVED = "resolved"
    ESCALATED = "escalated"
    CLOSED = "closed"


class ResolutionType(str, Enum):
    AI_RESOLVED = "ai_resolved"
    HUMAN_ESCALATED = "human_escalated"
    CUSTOMER_ABANDONED = "customer_abandoned"
    AUTO_CLOSED = "auto_closed"


@dataclass
class Message:
    """A single message in a conversation."""
    id: str
    conversation_id: str
    channel: str
    direction: str  # 'inbound' or 'outbound'
    role: str  # 'customer', 'agent', 'system'
    content: str
    created_at: str
    sentiment_score: float = 0.5
    topics: List[str] = field(default_factory=list)
    tool_calls: List[Dict] = field(default_factory=list)
    latency_ms: int = 0
    channel_message_id: Optional[str] = None
    delivery_status: str = "pending"


@dataclass
class Conversation:
    """A conversation thread with a customer."""
    id: str
    customer_id: str
    initial_channel: str
    started_at: str
    ended_at: Optional[str] = None
    status: str = ConversationStatus.ACTIVE
    sentiment_score: float = 0.5
    sentiment_trend: List[float] = field(default_factory=list)
    topics: List[str] = field(default_factory=list)
    resolution_type: Optional[str] = None
    escalated_to: Optional[str] = None
    messages: List[Message] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)

    def add_message(self, message: Message):
        """Add a message to the conversation."""
        self.messages.append(message)
        # Update topics
        for topic in message.topics:
            if topic not in self.topics:
                self.topics.append(topic)
        # Update sentiment trend
        self.sentiment_trend.append(message.sentiment_score)
        # Calculate average sentiment
        self.sentiment_score = sum(self.sentiment_trend) / len(self.sentiment_trend)

    def get_recent_messages(self, limit: int = 10) -> List[Message]:
        """Get most recent messages."""
        return self.messages[-limit:]

    def get_context_summary(self) -> str:
        """Generate a summary of conversation context."""
        if not self.messages:
            return "New conversation"

        summary_parts = [
            f"Conversation started: {self.started_at}",
            f"Initial channel: {self.initial_channel}",
            f"Topics discussed: {', '.join(self.topics)}",
            f"Average sentiment: {self.sentiment_score:.2f}",
            f"Message count: {len(self.messages)}"
        ]

        # Add recent context
        recent = self.get_recent_messages(3)
        if recent:
            summary_parts.append("\nRecent exchange:")
            for msg in recent:
                sender = "Customer" if msg.role == "customer" else "Agent"
                summary_parts.append(f"  {sender}: {msg.content[:100]}...")

        return "\n".join(summary_parts)


@dataclass
class Customer:
    """A customer with unified identity across channels."""
    id: str
    email: Optional[str] = None
    phone: Optional[str] = None
    name: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    conversations: List[str] = field(default_factory=list)  # Conversation IDs
    total_tickets: int = 0
    resolved_tickets: int = 0
    escalated_tickets: int = 0
    average_sentiment: float = 0.5
    preferred_channel: str = "email"
    metadata: Dict = field(default_factory=dict)

    def add_conversation(self, conversation_id: str):
        """Track a new conversation."""
        if conversation_id not in self.conversations:
            self.conversations.append(conversation_id)
            self.total_tickets += 1

    def get_history_summary(self) -> str:
        """Get summary of customer history."""
        return (
            f"Customer: {self.name or self.email or self.phone}\n"
            f"Total conversations: {len(self.conversations)}\n"
            f"Resolved: {self.resolved_tickets}\n"
            f"Escalated: {self.escalated_tickets}\n"
            f"Average sentiment: {self.average_sentiment:.2f}\n"
            f"Preferred channel: {self.preferred_channel}"
        )


class MemoryStore:
    """
    In-memory store for conversations and customers.
    In production, this will be replaced with PostgreSQL.
    """

    def __init__(self):
        self.customers: Dict[str, Customer] = {}
        self.conversations: Dict[str, Conversation] = {}
        self.messages: Dict[str, Message] = {}
        self.email_to_customer: Dict[str, str] = {}
        self.phone_to_customer: Dict[str, str] = {}

    def get_or_create_customer_by_email(self, email: str) -> Customer:
        """Get existing customer or create new one by email."""
        email_lower = email.lower()
        if email_lower in self.email_to_customer:
            return self.customers[self.email_to_customer[email_lower]]

        # Create new customer
        customer_id = str(uuid.uuid4())
        customer = Customer(id=customer_id, email=email_lower)
        self.customers[customer_id] = customer
        self.email_to_customer[email_lower] = customer_id
        return customer

    def get_or_create_customer_by_phone(self, phone: str) -> Customer:
        """Get existing customer or create new one by phone."""
        # Normalize phone number
        phone_normalized = ''.join(c for c in phone if c.isdigit() or c == '+')

        if phone_normalized in self.phone_to_customer:
            return self.customers[self.phone_to_customer[phone_normalized]]

        # Create new customer
        customer_id = str(uuid.uuid4())
        customer = Customer(id=customer_id, phone=phone_normalized)
        self.customers[customer_id] = customer
        self.phone_to_customer[phone_normalized] = customer_id
        return customer

    def get_or_create_customer(self, email: Optional[str] = None,
                                phone: Optional[str] = None,
                                name: Optional[str] = None) -> Customer:
        """
        Get or create customer by email or phone.
        If customer exists, merge any new information.
        """
        # Try email first
        if email:
            customer = self.get_or_create_customer_by_email(email)
            if name and not customer.name:
                customer.name = name
            return customer

        # Try phone
        if phone:
            customer = self.get_or_create_customer_by_phone(phone)
            if name and not customer.name:
                customer.name = name
            return customer

        # Create anonymous customer
        customer_id = str(uuid.uuid4())
        customer = Customer(id=customer_id, name=name)
        self.customers[customer_id] = customer
        return customer

    def create_conversation(self, customer_id: str, initial_channel: str) -> Conversation:
        """Create a new conversation."""
        conversation_id = str(uuid.uuid4())
        conversation = Conversation(
            id=conversation_id,
            customer_id=customer_id,
            initial_channel=initial_channel,
            started_at=datetime.now(timezone.utc).isoformat()
        )
        self.conversations[conversation_id] = conversation

        # Link to customer
        if customer_id in self.customers:
            self.customers[customer_id].add_conversation(conversation_id)

        return conversation

    def get_active_conversation(self, customer_id: str,
                                hours: int = 24) -> Optional[Conversation]:
        """Get active conversation for customer (within last N hours)."""
        cutoff = datetime.now(timezone.utc).timestamp() - (hours * 3600)

        for conv in self.conversations.values():
            if conv.customer_id == customer_id and conv.status == ConversationStatus.ACTIVE:
                conv_time = datetime.fromisoformat(conv.started_at.replace('Z', '+00:00')).timestamp()
                if conv_time > cutoff:
                    return conv

        return None

    def get_conversation_history(self, customer_id: str,
                                  limit: int = 20) -> List[Message]:
        """Get customer's message history across all conversations."""
        all_messages = []

        for conv in self.conversations.values():
            if conv.customer_id == customer_id:
                all_messages.extend(conv.messages)

        # Sort by created_at
        all_messages.sort(key=lambda m: m.created_at, reverse=True)
        return all_messages[:limit]

    def add_message(self, conversation_id: str, channel: str, direction: str,
                    role: str, content: str, sentiment_score: float = 0.5,
                    topics: Optional[List[str]] = None,
                    channel_message_id: Optional[str] = None) -> Message:
        """Add a message to a conversation."""
        message_id = str(uuid.uuid4())
        message = Message(
            id=message_id,
            conversation_id=conversation_id,
            channel=channel,
            direction=direction,
            role=role,
            content=content,
            created_at=datetime.now(timezone.utc).isoformat(),
            sentiment_score=sentiment_score,
            topics=topics or [],
            channel_message_id=channel_message_id
        )

        self.messages[message_id] = message

        if conversation_id in self.conversations:
            self.conversations[conversation_id].add_message(message)

        return message

    def resolve_conversation(self, conversation_id: str,
                             resolution_type: ResolutionType,
                             escalated_to: Optional[str] = None):
        """Mark a conversation as resolved."""
        if conversation_id not in self.conversations:
            return

        conv = self.conversations[conversation_id]
        conv.status = ConversationStatus.RESOLVED
        conv.ended_at = datetime.now(timezone.utc).isoformat()
        conv.resolution_type = resolution_type.value
        conv.escalated_to = escalated_to

        # Update customer stats
        if conv.customer_id in self.customers:
            customer = self.customers[conv.customer_id]
            if resolution_type == ResolutionType.AI_RESOLVED:
                customer.resolved_tickets += 1
            elif resolution_type == ResolutionType.HUMAN_ESCALATED:
                customer.escalated_tickets += 1

    def escalate_conversation(self, conversation_id: str, escalated_to: str):
        """Mark a conversation as escalated."""
        if conversation_id not in self.conversations:
            return

        conv = self.conversations[conversation_id]
        conv.status = ConversationStatus.ESCALATED
        conv.escalated_to = escalated_to

        # Update customer stats
        if conv.customer_id in self.customers:
            self.customers[conv.customer_id].escalated_tickets += 1

    def get_customer_history_across_channels(self, customer_id: str) -> str:
        """Get formatted customer history across all channels."""
        if customer_id not in self.customers:
            return "Customer not found"

        customer = self.customers[customer_id]
        history = []

        history.append(f"=== Customer History ===")
        history.append(f"Name: {customer.name or 'N/A'}")
        history.append(f"Email: {customer.email or 'N/A'}")
        history.append(f"Phone: {customer.phone or 'N/A'}")
        history.append(f"Total conversations: {len(customer.conversations)}")
        history.append(f"Resolved: {customer.resolved_tickets}")
        history.append(f"Escalated: {customer.escalated_tickets}")
        history.append("")

        # Show recent conversations
        history.append("=== Recent Conversations ===")
        for conv_id in customer.conversations[-5:]:  # Last 5 conversations
            if conv_id in self.conversations:
                conv = self.conversations[conv_id]
                history.append(f"\nConversation: {conv.id[:8]}...")
                history.append(f"  Channel: {conv.initial_channel}")
                history.append(f"  Status: {conv.status}")
                history.append(f"  Topics: {', '.join(conv.topics)}")
                history.append(f"  Sentiment: {conv.sentiment_score:.2f}")

        return "\n".join(history)


class ConversationManager:
    """
    High-level conversation manager that uses MemoryStore.
    This is the main interface for the agent to interact with memory.
    """

    def __init__(self, store: Optional[MemoryStore] = None):
        self.store = store or MemoryStore()

    def process_incoming_message(self, channel: str, content: str,
                                  email: Optional[str] = None,
                                  phone: Optional[str] = None,
                                  name: Optional[str] = None,
                                  subject: str = "",
                                  channel_message_id: Optional[str] = None,
                                  sentiment_score: float = 0.5,
                                  topics: Optional[List[str]] = None) -> Dict:
        """
        Process an incoming message and return conversation context.

        Returns:
            Dict with:
            - customer_id
            - conversation_id
            - is_continuation (bool)
            - customer_history (str)
            - conversation_context (str)
        """
        # Get or create customer
        customer = self.store.get_or_create_customer(
            email=email, phone=phone, name=name
        )

        # Check for active conversation
        conversation = self.store.get_active_conversation(customer.id)
        is_continuation = conversation is not None

        if not conversation:
            # Create new conversation
            conversation = self.store.create_conversation(
                customer_id=customer.id,
                initial_channel=channel
            )

        # Store incoming message
        self.store.add_message(
            conversation_id=conversation.id,
            channel=channel,
            direction="inbound",
            role="customer",
            content=content,
            sentiment_score=sentiment_score,
            topics=topics,
            channel_message_id=channel_message_id
        )

        # Get conversation history for agent context
        history_messages = self.store.get_conversation_history(customer.id, limit=10)
        conversation_context = self._format_history_for_agent(history_messages)

        # Get full customer history
        customer_history = self.store.get_customer_history_across_channels(customer.id)

        return {
            "customer_id": customer.id,
            "conversation_id": conversation.id,
            "is_continuation": is_continuation,
            "customer_name": customer.name,
            "customer_email": customer.email,
            "customer_phone": customer.phone,
            "customer_history": customer_history,
            "conversation_context": conversation_context,
            "total_messages": len(conversation.messages)
        }

    def store_agent_response(self, conversation_id: str, channel: str,
                             content: str, sentiment_score: float = 0.5,
                             topics: Optional[List[str]] = None,
                             tool_calls: Optional[List[Dict]] = None) -> Message:
        """Store agent response in conversation."""
        return self.store.add_message(
            conversation_id=conversation_id,
            channel=channel,
            direction="outbound",
            role="agent",
            content=content,
            sentiment_score=sentiment_score,
            topics=topics,
            tool_calls=tool_calls or []
        )

    def resolve_conversation(self, conversation_id: str,
                             resolution_type: ResolutionType,
                             escalated_to: Optional[str] = None):
        """Mark conversation as resolved."""
        self.store.resolve_conversation(
            conversation_id, resolution_type, escalated_to
        )

    def _format_history_for_agent(self, messages: List[Message]) -> str:
        """Format message history for agent context."""
        if not messages:
            return "No previous conversation history."

        formatted = []
        for msg in reversed(messages[-10:]):  # Last 10 messages
            sender = "Customer" if msg.role == "customer" else "Agent"
            channel = f"[{msg.channel}]"
            formatted.append(f"{sender} {channel}: {msg.content[:200]}")

        return "Conversation History:\n" + "\n".join(formatted)

    def detect_channel_switch(self, conversation: Conversation,
                              new_channel: str) -> bool:
        """Detect if customer switched channels."""
        return conversation.initial_channel != new_channel


# Convenience functions for testing
def create_test_memory() -> ConversationManager:
    """Create a conversation manager with test data."""
    manager = ConversationManager()

    # Add test customer
    customer = manager.store.get_or_create_customer(
        email="test@example.com",
        name="Test User"
    )

    # Add test conversation
    conversation = manager.store.create_conversation(
        customer_id=customer.id,
        initial_channel="email"
    )

    # Add some test messages
    manager.store.add_message(
        conversation_id=conversation.id,
        channel="email",
        direction="inbound",
        role="customer",
        content="How do I create an API key?",
        sentiment_score=0.7,
        topics=["authentication"]
    )

    manager.store.add_message(
        conversation_id=conversation.id,
        channel="email",
        direction="outbound",
        role="agent",
        content="To create an API key, go to Settings > API Keys...",
        sentiment_score=0.7,
        topics=["authentication"]
    )

    return manager


if __name__ == "__main__":
    print("=" * 60)
    print("MEMORY AND STATE MANAGEMENT - TEST")
    print("=" * 60)

    # Create test memory
    manager = create_test_memory()

    # Test 1: New message from existing customer (same channel)
    print("\n--- Test 1: Continuation on same channel ---")
    result = manager.process_incoming_message(
        channel="email",
        content="Thanks! And how do I use it in my code?",
        email="test@example.com",
        sentiment_score=0.8,
        topics=["authentication", "api"]
    )
    print(f"Customer ID: {result['customer_id'][:8]}...")
    print(f"Conversation ID: {result['conversation_id'][:8]}...")
    print(f"Is continuation: {result['is_continuation']}")
    print(f"Total messages: {result['total_messages']}")
    print(f"\nConversation Context:\n{result['conversation_context']}")

    # Test 2: Same customer, different channel (channel switch)
    print("\n--- Test 2: Channel switch (email -> whatsapp) ---")
    result2 = manager.process_incoming_message(
        channel="whatsapp",
        content="quick question about rate limits",
        email="test@example.com",
        sentiment_score=0.6,
        topics=["api"]
    )
    print(f"Customer ID: {result2['customer_id'][:8]}...")
    print(f"Same customer: {result2['customer_id'] == result['customer_id']}")
    print(f"Is continuation: {result2['is_continuation']}")
    print(f"Customer History:\n{result2['customer_history']}")

    # Test 3: New customer
    print("\n--- Test 3: New customer ---")
    result3 = manager.process_incoming_message(
        channel="web_form",
        content="Hello, I need help with billing",
        email="newuser@example.com",
        name="New User",
        sentiment_score=0.5,
        topics=["billing"]
    )
    print(f"Customer ID: {result3['customer_id'][:8]}...")
    print(f"Is new customer: {result3['customer_id'] != result['customer_id']}")
    print(f"Is continuation: {result3['is_continuation']}")

    # Test 4: Resolve conversation
    print("\n--- Test 4: Resolve conversation ---")
    manager.resolve_conversation(
        result['conversation_id'],
        ResolutionType.AI_RESOLVED
    )
    print(f"Conversation resolved successfully")

    # Test 5: Escalate conversation
    print("\n--- Test 5: Escalate conversation ---")
    manager.resolve_conversation(
        result2['conversation_id'],
        ResolutionType.HUMAN_ESCALATED,
        escalated_to="billing_team"
    )
    print(f"Conversation escalated successfully")

    # Final customer summary
    print("\n--- Final Customer Summary ---")
    customer = manager.store.customers[result['customer_id']]
    print(customer.get_history_summary())
