  # Gemini AI Integration Plan

## Overview
Integrate Google Gemini AI as an empathetic couples therapist that responds after every user message.

---

## Architecture

```
User Message → WebSocket → Room History → Gemini Service → AI Response → Broadcast
```

---

## Files to Create

### 1. `app/services/gemini_service.py`
Core AI service handling:
- Gemini API initialization with `google-generativeai` SDK
- Conversation context management (sliding window of last 50 messages)
- Response generation with error handling
- Rate limiting (1 second minimum between calls)
- Graceful degradation on API failures

### 2. `app/services/prompt_templates.py`
Contains:
- `THERAPIST_SYSTEM_PROMPT` - Detailed therapist persona instructions
- `WELCOME_MESSAGE` - Initial greeting when session starts
- `get_crisis_response(category)` - Crisis-specific responses

### 3. `app/utils/conversation_formatter.py`
Utilities for:
- Formatting messages for Gemini's chat format (user/model roles)
- Adding Partner A/B labels to messages
- Sliding window management for long conversations
- Merging consecutive user messages

---

## Files to Modify

### 1. `app/config.py`
Add Gemini configuration:
```python
# Gemini AI Settings
GEMINI_MODEL = os.environ.get('GEMINI_MODEL', 'gemini-1.5-flash')
GEMINI_MAX_TOKENS = int(os.environ.get('GEMINI_MAX_TOKENS', 1024))
GEMINI_TEMPERATURE = float(os.environ.get('GEMINI_TEMPERATURE', 0.7))
GEMINI_CONTEXT_WINDOW = int(os.environ.get('GEMINI_CONTEXT_WINDOW', 50))
GEMINI_RATE_LIMIT_DELAY = float(os.environ.get('GEMINI_RATE_LIMIT_DELAY', 1.0))
```

### 2. `app/websocket/events.py`
- Import `gemini_service`
- Replace TODO at line 209 with background task for AI response
- Add welcome message when both partners join

### 3. `app/services/__init__.py`
Export new `GeminiService` and `gemini_service`

### 4. `app/utils/__init__.py`
Export conversation formatter utilities

---

## Therapist System Prompt

The AI therapist will be configured with these guidelines:

**Role:**
- Act as empathetic couples therapist named "Dr. Harmony"
- Guide constructive dialogue between Partner A and Partner B
- Create safe, non-judgmental space

**Techniques:**
- Gottman Method (identify "Four Horsemen")
- Emotionally Focused Therapy
- Reflective listening
- Reframing and communication coaching

**Boundaries:**
- Do not diagnose conditions
- Do not take sides
- Recommend professional help when needed
- Not a replacement for licensed therapy

---

## Message Flow

```
1. Partner sends message
2. Message added to room history
3. Broadcast to room participants
4. Emit 'ai_typing' indicator
5. Background task: Generate AI response
6. Add AI message to room history
7. Broadcast AI response
8. Clear typing indicator
```

---

## Error Handling

| Error Type | User Message | Action |
|------------|--------------|--------|
| Rate Limit | "Taking a moment to reflect..." | Backoff, retry later |
| Timeout | "Apologize for delay..." | Skip, continue session |
| Content Blocked | Neutral follow-up question | Log, safe fallback |
| API Error | "Brief technical issue..." | Log, graceful fail |
| No API Key | "AI unavailable" | Skip AI, partners chat |

---

## Environment Variables

Add to `.env`:
```bash
# Required
GEMINI_API_KEY=your-api-key-here

# Optional (with defaults)
GEMINI_MODEL=gemini-1.5-flash
GEMINI_MAX_TOKENS=1024
GEMINI_TEMPERATURE=0.7
GEMINI_CONTEXT_WINDOW=50
GEMINI_RATE_LIMIT_DELAY=1.0
```

---

## Dependencies

Already included in `requirements.txt`:
```
google-generativeai==0.3.2
```

---

## Implementation Steps

1. **Configuration** - Add Gemini settings to `app/config.py`
2. **Prompt Templates** - Create therapist system prompt
3. **Conversation Formatter** - Message formatting utilities
4. **Gemini Service** - Core AI service class
5. **WebSocket Integration** - Connect AI to message flow
6. **Package Exports** - Update `__init__.py` files

---

## Testing Checklist

- [ ] Server starts without errors with valid API key
- [ ] Welcome message appears when both partners join
- [ ] AI responds after Partner A message
- [ ] AI responds after Partner B message
- [ ] AI typing indicator shows during generation
- [ ] Graceful error when API key invalid
- [ ] Partners can still chat if AI fails
- [ ] AI maintains context across messages
- [ ] AI addresses both partners appropriately

---

## Project File Structure After Implementation

```
app/
├── services/
│   ├── __init__.py
│   ├── room_store.py (existing)
│   ├── gemini_service.py (NEW)
│   └── prompt_templates.py (NEW)
├── utils/
│   ├── __init__.py
│   └── conversation_formatter.py (NEW)
├── websocket/
│   └── events.py (MODIFIED)
└── config.py (MODIFIED)
```

---

**Status:** Ready for Implementation
**Milestone:** 1.3 - Gemini AI Integration