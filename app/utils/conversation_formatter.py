"""Utilities for formatting conversation history for Gemini AI."""
from typing import List, Dict

from app.models.room import Message
from app.models.participant import ParticipantRole


def format_message_for_gemini(message: Message) -> Dict:
    """
    Format a single message for Gemini's chat format.

    Gemini expects messages in format:
    {"role": "user" | "model", "parts": [{"text": "..."}]}

    We map:
    - Partner A/B messages -> "user" role with prefix
    - AI messages -> "model" role
    """
    if message.is_ai:
        return {
            "role": "model",
            "parts": [{"text": message.content}]
        }
    else:
        # Prefix partner messages with their role for context
        if message.sender_role == ParticipantRole.PARTNER_A:
            role_label = "Partner A"
        elif message.sender_role == ParticipantRole.PARTNER_B:
            role_label = "Partner B"
        else:
            role_label = "Partner"

        prefixed_content = f"[{role_label}]: {message.content}"
        return {
            "role": "user",
            "parts": [{"text": prefixed_content}]
        }


def format_conversation_history(
    messages: List[Message],
    max_messages: int = 50,
    include_summary: bool = False
) -> List[Dict]:
    """
    Format conversation history for Gemini context.

    Args:
        messages: List of Message objects from room
        max_messages: Maximum messages to include (sliding window)
        include_summary: If True and messages exceed limit, prepend summary

    Returns:
        List of formatted messages for Gemini chat history
    """
    if not messages:
        return []

    # Apply sliding window
    if len(messages) > max_messages:
        recent_messages = messages[-max_messages:]

        if include_summary:
            older_count = len(messages) - max_messages
            summary_msg = {
                "role": "user",
                "parts": [{"text": f"[System Note: {older_count} earlier messages in this session have been summarized. The conversation has been ongoing.]"}]
            }
            formatted = [summary_msg]
        else:
            formatted = []
    else:
        recent_messages = messages
        formatted = []

    # Format each message
    for msg in recent_messages:
        formatted.append(format_message_for_gemini(msg))

    # Ensure conversation doesn't start with model response
    # Gemini requires user message first
    if formatted and formatted[0].get("role") == "model":
        formatted.insert(0, {
            "role": "user",
            "parts": [{"text": "[Session resumed]"}]
        })

    return formatted


def merge_consecutive_user_messages(history: List[Dict]) -> List[Dict]:
    """
    Merge consecutive user messages for better Gemini context.
    This handles cases where both partners send messages before AI responds.
    """
    if not history:
        return []

    merged = []
    current_user_parts = []

    for msg in history:
        if msg["role"] == "user":
            current_user_parts.extend(msg["parts"])
        else:
            # Flush accumulated user messages
            if current_user_parts:
                merged.append({
                    "role": "user",
                    "parts": current_user_parts
                })
                current_user_parts = []
            merged.append(msg)

    # Don't forget trailing user messages
    if current_user_parts:
        merged.append({
            "role": "user",
            "parts": current_user_parts
        })

    return merged


def estimate_token_count(messages: List[Message]) -> int:
    """
    Rough estimate of token count for monitoring.
    Approximation: ~4 characters per token for English text.
    """
    total_chars = sum(len(msg.content) for msg in messages)
    return total_chars // 4
