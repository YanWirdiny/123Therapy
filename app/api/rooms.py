"""Room management API endpoints."""
from flask import Blueprint, jsonify, request

from app.services.room_store import room_store

rooms_bp = Blueprint('rooms', __name__, url_prefix='/api/rooms')


@rooms_bp.route('', methods=['POST'])
def create_room():
    """
    Create a new therapy room.

    Returns:
        201: Room created successfully with room_code
    """
    room = room_store.create_room()

    return jsonify({
        'success': True,
        'room_code': room.room_code,
        'message': 'Room created successfully. Share this code with your partner.',
        'expires_in_hours': 2
    }), 201


@rooms_bp.route('/<room_code>', methods=['GET'])
def get_room(room_code: str):
    """
    Get room status and information.

    Args:
        room_code: 6-character room code

    Returns:
        200: Room info if found
        404: Room not found
    """
    room = room_store.get_room(room_code.upper())

    if not room:
        return jsonify({
            'success': False,
            'error': 'room_not_found',
            'message': 'Room not found. Please check the code and try again.'
        }), 404

    # Check if room has expired
    if room.is_expired():
        room.expire()
        return jsonify({
            'success': False,
            'error': 'room_expired',
            'message': 'This room has expired.'
        }), 410  # Gone

    return jsonify({
        'success': True,
        'room': {
            'room_code': room.room_code,
            'status': room.status.value,
            'created_at': room.created_at.isoformat(),
            'participant_count': len(room.participants),
            'connected_count': room.get_connected_count(),
            'is_full': room.is_full(),
            'crisis_detected': room.crisis_detected
        }
    }), 200


@rooms_bp.route('/<room_code>/validate', methods=['GET'])
def validate_room(room_code: str):
    """
    Quick validation endpoint to check if a room code is valid and joinable.

    Args:
        room_code: 6-character room code

    Returns:
        200: Room is valid and joinable
        400: Invalid code format
        404: Room not found
        410: Room expired
        409: Room is full
    """
    code = room_code.upper().strip()

    # Validate format
    if len(code) != 6:
        return jsonify({
            'valid': False,
            'joinable': False,
            'error': 'invalid_format',
            'message': 'Room code must be 6 characters.'
        }), 400

    room = room_store.get_room(code)

    if not room:
        return jsonify({
            'valid': False,
            'joinable': False,
            'error': 'not_found',
            'message': 'Room not found.'
        }), 404

    if room.is_expired():
        return jsonify({
            'valid': True,
            'joinable': False,
            'error': 'expired',
            'message': 'This room has expired.'
        }), 410

    if not room.is_active():
        return jsonify({
            'valid': True,
            'joinable': False,
            'error': 'closed',
            'message': 'This room has been closed.'
        }), 410

    if room.is_full():
        return jsonify({
            'valid': True,
            'joinable': False,
            'error': 'full',
            'message': 'This room is full.'
        }), 409

    return jsonify({
        'valid': True,
        'joinable': True,
        'participant_count': len(room.participants),
        'message': 'Room is available to join.'
    }), 200


@rooms_bp.route('/<room_code>', methods=['DELETE'])
def close_room(room_code: str):
    """
    Close and cleanup a room.

    Args:
        room_code: 6-character room code

    Returns:
        200: Room closed successfully
        404: Room not found
    """
    room = room_store.get_room(room_code.upper())

    if not room:
        return jsonify({
            'success': False,
            'error': 'room_not_found',
            'message': 'Room not found.'
        }), 404

    room.close()

    return jsonify({
        'success': True,
        'message': 'Room closed successfully.',
        'export_available': True,
        'export_window_minutes': 10
    }), 200


@rooms_bp.route('', methods=['GET'])
def get_stats():
    """
    Get general room statistics (for admin/monitoring).

    Returns:
        200: Room statistics
    """
    active_rooms = room_store.get_active_rooms()

    return jsonify({
        'total_rooms': room_store.get_room_count(),
        'active_rooms': len(active_rooms),
        'rooms_with_both_partners': sum(1 for r in active_rooms if r.both_connected())
    }), 200


@rooms_bp.route('/<room_code>/export', methods=['GET'])
def export_room(room_code: str):
    """
    Export room session data (messages and metadata).

    Args:
        room_code: 6-character room code

    Returns:
        200: Session data with messages
        404: Room not found
    """
    room = room_store.get_room(room_code.upper())

    if not room:
        return jsonify({
            'success': False,
            'error': 'room_not_found',
            'message': 'Room not found or export window has expired.'
        }), 404

    # Format messages for export
    messages = []
    for msg in room.messages:
        messages.append({
            'message_id': msg.message_id,
            'content': msg.content,
            'sender_role': msg.sender_role.value if msg.sender_role else None,
            'is_ai': msg.is_ai,
            'timestamp': msg.timestamp.isoformat()
        })

    return jsonify({
        'success': True,
        'room_code': room.room_code,
        'created_at': room.created_at.isoformat(),
        'status': room.status.value,
        'messages': messages,
        'message_count': len(messages),
        'crisis_detected': room.crisis_detected
    }), 200
