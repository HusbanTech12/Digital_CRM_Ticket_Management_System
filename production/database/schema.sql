-- =============================================================================
-- CUSTOMER SUCCESS FTE - CRM/TICKET MANAGEMENT SYSTEM
-- =============================================================================
-- This PostgreSQL schema serves as your complete CRM system for tracking:
-- - Customers (unified across all channels)
-- - Conversations and message history
-- - Support tickets and their lifecycle
-- - Knowledge base for AI responses
-- - Performance metrics and reporting
-- =============================================================================

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "vector";  -- pgvector for semantic search
CREATE EXTENSION IF NOT EXISTS "pg_trgm";  -- For text similarity search

-- =============================================================================
-- CUSTOMERS TABLE (unified across channels)
-- =============================================================================
CREATE TABLE customers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255),
    phone VARCHAR(50),
    name VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB DEFAULT '{}',
    -- Constraints
    CONSTRAINT customers_email_check CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'),
    CONSTRAINT customers_phone_check CHECK (phone ~ '^\+?[0-9]{7,15}$')
);

-- Create index for email lookups
CREATE INDEX idx_customers_email ON customers(email);
CREATE INDEX idx_customers_phone ON customers(phone);
CREATE INDEX idx_customers_created_at ON customers(created_at);

-- =============================================================================
-- CUSTOMER IDENTIFIERS (for cross-channel matching)
-- =============================================================================
CREATE TABLE customer_identifiers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_id UUID REFERENCES customers(id) ON DELETE CASCADE,
    identifier_type VARCHAR(50) NOT NULL,  -- 'email', 'phone', 'whatsapp'
    identifier_value VARCHAR(255) NOT NULL,
    verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    -- Ensure unique identifier per type
    UNIQUE(identifier_type, identifier_value)
);

CREATE INDEX idx_customer_identifiers_value ON customer_identifiers(identifier_value);
CREATE INDEX idx_customer_identifiers_customer ON customer_identifiers(customer_id);

-- =============================================================================
-- CONVERSATIONS TABLE
-- =============================================================================
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_id UUID REFERENCES customers(id) ON DELETE CASCADE,
    initial_channel VARCHAR(50) NOT NULL,  -- 'email', 'whatsapp', 'web_form'
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    ended_at TIMESTAMP WITH TIME ZONE,
    status VARCHAR(50) DEFAULT 'active',  -- 'active', 'pending', 'resolved', 'escalated', 'closed'
    sentiment_score DECIMAL(3,2) DEFAULT 0.5,  -- 0.00 to 1.00
    sentiment_trend DECIMAL[] DEFAULT '{}',  -- Array of sentiment scores over time
    resolution_type VARCHAR(50),  -- 'ai_resolved', 'human_escalated', 'customer_abandoned', 'auto_closed'
    escalated_to VARCHAR(255),  -- Team name if escalated
    metadata JSONB DEFAULT '{}',
    -- Constraints
    CONSTRAINT conversations_status_check CHECK (status IN ('active', 'pending', 'resolved', 'escalated', 'closed')),
    CONSTRAINT conversations_sentiment_check CHECK (sentiment_score >= 0.0 AND sentiment_score <= 1.0)
);

CREATE INDEX idx_conversations_customer ON conversations(customer_id);
CREATE INDEX idx_conversations_status ON conversations(status);
CREATE INDEX idx_conversations_channel ON conversations(initial_channel);
CREATE INDEX idx_conversations_started_at ON conversations(started_at);
CREATE INDEX idx_conversations_sentiment ON conversations(sentiment_score);

-- =============================================================================
-- MESSAGES TABLE (with channel tracking)
-- =============================================================================
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,
    channel VARCHAR(50) NOT NULL,  -- 'email', 'whatsapp', 'web_form'
    direction VARCHAR(20) NOT NULL,  -- 'inbound', 'outbound'
    role VARCHAR(20) NOT NULL,  -- 'customer', 'agent', 'system'
    content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    tokens_used INTEGER,
    latency_ms INTEGER,
    tool_calls JSONB DEFAULT '[]',  -- Array of tool call records
    channel_message_id VARCHAR(255),  -- External ID (Gmail message ID, Twilio SID)
    delivery_status VARCHAR(50) DEFAULT 'pending',  -- 'pending', 'sent', 'delivered', 'failed'
    sentiment_score DECIMAL(3,2) DEFAULT 0.5,
    topics VARCHAR(100)[],  -- Array of topic tags
    metadata JSONB DEFAULT '{}',
    -- Constraints
    CONSTRAINT messages_direction_check CHECK (direction IN ('inbound', 'outbound')),
    CONSTRAINT messages_role_check CHECK (role IN ('customer', 'agent', 'system')),
    CONSTRAINT messages_delivery_status_check CHECK (delivery_status IN ('pending', 'sent', 'delivered', 'failed')),
    CONSTRAINT messages_sentiment_check CHECK (sentiment_score >= 0.0 AND sentiment_score <= 1.0)
);

CREATE INDEX idx_messages_conversation ON messages(conversation_id);
CREATE INDEX idx_messages_channel ON messages(channel);
CREATE INDEX idx_messages_created_at ON messages(created_at);
CREATE INDEX idx_messages_direction ON messages(direction);
CREATE INDEX idx_messages_sentiment ON messages(sentiment_score);
-- Full-text search index for message content
CREATE INDEX idx_messages_content_fts ON messages USING gin(to_tsvector('english', content));

-- =============================================================================
-- TICKETS TABLE
-- =============================================================================
CREATE TABLE tickets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,
    customer_id UUID REFERENCES customers(id) ON DELETE CASCADE,
    source_channel VARCHAR(50) NOT NULL,  -- 'email', 'whatsapp', 'web_form'
    category VARCHAR(100),  -- 'authentication', 'cicd', 'billing', 'integrations', etc.
    priority VARCHAR(20) DEFAULT 'medium',  -- 'low', 'medium', 'high', 'critical'
    status VARCHAR(50) DEFAULT 'open',  -- 'open', 'in_progress', 'pending', 'resolved', 'escalated', 'closed'
    subject VARCHAR(500),
    issue TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    resolved_at TIMESTAMP WITH TIME ZONE,
    resolution_notes TEXT,
    escalated_to VARCHAR(255),  -- Team name
    escalation_reason VARCHAR(100),  -- 'legal_inquiry', 'pricing_inquiry', etc.
    metadata JSONB DEFAULT '{}',
    -- Constraints
    CONSTRAINT tickets_priority_check CHECK (priority IN ('low', 'medium', 'high', 'critical')),
    CONSTRAINT tickets_status_check CHECK (status IN ('open', 'in_progress', 'pending', 'resolved', 'escalated', 'closed')),
    CONSTRAINT tickets_source_channel_check CHECK (source_channel IN ('email', 'whatsapp', 'web_form'))
);

CREATE INDEX idx_tickets_status ON tickets(status);
CREATE INDEX idx_tickets_channel ON tickets(source_channel);
CREATE INDEX idx_tickets_customer ON tickets(customer_id);
CREATE INDEX idx_tickets_category ON tickets(category);
CREATE INDEX idx_tickets_priority ON tickets(priority);
CREATE INDEX idx_tickets_created_at ON tickets(created_at);
CREATE INDEX idx_tickets_escalated ON tickets(escalated_to) WHERE status = 'escalated';

-- =============================================================================
-- KNOWLEDGE BASE ENTRIES (with vector embeddings for semantic search)
-- =============================================================================
CREATE TABLE knowledge_base (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(500) NOT NULL,
    content TEXT NOT NULL,
    category VARCHAR(100),  -- 'authentication', 'cicd', 'billing', etc.
    tags VARCHAR(100)[],  -- Array of tags for filtering
    embedding vector(1536),  -- OpenAI ada-002 embeddings (1536 dimensions)
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'
);

-- Vector similarity index for semantic search
CREATE INDEX idx_knowledge_embedding ON knowledge_base USING ivfflat (embedding vector_cosine_ops);
CREATE INDEX idx_knowledge_category ON knowledge_base(category);
CREATE INDEX idx_knowledge_title_fts ON knowledge_base USING gin(to_tsvector('english', title));
CREATE INDEX idx_knowledge_content_fts ON knowledge_base USING gin(to_tsvector('english', content));

-- =============================================================================
-- CHANNEL CONFIGURATIONS
-- =============================================================================
CREATE TABLE channel_configs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    channel VARCHAR(50) UNIQUE NOT NULL,  -- 'email', 'whatsapp', 'web_form'
    enabled BOOLEAN DEFAULT TRUE,
    config JSONB NOT NULL,  -- API keys, webhook URLs, etc. (encrypted in production)
    response_template TEXT,
    max_response_length INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    -- Constraints
    CONSTRAINT channels_channel_check CHECK (channel IN ('email', 'whatsapp', 'web_form'))
);

-- Insert default channel configurations
INSERT INTO channel_configs (channel, enabled, config, response_template, max_response_length) VALUES
('email', TRUE, 
 '{"smtp_host": "smtp.gmail.com", "smtp_port": 587, "use_oauth": true}'::jsonb,
 'Dear {name},\n\nThank you for reaching out to TechCorp Support.\n\n{response}\n\nBest regards,\nTechCorp AI Support Team',
 2000),
('whatsapp', TRUE, 
 '{"twilio_enabled": true, "max_message_length": 1600}'::jsonb,
 '{response}\n\n📱 Reply for more help or type ''human'' for live support.',
 1600),
('web_form', TRUE, 
 '{"email_notification": true}'::jsonb,
 'Hi {name},\n\nThanks for contacting support!\n\n{response}\n\n---\nTicket: {ticket_id}',
 1000);

-- =============================================================================
-- AGENT PERFORMANCE METRICS
-- =============================================================================
CREATE TABLE agent_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    metric_name VARCHAR(100) NOT NULL,  -- 'response_time_ms', 'accuracy', 'escalation_rate', etc.
    metric_value DECIMAL(10,4) NOT NULL,
    channel VARCHAR(50),  -- Optional: channel-specific metrics
    dimensions JSONB DEFAULT '{}',  -- Additional dimensions (e.g., {"hour": "14", "day": "Monday"})
    recorded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_metrics_name ON agent_metrics(metric_name);
CREATE INDEX idx_metrics_channel ON agent_metrics(channel);
CREATE INDEX idx_metrics_recorded_at ON agent_metrics(recorded_at);
-- Composite index for time-series queries
CREATE INDEX idx_metrics_name_time ON agent_metrics(metric_name, recorded_at DESC);

-- =============================================================================
-- ESCALATIONS TABLE
-- =============================================================================
CREATE TABLE escalations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    ticket_id UUID REFERENCES tickets(id) ON DELETE CASCADE,
    conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,
    reason VARCHAR(100) NOT NULL,  -- 'legal_inquiry', 'pricing_inquiry', etc.
    urgency VARCHAR(20) DEFAULT 'normal',  -- 'normal', 'high', 'critical'
    assigned_to VARCHAR(255),  -- Team or person assigned
    status VARCHAR(50) DEFAULT 'pending',  -- 'pending', 'assigned', 'in_progress', 'resolved'
    additional_context TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    resolved_at TIMESTAMP WITH TIME ZONE,
    resolution_notes TEXT,
    -- Constraints
    CONSTRAINT escalations_urgency_check CHECK (urgency IN ('normal', 'high', 'critical')),
    CONSTRAINT escalations_status_check CHECK (status IN ('pending', 'assigned', 'in_progress', 'resolved'))
);

CREATE INDEX idx_escalations_status ON escalations(status);
CREATE INDEX idx_escalations_reason ON escalations(reason);
CREATE INDEX idx_escalations_urgency ON escalations(urgency);
CREATE INDEX idx_escalations_assigned_to ON escalations(assigned_to);

-- =============================================================================
-- CUSTOMER IDENTIFIERS HELPER FUNCTION
-- =============================================================================
CREATE OR REPLACE FUNCTION add_customer_identifier(
    p_customer_id UUID,
    p_identifier_type VARCHAR,
    p_identifier_value VARCHAR
) RETURNS VOID AS $$
BEGIN
    INSERT INTO customer_identifiers (customer_id, identifier_type, identifier_value)
    VALUES (p_customer_id, p_identifier_type, LOWER(p_identifier_value))
    ON CONFLICT (identifier_type, identifier_value) DO NOTHING;
END;
$$ LANGUAGE plpgsql;

-- =============================================================================
-- GET OR CREATE CUSTOMER FUNCTION
-- =============================================================================
CREATE OR REPLACE FUNCTION get_or_create_customer(
    p_email VARCHAR DEFAULT NULL,
    p_phone VARCHAR DEFAULT NULL,
    p_name VARCHAR DEFAULT NULL
) RETURNS UUID AS $$
DECLARE
    v_customer_id UUID;
BEGIN
    -- Try to find by email first
    IF p_email IS NOT NULL THEN
        SELECT id INTO v_customer_id FROM customers WHERE email = LOWER(p_email);
    END IF;
    
    -- Try to find by phone if not found by email
    IF v_customer_id IS NULL AND p_phone IS NOT NULL THEN
        SELECT id INTO v_customer_id FROM customers WHERE phone = p_phone;
    END IF;
    
    -- Create new customer if not found
    IF v_customer_id IS NULL THEN
        INSERT INTO customers (email, phone, name)
        VALUES (
            CASE WHEN p_email IS NOT NULL THEN LOWER(p_email) ELSE NULL END,
            p_phone,
            p_name
        )
        RETURNING id INTO v_customer_id;
        
        -- Add identifier if email provided
        IF p_email IS NOT NULL THEN
            INSERT INTO customer_identifiers (customer_id, identifier_type, identifier_value)
            VALUES (v_customer_id, 'email', LOWER(p_email));
        END IF;
        
        -- Add identifier if phone provided
        IF p_phone IS NOT NULL THEN
            INSERT INTO customer_identifiers (customer_id, identifier_type, identifier_value)
            VALUES (v_customer_id, 'phone', p_phone);
        END IF;
    END IF;
    
    RETURN v_customer_id;
END;
$$ LANGUAGE plpgsql;

-- =============================================================================
-- GET ACTIVE CONVERSATION FUNCTION
-- =============================================================================
CREATE OR REPLACE FUNCTION get_active_conversation(
    p_customer_id UUID,
    p_hours INTEGER DEFAULT 24
) RETURNS UUID AS $$
DECLARE
    v_conversation_id UUID;
BEGIN
    SELECT id INTO v_conversation_id
    FROM conversations
    WHERE customer_id = p_customer_id
      AND status = 'active'
      AND started_at > NOW() - (p_hours || ' hours')::INTERVAL
    ORDER BY started_at DESC
    LIMIT 1;
    
    RETURN v_conversation_id;
END;
$$ LANGUAGE plpgsql;

-- =============================================================================
-- CREATE CONVERSATION FUNCTION
-- =============================================================================
CREATE OR REPLACE FUNCTION create_conversation(
    p_customer_id UUID,
    p_initial_channel VARCHAR
) RETURNS UUID AS $$
DECLARE
    v_conversation_id UUID;
BEGIN
    INSERT INTO conversations (customer_id, initial_channel, status)
    VALUES (p_customer_id, p_initial_channel, 'active')
    RETURNING id INTO v_conversation_id;
    
    RETURN v_conversation_id;
END;
$$ LANGUAGE plpgsql;

-- =============================================================================
-- ADD MESSAGE FUNCTION
-- =============================================================================
CREATE OR REPLACE FUNCTION add_message(
    p_conversation_id UUID,
    p_channel VARCHAR,
    p_direction VARCHAR,
    p_role VARCHAR,
    p_content TEXT,
    p_sentiment_score DECIMAL DEFAULT 0.5,
    p_topics VARCHAR[] DEFAULT NULL,
    p_channel_message_id VARCHAR DEFAULT NULL
) RETURNS UUID AS $$
DECLARE
    v_message_id UUID;
BEGIN
    INSERT INTO messages (
        conversation_id, channel, direction, role, content,
        sentiment_score, topics, channel_message_id
    )
    VALUES (
        p_conversation_id, p_channel, p_direction, p_role, p_content,
        p_sentiment_score, p_topics, p_channel_message_id
    )
    RETURNING id INTO v_message_id;
    
    -- Update conversation sentiment
    UPDATE conversations
    SET sentiment_score = (
            SELECT AVG(sentiment_score)
            FROM messages
            WHERE conversation_id = p_conversation_id
        ),
        sentiment_trend = array_append(
            COALESCE(sentiment_trend, '{}'),
            p_sentiment_score
        )
    WHERE id = p_conversation_id;
    
    RETURN v_message_id;
END;
$$ LANGUAGE plpgsql;

-- =============================================================================
-- RESOLVE CONVERSATION FUNCTION
-- =============================================================================
CREATE OR REPLACE FUNCTION resolve_conversation(
    p_conversation_id UUID,
    p_resolution_type VARCHAR,
    p_escalated_to VARCHAR DEFAULT NULL
) RETURNS VOID AS $$
BEGIN
    UPDATE conversations
    SET status = CASE 
            WHEN p_escalated_to IS NOT NULL THEN 'escalated'
            ELSE 'resolved'
        END,
        ended_at = NOW(),
        resolution_type = p_resolution_type,
        escalated_to = p_escalated_to
    WHERE id = p_conversation_id;
END;
$$ LANGUAGE plpgsql;

-- =============================================================================
-- GET CUSTOMER HISTORY FUNCTION
-- =============================================================================
CREATE OR REPLACE FUNCTION get_customer_history(
    p_customer_id UUID,
    p_limit INTEGER DEFAULT 20
) RETURNS TABLE (
    conversation_id UUID,
    channel VARCHAR,
    started_at TIMESTAMP WITH TIME ZONE,
    status VARCHAR,
    content TEXT,
    role VARCHAR,
    message_channel VARCHAR,
    created_at TIMESTAMP WITH TIME ZONE
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        c.id AS conversation_id,
        c.initial_channel AS channel,
        c.started_at,
        c.status,
        m.content,
        m.role,
        m.channel AS message_channel,
        m.created_at
    FROM conversations c
    JOIN messages m ON m.conversation_id = c.id
    WHERE c.customer_id = p_customer_id
    ORDER BY m.created_at DESC
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql;

-- =============================================================================
-- UPDATE CUSTOMER STATISTICS TRIGGER
-- =============================================================================
CREATE OR REPLACE FUNCTION update_customer_stats() RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' AND NEW.resolution_type = 'ai_resolved' THEN
        UPDATE customers
        SET resolved_tickets = resolved_tickets + 1
        WHERE id = NEW.customer_id;
    ELSIF TG_OP = 'INSERT' AND NEW.resolution_type = 'human_escalated' THEN
        UPDATE customers
        SET escalated_tickets = escalated_tickets + 1
        WHERE id = NEW.customer_id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_customer_stats
    AFTER INSERT ON conversations
    FOR EACH ROW
    EXECUTE FUNCTION update_customer_stats();

-- =============================================================================
-- AUTO-UPDATE updated_at TIMESTAMP
-- =============================================================================
CREATE OR REPLACE FUNCTION update_updated_at_column() RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply to tables with updated_at
CREATE TRIGGER update_customers_updated_at
    BEFORE UPDATE ON customers
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_channel_configs_updated_at
    BEFORE UPDATE ON channel_configs
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_knowledge_base_updated_at
    BEFORE UPDATE ON knowledge_base
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- =============================================================================
-- SAMPLE DATA FOR TESTING
-- =============================================================================

-- Insert sample knowledge base entries
INSERT INTO knowledge_base (title, content, category, tags) VALUES
('Creating an API Key',
 'API keys authenticate your requests to the DevFlow API.

To create an API key:
1. Log in to your DevFlow dashboard at app.devflow.com
2. Navigate to Settings > API Keys
3. Click "Generate New Key"
4. Give your key a descriptive name (e.g., "Production CI/CD")
5. Copy the key immediately - it won''t be shown again

Security Best Practices:
- Never commit API keys to version control
- Store keys in environment variables
- Rotate keys every 90 days
- Revoke compromised keys immediately',
 'authentication',
 ARRAY['api', 'key', 'authentication', 'security']),

('Inviting Team Members',
 'To invite team members to your project:

1. Go to Project Settings > Members
2. Click "Invite Member"
3. Enter their email address
4. Select their role:
   - Viewer: Read-only access
   - Developer: Can create and edit issues
   - Admin: Full project access
5. Click "Send Invitation"

The invited member will receive an email with instructions to join.',
 'general',
 ARRAY['team', 'members', 'invite', 'collaboration']),

('GitHub Integration Setup',
 'To connect your GitHub repository:

1. Go to Settings > Integrations > GitHub
2. Click "Connect GitHub"
3. Authorize DevFlow access to your GitHub account
4. Select the repositories you want to connect
5. Click "Save"

Features:
- Automatic issue linking from commit messages
- Pipeline triggers on push/PR
- Status checks on pull requests

Troubleshooting:
- If authorization fails, clear browser cache and try again
- Ensure you have admin access to the repository',
 'integrations',
 ARRAY['github', 'integration', 'repository', 'ci/cd']),

('Pipeline Configuration',
 'Pipelines are defined in `.devflow/pipeline.yml` at your repository root.

Example configuration:
```yaml
name: Main Pipeline

stages:
  - name: build
    commands:
      - npm install
      - npm run build
    artifacts:
      - dist/

  - name: test
    commands:
      - npm test
    depends_on:
      - build

  - name: deploy
    commands:
      - ./deploy.sh
    depends_on:
      - test
```

Pipeline statuses:
- pending: Waiting to start
- running: Currently executing
- success: Completed successfully
- failed: One or more stages failed
- canceled: Manually canceled',
 'cicd',
 ARRAY['pipeline', 'ci/cd', 'build', 'deploy', 'configuration']),

('Rate Limits',
 'API rate limits by plan:

| Plan | Requests/minute | Requests/day |
|------|-----------------|--------------|
| Starter | 60 | 1,000 |
| Professional | 300 | 50,000 |
| Enterprise | 1,000 | Unlimited |

Rate limit headers:
- X-RateLimit-Limit: Maximum requests allowed
- X-RateLimit-Remaining: Requests remaining
- X-RateLimit-Reset: Unix timestamp when limit resets

If you exceed rate limits:
- Wait for the limit to reset
- Implement exponential backoff
- Consider upgrading your plan',
 'api',
 ARRAY['api', 'rate limit', 'throttling', 'quota']);

-- =============================================================================
-- VIEWS FOR COMMON QUERIES
-- =============================================================================

-- Active conversations view
CREATE VIEW active_conversations AS
SELECT
    c.id,
    c.customer_id,
    c.initial_channel,
    c.started_at,
    c.sentiment_score,
    c.status,
    COUNT(m.id) AS message_count,
    cu.name AS customer_name,
    cu.email AS customer_email
FROM conversations c
LEFT JOIN messages m ON m.conversation_id = c.id
LEFT JOIN customers cu ON cu.id = c.customer_id
WHERE c.status = 'active'
GROUP BY c.id, cu.name, cu.email;

-- Ticket summary view
CREATE VIEW ticket_summary AS
SELECT
    t.id,
    t.source_channel,
    t.category,
    t.priority,
    t.status,
    t.created_at,
    cu.name AS customer_name,
    cu.email AS customer_email,
    CASE
        WHEN t.status = 'resolved' THEN EXTRACT(EPOCH FROM (t.resolved_at - t.created_at))/60
        ELSE EXTRACT(EPOCH FROM (NOW() - t.created_at))/60
    END AS resolution_time_minutes
FROM tickets t
LEFT JOIN customers cu ON cu.id = t.customer_id;

-- Channel metrics view
CREATE VIEW channel_metrics AS
SELECT
    initial_channel AS channel,
    COUNT(*) AS total_conversations,
    COUNT(*) FILTER (WHERE status = 'resolved') AS resolved_count,
    COUNT(*) FILTER (WHERE status = 'escalated') AS escalated_count,
    ROUND(AVG(sentiment_score)::numeric, 2) AS avg_sentiment,
    ROUND(AVG(EXTRACT(EPOCH FROM (COALESCE(ended_at, NOW()) - started_at))/60)::numeric, 2) AS avg_duration_minutes
FROM conversations
GROUP BY initial_channel;

-- =============================================================================
-- GRANT PERMISSIONS (for production use)
-- =============================================================================

-- Create read-only role
CREATE ROLE fte_read_only;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO fte_read_only;

-- Create read-write role
CREATE ROLE fte_read_write;
GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO fte_read_write;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO fte_read_write;

-- Create admin role
CREATE ROLE fte_admin;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO fte_admin;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO fte_admin;

-- =============================================================================
-- END OF SCHEMA
-- =============================================================================
