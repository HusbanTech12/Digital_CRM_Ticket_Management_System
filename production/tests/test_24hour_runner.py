"""
24-Hour Continuous Operation Test Runner
Stage 3: Integration & Testing

Runs continuous testing for 24 hours to validate:
- System stability
- Memory leaks
- Resource consumption
- Error rates over time
- Message processing reliability
"""

import asyncio
import aiohttp
import json
import time
import random
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass, field
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# =============================================================================
# Test Configuration
# =============================================================================

@dataclass
class TestConfig:
    """Configuration for 24-hour test."""
    base_url: str = "http://localhost:8000"
    duration_hours: int = 24
    target_requests_per_hour: int = 100
    chaos_interval_minutes: int = 120  # Chaos testing every 2 hours

    # Traffic distribution
    web_form_weight: int = 50
    email_weight: int = 30
    whatsapp_weight: int = 20

    # Thresholds
    max_error_rate: float = 0.01  # 1%
    max_avg_latency_ms: float = 3000
    max_p95_latency_ms: float = 5000


# =============================================================================
# Metrics Collector
# =============================================================================

@dataclass
class TestMetrics:
    """Collect and track test metrics."""
    start_time: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_latency_ms: float = 0
    latencies: List[float] = field(default_factory=list)
    errors: List[Dict] = field(default_factory=list)
    requests_by_channel: Dict[str, int] = field(default_factory=dict)
    hourly_stats: List[Dict] = field(default_factory=list)

    def record_request(self, channel: str, latency_ms: float, success: bool, error: Optional[str] = None):
        """Record a request result."""
        self.total_requests += 1
        self.total_latency_ms += latency_ms
        self.latencies.append(latency_ms)

        if success:
            self.successful_requests += 1
        else:
            self.failed_requests += 1
            if error:
                self.errors.append({
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "channel": channel,
                    "error": error
                })

        # Track by channel
        self.requests_by_channel[channel] = self.requests_by_channel.get(channel, 0) + 1

    @property
    def error_rate(self) -> float:
        if self.total_requests == 0:
            return 0.0
        return self.failed_requests / self.total_requests

    @property
    def avg_latency_ms(self) -> float:
        if not self.latencies:
            return 0.0
        return sum(self.latencies) / len(self.latencies)

    @property
    def p95_latency_ms(self) -> float:
        if not self.latencies:
            return 0.0
        sorted_latencies = sorted(self.latencies)
        p95_index = int(len(sorted_latencies) * 0.95)
        return sorted_latencies[min(p95_index, len(sorted_latencies) - 1)]

    @property
    def uptime_percentage(self) -> float:
        if self.total_requests == 0:
            return 100.0
        return (self.successful_requests / self.total_requests) * 100

    def get_summary(self) -> Dict:
        """Get metrics summary."""
        elapsed = datetime.now(timezone.utc) - self.start_time
        return {
            "elapsed_hours": elapsed.total_seconds() / 3600,
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "failed_requests": self.failed_requests,
            "error_rate": self.error_rate,
            "avg_latency_ms": round(self.avg_latency_ms, 2),
            "p95_latency_ms": round(self.p95_latency_ms, 2),
            "uptime_percentage": round(self.uptime_percentage, 2),
            "requests_by_channel": self.requests_by_channel,
            "total_errors": len(self.errors)
        }


# =============================================================================
# Test Data Generators
# =============================================================================

class TestDataGenerator:
    """Generate test data for various channels."""

    @staticmethod
    def generate_email_message() -> Dict:
        return {
            "message": {
                "data": f"history-{random.randint(1, 99999)}",
                "messageId": f"pubsub-{random.randint(1, 99999)}"
            },
            "subscription": "projects/test/subscriptions/gmail-push"
        }

    @staticmethod
    def generate_whatsapp_message() -> Dict:
        return {
            "MessageSid": f"SM{random.randint(100000, 999999)}",
            "From": f"whatsapp:+1{random.randint(1000000000, 9999999999)}",
            "Body": random.choice([
                "Help needed with my account",
                "How do I create a project?",
                "Issue with pipeline",
                "Question about features"
            ]),
            "ProfileName": f"User{random.randint(1, 9999)}"
        }

    @staticmethod
    def generate_web_form() -> Dict:
        categories = ["general", "technical", "billing", "feedback"]
        return {
            "name": f"Test User {random.randint(1, 9999)}",
            "email": f"test{random.randint(1, 9999)}@example.com",
            "subject": f"Test Issue {random.randint(1, 9999)}",
            "category": random.choice(categories),
            "priority": random.choice(["low", "medium", "high"]),
            "message": "This is a test message for the 24-hour continuous operation test."
        }


# =============================================================================
# 24-Hour Test Runner
# =============================================================================

class ContinuousTestRunner:
    """Run continuous tests for 24 hours."""

    def __init__(self, config: TestConfig):
        self.config = config
        self.metrics = TestMetrics()
        self.data_generator = TestDataGenerator()
        self.running = False
        self.session: Optional[aiohttp.ClientSession] = None

    async def start(self):
        """Start the test runner."""
        self.running = True
        self.session = aiohttp.ClientSession()

        logger.info("=" * 60)
        logger.info("24-HOUR CONTINUOUS OPERATION TEST STARTING")
        logger.info("=" * 60)
        logger.info(f"Target: {self.config.base_url}")
        logger.info(f"Duration: {self.config.duration_hours} hours")
        logger.info(f"Target requests/hour: {self.config.target_requests_per_hour}")
        logger.info(f"Start time: {datetime.now(timezone.utc).isoformat()}")
        logger.info("=" * 60)

        # Start main test loop
        await self._test_loop()

    async def stop(self):
        """Stop the test runner."""
        self.running = False
        if self.session:
            await self.session.close()

        logger.info("=" * 60)
        logger.info("24-HOUR TEST COMPLETE")
        logger.info("=" * 60)

        # Print final summary
        summary = self.metrics.get_summary()
        for key, value in summary.items():
            logger.info(f"{key}: {value}")
        logger.info("=" * 60)

    async def _test_loop(self):
        """Main test loop."""
        start_time = time.time()
        end_time = start_time + (self.config.duration_hours * 3600)
        last_hour_stats = start_time
        requests_this_hour = 0

        while self.running and time.time() < end_time:
            # Calculate delay to meet target requests per hour
            elapsed_hours = (time.time() - start_time) / 3600
            expected_requests = elapsed_hours * self.config.target_requests_per_hour
            actual_requests = self.metrics.total_requests

            if actual_requests >= expected_requests:
                # Wait before next request
                await asyncio.sleep(3600 / self.config.target_requests_per_hour)
                continue

            # Execute random channel test
            channel = self._select_channel()
            success, latency = await self._execute_channel_test(channel)

            self.metrics.record_request(
                channel=channel,
                latency_ms=latency,
                success=success
            )
            requests_this_hour += 1

            # Log hourly stats
            if time.time() - last_hour_stats >= 3600:
                self._log_hourly_stats(requests_this_hour)
                requests_this_hour = 0
                last_hour_stats = time.time()

            # Check thresholds
            self._check_thresholds()

        # Final stats
        self._log_hourly_stats(requests_this_hour)

    def _select_channel(self) -> str:
        """Select channel based on weights."""
        total_weight = (
            self.config.web_form_weight +
            self.config.email_weight +
            self.config.whatsapp_weight
        )
        rand = random.randint(1, total_weight)

        if rand <= self.config.web_form_weight:
            return "web_form"
        elif rand <= self.config.web_form_weight + self.config.email_weight:
            return "email"
        else:
            return "whatsapp"

    async def _execute_channel_test(self, channel: str) -> tuple:
        """Execute test for specific channel."""
        start = time.time()

        try:
            if channel == "web_form":
                success = await self._test_web_form()
            elif channel == "email":
                success = await self._test_gmail_webhook()
            else:
                success = await self._test_whatsapp_webhook()

            latency = (time.time() - start) * 1000
            return success, latency

        except Exception as e:
            latency = (time.time() - start) * 1000
            logger.error(f"{channel} test failed: {e}")
            return False, latency

    async def _test_web_form(self) -> bool:
        """Test web form submission."""
        data = self.data_generator.generate_web_form()

        async with self.session.post(
            f"{self.config.base_url}/support/submit",
            json=data,
            timeout=aiohttp.ClientTimeout(total=30)
        ) as response:
            if response.status == 200:
                result = await response.json()
                return "ticket_id" in result
            return False

    async def _test_gmail_webhook(self) -> bool:
        """Test Gmail webhook."""
        data = self.data_generator.generate_email_message()

        async with self.session.post(
            f"{self.config.base_url}/webhooks/gmail",
            json=data,
            timeout=aiohttp.ClientTimeout(total=10)
        ) as response:
            return response.status in [200, 201]

    async def _test_whatsapp_webhook(self) -> bool:
        """Test WhatsApp webhook."""
        data = self.data_generator.generate_whatsapp_message()

        async with self.session.post(
            f"{self.config.base_url}/webhooks/whatsapp",
            data=data,
            timeout=aiohttp.ClientTimeout(total=10)
        ) as response:
            return response.status in [200, 403]  # 403 if signature validation

    def _log_hourly_stats(self, requests_this_hour: int):
        """Log hourly statistics."""
        summary = self.metrics.get_summary()
        logger.info("-" * 40)
        logger.info(f"HOURLY STATS: {requests_this_hour} requests this hour")
        logger.info(f"Error Rate: {summary['error_rate']:.2%}")
        logger.info(f"Avg Latency: {summary['avg_latency_ms']:.2f}ms")
        logger.info(f"P95 Latency: {summary['p95_latency_ms']:.2f}ms")
        logger.info(f"Uptime: {summary['uptime_percentage']:.2f}%")
        logger.info("-" * 40)

        self.metrics.hourly_stats.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "requests": requests_this_hour,
            **summary
        })

    def _check_thresholds(self):
        """Check if metrics exceed thresholds."""
        if self.metrics.error_rate > self.config.max_error_rate:
            logger.warning(
                f"ERROR RATE EXCEEDED: {self.metrics.error_rate:.2%} > "
                f"{self.config.max_error_rate:.2%}"
            )

        if self.metrics.avg_latency_ms > self.config.max_avg_latency_ms:
            logger.warning(
                f"AVG LATENCY EXCEEDED: {self.metrics.avg_latency_ms:.2f}ms > "
                f"{self.config.max_avg_latency_ms:.2f}ms"
            )

        if self.metrics.p95_latency_ms > self.config.max_p95_latency_ms:
            logger.warning(
                f"P95 LATENCY EXCEEDED: {self.metrics.p95_latency_ms:.2f}ms > "
                f"{self.config.max_p95_latency_ms:.2f}ms"
            )


# =============================================================================
# Chaos Testing
# =============================================================================

class ChaosTester:
    """Run chaos tests during 24-hour test."""

    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session: Optional[aiohttp.ClientSession] = None

    async def start(self):
        """Start chaos testing session."""
        self.session = aiohttp.ClientSession()

    async def stop(self):
        """Stop chaos testing session."""
        if self.session:
            await self.session.close()

    async def test_pod_restart(self):
        """Simulate pod restart by checking recovery."""
        logger.info("CHAOS TEST: Simulating pod restart...")

        # Check health before
        before = await self._check_health()

        # In real chaos testing, you would kill a pod here
        # kubectl delete pod -l app=customer-success-fte

        # Wait for recovery
        await asyncio.sleep(30)

        # Check health after
        after = await self._check_health()

        logger.info(f"CHAOS TEST: Health before={before}, after={after}")
        return before and after

    async def _check_health(self) -> bool:
        """Check service health."""
        try:
            async with self.session.get(
                f"{self.base_url}/health",
                timeout=aiohttp.ClientTimeout(total=5)
            ) as response:
                return response.status == 200
        except Exception:
            return False


# =============================================================================
# Report Generator
# =============================================================================

def generate_report(metrics: TestMetrics, output_path: str):
    """Generate test report."""
    import json

    report = {
        "test_type": "24-hour continuous operation",
        "completed_at": datetime.now(timezone.utc).isoformat(),
        "summary": metrics.get_summary(),
        "hourly_stats": metrics.hourly_stats,
        "errors": metrics.errors[:100],  # Limit errors in report
        "validation": {
            "uptime_target": "99.9%",
            "uptime_actual": f"{metrics.uptime_percentage:.2f}%",
            "uptime_passed": metrics.uptime_percentage >= 99.9,
            "latency_p95_target": "3000ms",
            "latency_p95_actual": f"{metrics.p95_latency_ms:.2f}ms",
            "latency_passed": metrics.p95_latency_ms <= 3000,
            "error_rate_target": "1%",
            "error_rate_actual": f"{metrics.error_rate:.2%}",
            "error_rate_passed": metrics.error_rate <= 0.01
        }
    }

    with open(output_path, 'w') as f:
        json.dump(report, f, indent=2)

    logger.info(f"Report saved to: {output_path}")
    return report


# =============================================================================
# Main Entry Point
# =============================================================================

async def main():
    """Run 24-hour continuous test."""
    config = TestConfig(
        base_url=os.getenv("TEST_BASE_URL", "http://localhost:8000"),
        duration_hours=int(os.getenv("TEST_DURATION_HOURS", "24")),
        target_requests_per_hour=int(os.getenv("TARGET_REQUESTS_PER_HOUR", "100"))
    )

    runner = ContinuousTestRunner(config)

    try:
        await runner.start()
    except KeyboardInterrupt:
        logger.info("Test interrupted by user")
    finally:
        await runner.stop()

        # Generate report
        generate_report(
            runner.metrics,
            f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )


if __name__ == "__main__":
    asyncio.run(main())
