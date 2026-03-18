"""Room and Message models for therapy sessions."""
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional, List
import secrets
import string

from app.models.participant import Participant, ParticipantRole

class RoomMode(Enum):
    """Mode of a therapy room."""
    SOLO = "solo"
    DUO = "duo"
    GROUP = "group"

class RelationshipType(Enum):
    """Type of relationship for therapy sessions."""
    COUPLE = "couple"
    FAMILY = "family"   
    FRIENDS = "friends"
    OTHER = "other"
class RoomStatus(Enum):
    """Status of a therapy room."""
    ACTIVE = "active"
    EXPIRED = "expired"
    CLOSED = "closed"


@dataclass
class Message:
    """Represents a message in a therapy session."""

    content: str
    sender_role: Optional[ParticipantRole] = None
    is_ai: bool = False
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    message_id: str = field(default_factory=lambda: secrets.token_hex(8))

    def to_dict(self) -> dict:
        """Convert message to dictionary for serialization."""
        return {
            "message_id": self.message_id,
            "content": self.content,
            "sender_role": self.sender_role.value if self.sender_role else "ai",
            "is_ai": self.is_ai,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class Room:
    """Represents a therapy room for a couple."""

    room_code: str
    mode: RoomMode = RoomMode.DUO
    relationship_type: Optional[RelationshipType] = None
    status: RoomStatus = RoomStatus.ACTIVE
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    participants: List[Participant] = field(default_factory=list)
    messages: List[Message] = field(default_factory=list)
    crisis_detected: bool = False
    crisis_category: Optional[str] = None

    CODE_LENGTH = 6

    def __post_init__(self):
        capacity = {RoomMode.SOLO: 1, RoomMode.DUO: 2, RoomMode.GROUP: 4}
        self.max_participants: int = capacity[self.mode]

    @classmethod
    def generate_room_code(cls) -> str:
        chars = string.ascii_uppercase + string.digits
        return ''.join(secrets.choice(chars) for _ in range(cls.CODE_LENGTH))

    @classmethod
    def create(cls) -> "Room":
        """Factory method to create a new room with a generated code."""
        return cls(room_code=cls.generate_room_code())

    def is_full(self) -> bool:
        """Check if room has reached maximum participants."""
        return len(self.participants) >= self.max_participants

    def is_active(self) -> bool:
        """Check if room is currently active."""
        return self.status == RoomStatus.ACTIVE

    def is_expired(self, timeout_hours: int = 2) -> bool:
        """Check if room has exceeded timeout period."""
        if self.status == RoomStatus.EXPIRED:
            return True
        elapsed = (datetime.now(timezone.utc) - self.created_at).total_seconds()
        return elapsed > (timeout_hours * 3600)

    def add_participant(self, user_id: str, socket_id: str) -> Optional[Participant]:
        """Add a participant to the room. Returns None if room is full."""
        if self.is_full():
            return None

        index = len(self.participants)

        if self.mode == RoomMode.SOLO:
            role = ParticipantRole.SOLO
        elif self.mode == RoomMode.DUO:
            role = ParticipantRole.PARTNER_A if index == 0 else ParticipantRole.PARTNER_B
        else:  # GROUP
            group_roles = [
                ParticipantRole.MEMBER_A,
                ParticipantRole.MEMBER_B,
                ParticipantRole.MEMBER_C,
                ParticipantRole.MEMBER_D,
            ]
            role = group_roles[index]

        participant = Participant(
            user_id=user_id,
            role=role,
            socket_id=socket_id,
            is_connected=True
        )
        self.participants.append(participant)
        return participant

    def get_participant(self, user_id: str) -> Optional[Participant]:
        """Get a participant by user ID."""
        for p in self.participants:
            if p.user_id == user_id:
                return p
        return None

    def get_participant_by_socket(self, socket_id: str) -> Optional[Participant]:
        """Get a participant by socket ID."""
        for p in self.participants:
            if p.socket_id == socket_id:
                return p
        return None

    def remove_participant(self, user_id: str) -> bool:
        """Remove a participant from the room."""
        for i, p in enumerate(self.participants):
            if p.user_id == user_id:
                self.participants.pop(i)
                return True
        return False

    def add_message(self, content: str, sender_role: Optional[ParticipantRole] = None, is_ai: bool = False) -> Message:
        """Add a message to the room's conversation history."""
        message = Message(
            content=content,
            sender_role=sender_role,
            is_ai=is_ai
        )
        self.messages.append(message)
        return message

    def get_connected_count(self) -> int:
        """Get number of currently connected participants."""
        return sum(1 for p in self.participants if p.is_connected)

    def is_session_ready(self) -> bool:
        """Check if enough participants are connected to begin the session."""
        if self.mode == RoomMode.SOLO:
            return self.get_connected_count() >= 1
        elif self.mode == RoomMode.DUO:
            return self.get_connected_count() >= 2
        else:  # GROUP
            return self.get_connected_count() >= 2

    def both_connected(self) -> bool:
        """Deprecated: use is_session_ready() instead."""
        return self.is_session_ready()

    def close(self) -> None:
        """Close the room."""
        self.status = RoomStatus.CLOSED

    def expire(self) -> None:
        """Mark room as expired."""
        self.status = RoomStatus.EXPIRED

    def flag_crisis(self, category: str) -> None:
        """Flag that a crisis was detected in this room."""
        self.crisis_detected = True
        self.crisis_category = category

    def get_conversation_context(self) -> List[dict]:
        """Get conversation history formatted for AI context."""
        return [msg.to_dict() for msg in self.messages]

    def to_dict(self) -> dict:
        """Convert room to dictionary for serialization."""
        return {
            "room_code": self.room_code,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "participants": [p.to_dict() for p in self.participants],
            "message_count": len(self.messages),
            "crisis_detected": self.crisis_detected,
            "crisis_category": self.crisis_category,
        }
