"""Participant model for therapy room users."""
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional


class ParticipantRole(Enum):
    """Role of a participant in a therapy room."""
    PARTNER_A = "partner_a"
    PARTNER_B = "partner_b"


@dataclass
class Participant:
    """Represents a user in a therapy room."""

    user_id: str
    role: ParticipantRole
    socket_id: Optional[str] = None
    is_connected: bool = False
    joined_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_seen: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    disconnected_at: Optional[datetime] = None

    def connect(self, socket_id: str) -> None:
        """Mark participant as connected with a socket."""
        self.socket_id = socket_id
        self.is_connected = True
        self.last_seen = datetime.now(timezone.utc)
        self.disconnected_at = None

    def disconnect(self) -> None:
        """Mark participant as disconnected."""
        self.is_connected = False
        self.disconnected_at = datetime.now(timezone.utc)
        self.socket_id = None

    def update_last_seen(self) -> None:
        """Update the last seen timestamp."""
        self.last_seen = datetime.now(timezone.utc)

    def can_reconnect(self, window_minutes: int = 5) -> bool:
        """Check if participant is within reconnection window."""
        if self.is_connected:
            return True
        if self.disconnected_at is None:
            return False
        elapsed = (datetime.now(timezone.utc) - self.disconnected_at).total_seconds()
        return elapsed < (window_minutes * 60)

    def to_dict(self) -> dict:
        """Convert participant to dictionary for serialization."""
        return {
            "user_id": self.user_id,
            "role": self.role.value,
            "is_connected": self.is_connected,
            "joined_at": self.joined_at.isoformat(),
            "last_seen": self.last_seen.isoformat(),
        }
