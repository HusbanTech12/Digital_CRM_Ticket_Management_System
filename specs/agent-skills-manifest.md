# Agent Skills Manifest - Customer Success FTE

**Version:** 1.0  
**Date:** 2026-03-30  
**Agent:** Customer Success FTE

---

## Overview

This document defines the reusable skills that the Customer Success FTE can invoke. Each skill has clear triggers, inputs, outputs, and integration points.

---

## Skills Manifest

### Skill 1: Knowledge Retrieval

**Skill ID:** `knowledge_retrieval`

| Attribute | Value |
|-----------|-------|
| **Purpose** | Search and retrieve relevant product documentation |
| **When to Use** | Customer asks product questions, how-to questions, technical queries |
| **Input** | `query: str`, `max_results: int (default: 5)`, `category: Optional[str]` |
| **Output** | `List[Dict]` with title, content, score |
| **Tools Used** | `search_knowledge_base` |
| **Fallback** | Return "No relevant documentation found" message |

**Skill Definition:**
```json
{
  "skill_id": "knowledge_retrieval",
  "name": "Knowledge Retrieval",
  "description": "Search product documentation for relevant information",
  "trigger_conditions": [
    "customer asks about product features",
    "customer needs how-to guidance",
    "customer has technical question"
  ],
  "input_schema": {
    "query": {"type": "string", "required": true},
    "max_results": {"type": "integer", "default": 5},
    "category": {"type": "string", "required": false}
  },
  "output_schema": {
    "results": {
      "type": "array",
      "items": {
        "title": "string",
        "content": "string",
        "score": "number"
      }
    }
  },
  "performance_metrics": {
    "avg_latency_ms": 100,
    "accuracy_target": 0.85
  }
}
```

**Example Usage:**
```python
# Input
query = "How do I create an API key?"
max_results = 3

# Output
{
  "results": [
    {
      "title": "API Keys",
      "content": "API keys authenticate your requests...",
      "score": 5
    }
  ]
}
```

---

### Skill 2: Sentiment Analysis

**Skill ID:** `sentiment_analysis`

| Attribute | Value |
|-----------|-------|
| **Purpose** | Analyze customer emotional state from message text |
| **When to Use** | Every incoming customer message |
| **Input** | `text: str` |
| **Output** | `float` (0.0-1.0), `str` (interpretation) |
| **Tools Used** | `analyze_sentiment` |
| **Fallback** | Default to neutral (0.5) on error |

**Skill Definition:**
```json
{
  "skill_id": "sentiment_analysis",
  "name": "Sentiment Analysis",
  "description": "Analyze customer sentiment from message text",
  "trigger_conditions": [
    "every incoming customer message"
  ],
  "input_schema": {
    "text": {"type": "string", "required": true}
  },
  "output_schema": {
    "score": {"type": "number", "range": [0.0, 1.0]},
    "interpretation": {"type": "string"}
  },
  "interpretation_ranges": {
    "very_positive": [0.7, 1.0],
    "neutral_positive": [0.5, 0.7),
    "slightly_negative": [0.3, 0.5),
    "very_negative": [0.0, 0.3)
  },
  "escalation_threshold": 0.3,
  "performance_metrics": {
    "avg_latency_ms": 10
  }
}
```

**Example Usage:**
```python
# Input
text = "This is RIDICULOUS! Your platform is BROKEN!"

# Output
{
  "score": 0.12,
  "interpretation": "Very negative - consider escalation"
}
```

---

### Skill 3: Escalation Decision

**Skill ID:** `escalation_decision`

| Attribute | Value |
|-----------|-------|
| **Purpose** | Determine if conversation should be escalated to human |
| **When to Use** | After generating response, before sending |
| **Input** | `conversation_context: Dict`, `sentiment_trend: List[float]`, `detected_triggers: List[str]` |
| **Output** | `should_escalate: bool`, `reason: Optional[str]`, `urgency: str` |
| **Tools Used** | `escalate_to_human` |
| **Fallback** | When in doubt, escalate |

**Skill Definition:**
```json
{
  "skill_id": "escalation_decision",
  "name": "Escalation Decision",
  "description": "Decide whether to escalate conversation to human support",
  "trigger_conditions": [
    "after generating response",
    "when escalation triggers detected"
  ],
  "input_schema": {
    "conversation_context": {"type": "object"},
    "sentiment_trend": {"type": "array", "items": {"type": "number"}},
    "detected_triggers": {"type": "array", "items": {"type": "string"}}
  },
  "output_schema": {
    "should_escalate": {"type": "boolean"},
    "reason": {"type": "string", "enum": [
      "legal_inquiry", "pricing_inquiry", "refund_request",
      "negative_sentiment", "human_requested", "critical_incident",
      "information_not_found", "enterprise_support"
    ]},
    "urgency": {"type": "string", "enum": ["normal", "high", "critical"]}
  },
  "escalation_rules": {
    "always_escalate": [
      "legal_inquiry",
      "pricing_inquiry",
      "refund_request",
      "critical_incident"
    ],
    "threshold_escalate": {
      "sentiment_below": 0.3,
      "search_failures_above": 2
    },
    "explicit_request": [
      "human", "real person", "live agent", "not a bot"
    ]
  },
  "team_routing": {
    "legal_inquiry": "legal_team",
    "pricing_inquiry": "billing_team",
    "refund_request": "billing_team",
    "negative_sentiment": "senior_support",
    "human_requested": "general_support",
    "critical_incident": "emergency_response"
  }
}
```

**Example Usage:**
```python
# Input
{
  "conversation_context": {...},
  "sentiment_trend": [0.5, 0.4, 0.2],
  "detected_triggers": ["refund", "angry_language"]
}

# Output
{
  "should_escalate": true,
  "reason": "refund_request",
  "urgency": "high"
}
```

---

### Skill 4: Channel Adaptation

**Skill ID:** `channel_adaptation`

| Attribute | Value |
|-----------|-------|
| **Purpose** | Format response appropriately for target channel |
| **When to Use** | Before sending any response |
| **Input** | `response_text: str`, `target_channel: str`, `customer_name: Optional[str]`, `ticket_id: str` |
| **Output** | `formatted_response: str` |
| **Tools Used** | `send_response` (internal formatting) |
| **Fallback** | Use default semi-formal format |

**Skill Definition:**
```json
{
  "skill_id": "channel_adaptation",
  "name": "Channel Adaptation",
  "description": "Adapt response format for target communication channel",
  "trigger_conditions": [
    "before sending any response"
  ],
  "input_schema": {
    "response_text": {"type": "string", "required": true},
    "target_channel": {"type": "string", "enum": ["email", "whatsapp", "web_form"]},
    "customer_name": {"type": "string", "required": false},
    "ticket_id": {"type": "string", "required": true}
  },
  "output_schema": {
    "formatted_response": {"type": "string"}
  },
  "channel_specifications": {
    "email": {
      "tone": "formal",
      "max_length": 500,
      "required_elements": ["greeting", "signature", "ticket_reference"],
      "template": "Dear {name},\n\nThank you for reaching out...\n\n{response}\n\nBest regards,\nTechCorp AI Support Team"
    },
    "whatsapp": {
      "tone": "conversational",
      "max_length": 300,
      "preferred_length": 160,
      "required_elements": ["emoji", "offer_more_help"],
      "template": "{response}\n\n📱 Reply for more help or type 'human' for live support."
    },
    "web_form": {
      "tone": "semi-formal",
      "max_length": 300,
      "required_elements": ["greeting", "ticket_reference"],
      "template": "Hi {name},\n\nThanks for contacting support!\n\n{response}\n\n---\nTicket: {ticket_id}"
    }
  }
}
```

**Example Usage:**
```python
# Input
{
  "response_text": "Go to Settings > API Keys and click Generate New Key.",
  "target_channel": "whatsapp",
  "ticket_id": "TKT-20260330-0001"
}

# Output (Email)
"Dear Customer,\n\nThank you for reaching out to TechCorp Support.\n\nGo to Settings > API Keys and click Generate New Key.\n\nIf you have any further questions...\n\nBest regards,\nTechCorp AI Support Team"

# Output (WhatsApp)
"Go to Settings > API Keys and click Generate New Key. 👍\n\n📱 Reply for more help or type 'human' for live support."
```

---

### Skill 5: Customer Identification

**Skill ID:** `customer_identification`

| Attribute | Value |
|-----------|-------|
| **Purpose** | Identify/unify customer across all channels |
| **When to Use** | On every incoming message |
| **Input** | `email: Optional[str]`, `phone: Optional[str]`, `name: Optional[str]` |
| **Output** | `customer_id: str`, `merged_history: List[Dict]`, `is_returning: bool` |
| **Tools Used** | `get_customer_history`, memory store lookup |
| **Fallback** | Create new anonymous customer record |

**Skill Definition:**
```json
{
  "skill_id": "customer_identification",
  "name": "Customer Identification",
  "description": "Identify customer and unify their history across channels",
  "trigger_conditions": [
    "every incoming message"
  ],
  "input_schema": {
    "email": {"type": "string", "required": false},
    "phone": {"type": "string", "required": false},
    "name": {"type": "string", "required": false}
  },
  "output_schema": {
    "customer_id": {"type": "string"},
    "merged_history": {
      "type": "array",
      "items": {
        "conversation_id": "string",
        "channel": "string",
        "messages": "array"
      }
    },
    "is_returning": {"type": "boolean"},
    "total_conversations": {"type": "integer"}
  },
  "identification_priority": [
    "email",
    "phone",
    "name + channel_message_id"
  ],
  "merge_rules": {
    "same_email_different_phone": "merge",
    "same_phone_different_email": "merge",
    "different_email_and_phone": "create_new"
  },
  "cross_channel_continuity": {
    "enabled": true,
    "lookback_hours": 24,
    "greeting_template": "I see you contacted us previously about {topic}. Let me help you further..."
  }
}
```

**Example Usage:**
```python
# Input
{
  "email": "john@example.com",
  "phone": "+14155551234"
}

# Output (New customer)
{
  "customer_id": "cust_abc123",
  "merged_history": [],
  "is_returning": false,
  "total_conversations": 0
}

# Output (Returning customer)
{
  "customer_id": "cust_xyz789",
  "merged_history": [
    {
      "conversation_id": "conv_001",
      "channel": "email",
      "messages": [...]
    }
  ],
  "is_returning": true,
  "total_conversations": 3
}
```

---

### Skill 6: Topic Extraction

**Skill ID:** `topic_extraction`

| Attribute | Value |
|-----------|-------|
| **Purpose** | Extract topics/categories from customer message |
| **When to Use** | On every incoming message |
| **Input** | `content: str`, `subject: Optional[str]` |
| **Output** | `topics: List[str]`, `primary_topic: str`, `category: str` |
| **Tools Used** | Keyword matching, (production: ML classifier) |
| **Fallback** | Default to "general" category |

**Skill Definition:**
```json
{
  "skill_id": "topic_extraction",
  "name": "Topic Extraction",
  "description": "Extract topics and categorize customer inquiry",
  "trigger_conditions": [
    "every incoming message"
  ],
  "input_schema": {
    "content": {"type": "string", "required": true},
    "subject": {"type": "string", "required": false}
  },
  "output_schema": {
    "topics": {"type": "array", "items": {"type": "string"}},
    "primary_topic": {"type": "string"},
    "category": {"type": "string"}
  },
  "topic_keywords": {
    "authentication": ["api key", "login", "password", "auth", "token", "oauth"],
    "cicd": ["pipeline", "ci/cd", "build", "deploy", "runner", "stage"],
    "billing": ["price", "cost", "billing", "invoice", "payment", "refund"],
    "integrations": ["github", "slack", "jira", "integration", "connect"],
    "api": ["api", "endpoint", "rate limit", "request", "response"],
    "general": ["help", "question", "how to", "get started"],
    "bug_report": ["bug", "error", "not working", "broken", "issue"],
    "feedback": ["feature request", "suggestion", "improve", "love", "great"]
  }
}
```

---

### Skill 7: Response Generation

**Skill ID:** `response_generation`

| Attribute | Value |
|-----------|-------|
| **Purpose** | Generate helpful, accurate response based on context |
| **When to Use** | After knowledge retrieval, before channel adaptation |
| **Input** | `query: str`, `kb_results: List[Dict]`, `conversation_context: Dict`, `topics: List[str]` |
| **Output** | `response_text: str`, `confidence: float` |
| **Tools Used** | LLM (production), template matching (prototype) |
| **Fallback** | Use category-specific fallback response |

**Skill Definition:**
```json
{
  "skill_id": "response_generation",
  "name": "Response Generation",
  "description": "Generate helpful response based on knowledge and context",
  "trigger_conditions": [
    "after knowledge retrieval",
    "before channel adaptation"
  ],
  "input_schema": {
    "query": {"type": "string"},
    "kb_results": {"type": "array"},
    "conversation_context": {"type": "object"},
    "topics": {"type": "array"}
  },
  "output_schema": {
    "response_text": {"type": "string"},
    "confidence": {"type": "number", "range": [0.0, 1.0]}
  },
  "quality_criteria": {
    "accuracy": "Only state facts from knowledge base",
    "completeness": "Answer the full question",
    "conciseness": "Be direct, then offer more help",
    "empathy": "Acknowledge frustration if present"
  },
  "constraints": {
    "never_discuss": ["competitor products", "internal processes"],
    "never_promise": ["features not in docs", "specific timelines"],
    "always_include": ["offer for further help"]
  }
}
```

---

## Skills Execution Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        SKILLS EXECUTION FLOW                                 │
│                                                                              │
│  INCOMING MESSAGE                                                            │
│       │                                                                      │
│       ▼                                                                      │
│  ┌────────────────────┐                                                     │
│  │ 1. Customer        │                                                     │
│  │    Identification  │                                                     │
│  └─────────┬──────────┘                                                     │
│            │                                                                │
│            ▼                                                                │
│  ┌────────────────────┐                                                     │
│  │ 2. Sentiment       │                                                     │
│  │    Analysis        │                                                     │
│  └─────────┬──────────┘                                                     │
│            │                                                                │
│            ▼                                                                │
│  ┌────────────────────┐                                                     │
│  │ 3. Topic           │                                                     │
│  │    Extraction      │                                                     │
│  └─────────┬──────────┘                                                     │
│            │                                                                │
│            ▼                                                                │
│  ┌────────────────────┐                                                     │
│  │ 4. Knowledge       │                                                     │
│  │    Retrieval       │                                                     │
│  └─────────┬──────────┘                                                     │
│            │                                                                │
│            ▼                                                                │
│  ┌────────────────────┐                                                     │
│  │ 5. Response        │                                                     │
│  │    Generation      │                                                     │
│  └─────────┬──────────┘                                                     │
│            │                                                                │
│            ▼                                                                │
│  ┌────────────────────┐                                                     │
│  │ 6. Escalation      │─────► ESCALATE (if needed)                         │
│  │    Decision        │                                                     │
│  └─────────┬──────────┘                                                     │
│            │ NO ESCALATION                                                  │
│            ▼                                                                │
│  ┌────────────────────┐                                                     │
│  │ 7. Channel         │                                                     │
│  │    Adaptation      │                                                     │
│  └─────────┬──────────┘                                                     │
│            │                                                                │
│            ▼                                                                │
│  OUTGOING RESPONSE                                                         │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Skills Performance Metrics

| Skill | Target Latency | Target Accuracy | Fallback Strategy |
|-------|---------------|-----------------|-------------------|
| Knowledge Retrieval | < 100ms | > 85% | "No results found" message |
| Sentiment Analysis | < 10ms | > 80% | Default neutral (0.5) |
| Escalation Decision | < 50ms | > 90% | When in doubt, escalate |
| Channel Adaptation | < 20ms | 100% | Default semi-formal |
| Customer Identification | < 30ms | > 95% | Create new customer |
| Topic Extraction | < 20ms | > 75% | Default "general" |
| Response Generation | < 500ms | > 85% | Category fallback |

---

## Skills Integration Points

### MCP Tools Mapping

| Skill | MCP Tool | Production Tool |
|-------|----------|-----------------|
| Knowledge Retrieval | `search_knowledge_base` | `@function_tool search_knowledge_base` |
| Sentiment Analysis | `analyze_sentiment` | Internal utility |
| Escalation Decision | `escalate_to_human` | `@function_tool escalate_to_human` |
| Channel Adaptation | (part of `send_response`) | `format_for_channel()` |
| Customer Identification | `get_customer_history` | `@function_tool get_customer_history` |
| Topic Extraction | (internal) | Internal utility |
| Response Generation | (LLM) | OpenAI Agents SDK |

---

## Skills Testing Matrix

| Skill | Test Case | Input | Expected Output |
|-------|-----------|-------|-----------------|
| Knowledge Retrieval | API key query | "how to create api key" | Results about API keys |
| Sentiment Analysis | Angry customer | "THIS IS BROKEN!!!" | Score < 0.3 |
| Escalation Decision | Pricing inquiry | "enterprise pricing?" | should_escalate=true |
| Channel Adaptation | WhatsApp response | "Go to settings" | Short, with emoji |
| Customer Identification | Returning email | "test@example.com" | Existing customer_id |
| Topic Extraction | Billing question | "refund request" | category="billing" |
| Response Generation | How-to question | Query + KB results | Helpful steps |

---

**End of Agent Skills Manifest**
