"""
Customer Success FTE - Core Interaction Loop Prototype
Stage 1: Incubation (Exercise 1.2)

This prototype handles the basic customer interaction flow:
1. Takes a customer message as input (with channel metadata)
2. Normalizes the message regardless of source channel
3. Searches the product docs for relevant information
4. Generates a helpful response
5. Formats response appropriately for the channel
6. Decides if escalation is needed
"""

import json
import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timezone


class Channel(str, Enum):
    EMAIL = "email"
    WHATSAPP = "whatsapp"
    WEB_FORM = "web_form"


@dataclass
class CustomerMessage:
    """Normalized customer message regardless of source channel."""
    channel: Channel
    channel_message_id: str
    customer_email: Optional[str] = None
    customer_phone: Optional[str] = None
    customer_name: Optional[str] = None
    subject: str = ""
    content: str = ""
    received_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    metadata: Dict = field(default_factory=dict)


@dataclass
class AgentResponse:
    """Agent response with channel formatting and escalation decision."""
    ticket_id: str
    response_text: str
    formatted_response: str
    should_escalate: bool
    escalation_reason: Optional[str] = None
    sentiment_score: float = 0.5
    topics: List[str] = field(default_factory=list)
    confidence: float = 0.8


class SimpleKnowledgeBase:
    """Simple keyword-based knowledge base search for prototype."""

    def __init__(self, product_docs_path: str):
        self.documents = []
        self._load_documents(product_docs_path)

    def _load_documents(self, path: str):
        """Load and index product documentation."""
        try:
            with open(path, 'r') as f:
                content = f.read()

            # Split into sections (simple approach for prototype)
            sections = re.split(r'\n##+\s+', content)
            for section in sections:
                if section.strip():
                    lines = section.strip().split('\n')
                    title = lines[0] if lines else "Untitled"
                    self.documents.append({
                        'title': title,
                        'content': section,
                        'keywords': self._extract_keywords(title + ' ' + section)
                    })
        except FileNotFoundError:
            print(f"Warning: Product docs not found at {path}")

    def _extract_keywords(self, text: str) -> set:
        """Extract keywords from text for search."""
        # Remove common words and extract meaningful terms
        stop_words = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been',
                      'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
                      'would', 'could', 'should', 'may', 'might', 'must', 'shall',
                      'can', 'need', 'to', 'of', 'in', 'for', 'on', 'with', 'at',
                      'by', 'from', 'as', 'into', 'through', 'during', 'before',
                      'after', 'above', 'below', 'between', 'under', 'again',
                      'further', 'then', 'once', 'here', 'there', 'when', 'where',
                      'why', 'how', 'all', 'each', 'few', 'more', 'most', 'other',
                      'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same',
                      'so', 'than', 'too', 'very', 'just', 'and', 'but', 'if', 'or'}

        words = re.findall(r'\b[a-z]+\b', text.lower())
        return set(w for w in words if w not in stop_words and len(w) > 2)

    def search(self, query: str, max_results: int = 5) -> List[Dict]:
        """Search knowledge base for relevant documents."""
        query_keywords = self._extract_keywords(query)

        results = []
        for doc in self.documents:
            # Calculate overlap score
            overlap = len(query_keywords & doc['keywords'])
            if overlap > 0:
                results.append({
                    'title': doc['title'],
                    'content': doc['content'][:500],  # Truncate for response
                    'score': overlap
                })

        # Sort by score and return top results
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:max_results]


class SentimentAnalyzer:
    """Simple rule-based sentiment analyzer for prototype."""

    POSITIVE_WORDS = {
        'happy', 'great', 'awesome', 'excellent', 'good', 'love', 'thanks',
        'thank', 'helpful', 'wonderful', 'fantastic', 'amazing', 'perfect',
        'best', 'nice', 'pleased', 'satisfied', 'appreciate'
    }

    NEGATIVE_WORDS = {
        'angry', 'terrible', 'awful', 'horrible', 'bad', 'hate', 'worst',
        'frustrated', 'disappointed', 'useless', 'broken', 'failed', 'fail',
        'error', 'problem', 'issue', 'wrong', 'ridiculous', 'unacceptable',
        'incompetent', 'lawsuit', 'attorney', 'legal', 'sue'
    }

    INTENSIFIERS = {
        'very', 'really', 'extremely', 'absolutely', 'totally', 'completely',
        'entirely', 'thoroughly', 'highly', 'incredibly'
    }

    def analyze(self, text: str) -> float:
        """
        Analyze sentiment of text.
        Returns score between 0.0 (very negative) and 1.0 (very positive).
        """
        text_lower = text.lower()
        words = re.findall(r'\b[a-z]+\b', text_lower)

        positive_count = sum(1 for w in words if w in self.POSITIVE_WORDS)
        negative_count = sum(1 for w in words if w in self.NEGATIVE_WORDS)
        intensifier_count = sum(1 for w in words if w in self.INTENSIFIERS)

        # Check for ALL CAPS (indicates strong emotion, usually negative)
        caps_ratio = sum(1 for c in text if c.isupper()) / max(len(text), 1)
        if caps_ratio > 0.5 and len(text) > 10:
            negative_count += 2

        # Check for multiple exclamation marks
        exclamation_count = text.count('!')
        if exclamation_count > 2:
            negative_count += 1

        # Calculate base sentiment
        total = positive_count + negative_count
        if total == 0:
            return 0.5  # Neutral

        base_sentiment = (positive_count + 0.5) / (total + 1)

        # Adjust for intensifiers (amplify the dominant sentiment)
        if intensifier_count > 0:
            if base_sentiment > 0.5:
                base_sentiment = min(1.0, base_sentiment + 0.1 * intensifier_count)
            else:
                base_sentiment = max(0.0, base_sentiment - 0.1 * intensifier_count)

        return round(base_sentiment, 2)


class EscalationDetector:
    """Detect when a conversation should be escalated to human support."""

    LEGAL_KEYWORDS = {
        'lawyer', 'attorney', 'lawsuit', 'sue', 'legal', 'court',
        'legal action', 'breach', 'compliance', 'gdpr', 'soc 2',
        'data processing', 'dpa', 'terms of service'
    }

    PRICING_KEYWORDS = {
        'pricing', 'cost', 'price', 'refund', 'money back', 'cancel',
        'subscription', 'billing error', 'overcharged', 'discount',
        'enterprise plan', 'custom pricing', 'negotiate'
    }

    HUMAN_REQUEST_PATTERNS = [
        r'\bhuman\b', r'\breal person\b', r'\blive agent\b',
        r'\bsupport representative\b', r'\btalk to someone\b',
        r'\bspeak with.*person\b', r'\bnot a bot\b', r'\bbot.*useless\b'
    ]

    CRITICAL_KEYWORDS = {
        'production down', 'outage', 'data loss', 'security breach',
        'hacked', 'unauthorized access', 'deleted', 'emergency'
    }

    def should_escalate(self, content: str, sentiment: float) -> Tuple[bool, Optional[str]]:
        """
        Determine if conversation should be escalated.
        Returns (should_escalate, reason).
        """
        content_lower = content.lower()

        # Check for legal keywords
        if any(kw in content_lower for kw in self.LEGAL_KEYWORDS):
            return True, "legal_inquiry"

        # Check for pricing/refund keywords
        if any(kw in content_lower for kw in self.PRICING_KEYWORDS):
            return True, "pricing_inquiry"

        # Check for human request patterns
        for pattern in self.HUMAN_REQUEST_PATTERNS:
            if re.search(pattern, content_lower):
                return True, "human_requested"

        # Check for critical issues
        if any(kw in content_lower for kw in self.CRITICAL_KEYWORDS):
            return True, "critical_incident"

        # Check for negative sentiment
        if sentiment < 0.3:
            return True, "negative_sentiment"

        return False, None


class ResponseFormatter:
    """Format responses appropriately for each channel."""

    def format(self, response: str, channel: Channel, ticket_id: str,
               customer_name: Optional[str] = None) -> str:
        """Format response based on channel requirements."""

        if channel == Channel.EMAIL:
            return self._format_email(response, ticket_id, customer_name)
        elif channel == Channel.WHATSAPP:
            return self._format_whatsapp(response)
        elif channel == Channel.WEB_FORM:
            return self._format_web_form(response, ticket_id, customer_name)
        else:
            return response

    def _format_email(self, response: str, ticket_id: str,
                      customer_name: Optional[str]) -> str:
        """Format for email: formal, detailed, with greeting/signature."""
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

    def _format_whatsapp(self, response: str) -> str:
        """Format for WhatsApp: concise, conversational, with emoji."""
        # Truncate if too long (WhatsApp preference)
        if len(response) > 300:
            response = response[:297] + "..."

        return f"{response}\n\n📱 Reply for more help or type 'human' for live support."

    def _format_web_form(self, response: str, ticket_id: str,
                         customer_name: Optional[str]) -> str:
        """Format for web form: semi-formal, with ticket reference."""
        greeting = f"Hi {customer_name}," if customer_name else "Hi,"

        return f"""{greeting}

Thanks for contacting support!

{response}

---
Need more help? Reply to this message or visit our support portal.
Ticket: {ticket_id}"""


class CustomerSuccessAgent:
    """
    Main agent class that orchestrates the customer interaction loop.
    """

    def __init__(self, product_docs_path: str):
        self.knowledge_base = SimpleKnowledgeBase(product_docs_path)
        self.sentiment_analyzer = SentimentAnalyzer()
        self.escalation_detector = EscalationDetector()
        self.formatter = ResponseFormatter()
        self.ticket_counter = 0

    def _generate_ticket_id(self) -> str:
        """Generate a unique ticket ID."""
        self.ticket_counter += 1
        return f"TKT-{datetime.now().strftime('%Y%m%d')}-{self.ticket_counter:04d}"

    def _extract_topics(self, content: str) -> List[str]:
        """Extract topics from customer message."""
        topic_keywords = {
            'authentication': ['api key', 'login', 'password', 'auth', 'token', 'oauth'],
            'cicd': ['pipeline', 'ci/cd', 'build', 'deploy', 'runner', 'stage'],
            'billing': ['price', 'cost', 'billing', 'invoice', 'payment', 'refund'],
            'integrations': ['github', 'slack', 'jira', 'integration', 'connect'],
            'api': ['api', 'endpoint', 'rate limit', 'request', 'response'],
            'general': ['help', 'question', 'how to', 'get started'],
            'bug_report': ['bug', 'error', 'not working', 'broken', 'issue'],
            'feedback': ['feature request', 'suggestion', 'improve', 'love', 'great']
        }

        content_lower = content.lower()
        topics = []

        for topic, keywords in topic_keywords.items():
            if any(kw in content_lower for kw in keywords):
                topics.append(topic)

        return topics if topics else ['general']

    def process_message(self, message: CustomerMessage) -> AgentResponse:
        """
        Process a customer message and generate response.

        This is the core interaction loop:
        1. Analyze sentiment
        2. Extract topics
        3. Search knowledge base
        4. Generate response
        5. Check for escalation
        6. Format for channel
        """
        # Handle empty messages
        if not message.content.strip():
            return AgentResponse(
                ticket_id=self._generate_ticket_id(),
                response_text="I'd be happy to help you! Could you please provide more details about your question or issue?",
                formatted_response=self.formatter.format(
                    "I'd be happy to help you! Could you please provide more details about your question or issue?",
                    message.channel,
                    self._generate_ticket_id(),
                    message.customer_name
                ),
                should_escalate=False,
                sentiment_score=0.5,
                topics=['general']
            )

        # Step 1: Analyze sentiment
        sentiment = self.sentiment_analyzer.analyze(message.content)

        # Step 2: Extract topics
        topics = self._extract_topics(message.content)

        # Step 3: Search knowledge base
        search_query = message.subject + ' ' + message.content if message.subject else message.content
        kb_results = self.knowledge_base.search(search_query, max_results=3)

        # Step 4: Generate response
        response_text = self._generate_response(message.content, kb_results, topics)

        # Step 5: Check for escalation
        should_escalate, escalation_reason = self.escalation_detector.should_escalate(
            message.content, sentiment
        )

        # If escalation needed, modify response
        if should_escalate:
            response_text = self._add_escalation_message(response_text, escalation_reason)

        # Step 6: Format for channel
        ticket_id = self._generate_ticket_id()
        formatted = self.formatter.format(
            response_text,
            message.channel,
            ticket_id,
            message.customer_name
        )

        return AgentResponse(
            ticket_id=ticket_id,
            response_text=response_text,
            formatted_response=formatted,
            should_escalate=should_escalate,
            escalation_reason=escalation_reason,
            sentiment_score=sentiment,
            topics=topics,
            confidence=0.8 if kb_results else 0.5
        )

    def _generate_response(self, content: str, kb_results: List[Dict],
                          topics: List[str]) -> str:
        """Generate helpful response based on knowledge base results."""

        if not kb_results:
            return self._generate_fallback_response(topics)

        # Use top result to craft response
        top_result = kb_results[0]

        # Simple response generation (in production, this would use an LLM)
        response = f"Based on our documentation about {top_result['title']}:\n\n"

        # Extract key information from the result
        lines = top_result['content'].split('\n')
        key_points = []
        for line in lines[:10]:  # Limit to first 10 lines
            if line.strip() and not line.startswith('#'):
                key_points.append(line.strip())

        response += '\n'.join(key_points[:5])  # Top 5 points

        if len(kb_results) > 1:
            response += f"\n\nYou can also find more information in: {kb_results[1]['title']}"

        return response

    def _generate_fallback_response(self, topics: List[str]) -> str:
        """Generate response when knowledge base has no results."""
        topic = topics[0] if topics else 'general'

        fallbacks = {
            'authentication': "For authentication issues, please check that you're using the correct API key format. API keys can be generated in Settings > API Keys. If you're still having trouble, I can connect you with a specialist.",
            'cicd': "Pipeline issues can have various causes. Please check that your .devflow/pipeline.yml is valid and that you have available runners. You can view runner status in Settings > Runners.",
            'billing': "For billing questions, I'll need to connect you with our billing team who can access your account details.",
            'integrations': "Integration setup can vary by platform. Please check our integrations documentation or I can connect you with a specialist.",
            'api': "For API questions, please check our API documentation at docs.devflow.com. If you're hitting rate limits, consider upgrading your plan.",
            'general': "I'd be happy to help! Could you provide more specific details about what you're trying to accomplish?",
            'bug_report': "Thank you for reporting this issue. Please try clearing your browser cache and refreshing. If the problem persists, I'll escalate this to our engineering team.",
            'feedback': "Thank you for your feedback! We really appreciate hearing from our users. I'll pass this along to our product team."
        }

        return fallbacks.get(topic, fallbacks['general'])

    def _add_escalation_message(self, response: str, reason: str) -> str:
        """Add escalation message to response."""
        escalation_messages = {
            'legal_inquiry': "\n\nI understand this is a serious matter. I'm connecting you with our legal team who can provide the appropriate documentation and assistance. They will contact you within 1 hour.",
            'pricing_inquiry': "\n\nI'll connect you with our billing team who can discuss pricing options and assist with your request. They will contact you within 2 hours.",
            'human_requested': "\n\nI'll connect you with a human agent who can assist you further. They will contact you within 4 hours.",
            'negative_sentiment': "\n\nI understand your frustration and I want to make sure you get the help you deserve. Let me connect you with a senior support specialist.",
            'critical_incident': "\n\nThis is a critical issue. I'm alerting our emergency response team immediately. They will contact you within 15 minutes."
        }

        return response + escalation_messages.get(reason, "\n\nLet me connect you with a specialist who can help further.")


# Convenience functions for testing
def create_message_from_email(channel_message_id: str, from_email: str,
                              subject: str, content: str) -> CustomerMessage:
    """Create a normalized message from email data."""
    return CustomerMessage(
        channel=Channel.EMAIL,
        channel_message_id=channel_message_id,
        customer_email=from_email,
        subject=subject,
        content=content
    )


def create_message_from_whatsapp(channel_message_id: str, from_phone: str,
                                  content: str) -> CustomerMessage:
    """Create a normalized message from WhatsApp data."""
    return CustomerMessage(
        channel=Channel.WHATSAPP,
        channel_message_id=channel_message_id,
        customer_phone=from_phone,
        content=content
    )


def create_message_from_web_form(channel_message_id: str, name: str,
                                  email: str, subject: str,
                                  content: str) -> CustomerMessage:
    """Create a normalized message from web form data."""
    return CustomerMessage(
        channel=Channel.WEB_FORM,
        channel_message_id=channel_message_id,
        customer_name=name,
        customer_email=email,
        subject=subject,
        content=content
    )


# Example usage and testing
if __name__ == "__main__":
    # Initialize agent
    agent = CustomerSuccessAgent(product_docs_path="context/product-docs.md")

    # Test 1: Email - API key question
    print("=" * 60)
    print("TEST 1: Email - API Key Question")
    print("=" * 60)
    msg1 = create_message_from_email(
        "msg-001",
        "john@example.com",
        "How do I create an API key?",
        "Hi, I just signed up and I'm trying to integrate with your API. How do I generate an API key?"
    )
    response1 = agent.process_message(msg1)
    print(f"Ticket ID: {response1.ticket_id}")
    print(f"Sentiment: {response1.sentiment_score}")
    print(f"Topics: {response1.topics}")
    print(f"Escalate: {response1.should_escalate}")
    print(f"\nFormatted Response:\n{response1.formatted_response}")

    # Test 2: WhatsApp - Quick question
    print("\n" + "=" * 60)
    print("TEST 2: WhatsApp - Quick Question")
    print("=" * 60)
    msg2 = create_message_from_whatsapp(
        "msg-002",
        "+14155551234",
        "hey how do i invite team members to my project?"
    )
    response2 = agent.process_message(msg2)
    print(f"Ticket ID: {response2.ticket_id}")
    print(f"Sentiment: {response2.sentiment_score}")
    print(f"Topics: {response2.topics}")
    print(f"Escalate: {response2.should_escalate}")
    print(f"\nFormatted Response:\n{response2.formatted_response}")

    # Test 3: Web Form - Technical issue
    print("\n" + "=" * 60)
    print("TEST 3: Web Form - Technical Issue")
    print("=" * 60)
    msg3 = create_message_from_web_form(
        "msg-003",
        "Mike Johnson",
        "mike@webdev.co",
        "GitHub integration not working",
        "I tried connecting our GitHub repository but keep getting an authorization error."
    )
    response3 = agent.process_message(msg3)
    print(f"Ticket ID: {response3.ticket_id}")
    print(f"Sentiment: {response3.sentiment_score}")
    print(f"Topics: {response3.topics}")
    print(f"Escalate: {response3.should_escalate}")
    print(f"\nFormatted Response:\n{response3.formatted_response}")

    # Test 4: Escalation - Pricing inquiry
    print("\n" + "=" * 60)
    print("TEST 4: Email - Pricing Inquiry (Should Escalate)")
    print("=" * 60)
    msg4 = create_message_from_email(
        "msg-004",
        "sarah@techcorp.com",
        "Enterprise pricing inquiry",
        "We're interested in the Enterprise plan. Can you provide custom pricing for 200 users?"
    )
    response4 = agent.process_message(msg4)
    print(f"Ticket ID: {response4.ticket_id}")
    print(f"Sentiment: {response4.sentiment_score}")
    print(f"Topics: {response4.topics}")
    print(f"Escalate: {response4.should_escalate}")
    print(f"Escalation Reason: {response4.escalation_reason}")
    print(f"\nFormatted Response:\n{response4.formatted_response}")

    # Test 5: Escalation - Negative sentiment
    print("\n" + "=" * 60)
    print("TEST 5: WhatsApp - Angry Customer (Should Escalate)")
    print("=" * 60)
    msg5 = create_message_from_whatsapp(
        "msg-005",
        "+14155559876",
        "THIS IS RIDICULOUS!!! Your platform is BROKEN!!! I want a FULL REFUND immediately!!!"
    )
    response5 = agent.process_message(msg5)
    print(f"Ticket ID: {response5.ticket_id}")
    print(f"Sentiment: {response5.sentiment_score}")
    print(f"Topics: {response5.topics}")
    print(f"Escalate: {response5.should_escalate}")
    print(f"Escalation Reason: {response5.escalation_reason}")
    print(f"\nFormatted Response:\n{response5.formatted_response}")
