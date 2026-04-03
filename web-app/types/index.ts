export interface Ticket {
  id: string;
  customer_id: string;
  channel: 'email' | 'whatsapp' | 'web_form';
  category: 'general' | 'technical' | 'billing' | 'feedback' | 'bug_report';
  priority: 'low' | 'medium' | 'high' | 'critical';
  status: 'open' | 'in_progress' | 'resolved' | 'escalated';
  subject: string;
  message: string;
  sentiment_score?: number;
  created_at: string;
  updated_at: string;
}

export interface Customer {
  id: string;
  email: string;
  phone?: string;
  name: string;
  created_at: string;
}

export interface Conversation {
  id: string;
  customer_id: string;
  initial_channel: string;
  status: 'open' | 'closed' | 'escalated';
  sentiment: number;
  topics: string[];
  started_at: string;
}

export interface Message {
  id: string;
  conversation_id: string;
  channel: string;
  direction: 'incoming' | 'outgoing';
  role: 'customer' | 'assistant' | 'human';
  content: string;
  sentiment?: number;
  created_at: string;
}

export interface SupportFormData {
  name: string;
  email: string;
  subject: string;
  category: string;
  priority: string;
  message: string;
}

export interface SubmitTicketResponse {
  ticket_id: string;
  status: string;
  message: string;
  estimated_response_time: string;
}

export interface ApiError {
  detail: string;
  status?: number;
}

export interface SearchParams {
  q?: string;
  category?: string;
  status?: string;
}
