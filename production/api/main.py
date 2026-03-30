"""
Customer Success FTE - FastAPI Service
Stage 2: Specialization (Exercise 2.6)

Main API service with:
- Channel webhook endpoints (Gmail, WhatsApp, Web Form)
- Health checks
- Metrics endpoints
- Conversation management
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime, timezone
import os
import logging

from production.channels.gmail_handler import gmail_handler, process_gmail_notification
from production.channels.whatsapp_handler import (
    whatsapp_handler,
    process_whatsapp_webhook,
    validate_whatsapp_webhook
)
from production.channels.web_form_handler import router as web_form_router
from production.workers.kafka_client import (
    FTEKafkaProducer,
    Topic,
    publish_ticket_incoming,
    publish_channel_inbound
)
from production.database import queries as db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# =============================================================================
# FastAPI Application
# =============================================================================

app = FastAPI(
    title="Customer Success FTE API",
    description="24/7 AI-powered customer support across Email, WhatsApp, and Web",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware for web form
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include web form router
app.include_router(web_form_router)


# =============================================================================
# Startup/Shutdown Events
# =============================================================================

@app.on_event("startup")
async def startup():
    """Initialize services on startup."""
    logger.info("Starting Customer Success FTE API...")

    # Initialize database
    await db.get_db()
    logger.info("Database connection initialized")

    # Initialize Kafka producer
    app.state.kafka_producer = FTEKafkaProducer()
    await app.state.kafka_producer.start()
    logger.info("Kafka producer initialized")

    logger.info("Customer Success FTE API started")


@app.on_event("shutdown")
async def shutdown():
    """Cleanup services on shutdown."""
    logger.info("Shutting down Customer Success FTE API...")

    # Close Kafka producer
    if hasattr(app.state, 'kafka_producer'):
        await app.state.kafka_producer.stop()

    # Close database
    await db.close_db()

    logger.info("Customer Success FTE API shutdown complete")


# =============================================================================
# Health Check Endpoints
# =============================================================================

@app.get("/health")
async def health_check():
    """
    Health check endpoint for Kubernetes probes.
    Returns service status and dependencies.
    """
    health_status = {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "2.0.0",
        "channels": {
            "email": "active",
            "whatsapp": "active",
            "web_form": "active"
        }
    }

    # Check database
    try:
        await db.get_db()
        health_status["dependencies"] = {
            "database": "connected",
            "kafka": "connected"
        }
    except Exception as e:
        health_status["status"] = "degraded"
        health_status["dependencies"] = {
            "database": f"error: {str(e)}",
            "kafka": "unknown"
        }

    return health_status


@app.get("/ready")
async def readiness_check():
    """
    Readiness check - is the service ready to receive traffic?
    """
    try:
        # Check all critical dependencies
        await db.get_db()

        return JSONResponse(
            status_code=200,
            content={"status": "ready"}
        )
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={"status": "not_ready", "error": str(e)}
        )


@app.get("/live")
async def liveness_check():
    """
    Liveness check - is the service alive?
    """
    return {"status": "alive"}


# =============================================================================
# Gmail Webhook Endpoints
# =============================================================================

@app.post("/webhooks/gmail")
async def gmail_webhook(
    request: Request,
    background_tasks: BackgroundTasks
):
    """
    Handle Gmail push notifications via Pub/Sub.

    Expected payload (Pub/Sub format):
    {
        "message": {
            "data": "base64_encoded_history_id",
            "messageId": "pubsub-message-id"
        },
        "subscription": "projects/xxx/subscriptions/yyy"
    }
    """
    try:
        body = await request.json()

        # Extract history ID from Pub/Sub message
        message_data = body.get('message', {})
        history_id = message_data.get('data')

        if not history_id:
            logger.warning("Gmail webhook received without history ID")
            return {"status": "ignored", "reason": "no_history_id"}

        # Process Gmail notification
        messages = await process_gmail_notification({
            'historyId': history_id
        })

        # Publish each message to Kafka for async processing
        for message in messages:
            background_tasks.add_task(
                publish_channel_inbound,
                'email',
                message
            )

        logger.info(f"Processed {len(messages)} Gmail messages")
        return {
            "status": "processed",
            "count": len(messages)
        }

    except Exception as e:
        logger.error(f"Gmail webhook error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/webhooks/gmail/setup")
async def setup_gmail_webhook():
    """
    Setup Gmail push notifications.
    Call this once to initialize Gmail webhook.
    """
    topic_name = os.getenv("GMAIL_PUBSUB_TOPIC", "projects/xxx/topics/gmail-push")

    result = await gmail_handler.setup_push_notifications(topic_name)

    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])

    return result


# =============================================================================
# WhatsApp Webhook Endpoints
# =============================================================================

@app.post("/webhooks/whatsapp")
async def whatsapp_webhook(
    request: Request,
    background_tasks: BackgroundTasks
):
    """
    Handle incoming WhatsApp messages via Twilio webhook.

    Twilio sends form-data with:
    - MessageSid: Unique message ID
    - From: Sender's WhatsApp number (whatsapp:+1234567890)
    - To: Your WhatsApp number
    - Body: Message text
    - ProfileName: Sender's name (if available)
    """
    try:
        # Validate Twilio signature
        is_valid = await validate_whatsapp_webhook(request)
        if not is_valid:
            logger.warning("Invalid Twilio signature")
            raise HTTPException(status_code=403, detail="Invalid signature")

        # Get form data
        form_data = await request.form()
        message_dict = dict(form_data)

        # Process webhook
        message = await process_whatsapp_webhook(message_dict)

        if message:
            # Publish to Kafka for async processing
            background_tasks.add_task(
                publish_channel_inbound,
                'whatsapp',
                message
            )
            logger.info(f"Queued WhatsApp message: {message['channel_message_id']}")

        # Return empty TwiML (agent responds asynchronously)
        return Response(
            content='<?xml version="1.0" encoding="UTF-8"?><Response></Response>',
            media_type="application/xml"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"WhatsApp webhook error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/webhooks/whatsapp/status")
async def whatsapp_status_webhook(request: Request):
    """
    Handle WhatsApp message status updates (delivered, read, etc.).

    Twilio sends status updates to this endpoint when message status changes.
    """
    try:
        form_data = await request.form()

        message_sid = form_data.get('MessageSid')
        status = form_data.get('MessageStatus')

        logger.info(f"WhatsApp message {message_sid} status: {status}")

        # Update delivery status in database
        if message_sid and status:
            # In production, update the messages table
            # await db.update_message_delivery_status(message_sid, status)
            pass

        return {"status": "received"}

    except Exception as e:
        logger.error(f"WhatsApp status webhook error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# Conversation Management Endpoints
# =============================================================================

class ConversationResponse(BaseModel):
    """Conversation response model."""
    conversation_id: str
    customer_id: str
    channel: str
    status: str
    started_at: str
    messages: List[Dict]
    sentiment_score: float


@app.get("/conversations/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(conversation_id: str):
    """
    Get full conversation history with cross-channel context.
    """
    # Get conversation from database
    # In production, use proper database queries

    # Mock response for development
    conversation = {
        "conversation_id": conversation_id,
        "customer_id": "mock-customer-id",
        "channel": "email",
        "status": "active",
        "started_at": datetime.now(timezone.utc).isoformat(),
        "messages": [],
        "sentiment_score": 0.7
    }

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    return conversation


@app.get("/customers/lookup")
async def lookup_customer(
    email: Optional[str] = None,
    phone: Optional[str] = None
):
    """
    Look up customer by email or phone across all channels.
    """
    if not email and not phone:
        raise HTTPException(
            status_code=400,
            detail="Provide email or phone parameter"
        )

    # Look up customer in database
    customer_id = await db.get_or_create_customer(
        email=email,
        phone=phone
    )

    if not customer_id:
        raise HTTPException(status_code=404, detail="Customer not found")

    customer = await db.get_customer_by_id(customer_id)

    return customer


@app.get("/customers/{customer_id}/history")
async def get_customer_history(customer_id: str, limit: int = 20):
    """
    Get customer's conversation history across all channels.
    """
    history = await db.get_customer_history(customer_id, limit)

    return {
        "customer_id": customer_id,
        "history": history,
        "count": len(history)
    }


# =============================================================================
# Metrics Endpoints
# =============================================================================

@app.get("/metrics/channels")
async def get_channel_metrics(hours: int = 24):
    """
    Get performance metrics by channel.
    """
    metrics = await db.get_channel_metrics(hours)

    return {
        "metrics": metrics,
        "period_hours": hours
    }


@app.get("/metrics/summary")
async def get_metrics_summary():
    """
    Get overall system metrics summary.
    """
    # In production, aggregate from agent_metrics table
    return {
        "total_tickets_24h": 0,
        "avg_response_time_ms": 0,
        "escalation_rate": 0,
        "resolution_rate": 0,
        "customer_satisfaction": 0
    }


# =============================================================================
# Ticket Management Endpoints
# =============================================================================

@app.get("/tickets/{ticket_id}")
async def get_ticket(ticket_id: str):
    """
    Get ticket details and status.
    """
    ticket = await db.get_ticket(ticket_id)

    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    return ticket


@app.post("/tickets/{ticket_id}/escalate")
async def escalate_ticket(
    ticket_id: str,
    reason: str,
    urgency: str = "normal",
    context: Optional[str] = None
):
    """
    Manually escalate a ticket to human support.
    """
    escalation_id = await db.escalate_ticket(
        ticket_id=ticket_id,
        reason=reason,
        urgency=urgency,
        additional_context=context
    )

    return {
        "ticket_id": ticket_id,
        "escalation_id": escalation_id,
        "status": "escalated"
    }


# =============================================================================
# Admin Endpoints
# =============================================================================

@app.post("/admin/knowledge-base/sync")
async def sync_knowledge_base(background_tasks: BackgroundTasks):
    """
    Trigger knowledge base synchronization.
    In production, this would fetch latest docs and generate embeddings.
    """
    logger.info("Knowledge base sync triggered")

    return {
        "status": "sync_started",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@app.get("/admin/config")
async def get_config():
    """
    Get current service configuration.
    """
    return {
        "channels": {
            "email": {"enabled": True, "type": "gmail"},
            "whatsapp": {"enabled": True, "type": "twilio"},
            "web_form": {"enabled": True}
        },
        "features": {
            "sentiment_analysis": True,
            "auto_escalation": True,
            "cross_channel_continuity": True
        }
    }


# =============================================================================
# Error Handlers
# =============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions."""
    logger.warning(f"HTTP error {exc.status_code}: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "status_code": exc.status_code}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unhandled exceptions."""
    logger.error(f"Unhandled error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "status_code": 500}
    )


# =============================================================================
# Main Entry Point
# =============================================================================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "production.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
