import { NextRequest, NextResponse } from 'next/server';
import { SupportFormData, SubmitTicketResponse } from '@/types';

// Simulated ticket storage (in production, this would be a database)
const tickets = new Map<string, any>();

function generateTicketId(): string {
  const timestamp = Date.now().toString(36);
  const randomPart = Math.random().toString(36).substring(2, 8);
  return `TKT-${timestamp}-${randomPart}`.toUpperCase();
}

function getEstimatedResponseTime(priority: string): string {
  switch (priority) {
    case 'critical':
      return '5 minutes';
    case 'high':
      return '15 minutes';
    case 'medium':
      return '30 minutes';
    case 'low':
      return '2 hours';
    default:
      return '30 minutes';
  }
}

export async function POST(request: NextRequest) {
  try {
    const body: SupportFormData = await request.json();

    // Validate required fields
    const requiredFields: (keyof SupportFormData)[] = ['name', 'email', 'subject', 'message', 'category', 'priority'];
    const missingFields = requiredFields.filter(field => !body[field]);

    if (missingFields.length > 0) {
      return NextResponse.json(
        { detail: `Missing required fields: ${missingFields.join(', ')}` },
        { status: 400 }
      );
    }

    // Validate email format
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(body.email)) {
      return NextResponse.json(
        { detail: 'Invalid email address format' },
        { status: 400 }
      );
    }

    // Validate message length
    if (body.message.trim().length < 10) {
      return NextResponse.json(
        { detail: 'Message must be at least 10 characters long' },
        { status: 400 }
      );
    }

    // Generate ticket ID
    const ticketId = generateTicketId();

    // Create ticket record
    const ticket = {
      id: ticketId,
      customer_id: body.email.toLowerCase(),
      channel: 'web_form' as const,
      category: body.category,
      priority: body.priority,
      status: 'open' as const,
      subject: body.subject,
      message: body.message,
      customer_name: body.name,
      customer_email: body.email,
      sentiment_score: 0.5, // Default neutral sentiment
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };

    // Store ticket (in production, save to database)
    tickets.set(ticketId, ticket);

    // Log ticket for debugging (in production, use proper logging)
    console.log('New ticket created:', {
      ticketId,
      channel: ticket.channel,
      category: ticket.category,
      priority: ticket.priority,
    });

    // In production, here you would:
    // 1. Save to PostgreSQL database
    // 2. Publish event to Kafka for processing
    // 3. Trigger the AI agent to process the ticket
    // 4. Send confirmation email to customer

    const response: SubmitTicketResponse = {
      ticket_id: ticketId,
      status: 'submitted',
      message: 'Your support request has been submitted successfully',
      estimated_response_time: getEstimatedResponseTime(body.priority),
    };

    return NextResponse.json(response, { status: 201 });
  } catch (error) {
    console.error('Error submitting ticket:', error);
    
    return NextResponse.json(
      { detail: 'Internal server error. Please try again later.' },
      { status: 500 }
    );
  }
}

export async function GET() {
  // Return all tickets (for debugging/development purposes)
  const allTickets = Array.from(tickets.values());
  return NextResponse.json({ tickets: allTickets });
}
