# Escalation Rules - Customer Success FTE

## Overview

This document defines when the AI agent should escalate to human support. Escalation ensures customers receive appropriate help for issues beyond the AI's scope.

---

## Automatic Escalation Triggers

### 1. Legal & Compliance (CRITICAL - Immediate Escalation)

**Keywords/Phrases:**
- "lawyer", "attorney", "legal action", "lawsuit", "sue"
- "court", "legal department", "compliance violation"
- "GDPR", "SOC 2", "HIPAA", "data processing agreement", "DPA"
- "terms of service violation", "breach of contract"

**Action:** Escalate immediately with reason `legal_inquiry`
**Priority:** Critical
**Response:** "I understand this is a serious matter. I'm connecting you with our legal team who can provide the appropriate documentation and assistance."

---

### 2. Pricing & Refunds (HIGH - Immediate Escalation)

**Keywords/Phrases:**
- "how much does enterprise cost", "custom pricing", "negotiate price"
- "refund", "money back", "cancel subscription", "chargeback"
- "too expensive", "discount", "promo code", "special pricing"
- "billing error", "overcharged", "double charged"

**Action:** Escalate with reason `pricing_inquiry` or `refund_request`
**Priority:** High
**Response:** "I'll connect you with our billing team who can discuss pricing options and assist with your request."

---

### 3. Negative Sentiment (HIGH - Contextual Escalation)

**Conditions:**
- Sentiment score < 0.3
- Customer uses profanity or aggressive language
- Multiple exclamation marks with negative words
- ALL CAPS messages indicating frustration

**Action:** Escalate with reason `negative_sentiment`
**Priority:** High
**Response:** "I understand your frustration and I want to make sure you get the help you deserve. Let me connect you with a senior support specialist."

---

### 4. Explicit Human Request (MEDIUM - Immediate Escalation)

**Keywords/Phrases:**
- "human", "real person", "live agent", "support representative"
- "talk to someone", "speak with a person", "not a bot"
- "this bot is useless", "AI not helpful"

**Action:** Escalate with reason `human_requested`
**Priority:** Medium (High if sentiment < 0.4)
**Response:** "I'll connect you with a human agent who can assist you further."

---

### 5. Critical System Issues (CRITICAL - Immediate Escalation)

**Keywords/Phrases:**
- "production down", "outage", "service unavailable"
- "data loss", "database deleted", "files missing"
- "security breach", "hacked", "unauthorized access"
- "can't access", "locked out", "account compromised"

**Action:** Escalate with reason `critical_incident`
**Priority:** Critical
**Response:** "This is a critical issue. I'm alerting our emergency response team immediately. They will contact you within 15 minutes."

---

### 6. Information Not Found (MEDIUM - After 2 Attempts)

**Conditions:**
- Knowledge base search returns no results twice
- Agent confidence in answer < 0.5
- Question is highly specific or technical

**Action:** Escalate with reason `information_not_found`
**Priority:** Medium
**Response:** "Let me get you in touch with a specialist who has more detailed information about this topic."

---

### 7. Enterprise Customer Requests (MEDIUM - Priority Escalation)

**Conditions:**
- Customer domain matches known Enterprise account
- Customer mentions "Enterprise" plan
- SSO, SLA, or custom integration questions

**Action:** Escalate with reason `enterprise_support`
**Priority:** Medium
**Response:** "As an Enterprise customer, you have access to our dedicated support team. I'll connect you with your account specialist."

---

## Escalation Decision Matrix

| Trigger | Priority | Response Time | Team |
|---------|----------|---------------|------|
| Legal/Compliance | Critical | < 15 min | Legal + Support |
| Critical Incident | Critical | < 15 min | Engineering + Support |
| Pricing/Refund | High | < 1 hour | Sales/Billing |
| Negative Sentiment | High | < 30 min | Senior Support |
| Human Requested | Medium | < 2 hours | General Support |
| Information Not Found | Medium | < 4 hours | Subject Expert |
| Enterprise Support | Medium | < 1 hour | Enterprise Team |

---

## Escalation Data Structure

When escalating, include:

```json
{
  "ticket_id": "uuid",
  "escalation_reason": "legal_inquiry",
  "urgency": "critical",
  "customer_sentiment": 0.1,
  "conversation_summary": "Customer is threatening legal action regarding...",
  "full_conversation_history": [...],
  "channel": "email",
  "customer_tier": "enterprise",
  "attempted_solutions": ["searched_knowledge_base", "checked_documentation"],
  "suggested_team": "legal",
  "sla_deadline": "2024-01-20T15:30:00Z"
}
```

---

## De-escalation Guidelines

In some cases, the AI can attempt to de-escalate:

1. **Acknowledge the frustration:** "I understand this is frustrating..."
2. **Apologize sincerely:** "I'm sorry you've had this experience..."
3. **Offer immediate value:** "Let me help you with..."
4. **Set clear expectations:** "Here's what will happen next..."

**Only attempt de-escalation if:**
- Sentiment is between 0.3-0.5
- Issue is solvable with available information
- Customer hasn't explicitly requested a human

---

## Post-Escalation Actions

After escalating:

1. **Create escalation record** in database
2. **Notify appropriate team** via Kafka event
3. **Send confirmation to customer** with expected response time
4. **Monitor escalation queue** for status updates
5. **Log escalation metrics** for continuous improvement

---

## Escalation Metrics to Track

- Escalation rate by channel
- Escalation rate by category
- Average time to escalation
- Customer satisfaction post-escalation
- False positive escalations (unnecessary escalations)
- False negative escalations (should have escalated but didn't)

**Target:** < 20% overall escalation rate
