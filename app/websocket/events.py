"""WebSocket event handlers for real-time therapy sessions."""
from flask import request, current_app
from flask_socketio import emit, join_room, leave_room
import secrets

from app.extensions import socketio
from app.services.room_store import room_store
from app.models import Room, ParticipantRole

from app.services.gemini_service import gemini_service
from app.services.crisis_detector import crisis_detector
from app.services.prompt_templates import get_crisis_response

def generate_user_id() -> str:
    """Generate a unique user ID for anonymous participants."""
    return secrets.token_hex(8)


@socketio.on('connect')
def handle_connect():
    """Handle new WebSocket connection."""
    socket_id = request.sid
    emit('connected', {
        'socket_id': socket_id,
        'message': 'Connected to 123Therapy server'
    })


@socketio.on('disconnect')
def handle_disconnect():
    """Handle WebSocket disconnection."""
    socket_id = request.sid

    # Find the room this socket was in
    room = room_store.get_room_by_socket(socket_id)
    if room:
        participant = room.get_participant_by_socket(socket_id)
        if participant:
            participant.disconnect()

            # Notify other participant
            emit('partner_disconnected', {
                'role': participant.role.value,
                'message': 'Your partner has disconnected',
                'can_reconnect': True
            }, room=room.room_code, include_self=False)


@socketio.on('create_room')
def handle_create_room():
    """Create a new therapy room."""
    room = room_store.create_room()

    emit('room_created', {
        'room_code': room.room_code,
        'message': 'Room created successfully. Share this code with your partner.'
    })


@socketio.on('join_room')
def handle_join_room(data):
    """Handle a user joining a therapy room."""
    socket_id = request.sid
    room_code = data.get('room_code', '').upper().strip()
    user_id = data.get('user_id') or generate_user_id()

    # Validate room code
    if not room_code or len(room_code) != 6:
        emit('error', {
            'type': 'invalid_code',
            'message': 'Invalid room code format. Please enter a 6-character code.'
        })
        return

    # Check if room exists
    room = room_store.get_room(room_code)
    if not room:
        emit('error', {
            'type': 'room_not_found',
            'message': 'Room not found. Please check the code and try again.'
        })
        return

    # Check if room is still active
    if not room.is_active():
        emit('error', {
            'type': 'room_inactive',
            'message': 'This room is no longer active.'
        })
        return

    # Check for reconnection
    existing = room.get_participant(user_id)
    if existing:
        if existing.can_reconnect():
            existing.connect(socket_id)
            join_room(room_code)

            emit('rejoined', {
                'room_code': room_code,
                'user_id': user_id,
                'role': existing.role.value,
                'message': 'Welcome back! You have reconnected to the session.'
            })

            # Notify partner
            emit('partner_reconnected', {
                'role': existing.role.value,
                'message': 'Your partner has reconnected'
            }, room=room_code, include_self=False)
            return
        else:
            emit('error', {
                'type': 'reconnect_expired',
                'message': 'Reconnection window has expired.'
            })
            return

    # Check if room is full
    if room.is_full():
        emit('error', {
            'type': 'room_full',
            'message': 'This room is full. Only two partners can join a session.'
        })
        return

    # Add participant to room
    participant = room.add_participant(user_id, socket_id)
    if not participant:
        emit('error', {
            'type': 'join_failed',
            'message': 'Failed to join the room. Please try again.'
        })
        return

    # Join the SocketIO room
    join_room(room_code)

    # Determine welcome message based on role
    if participant.role == ParticipantRole.PARTNER_A:
        welcome_msg = 'Room joined! Waiting for your partner to connect...'
    else:
        welcome_msg = 'Room joined! Both partners are now connected.'

    emit('joined', {
        'room_code': room_code,
        'user_id': user_id,
        'role': participant.role.value,
        'partner_count': room.get_connected_count(),
        'message': welcome_msg
    })

    # Notify partner if this is the second person joining
    if participant.role == ParticipantRole.PARTNER_B:
        emit('partner_joined', {
            'message': 'Your partner has joined the session.',
            'both_connected': True
        }, room=room_code, include_self=False)

        # Send welcome message from AI when both partners are connected
        emit('session_ready', {
            'message': 'Both partners are connected. The AI therapist will begin shortly.'
        }, room=room_code)

def generate_and_Send_ai_response(app, room):
    """Generate AI response and send to room."""
    with app.app_context():
        try:
            ai_response = gemini_service.generate_response(room)
            if ai_response.content:
                # Add AI message to room history
                message = room.add_message(
                    content=ai_response.content,
                    sender_role=None,
                    is_ai=True
                )

                # Broadcast AI message to room
                socketio.emit('new_message', {
                    'message_id': message.message_id,
                    'content': message.content,
                    'sender_role': 'ai',
                    'is_ai': True,
                    'timestamp': message.timestamp.isoformat()
                }, room=room.room_code)

            socketio.emit('ai_typing', {'typing': False}, room=room.room_code)
        except Exception as e:
            socketio.emit('ai_typing', {'typing': False}, room=room.room_code)
            print(f"Error sending AI response: {e}")
     


@socketio.on('send_message')
def handle_message(data):
    """Handle a message from a participant."""
    socket_id = request.sid
    content = data.get('content', '').strip()

    if not content:
        emit('error', {
            'type': 'empty_message',
            'message': 'Message cannot be empty.'
        })
        return

    # Find the room and participant
    room = room_store.get_room_by_socket(socket_id)
    if not room:
        emit('error', {
            'type': 'not_in_room',
            'message': 'You are not in a therapy session.'
        })
        return

    participant = room.get_participant_by_socket(socket_id)
    if not participant:
        emit('error', {
            'type': 'participant_not_found',
            'message': 'Session error. Please reconnect.'
        })
        return

    # Add message to room history
    message = room.add_message(
        content=content,
        sender_role=participant.role,
        is_ai=False
    )

    # Broadcast message to room
    emit('new_message', {
        'message_id': message.message_id,
        'content': message.content,
        'sender_role': participant.role.value,
        'is_ai': False,
        'timestamp': message.timestamp.isoformat()
    }, room=room.room_code)

    # Check for crisis keywords in the message
    crisis_result = crisis_detector.scan_message(content)
    if crisis_result:
        category , matched_keywords = crisis_result
        severity = crisis_detector.get_category_severity(category)

        room.flag_crisis(category)

        emit('crisis_detected', {
            'category': category,
            'severity': severity,
            'resources': get_crisis_response(category),
            'message': 'We noticed something concerning. Here are some resources that may help.'
        }, room=room.room_code)


    # Trigger AI response in background
    emit('ai_typing', {'typing': True}, room=room.room_code)
    socketio.start_background_task(generate_and_Send_ai_response, current_app._get_current_object(), room)


@socketio.on('leave_room')
def handle_leave_room(data):
    """Handle a user leaving the therapy room."""
    socket_id = request.sid
    room_code = data.get('room_code', '').upper().strip()

    room = room_store.get_room(room_code)
    if not room:
        return

    participant = room.get_participant_by_socket(socket_id)
    if not participant:
        return

    # Mark as disconnected (don't remove, allow reconnection)
    participant.disconnect()
    leave_room(room_code)

    emit('left_room', {
        'message': 'You have left the session.'
    })

    # Notify partner
    emit('partner_left', {
        'role': participant.role.value,
        'message': 'Your partner has left the session.',
        'can_reconnect': True
    }, room=room_code)


@socketio.on('end_session')
def handle_end_session(data):
    """Handle ending a therapy session permanently."""
    socket_id = request.sid
    room_code = data.get('room_code', '').upper().strip()

    room = room_store.get_room(room_code)
    if not room:
        emit('error', {
            'type': 'room_not_found',
            'message': 'Session not found.'
        })
        return

    # Close the room
    room.close()

    # Notify all participants
    emit('session_ended', {
        'room_code': room_code,
        'message': 'The therapy session has ended.',
        'export_available': True,
        'export_window_minutes': 10
    }, room=room_code)


@socketio.on('typing')
def handle_typing(data):
    """Broadcast typing indicator to partner."""
    socket_id = request.sid
    is_typing = data.get('typing', False)

    room = room_store.get_room_by_socket(socket_id)
    if not room:
        return

    participant = room.get_participant_by_socket(socket_id)
    if not participant:
        return

    emit('partner_typing', {
        'role': participant.role.value,
        'typing': is_typing
    }, room=room.room_code, include_self=False)


def register_events(app):
    """Register WebSocket events with the Flask app."""
    # Events are registered via decorators, but this function
    # can be used for any additional setup if needed
    pass
