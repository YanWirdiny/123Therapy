"""Frontend page routes."""
from flask import Blueprint, render_template

pages_bp = Blueprint('api', __name__)


@pages_bp.route('/')
def index():
    """Landing page."""
    return render_template('index.html')


@pages_bp.route('/room/create')
def create_room_page():
    """Create room page."""
    return render_template('room/create.html')


@pages_bp.route('/room/join')
def join_room_page():
    """Join room page."""
    return render_template('room/join.html')


@pages_bp.route('/room/<room_code>/chat')
def chat_page(room_code):
    """Chat page."""
    return render_template('room/chat.html', room_code=room_code)


@pages_bp.route('/room/<room_code>/export')
def export_page(room_code):
    """Export session page."""
    return render_template('room/export.html', room_code=room_code)