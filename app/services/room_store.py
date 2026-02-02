"""In-memory room storage service."""
from typing import Dict, Optional, List
from datetime import datetime

from app.models import Room, RoomStatus


class RoomStore:
    """Simple in-memory storage for therapy rooms."""

    def __init__(self):
        self._rooms: Dict[str, Room] = {}

    def create_room(self) -> Room:
        """Create a new room with a unique code."""
        room = Room.create()
        # Ensure unique code
        while room.room_code in self._rooms:
            room = Room.create()
        self._rooms[room.room_code] = room
        return room

    def get_room(self, room_code: str) -> Optional[Room]:
        """Get a room by its code."""
        return self._rooms.get(room_code.upper())

    def room_exists(self, room_code: str) -> bool:
        """Check if a room exists."""
        return room_code.upper() in self._rooms

    def delete_room(self, room_code: str) -> bool:
        """Delete a room."""
        code = room_code.upper()
        if code in self._rooms:
            del self._rooms[code]
            return True
        return False

    def get_active_rooms(self) -> List[Room]:
        """Get all active rooms."""
        return [r for r in self._rooms.values() if r.is_active()]

    def cleanup_expired(self, timeout_hours: int = 2) -> int:
        """Remove expired rooms. Returns count of removed rooms."""
        expired_codes = [
            code for code, room in self._rooms.items()
            if room.is_expired(timeout_hours)
        ]
        for code in expired_codes:
            self._rooms[code].expire()
            del self._rooms[code]
        return len(expired_codes)

    def get_room_by_socket(self, socket_id: str) -> Optional[Room]:
        """Find a room containing a participant with the given socket ID."""
        for room in self._rooms.values():
            if room.get_participant_by_socket(socket_id):
                return room
        return None

    def get_room_count(self) -> int:
        """Get total number of rooms."""
        return len(self._rooms)


# Global room store instance
room_store = RoomStore()