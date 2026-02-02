"""Session management API endpoints."""
from flask import Blueprint, jsonify, request, Response

from app.services.room_store import room_store
from app.models import SessionExport, ExportFormat

sessions_bp = Blueprint('sessions', __name__, url_prefix='/api/sessions')


@sessions_bp.route('/<room_code>', methods=['GET'])
def get_session(room_code: str):
    """
    Get session data for a room.

    Args:
        room_code: 6-character room code

    Returns:
        200: Session data
        404: Room/session not found
    """
    room = room_store.get_room(room_code.upper())

    if not room:
        return jsonify({
            'success': False,
            'error': 'session_not_found',
            'message': 'Session not found.'
        }), 404

    return jsonify({
        'success': True,
        'session': {
            'room_code': room.room_code,
            'status': room.status.value,
            'started_at': room.created_at.isoformat(),
            'participant_count': len(room.participants),
            'message_count': len(room.messages),
            'crisis_detected': room.crisis_detected,
            'crisis_category': room.crisis_category,
            'participants': [
                {
                    'role': p.role.value,
                    'is_connected': p.is_connected,
                    'joined_at': p.joined_at.isoformat()
                }
                for p in room.participants
            ]
        }
    }), 200


@sessions_bp.route('/<room_code>/messages', methods=['GET'])
def get_messages(room_code: str):
    """
    Get conversation history for a session.

    Args:
        room_code: 6-character room code

    Query params:
        limit: Max messages to return (default: 100)
        offset: Skip first N messages (default: 0)

    Returns:
        200: Message list
        404: Session not found
    """
    room = room_store.get_room(room_code.upper())

    if not room:
        return jsonify({
            'success': False,
            'error': 'session_not_found',
            'message': 'Session not found.'
        }), 404

    # Pagination
    limit = request.args.get('limit', 100, type=int)
    offset = request.args.get('offset', 0, type=int)

    messages = room.messages[offset:offset + limit]

    return jsonify({
        'success': True,
        'room_code': room.room_code,
        'total_messages': len(room.messages),
        'returned': len(messages),
        'offset': offset,
        'messages': [msg.to_dict() for msg in messages]
    }), 200


@sessions_bp.route('/<room_code>/export', methods=['POST'])
def export_session(room_code: str):
    """
    Export session transcript.

    Args:
        room_code: 6-character room code

    Request body:
        format: 'json' or 'txt' (default: 'json')

    Returns:
        200: Exported transcript
        404: Session not found
    """
    room = room_store.get_room(room_code.upper())

    if not room:
        return jsonify({
            'success': False,
            'error': 'session_not_found',
            'message': 'Session not found.'
        }), 404

    # Get format from request
    data = request.get_json(silent=True) or {}
    format_str = data.get('format', 'json').lower()

    if format_str == 'txt':
        export_format = ExportFormat.TXT
    else:
        export_format = ExportFormat.JSON

    # Create export
    export = SessionExport.from_room(room, export_format)
    content = export.export()

    # Return as downloadable file
    if export_format == ExportFormat.TXT:
        return Response(
            content,
            mimetype='text/plain',
            headers={
                'Content-Disposition': f'attachment; filename=session_{room_code}.txt'
            }
        )
    else:
        return Response(
            content,
            mimetype='application/json',
            headers={
                'Content-Disposition': f'attachment; filename=session_{room_code}.json'
            }
        )


@sessions_bp.route('/<room_code>/export/preview', methods=['GET'])
def preview_export(room_code: str):
    """
    Preview export without downloading.

    Args:
        room_code: 6-character room code

    Query params:
        format: 'json' or 'txt' (default: 'json')

    Returns:
        200: Export preview
        404: Session not found
    """
    room = room_store.get_room(room_code.upper())

    if not room:
        return jsonify({
            'success': False,
            'error': 'session_not_found',
            'message': 'Session not found.'
        }), 404

    format_str = request.args.get('format', 'json').lower()

    if format_str == 'txt':
        export_format = ExportFormat.TXT
    else:
        export_format = ExportFormat.JSON

    export = SessionExport.from_room(room, export_format)

    return jsonify({
        'success': True,
        'format': export_format.value,
        'metadata': export.to_dict(),
        'preview': export.export()[:2000] if len(export.export()) > 2000 else export.export(),
        'truncated': len(export.export()) > 2000
    }), 200


@sessions_bp.route('/<room_code>', methods=['DELETE'])
def end_session(room_code: str):
    """
    End a therapy session.

    Args:
        room_code: 6-character room code

    Query params:
        cleanup: If 'true', also delete the room data (default: false)

    Returns:
        200: Session ended
        404: Session not found
    """
    room = room_store.get_room(room_code.upper())

    if not room:
        return jsonify({
            'success': False,
            'error': 'session_not_found',
            'message': 'Session not found.'
        }), 404

    # Close the room
    room.close()

    # Check if we should cleanup immediately
    cleanup = request.args.get('cleanup', 'false').lower() == 'true'

    if cleanup:
        room_store.delete_room(room_code)
        return jsonify({
            'success': True,
            'message': 'Session ended and data deleted.',
            'data_deleted': True
        }), 200

    return jsonify({
        'success': True,
        'message': 'Session ended. Data available for export.',
        'export_available': True,
        'export_window_minutes': 10,
        'data_deleted': False
    }), 200
