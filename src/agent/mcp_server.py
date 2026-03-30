"""
Customer Success FTE - MCP Server
Stage 1: Incubation (Exercise 1.4)

Model Context Protocol (MCP) server that exposes the agent's capabilities as tools:
- search_knowledge_base(query) -> relevant docs
- create_ticket(customer_id, issue, priority, channel) -> ticket_id
- get_customer_history(customer_id) -> past interactions across ALL channels
- escalate_to_human(ticket_id, reason) -> escalation_id
- send_response(ticket_id, message, channel) -> delivery_status
"""

import json
import asyncio
from typing import Dict, List, Optional
from enum import Enum
from dataclasses import dataclass
from datetime import datetime, timezone

# Import from our prototype modules
import sys
sys.path.append('.')

from src.agent.core_loop import (
    CustomerSuccessAgent, CustomerMessage, Channel,
    create_message_from_email, create_message_from_whatsapp,
    create_message_from_web_form
)
from src.agent.memory import (
    ConversationManager, MemoryStore, ResolutionType
)


class TicketStatus(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    PENDING = "pending"
    RESOLVED = "resolved"
    ESCALATED = "escalated"
    CLOSED = "closed"


class TicketPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class Ticket:
    """Support ticket representation."""
    id: str
    customer_id: str
    conversation_id: str
    channel: str
    category: str
    priority: str
    status: str
    subject: str
    issue: str
    created_at: str
    resolved_at: Optional[str] = None
    resolution_notes: Optional[str] = None
    escalated_to: Optional[str] = None


class MCPServer:
    """
    MCP Server exposing customer success agent tools.
    """

    def __init__(self, product_docs_path: str = "context/product-docs.md"):
        self.agent = CustomerSuccessAgent(product_docs_path)
        self.memory = ConversationManager()
        self.tickets: Dict[str, Ticket] = {}
        self.escalations: Dict[str, Dict] = {}
        self.ticket_counter = 0

    def _generate_ticket_id(self) -> str:
        """Generate unique ticket ID."""
        self.ticket_counter += 1
        return f"TKT-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{self.ticket_counter:04d}"

    def _generate_escalation_id(self) -> str:
        """Generate unique escalation ID."""
        import random
        return f"ESC-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}-{random.randint(1000, 9999)}"

    # =========================================================================
    # TOOL 1: search_knowledge_base
    # =========================================================================
    def search_knowledge_base(self, query: str, max_results: int = 5,
                              category: Optional[str] = None) -> str:
        """
        Search product documentation for relevant information.

        Use this when the customer asks questions about product features,
        how to use something, or needs technical information.

        Args:
            query: The search query from the customer
            max_results: Maximum number of results to return (default: 5)
            category: Optional category filter

        Returns:
            Formatted search results with relevance scores
        """
        results = self.agent.knowledge_base.search(query, max_results)

        if not results:
            return "No relevant documentation found. Consider escalating to human support."

        formatted = []
        for i, result in enumerate(results, 1):
            formatted.append(f"**{result['title']}** (relevance: {result['score']})")
            # Extract key points
            content_preview = result['content'][:300].replace('\n', ' ').strip()
            formatted.append(f"  {content_preview}...")
            formatted.append("")

        return "\n".join(formatted)

    # =========================================================================
    # TOOL 2: create_ticket
    # =========================================================================
    def create_ticket(self, customer_id: str, issue: str, priority: str,
                      channel: str, category: Optional[str] = None,
                      subject: str = "") -> str:
        """
        Create a support ticket for tracking.

        ALWAYS create a ticket at the start of every conversation.
        Include the source channel for proper tracking.

        Args:
            customer_id: Unique customer identifier
            issue: Description of the customer's issue
            priority: Ticket priority (low, medium, high, critical)
            channel: Source channel (email, whatsapp, web_form)
            category: Optional category (authentication, billing, cicd, etc.)
            subject: Optional subject line

        Returns:
            Ticket ID for reference
        """
        # Get or create conversation
        customer = self.memory.store.customers.get(customer_id)
        if not customer:
            return "Error: Customer not found. Please identify customer first."

        # Check for existing active conversation
        conversation = self.memory.store.get_active_conversation(customer_id)
        if not conversation:
            conversation = self.memory.store.create_conversation(
                customer_id=customer_id,
                initial_channel=channel
            )

        # Create ticket
        ticket_id = self._generate_ticket_id()
        ticket = Ticket(
            id=ticket_id,
            customer_id=customer_id,
            conversation_id=conversation.id,
            channel=channel,
            category=category or "general",
            priority=priority,
            status=TicketStatus.OPEN.value,
            subject=subject,
            issue=issue,
            created_at=datetime.now(timezone.utc).isoformat()
        )

        self.tickets[ticket_id] = ticket

        # Store initial message in conversation
        self.memory.store.add_message(
            conversation_id=conversation.id,
            channel=channel,
            direction="inbound",
            role="customer",
            content=issue,
            topics=[category] if category else []
        )

        return f"Ticket created: {ticket_id}"

    # =========================================================================
    # TOOL 3: get_customer_history
    # =========================================================================
    def get_customer_history(self, customer_id: str) -> str:
        """
        Get customer's complete interaction history across ALL channels.

        Use this to understand context from previous conversations,
        even if they happened on a different channel.

        Args:
            customer_id: Unique customer identifier

        Returns:
            Formatted customer history including all channels
        """
        if customer_id not in self.memory.store.customers:
            return "Customer not found."

        return self.memory.store.get_customer_history_across_channels(customer_id)

    # =========================================================================
    # TOOL 4: escalate_to_human
    # =========================================================================
    def escalate_to_human(self, ticket_id: str, reason: str,
                          urgency: str = "normal",
                          additional_context: Optional[str] = None) -> str:
        """
        Escalate ticket to human support.

        Use this when:
        - Customer asks about pricing or refunds
        - Customer sentiment is negative
        - You cannot find relevant information
        - Customer explicitly requests human help
        - Legal or compliance issues are mentioned

        Args:
            ticket_id: The ticket to escalate
            reason: Reason for escalation (pricing_inquiry, legal_inquiry,
                    negative_sentiment, human_requested, critical_incident)
            urgency: Urgency level (normal, high, critical)
            additional_context: Any additional context for the human agent

        Returns:
            Escalation reference ID
        """
        if ticket_id not in self.tickets:
            return f"Error: Ticket {ticket_id} not found."

        ticket = self.tickets[ticket_id]

        # Update ticket status
        ticket.status = TicketStatus.ESCALATED.value
        ticket.escalated_to = self._get_team_for_reason(reason)

        # Create escalation record
        escalation_id = self._generate_escalation_id()
        self.escalations[escalation_id] = {
            "ticket_id": ticket_id,
            "reason": reason,
            "urgency": urgency,
            "additional_context": additional_context,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "status": "pending",
            "assigned_to": ticket.escalated_to
        }

        # Update conversation in memory
        self.memory.resolve_conversation(
            ticket.conversation_id,
            ResolutionType.HUMAN_ESCALATED,
            escalated_to=ticket.escalated_to
        )

        return f"Escalated to human support. Reference: {escalation_id}. Team: {ticket.escalated_to}"

    def _get_team_for_reason(self, reason: str) -> str:
        """Get appropriate team for escalation reason."""
        team_mapping = {
            "legal_inquiry": "legal_team",
            "pricing_inquiry": "billing_team",
            "refund_request": "billing_team",
            "negative_sentiment": "senior_support",
            "human_requested": "general_support",
            "critical_incident": "emergency_response",
            "information_not_found": "subject_expert",
            "enterprise_support": "enterprise_team"
        }
        return team_mapping.get(reason, "general_support")

    # =========================================================================
    # TOOL 5: send_response
    # =========================================================================
    def send_response(self, ticket_id: str, message: str,
                      channel: str) -> str:
        """
        Send response to customer via their preferred channel.

        The response will be automatically formatted for the channel:
        - Email: Formal with greeting/signature
        - WhatsApp: Concise and conversational
        - Web: Semi-formal

        Args:
            ticket_id: The ticket to respond to
            message: The response message content
            channel: Target channel (email, whatsapp, web_form)

        Returns:
            Delivery status
        """
        if ticket_id not in self.tickets:
            return f"Error: Ticket {ticket_id} not found."

        ticket = self.tickets[ticket_id]

        # Format response for channel
        formatted = self.agent.formatter.format(
            response=message,
            channel=Channel(channel),
            ticket_id=ticket_id,
            customer_name=None  # Would look up from customer record
        )

        # Store response in conversation
        self.memory.store.add_message(
            conversation_id=ticket.conversation_id,
            channel=channel,
            direction="outbound",
            role="agent",
            content=formatted,
            topics=[ticket.category]
        )

        # In production, this would actually send via Gmail/Twilio API
        # For prototype, we just simulate delivery
        delivery_status = "sent"

        # Update ticket if this resolves it
        if ticket.status == TicketStatus.OPEN.value:
            ticket.status = TicketStatus.PENDING.value

        return f"Response sent via {channel}: {delivery_status}"

    # =========================================================================
    # TOOL 6: analyze_sentiment (Additional tool)
    # =========================================================================
    def analyze_sentiment(self, text: str) -> str:
        """
        Analyze the sentiment of a customer message.

        Args:
            text: The text to analyze

        Returns:
            Sentiment score (0.0-1.0) and interpretation
        """
        score = self.agent.sentiment_analyzer.analyze(text)

        if score >= 0.7:
            interpretation = "Very positive"
        elif score >= 0.5:
            interpretation = "Neutral/Positive"
        elif score >= 0.3:
            interpretation = "Slightly negative"
        else:
            interpretation = "Very negative - consider escalation"

        return f"Sentiment score: {score:.2f} ({interpretation})"

    # =========================================================================
    # TOOL 7: get_ticket_status (Additional tool)
    # =========================================================================
    def get_ticket_status(self, ticket_id: str) -> str:
        """
        Get the current status of a ticket.

        Args:
            ticket_id: The ticket ID to look up

        Returns:
            Formatted ticket status information
        """
        if ticket_id not in self.tickets:
            return f"Error: Ticket {ticket_id} not found."

        ticket = self.tickets[ticket_id]
        return (
            f"Ticket: {ticket.id}\n"
            f"Status: {ticket.status}\n"
            f"Priority: {ticket.priority}\n"
            f"Category: {ticket.category}\n"
            f"Channel: {ticket.channel}\n"
            f"Created: {ticket.created_at}\n"
            f"Escalated to: {ticket.escalated_to or 'N/A'}"
        )

    # =========================================================================
    # MCP Server Interface
    # =========================================================================
    def list_tools(self) -> List[Dict]:
        """List all available tools with their descriptions."""
        return [
            {
                "name": "search_knowledge_base",
                "description": "Search product documentation for relevant information. Use when customer asks product questions.",
                "parameters": {
                    "query": {"type": "string", "description": "Search query"},
                    "max_results": {"type": "integer", "description": "Max results (default: 5)"},
                    "category": {"type": "string", "description": "Optional category filter"}
                }
            },
            {
                "name": "create_ticket",
                "description": "Create a support ticket for tracking. ALWAYS create at conversation start.",
                "parameters": {
                    "customer_id": {"type": "string", "description": "Customer ID"},
                    "issue": {"type": "string", "description": "Issue description"},
                    "priority": {"type": "string", "description": "low, medium, high, critical"},
                    "channel": {"type": "string", "description": "email, whatsapp, web_form"},
                    "category": {"type": "string", "description": "Optional category"},
                    "subject": {"type": "string", "description": "Optional subject"}
                }
            },
            {
                "name": "get_customer_history",
                "description": "Get customer's complete interaction history across ALL channels.",
                "parameters": {
                    "customer_id": {"type": "string", "description": "Customer ID"}
                }
            },
            {
                "name": "escalate_to_human",
                "description": "Escalate ticket to human support. Use for pricing, legal, negative sentiment, or human requests.",
                "parameters": {
                    "ticket_id": {"type": "string", "description": "Ticket ID"},
                    "reason": {"type": "string", "description": "Reason for escalation"},
                    "urgency": {"type": "string", "description": "normal, high, critical"},
                    "additional_context": {"type": "string", "description": "Additional context"}
                }
            },
            {
                "name": "send_response",
                "description": "Send response to customer via their channel. Auto-formats for channel.",
                "parameters": {
                    "ticket_id": {"type": "string", "description": "Ticket ID"},
                    "message": {"type": "string", "description": "Response message"},
                    "channel": {"type": "string", "description": "email, whatsapp, web_form"}
                }
            },
            {
                "name": "analyze_sentiment",
                "description": "Analyze sentiment of customer message.",
                "parameters": {
                    "text": {"type": "string", "description": "Text to analyze"}
                }
            },
            {
                "name": "get_ticket_status",
                "description": "Get current status of a ticket.",
                "parameters": {
                    "ticket_id": {"type": "string", "description": "Ticket ID"}
                }
            }
        ]

    def call_tool(self, tool_name: str, **kwargs) -> str:
        """Call a tool by name with arguments."""
        if not hasattr(self, tool_name):
            return f"Error: Unknown tool '{tool_name}'"

        tool_method = getattr(self, tool_name)
        try:
            return tool_method(**kwargs)
        except TypeError as e:
            return f"Error: Invalid arguments - {str(e)}"
        except Exception as e:
            return f"Error: {str(e)}"


# Create global server instance
server = MCPServer()


def run_demo():
    """Run a demonstration of the MCP server."""
    print("=" * 70)
    print("MCP SERVER DEMO - Customer Success FTE Tools")
    print("=" * 70)

    # List available tools
    print("\n📋 Available Tools:")
    print("-" * 50)
    for tool in server.list_tools():
        print(f"  • {tool['name']}: {tool['description'][:60]}...")

    # Demo scenario 1: New customer inquiry
    print("\n" + "=" * 70)
    print("SCENARIO 1: New customer asks about API keys")
    print("=" * 70)

    # Step 1: Create customer in memory
    customer = server.memory.store.get_or_create_customer(
        email="developer@startup.io",
        name="Alex Developer"
    )
    print(f"\n1. Customer created: {customer.id[:8]}...")

    # Step 2: Create ticket
    ticket_result = server.create_ticket(
        customer_id=customer.id,
        issue="How do I create an API key for my application?",
        priority="medium",
        channel="email",
        category="authentication",
        subject="API Key Question"
    )
    print(f"2. {ticket_result}")
    ticket_id = ticket_result.split(": ")[1]

    # Step 3: Search knowledge base
    print("\n3. Searching knowledge base...")
    search_result = server.search_knowledge_base(
        query="how to create API key",
        max_results=2
    )
    print(search_result[:300] + "...")

    # Step 4: Get customer history
    print("\n4. Checking customer history...")
    history = server.get_customer_history(customer.id)
    print(history[:200] + "...")

    # Step 5: Send response
    print("\n5. Sending response...")
    response = """To create an API key:
1. Log in to your DevFlow dashboard
2. Navigate to Settings > API Keys
3. Click "Generate New Key"
4. Give your key a descriptive name
5. Copy the key immediately - it won't be shown again

Store your API key securely and use it in the Authorization header."""

    send_result = server.send_response(
        ticket_id=ticket_id,
        message=response,
        channel="email"
    )
    print(f"   {send_result}")

    # Demo scenario 2: Escalation
    print("\n" + "=" * 70)
    print("SCENARIO 2: Customer asks about enterprise pricing (ESCALATE)")
    print("=" * 70)

    # Create another customer
    customer2 = server.memory.store.get_or_create_customer(
        email="cto@enterprise.com",
        name="Sarah CTO"
    )

    # Create ticket
    ticket_result2 = server.create_ticket(
        customer_id=customer2.id,
        issue="We need custom pricing for 200 users on Enterprise plan",
        priority="high",
        channel="email",
        category="pricing",
        subject="Enterprise Pricing Inquiry"
    )
    print(f"\n1. {ticket_result2}")
    ticket_id2 = ticket_result2.split(": ")[1]

    # Detect pricing inquiry - should escalate
    print("\n2. Detected pricing inquiry - escalating to billing team...")
    escalation_result = server.escalate_to_human(
        ticket_id=ticket_id2,
        reason="pricing_inquiry",
        urgency="high",
        additional_context="Customer interested in Enterprise plan for 200 users"
    )
    print(f"   {escalation_result}")

    # Demo scenario 3: WhatsApp conversation
    print("\n" + "=" * 70)
    print("SCENARIO 3: WhatsApp - Quick question with channel-aware response")
    print("=" * 70)

    customer3 = server.memory.store.get_or_create_customer(
        phone="+14155551234"
    )

    ticket_result3 = server.create_ticket(
        customer_id=customer3.id,
        issue="how do i invite team members?",
        priority="low",
        channel="whatsapp",
        category="general"
    )
    print(f"\n1. {ticket_result3}")
    ticket_id3 = ticket_result3.split(": ")[1]

    # Search and send WhatsApp-formatted response
    print("\n2. Searching and sending WhatsApp-formatted response...")
    search_result3 = server.search_knowledge_base("invite team members", max_results=1)

    whatsapp_response = "Go to Project Settings > Members, click 'Invite Member', enter their email, and select their role! 👍"

    send_result3 = server.send_response(
        ticket_id=ticket_id3,
        message=whatsapp_response,
        channel="whatsapp"
    )
    print(f"   {send_result3}")

    # Demo scenario 4: Sentiment analysis
    print("\n" + "=" * 70)
    print("SCENARIO 4: Sentiment Analysis")
    print("=" * 70)

    test_messages = [
        "This is amazing! Best product ever!",
        "I need help with my account",
        "This is ridiculous! Your platform is broken!",
        "human agent please, this bot is useless"
    ]

    for msg in test_messages:
        sentiment = server.analyze_sentiment(msg)
        print(f"\n  Message: \"{msg[:40]}...\"")
        print(f"  {sentiment}")

    # Final summary
    print("\n" + "=" * 70)
    print("DEMO SUMMARY")
    print("=" * 70)
    print(f"Total tickets created: {len(server.tickets)}")
    print(f"Total escalations: {len(server.escalations)}")
    print(f"Customers in memory: {len(server.memory.store.customers)}")

    # Show ticket statuses
    print("\nTicket Statuses:")
    for tid, ticket in server.tickets.items():
        print(f"  {tid}: {ticket.status} (channel: {ticket.channel})")


if __name__ == "__main__":
    run_demo()
