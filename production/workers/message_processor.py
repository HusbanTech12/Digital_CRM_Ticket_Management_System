"""
Unified Message Processor for Customer Success FTE.
Kafka consumer that processes incoming messages through the AI agent.
"""

import asyncio
import logging
from datetime import datetime, timezone
from typing import Dict, Optional
import os

from production.workers.kafka_client import (
    FTEKafkaConsumer,
    FTEKafkaProducer,
    Topic,
    publish_ticket_incoming,
    publish_metrics,
    publish_error
)
from production.agent.customer_success_agent import (
    run_agent,
    customer_success_agent
)
from production.database import queries as db

logger = logging.getLogger(__name__)


# =============================================================================
# Message Processor Configuration
# =============================================================================

class ProcessorConfig:
    """Configuration for message processor."""

    # Kafka settings
    KAFKA_GROUP_ID = os.getenv("KAFKA_GROUP_ID", "fte-message-processor")
    KAFKA_TOPICS = [
        Topic.TICKETS_INCOMING.value,
        Topic.EMAIL_INBOUND.value,
        Topic.WHATSAPP_INBOUND.value,
        Topic.WEBFORM_INBOUND.value
    ]

    # Processing settings
    MAX_RETRIES = 3
    RETRY_DELAY_MS = 1000
    BATCH_SIZE = 10

    # Metrics
    METRICS_BATCH_SIZE = 100


# =============================================================================
# Unified Message Processor
# =============================================================================

class UnifiedMessageProcessor:
    """
    Process incoming messages from all channels through the FTE agent.

    This is the main worker that:
    1. Consumes messages from Kafka
    2. Resolves/creates customers
    3. Creates conversations
    4. Runs the AI agent
    5. Stores responses
    6. Publishes metrics
    """

    def __init__(self):
        self.producer: Optional[FTEKafkaProducer] = None
        self.consumer: Optional[FTEKafkaConsumer] = None
        self._running = False
        self._metrics_buffer = []
        self._processed_count = 0
        self._error_count = 0

    async def start(self):
        """Start the message processor."""
        logger.info("Starting message processor...")

        # Initialize producer
        self.producer = FTEKafkaProducer()
        await self.producer.start()

        # Initialize consumer
        self.consumer = FTEKafkaConsumer(
            topics=ProcessorConfig.KAFKA_TOPICS,
            group_id=ProcessorConfig.KAFKA_GROUP_ID,
            auto_commit=False,  # Manual commit for reliability
            earliest=False
        )
        await self.consumer.start()

        self._running = True
        logger.info("Message processor started")

        # Start processing
        await self._process_loop()

    async def stop(self):
        """Stop the message processor."""
        logger.info("Stopping message processor...")
        self._running = False

        # Flush metrics
        await self._flush_metrics()

        # Close connections
        if self.consumer:
            await self.consumer.stop()
        if self.producer:
            await self.producer.stop()

        logger.info(f"Message processor stopped. Processed: {self._processed_count}, Errors: {self._error_count}")

    async def _process_loop(self):
        """Main processing loop."""
        batch = []

        while self._running:
            try:
                # Get message with timeout
                result = await self.consumer.get_one(timeout_ms=5000)

                if result:
                    topic, message = result
                    batch.append((topic, message))

                    # Process batch when full
                    if len(batch) >= ProcessorConfig.BATCH_SIZE:
                        await self._process_batch(batch)
                        batch = []
                else:
                    # No message, process any pending batch
                    if batch:
                        await self._process_batch(batch)
                        batch = []

            except Exception as e:
                logger.error(f"Process loop error: {e}")
                await asyncio.sleep(1)  # Back off on error

        # Process remaining messages
        if batch:
            await self._process_batch(batch)

    async def _process_batch(self, batch: list):
        """Process a batch of messages."""
        for topic, message in batch:
            await self._process_message(topic, message)

    async def _process_message(self, topic: str, message: Dict):
        """
        Process a single incoming message.

        Flow:
        1. Extract channel and customer info
        2. Resolve/create customer
        3. Get/create conversation
        4. Store incoming message
        5. Run AI agent
        6. Store agent response
        7. Publish metrics
        """
        start_time = datetime.now(timezone.utc)
        retry_count = 0

        while retry_count <= ProcessorConfig.MAX_RETRIES:
            try:
                # Extract channel
                channel = message.get('channel', 'email')
                channel_message_id = message.get('channel_message_id', '')

                logger.info(f"Processing {channel} message: {channel_message_id}")

                # Step 1: Resolve or create customer
                customer_id = await self._resolve_customer(message)
                if not customer_id:
                    logger.error(f"Could not resolve customer for message: {channel_message_id}")
                    await self._handle_error(message, "Could not resolve customer")
                    return

                # Step 2: Get or create conversation
                conversation_id = await self._get_or_create_conversation(
                    customer_id=customer_id,
                    channel=channel,
                    message=message
                )

                # Step 3: Store incoming message
                await self._store_incoming_message(
                    conversation_id=conversation_id,
                    channel=channel,
                    message=message
                )

                # Step 4: Run AI agent
                agent_result = await run_agent(
                    message=message.get('content', ''),
                    customer_id=customer_id,
                    channel=channel,
                    conversation_id=conversation_id
                )

                # Step 5: Store agent response
                if agent_result.get('success'):
                    await self._store_agent_response(
                        conversation_id=conversation_id,
                        channel=channel,
                        result=agent_result
                    )

                    # Step 6: Actually send response via channel
                    await self._send_channel_response(
                        message=message,
                        response=agent_result.get('output', ''),
                        channel=channel
                    )

                # Step 7: Record metrics
                processing_time = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
                await self._record_metric(
                    event_type='message_processed',
                    channel=channel,
                    latency_ms=processing_time,
                    success=agent_result.get('success', False),
                    escalated=self._check_escalation(agent_result)
                )

                self._processed_count += 1
                logger.info(f"Processed {channel} message in {processing_time:.0f}ms")
                return  # Success, exit retry loop

            except Exception as e:
                retry_count += 1
                logger.error(f"Processing error (attempt {retry_count}): {e}")

                if retry_count > ProcessorConfig.MAX_RETRIES:
                    await self._handle_error(message, str(e))
                    self._error_count += 1
                else:
                    await asyncio.sleep(ProcessorConfig.RETRY_DELAY_MS * retry_count / 1000)

    async def _resolve_customer(self, message: Dict) -> Optional[str]:
        """Resolve or create customer from message identifiers."""
        email = message.get('customer_email')
        phone = message.get('customer_phone')
        name = message.get('customer_name')

        return await db.get_or_create_customer(
            email=email,
            phone=phone,
            name=name
        )

    async def _get_or_create_conversation(
        self,
        customer_id: str,
        channel: str,
        message: Dict
    ) -> str:
        """Get active conversation or create new one."""
        # Check for active conversation (within last 24 hours)
        conversation_id = await db.get_active_conversation(customer_id, hours=24)

        if not conversation_id:
            # Create new conversation
            conversation_id = await db.create_conversation(customer_id, channel)
            logger.info(f"Created new conversation: {conversation_id}")

        return conversation_id

    async def _store_incoming_message(
        self,
        conversation_id: str,
        channel: str,
        message: Dict
    ):
        """Store incoming customer message."""
        await db.add_message(
            conversation_id=conversation_id,
            channel=channel,
            direction='inbound',
            role='customer',
            content=message.get('content', ''),
            sentiment_score=0.5,  # Would calculate from message
            topics=[],  # Would extract from message
            channel_message_id=message.get('channel_message_id')
        )

    async def _store_agent_response(
        self,
        conversation_id: str,
        channel: str,
        result: Dict
    ):
        """Store agent response message."""
        await db.add_message(
            conversation_id=conversation_id,
            channel=channel,
            direction='outbound',
            role='agent',
            content=result.get('output', ''),
            sentiment_score=0.7,  # Agent responses are positive
            tool_calls=result.get('tool_calls', []),
            latency_ms=0  # Would calculate
        )

    async def _send_channel_response(
        self,
        message: Dict,
        response: str,
        channel: str
    ):
        """Send response via appropriate channel."""
        # In production, this would call the actual channel handlers
        # For now, we just log and publish to channel outbound topic

        logger.info(f"Sending {channel} response")

        # Publish to channel outbound topic for actual sending
        outbound_event = {
            'channel': channel,
            'recipient': message.get('customer_email') or message.get('customer_phone'),
            'content': response,
            'channel_message_id': message.get('channel_message_id'),
            'conversation_id': message.get('conversation_id')
        }

        await self.producer.publish(
            f'fte.channels.{channel}.outbound',
            outbound_event
        )

    async def _record_metric(
        self,
        event_type: str,
        channel: str,
        latency_ms: float,
        success: bool,
        escalated: bool
    ):
        """Record processing metric."""
        metric = {
            'event_type': event_type,
            'channel': channel,
            'latency_ms': latency_ms,
            'success': success,
            'escalated': escalated,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }

        self._metrics_buffer.append(metric)

        # Flush metrics when buffer is full
        if len(self._metrics_buffer) >= METRICS_BATCH_SIZE:
            await self._flush_metrics()

    async def _flush_metrics(self):
        """Flush metrics buffer to Kafka."""
        if self._metrics_buffer and self.producer:
            for metric in self._metrics_buffer:
                await self.producer.publish(Topic.METRICS.value, metric)
            self._metrics_buffer = []
            logger.debug(f"Flushed {len(self._metrics_buffer)} metrics")

    def _check_escalation(self, agent_result: Dict) -> bool:
        """Check if agent result indicates escalation."""
        tool_calls = agent_result.get('tool_calls', [])
        for call in tool_calls:
            if call.get('name') == 'escalate_to_human':
                return True
        return False

    async def _handle_error(self, message: Dict, error: str):
        """Handle processing error - send to DLQ and notify."""
        logger.error(f"Message processing failed: {error}")

        # Publish to DLQ
        dlq_event = {
            'original_message': message,
            'error': error,
            'failed_at': datetime.now(timezone.utc).isoformat()
        }
        await self.producer.publish(Topic.DLQ.value, dlq_event)

        # Publish error event
        await publish_error({
            'message_id': message.get('channel_message_id'),
            'channel': message.get('channel'),
            'error': error
        })


# =============================================================================
# Standalone Runner
# =============================================================================

async def run_processor():
    """Run the message processor as a standalone service."""
    processor = UnifiedMessageProcessor()

    # Setup signal handlers
    import signal

    def signal_handler(sig, frame):
        logger.info(f"Received signal {sig}, shutting down...")
        asyncio.create_task(processor.stop())

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        await processor.start()
    except Exception as e:
        logger.error(f"Processor failed: {e}")
        await processor.stop()
        raise


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    asyncio.run(run_processor())
