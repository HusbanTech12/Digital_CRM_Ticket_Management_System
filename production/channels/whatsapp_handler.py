"""
WhatsApp Integration Handler for Customer Success FTE.
Handles incoming/outgoing messages via Twilio WhatsApp API.
"""

import os
import re
from datetime import datetime, timezone
from typing import Dict, List, Optional
from twilio.rest import Client
from twilio.request_validator import RequestValidator
from fastapi import Request, HTTPException
import logging

logger = logging.getLogger(__name__)


class WhatsAppHandler:
    """Handler for WhatsApp messaging via Twilio."""

    def __init__(self):
        self.account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        self.auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        self.whatsapp_number = os.getenv('TWILIO_WHATSAPP_NUMBER', 'whatsapp:+14155238886')
        self.client: Optional[Client] = None
        self.validator: Optional[RequestValidator] = None
        self._initialize_client()

    def _initialize_client(self):
        """Initialize Twilio client."""
        if self.account_sid and self.auth_token:
            try:
                self.client = Client(self.account_sid, self.auth_token)
                self.validator = RequestValidator(self.auth_token)
                logger.info("Twilio WhatsApp client initialized")
            except Exception as e:
                logger.warning(f"Twilio client initialization failed: {e}")
        else:
            logger.info("WhatsApp handler initialized (credentials required for production)")

    async def validate_webhook(self, request: Request) -> bool:
        """
        Validate incoming Twilio webhook signature.
        This ensures the webhook is actually from Twilio.
        """
        if not self.validator:
            # In development, skip validation
            logger.debug("Skipping webhook validation (dev mode)")
            return True

        signature = request.headers.get('X-Twilio-Signature', '')
        url = str(request.url)

        # Get form data for validation
        form_data = await request.form()
        params = {k: v for k, v in form_data.items()}

        is_valid = self.validator.validate(url, params, signature)

        if not is_valid:
            logger.warning(f"Invalid Twilio webhook signature from {url}")

        return is_valid

    async def process_webhook(self, form_data: Dict) -> Optional[Dict]:
        """
        Process incoming WhatsApp message from Twilio webhook.
        Returns normalized message object.
        """
        # Check if this is a message (not a status update)
        message_sid = form_data.get('MessageSid')
        if not message_sid:
            logger.debug("Received non-message webhook")
            return None

        # Extract message components
        from_number = form_data.get('From', '').replace('whatsapp:', '')
        body = form_data.get('Body', '')
        profile_name = form_data.get('ProfileName')

        # Handle media messages
        num_media = int(form_data.get('NumMedia', '0'))
        media_urls = []
        if num_media > 0:
            for i in range(num_media):
                media_url = form_data.get(f'MediaUrl{i}')
                if media_url:
                    media_urls.append(media_url)

        # Create normalized message
        message = {
            'channel': 'whatsapp',
            'channel_message_id': message_sid,
            'customer_phone': from_number,
            'customer_name': profile_name,
            'content': body,
            'received_at': datetime.now(timezone.utc).isoformat(),
            'metadata': {
                'num_media': num_media,
                'media_urls': media_urls,
                'profile_name': profile_name,
                'wa_id': form_data.get('WaId'),
                'from': form_data.get('From'),
                'to': form_data.get('To'),
                'status': form_data.get('SmsStatus')
            }
        }

        logger.info(f"WhatsApp message received from {from_number}: {body[:50]}...")
        return message

    async def send_message(
        self,
        to_phone: str,
        body: str,
        media_url: Optional[str] = None
    ) -> Dict:
        """
        Send WhatsApp message via Twilio.
        Returns delivery status and message SID.
        """
        # Ensure phone number is in WhatsApp format
        if not to_phone.startswith('whatsapp:'):
            to_phone = f'whatsapp:{to_phone}'

        if not self.client:
            # Development mode
            logger.info(f"[DEV MODE] Would send WhatsApp to {to_phone}: {body[:50]}...")
            return {
                'channel_message_id': f'dev-{datetime.now(timezone.utc).isoformat()}',
                'delivery_status': 'sent_dev_mode'
            }

        try:
            # Build message with optional media
            message_kwargs = {
                'body': body,
                'from_': self.whatsapp_number,
                'to': to_phone
            }

            if media_url:
                message_kwargs['media_url'] = media_url

            message = self.client.messages.create(**message_kwargs)

            logger.info(f"WhatsApp message sent: {message.sid}")
            return {
                'channel_message_id': message.sid,
                'delivery_status': message.status,  # 'queued', 'sent', 'delivered', 'failed'
                'date_created': message.date_created.isoformat() if message.date_created else None
            }

        except Exception as e:
            logger.error(f"WhatsApp send failed: {e}")
            return {
                'error': str(e),
                'delivery_status': 'failed'
            }

    async def send_media_message(
        self,
        to_phone: str,
        body: str,
        media_url: str,
        media_type: str = 'image'
    ) -> Dict:
        """
        Send WhatsApp message with media attachment.
        media_type: 'image', 'video', 'audio', 'document'
        """
        # Ensure phone number is in WhatsApp format
        if not to_phone.startswith('whatsapp:'):
            to_phone = f'whatsapp:{to_phone}'

        if not self.client:
            logger.info(f"[DEV MODE] Would send WhatsApp media to {to_phone}")
            return {
                'channel_message_id': f'dev-{datetime.now(timezone.utc).isoformat()}',
                'delivery_status': 'sent_dev_mode'
            }

        try:
            message = self.client.messages.create(
                body=body,
                from_=self.whatsapp_number,
                to=to_phone,
                media_url=media_url
            )

            logger.info(f"WhatsApp media message sent: {message.sid}")
            return {
                'channel_message_id': message.sid,
                'delivery_status': message.status
            }

        except Exception as e:
            logger.error(f"WhatsApp media send failed: {e}")
            return {
                'error': str(e),
                'delivery_status': 'failed'
            }

    def format_response(self, response: str, max_length: int = 1600) -> List[str]:
        """
        Format and split response for WhatsApp.
        WhatsApp has a 1600 character limit per message.
        Returns list of messages if splitting is needed.
        """
        if len(response) <= max_length:
            return [response]

        messages = []
        remaining = response

        while remaining:
            if len(remaining) <= max_length:
                messages.append(remaining)
                break

            # Find a good break point (sentence or word boundary)
            break_point = remaining.rfind('. ', 0, max_length)
            if break_point == -1:
                break_point = remaining.rfind(' ', 0, max_length)
            if break_point == -1:
                break_point = max_length

            messages.append(remaining[:break_point + 1].strip())
            remaining = remaining[break_point + 1:].strip()

        return messages

    async def send_conversation(
        self,
        to_phone: str,
        messages: List[str],
        delay_seconds: int = 1
    ) -> List[Dict]:
        """
        Send multiple messages as a conversation.
        Useful for long responses split into multiple messages.
        """
        results = []
        for i, message in enumerate(messages):
            result = await self.send_message(to_phone, message)
            results.append(result)

            # Add delay between messages (except for last)
            if i < len(messages) - 1 and delay_seconds > 0:
                import asyncio
                await asyncio.sleep(delay_seconds)

        return results

    async def get_message_status(self, message_sid: str) -> Optional[str]:
        """
        Get delivery status of a message.
        Returns: 'queued', 'sent', 'delivered', 'read', 'failed', 'undelivered'
        """
        if not self.client:
            return None

        try:
            message = self.client.messages(message_sid).fetch()
            return message.status
        except Exception as e:
            logger.error(f"Failed to get message status: {e}")
            return None

    async def update_delivery_status(
        self,
        message_sid: str,
        status: str
    ) -> bool:
        """
        Update message delivery status in database.
        Called by status webhook handler.
        """
        # This would update the messages table in production
        logger.info(f"Message {message_sid} status: {status}")

        # Map Twilio status to our internal status
        status_mapping = {
            'queued': 'pending',
            'sent': 'sent',
            'delivered': 'delivered',
            'read': 'delivered',
            'failed': 'failed',
            'undelivered': 'failed'
        }

        internal_status = status_mapping.get(status, 'pending')

        # In production, update the database:
        # await db.execute(
        #     "UPDATE messages SET delivery_status = $1 WHERE channel_message_id = $2",
        #     internal_status, message_sid
        # )

        return True


# Global handler instance
whatsapp_handler = WhatsAppHandler()


# Convenience functions for use in other modules
async def process_whatsapp_webhook(form_data: Dict) -> Optional[Dict]:
    """Process WhatsApp webhook."""
    return await whatsapp_handler.process_webhook(form_data)


async def send_whatsapp_message(to_phone: str, body: str) -> Dict:
    """Send WhatsApp message."""
    return await whatsapp_handler.send_message(to_phone, body)


async def validate_whatsapp_webhook(request: Request) -> bool:
    """Validate WhatsApp webhook."""
    return await whatsapp_handler.validate_webhook(request)


# FastAPI webhook endpoint helper
async def handle_whatsapp_webhook(request: Request) -> Dict:
    """
    Handle incoming WhatsApp webhook from Twilio.
    Returns TwiML response (empty = no immediate reply).
    """
    # Validate webhook
    if not await validate_whatsapp_webhook(request):
        raise HTTPException(status_code=403, detail="Invalid signature")

    # Get form data
    form_data = await request.form()
    message_dict = dict(form_data)

    # Process message
    message = await process_whatsapp_webhook(message_dict)

    if message:
        # In production, publish to Kafka for async processing
        # await kafka_producer.publish('fte.tickets.incoming', message)
        logger.info(f"WhatsApp message queued for processing: {message['channel_message_id']}")

    # Return empty TwiML (agent will respond asynchronously)
    return {
        "status": "received",
        "message_sid": message_dict.get('MessageSid')
    }
