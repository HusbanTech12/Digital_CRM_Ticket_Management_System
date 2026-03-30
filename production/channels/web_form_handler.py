"""
Web Support Form Handler for Customer Success FTE.
FastAPI router for handling support form submissions.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, EmailStr, validator, Field
from typing import Optional, List
from datetime import datetime, timezone
import uuid
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/support", tags=["support-form"])


# =============================================================================
# Request/Response Models
# =============================================================================

class SupportFormSubmission(BaseModel):
    """Support form submission model with validation."""
    name: str = Field(..., min_length=2, max_length=255, description="Customer name")
    email: EmailStr = Field(..., description="Customer email address")
    subject: str = Field(..., min_length=5, max_length=500, description="Subject line")
    category: str = Field(..., description="Issue category")
    message: str = Field(..., min_length=10, max_length=5000, description="Message content")
    priority: Optional[str] = Field(default='medium', description="Priority level")
    attachments: Optional[List[str]] = Field(default_factory=list, description="Attachment URLs")

    @validator('category')
    def category_must_be_valid(cls, v):
        valid_categories = ['general', 'technical', 'billing', 'feedback', 'bug_report']
        if v not in valid_categories:
            raise ValueError(f'Category must be one of: {valid_categories}')
        return v

    @validator('priority')
    def priority_must_be_valid(cls, v):
        valid_priorities = ['low', 'medium', 'high', 'critical']
        if v not in valid_priorities:
            raise ValueError(f'Priority must be one of: {valid_priorities}')
        return v


class SupportFormResponse(BaseModel):
    """Response model for form submission."""
    ticket_id: str
    message: str
    estimated_response_time: str
    status: str = 'submitted'


class TicketStatusResponse(BaseModel):
    """Response model for ticket status lookup."""
    ticket_id: str
    status: str
    category: str
    priority: str
    created_at: str
    last_updated: Optional[str]
    messages: List[dict]
    estimated_resolution: Optional[str]


# =============================================================================
# API Endpoints
# =============================================================================

@router.post("/submit", response_model=SupportFormResponse)
async def submit_support_form(
    submission: SupportFormSubmission,
    background_tasks: BackgroundTasks
):
    """
    Handle support form submission.

    This endpoint:
    1. Validates the submission
    2. Creates a ticket in the system
    3. Publishes to Kafka for agent processing
    4. Returns confirmation to user
    """
    ticket_id = str(uuid.uuid4())

    logger.info(f"Support form submission received: {ticket_id}")

    # Create normalized message for agent
    message_data = {
        'channel': 'web_form',
        'channel_message_id': ticket_id,
        'customer_email': submission.email,
        'customer_name': submission.name,
        'subject': submission.subject,
        'content': submission.message,
        'category': submission.category,
        'priority': submission.priority,
        'received_at': datetime.now(timezone.utc).isoformat(),
        'metadata': {
            'form_version': '1.0',
            'attachments': submission.attachments,
            'user_agent': None  # Would be populated from request headers
        }
    }

    # In production:
    # 1. Store in database
    # 2. Publish to Kafka for async processing

    # Store initial ticket (pseudo-code, would use database module)
    # await create_ticket(
    #     customer_id=await get_or_create_customer(email=submission.email),
    #     conversation_id=await create_conversation(...),
    #     source_channel='web_form',
    #     category=submission.category,
    #     priority=submission.priority,
    #     subject=submission.subject,
    #     issue=submission.message
    # )

    # Publish to Kafka (pseudo-code)
    # await kafka_producer.publish('fte.tickets.incoming', message_data)

    # Estimate response time based on priority
    response_times = {
        'critical': '15 minutes',
        'high': '1 hour',
        'medium': '4 hours',
        'low': '24 hours'
    }
    estimated_time = response_times.get(submission.priority, '4 hours')

    return SupportFormResponse(
        ticket_id=ticket_id,
        message="Thank you for contacting us! Our AI assistant will respond shortly.",
        estimated_response_time=estimated_time,
        status='submitted'
    )


@router.get("/ticket/{ticket_id}", response_model=TicketStatusResponse)
async def get_ticket_status(ticket_id: str):
    """
    Get status and conversation history for a ticket.
    """
    # In production, fetch from database
    # ticket = await get_ticket(ticket_id)

    # Mock response for development
    ticket = {
        'id': ticket_id,
        'status': 'open',
        'category': 'general',
        'priority': 'medium',
        'created_at': datetime.now(timezone.utc).isoformat(),
        'messages': []
    }

    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    return TicketStatusResponse(
        ticket_id=ticket['id'],
        status=ticket['status'],
        category=ticket['category'],
        priority=ticket['priority'],
        created_at=ticket['created_at'],
        last_updated=ticket.get('updated_at'),
        messages=ticket.get('messages', []),
        estimated_resolution='4 hours'
    )


@router.get("/categories")
async def get_support_categories():
    """Get available support categories."""
    return {
        'categories': [
            {'id': 'general', 'name': 'General Question', 'description': 'General inquiries'},
            {'id': 'technical', 'name': 'Technical Support', 'description': 'Product technical issues'},
            {'id': 'billing', 'name': 'Billing Inquiry', 'description': 'Payment and billing questions'},
            {'id': 'feedback', 'name': 'Feedback', 'description': 'Product feedback and suggestions'},
            {'id': 'bug_report', 'name': 'Bug Report', 'description': 'Report a bug or issue'}
        ]
    }


@router.get("/priority-levels")
async def get_priority_levels():
    """Get available priority levels."""
    return {
        'priority_levels': [
            {'id': 'low', 'name': 'Low', 'description': 'Not urgent, can wait'},
            {'id': 'medium', 'name': 'Medium', 'description': 'Need help soon'},
            {'id': 'high', 'name': 'High', 'description': 'Urgent issue'},
            {'id': 'critical', 'name': 'Critical', 'description': 'Production down'}
        ]
    }
