# Customer Success FTE Specification

**Version:** 1.0  
**Date:** 2026-03-30  
**Status:** Incubation Complete - Ready for Specialization

---

## Purpose

Handle routine customer support queries with speed and consistency across multiple communication channels (Email, WhatsApp, Web Form). The agent serves as a 24/7 Digital FTE (Full-Time Equivalent) that reduces support costs from $75,000/year per human agent to <$1,000/year.

---

## Supported Channels

| Channel | Identifier | Response Style | Max Length | Response Time Target |
|---------|------------|----------------|------------|---------------------|
| **Email (Gmail)** | Email address | Formal, detailed | 500 words | < 30 seconds |
| **WhatsApp** | Phone number | Conversational, concise | 300 chars preferred | < 30 seconds |
| **Web Form** | Email address | Semi-formal | 300 words | < 30 seconds |

### Channel Characteristics

#### Email
- **Format:** Formal with greeting and signature
- **Structure:** Proper paragraphs, links, attachments possible
- **Customer expectation:** Detailed, thorough response
- **Template:**
  ```
  Dear [Name],

  Thank you for reaching out to TechCorp Support.

  [Detailed response]

  If you have any further questions, please don't hesitate to reply to this email.

  Best regards,
  TechCorp AI Support Team
  ---
  Ticket Reference: [ID]
  ```

#### WhatsApp
- **Format:** Casual, conversational
- **Structure:** Short sentences, emojis acceptable
- **Customer expectation:** Quick, actionable answer
- **Template:**
  ```
  [Quick answer]

  📱 Reply for more help or type 'human' for live support.
  ```

#### Web Form
- **Format:** Semi-formal
- **Structure:** Clear sections, ticket reference
- **Customer expectation:** Confirmation + helpful response
- **Template:**
  ```
  Hi [Name],

  Thanks for contacting support!

  [Response]

  ---
  Need more help? Reply to this message or visit our support portal.
  Ticket: [ID]
  ```

---

## Scope

### In Scope

| Category | Description | Examples |
|----------|-------------|----------|
| **Product Feature Questions** | Questions about what the product can do | "Can I integrate with GitHub?", "What CI/CD features are available?" |
| **How-To Guidance** | Step-by-step instructions | "How do I create an API key?", "How to invite team members?" |
| **Bug Report Intake** | Collecting information about issues | "The pipeline keeps failing", "Issue status not updating" |
| **Feedback Collection** | Gathering user feedback | "Feature request: Dark mode", "Love your product!" |
| **Cross-Channel Continuity** | Maintaining context across channels | Customer starts on email, follows up on WhatsApp |
| **Authentication Help** | Login, API keys, OAuth | "Can't log in", "API key not working" |
| **CI/CD Support** | Pipeline configuration and troubleshooting | "Pipeline stuck in pending", "Build failing" |
| **Integration Setup** | Third-party integrations | "GitHub integration not working", "Slack setup" |

### Out of Scope (Escalate Immediately)

| Category | Reason | Escalation Team |
|----------|--------|-----------------|
| **Pricing Negotiations** | Requires sales authority | Billing/Sales Team |
| **Refund Requests** | Requires billing authority | Billing Team |
| **Legal/Compliance Questions** | Requires legal expertise | Legal Team |
| **Angry Customers (sentiment < 0.3)** | Requires human empathy | Senior Support |
| **Critical Incidents** | Requires engineering response | Emergency Response Team |
| **Enterprise Support Requests** | Requires dedicated account management | Enterprise Team |

---

## Tools

The agent has access to the following tools (MCP server tools):

| Tool | Purpose | Constraints | Input Schema |
|------|---------|-------------|--------------|
| `search_knowledge_base` | Find relevant product documentation | Max 5 results, relevance-scored | `{query: str, max_results: int, category?: str}` |
| `create_ticket` | Log all customer interactions | Required for every conversation; must include channel | `{customer_id: str, issue: str, priority: str, channel: str, category?: str}` |
| `get_customer_history` | Retrieve cross-channel conversation history | Returns last 20 messages | `{customer_id: str}` |
| `escalate_to_human` | Hand off complex issues to human agents | Must include reason and context | `{ticket_id: str, reason: str, urgency?: str, additional_context?: str}` |
| `send_response` | Send formatted response via appropriate channel | Auto-formats for channel | `{ticket_id: str, message: str, channel: str}` |
| `analyze_sentiment` | Analyze customer emotional state | Returns 0.0-1.0 score | `{text: str}` |
| `get_ticket_status` | Check current ticket status | Read-only | `{ticket_id: str}` |

### Tool Execution Order

For every customer interaction, tools MUST be called in this order:

1. **FIRST:** `create_ticket` - Log the interaction
2. **THEN:** `get_customer_history` - Check for prior context
3. **THEN:** `search_knowledge_base` - Find relevant information
4. **THEN:** `analyze_sentiment` - Check customer emotional state
5. **THEN:** `escalate_to_human` (if needed) - Based on triggers
6. **FINALLY:** `send_response` - Reply to customer (NEVER skip this)

---

## Performance Requirements

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Response Time (Processing)** | < 3 seconds | From message received to response generated |
| **Response Time (Delivery)** | < 30 seconds | From message received to customer receives response |
| **Accuracy** | > 85% on test set | Correct answers on 25+ question test set |
| **Escalation Rate** | < 20% | Percentage of conversations escalated |
| **Cross-Channel Identification** | > 95% accuracy | Correctly identifying returning customers across channels |
| **Customer Satisfaction** | > 4.0/5.0 | Post-interaction survey scores |
| **Resolution Rate** | > 70% | Conversations resolved without human escalation |
| **Uptime** | 99.9% | 24/7 availability |

### Load Requirements

| Scenario | Volume | Handling |
|----------|--------|----------|
| **Average Day** | 150-200 tickets | 3 worker pods |
| **Peak Hours** | 300-400 tickets | Auto-scale to 10 pods |
| **Outage Spike** | 500+ tickets | Auto-scale to 20 pods, prioritize critical |

---

## Guardrails

### NEVER (Hard Constraints)

- ❌ **NEVER** discuss competitor products
- ❌ **NEVER** promise features not in documentation
- ❌ **NEVER** process refunds or discuss pricing (escalate immediately)
- ❌ **NEVER** share internal processes or system details
- ❌ **NEVER** respond without using `send_response` tool (ensures channel formatting)
- ❌ **NEVER** exceed response limits (Email=500 words, WhatsApp=300 chars, Web=300 words)
- ❌ **NEVER** create ticket AFTER responding (must create first)

### ALWAYS (Required Behaviors)

- ✅ **ALWAYS** create ticket before responding
- ✅ **ALWAYS** check customer history across all channels
- ✅ **ALWAYS** search knowledge base before answering product questions
- ✅ **ALWAYS** check sentiment before closing conversation
- ✅ **ALWAYS** use channel-appropriate tone and formatting
- ✅ **ALWAYS** offer further help at end of response
- ✅ **ALWAYS** include ticket reference in response

### ESCALATE IMMEDIATELY When Detected

| Trigger | Keywords/Patterns | Reason Code |
|---------|-------------------|-------------|
| **Legal Inquiry** | "lawyer", "attorney", "lawsuit", "sue", "legal", "compliance", "GDPR", "SOC 2" | `legal_inquiry` |
| **Pricing/Refund** | "pricing", "cost", "refund", "money back", "cancel", "discount", "enterprise plan" | `pricing_inquiry` |
| **Negative Sentiment** | Sentiment score < 0.3, profanity, aggressive language | `negative_sentiment` |
| **Human Request** | "human", "real person", "live agent", "not a bot", "bot useless" | `human_requested` |
| **Critical Incident** | "production down", "outage", "data loss", "security breach", "emergency" | `critical_incident` |
| **Information Not Found** | No relevant results after 2 search attempts | `information_not_found` |

---

## Data Model

### Core Entities

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              DATA MODEL                                      │
│                                                                              │
│  ┌──────────────┐     ┌──────────────────┐     ┌──────────────┐            │
│  │   Customer   │────▶│   Conversation   │────▶│   Message    │            │
│  │              │     │                  │     │              │            │
│  │ - id         │     │ - id             │     │ - id         │            │
│  │ - email      │     │ - customer_id    │     │ - conv_id    │            │
│  │ - phone      │     │ - initial_channel│     │ - channel    │            │
│  │ - name       │     │ - status         │     │ - direction  │            │
│  │ - created_at │     │ - started_at     │     │ - role       │            │
│  └──────────────┘     │ - sentiment      │     │ - content    │            │
│                       │ - topics         │     │ - sentiment  │            │
│                       └──────────────────┘     │ - created_at │            │
│                                                └──────────────┘            │
│  ┌──────────────┐     ┌──────────────────┐                                 │
│  │    Ticket    │     │  Knowledge Base  │                                 │
│  │              │     │                  │                                 │
│  │ - id         │     │ - id             │                                 │
│  │ - customer_id│     │ - title          │                                 │
│  │ - conv_id    │     │ - content        │                                 │
│  │ - channel    │     │ - category       │                                 │
│  │ - category   │     │ - embedding      │                                 │
│  │ - priority   │     │ - created_at     │                                 │
│  │ - status     │     └──────────────────┘                                 │
│  │ - created_at │                                                            │
│  └──────────────┘                                                            │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Customer Identification

- **Primary Key:** Email address (normalized to lowercase)
- **Secondary Key:** Phone number (normalized to E.164 format)
- **Cross-Channel Matching:** Same email or phone = same customer
- **Anonymous Customers:** Created for unauthenticated web form submissions

---

## Escalation Routing

| Reason Code | Team | SLA | Response Method |
|-------------|------|-----|-----------------|
| `legal_inquiry` | Legal Team | < 1 hour | Email |
| `pricing_inquiry` | Billing/Sales | < 2 hours | Email/Phone |
| `refund_request` | Billing Team | < 2 hours | Email |
| `negative_sentiment` | Senior Support | < 30 minutes | Channel-matched |
| `human_requested` | General Support | < 4 hours | Channel-matched |
| `critical_incident` | Emergency Response | < 15 minutes | Phone + Email |
| `information_not_found` | Subject Expert | < 4 hours | Email |
| `enterprise_support` | Enterprise Team | < 1 hour | Dedicated channel |

---

## Testing Requirements

### Unit Tests

- [ ] Knowledge base search returns relevant results
- [ ] Sentiment analysis correctly scores positive/negative text
- [ ] Escalation triggers detected accurately
- [ ] Channel formatting produces correct output
- [ ] Customer identification works across channels

### Integration Tests

- [ ] Full conversation flow (receive → process → respond)
- [ ] Cross-channel continuity (email → WhatsApp)
- [ ] Escalation creates proper records
- [ ] Ticket lifecycle (open → in_progress → resolved/escalated)

### E2E Tests

- [ ] 25+ question test set with >85% accuracy
- [ ] 24-hour continuous operation test
- [ ] Load test with 100+ concurrent tickets
- [ ] Chaos test (pod kills, network partitions)

---

## Monitoring & Metrics

### Real-Time Metrics

| Metric | Alert Threshold | Dashboard |
|--------|-----------------|-----------|
| Response latency (p95) | > 3 seconds | ✅ |
| Error rate | > 1% | ✅ |
| Escalation rate | > 25% | ✅ |
| Queue depth | > 100 tickets | ✅ |
| Worker CPU | > 80% | ✅ |

### Daily Reports

- Tickets processed by channel
- Escalation breakdown by reason
- Customer satisfaction scores
- Top topics/categories
- Knowledge base gaps (no results queries)

---

## Version History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | 2026-03-30 | Initial specification from incubation phase | AI FTE Team |

---

## Appendix A: Sample Test Set

The agent must achieve >85% accuracy on this test set:

| # | Channel | Question | Expected Category | Should Escalate |
|---|---------|----------|-------------------|-----------------|
| 1 | Email | "How do I create an API key?" | authentication | No |
| 2 | WhatsApp | "hey how do i invite team members?" | general | No |
| 3 | Web | "GitHub integration keeps failing" | integrations | No |
| 4 | Email | "What's the pricing for Enterprise?" | pricing | **Yes** |
| 5 | WhatsApp | "THIS IS BROKEN! I want a REFUND!" | billing | **Yes** |
| ... | ... | ... | ... | ... |

---

## Appendix B: Response Templates

### Email Template
```
Dear {customer_name},

Thank you for reaching out to TechCorp Support.

{response_body}

If you have any further questions, please don't hesitate to reply to this email.

Best regards,
TechCorp AI Support Team
---
Ticket Reference: {ticket_id}
This response was generated by our AI assistant. For complex issues, you can request human support.
```

### WhatsApp Template
```
{response_body}

📱 Reply for more help or type 'human' for live support.
```

### Web Form Template
```
Hi {customer_name},

Thanks for contacting support!

{response_body}

---
Need more help? Reply to this message or visit our support portal.
Ticket: {ticket_id}
```

---

**End of Specification**
