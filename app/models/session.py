"""Session export model for saving therapy transcripts."""
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
import json

from app.models.room import Room, Message


class ExportFormat(Enum):
    """Supported export formats."""
    JSON = "json"
    TXT = "txt"


@dataclass
class SessionExport:
    """Represents an exported therapy session transcript."""

    room_code: str
    messages: List[Message]
    export_format: ExportFormat = ExportFormat.JSON
    created_at: datetime = field(default_factory=datetime.utcnow)
    session_started: Optional[datetime] = None
    session_ended: Optional[datetime] = None
    crisis_detected: bool = False
    crisis_category: Optional[str] = None

    @classmethod
    def from_room(cls, room: Room, export_format: ExportFormat = ExportFormat.JSON) -> "SessionExport":
        """Create a session export from a room."""
        return cls(
            room_code=room.room_code,
            messages=room.messages.copy(),
            export_format=export_format,
            session_started=room.created_at,
            session_ended=datetime.utcnow(),
            crisis_detected=room.crisis_detected,
            crisis_category=room.crisis_category,
        )

    def to_json(self) -> str:
        """Export session as JSON string."""
        data = {
            "room_code": self.room_code,
            "session_started": self.session_started.isoformat() if self.session_started else None,
            "session_ended": self.session_ended.isoformat() if self.session_ended else None,
            "exported_at": self.created_at.isoformat(),
            "crisis_detected": self.crisis_detected,
            "crisis_category": self.crisis_category,
            "message_count": len(self.messages),
            "transcript": [msg.to_dict() for msg in self.messages],
        }
        return json.dumps(data, indent=2)

    def to_txt(self) -> str:
        """Export session as human-readable text."""
        lines = [
            "=" * 60,
            "123THERAPY - SESSION TRANSCRIPT",
            "=" * 60,
            "",
            f"Room Code: {self.room_code}",
            f"Session Started: {self.session_started.strftime('%Y-%m-%d %H:%M:%S') if self.session_started else 'N/A'}",
            f"Session Ended: {self.session_ended.strftime('%Y-%m-%d %H:%M:%S') if self.session_ended else 'N/A'}",
            f"Exported At: {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}",
            "",
        ]

        if self.crisis_detected:
            lines.extend([
                "*** CRISIS DETECTED ***",
                f"Category: {self.crisis_category}",
                "",
            ])

        lines.extend([
            "-" * 60,
            "CONVERSATION TRANSCRIPT",
            "-" * 60,
            "",
        ])

        for msg in self.messages:
            timestamp = msg.timestamp.strftime('%H:%M:%S')
            if msg.is_ai:
                sender = "AI Therapist"
            elif msg.sender_role:
                sender = msg.sender_role.value.replace("_", " ").title()
            else:
                sender = "Unknown"

            lines.append(f"[{timestamp}] {sender}:")
            lines.append(f"  {msg.content}")
            lines.append("")

        lines.extend([
            "-" * 60,
            "END OF TRANSCRIPT",
            "-" * 60,
            "",
            "DISCLAIMER: This transcript is from an AI-assisted therapy",
            "session and is intended to supplement, not replace,",
            "professional mental health services.",
        ])

        return "\n".join(lines)

    def export(self) -> str:
        """Export session in the configured format."""
        if self.export_format == ExportFormat.JSON:
            return self.to_json()
        return self.to_txt()

    def to_dict(self) -> dict:
        """Convert to dictionary for API responses."""
        return {
            "room_code": self.room_code,
            "export_format": self.export_format.value,
            "created_at": self.created_at.isoformat(),
            "session_started": self.session_started.isoformat() if self.session_started else None,
            "session_ended": self.session_ended.isoformat() if self.session_ended else None,
            "message_count": len(self.messages),
            "crisis_detected": self.crisis_detected,
        }
