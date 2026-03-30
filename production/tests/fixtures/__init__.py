"""
Test Fixtures for Customer Success FTE
Stage 3: Integration & Testing

Provides reusable fixtures for unit, integration, and E2E tests.
"""

import pytest
import asyncio
from typing import AsyncGenerator, Dict, Any
from datetime import datetime, timezone
import os
import sys

# Add production to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))


# =============================================================================
# Test Data Fixtures
# =============================================================================

@pytest.fixture
def sample_customer_data() -> Dict[str, Any]:
    """Sample customer data for testing."""
    return {
        "email": "test.customer@example.com",
        "phone": "+14155551234",
        "name": "Test Customer"
    }


@pytest.fixture
def sample_email_message() -> Dict[str, Any]:
    """Sample email message for testing."""
    return {
        "channel": "email",
        "channel_message_id": "test-email-001",
        "customer_email": "test.customer@example.com",
        "customer_name": "Test Customer",
        "subject": "How do I create an API key?",
        "content": "Hi, I just signed up for DevFlow and I'm trying to integrate it with our CI/CD pipeline. I can't figure out how to generate an API key. Could you please help?",
        "received_at": datetime.now(timezone.utc).isoformat(),
        "metadata": {
            "thread_id": "thread-001",
            "labels": ["INBOX", "UNREAD"]
        }
    }


@pytest.fixture
def sample_whatsapp_message() -> Dict[str, Any]:
    """Sample WhatsApp message for testing."""
    return {
        "channel": "whatsapp",
        "channel_message_id": "SM123456789",
        "customer_phone": "+14155551234",
        "customer_name": "Test User",
        "content": "hey how do i invite team members to my project?",
        "received_at": datetime.now(timezone.utc).isoformat(),
        "metadata": {
            "num_media": "0",
            "profile_name": "Test User",
            "from": "whatsapp:+14155551234",
            "to": "whatsapp:+14155238886"
        }
    }


@pytest.fixture
def sample_web_form_submission() -> Dict[str, Any]:
    """Sample web form submission for testing."""
    return {
        "name": "Web Form User",
        "email": "webuser@example.com",
        "subject": "GitHub integration not working",
        "category": "technical",
        "priority": "medium",
        "message": "I tried connecting our GitHub repository but keep getting an authorization error. I've tried multiple times and cleared my browser cache."
    }


@pytest.fixture
def sample_escalation_message() -> Dict[str, Any]:
    """Sample message that should trigger escalation."""
    return {
        "channel": "email",
        "channel_message_id": "test-escalation-001",
        "customer_email": "angry.customer@example.com",
        "subject": "Enterprise pricing inquiry",
        "content": "We're a team of 200 developers and we're interested in the Enterprise plan. Can you provide custom pricing? Also, we need a refund for last month.",
        "received_at": datetime.now(timezone.utc).isoformat()
    }


@pytest.fixture
def sample_knowledge_base_entries() -> list:
    """Sample knowledge base entries for testing."""
    return [
        {
            "title": "Creating an API Key",
            "content": """API keys authenticate your requests to the DevFlow API.

To create an API key:
1. Log in to your DevFlow dashboard at app.devflow.com
2. Navigate to Settings > API Keys
3. Click "Generate New Key"
4. Give your key a descriptive name
5. Copy the key immediately - it won't be shown again

Security Best Practices:
- Never commit API keys to version control
- Store keys in environment variables
- Rotate keys every 90 days""",
            "category": "authentication",
            "tags": ["api", "key", "authentication", "security"]
        },
        {
            "title": "Inviting Team Members",
            "content": """To invite team members to your project:

1. Go to Project Settings > Members
2. Click "Invite Member"
3. Enter their email address
4. Select their role:
   - Viewer: Read-only access
   - Developer: Can create and edit issues
   - Admin: Full project access
5. Click "Send Invitation"

The invited member will receive an email with instructions to join.""",
            "category": "general",
            "tags": ["team", "members", "invite", "collaboration"]
        },
        {
            "title": "GitHub Integration Setup",
            "content": """To connect your GitHub repository:

1. Go to Settings > Integrations > GitHub
2. Click "Connect GitHub"
3. Authorize DevFlow access to your GitHub account
4. Select the repositories you want to connect
5. Click "Save"

Features:
- Automatic issue linking from commit messages
- Pipeline triggers on push/PR
- Status checks on pull requests""",
            "category": "integrations",
            "tags": ["github", "integration", "repository"]
        }
    ]


@pytest.fixture
def escalation_test_cases() -> list:
    """Test cases for escalation detection."""
    return [
        {
            "name": "legal_inquiry",
            "message": "I'm going to contact my lawyer about this breach of contract.",
            "should_escalate": True,
            "expected_reason": "legal_inquiry"
        },
        {
            "name": "pricing_inquiry",
            "message": "What's the pricing for the Enterprise plan?",
            "should_escalate": True,
            "expected_reason": "pricing_inquiry"
        },
        {
            "name": "refund_request",
            "message": "I want a full refund immediately!",
            "should_escalate": True,
            "expected_reason": "refund_request"
        },
        {
            "name": "human_requested",
            "message": "I want to speak to a human agent please.",
            "should_escalate": True,
            "expected_reason": "human_requested"
        },
        {
            "name": "negative_sentiment",
            "message": "This is RIDICULOUS! Your platform is BROKEN and USELESS!",
            "should_escalate": True,
            "expected_reason": "negative_sentiment"
        },
        {
            "name": "critical_incident",
            "message": "Production is down! We have a critical outage!",
            "should_escalate": True,
            "expected_reason": "critical_incident"
        },
        {
            "name": "normal_question",
            "message": "How do I create an API key?",
            "should_escalate": False,
            "expected_reason": None
        },
        {
            "name": "positive_feedback",
            "message": "Love your product! It's amazing!",
            "should_escalate": False,
            "expected_reason": None
        }
    ]


@pytest.fixture
def channel_response_tests() -> list:
    """Test cases for channel-specific responses."""
    return [
        {
            "channel": "email",
            "expected_elements": ["Dear", "Thank you", "Best regards", "Ticket Reference"],
            "max_words": 500,
            "tone": "formal"
        },
        {
            "channel": "whatsapp",
            "expected_elements": ["📱", "human"],
            "max_chars": 300,
            "tone": "conversational"
        },
        {
            "channel": "web_form",
            "expected_elements": ["Hi", "Thanks", "Ticket:"],
            "max_words": 300,
            "tone": "semi-formal"
        }
    ]


# =============================================================================
# Async Test Helpers
# =============================================================================

@pytest.fixture
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def async_client():
    """Async HTTP client for API testing."""
    import httpx
    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        yield client


# =============================================================================
# Database Test Fixtures
# =============================================================================

@pytest.fixture
async def db_connection():
    """Database connection for testing."""
    from production.database import queries as db

    # Connect
    await db.get_db()

    yield db

    # Cleanup
    await db.close_db()


# =============================================================================
# Mock Fixtures
# =============================================================================

@pytest.fixture
def mock_openai_response():
    """Mock OpenAI API response."""
    return {
        "success": True,
        "output": "To create an API key, go to Settings > API Keys and click Generate New Key.",
        "tool_calls": [
            {"name": "create_ticket", "arguments": {"customer_id": "test-123"}},
            {"name": "search_knowledge_base", "arguments": {"query": "API key"}},
            {"name": "send_response", "arguments": {"message": "Response", "channel": "email"}}
        ]
    }


@pytest.fixture
def mock_kafka_producer():
    """Mock Kafka producer."""
    class MockProducer:
        def __init__(self):
            self.published_messages = []

        async def start(self):
            pass

        async def stop(self):
            pass

        async def publish(self, topic, event, key=None):
            self.published_messages.append({
                "topic": topic,
                "event": event,
                "key": key
            })

    return MockProducer()


# =============================================================================
# Test Configuration
# =============================================================================

@pytest.fixture
def test_config():
    """Test configuration."""
    return {
        "api_base_url": "http://localhost:8000",
        "timeout_seconds": 30,
        "max_retries": 3,
        "retry_delay_ms": 100
    }


# =============================================================================
# Pytest Hooks
# =============================================================================

def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line(
        "markers", "e2e: mark test as end-to-end test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "unit: mark test as unit test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "channel: mark test as channel-specific test"
    )
