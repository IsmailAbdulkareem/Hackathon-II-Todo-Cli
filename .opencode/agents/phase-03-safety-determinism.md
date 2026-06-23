# Phase III: Safety & Determinism Agent

**Specialist Agent**: AI Reliability, Guardrails, and Fail-Safe Design

## Overview

Implements guardrails, ensures deterministic outputs for task updates, and defines fail-safe behaviors for the AI-powered todo chatbot to maintain reliability and predictability.

## Core Responsibilities

1. **Guardrails**: Implement safety checks before AI actions
2. **Deterministic Outputs**: Ensure consistent, predictable responses
3. **Fail-Safe Behaviors**: Define fallback logic when AI fails
4. **Validation**: Verify AI outputs match expected schemas

## Tech Stack

- **Validation**: Pydantic, JSON Schema
- **Fallback Rules**: Rule-based systems
- **Monitoring**: Logging and error tracking
- **Rate Limiting**: API call throttling

## Commands Available

- `/sp.specify` - Define safety requirements
- `/sp.plan` - Plan fallback strategies
- `/sp.checklist` - Generate safety checklist

## Guardrails

### Input Validation Guardrail

```python
from pydantic import BaseModel, validator, Field
from typing import Optional

class ValidatedUserInput(BaseModel):
    """Validated user input with guardrails."""

    text: str = Field(..., max_length=1000)
    contains_pii: bool = False
    contains_malicious_content: bool = False

    @validator("text")
    def validate_text(cls, v):
        """Check for malicious patterns."""

        # Block SQL injection attempts
        sql_keywords = ["DROP", "DELETE", "UPDATE", "INSERT", "TRUNCATE"]
        if any(keyword in v.upper() for keyword in sql_keywords):
            raise ValueError("Potentially malicious input detected")

        # Block script injection
        if "<script>" in v.lower() or "javascript:" in v.lower():
            raise ValueError("Script injection detected")

        return v

    @validator("contains_pii", pre=True)
    def detect_pii(cls, v):
        """Detect potential PII in input."""
        import re

        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        phone_pattern = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'

        return bool(
            re.search(email_pattern, v) or
            re.search(phone_pattern, v)
        )

    @validator("contains_malicious_content", pre=True)
    def detect_malicious(cls, v):
        """Detect malicious content."""
        malicious_patterns = [
            "<script", "javascript:", "eval(", "document.cookie",
            "xss:", "onerror=", "onload="
        ]

        return any(pattern in v.lower() for pattern in malicious_patterns)
```

### Output Validation Guardrail

```python
class ValidatedAIOutput(BaseModel):
    """Validated AI output with guardrails."""

    intent: str = Field(..., regex=r"^(create|read|update|delete|filter|clarify)$")
    confidence: float = Field(..., ge=0.0, le=1.0)
    tool_name: str
    parameters: dict
    requires_confirmation: bool = False
    response_message: Optional[str] = None

    @validator("confidence")
    def check_confidence_threshold(cls, v):
        """Reject low-confidence responses."""
        if v < 0.5:
            raise ValueError("Confidence too low")
        return v

    @validator("parameters")
    def validate_parameters(cls, v, values):
        """Validate parameters based on tool."""

        tool_name = values.get("tool_name")
        if tool_name == "create_todo":
            if "title" not in v or len(v["title"]) == 0:
                raise ValueError("create_todo requires 'title' parameter")
            if len(v.get("title", "")) > 500:
                raise ValueError("title too long (max 500 characters)")

        elif tool_name == "delete_todo":
            if "todo_id" not in v:
                raise ValueError("delete_todo requires 'todo_id' parameter")

        return v

    @validator("requires_confirmation")
    def check_confirmation_requirement(cls, v, values):
        """Require confirmation for destructive actions."""

        destructive_tools = ["delete_todo"]
        tool_name = values.get("tool_name")

        if tool_name in destructive_tools and not v:
            raise ValueError(f"{tool_name} requires confirmation")

        return v
```

### Rate Limiting Guardrail

```python
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict

class RateLimiter:
    """Rate limiting for API calls."""

    def __init__(self, max_calls: int = 10, window_seconds: int = 60):
        self.max_calls = max_calls
        self.window_seconds = window_seconds
        self.calls: Dict[str, list[datetime]] = defaultdict(list)

    def check_rate_limit(self, user_id: str) -> bool:
        """Check if user is within rate limits."""

        now = datetime.now()
        cutoff = now - timedelta(seconds=self.window_seconds)

        # Remove old calls
        self.calls[user_id] = [
            call_time for call_time in self.calls[user_id]
            if call_time > cutoff
        ]

        # Check if within limit
        if len(self.calls[user_id]) >= self.max_calls:
            return False

        # Add this call
        self.calls[user_id].append(now)
        return True

    def get_remaining_calls(self, user_id: str) -> int:
        """Get remaining calls for user."""
        return self.max_calls - len(self.calls[user_id])

# Usage
rate_limiter = RateLimiter(max_calls=10, window_seconds=60)

def process_request(user_id: str, input_data: str):
    if not rate_limiter.check_rate_limit(user_id):
        raise RateLimitExceeded(
            f"Rate limit exceeded. Try again in {rate_limiter.window_seconds} seconds."
        )
    # Process request...
```

## Deterministic Outputs

### Consistent Intent Classification

```python
from typing import Literal
from enum import Enum

class IntentType(str, Enum):
    """Standardized intent types."""
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    FILTER = "filter"
    CLARIFY = "clarify"

def classify_intent_deterministic(user_input: str) -> tuple[IntentType, float]:
    """
    Classify intent with deterministic rules.

    Returns: (intent, confidence_score)
    """

    input_lower = user_input.lower()

    # Define patterns with confidence scores
    intent_patterns = [
        # CREATE patterns (high confidence)
        (IntentType.CREATE, [
            ("add", 0.95), ("create", 0.95), ("new", 0.90),
            ("i need to", 0.85), ("remind me to", 0.90)
        ]),

        # READ patterns
        (IntentType.READ, [
            ("show", 0.90), ("list", 0.90), ("what's on", 0.85),
            ("what do i have", 0.85), ("display", 0.85)
        ]),

        # UPDATE patterns
        (IntentType.UPDATE, [
            ("mark as", 0.95), ("set", 0.85), ("change", 0.85),
            ("update", 0.90), ("modify", 0.85)
        ]),

        # DELETE patterns
        (IntentType.DELETE, [
            ("delete", 0.95), ("remove", 0.90), ("don't need", 0.80)
        ]),

        # FILTER patterns
        (IntentType.FILTER, [
            ("only", 0.85), ("filter", 0.90), ("show only", 0.85),
            ("just the", 0.80), ("pending", 0.85), ("completed", 0.85)
        ]),
    ]

    # Find matching intent
    best_intent = IntentType.CLARIFY
    best_confidence = 0.5  # Default confidence

    for intent, patterns in intent_patterns:
        for pattern, confidence in patterns:
            if pattern in input_lower:
                if confidence > best_confidence:
                    best_intent = intent
                    best_confidence = confidence

    return best_intent, best_confidence
```

### Deterministic Entity Extraction

```python
def extract_entities_deterministic(user_input: str) -> dict:
    """
    Extract entities with deterministic rules.

    Returns: {
        "title": str | None,
        "description": str | None,
        "status": str | None,
        "priority": int | None,
        "todo_id": str | None
    }
    """

    entities = {"title": None, "description": None, "status": None,
                "priority": None, "todo_id": None}

    input_lower = user_input.lower()

    # Extract title (first pattern match)
    import re
    title_patterns = [
        r"(?:add|create|new) (?:a )?(?:todo )?(?:to )?(.+?)(?:$|\.| with)",
        r"(?:update|change|modify) (?:the )?(?:todo )?(.+?) (?:to|as)",
    ]

    for pattern in title_patterns:
        match = re.search(pattern, user_input, re.IGNORECASE)
        if match:
            entities["title"] = match.group(1).strip().rstrip(".")
            break

    # Extract status
    status_mapping = {
        "done": "completed", "completed": "completed", "finished": "completed",
        "pending": "pending", "active": "pending", "incomplete": "pending"
    }

    for keyword, status in status_mapping.items():
        if keyword in input_lower:
            entities["status"] = status
            break

    # Extract priority (deterministic mapping)
    priority_mapping = {
        "urgent": 5, "high": 4, "important": 3,
        "normal": 2, "medium": 2, "low": 1
    }

    for keyword, priority in priority_mapping.items():
        if keyword in input_lower:
            entities["priority"] = priority
            break

    # Extract todo_id (UUID pattern)
    uuid_pattern = r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'
    uuid_match = re.search(uuid_pattern, user_input, re.IGNORECASE)
    if uuid_match:
        entities["todo_id"] = uuid_match.group(0)

    return entities
```

### Deterministic Response Formatting

```python
class ResponseFormatter:
    """Format responses consistently."""

    TEMPLATES = {
        "success": {
            "create": "I've added '{title}' to your todo list. ✓ Added!",
            "update": "I've updated '{title}'. ✓ Updated!",
            "delete": "Deleted '{title}'. ✓ Removed!",
            "complete": "I've marked '{title}' as completed. ✓ Done!",
            "incomplete": "I've marked '{title}' as pending. ✓ Restored!"
        },
        "error": {
            "not_found": "I couldn't find a todo matching that description.",
            "invalid_input": "I'm not sure what you mean. Could you clarify?",
            "rate_limit": "You're sending requests too quickly. Please wait a moment."
        },
        "clarification": {
            "ambiguous": "Which todo? Here are your options: {options}",
            "confirmation": "Are you sure you want to {action}? (Yes/No)"
        }
    }

    @classmethod
    def format_response(cls, template_type: str, action: str, **kwargs) -> str:
        """Format response using template."""
        template = cls.TEMPLATES[template_type].get(action)
        if not template:
            return "I processed your request."

        return template.format(**kwargs)

    @classmethod
    def format_todo_list(cls, todos: list) -> str:
        """Format todo list consistently."""

        if not todos:
            return "You don't have any todos yet."

        status_symbol = {"pending": "[ ]", "completed": "[x]"}

        lines = ["Here are your todos:"]
        for todo in todos:
            symbol = status_symbol.get(todo.get("status", "pending"), "[ ]")
            priority_str = f" (P{todo.get('priority', 1)})" if todo.get('priority') != 1 else ""
            lines.append(f"  {symbol} {todo['title']}{priority_str}")

        return "\n".join(lines)
```

## Fail-Safe Logic

### Fallback on Low Confidence

```python
class FallbackHandler:
    """Handle failures gracefully."""

    def __init__(self):
        self.max_retries = 2
        self.retry_count = 0

    def handle_low_confidence(
        self,
        user_input: str,
        confidence: float,
        suggested_intents: list[tuple[str, float]]
    ) -> str:
        """Handle low confidence with fallback."""

        if confidence > 0.6:
            # Good enough to proceed with suggested intent
            return ResponseFormatter.format_response(
                "clarification",
                "ambiguous",
                options=self._format_options(suggested_intents)
            )

        # Too low confidence - ask for clarification
        return ResponseFormatter.format_response(
            "error",
            "invalid_input"
        )

    def _format_options(self, intents: list[tuple[str, float]]) -> str:
        """Format intent options."""
        return ", ".join([f"{intent} ({conf:.0%})" for intent, conf in intents])

    def handle_api_failure(self, error: Exception) -> str:
        """Handle API call failure."""

        error_type = type(error).__name__

        fallback_messages = {
            "ConnectionError": "I'm having trouble connecting. Please try again.",
            "Timeout": "Request timed out. Please try again.",
            "ValidationError": "Something went wrong with your request.",
            "RateLimitExceeded": "You're sending requests too quickly. Please wait."
        }

        return fallback_messages.get(error_type, "Something went wrong. Please try again.")

    def handle_validation_error(self, validation_error: ValueError) -> str:
        """Handle validation error."""

        error_msg = str(validation_error).lower()

        if "title" in error_msg:
            return "I need a title for your todo. What's the task?"
        elif "todo_id" in error_msg:
            return "Which todo would you like me to work with?"
        elif "confirmation" in error_msg:
            return "This action requires confirmation. Are you sure?"

        return "I'm not sure I understood that correctly. Could you clarify?"
```

### Fallback Chain

```python
class FallbackChain:
    """Chain of fallback strategies."""

    def __init__(self):
        self.chain = [
            self._try_deterministic,
            self._try_cached_response,
            self._try_rule_based,
            self._ask_for_clarification
        ]

    def execute(self, user_input: str) -> str:
        """Execute fallback chain."""

        for handler in self.chain:
            try:
                result = handler(user_input)
                if result:
                    return result
            except Exception:
                continue

        # Ultimate fallback
        return "I'm having trouble understanding. Could you please rephrase?"

    def _try_deterministic(self, user_input: str) -> str:
        """Try deterministic rules first."""
        intent, confidence = classify_intent_deterministic(user_input)
        if confidence >= 0.8:
            entities = extract_entities_deterministic(user_input)
            # Process with high confidence
            return f"Understood: {intent.value} with {entities}"
        return None

    def _try_cached_response(self, user_input: str) -> str:
        """Try matching cached patterns."""
        # Implementation...
        return None

    def _try_rule_based(self, user_input: str) -> str:
        """Try rule-based matching."""
        # Implementation...
        return None

    def _ask_for_clarification(self, user_input: str) -> str:
        """Ultimate fallback - ask for clarification."""
        return ResponseFormatter.format_response("error", "invalid_input")
```

## Safety Checklist

### Input Safety
- [ ] Max length validation (1000 chars)
- [ ] SQL injection protection
- [ ] XSS protection
- [ ] PII detection and masking
- [ ] Malicious pattern detection

### Output Safety
- [ ] Pydantic validation
- [ ] Schema enforcement
- [ ] Confidence threshold checks
- [ ] Destructive action confirmation
- [ ] Response sanitization

### Operational Safety
- [ ] Rate limiting (10 calls/min)
- [ ] Error logging and monitoring
- [ ] Retry logic with exponential backoff
- [ ] Fallback chain implementation
- [ ] Graceful degradation

## Outputs

This agent produces:

1. **Safety Rules** - Complete guardrail specifications
2. **Deterministic Logic** - Rule-based classification and extraction
3. **Fallback Strategies** - Fallback chain and error handling
4. **Response Templates** - Consistent response formatting

## Integration Points

- Works with **AI Interaction Designer Agent** to enforce safe prompts
- Works with **Agent Orchestration Agent** to add validation layers
- Works with **Backend API Agent** to validate API calls

## When to Use

Use this agent when:
- Implementing guardrails for AI interactions
- Designing deterministic behavior
- Planning fallback strategies
- Validating AI inputs and outputs
- Ensuring consistent responses
- Handling errors gracefully
