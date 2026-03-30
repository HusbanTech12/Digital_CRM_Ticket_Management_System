"""
Kafka Event Streaming for Customer Success FTE.
Provides producers and consumers for event-driven architecture.
"""

from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
from aiokafka.errors import KafkaError
import json
import os
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional, Callable
from enum import Enum

logger = logging.getLogger(__name__)


# =============================================================================
# Topic Definitions
# =============================================================================

class Topic(str, Enum):
    """Kafka topics for FTE event streaming."""
    # Incoming tickets from all channels
    TICKETS_INCOMING = "fte.tickets.incoming"

    # Channel-specific inbound
    EMAIL_INBOUND = "fte.channels.email.inbound"
    WHATSAPP_INBOUND = "fte.channels.whatsapp.inbound"
    WEBFORM_INBOUND = "fte.channels.webform.inbound"

    # Channel-specific outbound
    EMAIL_OUTBOUND = "fte.channels.email.outbound"
    WHATSAPP_OUTBOUND = "fte.channels.whatsapp.outbound"

    # Agent processing
    AGENT_PROCESSING = "fte.agent.processing"
    AGENT_RESPONSES = "fte.agent.responses"

    # Escalations
    ESCALATIONS = "fte.escalations"

    # Metrics and monitoring
    METRICS = "fte.metrics"
    ERRORS = "fte.errors"

    # Dead letter queue for failed processing
    DLQ = "fte.dlq"


# Kafka configuration
KAFKA_BOOTSTRAP_SERVERS = os.getenv(
    "KAFKA_BOOTSTRAP_SERVERS",
    "localhost:9092"
)

KAFKA_SECURITY_PROTOCOL = os.getenv("KAFKA_SECURITY_PROTOCOL", "PLAINTEXT")
KAFKA_SASL_MECHANISM = os.getenv("KAFKA_SASL_MECHANISM", "PLAIN")
KAFKA_USERNAME = os.getenv("KAFKA_USERNAME")
KAFKA_PASSWORD = os.getenv("KAFKA_PASSWORD")


def get_kafka_config() -> dict:
    """Get Kafka configuration based on environment."""
    config = {
        "bootstrap_servers": KAFKA_BOOTSTRAP_SERVERS,
    }

    # Add security if configured
    if KAFKA_USERNAME and KAFKA_PASSWORD:
        config.update({
            "security_protocol": KAFKA_SECURITY_PROTOCOL,
            "sasl_mechanism": KAFKA_SASL_MECHANISM,
            "sasl_plain_username": KAFKA_USERNAME,
            "sasl_plain_password": KAFKA_PASSWORD
        })

    return config


# =============================================================================
# Kafka Producer
# =============================================================================

class FTEKafkaProducer:
    """Async Kafka producer for FTE events."""

    def __init__(self):
        self.producer: Optional[AIOKafkaProducer] = None
        self._config = get_kafka_config()

    async def start(self):
        """Initialize and start the producer."""
        if self.producer is None:
            self.producer = AIOKafkaProducer(
                **self._config,
                value_serializer=lambda v: json.dumps(v, default=str).encode('utf-8'),
                key_serializer=lambda k: k.encode('utf-8') if k else None,
                acks='all',  # Wait for all replicas to acknowledge
                retries=3,
                retry_backoff_ms=100
            )
            await self.producer.start()
            logger.info("Kafka producer started")

    async def stop(self):
        """Stop the producer."""
        if self.producer:
            await self.producer.stop()
            self.producer = None
            logger.info("Kafka producer stopped")

    async def publish(
        self,
        topic: str,
        event: Dict,
        key: Optional[str] = None
    ):
        """
        Publish an event to a Kafka topic.

        Args:
            topic: Kafka topic name
            event: Event data (will be JSON serialized)
            key: Optional partition key
        """
        if not self.producer:
            await self.start()

        # Add timestamp to event
        event["timestamp"] = datetime.now(timezone.utc).isoformat()

        try:
            future = await self.producer.send_and_wait(
                topic,
                value=event,
                key=key
            )
            logger.debug(f"Published event to {topic} at offset {future.offset}")
            return future

        except KafkaError as e:
            logger.error(f"Failed to publish to {topic}: {e}")
            # Publish to DLQ
            await self.publish_to_dlq(topic, event, str(e))
            raise

    async def publish_batch(
        self,
        topic: str,
        events: List[Dict],
        keys: Optional[List[str]] = None
    ):
        """Publish multiple events to a topic."""
        if not self.producer:
            await self.start()

        try:
            for i, event in enumerate(events):
                event["timestamp"] = datetime.now(timezone.utc).isoformat()
                key = keys[i] if keys and i < len(keys) else None
                await self.producer.send_and_wait(topic, value=event, key=key)

            logger.info(f"Published {len(events)} events to {topic}")

        except KafkaError as e:
            logger.error(f"Failed to publish batch to {topic}: {e}")
            raise

    async def publish_to_dlq(
        self,
        original_topic: str,
        event: Dict,
        error: str
    ):
        """Publish failed event to dead letter queue."""
        dlq_event = {
            "original_topic": original_topic,
            "original_event": event,
            "error": error,
            "failed_at": datetime.now(timezone.utc).isoformat()
        }
        try:
            await self.publish(Topic.DLQ, dlq_event)
        except Exception as e:
            logger.error(f"Failed to publish to DLQ: {e}")


# =============================================================================
# Kafka Consumer
# =============================================================================

class FTEKafkaConsumer:
    """Async Kafka consumer for FTE events."""

    def __init__(
        self,
        topics: List[str],
        group_id: str,
        auto_commit: bool = True,
        earliest: bool = False
    ):
        self.topics = topics
        self.group_id = group_id
        self.consumer: Optional[AIOKafkaConsumer] = None
        self._config = get_kafka_config()
        self._auto_commit = auto_commit
        self._earliest = earliest

    async def start(self):
        """Initialize and start the consumer."""
        if self.consumer is None:
            self.consumer = AIOKafkaConsumer(
                *self.topics,
                **self._config,
                group_id=self.group_id,
                auto_offset_reset='earliest' if self._earliest else 'latest',
                enable_auto_commit=self._auto_commit,
                value_deserializer=lambda v: json.loads(v.decode('utf-8')),
                key_deserializer=lambda k: k.decode('utf-8') if k else None,
                consumer_timeout_ms=10000,  # 10 seconds timeout for empty batches
                max_poll_records=100,
                session_timeout_ms=30000,
                heartbeat_interval_ms=10000
            )
            await self.consumer.start()
            logger.info(f"Kafka consumer started for topics: {self.topics}")

    async def stop(self):
        """Stop the consumer."""
        if self.consumer:
            await self.consumer.stop()
            self.consumer = None
            logger.info("Kafka consumer stopped")

    async def consume(
        self,
        handler: Callable,
        batch_size: int = 1
    ):
        """
        Consume messages and call handler for each.

        Args:
            handler: Async function to call with (topic, message)
            batch_size: Number of messages to process before committing
        """
        if not self.consumer:
            await self.start()

        batch = []
        batch_topics = []

        try:
            async for msg in self.consumer:
                batch.append((msg.topic, msg.value))
                batch_topics.append(msg.topic)

                # Process batch when full
                if len(batch) >= batch_size:
                    await self._process_batch(batch, handler)
                    batch = []
                    batch_topics = []

            # Process remaining messages
            if batch:
                await self._process_batch(batch, handler)

        except Exception as e:
            logger.error(f"Consumer error: {e}")
            raise
        finally:
            # Commit any remaining offsets
            if self.consumer and self._auto_commit:
                await self.consumer.commit()

    async def _process_batch(
        self,
        batch: List[tuple],
        handler: Callable
    ):
        """Process a batch of messages."""
        for topic, message in batch:
            try:
                await handler(topic, message)
            except Exception as e:
                logger.error(f"Handler error for {topic}: {e}")
                # Publish to DLQ
                producer = FTEKafkaProducer()
                await producer.start()
                await producer.publish_to_dlq(topic, message, str(e))
                await producer.stop()

        # Commit offsets after batch
        if self.consumer and self._auto_commit:
            await self.consumer.commit()

    async def get_one(self, timeout_ms: int = 5000) -> Optional[tuple]:
        """Get a single message with timeout."""
        if not self.consumer:
            await self.start()

        try:
            msg = await self.consumer.getone(timeout_ms=timeout_ms)
            if msg:
                return (msg.topic, msg.value)
        except Exception:
            pass

        return None


# =============================================================================
# Event Publishers (Convenience Functions)
# =============================================================================

async def publish_ticket_incoming(ticket_data: Dict):
    """Publish incoming ticket event."""
    producer = FTEKafkaProducer()
    await producer.start()
    await producer.publish(
        Topic.TICKETS_INCOMING,
        ticket_data,
        key=ticket_data.get('channel_message_id', '')
    )
    await producer.stop()


async def publish_channel_inbound(channel: str, message_data: Dict):
    """Publish channel-specific inbound message."""
    producer = FTEKafkaProducer()
    await producer.start()

    topic_map = {
        'email': Topic.EMAIL_INBOUND,
        'whatsapp': Topic.WHATSAPP_INBOUND,
        'web_form': Topic.WEBFORM_INBOUND
    }

    topic = topic_map.get(channel, Topic.TICKETS_INCOMING)
    await producer.publish(topic, message_data)
    await producer.stop()


async def publish_escalation(escalation_data: Dict):
    """Publish escalation event."""
    producer = FTEKafkaProducer()
    await producer.start()
    await producer.publish(
        Topic.ESCALATIONS,
        escalation_data,
        key=escalation_data.get('ticket_id', '')
    )
    await producer.stop()


async def publish_metrics(metric_data: Dict):
    """Publish metrics event."""
    producer = FTEKafkaProducer()
    await producer.start()
    await producer.publish(Topic.METRICS, metric_data)
    await producer.stop()


async def publish_error(error_data: Dict):
    """Publish error event."""
    producer = FTEKafkaProducer()
    await producer.start()
    await producer.publish(Topic.ERRORS, error_data)
    await producer.stop()


# =============================================================================
# Topic Creation (for development)
# =============================================================================

async def create_topics():
    """Create all FTE topics if they don't exist."""
    from aiokafka.admin import AIOKafkaAdminClient, NewTopic

    admin_client = AIOKafkaAdminClient(**get_kafka_config())
    await admin_client.start()

    try:
        topics = []
        for topic in Topic:
            # Create with 3 partitions and replication factor of 1 for local dev
            new_topic = NewTopic(
                name=topic.value,
                num_partitions=3,
                replication_factor=1,
                topic_configs={
                    'retention.ms': '604800000',  # 7 days
                    'cleanup.policy': 'delete'
                }
            )
            topics.append(new_topic)

        await admin_client.create_topics(new_topics=topics, validate_only=False)
        logger.info(f"Created {len(topics)} Kafka topics")

    except Exception as e:
        # Topics may already exist
        logger.info(f"Topic creation status: {e}")

    finally:
        await admin_client.close()


# =============================================================================
# Main Entry Point
# =============================================================================

if __name__ == "__main__":
    import asyncio

    async def test_kafka():
        """Test Kafka producer and consumer."""
        print("=" * 60)
        print("Kafka Event Streaming - Test")
        print("=" * 60)

        # Create topics
        print("\nCreating topics...")
        await create_topics()

        # Test producer
        print("\nTesting producer...")
        producer = FTEKafkaProducer()
        await producer.start()

        test_event = {
            "test": "hello",
            "channel": "email",
            "message": "Test message"
        }

        await producer.publish(Topic.TICKETS_INCOMING, test_event)
        print(f"Published event to {Topic.TICKETS_INCOMING}")

        await producer.stop()
        print("Producer stopped")

        # Test consumer
        print("\nTesting consumer (will wait 5 seconds)...")
        consumer = FTEKafkaConsumer(
            topics=[Topic.TICKETS_INCOMING],
            group_id="test-consumer-group",
            earliest=True
        )

        async def handler(topic, message):
            print(f"Received from {topic}: {message}")

        # Consume for 5 seconds
        import asyncio
        try:
            await asyncio.wait_for(
                consumer.consume(handler),
                timeout=5.0
            )
        except asyncio.TimeoutError:
            print("Consumer timeout (expected)")

        await consumer.stop()
        print("Consumer stopped")

        print("\nTest complete!")

    asyncio.run(test_kafka())
