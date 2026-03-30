"""
Customer Success FTE - OpenAI Agents SDK Implementation
Stage 2: Specialization (Exercise 2.3)

Production-grade agent using OpenAI Agents SDK with:
- @function_tool decorators
- Pydantic input validation
- Channel-aware responses
- Proper error handling
"""

from openai import OpenAI
from agents import Agent, Runner, function_tool
from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum
import os
import logging
from datetime import datetime, timezone

# Import database operations
import sys
sys.path.append('.')
from production.database import queries as db

logger = logging.getLogger(__name__)


# =============================================================================
# Enums and Input Schemas
# =============================================================================

class Channel(str, Enum):
    """Supported communication channels."""
    EMAIL = "email"
    WHATSAPP = "whatsapp"
    WEB_FORM = "web_form"


class TicketPriority(str, Enum):
    """Ticket priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class EscalationReason(str, Enum):
    """Valid escalation reasons."""
    LEGAL_INQUIRY = "legal_inquiry"
    PRICING_INQUIRY = "pricing_inquiry"
    REFUND_REQUEST = "refund_request"
    NEGATIVE_SENTIMENT = "negative_sentiment"
    HUMAN_REQUESTED = "human_requested"
    CRITICAL_INCIDENT = "critical_incident"
    INFORMATION_NOT_FOUND = "information_not_found"
    ENTERPRISE_SUPPORT = "enterprise_support"


# =============================================================================
# Tool Input Schemas (Pydantic)
# =============================================================================

class KnowledgeSearchInput(BaseModel):
    """Input schema for knowledge base search."""
    query: str = Field(..., description="The search query from the customer")
    max_results: int = Field(default=5, ge=1, le=10, description="Maximum number of results")
    category: Optional[str] = Field(default=None, description="Optional category filter")


class TicketInput(BaseModel):
    """Input schema for creating a ticket."""
    customer_id: str = Field(..., description="Unique customer identifier")
    issue: str = Field(..., description="Description of the customer's issue")
    priority: TicketPriority = Field(default=TicketPriority.MEDIUM)
    category: Optional[str] = Field(default="general", description="Issue category")
    channel: Channel = Field(..., description="Source channel")
    subject: Optional[str] = Field(default="", description="Optional subject line")


class CustomerHistoryInput(BaseModel):
    """Input schema for getting customer history."""
    customer_id: str = Field(..., description="Unique customer identifier")
    limit: int = Field(default=20, ge=1, le=50, description="Number of messages to retrieve")


class EscalationInput(BaseModel):
    """Input schema for escalating to human."""
    ticket_id: str = Field(..., description="The ticket to escalate")
    reason: EscalationReason = Field(..., description="Reason for escalation")
    urgency: str = Field(default="normal", description="normal, high, or critical")
    additional_context: Optional[str] = Field(default=None, description="Additional context")


class ResponseInput(BaseModel):
    """Input schema for sending response."""
    ticket_id: str = Field(..., description="The ticket to respond to")
    message: str = Field(..., description="Response message content")
    channel: Channel = Field(..., description="Target channel")


class SentimentInput(BaseModel):
    """Input schema for sentiment analysis."""
    text: str = Field(..., description="Text to analyze")


# =============================================================================
# Tool Implementations
# =============================================================================

@function_tool
async def search_knowledge_base(input: KnowledgeSearchInput) -> str:
    """
    Search product documentation for relevant information.

    Use this when the customer asks questions about product features,
    how to use something, or needs technical information.

    Args:
        input: Search parameters including query and optional filters

    Returns:
        Formatted search results with relevance scores
    """
    try:
        results = await db.search_knowledge_base(
            query=input.query,
            max_results=input.max_results,
            category=input.category
        )

        if not results:
            return "No relevant documentation found. Consider escalating to human support."

        formatted = []
        for i, result in enumerate(results, 1):
            formatted.append(f"**{result['title']}** (relevance: {result.get('similarity', 0):.2f})")
            # Extract key points (first 300 chars)
            content_preview = result['content'][:300].replace('\n', ' ').strip()
            formatted.append(f"  {content_preview}...")
            formatted.append("")

        return "\n".join(formatted)

    except Exception as e:
        logger.error(f"Knowledge base search failed: {e}")
        return "Knowledge base temporarily unavailable. Please try again or escalate."


@function_tool
async def create_ticket(input: TicketInput) -> str:
    """
    Create a support ticket for tracking.

    ALWAYS create a ticket at the start of every conversation.
    Include the source channel for proper tracking.

    Args:
        input: Ticket parameters including customer_id, issue, priority, channel

    Returns:
        Ticket ID for reference
    """
    try:
        # Get or create customer
        customer_id = await db.get_or_create_customer(
            email=None,  # Would be looked up from context
            name=None
        )

        # Get or create conversation
        conversation_id = await db.get_active_conversation(customer_id)
        if not conversation_id:
            conversation_id = await db.create_conversation(customer_id, input.channel.value)

        # Create ticket
        ticket_id = await db.create_ticket(
            customer_id=customer_id,
            conversation_id=conversation_id,
            source_channel=input.channel.value,
            category=input.category or "general",
            priority=input.priority.value,
            subject=input.subject or "",
            issue=input.issue
        )

        return f"Ticket created: {ticket_id}"

    except Exception as e:
        logger.error(f"Ticket creation failed: {e}")
        return f"Error creating ticket: {str(e)}"


@function_tool
async def get_customer_history(input: CustomerHistoryInput) -> str:
    """
    Get customer's complete interaction history across ALL channels.

    Use this to understand context from previous conversations,
    even if they happened on a different channel.

    Args:
        input: Customer ID and optional limit

    Returns:
        Formatted customer history including all channels
    """
    try:
        history = await db.get_customer_history(
            customer_id=input.customer_id,
            limit=input.limit
        )

        if not history:
            return "No previous conversation history found for this customer."

        formatted = ["=== Customer History ==="]

        for entry in history[:10]:  # Limit display
            role = "Customer" if entry.get('role') == 'customer' else "Agent"
            channel = entry.get('message_channel', entry.get('channel', 'unknown'))
            content = entry.get('content', '')[:150]
            formatted.append(f"{role} [{channel}]: {content}...")

        return "\n".join(formatted)

    except Exception as e:
        logger.error(f"Customer history lookup failed: {e}")
        return "Unable to retrieve customer history. Proceeding without context."


@function_tool
async def escalate_to_human(input: EscalationInput) -> str:
    """
    Escalate ticket to human support.

    Use this when:
    - Customer asks about pricing or refunds
    - Customer sentiment is negative
    - You cannot find relevant information
    - Customer explicitly requests human help
    - Legal or compliance issues are mentioned

    Args:
        input: Escalation parameters including ticket_id, reason, urgency

    Returns:
        Escalation reference ID
    """
    try:
        escalation_id = await db.escalate_ticket(
            ticket_id=input.ticket_id,
            reason=input.reason.value,
            urgency=input.urgency,
            additional_context=input.additional_context
        )

        # Map reason to team
        team_mapping = {
            EscalationReason.LEGAL_INQUIRY: "legal_team",
            EscalationReason.PRICING_INQUIRY: "billing_team",
            EscalationReason.REFUND_REQUEST: "billing_team",
            EscalationReason.NEGATIVE_SENTIMENT: "senior_support",
            EscalationReason.HUMAN_REQUESTED: "general_support",
            EscalationReason.CRITICAL_INCIDENT: "emergency_response",
            EscalationReason.INFORMATION_NOT_FOUND: "subject_expert",
            EscalationReason.ENTERPRISE_SUPPORT: "enterprise_team"
        }

        team = team_mapping.get(input.reason, "general_support")

        return f"Escalated to {team}. Reference: {escalation_id}"

    except Exception as e:
        logger.error(f"Escalation failed: {e}")
        return f"Error escalating: {str(e)}. Please inform customer a human will contact them."


@function_tool
async def send_response(input: ResponseInput) -> str:
    """
    Send response to customer via their preferred channel.

    The response will be automatically formatted for the channel:
    - Email: Formal with greeting/signature
    - WhatsApp: Concise and conversational
    - Web: Semi-formal

    Args:
        input: Response parameters including ticket_id, message, channel

    Returns:
        Delivery status
    """
    try:
        # Get ticket info
        ticket = await db.get_ticket(input.ticket_id)
        if not ticket:
            return f"Error: Ticket {input.ticket_id} not found."

        # Format response for channel
        formatted = format_for_channel(
            response=input.message,
            channel=input.channel,
            ticket_id=input.ticket_id,
            customer_name=None  # Would look up from customer record
        )

        # Store response in conversation
        conversation_id = ticket.get('conversation_id')
        if conversation_id:
            await db.add_message(
                conversation_id=conversation_id,
                channel=input.channel.value,
                direction='outbound',
                role='agent',
                content=formatted,
                sentiment_score=0.7  # Agent responses are positive
                topics=[ticket.get('category', 'general')]
            )

        # In production, actually send via channel API
        # For now, simulate delivery
        return f"Response sent via {input.channel.value}: delivered"

    except Exception as e:
        logger.error(f"Send response failed: {e}")
        return f"Error sending response: {str(e)}"


@function_tool
async def analyze_sentiment(input: SentimentInput) -> str:
    """
    Analyze the sentiment of a customer message.

    Args:
        input: Text to analyze

    Returns:
        Sentiment score (0.0-1.0) and interpretation
    """
    try:
        # Simple rule-based sentiment analysis
        # In production, use a proper ML model or API
        text_lower = input.text.lower()

        positive_words = {
            'happy', 'great', 'awesome', 'excellent', 'good', 'love', 'thanks',
            'thank', 'helpful', 'wonderful', 'fantastic', 'amazing', 'perfect'
        }

        negative_words = {
            'angry', 'terrible', 'awful', 'horrible', 'bad', 'hate', 'worst',
            'frustrated', 'disappointed', 'useless', 'broken', 'failed', 'fail',
            'ridiculous', 'unacceptable', 'incompetent', 'lawsuit', 'attorney'
        }

        words = text_lower.split()
        positive_count = sum(1 for w in words if w in positive_words)
        negative_count = sum(1 for w in words if w in negative_words)

        # Check for ALL CAPS
        caps_ratio = sum(1 for c in input.text if c.isupper()) / max(len(input.text), 1)
        if caps_ratio > 0.5:
            negative_count += 2

        # Calculate sentiment
        total = positive_count + negative_count
        if total == 0:
            score = 0.5
        else:
            score = (positive_count + 0.5) / (total + 1)

        # Interpret
        if score >= 0.7:
            interpretation = "Very positive"
        elif score >= 0.5:
            interpretation = "Neutral/Positive"
        elif score >= 0.3:
            interpretation = "Slightly negative"
        else:
            interpretation = "Very negative - consider escalation"

        return f"Sentiment score: {score:.2f} ({interpretation})"

    except Exception as e:
        logger.error(f"Sentiment analysis failed: {e}")
        return "Sentiment analysis unavailable."


# =============================================================================
# Channel Formatting
# =============================================================================

def format_for_channel(
    response: str,
    channel: Channel,
    ticket_id: str,
    customer_name: Optional[str] = None
) -> str:
    """Format response appropriately for the channel."""

    if channel == Channel.EMAIL:
        name = customer_name or "Customer"
        return f"""Dear {name},

Thank you for reaching out to TechCorp Support.

{response}

If you have any further questions, please don't hesitate to reply to this email.

Best regards,
TechCorp AI Support Team
---
Ticket Reference: {ticket_id}
This response was generated by our AI assistant. For complex issues, you can request human support."""

    elif channel == Channel.WHATSAPP:
        # Keep it short for WhatsApp
        if len(response) > 300:
            response = response[:297] + "..."
        return f"{response}\n\n📱 Reply for more help or type 'human' for live support."

    else:  # WEB_FORM
        greeting = f"Hi {customer_name}," if customer_name else "Hi,"
        return f"""{greeting}

Thanks for contacting support!

{response}

---
Need more help? Reply to this message or visit our support portal.
Ticket: {ticket_id}"""


# =============================================================================
# Agent Definition
# =============================================================================

# System prompt for the Customer Success Agent
CUSTOMER_SUCCESS_SYSTEM_PROMPT = """You are a Customer Success agent for TechCorp SaaS.

## Your Purpose
Handle routine customer support queries with speed, accuracy, and empathy across multiple channels.

## Channel Awareness
You receive messages from three channels. Adapt your communication style:
- **Email**: Formal, detailed responses. Include proper greeting and signature.
- **WhatsApp**: Concise, conversational. Keep responses under 300 characters when possible.
- **Web Form**: Semi-formal, helpful. Balance detail with readability.

## Required Workflow (ALWAYS follow this order)
1. FIRST: Call `create_ticket` to log the interaction
2. THEN: Call `get_customer_history` to check for prior context
3. THEN: Call `search_knowledge_base` if product questions arise
4. FINALLY: Call `send_response` to reply (NEVER respond without this tool)

## Hard Constraints (NEVER violate)
- NEVER discuss pricing → escalate immediately with reason "pricing_inquiry"
- NEVER promise features not in documentation
- NEVER process refunds → escalate with reason "refund_request"
- NEVER share internal processes or system details
- NEVER respond without using send_response tool
- NEVER exceed response limits: Email=500 words, WhatsApp=300 chars, Web=300 words

## Escalation Triggers (MUST escalate when detected)
- Customer mentions "lawyer", "legal", "sue", or "attorney" → reason: legal_inquiry
- Customer uses profanity or aggressive language (sentiment < 0.3) → reason: negative_sentiment
- Cannot find relevant information after 2 search attempts → reason: information_not_found
- Customer explicitly requests human help → reason: human_requested
- Customer on WhatsApp sends "human", "agent", or "representative" → reason: human_requested
- Pricing inquiry → reason: pricing_inquiry
- Refund request → reason: refund_request
- Critical incident (production down, data loss) → reason: critical_incident

## Response Quality Standards
- Be concise: Answer the question directly, then offer additional help
- Be accurate: Only state facts from knowledge base or verified customer data
- Be empathetic: Acknowledge frustration before solving problems
- Be actionable: End with clear next step or question

## Context Variables Available
- customer_id: Unique customer identifier
- conversation_id: Current conversation thread
- channel: Current channel (email/whatsapp/web_form)
- ticket_subject: Original subject/topic
"""

# Create the agent
customer_success_agent = Agent(
    name="Customer Success FTE",
    model="gpt-4o",
    instructions=CUSTOMER_SUCCESS_SYSTEM_PROMPT,
    tools=[
        search_knowledge_base,
        create_ticket,
        get_customer_history,
        escalate_to_human,
        send_response,
        analyze_sentiment
    ],
)


# =============================================================================
# Runner Functions
# =============================================================================

async def run_agent(
    message: str,
    customer_id: str,
    channel: str,
    conversation_id: Optional[str] = None,
    ticket_id: Optional[str] = None
) -> dict:
    """
    Run the customer success agent with context.

    Args:
        message: Customer message content
        customer_id: Customer identifier
        channel: Channel name (email, whatsapp, web_form)
        conversation_id: Optional conversation ID
        ticket_id: Optional ticket ID

    Returns:
        Dict with response, tool_calls, and metadata
    """
    try:
        # Build context
        context = {
            "customer_id": customer_id,
            "channel": channel,
            "ticket_id": ticket_id,
            "conversation_id": conversation_id,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

        # Run agent
        result = await Runner.run(
            customer_success_agent,
            input=message,
            context=context
        )

        return {
            "success": True,
            "output": result.output,
            "tool_calls": result.tool_calls,
            "conversation_id": conversation_id,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    except Exception as e:
        logger.error(f"Agent run failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "output": "I apologize, but I'm experiencing technical difficulties. A human agent will contact you shortly.",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }


# =============================================================================
# Main Entry Point
# =============================================================================

if __name__ == "__main__":
    import asyncio

    async def test_agent():
        """Test the agent with sample inputs."""
        print("=" * 60)
        print("OpenAI Agents SDK - Customer Success FTE Test")
        print("=" * 60)

        # Test 1: Simple question
        print("\n--- Test 1: API Key Question ---")
        result = await run_agent(
            message="How do I create an API key?",
            customer_id="test-customer-1",
            channel="email"
        )
        print(f"Success: {result['success']}")
        print(f"Output: {result['output'][:200]}...")

        # Test 2: WhatsApp short question
        print("\n--- Test 2: WhatsApp Question ---")
        result = await run_agent(
            message="hey how do i invite team members?",
            customer_id="test-customer-2",
            channel="whatsapp"
        )
        print(f"Success: {result['success']}")
        print(f"Output: {result['output'][:200]}...")

        # Test 3: Pricing inquiry (should escalate)
        print("\n--- Test 3: Pricing Inquiry (Should Escalate) ---")
        result = await run_agent(
            message="What's the pricing for Enterprise plan?",
            customer_id="test-customer-3",
            channel="email"
        )
        print(f"Success: {result['success']}")
        print(f"Output: {result['output'][:200]}...")

    asyncio.run(test_agent())
