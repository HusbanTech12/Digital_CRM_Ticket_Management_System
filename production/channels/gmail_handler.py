"""
Gmail Integration Handler for Customer Success FTE.
Handles incoming emails via Gmail API and sends responses.
"""

import base64
import os
import re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timezone
from typing import Dict, List, Optional
from google.oauth2.credentials import Credentials
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import logging

logger = logging.getLogger(__name__)


class GmailHandler:
    """Handler for Gmail API integration."""

    def __init__(self):
        self.credentials: Optional[Credentials] = None
        self.service = None
        self._initialize_credentials()

    def _initialize_credentials(self):
        """Initialize Gmail API credentials."""
        # Try service account first (for production)
        credentials_path = os.getenv('GMAIL_CREDENTIALS_PATH')
        if credentials_path and os.path.exists(credentials_path):
            try:
                self.credentials = service_account.Credentials.from_service_account_file(
                    credentials_path,
                    scopes=['https://www.googleapis.com/auth/gmail.send',
                            'https://www.googleapis.com/auth/gmail.readonly',
                            'https://www.googleapis.com/auth/gmail.modify']
                )
                self.service = build('gmail', 'v1', credentials=self.credentials)
                logger.info("Gmail credentials initialized from service account")
                return
            except Exception as e:
                logger.warning(f"Service account auth failed: {e}")

        # Fall back to OAuth credentials (for development)
        # In development, credentials would be set via environment or mounted file
        logger.info("Gmail handler initialized (credentials required for production)")

    async def setup_push_notifications(self, topic_name: str) -> Dict:
        """
        Set up Gmail push notifications via Pub/Sub.
        This allows real-time email processing.
        """
        if not self.service:
            return {"error": "Gmail service not initialized"}

        try:
            request = {
                'labelIds': ['INBOX'],
                'topicName': topic_name,
                'labelFilterAction': 'include'
            }

            result = self.service.users().watch(
                userId='me',
                body=request
            ).execute()

            logger.info(f"Gmail push notifications setup: {result}")
            return {
                "status": "success",
                "history_id": result.get('historyId'),
                "expiration": result.get('expiration')
            }

        except HttpError as e:
            logger.error(f"Gmail watch setup failed: {e}")
            return {"error": str(e)}

    async def stop_push_notifications(self) -> bool:
        """Stop Gmail push notifications."""
        if not self.service:
            return False

        try:
            self.service.users().stop(userId='me').execute()
            logger.info("Gmail push notifications stopped")
            return True
        except HttpError as e:
            logger.error(f"Gmail stop failed: {e}")
            return False

    async def process_pubsub_message(self, message_data: Dict) -> List[Dict]:
        """
        Process incoming Pub/Sub notification from Gmail.
        Returns list of normalized message objects.
        """
        if not self.service:
            return []

        history_id = message_data.get('historyId')
        if not history_id:
            return []

        try:
            # Get messages since last history ID
            history = self.service.users().history().list(
                userId='me',
                startHistoryId=history_id,
                historyTypes=['messageAdded']
            ).execute()

            messages = []
            for record in history.get('history', []):
                for msg_added in record.get('messagesAdded', []):
                    msg_id = msg_added['message']['id']
                    message = await self.get_message(msg_id)
                    if message:
                        messages.append(message)

            return messages

        except HttpError as e:
            logger.error(f"Gmail history fetch failed: {e}")
            return []

    async def get_message(self, message_id: str) -> Optional[Dict]:
        """Fetch and parse a Gmail message."""
        if not self.service:
            return None

        try:
            msg = self.service.users().messages().get(
                userId='me',
                id=message_id,
                format='full'
            ).execute()

            payload = msg.get('payload', {})
            headers = {h['name']: h['value'] for h in payload.get('headers', [])}

            # Extract email components
            from_email = self._extract_email(headers.get('From', ''))
            subject = headers.get('Subject', '')
            body = self._extract_body(payload)

            # Check if this is a reply (has In-Reply-To header)
            thread_id = msg.get('threadId')
            in_reply_to = headers.get('In-Reply-To')

            return {
                'channel': 'email',
                'channel_message_id': message_id,
                'customer_email': from_email,
                'customer_name': self._extract_name(headers.get('From', '')),
                'subject': subject.replace('Re: ', '').strip(),
                'content': body,
                'received_at': datetime.now(timezone.utc).isoformat(),
                'thread_id': thread_id,
                'in_reply_to': in_reply_to,
                'metadata': {
                    'headers': headers,
                    'labels': msg.get('labelIds', []),
                    'internal_date': msg.get('internalDate')
                }
            }

        except HttpError as e:
            logger.error(f"Gmail message fetch failed: {e}")
            return None

    def _extract_body(self, payload: Dict) -> str:
        """Extract text body from email payload."""
        # Try to get plain text body first
        if 'body' in payload and payload['body'].get('data'):
            try:
                return base64.urlsafe_b64decode(
                    payload['body']['data']
                ).decode('utf-8')
            except Exception:
                pass

        # Try parts (multipart message)
        if 'parts' in payload:
            for part in payload['parts']:
                if part.get('mimeType') == 'text/plain' and part['body'].get('data'):
                    try:
                        return base64.urlsafe_b64decode(
                            part['body']['data']
                        ).decode('utf-8')
                    except Exception:
                        pass

            # Fall back to HTML if no plain text
            for part in payload['parts']:
                if part.get('mimeType') == 'text/html' and part['body'].get('data'):
                    try:
                        html = base64.urlsafe_b64decode(
                            part['body']['data']
                        ).decode('utf-8')
                        # Simple HTML to text conversion
                        return re.sub(r'<[^>]+>', '', html)
                    except Exception:
                        pass

        return ''

    def _extract_email(self, from_header: str) -> str:
        """Extract email address from From header."""
        # Handle formats like "John Doe <john@example.com>"
        match = re.search(r'<([^>]+)>', from_header)
        if match:
            return match.group(1).lower()

        # Handle plain email
        email = from_header.strip().lower()
        if '@' in email:
            return email

        return ''

    def _extract_name(self, from_header: str) -> Optional[str]:
        """Extract name from From header."""
        # Handle formats like "John Doe <john@example.com>"
        match = re.search(r'^"([^"]+)"', from_header)
        if match:
            return match.group(1)

        # Handle formats like "John Doe <john@example.com>"
        match = re.search(r'^([^<]+)<', from_header)
        if match:
            return match.group(1).strip()

        return None

    async def send_reply(
        self,
        to_email: str,
        subject: str,
        body: str,
        thread_id: Optional[str] = None,
        in_reply_to: Optional[str] = None
    ) -> Dict:
        """
        Send email reply.
        Returns delivery status and message ID.
        """
        if not self.service:
            # In development mode, log the email that would be sent
            logger.info(f"[DEV MODE] Would send email to {to_email}: {subject}")
            return {
                'channel_message_id': f'dev-{datetime.now(timezone.utc).isoformat()}',
                'delivery_status': 'sent_dev_mode'
            }

        try:
            # Create message
            message = MIMEMultipart('alternative')
            message['to'] = to_email
            message['subject'] = f"Re: {subject}" if not subject.startswith('Re:') else subject

            # Add plain text and HTML versions
            message.attach(MIMEText(body, 'plain'))
            message.attach(MIMEText(
                self._text_to_html(body),
                'html'
            ))

            # Add In-Reply-To header for threading
            if in_reply_to:
                message['In-Reply-To'] = in_reply_to
                message['References'] = in_reply_to

            # Encode message
            raw = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')

            # Send message
            send_request = {'raw': raw}
            if thread_id:
                send_request['threadId'] = thread_id

            result = self.service.users().messages().send(
                userId='me',
                body=send_request
            ).execute()

            logger.info(f"Email sent: {result['id']}")
            return {
                'channel_message_id': result['id'],
                'thread_id': result.get('threadId'),
                'delivery_status': 'sent'
            }

        except HttpError as e:
            logger.error(f"Gmail send failed: {e}")
            return {
                'error': str(e),
                'delivery_status': 'failed'
            }

    def _text_to_html(self, text: str) -> str:
        """Convert plain text to simple HTML."""
        # Escape HTML
        html = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

        # Convert newlines to <br>
        html = html.replace('\n', '<br>')

        # Wrap in basic HTML structure
        return f"""
<html>
<body style="font-family: Arial, sans-serif; line-height: 1.6;">
{html}
</body>
</html>
"""

    async def mark_as_read(self, message_id: str) -> bool:
        """Mark message as read."""
        if not self.service:
            return False

        try:
            self.service.users().messages().modify(
                userId='me',
                id=message_id,
                body={'removeLabelIds': ['UNREAD']}
            ).execute()
            return True
        except HttpError as e:
            logger.error(f"Gmail mark as read failed: {e}")
            return False

    async def add_label(self, message_id: str, label_name: str) -> bool:
        """Add label to message."""
        if not self.service:
            return False

        try:
            # Create label if it doesn't exist
            label_id = await self._get_or_create_label(label_name)

            self.service.users().messages().modify(
                userId='me',
                id=message_id,
                body={'addLabelIds': [label_id]}
            ).execute()
            return True
        except HttpError as e:
            logger.error(f"Gmail add label failed: {e}")
            return False

    async def _get_or_create_label(self, label_name: str) -> str:
        """Get or create Gmail label."""
        # Try to find existing label
        labels = self.service.users().labels().list(userId='me').execute()
        for label in labels.get('labels', []):
            if label['name'] == label_name:
                return label['id']

        # Create new label
        label = self.service.users().labels().create(
            userId='me',
            body={'name': label_name}
        ).execute()
        return label['id']


# Global handler instance
gmail_handler = GmailHandler()


# Convenience functions for use in other modules
async def process_gmail_notification(message_data: Dict) -> List[Dict]:
    """Process Gmail Pub/Sub notification."""
    return await gmail_handler.process_pubsub_message(message_data)


async def send_gmail_reply(
    to_email: str,
    subject: str,
    body: str,
    thread_id: Optional[str] = None
) -> Dict:
    """Send Gmail reply."""
    return await gmail_handler.send_reply(to_email, subject, body, thread_id)
