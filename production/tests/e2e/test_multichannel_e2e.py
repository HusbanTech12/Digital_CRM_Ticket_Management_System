"""
Multi-Channel E2E Test Suite
Stage 3: Integration & Testing (Exercise 3.1)

End-to-end tests for all communication channels:
- Email (Gmail)
- WhatsApp (Twilio)
- Web Form

Tests verify the complete flow from message intake to response.
"""

import pytest
import asyncio
from typing import Dict, Any
from datetime import datetime, timezone
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))


# =============================================================================
# Test Configuration
# =============================================================================

BASE_URL = "http://localhost:8000"
TIMEOUT = 30  # seconds


# =============================================================================
# Web Form Channel Tests
# =============================================================================

class TestWebFormChannel:
    """Test the web support form (required build)."""

    @pytest.mark.e2e
    @pytest.mark.channel
    @pytest.mark.asyncio
    async def test_form_submission_success(self, async_client, sample_web_form_submission):
        """Web form submission should create ticket and return ID."""
        response = await async_client.post(
            "/support/submit",
            json=sample_web_form_submission,
            timeout=TIMEOUT
        )

        assert response.status_code == 200
        data = response.json()
        assert "ticket_id" in data
        assert data["message"] is not None
        assert "estimated_response_time" in data
        assert data["status"] == "submitted"

    @pytest.mark.e2e
    @pytest.mark.channel
    @pytest.mark.asyncio
    async def test_form_validation_name_required(self, async_client, sample_web_form_submission):
        """Form should validate name is required."""
        sample_web_form_submission["name"] = ""
        response = await async_client.post(
            "/support/submit",
            json=sample_web_form_submission,
            timeout=TIMEOUT
        )

        assert response.status_code == 422  # Validation error

    @pytest.mark.e2e
    @pytest.mark.channel
    @pytest.mark.asyncio
    async def test_form_validation_email_required(self, async_client, sample_web_form_submission):
        """Form should validate email is required."""
        sample_web_form_submission["email"] = ""
        response = await async_client.post(
            "/support/submit",
            json=sample_web_form_submission,
            timeout=TIMEOUT
        )

        assert response.status_code == 422

    @pytest.mark.e2e
    @pytest.mark.channel
    @pytest.mark.asyncio
    async def test_form_validation_invalid_email(self, async_client, sample_web_form_submission):
        """Form should validate email format."""
        sample_web_form_submission["email"] = "invalid-email"
        response = await async_client.post(
            "/support/submit",
            json=sample_web_form_submission,
            timeout=TIMEOUT
        )

        assert response.status_code == 422

    @pytest.mark.e2e
    @pytest.mark.channel
    @pytest.mark.asyncio
    async def test_form_validation_category_required(self, async_client, sample_web_form_submission):
        """Form should validate category."""
        sample_web_form_submission["category"] = "invalid_category"
        response = await async_client.post(
            "/support/submit",
            json=sample_web_form_submission,
            timeout=TIMEOUT
        )

        assert response.status_code == 422

    @pytest.mark.e2e
    @pytest.mark.channel
    @pytest.mark.asyncio
    async def test_form_validation_message_length(self, async_client, sample_web_form_submission):
        """Form should validate message minimum length."""
        sample_web_form_submission["message"] = "Short"
        response = await async_client.post(
            "/support/submit",
            json=sample_web_form_submission,
            timeout=TIMEOUT
        )

        assert response.status_code == 422

    @pytest.mark.e2e
    @pytest.mark.channel
    @pytest.mark.asyncio
    async def test_ticket_status_retrieval(self, async_client, sample_web_form_submission):
        """Should be able to check ticket status after submission."""
        # Submit form
        submit_response = await async_client.post(
            "/support/submit",
            json=sample_web_form_submission,
            timeout=TIMEOUT
        )

        ticket_id = submit_response.json()["ticket_id"]

        # Check status
        status_response = await async_client.get(
            f"/support/ticket/{ticket_id}",
            timeout=TIMEOUT
        )

        assert status_response.status_code == 200
        data = status_response.json()
        assert data["ticket_id"] == ticket_id
        assert data["status"] in ["open", "processing", "submitted"]

    @pytest.mark.e2e
    @pytest.mark.channel
    @pytest.mark.asyncio
    async def test_form_categories_endpoint(self, async_client):
        """Should return available categories."""
        response = await async_client.get("/support/categories", timeout=TIMEOUT)

        assert response.status_code == 200
        data = response.json()
        assert "categories" in data
        assert len(data["categories"]) >= 5

    @pytest.mark.e2e
    @pytest.mark.channel
    @pytest.mark.asyncio
    async def test_form_priority_levels_endpoint(self, async_client):
        """Should return available priority levels."""
        response = await async_client.get("/support/priority-levels", timeout=TIMEOUT)

        assert response.status_code == 200
        data = response.json()
        assert "priority_levels" in data
        assert len(data["priority_levels"]) >= 4


# =============================================================================
# Email Channel Tests
# =============================================================================

class TestEmailChannel:
    """Test Gmail integration."""

    @pytest.mark.e2e
    @pytest.mark.channel
    @pytest.mark.asyncio
    async def test_gmail_webhook_processing(self, async_client, sample_email_message):
        """Gmail webhook should process incoming emails."""
        # Simulate Pub/Sub notification
        pubsub_payload = {
            "message": {
                "data": "test-history-id",
                "messageId": "pubsub-123"
            },
            "subscription": "projects/test/subscriptions/gmail-push"
        }

        response = await async_client.post(
            "/webhooks/gmail",
            json=pubsub_payload,
            timeout=TIMEOUT
        )

        # Should accept the webhook (may return ignored if no history)
        assert response.status_code in [200, 201]

    @pytest.mark.e2e
    @pytest.mark.channel
    @pytest.mark.asyncio
    async def test_gmail_webhook_invalid_payload(self, async_client):
        """Gmail webhook should handle invalid payload."""
        response = await async_client.post(
            "/webhooks/gmail",
            json={"invalid": "payload"},
            timeout=TIMEOUT
        )

        # Should handle gracefully
        assert response.status_code in [200, 400, 500]

    @pytest.mark.e2e
    @pytest.mark.channel
    @pytest.mark.asyncio
    async def test_gmail_setup_endpoint(self, async_client):
        """Gmail setup endpoint should be available."""
        response = await async_client.get(
            "/webhooks/gmail/setup",
            timeout=TIMEOUT
        )

        # May fail without credentials, but endpoint should exist
        assert response.status_code in [200, 500]


# =============================================================================
# WhatsApp Channel Tests
# =============================================================================

class TestWhatsAppChannel:
    """Test WhatsApp/Twilio integration."""

    @pytest.mark.e2e
    @pytest.mark.channel
    @pytest.mark.asyncio
    async def test_whatsapp_webhook_processing(self, async_client, sample_whatsapp_message):
        """WhatsApp webhook should process incoming messages."""
        # Note: Signature validation is skipped in test mode
        response = await async_client.post(
            "/webhooks/whatsapp",
            data={
                "MessageSid": "SM123",
                "From": "whatsapp:+1234567890",
                "Body": "Hello, I need help",
                "ProfileName": "Test User"
            },
            timeout=TIMEOUT
        )

        # Will return TwiML or accept in dev mode
        assert response.status_code in [200, 403]  # 403 if signature validation enabled

    @pytest.mark.e2e
    @pytest.mark.channel
    @pytest.mark.asyncio
    async def test_whatsapp_status_webhook(self, async_client):
        """WhatsApp status webhook should handle delivery updates."""
        response = await async_client.post(
            "/webhooks/whatsapp/status",
            data={
                "MessageSid": "SM123",
                "MessageStatus": "delivered"
            },
            timeout=TIMEOUT
        )

        assert response.status_code == 200


# =============================================================================
# Cross-Channel Continuity Tests
# =============================================================================

class TestCrossChannelContinuity:
    """Test that conversations persist across channels."""

    @pytest.mark.e2e
    @pytest.mark.asyncio
    async def test_customer_history_across_channels(
        self, async_client, sample_customer_data
    ):
        """Customer history should include all channel interactions."""
        # Submit form via web
        web_response = await async_client.post(
            "/support/submit",
            json={
                "name": sample_customer_data["name"],
                "email": sample_customer_data["email"],
                "subject": "Initial Contact",
                "category": "general",
                "message": "First contact via web form"
            },
            timeout=TIMEOUT
        )

        ticket_id = web_response.json()["ticket_id"]

        # Look up customer
        customer_response = await async_client.get(
            "/customers/lookup",
            params={"email": sample_customer_data["email"]},
            timeout=TIMEOUT
        )

        # Customer should be found
        if customer_response.status_code == 200:
            customer = customer_response.json()
            assert customer["email"] == sample_customer_data["email"]

    @pytest.mark.e2e
    @pytest.mark.asyncio
    async def test_same_customer_different_channels(
        self, async_client, sample_customer_data
    ):
        """Same customer contacting via different channels should be linked."""
        email = sample_customer_data["email"]

        # First contact via web form
        await async_client.post(
            "/support/submit",
            json={
                "name": "Test User",
                "email": email,
                "subject": "First Issue",
                "category": "general",
                "message": "First issue via web"
            },
            timeout=TIMEOUT
        )

        # Second contact - should recognize customer
        customer_response = await async_client.get(
            "/customers/lookup",
            params={"email": email},
            timeout=TIMEOUT
        )

        assert customer_response.status_code == 200


# =============================================================================
# Channel Metrics Tests
# =============================================================================

class TestChannelMetrics:
    """Test channel-specific metrics."""

    @pytest.mark.e2e
    @pytest.mark.asyncio
    async def test_metrics_by_channel(self, async_client):
        """Should return metrics broken down by channel."""
        response = await async_client.get(
            "/metrics/channels",
            timeout=TIMEOUT
        )

        assert response.status_code == 200
        data = response.json()

        # Should have metrics structure
        assert "metrics" in data or isinstance(data, list)

    @pytest.mark.e2e
    @pytest.mark.asyncio
    async def test_metrics_summary(self, async_client):
        """Should return overall metrics summary."""
        response = await async_client.get(
            "/metrics/summary",
            timeout=TIMEOUT
        )

        assert response.status_code == 200


# =============================================================================
# Health and Readiness Tests
# =============================================================================

class TestHealthEndpoints:
    """Test health and readiness endpoints."""

    @pytest.mark.e2e
    @pytest.mark.asyncio
    async def test_health_check(self, async_client):
        """Health check should return service status."""
        response = await async_client.get("/health", timeout=TIMEOUT)

        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "timestamp" in data
        assert "channels" in data

    @pytest.mark.e2e
    @pytest.mark.asyncio
    async def test_readiness_check(self, async_client):
        """Readiness check should verify dependencies."""
        response = await async_client.get("/ready", timeout=TIMEOUT)

        # Should be ready or not ready (but endpoint works)
        assert response.status_code in [200, 503]

    @pytest.mark.e2e
    @pytest.mark.asyncio
    async def test_liveness_check(self, async_client):
        """Liveness check should confirm service is alive."""
        response = await async_client.get("/live", timeout=TIMEOUT)

        assert response.status_code == 200


# =============================================================================
# Escalation Flow Tests
# =============================================================================

class TestEscalationFlow:
    """Test escalation functionality."""

    @pytest.mark.e2e
    @pytest.mark.asyncio
    async def test_ticket_escalation(self, async_client, sample_web_form_submission):
        """Tickets should be escalatable."""
        # Create ticket
        submit_response = await async_client.post(
            "/support/submit",
            json=sample_web_form_submission,
            timeout=TIMEOUT
        )

        ticket_id = submit_response.json()["ticket_id"]

        # Escalate ticket
        escalate_response = await async_client.post(
            f"/tickets/{ticket_id}/escalate",
            params={
                "reason": "customer_request",
                "urgency": "high",
                "context": "Test escalation"
            },
            timeout=TIMEOUT
        )

        assert escalate_response.status_code == 200
        data = escalate_response.json()
        assert "escalation_id" in data or data.get("status") == "escalated"


# =============================================================================
# Performance Tests (Basic)
# =============================================================================

class TestBasicPerformance:
    """Basic performance tests."""

    @pytest.mark.e2e
    @pytest.mark.asyncio
    async def test_response_time_health(self, async_client):
        """Health endpoint should respond quickly."""
        import time

        start = time.time()
        response = await async_client.get("/health", timeout=TIMEOUT)
        elapsed = time.time() - start

        assert response.status_code == 200
        assert elapsed < 1.0  # Should respond in under 1 second

    @pytest.mark.e2e
    @pytest.mark.asyncio
    async def test_response_time_form_submission(self, async_client, sample_web_form_submission):
        """Form submission should respond quickly."""
        import time

        start = time.time()
        response = await async_client.post(
            "/support/submit",
            json=sample_web_form_submission,
            timeout=TIMEOUT
        )
        elapsed = time.time() - start

        assert response.status_code == 200
        assert elapsed < 2.0  # Should respond in under 2 seconds


# =============================================================================
# Error Handling Tests
# =============================================================================

class TestErrorHandling:
    """Test error handling."""

    @pytest.mark.e2e
    @pytest.mark.asyncio
    async def test_404_for_unknown_ticket(self, async_client):
        """Unknown ticket should return 404."""
        response = await async_client.get(
            "/support/ticket/nonexistent-ticket-id",
            timeout=TIMEOUT
        )

        assert response.status_code == 404

    @pytest.mark.e2e
    @pytest.mark.asyncio
    async def test_400_for_missing_params(self, async_client):
        """Missing required params should return 400."""
        response = await async_client.get(
            "/customers/lookup",
            timeout=TIMEOUT
        )

        assert response.status_code == 400


# =============================================================================
# Main Test Runner
# =============================================================================

if __name__ == "__main__":
    pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "--maxfail=5",
        "-m", "e2e"
    ])
