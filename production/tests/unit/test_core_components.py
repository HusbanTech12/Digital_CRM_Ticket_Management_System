"""
Unit Tests for Customer Success FTE
Stage 3: Integration & Testing

Unit tests for core components:
- Sentiment analysis
- Escalation detection
- Channel formatting
- Knowledge base search
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.agent.core_loop import (
    SentimentAnalyzer,
    EscalationDetector,
    ResponseFormatter,
    Channel
)


# =============================================================================
# Sentiment Analysis Tests
# =============================================================================

class TestSentimentAnalyzer:
    """Test sentiment analysis functionality."""

    @pytest.fixture
    def analyzer(self):
        return SentimentAnalyzer()

    @pytest.mark.unit
    def test_positive_sentiment(self, analyzer):
        """Should detect positive sentiment."""
        text = "This is amazing! Best product ever! I love it!"
        score = analyzer.analyze(text)
        assert score >= 0.7

    @pytest.mark.unit
    def test_negative_sentiment(self, analyzer):
        """Should detect negative sentiment."""
        text = "This is terrible! Worst product ever! I hate it!"
        score = analyzer.analyze(text)
        assert score < 0.3

    @pytest.mark.unit
    def test_neutral_sentiment(self, analyzer):
        """Should detect neutral sentiment."""
        text = "I have a question about the product."
        score = analyzer.analyze(text)
        assert 0.4 <= score <= 0.6

    @pytest.mark.unit
    def test_all_caps_negative(self, analyzer):
        """Should detect ALL CAPS as negative."""
        text = "THIS IS RIDICULOUS! YOUR PLATFORM IS BROKEN!"
        score = analyzer.analyze(text)
        assert score < 0.3

    @pytest.mark.unit
    def test_exclamation_marks(self, analyzer):
        """Should consider multiple exclamation marks."""
        text = "This is bad!!!"
        score = analyzer.analyze(text)
        assert score < 0.5

    @pytest.mark.unit
    def test_empty_text(self, analyzer):
        """Should handle empty text."""
        score = analyzer.analyze("")
        assert score == 0.5  # Default neutral

    @pytest.mark.unit
    def test_mixed_sentiment(self, analyzer):
        """Should handle mixed sentiment."""
        text = "Good product but has some issues."
        score = analyzer.analyze(text)
        assert 0.3 <= score <= 0.7


# =============================================================================
# Escalation Detection Tests
# =============================================================================

class TestEscalationDetector:
    """Test escalation detection functionality."""

    @pytest.fixture
    def detector(self):
        return EscalationDetector()

    @pytest.mark.unit
    def test_legal_keywords_escalate(self, detector, escalation_test_cases):
        """Legal keywords should trigger escalation."""
        test_case = escalation_test_cases[0]  # legal_inquiry
        should_escalate, reason = detector.should_escalate(test_case["message"], 0.5)
        assert should_escalate == test_case["should_escalate"]
        assert reason == test_case["expected_reason"]

    @pytest.mark.unit
    def test_pricing_keywords_escalate(self, detector, escalation_test_cases):
        """Pricing keywords should trigger escalation."""
        test_case = escalation_test_cases[1]  # pricing_inquiry
        should_escalate, reason = detector.should_escalate(test_case["message"], 0.5)
        assert should_escalate == test_case["should_escalate"]
        assert reason == test_case["expected_reason"]

    @pytest.mark.unit
    def test_refund_request_escalate(self, detector, escalation_test_cases):
        """Refund requests should trigger escalation."""
        test_case = escalation_test_cases[2]  # refund_request
        should_escalate, reason = detector.should_escalate(test_case["message"], 0.5)
        assert should_escalate == test_case["should_escalate"]
        assert reason == test_case["expected_reason"]

    @pytest.mark.unit
    def test_human_request_escalate(self, detector, escalation_test_cases):
        """Human agent requests should trigger escalation."""
        test_case = escalation_test_cases[3]  # human_requested
        should_escalate, reason = detector.should_escalate(test_case["message"], 0.5)
        assert should_escalate == test_case["should_escalate"]
        assert reason == test_case["expected_reason"]

    @pytest.mark.unit
    def test_negative_sentiment_escalate(self, detector, escalation_test_cases):
        """Negative sentiment should trigger escalation."""
        test_case = escalation_test_cases[4]  # negative_sentiment
        should_escalate, reason = detector.should_escalate(test_case["message"], 0.1)
        assert should_escalate == test_case["should_escalate"]

    @pytest.mark.unit
    def test_critical_incident_escalate(self, detector, escalation_test_cases):
        """Critical incidents should trigger escalation."""
        test_case = escalation_test_cases[5]  # critical_incident
        should_escalate, reason = detector.should_escalate(test_case["message"], 0.5)
        assert should_escalate == test_case["should_escalate"]
        assert reason == test_case["expected_reason"]

    @pytest.mark.unit
    def test_normal_question_no_escalate(self, detector, escalation_test_cases):
        """Normal questions should not escalate."""
        test_case = escalation_test_cases[6]  # normal_question
        should_escalate, reason = detector.should_escalate(test_case["message"], 0.6)
        assert should_escalate == test_case["should_escalate"]

    @pytest.mark.unit
    def test_positive_feedback_no_escalate(self, detector, escalation_test_cases):
        """Positive feedback should not escalate."""
        test_case = escalation_test_cases[7]  # positive_feedback
        should_escalate, reason = detector.should_escalate(test_case["message"], 0.9)
        assert should_escalate == test_case["should_escalate"]

    @pytest.mark.unit
    def test_all_escalation_triggers(self, detector, escalation_test_cases):
        """Test all escalation triggers from fixture."""
        for test_case in escalation_test_cases:
            should_escalate, reason = detector.should_escalate(
                test_case["message"],
                0.1 if "negative" in test_case["name"] else 0.5
            )
            assert should_escalate == test_case["should_escalate"], \
                f"Failed for test case: {test_case['name']}"
            if test_case["should_escalate"]:
                assert reason == test_case["expected_reason"], \
                    f"Wrong reason for: {test_case['name']}"


# =============================================================================
# Channel Formatting Tests
# =============================================================================

class TestResponseFormatter:
    """Test channel-specific response formatting."""

    @pytest.fixture
    def formatter(self):
        return ResponseFormatter()

    @pytest.mark.unit
    def test_email_format_greeting(self, formatter, channel_response_tests):
        """Email should include proper greeting."""
        test_config = channel_response_tests[0]  # email
        response = formatter.format(
            "Here is your answer.",
            Channel.EMAIL,
            "TKT-001",
            "John Doe"
        )
        assert "Dear John Doe" in response or "Dear Customer" in response

    @pytest.mark.unit
    def test_email_format_signature(self, formatter, channel_response_tests):
        """Email should include signature."""
        test_config = channel_response_tests[0]  # email
        response = formatter.format(
            "Here is your answer.",
            Channel.EMAIL,
            "TKT-001"
        )
        assert "Best regards" in response or "TechCorp" in response

    @pytest.mark.unit
    def test_email_format_ticket_reference(self, formatter):
        """Email should include ticket reference."""
        response = formatter.format(
            "Here is your answer.",
            Channel.EMAIL,
            "TKT-TEST-123"
        )
        assert "TKT-TEST-123" in response

    @pytest.mark.unit
    def test_whatsapp_format_concise(self, formatter, channel_response_tests):
        """WhatsApp should be concise."""
        test_config = channel_response_tests[1]  # whatsapp
        long_response = "A" * 500
        formatted = formatter.format(
            long_response,
            Channel.WHATSAPP,
            "TKT-001"
        )
        assert len(formatted) <= test_config["max_chars"] + 50  # Allow some buffer

    @pytest.mark.unit
    def test_whatsapp_format_emoji(self, formatter, channel_response_tests):
        """WhatsApp should include emoji."""
        test_config = channel_response_tests[1]  # whatsapp
        response = formatter.format(
            "Here is your answer.",
            Channel.WHATSAPP,
            "TKT-001"
        )
        assert any(char in response for char in ["📱", "👍", "😊"])

    @pytest.mark.unit
    def test_whatsapp_format_human_option(self, formatter, channel_response_tests):
        """WhatsApp should offer human agent option."""
        test_config = channel_response_tests[1]  # whatsapp
        response = formatter.format(
            "Here is your answer.",
            Channel.WHATSAPP,
            "TKT-001"
        )
        assert "human" in response.lower()

    @pytest.mark.unit
    def test_web_form_format_greeting(self, formatter, channel_response_tests):
        """Web form should include greeting."""
        test_config = channel_response_tests[2]  # web_form
        response = formatter.format(
            "Here is your answer.",
            Channel.WEB_FORM,
            "TKT-001",
            "Jane"
        )
        assert "Hi Jane" in response or "Hi," in response

    @pytest.mark.unit
    def test_web_form_format_ticket_reference(self, formatter, channel_response_tests):
        """Web form should include ticket reference."""
        test_config = channel_response_tests[2]  # web_form
        response = formatter.format(
            "Here is your answer.",
            Channel.WEB_FORM,
            "TKT-WEB-456"
        )
        assert "TKT-WEB-456" in response or "Ticket:" in response

    @pytest.mark.unit
    def test_format_unknown_channel(self, formatter):
        """Should handle unknown channel gracefully."""
        response = formatter.format(
            "Here is your answer.",
            "unknown_channel",  # type: ignore
            "TKT-001"
        )
        assert response  # Should return something


# =============================================================================
# Core Loop Tests
# =============================================================================

class TestCoreLoop:
    """Test the core interaction loop."""

    @pytest.fixture
    def agent(self):
        from src.agent.core_loop import CustomerSuccessAgent
        return CustomerSuccessAgent("context/product-docs.md")

    @pytest.mark.unit
    def test_empty_message_handling(self, agent):
        """Should handle empty messages gracefully."""
        from src.agent.core_loop import CustomerMessage, Channel

        message = CustomerMessage(
            channel=Channel.EMAIL,
            channel_message_id="test-001",
            customer_email="test@example.com",
            content=""
        )
        response = agent.process_message(message)

        assert response.ticket_id is not None
        assert "help" in response.response_text.lower() or "question" in response.response_text.lower()

    @pytest.mark.unit
    def test_api_key_question(self, agent):
        """Should answer API key questions."""
        from src.agent.core_loop import CustomerMessage, Channel

        message = CustomerMessage(
            channel=Channel.EMAIL,
            channel_message_id="test-002",
            customer_email="test@example.com",
            subject="API Key",
            content="How do I create an API key?"
        )
        response = agent.process_message(message)

        assert response.ticket_id is not None
        assert response.should_escalate == False

    @pytest.mark.unit
    def test_pricing_question_escalates(self, agent):
        """Pricing questions should escalate."""
        from src.agent.core_loop import CustomerMessage, Channel

        message = CustomerMessage(
            channel=Channel.EMAIL,
            channel_message_id="test-003",
            customer_email="test@example.com",
            subject="Pricing",
            content="What's the price for Enterprise?"
        )
        response = agent.process_message(message)

        assert response.should_escalate == True
        assert response.escalation_reason == "pricing_inquiry"


# =============================================================================
# Memory Tests
# =============================================================================

class TestMemory:
    """Test conversation memory functionality."""

    @pytest.fixture
    def memory_store(self):
        from src.agent.memory import MemoryStore
        return MemoryStore()

    @pytest.mark.unit
    def test_get_or_create_customer_by_email(self, memory_store):
        """Should get or create customer by email."""
        customer = memory_store.get_or_create_customer(
            email="test@example.com",
            name="Test User"
        )

        assert customer.email == "test@example.com"
        assert customer.name == "Test User"

    @pytest.mark.unit
    def test_get_or_create_customer_by_phone(self, memory_store):
        """Should get or create customer by phone."""
        customer = memory_store.get_or_create_customer(
            phone="+14155551234",
            name="Phone User"
        )

        assert customer.phone == "+14155551234"

    @pytest.mark.unit
    def test_same_customer_different_identifiers(self, memory_store):
        """Same email should return same customer."""
        customer1 = memory_store.get_or_create_customer(email="test@example.com")
        customer2 = memory_store.get_or_create_customer(email="test@example.com")

        assert customer1.id == customer2.id

    @pytest.mark.unit
    def test_create_conversation(self, memory_store):
        """Should create conversation for customer."""
        customer = memory_store.get_or_create_customer(email="conv-test@example.com")
        conversation = memory_store.create_conversation(customer.id, "email")

        assert conversation.customer_id == customer.id
        assert conversation.initial_channel == "email"
        assert conversation.status == "active"

    @pytest.mark.unit
    def test_get_active_conversation(self, memory_store):
        """Should get active conversation."""
        customer = memory_store.get_or_create_customer(email="active-test@example.com")
        conv1 = memory_store.create_conversation(customer.id, "email")

        active = memory_store.get_active_conversation(customer.id)

        assert active is not None
        assert active.id == conv1.id


# =============================================================================
# Run Tests
# =============================================================================

if __name__ == "__main__":
    pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "-m", "unit"
    ])
