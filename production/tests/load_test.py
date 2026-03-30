"""
Load Testing Configuration for Customer Success FTE
Stage 3: Integration & Testing (Exercise 3.2)

Uses Locust for load testing with scenarios for:
- Web form submissions
- Health checks
- API endpoints
- Multi-channel simulation
"""

from locust import HttpUser, task, between, events
import random
import json
import time
from datetime import datetime


# =============================================================================
# Test Data Generators
# =============================================================================

def generate_random_email():
    """Generate random email address."""
    domains = ["example.com", "test.io", "demo.org", "sample.net"]
    names = ["user", "customer", "test", "demo", "john", "jane"]
    return f"{random.choice(names)}{random.randint(1, 9999)}@{random.choice(domains)}"


def generate_random_name():
    """Generate random name."""
    first_names = ["John", "Jane", "Mike", "Sarah", "David", "Emma", "Chris", "Lisa"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Davis", "Miller"]
    return f"{random.choice(first_names)} {random.choice(last_names)}"


def generate_support_message():
    """Generate random support message."""
    categories = ["general", "technical", "billing", "feedback", "bug_report"]
    subjects = [
        "Help with API integration",
        "Question about features",
        "Issue with pipeline",
        "Billing inquiry",
        "Feature request",
        "Bug report",
        "Account access issue"
    ]
    messages = [
        "I'm trying to integrate your API but having trouble with authentication. Can you help?",
        "How do I invite team members to my project?",
        "The pipeline keeps failing with no clear error message.",
        "I have a question about my invoice from last month.",
        "Would love to see dark mode in the dashboard!",
        "Found a bug where the issue status doesn't update correctly.",
        "I can't log in to my account. Password reset isn't working."
    ]

    return {
        "name": generate_random_name(),
        "email": generate_random_email(),
        "subject": random.choice(subjects),
        "category": random.choice(categories),
        "priority": random.choice(["low", "medium", "high"]),
        "message": random.choice(messages)
    }


# =============================================================================
# Web Form User Simulation
# =============================================================================

class WebFormUser(HttpUser):
    """
    Simulate users submitting support forms.
    Most common traffic pattern.
    """
    wait_time = between(2, 10)  # Wait 2-10 seconds between tasks
    weight = 5  # Higher weight = more frequent

    @task(3)
    def submit_support_form(self):
        """Submit a support form."""
        form_data = generate_support_message()

        with self.client.post(
            "/support/submit",
            json=form_data,
            catch_response=True,
            name="/support/submit"
        ) as response:
            if response.status_code == 200:
                data = response.json()
                if "ticket_id" in data:
                    response.success()
                else:
                    response.failure("Missing ticket_id in response")
            else:
                response.failure(f"Status code: {response.status_code}")

    @task(1)
    def check_ticket_status(self):
        """Check ticket status (after submission)."""
        # First submit to get a ticket ID
        form_data = generate_support_message()
        submit_response = self.client.post(
            "/support/submit",
            json=form_data
        )

        if submit_response.status_code == 200:
            ticket_id = submit_response.json().get("ticket_id")

            # Then check status
            self.client.get(
                f"/support/ticket/{ticket_id}",
                name="/support/ticket/[id]"
            )

    @task(1)
    def get_categories(self):
        """Get support categories."""
        self.client.get(
            "/support/categories",
            name="/support/categories"
        )


# =============================================================================
# Health Check User Simulation
# =============================================================================

class HealthCheckUser(HttpUser):
    """
    Simulate monitoring systems checking health.
    Lower frequency but critical for uptime.
    """
    wait_time = between(5, 15)
    weight = 1

    @task(3)
    def check_health(self):
        """Check health endpoint."""
        self.client.get("/health", name="/health")

    @task(1)
    def check_readiness(self):
        """Check readiness endpoint."""
        self.client.get("/ready", name="/ready")

    @task(1)
    def check_liveness(self):
        """Check liveness endpoint."""
        self.client.get("/live", name="/live")


# =============================================================================
# API User Simulation
# =============================================================================

class APIUser(HttpUser):
    """
    Simulate API consumers using various endpoints.
    """
    wait_time = between(3, 8)
    weight = 3

    @task(2)
    def lookup_customer(self):
        """Look up customer by email."""
        email = generate_random_email()
        self.client.get(
            "/customers/lookup",
            params={"email": email},
            name="/customers/lookup"
        )

    @task(1)
    def get_metrics(self):
        """Get channel metrics."""
        self.client.get(
            "/metrics/channels",
            name="/metrics/channels"
        )

    @task(1)
    def get_metrics_summary(self):
        """Get metrics summary."""
        self.client.get(
            "/metrics/summary",
            name="/metrics/summary"
        )


# =============================================================================
# Multi-Channel Simulation
# =============================================================================

class MultiChannelUser(HttpUser):
    """
    Simulate multi-channel traffic pattern.
    Tests the complete system under realistic load.
    """
    wait_time = between(1, 5)
    weight = 4

    @task(5)
    def web_form_submission(self):
        """Web form submission (most common)."""
        form_data = generate_support_message()
        self.client.post(
            "/support/submit",
            json=form_data,
            name="/support/submit"
        )

    @task(2)
    def gmail_webhook(self):
        """Simulate Gmail webhook (Pub/Sub notification)."""
        payload = {
            "message": {
                "data": f"history-{random.randint(1, 99999)}",
                "messageId": f"pubsub-{random.randint(1, 99999)}"
            },
            "subscription": "projects/test/subscriptions/gmail-push"
        }
        self.client.post(
            "/webhooks/gmail",
            json=payload,
            name="/webhooks/gmail"
        )

    @task(2)
    def whatsapp_webhook(self):
        """Simulate WhatsApp webhook (Twilio)."""
        data = {
            "MessageSid": f"SM{random.randint(100000, 999999)}",
            "From": f"whatsapp:+1{random.randint(1000000000, 9999999999)}",
            "Body": random.choice([
                "Help needed",
                "How do I...",
                "Issue with...",
                "Question about..."
            ]),
            "ProfileName": generate_random_name()
        }
        self.client.post(
            "/webhooks/whatsapp",
            data=data,
            name="/webhooks/whatsapp"
        )

    @task(1)
    def health_check(self):
        """Periodic health check."""
        self.client.get("/health", name="/health")


# =============================================================================
# Stress Test User
# =============================================================================

class StressTestUser(HttpUser):
    """
    High-frequency user for stress testing.
    Use with caution - generates significant load.
    """
    wait_time = between(0.1, 0.5)
    weight = 1

    @task
    def rapid_form_submission(self):
        """Rapid fire form submissions."""
        form_data = generate_support_message()
        self.client.post(
            "/support/submit",
            json=form_data,
            name="/stress/submit"
        )


# =============================================================================
# Event Handlers
# =============================================================================

@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Called when load test starts."""
    print("\n" + "=" * 60)
    print("LOAD TEST STARTING")
    print("=" * 60)
    print(f"Target: {environment.host}")
    print(f"Start time: {datetime.now().isoformat()}")
    print("=" * 60 + "\n")


@events.test_stop.add_listener
def on_test_stop(environment, result, **kwargs):
    """Called when load test stops."""
    print("\n" + "=" * 60)
    print("LOAD TEST COMPLETE")
    print("=" * 60)
    print(f"End time: {datetime.now().isoformat()}")

    # Print summary statistics
    stats = environment.stats
    print(f"\nTotal Requests: {stats.total.num_requests}")
    print(f"Total Failures: {stats.total.num_failures}")
    print(f"Failure Rate: {stats.total.num_failures / max(stats.total.num_requests, 1) * 100:.2f}%")
    print(f"Avg Response Time: {stats.total.avg_response_time:.2f}ms")
    print(f"Min Response Time: {stats.total.min_response_time:.2f}ms")
    print(f"Max Response Time: {stats.total.max_response_time:.2f}ms")

    # Print per-endpoint stats
    print("\n--- Per-Endpoint Stats ---")
    for name, stat in stats.entries.items():
        print(f"{name[1]}: {stat.num_requests} requests, {stat.avg_response_time:.2f}ms avg")

    print("=" * 60 + "\n")


@events.request.add_listener
def on_request(request_type, name, response_time, response_length, exception, **kwargs):
    """Called on each request - can be used for custom logging."""
    if exception:
        print(f"Request failed: {name} - {exception}")


# =============================================================================
# Configuration for Running
# =============================================================================

"""
To run load tests:

1. Install locust:
   pip install locust

2. Start Locust:
   locust -f production/tests/load_test.py --host=http://localhost:8000

3. Open browser to http://localhost:8089

4. Configure:
   - Number of users: 100
   - Ramp up: 10 users/second
   - Run time: 5m (or until satisfied)

Command line (headless):
   locust -f production/tests/load_test.py \
     --host=http://localhost:8000 \
     --headless \
     -u 100 \
     -r 10 \
     -t 5m \
     --html=report.html

For stress testing:
   locust -f production/tests/load_test.py \
     --host=http://localhost:8000 \
     --headless \
     -u 500 \
     -r 50 \
     -t 10m
"""


# =============================================================================
# Main Entry Point
# =============================================================================

if __name__ == "__main__":
    import os
    os.system("locust -f production/tests/load_test.py --host=http://localhost:8000")
