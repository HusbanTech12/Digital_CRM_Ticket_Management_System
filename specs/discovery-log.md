# Discovery Log - Initial Exploration

**Date:** 2026-03-30  
**Phase:** Stage 1 - Incubation (Exercise 1.1)  
**Objective:** Analyze sample tickets and identify patterns across channels

---

## Sample Ticket Analysis

### Dataset Overview

| Metric | Value |
|--------|-------|
| Total Tickets Analyzed | 25 |
| Email Tickets | 10 (40%) |
| WhatsApp Tickets | 9 (36%) |
| Web Form Tickets | 6 (24%) |
| Escalation Required | 8 (32%) |
| Average Sentiment | 0.58 |

---

## Pattern Discovery

### 1. Channel-Specific Patterns

#### Email Characteristics
- **Average length:** 100-300 words
- **Structure:** Formal with greeting/signature
- **Common topics:** Authentication, billing, legal/compliance
- **Sentiment range:** 0.05 - 0.95 (wide range)
- **Escalation rate:** 40% (4/10 tickets)

**Key Observations:**
- Email tends to be used for complex, detailed issues
- Legal and compliance inquiries come via email
- Customers include context (account numbers, previous interactions)
- More likely to contain escalation triggers (legal, refund requests)

#### WhatsApp Characteristics
- **Average length:** 10-50 words
- **Structure:** Casual, no greeting/signature
- **Common topics:** Quick status checks, how-to questions
- **Sentiment range:** 0.1 - 0.8
- **Escalation rate:** 22% (2/9 tickets)

**Key Observations:**
- Much shorter, conversational messages
- Lowercase, informal language ("hey", "thx")
- Urgent status checks ("is there an outage?")
- Direct human requests ("human agent please")
- Emoji usage expected in responses

#### Web Form Characteristics
- **Average length:** 50-150 words
- **Structure:** Semi-formal, includes subject line
- **Common topics:** Technical issues, bug reports, feature questions
- **Sentiment range:** 0.2 - 0.95
- **Escalation rate:** 17% (1/6 tickets)

**Key Observations:**
- Structured data available (name, email, category, priority)
- More technical detail than WhatsApp
- Bug reports and integration questions common
- Customers expect ticket ID confirmation

---

### 2. Category Distribution

| Category | Count | Percentage | Primary Channel |
|----------|-------|------------|-----------------|
| General | 5 | 20% | WhatsApp |
| CI/CD | 4 | 16% | Email/Web |
| Authentication | 2 | 8% | Email |
| Integrations | 2 | 8% | Web Form |
| Billing | 2 | 8% | Email/WhatsApp |
| API | 2 | 8% | Email/WhatsApp |
| Legal/Compliance | 2 | 8% | Email |
| Critical | 2 | 8% | All channels |
| Other | 6 | 24% | Mixed |

---

### 3. Escalation Pattern Analysis

#### Escalation Triggers Found

| Trigger | Occurrences | Example |
|---------|-------------|---------|
| Pricing inquiry | 1 | "Enterprise pricing inquiry" |
| Refund request | 1 | "I want a FULL REFUND immediately" |
| Legal threat | 2 | "you'll be hearing from our attorneys" |
| Compliance request | 1 | "SOC 2 Type II compliant" |
| Negative sentiment | 2 | "THIS IS RIDICULOUS!!!" |
| Human requested | 1 | "human agent please" |
| Critical incident | 2 | "Production down" |

**Key Finding:** 32% escalation rate is ABOVE the 20% target. This suggests:
- Some escalations may be preventable with better knowledge base
- Legal/pricing escalations are unavoidable (policy constraint)
- Critical incidents should always escalate (correct behavior)

---

### 4. Sentiment Analysis Patterns

#### Sentiment Distribution

| Range | Count | Percentage | Typical Response |
|-------|-------|------------|------------------|
| 0.8-1.0 (Very Positive) | 5 | 20% | Enthusiastic, helpful |
| 0.5-0.7 (Neutral/Positive) | 10 | 40% | Professional, clear |
| 0.3-0.4 (Slightly Negative) | 3 | 12% | Empathetic, solution-focused |
| 0.0-0.2 (Very Negative) | 7 | 28% | Calm, apologetic, escalate |

**Key Finding:** Sentiment < 0.3 is a strong escalation indicator. All tickets with sentiment < 0.2 required escalation.

---

### 5. Edge Cases Discovered

| Edge Case | Frequency | Handling Strategy |
|-----------|-----------|-------------------|
| Empty message | 1/25 | Request clarification politely |
| Very short message ("thx") | 1/25 | Acknowledge, offer further help |
| ALL CAPS anger | 2/25 | De-escalate, then escalate if needed |
| Legal threats | 2/25 | Immediate escalation, calm response |
| Production emergency | 2/25 | Immediate escalation, fast response |
| Cross-channel customer | Potential | Unified customer identification |
| Follow-up questions | Expected | Conversation memory required |

---

## Requirements Discovered

### Functional Requirements

#### FR-1: Multi-Channel Support
- **FR-1.1:** System must accept tickets from Gmail, WhatsApp, and Web Form
- **FR-1.2:** System must track channel source for each ticket
- **FR-1.3:** System must format responses appropriately per channel
- **FR-1.4:** System must identify customers across channels (email/phone)

#### FR-2: Ticket Processing
- **FR-2.1:** System must create a ticket record for every interaction
- **FR-2.2:** System must categorize tickets (authentication, billing, cicd, etc.)
- **FR-2.3:** System must assign priority based on content and sentiment
- **FR-2.4:** System must track ticket status (open, processing, resolved, escalated)

#### FR-3: Knowledge Base Search
- **FR-3.1:** System must search product documentation for relevant answers
- **FR-3.2:** System must rank results by relevance
- **FR-3.3:** System must handle "no results" gracefully

#### FR-4: Escalation Management
- **FR-4.1:** System must detect escalation triggers automatically
- **FR-4.2:** System must escalate for legal, pricing, refund inquiries
- **FR-4.3:** System must escalate for sentiment < 0.3
- **FR-4.4:** System must escalate when customer explicitly requests human
- **FR-4.5:** System must include full context in escalation

#### FR-5: Conversation Memory
- **FR-5.1:** System must remember conversation history within a session
- **FR-5.2:** System must recognize returning customers across channels
- **FR-5.3:** System must track topics discussed for reporting

#### FR-6: Response Generation
- **FR-6.1:** System must generate channel-appropriate responses
- **FR-6.2:** Email: Formal, 200-500 words, greeting/signature
- **FR-6.3:** WhatsApp: Casual, <300 chars preferred, emojis OK
- **FR-6.4:** Web Form: Semi-formal, 100-300 words, ticket reference

### Non-Functional Requirements

#### NFR-1: Performance
- **NFR-1.1:** Response time < 3 seconds (processing)
- **NFR-1.2:** Delivery time < 30 seconds (end-to-end)
- **NFR-1.3:** Support 200 tickets/day average, 500 peak

#### NFR-2: Reliability
- **NFR-2.1:** 99.9% uptime (24/7 operation)
- **NFR-2.2:** No message loss
- **NFR-2.3:** Survive pod restarts without data loss

#### NFR-3: Accuracy
- **NFR-3.1:** >85% accuracy on test set
- **NFR-3.2:** <20% escalation rate (excluding legal/pricing)
- **NFR-3.3:** >95% cross-channel customer identification

#### NFR-4: Scalability
- **NFR-4.1:** Auto-scale based on ticket volume
- **NFR-4.2:** Handle 10x spike during outages

---

## Channel-Specific Response Templates (Discovered)

### Email Template
```
Dear [Customer Name],

Thank you for reaching out to TechCorp Support.

[Detailed response with steps, links, and context]

If you have any further questions, please don't hesitate to reply to this email.

Best regards,
TechCorp AI Support Team
---
Ticket Reference: [ID]
```

### WhatsApp Template
```
[Quick answer in 1-2 sentences]

[Optional brief follow-up]

[Emoji] Reply for more help or type 'human' for live support.
```

### Web Form Template
```
Hi [Name],

Thanks for contacting support!

[Clear, structured response]

---
Need more help? Reply to this message or visit our support portal.
Ticket: [ID]
```

---

## Initial Architecture Insights

### Data Model Requirements
1. **Customers table:** Unified identity across channels (email, phone)
2. **Conversations table:** Thread tracking with channel metadata
3. **Messages table:** All interactions with channel source
4. **Tickets table:** Issue tracking with status/priority
5. **Knowledge Base table:** Searchable documentation with embeddings

### Event Flow
1. Channel webhook receives message
2. Normalize to unified format
3. Publish to Kafka (fte.tickets.incoming)
4. Agent worker consumes and processes
5. Agent calls tools (search, create_ticket, etc.)
6. Response sent via appropriate channel
7. Metrics published to Kafka

### Key Design Decisions
1. **PostgreSQL as CRM:** Build custom schema vs external CRM
2. **Kafka for decoupling:** Channel handlers don't wait for agent
3. **OpenAI Agents SDK:** Production agent framework
4. **Kubernetes:** Auto-scaling, reliability
5. **pgvector:** Semantic search for knowledge base

---

## Questions for Clarification

1. **Gmail Integration:**
   - Should we use Gmail API polling or Pub/Sub push notifications?
   - Do we have a test Gmail account for development?

2. **WhatsApp Integration:**
   - Are we using Twilio Sandbox for development?
   - What's the WhatsApp business number configuration?

3. **Knowledge Base:**
   - What format is the source documentation in?
   - How do we generate embeddings (which model)?

4. **Escalation Destination:**
   - Where do escalated tickets go? (Slack, email, ticketing system?)
   - What's the SLA for human response?

5. **Customer Identification:**
   - How do we handle customers with multiple emails?
   - Should we support merging customer records?

---

## Next Steps (Exercise 1.2)

Based on this analysis, the core interaction loop should:

1. **Receive** message with channel metadata
2. **Normalize** to unified format
3. **Identify** customer (email/phone lookup)
4. **Create** ticket record
5. **Check** conversation history
6. **Search** knowledge base
7. **Generate** response (channel-appropriate)
8. **Evaluate** escalation triggers
9. **Send** response via appropriate channel
10. **Store** all interactions

---

## Metrics Baseline (from sample data)

| Metric | Current (Human) | Target (AI FTE) |
|--------|-----------------|-----------------|
| Response Time | 2-24 hours | < 30 seconds |
| Resolution Rate | ~70% | > 70% |
| Escalation Rate | ~30% | < 20% |
| Customer Satisfaction | ~4.0/5.0 | > 4.0/5.0 |
| Cost per Ticket | ~$5-10 | ~$0.50-1.00 |

---

**End of Discovery Log - Exercise 1.1**
